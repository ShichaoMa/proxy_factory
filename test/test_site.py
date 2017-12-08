import unittest
from proxy_factory import ProxyFactory
from proxy_factory.proxy_site_spider import *


class SiteTest(unittest.TestCase):

    def setUp(self):
        self.pf = ProxyFactory("settings")

    def assertHasProxy(self, proxies):
        super(SiteTest, self).assertTrue(len(proxies)>0)

    def test_kxdaili(self):
        self.assertHasProxy(fetch_kxdaili(self.pf, 1))

    def test_mimvp(self):
        self.assertHasProxy(fetch_mimvp(self.pf))

    def test_66ip(self):
        self.assertHasProxy(fetch_66ip(self.pf))

    def test_66ip_sd(self):
        self.assertHasProxy(fetch_66ip_sd(self.pf))

    def test_goubanjia(self):
        self.assertHasProxy(fetch_goubanjia(self.pf))

    def test_cn_proxy(self):
        self.assertHasProxy(fetch_cn_proxy(self.pf))

    def test_httpdaili(self):
        self.assertHasProxy(fetch_httpdaili(self.pf))

    def test_nianshao(self):
        self.assertHasProxy(fetch_nianshao(self.pf))


if __name__ == "__main__":
    unittest.main()