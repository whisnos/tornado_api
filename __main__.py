import tornado.ioloop
import tornado.options
from peewee_async import Manager

import router
from config import DATABASE

if __name__ == "__main__":
    tornado.options.define("port", default=6868, help="run on the given port", type=int)
    tornado.options.parse_command_line()
    # threading.Thread(target=lambda:torloop.spawn_callback(userobjall.api_callback), name='thread_api_callback').start()
    # workers = gen.multi([userobjall.get_api_result() for b in range(30)])
    # await workers
    # aliyunsms.send_aliyun_register_sms()
    tornadoloop = tornado.ioloop.IOLoop.current()
    # tornadoloop.spawn_callback(lambda: DbOperate().instance().create_db_pool())
    # tornadoloop.spawn_callback(lambda: RedisOperate().instance().create_redis_pool())
    app = router.make_app()
    app.settings.update(xheader=True)
    app.settings.update(debug=True)
    app.settings.update(autoreload=True)
    app.settings.update(serve_traceback=False)
    app.listen(tornado.options.options.port)
    objects = Manager(DATABASE)
    # No need for sync anymore!
    DATABASE.set_allow_sync(False)
    app.objects = objects
    tornadoloop.start()
