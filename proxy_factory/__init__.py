# -*- coding: utf-8 -*-
import re
import sys
import time
import requests
import traceback
import pytesseract

from os import getcwd
from PIL import Image
from io import BytesIO
from redis import Redis
from threading import Thread
from bs4 import BeautifulSoup
from queue import Queue, Empty
from urllib.parse import urljoin
from functools import reduce, wraps
from argparse import ArgumentParser
from . import settings as default_settings
from toolkit import SettingsWrapper, Logger, MultiMonitor, SleepManager, ExceptContext, common_stop_start_control

__version__ = "0.1.0"


def exception_wrapper(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        self = args[0]
        try:
            return func(*args, **kwargs)
        except Exception as e:
            self.logger.warn("failed in %s: %s" % (func.__name__, e))
            return set()

    return wrapper


class ProxyFactory(MultiMonitor):
    name = "proxy_factory"
    setting_wrapper = SettingsWrapper()
    currenet_path = getcwd()
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:41.0) Gecko/20100101 Firefox/41.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
    }

    def __init__(self, settings):
        """
            初始化logger, redis_conn
        """
        super(ProxyFactory, self).__init__()
        sys.path.insert(0, self.currenet_path)
        self.settings = self.setting_wrapper.load(settings, default_settings)
        self.logger = Logger.init_logger(self.settings, name=self.name)
        self.proxies_check_in_queue = Queue()
        self.proxies_check_out_queue = Queue()
        self.redis_conn = Redis(self.settings.get("REDIS_HOST"), self.settings.get("REDIS_PORT"))

    def get_html(self, url, proxies=None):
        """
        获取html body
        """
        return requests.get(url, headers=self.headers, proxies=proxies).text

    def download(self, url):
        buffer = b""
        for chunk in requests.get(url, headers=self.headers, stream=True).iter_content(1024):
            buffer += chunk
        return buffer

    def parse_port(self, url):
        with Image.open(BytesIO(self.download(url))) as image:
            image = image.convert("RGB")
            gray_image = Image.new('1', image.size)
            width, height = image.size
            raw_data = image.load()
            image.close()
            for x in range(width):
                for y in range(height):
                    value = raw_data[x, y]
                    value = value[0] if isinstance(value, tuple) else value
                    if value < 1:
                        gray_image.putpixel((x, y), 0)
                    else:
                        gray_image.putpixel((x, y), 255)
            num = pytesseract.image_to_string(gray_image)
            result = self.guess(num)
            if result:
                return result
            else:
                new_char = list()
                for i in num:
                    if i.isdigit():
                        new_char.append(i)
                    else:
                        new_char.append(self.guess(i))
                return "".join(new_char)

    @staticmethod
    def guess(word):
        try:
            mapping = {
                "b": "8",
                "o": "0",
                "e": "8",
                "s": "9",
                "a": "9",
                "51234": "61234",
                "3737": "9797",
                "3000": "9000",
                "52385": "62386",
            }
            return mapping[word.lower()]
        except KeyError:
            if len(word) == 1:
                print(word)
            return word

    @exception_wrapper
    def fetch_kxdaili(self, page=1):
        """
        从www.kxdaili.com抓取免费代理
        """
        proxies = set()
        url_tmpl = "http://www.kxdaili.com/dailiip/1/%d.html"
        for page_num in range(page):
            url = url_tmpl % (page_num + 1)
            soup = BeautifulSoup(self.get_html(url), "html")
            table_tag = soup.find("table", attrs={"class": "segment"})
            trs = table_tag.tbody.find_all("tr")
            for tr in trs:
                tds = tr.find_all("td")
                ip = tds[0].text
                port = tds[1].text
                latency = tds[4].text.split(" ")[0]
                if float(latency) < 0.5:  # 输出延迟小于0.5秒的代理
                    proxy = "%s:%s" % (ip, port)
                    proxies.add(proxy)
        return proxies

    @exception_wrapper
    def fetch_mimvp(self):
        """
        从http://proxy.mimvp.com/free.php抓免费代理
        """
        proxies = set()
        url = "http://proxy.mimvp.com/free.php?proxy=in_hp"
        soup = BeautifulSoup(self.get_html(url), "html")
        tds = soup.select("tbody > td")
        for i in range(0, len(tds), 10):
            ip = tds[i + 1].text
            port = self.parse_port(urljoin(url, tds[i + 2].img["src"]))
            proxies.add("%s:%s" % (ip, port))
        return proxies

    @exception_wrapper
    def fetch_xici(self):
        """
        http://www.xicidaili.com/nn/
        """
        proxies = set()
        url = "http://www.xicidaili.com/nn/"
        soup = BeautifulSoup(self.get_html(url), "html")
        table = soup.find("table", attrs={"id": "ip_list"})
        trs = table.find_all("tr")
        for i in range(1, len(trs)):
            tr = trs[i]
            tds = tr.find_all("td")
            ip = tds[1].text
            port = tds[2].text
            proxies.add("%s:%s" % (ip, port))
        return proxies

    @exception_wrapper
    def fetch_nianshao(self):
        """
        http://www.nianshao.com/
        """
        proxies = set()
        url = "http://www.nianshao.me/"
        soup = BeautifulSoup(self.get_html(url), "html")
        table = soup.find("table", attrs={"class": "table"})
        trs = table.find_all("tr")
        for i in range(1, len(trs)):
            tr = trs[i]
            tds = tr.find_all("td")
            ip = tds[0].text
            port = tds[1].text
            proxies.add("%s:%s" % (ip, port))
        return proxies

    @exception_wrapper
    def fetch_ip181(self):
        """
        http://www.ip181.com/
        """
        proxies = set()
        url = "http://www.ip181.com/"
        soup = BeautifulSoup(self.get_html(url), "html")
        table = soup.find("table")
        trs = table.find_all("tr")
        for i in range(1, len(trs)):
            tds = trs[i].find_all("td")
            ip = tds[0].text
            port = tds[1].text
            proxies.add("%s:%s" % (ip, port))
        return proxies

    @exception_wrapper
    def fetch_httpdaili(self):
        """
        http://www.httpdaili.com/mfdl/
        更新比较频繁
        """
        proxies = set()
        url = "http://www.httpdaili.com/mfdl/"
        soup = BeautifulSoup(self.get_html(url), "html")
        trs = soup.select(".kb-item-wrap11 tr")

        for i in range(len(trs)):
            tds = trs[i].find_all("td")
            if len(tds) > 2 and tds[1].text.isdigit():
                ip = tds[0].text
                port = tds[1].text
                type = tds[2].text
                if type.encode("iso-8859-1").decode("utf-8") == "匿名":
                    proxies.add("%s:%s" % (ip, port))
        return proxies

    @exception_wrapper
    def fetch_66ip_sd(self):
        """
        http://www.66ip.cn/areaindex_15/1.html
        @return:
        """
        proxies = set()
        url = "http://www.66ip.cn/areaindex_15/1.html"
        soup = BeautifulSoup(self.get_html(url), "html")
        table = soup.find("table", attrs={"border": "2px"})
        trs = table.find_all("tr")
        for i in range(1, len(trs)):
            tds = trs[i].find_all("td")
            ip = tds[0].text
            port = tds[1].text
            type = tds[3].text
            if type.encode("iso-8859-1").decode("gbk") == "高匿代理":
                proxies.add("%s:%s" % (ip, port))
        return proxies

    @exception_wrapper
    def fetch_cn_proxy(self):
        """
        http://cn-proxy.com/
        """
        proxies = set()
        url = "http://cn-proxy.com/"
        soup = BeautifulSoup(self.get_html(url, proxies={"http": "http://192.168.200.51:8123"}), "html")
        trs = soup.select("tr")
        for i in range(2, len(trs)):
            tds = trs[i].find_all("td")
            try:
                ip = tds[0].text
                port = tds[1].text
                if port.isdigit():
                    proxies.add("%s:%s" % (ip, port))
            except IndexError:
                pass
        return proxies

    @exception_wrapper
    def fetch_66ip(self):
        """
        http://www.66ip.cn/areaindex_15/1.html
        """
        proxies = set()
        url = "http://www.66ip.cn/areaindex_15/1.html"
        soup = BeautifulSoup(self.get_html(url), "html")
        trs = soup.select("tr")
        for i in range(4, len(trs)):
            tds = trs[i].find_all("td")
            ip = tds[0].text
            port = tds[1].text
            proxies.add("%s:%s" % (ip, port))
        return proxies

    @staticmethod
    def parse_class(cls):
        """
        隐藏的解码函数
        :param cls:
        :return:
        """
        meta = dict(zip("ABCDEFGHIZ", range(10)))
        num = reduce(lambda x, y: x + str(meta.get(y)), cls, "")
        return int(num) >> 3

    @exception_wrapper
    def fetch_goubanjia(self, page=1):
        """
        http://www.goubanjia.com/
        :return:
        """
        proxies = set()
        url_tmpl = "http://www.goubanjia.com/index%s.shtml"
        for page_num in range(page):
            url = url_tmpl % (page_num + 1)
            soup = BeautifulSoup(self.get_html(url), "html")
            trs = soup.select("tbody > tr")
            for tr in trs:
                tds = tr.find_all("td")
                ip = "".join(re.findall(r"(?<!none;\")>(.*?)<", str(tds[0]))).split(":")[0]
                port = self.parse_class(tds[0].select(".port")[0]["class"][-1])
                type = tds[1].a.text
                if type.count("匿"):
                    proxies.add("%s:%s" % (ip, port))
        return proxies

    def check(self, proxy, good):
        """
            检查代理是否可用
        """
        try:
            resp = requests.get(
                "http://www.whatismyip.com.tw/", headers=self.headers, timeout=10,
                proxies={"http": "http://%s" % proxy})
            # self.logger.debug("proxy: %s,resposne code: %s" % (proxy, resp.status_code))
            ip, real_ip = re.search(r'"ip": "(.*?)"[\s\S]+"ip-real": "(.*?)",', resp.text).groups()
            self.logger.debug("IP: %s. Real IP: %s. Proxy: %s" % (ip, real_ip, proxy))
            if resp.status_code < 300 and not real_ip:
                good.append(proxy)
        except Exception as e:
            return False

    def check_proxies(self):
        self.logger.debug("Start check thread. ")
        while self.alive:
            with ExceptContext(self.log_err, Exception, "check_proxies"):
                try:
                    proxies = self.proxies_check_in_queue.get_nowait()
                except Empty:
                    proxies = None
                if proxies:
                    self.logger.debug("Got %s proxies to check. " % len(proxies))
                    proxies = [proxy.decode() if isinstance(proxy, bytes) else proxy for proxy in proxies]
                    good = list()
                    thread_list = []
                    for proxy in proxies:
                        th = Thread(target=self.check, args=(proxy, good))
                        th.start()
                        thread_list.append(th)

                    for thread in thread_list:
                        thread.join()
                    self.logger.debug("%s proxies is good. " % (len(good)))
                    self.proxies_check_out_queue.put(dict((proxy, proxy in good) for proxy in proxies))
                else:
                    time.sleep(1)
            time.sleep(1)

    def bad_source(self):
        self.logger.debug("Start bad source thread. ")
        while self.alive:
            with SleepManager(self.settings.get("BAD_CHECK_INTERVAL", 60 * 5), self) as sm:
                if not sm.is_notified:
                    continue
                with ExceptContext(self.log_err, Exception, "bad_source"):
                    proxies = self.redis_conn.hgetall("bad_proxies")
                    if proxies:
                        self.logger.debug("Bad proxy count is : %s, ready to check. " % len(proxies))
                        for proxy, times in proxies.items():
                            if int(times) > self.settings.get("FAILED_TIMES", 5):
                                self.redis_conn.hdel("bad_proxies", proxy)
                                self.logger.debug("Abandon %s of failed for %s times. " % (proxy, times))
                        self.proxies_check_in_queue.put(proxies.keys())

    def good_source(self):
        self.logger.debug("Start good source thread. ")
        while self.alive:
            with SleepManager(self.settings.get("GOOD_CHECK_INTERVAL", 60 * 5), self) as sm:
                if not sm.is_notified:
                    continue
                with ExceptContext(self.log_err, Exception, "good_source"):
                    proxies = self.redis_conn.smembers("good_proxies")
                    if proxies:
                        self.logger.debug("Good proxy count is : %s, ready to check. " % len(proxies))
                        self.proxies_check_in_queue.put(proxies)

    def reset_proxies(self):
        self.logger.debug("Start resets thread. ")
        while self.alive:
            with ExceptContext(self.log_err, Exception, "reset_proxies"):
                try:
                    proxies = self.proxies_check_out_queue.get_nowait()
                except Empty:
                    proxies = None
                if proxies:
                    self.logger.debug("Got %s proxies to reset. " % len(proxies))
                    for proxy, good in proxies.items():
                        if good:
                            self.redis_conn.sadd("good_proxies", proxy)
                            self.redis_conn.hdel("bad_proxies", proxy)
                        else:
                            self.redis_conn.hincrby("bad_proxies", proxy)
                            self.redis_conn.srem("good_proxies", proxy)
                else:
                    time.sleep(1)
            time.sleep(1)

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
            with SleepManager(self.settings.get("FETCH_INTERVAL", 10 * 60), self) as sm:
                if not sm.is_notified:
                    continue
                with ExceptContext(self.log_err, Exception, "main"):
                    if self.alive:
                        self.logger.debug("Start to fetch proxies. ")
                        proxies = self.fetch_all()
                        self.logger.debug("%s proxies found. " % len(proxies))
                        self.proxies_check_in_queue.put(proxies)

    def log_err(self, exc_type, exc_val, exc_tb, func_name):
        self.logger.error(
            "Error in %s: %s" % (func_name, "".join(traceback.format_exception(exc_type, exc_val, exc_tb))))

    def fetch_all(self):
        """
            获取全部网站代理，内部调用各网站代理获取函数
        """
        proxies = set()
        proxies.update(self.fetch_kxdaili(3))
        proxies.update(self.fetch_mimvp())
        proxies.update(self.fetch_xici())
        proxies.update(self.fetch_ip181())
        proxies.update(self.fetch_httpdaili())
        proxies.update(self.fetch_66ip())
        proxies.update(self.fetch_66ip_sd())
        proxies.update(self.fetch_nianshao())
        proxies.update(self.fetch_goubanjia(5))
        return proxies

    @classmethod
    def parse_args(cls):
        parser = ArgumentParser("proxy factory")
        parser.add_argument("-s", "--settings", help="local settings. ", default="localsettings")
        args = common_stop_start_control(parser, '/dev/null')
        return cls(args.settings)


def main():
    ProxyFactory.parse_args().start()


if __name__ == '__main__':
    main()
