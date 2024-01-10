import struct

"""

Des=鉴权包，作为用户发送的第一个数据包
DateTime=2023.12.4
Author=theOrange

"""


def generate_proto(auth_body):  # auth_body为 /v2/app/start 接口获取的auth_body字段
    format_str = ">IHHII"

    # header的长度, 固定为16
    HeaderLength = 16

    # version=0, body中的数据即实际发送的数据
    # version=1, body中的数据即压缩后的数据, 用zlib解压
    Version = 0

    # 消息的类型, 鉴权的类型为7
    Operation = 7

    # sequence字段 可忽略
    Sequence = 0

    # body格式为json字符串
    Body = auth_body.encode()

    # 封装鉴权包
    proto = struct.pack(format_str, HeaderLength + len(Body), HeaderLength, Version, Operation, Sequence) + Body

    return proto

