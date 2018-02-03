自动从网上抓取免费代理,并对代理的可用性和匿名性进行检查，同时定时检查有效代理和无效代理，对于多次检查始终无效的代理，做放弃处理。同时检查函数可以自定义指定，用来针对不同的检查结果做出不同的反应。当然代理网站也可以自定义，简单的几行代码几条配置信息，实现最大限度的free-style。

# INSTALL

```angular2html
# python3 以上版本
pip install proxy-factory
# 依赖 redis(必须), tesseract-ocr（可选）
```

# USAGE
```angular2html
mashichaodeMac-mini:toolkit mashichao$ product -h
usage: product [-h] [-cm CHECK_METHOD] [-sm SPIDER_MODULE] [--console]
               [--console-host CONSOLE_HOST] [--console-port CONSOLE_PORT]
               [-s SETTINGS] [-ls LOCALSETTINGS] [-d]
               [{stop,start,restart,status}]

positional arguments:
  {stop,start,restart,status}

optional arguments:
  -h, --help            show this help message and exit
  -cm CHECK_METHOD, --check-method CHECK_METHOD
                        proivde a check method to check proxies.
                        eg:module.func
  -sm SPIDER_MODULE, --spider-module SPIDER_MODULE
                        proivde a module contains proxy site spider methods.
                        eg:module1.module2
  --console             start a console.
  --console-host CONSOLE_HOST
                        console host.
  --console-port CONSOLE_PORT
                        console port.
  -s SETTINGS, --settings SETTINGS
                        Setting module.
  -ls LOCALSETTINGS, --localsettings LOCALSETTINGS
                        Local setting module.
  -d, --daemon
####################################################################
- product start： 程序开始(阻塞式)
- product -d start: 程序开始(守护进程模式)
- product restart 程序重启(守护进程模式)
- product stop 程序关闭(守护进程模式)
- product status 程序状态(守护进程模式)
- product --console 开启一个console客户端，调试专用，详细请参见(https://github.com/ShichaoMa/toolkit)
- product -s settings 指定一个配置模块。(只要在sys.path中就可以找到)
- product -ls localsettings 指定一个自定义配置模块。(只要在sys.path中就可以找到)
- product -cm check-method 指定一个自定义检查方法。(只要在sys.path中就可以找到)
- product -sm spider-module 指定一个自定义的spider模块，存放自定义的spider方法。(只要在sys.path中就可以找到)
```

# DOCKER

```python
docker run -d -e REDIS_HOST=192.168.200.150 cnaafhvk/proxy-factory product start
```

# CONFIG

### CUSTOM CHECK
```python
def check(self, proxy):
    """
    自义定检查方法
    :param self: ProxyFactory对象
    :param proxy: 代理
    :return: True则代理可用，否则False
    """
    import requests
    resp = requests.get("http://2017.ip138.com/ic.asp", proxies={"http": "http://%s"%proxy})
    self.logger.info(resp.text)
    ....
    return resp.status_code < 300
```
### CUSTOM PROXY SITE METHOD

```python
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
        soup = BeautifulSoup(get_html(url, self.headers), "html")
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
```

### SETTINGS

```python
REDIS_HOST = "0.0.0.0"

REDIS_PORT = 6379

# 质量不好的代理检查的时间间隔
BAD_CHECK_INTERVAL = 60

# 质量不好的代理连续检查失败次数的最大值，超过则丢弃
FAILED_TIMES = 5

# 质量好的代理检查的时间间隔
GOOD_CHECK_INTERVAL = 60

# 抓取新代理的时间间隔
FETCH_INTERVAL = 60

LOG_LEVEL = 'DEBUG'

LOG_MAX_BYTES = 1024*1024*10

LOG_BACKUPS = 5

LOG_DIR = "/home/pi/logs"

LOG_STDOUT = False

LOG_JSON = False 
```

参考资料
[一键获取免费真实的匿名代理](https://zhuanlan.zhihu.com/p/31421147?group_id=918195817936896000)