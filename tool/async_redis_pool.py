from tornado.escape import json_encode, json_decode
from tool import applog
from config import CONFIG_REDIS_URI, CONFIG_REDIS_MAXCONNECT, CONFIG_REDIS_MINCONNECT
import aioredis

log = applog.get_log('tool.async_redis_pool')

class RedisOperate(object):
    def __init__(self):
        self.obj_pool = None

    @classmethod
    def instance(cls, *args, **kwargs):
        if not hasattr(RedisOperate, "_instance"):
            RedisOperate._instance = RedisOperate(*args, **kwargs)
        return RedisOperate._instance

    async def create_redis_pool(self):
        log.info('create redis connection pool...')
        self.obj_pool = await aioredis.create_pool(CONFIG_REDIS_URI, minsize=CONFIG_REDIS_MINCONNECT, maxsize=CONFIG_REDIS_MAXCONNECT)

    async def execute(self, *arg):
        # 总的执行方法
        if self.obj_pool is None:
            await self.create_redis_pool()
        try:
            return await self.obj_pool.execute(*arg)
        except Exception as e:
            log.error('redis 执行异常:{}'.format(e))
            return None

    async def close_pool(self):
        self.obj_pool.close()
        await self.obj_pool.wait_closed()

    async def set_data(self, key, value):
        '''set data with (key, value)
        '''
        if isinstance(value, dict):
            return await self.execute('SET', key, json_encode(value))
        else:
            return await self.execute('SET', key, value)

    async def get_data(self, key):
        '''get data by key
        '''
        return await self.execute('GET', key)
 
    async def del_data(self, *key):
        '''delete cache by key
        '''
        return await self.execute('DEL', *key)

    async def exprie(self, key, etime):
        '''exprie time set by key'''
        return await self.execute('EXPIRE', key, etime)

    async def exists(self, key):
        return await self.execute('EXISTS', key)

    async def set_and_expire(self, key, value, etime):
        ''' 设置key,并增加过期时间 '''
        rdsave = await self.set_data(key, value)
        if rdsave != 'OK':
            return False
        rdexp = await self.exprie(key, etime)
        if rdexp != 1:
            return False
        return True

    async def hash_set(self, *hset):
        ''' 设置hash HMSET值 '''
        # print(*hset)
        return await self.execute('HMSET', *hset)

    async def hash_get(self, key, field):
        ''' 设置hash HMSET值 '''
        return await self.execute('HGET', key, field)

    async def hash_hexists(self, key, field):
        ''' 检查hash HEXISTS值 '''
        return await self.execute('HEXISTS', key, field)

    async def hash_mget(self, *hget):
        ''' 设置hash HMSET值 '''
        return await self.execute('HMGET', *hget)

    async def hash_hincrby(self, key, field, value=1):
        ''' 设置hash HINCRBY '''
        return await self.execute('HINCRBY', key, field, value)

    async def set_sadd(self, key,*add_arg):
        ''' 添加Set sadd值 '''
        return await self.execute('SADD', key, *add_arg)

    async def set_size(self, key):
        ''' 返回Set 成员数量 '''
        return await self.execute('SCARD', key)

    async def set_exists(self, key, member):
        ''' 检查Set 成员是否存在 '''
        return await self.execute('SISMEMBER', key, member)

    async def set_getall(self, key):
        ''' 获取Set SMEMBERS 所有成员变量 '''
        return await self.execute('SMEMBERS', key)

    async def set_sinter(self, *key):
        ''' 获取Set所有成员变量 '''
        return await self.execute('SINTER', *key)

    async def set_sdiff(self, *key):
        ''' 获取Set 差集 '''
        return await self.execute('SDIFF', *key)

    async def set_sunion(self, *key):
        ''' 获取Set 差集 '''
        return await self.execute('SUNION', *key)

    async def set_srem(self, key, *members):
        ''' Set SREM 删除成员变量 '''
        return await self.execute('SREM', key, *members)

    async def set_srand(self, key, num=1):
        ''' Set SRANDMEMBER 返回范围内的随机数 '''
        return await self.execute('SRANDMEMBER', key, num)

if __name__ == '__main__':
    async def test():
        rdget = await RedisOperate().instance().set_sadd("website", "g.com", "google.com", "www.g.cn", "www.123.cn")
        print(rdget)
        await RedisOperate().instance().close_pool()

    async def test_set_srand():
        rdget = await RedisOperate().instance().set_srand("recommenddongtai",12)
        print(rdget)
        await RedisOperate().instance().close_pool()


    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_set_srand())