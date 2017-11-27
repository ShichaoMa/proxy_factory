def check(self, proxy):
    """
    自义定检查方法
    :param self: ProxyFactory对象
    :param proxy: 代理
    :return:
    """
    import requests
    resp = requests.get("http://2017.ip138.com/ic.asp", proxies={"http": "http://%s"%proxy})
    self.logger.info(resp.text)
    return resp.status_code < 300
