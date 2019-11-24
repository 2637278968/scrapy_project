import redis
from redis import ConnectionPool
import threading
from scrapyProject.config import RedisConfig


class ioRedis(object):
    _instance_lock = threading.Lock()

    def __init__(self, host=RedisConfig.HOST, port=RedisConfig.PORT, max_connections=RedisConfig.MAX_CONNECTIONS,
                 db=RedisConfig.DB):
        self.host = host
        self.port = port
        self.max_connections = max_connections
        self.db = db
        # 连接池
        self.POOL = ConnectionPool(host=self.host, port=self.port, max_connections=self.max_connections,
                                   decode_responses=True, db=self.db)
        self.__conn = redis.Redis(connection_pool=self.POOL)

    def hmset(self, key, data):
        result = self.__conn.hmset(key, data)
        print(result)

    def hmget(self, key, detail_key):
        """
        redis的哈希get
        :param key:
        :param detail_key:
        :return:
        """
        result = self.__conn.hmget(key, detail_key)
        return result

    def hgetall(self, key):
        """
        redis的哈希getall
        :param key:
        :return:
        """
        return self.__conn.hgetall(key)

    def sadd(self, key, *args):
        self.__conn.sadd(key, *args)

    def sunionstore(self, key1, key2, key3):
        return self.__conn.sunionstore(key1, key2, key3)

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            # 加入线程锁防止多线程可初始化多个线程
            with ioRedis._instance_lock:
                if not hasattr(cls, '_instance'):
                    ioRedis._instance = super().__new__(cls)

        return ioRedis._instance

    # 使用连接池来管理redis


if __name__ == '__main__':
    ioredis = ioRedis()
    ioredis.sadd('hha', 'book-title', 'book_author')
    ioredis.sadd('hha','heihei')
    #
    # ioredis.hmset('book-傲世丹神-1', {
    #     'chapter_title': 'title',
    #     'chapter_condet': 'content',
    #     'chapter_id': 1
    # })
    # tmp = ioredis.hgetall('book-傲世丹神-2')
    # # res = json.loads(tmp)
    # print(tmp)
    # print(type(tmp))
    # tmp = ioredis.hmget('book', 'title-风华绝代')[0].decode()
    # print(tmp)
    # print(type(json.loads(tmp)))
    # res = ioredis.hmget('book', 'title-权妃之帝医风华')
    # print(res)
    # def test(*args):
    #     print(args)
    #     print(*args)
    #
    #
    # test(1, 2, 3)
