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

LOG_LEVEL = 'DEBUG'
LOG_MAX_BYTES = 1024*1024*10
LOG_BACKUPS = 5
LOG_DIR = "logs"
LOG_STDOUT = True
LOG_JSON = False
