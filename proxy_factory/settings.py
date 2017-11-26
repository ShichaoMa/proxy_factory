import os

REDIS_HOST = os.environ.get('REDIS_HOST', "0.0.0.0")

REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))

# 质量不好的代理检查的时间间隔
BAD_CHECK_INTERVAL = int(os.environ.get('BAD_CHECK_INTERVAL', 5*60))

# 质量不好的代理连续检查失败次数的最大值，超过则丢弃
FAILED_TIMES = int(os.environ.get('FAILED_TIMES', 5))

# 质量好的代理检查的时间间隔
GOOD_CHECK_INTERVAL = int(os.environ.get('GOOD_CHECK_INTERVAL', 5*60))

# 抓取新代理的时间间隔
FETCH_INTERVAL = int(os.environ.get('FETCH_INTERVAL', 10*60))

LOG_LEVEL = os.environ.get('LOG_LEVEL', 'DEBUG')

LOG_MAX_BYTES = int(os.environ.get('LOG_MAX_BYTES', 1024*1024*10))

LOG_BACKUPS = int(os.environ.get('LOG_BACKUPS', 5))

LOG_DIR = os.environ.get('LOG_DIR', "logs")

LOG_STDOUT = eval(os.environ.get('LOG_STDOUT', "True"))

LOG_JSON = eval(os.environ.get('LOG_JSON', "False"))