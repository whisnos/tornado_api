import logging
from tornado.httpclient import AsyncHTTPClient,HTTPRequest
from tornado.escape import json_decode
from tool import applog

log = applog.get_log('tool.asynchttp')


AsyncHTTPClient.configure(
    None, defaults={'User-Agent': 'AlibabaCloud (Windows 10;AMD64) Python/3.6.6 Core/2.13.3 python-requests/2.18.3', 'Accept-Encoding': 'gzip, deflate', 'Accept': '*/*', 'Connection': 'keep-alive', 'x-sdk-invoke-type': 'common', 'x-sdk-client': 'python/2.0.0', 'Content-Length': '0'})

# log.warning('dfasd')

async def async_http_response(url, method='GET', post_data=None, headers={}, datatype='str'):
    '''访问公共接口, 返回值(true,str)'''
    # log.debug('request,method:{},url:{},post_data:{}'.format(method, url, post_data))
    # post_str = "&".join([k+'='+str(v) for k,v in post_data.items()])
    reqobj = HTTPRequest(url, method=method, body=post_data, headers=headers, 
        connect_timeout=10, request_timeout=10, validate_cert=False)

    response = await AsyncHTTPClient().fetch(reqobj, raise_error=False)
    rsp_str = response.body.decode("utf-8") if response.body is not None else ''
    log.debug('\nrequest,url:{},post:{}\nresponse,code:{}'.format(url, post_data, response.code))
    if response.code == 200:
        try:
            return (True, json_decode(rsp_str)) if datatype == 'json' else (True, rsp_str)
        except Exception as e:
            log.error("url:{},post:{}\nerror:{}\nresponse:\n{}".format(url,post_data, e, rsp_str))
            return False,'json 解码错误'
    else:
        log.warning("url:{},post:{}\ncode:{}\nerror:{}\nresponse:\n{}".format(url,post_data, response.code, response.error, rsp_str))
        return False, rsp_str


if __name__ == '__main__':
    async def aliyuncs():
        sucess, result = await async_http_response('https://dysmsapi.aliyuncs.com')
        print(sucess)
    import tornado.ioloop
    tornado.ioloop.IOLoop.current().run_sync(aliyuncs)



