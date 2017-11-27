from bs4 import BeautifulSoup


def fetch_custom(self, page=5):
    """
    自定义代理网站抓取
    :param self:ProxyFactory对象
    :param page: 可以在里记录一些可选参数，但是方法只能接收一个必选参数
    :return: set类型的代理列表，ip:port
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