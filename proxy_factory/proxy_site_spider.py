import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from .utils import parse_class, parse_port


def fetch_kxdaili(self, page=5):
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
        port = parse_port(self.download(urljoin(url, tds[i + 2].img["src"])))
        proxies.add("%s:%s" % (ip, port))
    return proxies


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


def fetch_goubanjia(self, page=5):
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
            port = parse_class(tds[0].select(".port")[0]["class"][-1])
            type = tds[1].a.text
            if type.count("匿"):
                proxies.add("%s:%s" % (ip, port))
    return proxies