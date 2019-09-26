# -*- coding: utf-8 -*-
import sys
import time
import requests

from os import getcwd
from redis import Redis
from threading import Thread
from functools import partial

from toolkit import load, re_search
from toolkit.service.monitors import Service
from toolkit.tools.managers import Blocker, ExceptContext
from toolkit.structures.thread_safe_collections import ThreadSafeSet, TreadSafeDict

from . import proxy_site_spider
from .utils import exception_wrapper
from . import settings


class ProxyFactory(Service):
    name = "proxy_factory"
    current_dir = getcwd()
    default_settings = settings
    proxy_methods = dict()

    def __init__(self):
        """
            初始化logger, redis_conn
        """
        super().__init__()
        sys.path.insert(0, self.current_dir)
        self.headers = self.settings.HEADERS
        self.proxies_check_in_channel = ThreadSafeSet()
        self.proxies_check_out_channel = TreadSafeDict()
        self.load_site(proxy_site_spider)
        self.load_site(self.args.spider_module)
        self.redis_conn = Redis(self.settings.get("REDIS_HOST"), self.settings.get_int("REDIS_PORT"))
        if self.args.check_method:
            self.is_anonymous = partial(load(self.args.check_method), self)
        self.my_ip = requests.get("https://httpbin.org/ip").json()["origin"]

    def load_site(self, module_str):
        if module_str:
            if isinstance(module_str, str):
                mod = load(module_str)
            else:
                mod = module_str
            for key, func in vars(mod).items():
                if key.startswith("fetch"):
                    self.proxy_methods[key] = partial(exception_wrapper(func), self)

    def is_anonymous(self, proxy):
        url = "http://www.98bk.com/cycx/ip1/"
        resp = requests.get(url, timeout=10, headers=self.headers, proxies={"http": "http://%s" % proxy})
        buf = resp.text.encode("iso-8859-1").decode("gbk")
        real_ip = re_search(r"您的真实IP是([\d\.]+)", buf)
        self.logger.info(f"My ip :{self.my_ip}, Real ip: {real_ip}")
        return real_ip == "" or not self.my_ip.count(real_ip)

    def check(self, proxy, good):
        """
            检查代理是否可用
        """
        with ExceptContext(errback=lambda *args: True):
            if self.is_anonymous(proxy):
                good.add(proxy)

    def check_proxies(self):
        """
        对待检查队列中的代理进行检查
        :return:
        """
        self.logger.debug("Start check thread. ")

        threads = dict()
        good = set()
        while self.alive:
            if len(self.proxies_check_in_channel):
                proxy = self.proxies_check_in_channel.pop()
            else:
                proxy = None
            if isinstance(proxy, bytes):
                proxy = proxy.decode()
            if len(threads) < 150 and proxy:
                th = Thread(target=self.check, args=(proxy, good))
                th.setDaemon(True)
                th.start()
                threads[time.time()] = (th, proxy)
                time.sleep(.001)
            else:
                time.sleep(1)
                for start_time, (th, proxy) in threads.copy().items():
                    if start_time + 60 < time.time() or not th.is_alive():
                        del threads[start_time]
                        self.proxies_check_out_channel[proxy] = proxy in good
                        good.discard(proxy)

        self.logger.debug("Stop check thread. ")

    def bad_source(self):
        """
        每隔指定时间间隔将无效代理放到待检查队列进行检查
        :return:
        """
        self.logger.debug("Start bad source thread. ")
        while self.alive:
            if len(self.proxies_check_in_channel):
                continue

            with ExceptContext(errback=self.log_err):
                proxies = self.redis_conn.hgetall("bad_proxies")
                if proxies:
                    self.logger.debug("Bad proxy count is : %s, ready to check. " % len(proxies))
                    while proxies:
                        proxy, times = proxies.popitem()
                        self.proxies_check_in_channel.add(proxy)

            Blocker(self.settings.get_int("BAD_CHECK_INTERVAL", 60 * 5)).wait_timeout_or_notify(
                notify=lambda: not self.alive)

        self.logger.debug("Stop bad source thread. ")

    def good_source(self):
        """
        每隔指定时间间隔将有效代理放到待检查队列进行检查
        :return:
        """
        self.logger.debug("Start good source thread. ")
        while self.alive:
            with ExceptContext(errback=self.log_err):
                proxies = self.redis_conn.smembers("good_proxies")
                if proxies:
                    self.logger.debug("Good proxy count is : %s, ready to check. " % len(proxies))
                    self.proxies_check_in_channel.update(proxies)
            Blocker(self.settings.get_int("GOOD_CHECK_INTERVAL", 60 * 5)).wait_timeout_or_notify(
                notify=lambda: not self.alive)

        self.logger.debug("Stop good source thread. ")

    def reset_proxies(self):
        """
        分发有效代理和无效代理
        :return:
        """
        self.logger.debug("Start resets thread. ")
        while self.alive:
            with ExceptContext(errback=self.log_err):
                proxies = list(self.proxies_check_out_channel.pop_all())
                if proxies:
                    self.logger.debug("Got %s proxies to reset. " % len(proxies))
                    for proxy, good in proxies:
                        if good:
                            self.redis_conn.sadd("good_proxies", proxy)
                            self.redis_conn.hdel("bad_proxies", proxy)
                        else:
                            count = self.redis_conn.hincrby("bad_proxies", proxy)
                            if count > self.settings.get_int("FAILED_TIMES", 5):
                                self.redis_conn.hdel("bad_proxies", proxy)
                                self.logger.debug("Abandon %s of failed for %s times. " % (proxy, count))
                            self.redis_conn.srem("good_proxies", proxy)
                else:
                    time.sleep(1)
            time.sleep(1)
        self.logger.debug("Stop resets thread. ")

    def gen_thread(self, target, name=None, args=(), kwargs=None):
        thread = Thread(target=target, name=name, args=args, kwargs=kwargs)
        thread.setDaemon(True)
        thread.start()
        self.children.append(thread)

    def start(self):
        self.logger.debug("Start proxy factory. ")
        self.gen_thread(self.check_proxies)
        self.gen_thread(self.bad_source)
        self.gen_thread(self.good_source)
        self.gen_thread(self.reset_proxies)

        while self.alive or [thread for thread in self.children if thread.is_alive()]:
            with ExceptContext(errback=self.log_err):
                if self.alive:
                    self.logger.debug("Start to fetch proxies. ")
                    proxies = self.fetch_all()
                    self.logger.debug("%s proxies found. " % len(proxies))
                    self.proxies_check_in_channel.update(proxies)

            Blocker(self.settings.get_int("FETCH_INTERVAL", 10 * 60)).wait_timeout_or_notify(
                notify=lambda: not self.alive)
        self.logger.debug("Stop proxy factory. ")

    def fetch_all(self):
        """
            获取全部网站代理，内部调用各网站代理获取函数
        """
        proxies = set()
        for key, value in self.proxy_methods.items():
            proxies.update(value())
        return proxies

    def enrich_parser_arguments(self):
        self.parser.add_argument("-cm", "--check-method", help="provide a check method to check proxies. eg:module.func")
        self.parser.add_argument("-sm", "--spider-module",
                            help="provide a module contains proxy site spider methods. eg:module1.module2")
        return super(ProxyFactory, self).enrich_parser_arguments()


def main():
    ProxyFactory().start()


if __name__ == '__main__':
    main()
