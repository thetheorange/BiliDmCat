import struct

"""

Des=心跳包，保证与服务器的健康连接
DateTime=2023.12.4
Author=theOrange

"""


def generate_heart():
    format_str = ">IHHII"

    # header的长度, 固定为16
    HeaderLength = 16

    # version=0, body中的数据即实际发送的数据
    # version=1, body中的数据即压缩后的数据, 用zlib解压
    Version = 0

    # 消息的类型, 心跳的类型为2
    Operation = 2

    # sequence字段 可忽略
    Sequence = 0

    # body默认为空
    Body = b""

    # 封装心跳包
    HeartBeat = struct.pack(format_str, HeaderLength + len(Body), HeaderLength, Version, Operation, Sequence) + Body

    return HeartBeat


