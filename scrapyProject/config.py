# 全本的url方便拼接
BASER_URL = 'http://quanben.io'
# 获取每一章详细的url
DETAIL_CONTENT_URL = 'http://www.quanben.io/index.php'

# over_write_flag 是否覆盖标志
OVER_WRITE_FLAG = False
# 超时时间，超过了就重传requests
REQUEST_TIMEOUT = 20

# 开启线程数
CONCURRENT_REQUESTS = 32


class RedisConfig(object):
    HOST = 'localhost'
    PORT = 6379
    MAX_CONNECTIONS = 100
    DB = 1
