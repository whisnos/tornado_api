import hashlib
import uuid

def MD5encrypt(text):
    ''' md5加密 '''
    m5 = hashlib.md5(text.encode('utf-8'))
    return m5.hexdigest()

def get_uuid():
    # 获取一个随机字符串
    return str(uuid.uuid4())


def verify_num(value):
    # 判断是否是纯数字
    try:
        if isinstance(value, str):
            return int(value)
        else:
            return False
    except ValueError as e:
        return False

if __name__ == '__main__':
    import time
    stamp = int(time.time())
    sign = MD5encrypt('pLEcUd0v8BXaEnOF' + str(stamp))
    print(stamp)
    print(sign)