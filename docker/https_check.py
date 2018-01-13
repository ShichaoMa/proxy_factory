import requests
import re
import json

my_ip = json.loads(requests.get("https://httpbin.org/ip").text)["origin"]


def https_check(self, proxy):
    """
    自义定检查方法
    :param self: ProxyFactory对象
    :param proxy: 代理
    :return: True则代理可用，否则False
    """
    resp = requests.get("http://www.whatismyip.com.tw/",
                        headers=self.headers, timeout=10, proxies={"http": "http://%s" % proxy})
    ip, real_ip = re.search(r'"ip": "(.*?)"[\s\S]+"ip-real": "(.*?)",', resp.text).groups()
    if resp.status_code < 300 and not real_ip:
        requests.head("https://httpbin.org/ip", timeout=10, proxies={"https": "http://%s" % proxy})
        self.logger.debug("IP: %s. Real IP: %s. Proxy: %s" % (ip, real_ip, proxy))
        return True
    return False
