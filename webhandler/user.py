import tornado.web
from tool.dbpool import DbOperate
from tool.async_redis_pool import RedisOperate
from sms.aliyunsms import send_aliyun_send_sms
from webhandler.basehandler import BaseHandler,check_login
from tool import applog,function
from config import TOKEN_TIME, SMS_VERIFY_TIME, SMS_TEMPLATE_DICT
from webhandler.cacheoperate import CacheUserinfo
import time

log = applog.get_log('webhandler.user')
# 用户密码及验证码登录

class LoginHandler(BaseHandler):
    async def get(self):
        # print('query:', self.request.query)
        # print('body:', self.request.body)
        # print(dir(self.request))
        # print(self.request.query_arguments)
        self.write('login')

    async def post(self):
        login_type = self.get_body_argument('type')
        phone = self.get_body_argument('phone')
        # print('body_arguments', self.request.body)
        # b'phone=13950126971&password=123123&type=1'
        if 0<len(phone) >= 20:
            return self.send_message(False, 1001, '手机参数错误')
        if login_type == '1':
            # 账号密码登录
            pw = self.get_body_argument('password')
            if 0<len(pw)> 20:
                return self.send_message(False, 1002, '参数错误')
            sucess, code, message, result = await user_handler_obj.login_password(phone, pw)
            return self.send_message(sucess, code, message, result)
        elif login_type == '2':
            verify_code = self.get_body_argument('verify')
            if 0<len(verify_code)>6:
                return self.send_message(False, 1003, '错误的验证码')
            sucess, code, message ,result = await user_handler_obj.login_verify(phone, verify_code)
            return self.send_message(sucess, code, message, result)
        else:
            return self.send_message(False, 1004, '错误的登录类型')

class RegisterHandler(BaseHandler):
    ''' 用户注册 '''
    async def post(self):
        password = self.get_body_argument('password')
        phone = self.get_body_argument('phone')
        # tag = self.get_body_argument('tag')
        verify = self.get_body_argument('verify')
        if len(password) > 20:
            return self.send_message(False, 1006, '密码过长')
        if len(phone) > 20:
            return self.send_message(False, 1007, '手机号错误')
        # if len(tag) > 100:
        #     return self.send_message(False, 1008, '标签内容过长')
        if len(verify) > 6:
            return self.send_message(False, 1009, '验证码错误')

        sucess, code, message, result = await user_handler_obj.register(phone, password, verify, tag='')
        return self.send_message(sucess, code, message, result)


class SendSmsHandler(BaseHandler):
    ''' 发送验证码短信 '''
    async def post(self):
        phone = self.get_body_argument('phone')
        t = self.get_body_argument('type')
        if len(phone) >= 15 or len(t)>2:
            return self.send_message(False, 1005, '参数错误')

        user_session = await self.get_login()
        if user_session is False:
            # 未登录
            myid=0
        else:
            # 获取关注状态
            myid = user_session.get('id',0)

        sucess, code, message = await user_handler_obj.send_sms(myid, t,phone)
        return self.send_message(sucess, code, message)

class RestPasswordHandler(BaseHandler):
    ''' 修改密码 '''
    @check_login
    async def post(self):
        password = self.get_body_argument('password')
        if len(password)> 20:
            return self.send_message(False, 1006, '参数错误')
        sucess, code, message = await user_handler_obj.reset_password(self.get_session().get('id', 0), password)
        await self.clear_user_session()
        return self.send_message(sucess, code, message)

class ModifyPhonedHandler(BaseHandler):
    '''修改手机号'''
    @check_login
    async def post(self):
        password = self.get_body_argument('password')
        phone = self.get_body_argument('phone')
        phone = phone.strip()
        verify_code = self.get_body_argument('verify')
        sucess, code, message = await user_handler_obj.modify_phone(self.get_session(), phone, verify_code, password)
        if sucess:
            await self.clear_user_session()
        return self.send_message(sucess, code, message)


class PersonInfoHandler(BaseHandler):
    '''获取个人信息'''
    @check_login
    async def post(self):
        userid = self.get_session().get('id', 0)
        sucess, code, message,result = await user_handler_obj.person_detail(userid)
        return self.send_message(sucess, code, message,result)

# 退出登录
class LogoutHandler(BaseHandler):
    @check_login
    async def post(self):
        await self.clear_user_session()
        return self.send_message(True, 0, '退出登录成功')


class ModifyInfoHandler(BaseHandler):
    ''' 修改用户个人信息 '''
    @check_login
    async def post(self):
        # nickname, img, sex, birthday, address, perinfo,  taste, tag
        userid = self.get_session().get('id', 0)
        nickname = self.get_body_argument('nickname')
        name_check = True
        if len(nickname)>40:
            return self.send_message(False,1001,'昵称过长')
        img = self.get_body_argument('img')
        if len(img)>255:
            return self.send_message(False,1001,'用户头像地址错误')
        sex = self.get_body_argument('sex')
        if sex !='男' and sex !='女':
            return self.send_message(False,1001,'性别格式错误')
            
        birthday = self.get_body_argument('birthday')
        if len(birthday)>20:
            return self.send_message(False,1001,'生日格式错误')
        address = self.get_body_argument('address')
        if len(address)>255:
            return self.send_message(False,1001,'地址内容过长')
        perinfo = self.get_body_argument('perinfo')
        if len(perinfo)>500:
            return self.send_message(False,1001,'个人简介过长')
        taste = self.get_body_argument('taste')
        if len(taste)>20:
            return self.send_message(False,1001,'口味格式错误')
        if taste not in ('酸','甜','苦','辣','咸','麻辣','酸甜','咸苦','酸苦','微辣','变态辣','超级咸','腻人甜','无敌酸','清淡','通吃','重口味'):
            return self.send_message(False,1001,'口味内容错误')
            
        tag = self.get_body_argument('tag')
        if len(tag)>100:
            return self.send_message(False,1001,'标签内容过长')

        isex = 1 if sex == '男' else 0
        sucess, code, message, result = await user_handler_obj.update_user_info(userid,nickname, img, isex, birthday, address, perinfo, taste, tag)
        return self.send_message(sucess, code, message,result)


class SubmitAdvancedHandler(BaseHandler):
    '''提交高级验证资料'''
    @check_login
    async def post(self):
        # certify_name, real_name, phone, address, docurl, perinfo
        userid = self.get_session().get('id', 0)
        certify_name = '吃货达人'
        # certify_name = self.get_body_argument('certifyname')
        # if len(certify_name)>30:
        #     return self.send_message(False,1001,'类型过长')

        realname = self.get_body_argument('realname')
        if len(realname)>20:
            return self.send_message(False,1001,'名字过长')

        phone = self.get_session().get('phone', 0)
        # phone = self.get_body_argument('phone')
        # if len(phone)>20:
        #     return self.send_message(False,1001,'手机号过长')

        address = self.get_body_argument('address')
        if len(address)>255:
            return self.send_message(False,1001,'地址过长')

        certifyimg = self.get_body_argument('certifyimg')
        if len(certifyimg)>255:
            return self.send_message(False,1001,'证书地址过长')

        perinfo = self.get_body_argument('perinfo')
        if len(perinfo)>500:
            return self.send_message(False,1001,'个人介绍过长')

        sucess, code, message,result = await user_handler_obj.submit_user_advanced_certify(userid, certify_name, realname, phone, address, certifyimg, perinfo)
        return self.send_message(sucess, code, message, result)


class UserHandler(object):
    """用户处理模块"""
    def __init__(self):
        self.verify_str = "phone.verify.{}:{}"
        self.taoken_str = "token:{}"

    async def register(self, phone, password, verify_code, tag):
        ''' 用户注册 '''
        verify_key = "phone.verify.register:{}".format(phone)
        res = await DbOperate().instance().select('select id from user where mobile=? limit 1', (phone))
        if len(res) > 0:
            return False, 1007, '手机号已注册',None

        rdget = await RedisOperate().instance().get_data(verify_key)
        if rdget == verify_code:
            # 验证码一致
            import random
            # nickname = 'u{}'.format(random.randint(1000000,9999999))
            nickname = '饭友_{}'.format(''.join(random.sample('1z2yx5w6v7u8t9srqpon3m4lkji0hgfedcba',5)))
            insert_sql = "INSERT into user (`userName`,`mobile`,`password`) values (?,?,?)"
            md5pw = function.MD5encrypt(password)
            dbsave = await DbOperate().instance().execute(insert_sql, (nickname, phone, md5pw))
            if dbsave is None:
                return False, 3200,'保存数据出错,请重试' ,None
            # 获取新用户的ID
            userid = await DbOperate().instance().select('select id from user where mobile=? limit 1', (phone))
            if len(userid) != 1:
                return False, 3004,'获取注册数据出错,请重试！' ,None
            # 更新token到redis
            uid = function.get_uuid()
            key = self.taoken_str.format(uid)
            value = {'id': userid[0].get('id'), 'phone': phone, 'login': time.time(), 'loginby':1}
            rdsave = await RedisOperate().instance().set_data(key, value)
            if rdsave != 'OK':
                return False, 3005, '保存注册数据缓存出错,请重试', None
            rdsup = await RedisOperate().instance().exprie(key, TOKEN_TIME)
            if rdsup != 1:
                return False, 3008, '更新缓存出错,请重试', None
            else:
                return True, 0, '注册成功',{'token':uid}
        else:
            return False, 2001, '验证码错误',None

    async def send_sms(self, myid, t, phone):
        '''短信类型 t 类型 phone 手机号'''
        key = "phone.verify.{}:{}"
        res = await DbOperate().instance().select('select id from user where mobile=? limit 1', (phone))
        if res is None:
            return False, 3001, '访问异常'
            
        temple_code = ''
        if t == '1':
            # 登录
            if len(res) == 0:
                return False, 1007, '用户未注册'
            key = key.format('login', phone)
            temple_code = SMS_TEMPLATE_DICT.get('login')
        elif t == '2':
            # 注册
            if len(res) > 0:
                return False, 1008, '用户已注册'
            key = key.format('register', phone)
            temple_code = SMS_TEMPLATE_DICT.get('register')
        elif t == '3':
            # 忘记密码,重置密码
            if len(res) == 0:
                return False, 1009, '用户未注册'
            key = key.format('login', phone)
            temple_code = SMS_TEMPLATE_DICT.get('reset')
        elif t == '4':
            # 修改手机
            if len(res) != 0:
                return False, 1010, '用户已注册'
            key = key.format('modifyphone', phone)
            temple_code = SMS_TEMPLATE_DICT.get('modifyphone')
        elif t == '5':
            # 第三方登录绑定
            # if len(res) == 0:
            #     return False, 1009, '用户未注册'
            # # 登录绑定不需要验证手机号注册还是未注册
            key = key.format('bind', phone)
            temple_code = SMS_TEMPLATE_DICT.get('bind')
        else:
            return False, 1011, 'type参数错误'

        sucess, requestid, verify_code = await send_aliyun_send_sms(phone, temple_code)
        # sucess, requestid, verify_code = (True, '123','909090')
        if sucess:
            # 发送成功
            log.info('sms send:{},{},{}'.format(key,phone,verify_code))
            # 保存到redis
            rdsave = await RedisOperate().instance().set_data(key, verify_code)
            # print('redis:', rdsave)
            if rdsave != 'OK':
                return False, 3100, '保存缓存出错,请重试'

            rdsup = await RedisOperate().instance().exprie(key, SMS_VERIFY_TIME)
            # print('redis update:', rdsup)
            # 更新五分钟过期时间
            if rdsup != 1:
                return False, 3101, '更新缓存出错,请重试'

            dbsave = await DbOperate().instance().execute("INSERT into sms_log (`type`,`phone`,`code`) values (?,?,?)", (t, phone, verify_code))
            # print('mysql save:', dbsave)
            if dbsave is None:
                return False, 3200,'保存数据出错,请重试'
            return True, 0, '发送成功'
        else:
            return False, 2001, '号码:{}, 发送短信失败, 错误码:{}'.format(phone, verify_code)

    async def login_verify(self, phone, verify_code):
        ''' 使用手机验证码登录 '''
        res = await DbOperate().instance().select('select id from user where mobile=? and status=0 limit 1', (phone))
        # if len(res) != 1:
        #     return False, 1001, '手机号或者验证码错误', None
        verify_key = "phone.verify.login:{}".format(phone)
        rdget = await RedisOperate().instance().get_data(verify_key)
        if rdget == verify_code:
            # 手机验证码正确
            uid = function.get_uuid()
            key = self.taoken_str.format(uid)
            if len(res) == 1:
                # 已存在用户登录
                value = {'id': res[0].get('id'), 'phone': phone, 'login': time.time(), 'loginby':1}
                rdsave = await RedisOperate().instance().set_data(key, value)
                if rdsave != 'OK':
                    return False, 3001, '保存缓存出错,请重试', None
                # 删除验证码缓存
                rd_del = await RedisOperate().instance().del_data(verify_key)
                if rd_del == 1:
                    # 删除验证码成功
                    await CacheUserinfo(res[0].get('id')).createCache(force_update=True)
                    return True, 0, '登录成功', {'token':uid}
                else:
                    return False, 3002, '清空缓存出错,请重试', None

            else:
                return False, 1001, '用户未注册', None
        else:
            return False, 1012, '验证码或手机号错误', None

    async def login_password(self, phone, password):
        ''' 使用密码登录'''
        pwMD5 = function.MD5encrypt(password)
        res = await DbOperate().instance().select('select id,userName from user where mobile=? and password=? and status=0 limit 1', (phone, pwMD5))
        if len(res) == 1:
            # 登录成功
            # 添加用户会话增加到redis
            uid = function.get_uuid()
            key = self.taoken_str.format(uid)
            value = {'id':res[0].get('id'), 'nickname':res[0].get('userName'), 'phone': phone, 'login': time.time(), 'loginby':0}
            rdsave = await RedisOperate().instance().set_data(key, value)
            if rdsave != 'OK':
                return False, 3007, '保存缓存出错,请重试', None
            rdsup = await RedisOperate().instance().exprie(key, TOKEN_TIME)
            if rdsup != 1:
                return False, 3008, '更新缓存出错,请重试', None
            await CacheUserinfo(res[0].get('id')).createCache(force_update=True)
            return True, 0, '登录成功', {'token':uid}
        else:
            return False, 2001, '用户名或密码错误', None

    async def reset_password(self, uid, password):
        ''' reset password'''
        md5pw = function.MD5encrypt(password)
        dbsave = await DbOperate().instance().execute("update user set password= ? where id = ?", (md5pw, uid))
        if dbsave is None:
            return False, 3014, '密码保存失败,请重试'

        if dbsave == 0:
            log.warning("需要验证新旧密码是否一致,id:{} ,当前:{}".format(uid, md5pw))
            return True, 0, '已重置密码,请尝试登录{}'.format(dbsave)
        else:
            return True, 0, '重置密码成功'

    async def modify_phone(self, session, newphone, verify_code, password):
        ''' 修改手机号 '''
        # 新旧手机号不能一样
        db_phone_read = await DbOperate().instance().select('select id from user where mobile=? limit 1', (newphone))
        if len(db_phone_read)>0:
            return False, 2003, '手机号已注册'

        oldphone = session.get('phone', '')
        userid = session.get('id', 0)
        if oldphone == newphone:
            return False, 1014, '新旧号码不能相同'
        # 匹配手机验证码
        verify_key = "phone.verify.modifyphone:{}".format(newphone)
        rdget = await RedisOperate().instance().get_data(verify_key)
        # 匹配密码是否正确
        db_read = await DbOperate().instance().select('select password from user where id=? limit 1', (userid))
        if verify_key is None:
            return False, 2004, '短信验证码未发送！'
        if len(db_read)==0:
            return False, 2005, '用户不存在'

        if rdget == verify_code and db_read[0].get('password', '') == function.MD5encrypt(password):
            db_up = await DbOperate().instance().execute('update user set mobile = ? where id= ?', (newphone, userid))
            if db_up is not None:
                # 删除验证码
                rd_del = await RedisOperate().instance().del_data(verify_key)
                # 清除用户session
                return True, 0, '手机号修改成功'
            else:
                return False, 2006, '手机号保存失败！'
        else:
            return False, 1015, '验证码错误或密码错误'
        # if 验证码 and 密码 正确；
            # 更新手机号
        # else:
            # 验证码或密码错误

    async def person_detail(self, userid):
        '''获取个人信息''' 
        sql = "SELECT `userName` as 'name', `mobile` as `phone`, `headImg` as 'img',`sex`,`birthday`,`address`, `personalProfile` as 'personinfo',`tag`, `taste`,`certificationStatus` as 'verify_status' FROM user where id = ?  and status=0"
        db_read = await DbOperate().instance().select(sql, (userid))
        # print(db_read)
        if len(db_read) == 0:
            return False, 2007, '未知的用户', None
        resutl = db_read[0]
        # sql_taste = "SELECT tasteName AS 'taste',sort from taste_info where userId=? and status=0"
        # db_taste_list = await DbOperate().instance().select(sql_taste, (userid))
        # sql_tag = "SELECT tagName AS 'tag',sort from tag_info where userId=? and status=0"
        # db_tag_list = await DbOperate().instance().select(sql_tag, (userid))
        # print(db_taste_list, db_tag_list)
        # resutl.setdefault('tastlist', db_taste_list)
        # resutl.setdefault('taglist', db_tag_list)
        return True, 0, 'ok', resutl

    async def update_user_info(self, userid, nickname, img, sex, birthday, address, perinfo,  taste, tag):
        ''' 更新个人用户信息 '''
        # 检查 昵称 是否已经有人注册

        chek_nickname_sql = 'select id from user where userName=?'
        db_read = await DbOperate().instance().select(chek_nickname_sql, (nickname))
        if len(db_read) > 2:
            return False, 1001, '昵称已存在', None
        if len(db_read) == 1:
            if db_read[0].get('id') != userid:
                return False, 1001, '昵称已存在', None

        up_user_sql = 'update user set userName = ?, headImg = ?, sex = ?, birthday = ?, address = ?, personalProfile = ?, taste = ?, tag = ?, updateTime=? where id= ?'
        db_up = await DbOperate().instance().execute(up_user_sql, (nickname, img, sex, birthday, address, perinfo,  taste, tag, time.strftime('%Y-%m-%d %H:%M:%S'), userid))
        if db_up is not None:
            await CacheUserinfo(userid).createCache(force_update=True)
            return True, 0, '修改个人信息成功', None
        else:
            return False, 3012, '修改个人信息异常，请重试', None

    async def submit_user_advanced_certify(self, userid, certify_name, real_name, phone, address, docurl, perinfo):
        ''' 提交高级认证 '''
        # 检查用户是否已经提交过
        chek_user_sql = 'select id from certification_apply where userId=? and (status=1 or status=2)'
        db_read = await DbOperate().instance().select(chek_user_sql, (userid))
        print(db_read)
        if len(db_read) > 0:
            return False, 1001, '认证资料之前已提交,等待审核!', None

        up_advanced_sql = 'INSERT into certification_apply(`userId`, `certifiedId`, `realName`, `phone`, `address`, `docUrl`, `personalProfile`) values (?,?,?,?,?,?,?)'
        db_up = await DbOperate().instance().execute(up_advanced_sql, (userid, '吃货达人', real_name, phone, address, docurl, perinfo))

        up_user_sql = 'update user set certificationStatus=1, certified=? where id = ?'
        db_user_up = await DbOperate().instance().execute(up_user_sql, ('吃货达人', userid))
        if db_user_up is None:
            return False, 3012, '修改提交认证状态异常,请重试', None

        if db_up is not None:
            return True, 0, '提交高级认证成功', None
        else:
            return False, 3013, '提交高级认证失败，请重试', None

user_handler_obj = UserHandler()
# print(id(user_handler_obj))

if __name__ == '__main__':
    pass
    # async def test_user_sendsms():
    #     obj = UserHandler()
    #     await RedisOperate().instance().create_redis_pool()
    #     await DbOperate().instance().create_db_pool()
    #     code, result = await obj.send_sms('1','13950126971')
    #     print(code, result)

    # import asyncio
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(test_user_sendsms())
    




