'''
dbpool 数据库操作类
'''
import aiomysql
from tool import applog
from config import CONFIG_MYSQL


log = applog.get_log('tool.dbpool')

class DbOperate(object):
    def __init__(self):
        self.__pool = None

    @classmethod
    def instance(cls, *args, **kwargs):
        if not hasattr(DbOperate, "_instance"):
            DbOperate._instance = DbOperate(*args, **kwargs)
        return DbOperate._instance

    async def create_db_pool(self):
        log.info('create database connection pool...')
        if isinstance(self.__pool,aiomysql.pool.Pool):
            return self.__pool
        try:
            obj_pool = await aiomysql.create_pool(
            host = CONFIG_MYSQL.get('host','127.0.0.1'),
            port = CONFIG_MYSQL.get('port', 3306),
            user = CONFIG_MYSQL['user'],
            password = CONFIG_MYSQL['password'],
            db = CONFIG_MYSQL['db'],
            charset = CONFIG_MYSQL.get('charset', 'utf8'),
            autocommit = CONFIG_MYSQL.get('autocommit', True),
            maxsize = CONFIG_MYSQL.get('maxsize', 170),
            minsize = CONFIG_MYSQL.get('minsize', 10)
            )
            self.__pool = obj_pool
        except BaseException as e:
            log.error("do pool create fail:{}".format(e))
            raise 


    async def select(self, sql, args, size=None):
        log.debug("sql:{}\nargs:{}".format(sql, args))
        if self.__pool is None:
            await self.create_db_pool()
        async with (self.__pool.acquire()) as conn:
            try:
                cur = await conn.cursor(aiomysql.DictCursor)
                await cur.execute(sql.replace('?', '%s'), args or ())
                if size:
                    rs = await cur.fetchmany(size)
                else:
                    rs = await cur.fetchall()
                log.debug('rows returned: %s' % cur.rowcount)
            except BaseException as e:
                log.error("sql:{}\nargs:{}\nerror:{}".format(sql, args, e))
                return None
            return rs

    async def selectone(self, sql, args):
        log.debug("sql:{}\nargs:{}".format(sql, args))
        if self.__pool is None:
            await self.create_db_pool()
        async with (self.__pool.acquire()) as conn:
            try:
                cur = await conn.cursor(aiomysql.DictCursor)
                await cur.execute(sql.replace('?', '%s'), args or ())
                rs = await cur.fetchone()
                log.debug('rows returned: %s' % cur.rowcount)
            except BaseException as e:
                log.error("sql:{}\nargs:{}\nerror:{}".format(sql, args, e))
                return None
            return rs

    async def execute(self, sql, args):
        '''insert update delete操作使用'''
        log.debug("sql:{}\nargs:{}".format(sql, args))
        if self.__pool is None:
            await self.create_db_pool()

        async with (self.__pool.acquire()) as conn:
            try:
                cur = await conn.cursor()
                await cur.execute(sql.replace('?', '%s'), args)
                affected = cur.rowcount
            except BaseException as e:
                log.error("sql:{}\nargs:{}\nerror:{}".format(sql, args, e))
                return None
            return affected

    async def executes(self, sql, args):
        '''insert 等多条记录操作使用'''
        log.debug("sql:{}\nargs:{}".format(sql, args))
        if self.__pool is None:
            await self.create_db_pool()

        async with (self.__pool.acquire()) as conn:
            try:
                cur = await conn.cursor()
                await cur.executemany(sql.replace('?', '%s'), args)
                affected = cur.rowcount
            except BaseException as e:
                log.error("sql:{}\nargs:{}\nerror:{}".format(sql, args, e))
                return None
            return affected

    async def execute_many(self, sqllist):
        '''执行多个SQL操作'''
        log.debug("sqls:{}".format(sqllist))
        if self.__pool is None:
            await self.create_db_pool()

        async with (self.__pool.acquire()) as conn:
            try:
                result = []
                cur = await conn.cursor()
                for sqltuple in sqllist:
                    await cur.execute(sqltuple[0].replace('?', '%s'), sqltuple[1])
                    affected = cur.rowcount
                    rs = await cur.fetchone()
                    result.append((affected,rs))
                return result
            except BaseException as e:
                log.error("sql:{}\nerror:{}".format(sqllist, e))
                return None

    async def close_db_pool(self,):
        '''关闭数据库连接池'''
        # print('before:', self.__pool)
        self.__pool.close()
        await self.__pool.wait_closed()
        # print('after:', self.__pool)

    def get_connect(self,):
        ''' 从连接池中获取一个数据库连接'''
        if self.__pool.size < self.__pool.maxsize:
            return self.__pool.get()
        else:
            log.error("db poll dry!!")
            return None

# dboperate = DbOperate()

if __name__ == '__main__':
    # '''
    async def test_example():
        pool = await aiomysql.create_pool(host='127.0.0.1', port=3306,
                                          user='operatedb', password='operatedb',
                                          db='masterchef')
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT 42;")
                print(cur.description)
                (r,) = await cur.fetchone()
                assert r == 42
        pool.close()
        await pool.wait_closed()

    async def test_pool_db():
        await DbOperate().instance().create_db_pool()
        result = await DbOperate().instance().select('select id,userName from user where mobile=?', '')
        print(result)
        asyncio.get_event_loop().stop()

    async def test_exc_many():
        # 测试执行多条
        await DbOperate().instance().create_db_pool()
        # sqllist = [('select 18',()), ('select 19',())]
        sqllist = [('INSERT INTO sys_role(`name`,`status`) values(?,?)',('hellorole', 0)), ('select last_insert_id() as nid',())]
        result = await DbOperate().instance().execute_many(sqllist)
        print(result)
        for i in result:
            t = i[1]
            print(i[0], i[1])

    import asyncio
    func = asyncio.coroutine(test_exc_many)
    future = func()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(future)
    # loop.run_until_complete(close_db_pool())
    # loop.run_until_complete(get_connect())
    # '''
