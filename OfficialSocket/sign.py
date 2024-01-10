import hashlib
import hmac
import json
import random
import time
from hashlib import sha256

"""

Des=生成鉴权所需的请求头
Author=theOrange
DateTime=2023.12.4

"""


def generate_sign(params, access_key, secret):  # key, secret为开发者秘钥
    # 使用MD5加密请求体
    md5 = hashlib.md5()
    params = json.dumps(params)
    md5.update(params.encode())  # params data = {"code": self.code,"app_id": self.app_id}
    md5data = md5.hexdigest()

    # 生成时间戳
    ts = time.time()
    # 生成随机数
    nonce = random.randint(1, 100000) + time.time()

    # 生成请求头映射
    headerMap = {
        "x-bili-timestamp": str(int(ts)),
        "x-bili-signature-method": "HMAC-SHA256",
        "x-bili-signature-nonce": str(nonce),
        "x-bili-accesskeyid": access_key,
        "x-bili-signature-version": "1.0",
        "x-bili-content-md5": md5data,
    }

    # 拼接字符串, 生成签名
    headerList = sorted(headerMap)
    headerStr = ''

    for key in headerList:
        headerStr = headerStr + key + ":" + str(headerMap[key]) + "\n"
    headerStr = headerStr.rstrip("\n")
    app_secret = secret.encode()
    data = headerStr.encode()

    signature = hmac.new(app_secret, data, digestmod=sha256).hexdigest()

    # 生成请求头
    headerMap["Authorization"] = signature
    headerMap["Content-Type"] = "application/json"
    headerMap["Accept"] = "application/json"

    # print(headerMap)

    return headerMap


# generate_sign({"room_id": 1111}, "9576151", 1706598850402)
