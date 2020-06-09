import base64
import hmac
from hashlib import sha1
import time
import uuid
import urllib.parse
from tool.asynchttp import async_http_response
from config import STS_UPLOAD_ROLEARN, STS_ACCESS_KEY, STS_ACCESS_KEY_SECRET, OSS_BUCKET_NAME

access_key_id = STS_ACCESS_KEY;
access_key_secret = STS_ACCESS_KEY_SECRET;
endpoint = 'https://sts.aliyuncs.com'
# endpoint = 'http://oss-cn-shenzhen.aliyuncs.com'
APIVERSION='2015-04-01'

def percent_encode(string):
    res = urllib.parse.quote(string, '')
    res = res.replace('+', '%20')
    res = res.replace('*', '%2A')
    res = res.replace('%7E', '~')
    return res

def compute_signature(parameters, access_key_secret):
    # 给字典排序
    sortedParameters = sorted(parameters.items(), key=lambda parameters: parameters[0])
    # print(sortedParameters)

    canonicalizedQueryString = ''
    for (k,v) in sortedParameters:
        canonicalizedQueryString += '&' + percent_encode(k) + '=' + percent_encode(v)

    stringToSign = 'GET&%2F&' + percent_encode(canonicalizedQueryString[1:])
    # print(stringToSign)
    keystr = access_key_secret + "&"
    h = hmac.new(keystr.encode('utf-8'), stringToSign.encode('utf-8'), sha1)
    signature = base64.encodestring(h.digest()).strip()
    return signature

def compose_url(user_params):
    # 获取URL
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    parameters = {
            'Format'        : 'JSON',
            'Version'       :  APIVERSION,
            'AccessKeyId'   : access_key_id,
            'SignatureVersion'  : '1.0', 
            'SignatureMethod'   : 'HMAC-SHA1', 
            'SignatureNonce'    : str(uuid.uuid4()), 
            'Timestamp'         : time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }
    for key in user_params.keys():
        parameters[key] = user_params[key]

    signature = compute_signature(parameters, access_key_secret)
    parameters['Signature'] = signature
    url = endpoint + "/?" + urllib.parse.urlencode(parameters)
    return url

def get_STS_security_token_url(user_phone='', roloArn='', policy='', action='AssumeRole', seconds='900'):
    # 获取STS进行临时验证信息的URL
    send_param = {}
    send_param.setdefault('Action', action)
    send_param.setdefault('RoleSessionName', user_phone)
    send_param.setdefault('RoleArn', roloArn)
    send_param.setdefault('Policy', policy)
    send_param.setdefault('DurationSeconds', seconds)
    return compose_url(send_param)


async def upload_caipu_sts_token(user_id, seconds='900'):
    '''获取上传菜谱所需要的STStoken'''
    rolearn = STS_UPLOAD_ROLEARN
    policy = '''{"Version":"1","Statement":[{"Effect":"Allow","Action":["oss:PutObject"],"Resource":["acs:oss:*:*:[bucket]/[userspace]/caipu/*/*/*/*"]}]}'''.replace('[userspace]', str(user_id)).replace('[bucket]', OSS_BUCKET_NAME)
    get_token_url = get_STS_security_token_url("uid.{}".format(user_id), rolearn, policy, seconds=seconds)
    return await async_http_response(get_token_url, datatype='json')

async def upload_dongtai_sts_token(user_id, seconds='900'):
    '''获取上传动态所需要的STStoken'''
    rolearn = STS_UPLOAD_ROLEARN
    policy = '{"Version":"1","Statement":[{"Effect":"Allow","Action":["oss:PutObject"],"Resource":["acs:oss:*:*:[bucket]/[userspace]/pushimg/*/*/*/*"]}]}'.replace('[userspace]', str(user_id)).replace('[bucket]', OSS_BUCKET_NAME)
    get_token_url = get_STS_security_token_url("uid.{}".format(user_id), rolearn, policy, seconds=seconds)
    return await async_http_response(get_token_url, datatype='json')

async def upload_person_img_sts_token(user_id, seconds='900'):
    '''上传个人头像信息所需要的STStoken'''
    rolearn = STS_UPLOAD_ROLEARN
    policy = '{"Version":"1","Statement":[{"Effect":"Allow","Action":["oss:PutObject"],"Resource":["acs:oss:*:*:[bucket]/[userspace]/userimg/*/*/*/*"]}]}'.replace('[userspace]', str(user_id)).replace('[bucket]', OSS_BUCKET_NAME)
    get_token_url = get_STS_security_token_url("uid.{}".format(user_id), rolearn, policy, seconds=seconds)
    return await async_http_response(get_token_url, datatype='json')

async def upload_topic_img_sts_token(user_id, seconds='900'):
    '''上传主题封面STStoken'''
    rolearn = STS_UPLOAD_ROLEARN
    policy = '{"Version":"1","Statement":[{"Effect":"Allow","Action":["oss:PutObject"],"Resource":["acs:oss:*:*:[bucket]/[userspace]/topic/*/*/*/*"]}]}'.replace('[userspace]', str(user_id)).replace('[bucket]', OSS_BUCKET_NAME)
    get_token_url = get_STS_security_token_url("uid.{}".format(user_id), rolearn, policy, seconds=seconds)
    return await async_http_response(get_token_url, datatype='json')

async def upload_person_auth_img_sts_token(user_id, seconds='900'):
    '''上传高级验证需要的STStoken'''
    rolearn = STS_UPLOAD_ROLEARN
    policy = '{"Version":"1","Statement":[{"Effect":"Allow","Action":["oss:PutObject"],"Resource":["acs:oss:*:*:[bucket]/[userspace]/certifyimg/*/*/*/*"]}]}'.replace('[userspace]', str(user_id)).replace('[bucket]', OSS_BUCKET_NAME)
    get_token_url = get_STS_security_token_url("uid.{}".format(user_id), rolearn, policy, seconds=seconds)
    return await async_http_response(get_token_url, datatype='json')
    # rolearn = "acs:ram::1873866368954155:role/actor-test-app-userauth-writer"
    # policy = '{"Version":"1","Statement":[{"Effect":"Allow","Action":["oss:PutObject"],"Resource":["acs:oss:*:*:[bucket]-verifyimg/[userspace]/certifyimg/*/*/*/*"]}]}'.replace('[userspace]', str(user_id)).replace('[bucket]', OSS_BUCKET_NAME)
    # get_token_url = get_STS_security_token_url("uid.{}".format(user_id), rolearn, policy, seconds=seconds)
    # return await async_http_response(get_token_url, datatype='json')

async def get_person_auth_img_sts_token(user_id, seconds='900'):
    '''下载高级验证图片的STStoken'''
    rolearn = STS_UPLOAD_ROLEARN
    policy = '{"Version":"1","Statement":[{"Effect":"Allow","Action":["oss:GetObject"],"Resource":["acs:oss:*:*:[bucket]-verifyimg/[userspace]/certifyimg/*/*/*/*"]}]}'.replace('[userspace]', str(user_id)).replace('[bucket]', OSS_BUCKET_NAME)
    get_token_url = get_STS_security_token_url("uid.{}".format(user_id), rolearn, policy, seconds=seconds)
    return await async_http_response(get_token_url, datatype='json')


if __name__ == '__main__':
    async def test_upload_caipu_token():
        sucess, result = await upload_caipu_sts_token('1')
        print(sucess, result)

    async def test_upload_pushimg_token():
        sucess, result = await upload_dongtai_sts_token('chdongtaitest')
        print(sucess, result)

    async def test_upload_person_img_sts_token():
        sucess, result = await upload_person_img_sts_token('13950126971')
        print(sucess, result)

    async def test_upload_person_auth_img_sts_token():
        sucess, result = await upload_person_auth_img_sts_token('13950126971')
        print(sucess, result)

    async def test_get_person_auth_img_sts_token():
        sucess, result = await get_person_auth_img_sts_token('13950126971')
        print(sucess, result)

    import tornado.ioloop
    tornado.ioloop.IOLoop.current().run_sync(test_upload_person_auth_img_sts_token)