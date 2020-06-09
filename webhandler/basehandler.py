import tornado.web
import urllib.parse
import tornado.options
import time

from tornado.escape import json_decode
from tool import applog, function
from tool.async_redis_pool import RedisOperate
from config import SENSTIVE_WORD, API_SECURITY_CHECK_OPEN, API_SECURITY_SECONDS, API_SECURITY_SECRET

log = applog.get_log('webhandler.basehandler')
log.setLevel('INFO')
redisdb = RedisOperate().instance()


class BaseHandler(tornado.web.RequestHandler):
    def options(self):
        # no body
        self.set_status(204)
        self.finish()

    def get_current_user(self):
        ''' 验证用户是否登录 '''
        user = self.get_secure_cookie("cmsadmincookie")
        if user:
            return self.send_cms_msg(0, 'ok', user)
        else:
            return self.send_cms_msg(1, 'fail', None)
        # return self.get_secure_cookie("cmsadmincookie")

    def send_cms_msg(self, code, msg='ok', result=None):
        '''设置CMS接口回调内容'''
        responsedict = {}
        responsedict.setdefault('code', code)
        responsedict.setdefault('msg', msg)
        responsedict.setdefault('data', result)
        self.write(responsedict)
        raise tornado.web.Finish()
        # return self.finish()

    def send_message(self, success, code, msg='ok', result=None):
        '''send error message'''
        responsedict = {}
        responsedict.setdefault('success', success)
        responsedict.setdefault('code', code)
        responsedict.setdefault('message', msg)
        responsedict.setdefault('result', result)
        self.write(responsedict)
        # tornado.web.Finish()
        return self.finish()

    def send_msg(self, success, code, msg='ok', result=None):
        '''send error message'''
        responsedict = {}
        responsedict.setdefault('success', success)
        responsedict.setdefault('code', code)
        responsedict.setdefault('message', msg)
        responsedict.setdefault('result', result)
        self.write(responsedict)
        # tornado.web.Finish()
        return self.finish()

    def set_default_headers(self):
        ''' 设置header头部解决跨域 '''
        self.set_header("Access-Control-Allow-Origin", "*")  # 这个地方可以写域名
        self.set_header("Access-Control-Allow-Headers", "*")
        # self.set_header("Access-Control-Allow-Headers", "token")

    async def clear_user_session(self):
        '''清除用户的会话'''
        if self.token_key is None:
            return
        rd_del = await RedisOperate().instance().del_data(self.token_key)
        if rd_del != 1:
            log.warning('删除token失败,{},{}'.format(self.token_key, rd_del))

    def prepare(self):
        ''' 所有请求都经过这里 '''
        if API_SECURITY_CHECK_OPEN:
            '''需要验证'''
            # if len(self.request.body) == 0:
            #     return
            # if self.request.uri.endswith("timestamp"):
            #     # 时间戳接口不需要验证.
            #     return

            # 获得加密时间戳
            getstamp = self.get_body_argument('stamp')
            try:
                stamp = int(getstamp)
            except Exception as e:
                self.send_message(False, 5001, "非法参数", None)

            # 获得签名
            sign = self.get_body_argument('sign')
            server_stamp = int(time.time())
            if server_stamp - stamp > API_SECURITY_SECONDS or server_stamp - stamp < 0:
                self.send_message(False, 5002, "无效,非法访问", None)

            # 签名生成规则: md5(密钥+参数(排序)+时间戳)
            server_sign = function.MD5encrypt(API_SECURITY_SECRET + getstamp)
            print(server_sign)
            if server_sign == sign:
                return
            else:
                # 签名错误
                self.send_message(False, 5003, "错误,非法访问", None)
        else:
            # 接口不需要安全认证
            return

    def verify_arg_legal(self, value, description, is_sensword=False, is_len=False, olen=10, **kwargs):
        ''' 校验参数是否合法 '''
        value = value.strip()
        if is_sensword:
            # 需要检查敏感词
            for word in SENSTIVE_WORD:
                if word in value:
                    return self.send_message(False, 1999, '操作失败! {} 出现敏感词:{}'.format(description, word))
                else:
                    continue
        if is_len:
            # 需要判断长度
            if len(value) > olen:
                return self.send_message(False, 1998, '操作失败! {} 内容长度大于:{}'.format(description, olen))
            else:
                pass
        if kwargs.get('is_not_null'):
            if value == '':
                return self.send_message(False, 1995, '操作失败! {} 不能为空'.format(description))

        if kwargs.get('is_num'):
            # 判断是否是纯数字
            try:
                if isinstance(value, str):
                    int(value)
                else:
                    return self.send_message(False, 1995, '操作失败! {} 不是数字'.format(description))
            except ValueError as e:
                return self.send_message(False, 1997, '操作失败! {} 不是数字'.format(description))

        if kwargs.get('ucklist') or kwargs.get('uchecklist'):
            # 列表内容校验
            if value not in kwargs.get('user_check_list'):
                return self.send_message(False, 1996, '操作失败! {} 内容不合法'.format(description))

        if kwargs.get('img'):
            # 图片内容校验
            # print("img check", value)
            if value.endswith('.jpg') is False and value.endswith('.png') is False and value.endswith('.jpeg') is False:
                return self.send_message(False, 1995, '操作失败! {} 图片格式错误'.format(description))
            # if value.count('/') !=4:
            #     return self.send_message(False, 1994, '操作失败! {} 内容格式错误'.format(description))

        return value

    def verify_arg_num(self, value, description, **kwargs):
        ''' 校验参数是否合法 '''
        value = value.strip()
        if kwargs.get('ucklist'):
            # 列表内容校验
            if value not in kwargs.get('user_check_list'):
                return self.send_msg(False, 1996, '操作失败! {} 内容不合法'.format(description))

        if kwargs.get('is_num'):
            # 判断是否是纯数字
            try:
                if isinstance(value, str):
                    return int(value)
                else:
                    return self.send_msg(False, 1995, '操作失败! {} 不是数字'.format(description))
            except ValueError as e:
                return self.send_msg(False, 1997, '操作失败! {} 不是数字'.format(description))




    def get_session(self):
        # 返回用户的会话
        if hasattr(self, 'token_session'):
            return self.token_session
        else:
            return None

    def get_session_key(self):
        # 返回保存在redis的会话的key
        return self.token_key

    async def get_login(self):
        ''' 获取用户的登录信息 '''
        if self.request.headers.get('token', False) is False:
            return False
            # self.send_message(False, 2001, '参数错误,请先登录')
        token = self.request.headers.get('token')
        key = "token:{}".format(token)
        # token_exists = await RedisOperate().instance().exists(key)
        rdget = await RedisOperate().instance().get_data(key)
        if rdget is not None:
            # 会话存在
            self.token_key = key
            try:
                self.token_session = json_decode(rdget)
                return self.token_session
            except Exception as e:
                log.error("数据:{},异常:{}".format(rdget, e))
                # self.send_message(False, 2001, '用户数据异常')
                return False
        else:
            # self.send_message(False, 9999, '请先登录')
            return False

    def on_finish(self):
        ''' 所有请求调用结束时执行 '''
        # print(self.request.query,self.request.path, self.request.full_url)
        # print(dir(self.request))
        # log.info(self.request.protocol + '://' + self.request.host + self.request.uri)

        userid = None  # 未登录的用户
        # print(hasattr(self, 'token_session'))
        if hasattr(self, 'token_session'):
            token = self.get_session()
            userid = token.get('id', 0)  # 0表示未知用户

        # print(self.request.remote_ip,type(self.request.remote_ip))

        log.info("port:{}| userid: {}| ip:{}| real-ip:{}| uri: {}| query: {}| body: {}".format(
            tornado.options.options.port,
            userid,
            self.request.remote_ip,
            self.request.headers.get("X-Real-IP", ""),
            self.request.uri,
            self.request.query,
            urllib.parse.unquote(self.request.body.decode('utf-8'), errors='replace')))
        return


def check_login(func):
    """
    拦截配置，装饰器
    :param func:
    :return:
    """

    async def wrapper(self, *args, **kwargs):
        # if self.request.query_arguments.get('token',False) is False:
        #     self.send_message(False, 2001, '参数错误,请先登录')
        if self.request.headers.get('token', False) is False:
            self.send_msg(False, 2001, '参数错误,请先登录')

        token = self.request.headers.get('token')
        key = "token:{}".format(token)
        # token_exists = await RedisOperate().instance().exists(key)
        rdget = await RedisOperate().instance().get_data(key)
        if rdget is not None:
            # 会话存在
            self.token_key = key
            try:
                self.token_session = json_decode(rdget)
            except Exception as e:
                log.error("数据:{},异常:{}".format(rdget, e))
                self.send_msg(False, 2002, '用户数据异常')
            return await func(self, *args, **kwargs)
        else:
            self.send_msg(False, 9999, '请先登录')

    return wrapper
