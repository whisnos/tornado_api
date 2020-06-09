from random import randint
from tool.asynchttp import async_http_response
from tool import applog
from sms.buildsmsurl import AliyunSMSAdapter

log = applog.get_log('sms.aliyunsms')

async def send_aliyun_send_sms(phone, t_code):
    # 发送短信
    verifi_code = randint(100000,999999)
    sms = AliyunSMSAdapter()
    url = sms.get_signature_url(phone, t_code, {"code": verifi_code})
    success, result = await async_http_response(url, datatype='json')
    if success:
        if result.get('Code') == 'OK':
            log.debug("url:{}\nresponse:{}".format(url, result))
            return True, result.get('RequestId'), verifi_code
        else:
            log.error("url:{},errorcode:{},RequestId:{}".format(url, result.get('Code'), result.get('RequestId')))
            return False, result.get('RequestId'), result.get('Code')
    else:
        from tornado.escape import json_decode
        result = json_decode(result)
        log.error("url:{},errorcode:{},RequestId:{}".format(url, result.get('Code'), result.get('RequestId')))
        return False, result.get('RequestId'), result.get('Code')
    # {
    #     "Message":"OK",
    #     "RequestId":"2184201F-BFB3-446B-B1F2-C746B7BF0657",
    #     "BizId":"197703245997295588^0",
    #     "Code":"OK"
    # }

if __name__ == '__main__':
    pass
    # import asyncio
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(send_aliyun_send_sms('13950126971', 'SMS_172882935'))
