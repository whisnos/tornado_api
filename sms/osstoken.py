# -*- coding: UTF-8 -*-

import socket
import base64
import sys
import time
import datetime
import json
import hmac
from hashlib import sha1 as sha
from config import ALIYUN_SMS_ID,ALIYUN_SMS_KEY_SECRET,ALIYUN_OSS_HOST, ALIYUN_OSS_CALLBACK


APIVERSION='2015-04-01'
# 请填写您的AccessKeyId。
access_key_id = ALIYUN_SMS_ID
# 请填写您的AccessKeySecret。
access_key_secret = ALIYUN_SMS_KEY_SECRET
# host的格式为 bucketname.endpoint ，请替换为您的真实信息。
host = ALIYUN_OSS_HOST
# callback_url为 上传回调服务器的URL，请将下面的IP和Port配置为您自己的真实信息。
callback_url = ALIYUN_OSS_CALLBACK
# 用户上传文件时指定的前缀。
expire_time = 30


def get_iso_8601(expire):
    gmt = datetime.datetime.utcfromtimestamp(expire).isoformat()
    gmt += 'Z'
    return gmt


def get_token(startpath=''):
    now = int(time.time())
    expire_syncpoint = now + expire_time
    # expire_syncpoint = 1612345678
    expire = get_iso_8601(expire_syncpoint)

    policy_dict = {}
    policy_dict['expiration'] = expire
    condition_array = []
    array_item = []
    # array_item.append('eq') # 限制文件上传名字
    # array_item.append('$key')
    # array_item.append(startpath)
    array_item.append('starts-with') # 限制文件上传目录
    array_item.append('$key')
    array_item.append(startpath)
    condition_array.append(array_item)
    condition_length_item = []
    condition_length_item.append('content-length-range')
    condition_length_item.append(0)
    condition_length_item.append(10485760)
    condition_array.append(condition_length_item)
    policy_dict['conditions'] = condition_array

    policy = json.dumps(policy_dict).strip()
    policy_encode = base64.b64encode(policy.encode())
    h = hmac.new(access_key_secret.encode(), policy_encode, sha)
    sign_result = base64.encodestring(h.digest()).strip()

    callback_dict = {}
    callback_dict['callbackUrl'] = callback_url
    callback_dict['callbackBody'] = 'filename=${object}&size=${size}&mimeType=${mimeType}' \
                                    '&height=${imageInfo.height}&width=${imageInfo.width}'
    callback_dict['callbackBodyType'] = 'application/x-www-form-urlencoded'
    callback_param = json.dumps(callback_dict).strip()
    base64_callback_body = base64.b64encode(callback_param.encode())

    token_dict = {}
    token_dict['accessid'] = access_key_id
    token_dict['host'] = host
    token_dict['policy'] = policy_encode.decode()
    token_dict['signature'] = sign_result.decode()
    token_dict['expire'] = expire_syncpoint
    token_dict['dir'] = startpath
    token_dict['callback'] = base64_callback_body.decode()
    # result = token_dict
    return token_dict

if __name__ == '__main__':
    print(get_token('haibao/config'))

# def get_local_ip():
#     """
#     获取本机 IPV4 地址
#     :return: 成功返回本机 IP 地址，否则返回空
#     """
#     try:
#         csocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#         csocket.connect(('8.8.8.8', 80))
#         (addr, port) = csocket.getsockname()
#         csocket.close()
#         return addr
#     except socket.error:
#         return ""


# def do_POST(server):
#     """
#     启用 POST 调用处理逻辑
#     :param server: Web HTTP Server 服务
#     :return:
#     """
#     print("********************* do_POST ")
#     # get public key
#     pub_key_url = ''

#     try:
#         pub_key_url_base64 = server.headers['x-oss-pub-key-url']
#         pub_key = httpserver.get_pub_key(pub_key_url_base64)
#     except Exception as e:
#         print(str(e))
#         print('Get pub key failed! pub_key_url : ' + pub_key_url)
#         server.send_response(400)
#         server.end_headers()
#         return

#     # get authorization
#     authorization_base64 = server.headers['authorization']

#     # get callback body
#     content_length = server.headers['content-length']
#     callback_body = server.rfile.read(int(content_length))

#     # compose authorization string
#     auth_str = ''
#     pos = server.path.find('?')
#     if -1 == pos:
#         auth_str = server.path + '\n' + callback_body.decode()
#     else:
#         auth_str = httpserver.get_http_request_unquote(server.path[0:pos]) + server.path[pos:] + '\n' + callback_body

#     result = httpserver.verrify(auth_str, authorization_base64, pub_key)

#     if not result:
#         print('Authorization verify failed!')
#         print('Public key : %s' % (pub_key))
#         print('Auth string : %s' % (auth_str))
#         server.send_response(400)
#         server.end_headers()
#         return

#     # response to OSS
#     resp_body = '{"Status":"OK"}'
#     server.send_response(200)
#     server.send_header('Content-Type', 'application/json')
#     server.send_header('Content-Length', str(len(resp_body)))
#     server.end_headers()
#     server.wfile.write(resp_body.encode())


# def do_GET(server):
#     """
#     启用 Get 调用处理逻辑
#     :param server: Web HTTP Server 服务
#     :return:
#     """
#     print("********************* do_GET ")
#     token = get_token()
#     server.send_response(200)
#     server.send_header('Access-Control-Allow-Methods', 'POST')
#     server.send_header('Access-Control-Allow-Origin', '*')
#     server.send_header('Content-Type', 'text/html; charset=UTF-8')
#     server.end_headers()
#     server.wfile.write(token.encode())


# if '__main__' == __name__:
#     # 在服务器中, 0.0.0.0指的是本机上的所有IPV4地址, 如果一个主机有两个IP地址,
#     # 192.168.1.1 和 10.1.2.1, 并且该主机上的一个服务监听的地址是0.0.0.0, 那么通过两个IP地址都能够访问该服务。
#     # server_ip = get_local_ip() 若用户希望监听本机外网IPV4地址，则采用本行代码并注释掉下一行代码
#     server_ip = "0.0.0.0"
#     server_port = 9090
#     if len(sys.argv) == 2:
#         server_port = int(sys.argv[1])
#     if len(sys.argv) == 3:
#         server_ip = sys.argv[1]
#         server_port = int(sys.argv[2])
#     print("App server is running on http://%s:%s " % (server_ip, server_port))

#     server = httpserver.MyHTTPServer(server_ip, server_port)
#     server.serve_forever()
    # print(get_token("haibao"))