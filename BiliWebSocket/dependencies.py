"""
Des BiliSocket依赖文件，包括连接的wss服务器地址，获取真实房间号，
    获取鉴权用的token同时生成鉴权包，生成心跳包
@Author thetheOrange
Time 2023/12/8
"""

import json
import struct
import time
import urllib
from functools import reduce
from hashlib import md5

import jsonpath
import requests

from staticData import headers, cookies_dict

wss_addr = "wss://broadcastlv.chat.bilibili.com/sub"

mixinKeyEncTab = [
    46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35, 27, 43, 5, 49,
    33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13, 37, 48, 7, 16, 24, 55, 40,
    61, 26, 17, 0, 1, 60, 51, 30, 4, 22, 25, 54, 21, 56, 59, 6, 63, 57, 62, 11,
    36, 20, 34, 44, 52
]


def get_mixin_key(orig: str):
    '对 imgKey 和 subKey 进行字符顺序打乱编码'
    return reduce(lambda s, i: s + orig[i], mixinKeyEncTab, '')[:32]


def encode_wbi(params: dict, img_key: str, sub_key: str):
    '为请求参数进行 wbi 签名'
    mixin_key = get_mixin_key(img_key + sub_key)
    curr_time = round(time.time())
    params['wts'] = curr_time  # 添加 wts 字段
    params = dict(sorted(params.items()))  # 按照 key 重排参数
    # 过滤 value 中的 "!'()*" 字符
    params = {
        k: ''.join(filter(lambda chr: chr not in "!'()*", str(v)))
        for k, v
        in params.items()
    }
    query = urllib.parse.urlencode(params)  # 序列化参数
    wbi_sign = md5((query + mixin_key).encode()).hexdigest()  # 计算 w_rid
    params['w_rid'] = wbi_sign
    return params


def get_wbi_keys() -> tuple[str, str]:
    '获取最新的 img_key 和 sub_key'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Referer': 'https://www.bilibili.com/'
    }
    resp = requests.get('https://api.bilibili.com/x/web-interface/nav', headers=headers)
    resp.raise_for_status()
    json_content = resp.json()
    img_url: str = json_content['data']['wbi_img']['img_url']
    sub_url: str = json_content['data']['wbi_img']['sub_url']
    img_key = img_url.rsplit('/', 1)[1].split('.')[0]
    sub_key = sub_url.rsplit('/', 1)[1].split('.')[0]
    return img_key, sub_key


img_key, sub_key = get_wbi_keys()


# 获取真实房间号
def get_room_id(room_id: int):
    # 获取真实房间号的api地址
    url = "https://api.live.bilibili.com/room/v1/Room/room_init"

    # 请求的房间号参数
    params = {"id": room_id}  # room_id 为int类型
    signed_params = encode_wbi(
        params=params,
        img_key=img_key,
        sub_key=sub_key
    )
    query = urllib.parse.urlencode(signed_params)
    r = requests.get(url=url, params=query, headers=headers)
    # 获取真实房间号
    real_room_id = jsonpath.jsonpath(r.json(), "$..data.room_id")[0]
    return real_room_id


# 生成鉴权包，需要先获取到token
def generate_certificate(real_room_id, UID):
    # 获取密钥的api地址
    url = "https://api.live.bilibili.com/xlive/web-room/v1/index/getDanmuInfo"

    # 请求的房间号参数
    params = {"id": real_room_id,
              "type": 0
              }  # real_room_id 为int类型
    signed_params = encode_wbi(
        params=params,
        img_key=img_key,
        sub_key=sub_key
    )
    query = urllib.parse.urlencode(signed_params)
    # 获取鉴权用的token
    r = requests.get(url=url, params=query, headers=headers)
    code: int | str = r.json().get("code")
    if code != 0:
        raise Exception("状态码错误")
    token = jsonpath.jsonpath(r.json(), "$..data.token")[0]
    # 生成鉴权包

    format_str = ">IHHII"
    # header的长度, 固定为16
    HeaderLength = 16
    # protocol 协议类型，鉴权包为special类型，即参数为1
    Protocol = 1
    # type 操作类型
    Type = 7
    # sequence字段 可忽略
    Sequence = 2
    # 获取cookie中的buvid3参数
    buvid = cookies_dict.get("buvid3")
    # body 为json字符串
    Body = {"buvid": buvid,
            "key": token,
            "platform": "web",
            "protover": 2,
            "roomid": real_room_id,
            "type": 2,
            "uid": 0
            }  # 这里的协议类型指的是后续会收到的压缩类型
    Body = json.dumps(Body).encode()

    # 封装成鉴权包
    certificate_pack = struct.pack(format_str, HeaderLength + len(Body), HeaderLength, Protocol, Type, Sequence) + Body
    return certificate_pack


# 生成心跳包
def generate_heartbeat():
    format_str = ">IHHII"
    # header的长度, 固定为16
    HeaderLength = 16
    # protocol 协议类型，心跳包为special类型，即参数为1
    Protocol = 1
    # type 操作类型
    Type = 2
    # sequence字段 可忽略
    Sequence = 2
    # body 为字符串
    Body = "[Object object]".encode()

    # 封装成心跳包
    heartbeat = struct.pack(format_str, HeaderLength + len(Body), HeaderLength, Protocol, Type, Sequence) + Body
    return heartbeat
