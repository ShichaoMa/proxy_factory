from proxy_factory.proxy_site_spider import *

pf = type("AA", (object,), {})()
pf.headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:41.0) Gecko/20100101 Firefox/41.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
}


class TestSite(object):

    def test_kxdaili(self):
        assert len(fetch_kxdaili(pf)) > 0

    def test_mimvp(self):
        assert fetch_mimvp(pf)

    def test_66ip(self):
        assert len(fetch_66ip(pf, 15)) > 0

    def test_goubanjia(self):
        assert len(fetch_goubanjia(pf)) > 0

    def test_xici(self):
        assert len(fetch_xici(pf)) > 0
    #
    # def test_cn_proxy(self):
    #     assert len(fetch_cn_proxy(pf)) > 0
    #
    # def test_httpdaili(self):
    #     assert len(fetch_httpdaili(pf)) > 0
    #
    # def test_nianshao(self):
    #     assert len(fetch_nianshao(pf)) > 0
