REDIS_HOST = "0.0.0.0"
REDIS_PORT = 6379

# 质量不好的代理检查的时间间隔
BAD_CHECK_INTERVAL = 5*60
# 质量不好的代理连续检查失败次数的最大值，超过则丢弃
FAILED_TIMES = 5
# 质量好的代理检查的时间间隔
GOOD_CHECK_INTERVAL = 5*60
# 抓取新代理的时间间隔
FETCH_INTERVAL = 10*60
# redis中用来存放有效代理的set
GOOD_PROXY_SET = "good_proxies"
# redis中用来存放无效代理的hash
BAD_PROXY_HASH = "bad_proxies"

HEADERS = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:41.0) '
                      'Gecko/20100101 Firefox/41.0',
        'Accept': 'text/html,application/xhtml+xml,'
                  'application/xml;q=0.9,*/*;q=0.8',
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
    }