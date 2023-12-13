
"""
Des BiliSocket依赖文件，包括连接的wss服务器地址，获取真实房间号，
    获取鉴权用的token同时生成鉴权包，生成心跳包
@Author thetheOrange
Time 2023/12/8
"""

import json
import struct

import jsonpath
import requests

from staticData import headers, cookies_dict

wss_addr = "wss://broadcastlv.chat.bilibili.com/sub"


# 获取真实房间号
def get_room_id(room_id):
    # 获取真实房间号的api地址
    url = "https://api.live.bilibili.com/room/v1/Room/room_init"

    # 请求的房间号参数
    params = {"id": room_id}  # room_id 为int类型
    r = requests.get(url=url, params=params, headers=headers)
    # 获取真实房间号
    real_room_id = jsonpath.jsonpath(r.json(), "$..data.room_id")[0]
    return real_room_id


# 生成鉴权包，需要先获取到token
def generate_certificate(real_room_id, UID):
    # 获取密钥的api地址
    url = "https://api.live.bilibili.com/xlive/web-room/v1/index/getDanmuInfo"

    # 请求的房间号参数
    params = {"id": real_room_id,
              "type": 0}  # real_room_id 为int类型

    # 获取鉴权用的token
    r = requests.get(url=url, params=params, headers=headers, cookies=cookies_dict)
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
    if cookies_dict:
        buvid = cookies_dict.get("buvid3")
    else:
        buvid = ""
    # body 为json字符串
    Body = {"buvid": buvid,
            "key": token,
            "platform": "web",
            "protover": 2,
            "roomid": real_room_id,
            "type": 2,
            "uid": UID
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
