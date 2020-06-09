# -*- coding:utf-8 -*-
''' 保存项目配置文件相关信息 '''
# 接口安全验证开关
import peewee_async

API_SECURITY_CHECK_OPEN = False
API_SECURITY_SECONDS = 15
API_SECURITY_SECRET = "pLEcUd0v8BXaEnOF"

# redis
# CONFIG_REDIS_URI = "redis://localhost:10086/0?encoding=utf-8"
CONFIG_REDIS_MAXCONNECT = 2000
CONFIG_REDIS_MINCONNECT = 50
CONFIG_REDIS_URI = "redis://127.0.0.1:6379/0?encoding=utf-8"

# 本地
CONFIG_MYSQL = {
    "host": '127.0.0.1',
    "port": 3306,
    "db": 'pay',
    'user': 'root',
    'password': 'root',
    'maxsize': 300,  # 连接池最大连接数量
    'minsize': 30  # 连接池最小
}

# 异步数据库
from torpeewee import MySQLDatabase


class MyDatabase(MySQLDatabase, peewee_async.PooledMySQLDatabase):
    pass


DATABASE = MyDatabase(
    'pay', host='127.0.0.1', port=3306,
    user='root', password='root')

# 建表时打开
from peewee import MySQLDatabase
# ## 本地环境
# DATABASE = MySQLDatabase(
#     'pay', host='127.0.0.1', port=3306,
#     user='root', password='root')
#
# 测试环境
# DATABASE = MySQLDatabase(
#     'pay', host='0.0.0.0', port=3306,
#     user='', password='')



# 分页配置
PAGE_SIZE = 10

# 本地日志绝对路径
# LOGPATH = '/home/server/'
LOGPATH = 'D:/test/server/'

# 阿里云短信配置:
ALIYUN_SMS_ID = ""
ALIYUN_SMS_KEY_SECRET = ""
ALIYUN_SMS_APP_SIGNNAME = ""

# oss web服务
ALIYUN_OSS_HOST = ""
ALIYUN_OSS_CALLBACK = ""  # 文件上传回调
# redis缓存相关配置:

# 用户会话有效时间 现网15天
TOKEN_TIME = 1296000
# 短信验证码有效时间
SMS_VERIFY_TIME = 300
# 短信模板
SMS_TEMPLATE_DICT = {
    "login": '',
    "register": '',
    "reset": '',
    "modifyphone": '',
    "bind": ""
}

# STS key
STS_ACCESS_KEY = ""
# STS 密钥
STS_ACCESS_KEY_SECRET = ""
# STS 上传角色
STS_UPLOAD_ROLEARN = ""
# OSS 存储空间名字
OSS_BUCKET_NAME = ""

# 短视频 VOD key
# 用户登录名称
VOD_ACCESS_KEY = ""
# VOD 密钥
VOD_ACCESS_KEY_SECRET = ""
# 阿里云视频应用ID
VOD_APP_ID = ""
# 视频处理流程ID
VOD_WORKFLOW_ID = ""
# 视频事件回调鉴权KEY
VOD_CALLBACK_AUTH_KEY = ""
# 视频回调地址
VOD_EVENT_CALLBACK_URL = ""
# 视频分类ID(区分正式或测试) 现网：1000105488
VOD_VIDEO_CATEID = ""

# 苹果第三方认证
# 苹果公钥
APPLE_PUBLIC_KEY_PEM = '''
'''
# 苹果应用ID
APPLE_GUANFAN_CLIEND_ID = ""


# 淘宝客配置
TAO_APP_KEY = ''
TAO_APP_SECRET = ''

TAO_APP_KEY_ANDROID = ''
TAO_APP_SECRET_ANDROID = ''

SENSTIVE_WORD = []
