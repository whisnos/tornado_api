import uuid
import datetime
import hmac
import base64
from urllib.parse import urlencode, quote
from config import ALIYUN_SMS_ID,ALIYUN_SMS_KEY_SECRET,ALIYUN_SMS_APP_SIGNNAME

class AliyunSMSAdapter(object):
    def __init__(self):
        self.format = "JSON"
        self.version = "2017-05-25"
        self.key = ALIYUN_SMS_ID
        self.secret = ALIYUN_SMS_KEY_SECRET
        self.signature_app = ALIYUN_SMS_APP_SIGNNAME
        self.signature_method = "HMAC-SHA1"
        self.signature_version = "1.0"
        self.signature_nonce = str(uuid.uuid4())
        self.timestamp = datetime.datetime.utcnow().isoformat("T")
        self.region_id = 'cn-hangzhou'

        self.gateway = 'https://dysmsapi.aliyuncs.com'
        self.action = "SendSms"
        self.template = ""
        self.params = {}
        self.phones = []

    def get_signature_url(self, phone, template, params):
        self.phones.append(phone)
        self.params = params
        self.template = template
        query_string = self.build_query_string()
        url = self.gateway + '/?' + query_string
        return url

    def build_query_string(self):
        query = []
        query.append(("Format", self.format))
        query.append(("Version", self.version))
        query.append(("AccessKeyId", self.key))
        query.append(("SignatureMethod", self.signature_method))
        query.append(("SignatureVersion", self.signature_version))
        query.append(("SignatureNonce", self.signature_nonce))
        query.append(("Timestamp", self.timestamp))
        query.append(("RegionId", self.region_id))
        query.append(("Action", self.action))
        query.append(("SignName", self.signature_app))
        query.append(("TemplateCode", self.template))
        query.append(("PhoneNumbers", ",".join(self.phones)))
        params = "{"
        for param in self.params:
            params += "\"" + param + "\"" + ":" + "\"" + str(self.params[param]) + "\"" + ","
        params = params[:-1] + "}"
        query.append(("TemplateParam", params))
        query = sorted(query, key=lambda key: key[0])
        query_string = ""
        for item in query:
            query_string += quote(item[0], safe="~") + "=" + quote(item[1], safe="~") + "&"
        query_string = query_string[:-1]
        tosign = "GET&%2F&" + quote(query_string, safe="~")
        secret = self.secret + "&"
        hmb = hmac.new(secret.encode("utf-8"), tosign.encode("utf-8"), "sha1").digest()
        signature_str = quote(base64.standard_b64encode(hmb).decode("ascii"), safe="~")
        query_string += "&" + "Signature=" + signature_str
        return query_string

if __name__ == '__main__':
    sms = AliyunSMSAdapter()
    # :param phone: 手机号
    # :param sign: 短信签名
    # :param template: 短信模板
    # :param params: 模板变量
    # sms.send_singe(phone, sign, template, params)
    print(sms.get_signature_url("", 'SMS_172882935', {"code": 123456}))
    print(hmac.new(b'abc', b'asfdasdfasfasfasd', "md5").digest())
