import uuid
import datetime
import hmac
import base64
from urllib.parse import urlencode, quote
from config import VOD_ACCESS_KEY, VOD_ACCESS_KEY_SECRET

class AliyunMediaAdapter(object):
    def __init__(self):
        self.format = "JSON"
        self.version = "2017-03-21"
        self.key = VOD_ACCESS_KEY
        self.secret = VOD_ACCESS_KEY_SECRET
        self.signature_method = "HMAC-SHA1"
        self.signature_version = "1.0"
        self.signature_nonce = str(uuid.uuid4())
        self.timestamp = datetime.datetime.utcnow().isoformat("T")
        self.region_id = 'cn-shanghai'
        self.gateway = 'http://vod.cn-shanghai.aliyuncs.com'
        self.action = "CreateUploadVideo"
        self.params = [] # 获取参数元祖参数对[("Title","你好未来"),('a','b')]

    def get_signature_url(self, action, params):
        self.action = action
        self.params = params
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
        query.append(("Action", self.action))
        query.extend(self.params)
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
    media = AliyunMediaAdapter()
    param = []
    param.append(("Title", "我的标题"))
    param.append(("FileName", "test.avi"))
    # param.append(("", ""))
    # param.append(("", ""))
    print(media.get_signature_url("CreateUploadVideo", param))
