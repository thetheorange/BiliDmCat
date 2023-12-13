
"""
Des bilibili 弹幕机类，后端获取弹幕数据文件，同时对弹幕信息进行处理
    将数据在前端qt界面上展示
@Author thetheOrange
Time 2023/12/8
"""

import asyncio
import json
import zlib

import websockets

from Logger.Logger import my_logger
from BiliWebSocket.dependencies import get_room_id, generate_certificate, generate_heartbeat, wss_addr
from staticData import headers, global_signal, UID


class BiliSocket:
    def __init__(self, room_id):

        # 获取真实房间号
        self.real_room_id = get_room_id(room_id)
        # 获取用户UID
        self.UID = UID
        # wss服务器地址
        self.wss_addr = wss_addr
        # 创建心跳包
        self.heartbeat = generate_heartbeat()

        # 项目关闭标志
        self.__stop_flag = False

    # 项目关闭接口
    def stop(self):
        self.__stop_flag = True
        my_logger.info("STOP")

    # 连接wss服务器
    async def start(self):
        async with websockets.connect(uri=self.wss_addr, user_agent_header=headers) as wss_app:
            # 发送鉴权包
            await wss_app.send(generate_certificate(real_room_id=self.real_room_id, UID=self.UID))

            heartbeat_t = asyncio.create_task(self.__heartbeat(wss_app))
            recv_msg_t = asyncio.create_task(self.__recv_msg(wss_app))

            Tasks = [heartbeat_t, recv_msg_t]
            await asyncio.wait(Tasks)

    # 每20秒发送一次心跳包
    async def __heartbeat(self, wss_app):
        try:
            while not self.__stop_flag:
                await asyncio.sleep(0.1)
                if wss_app:
                    await wss_app.send(self.heartbeat)
                    await asyncio.sleep(20)
        except Exception as e:
            my_logger.info(f"[ASYNC HEARTBEAT]: {e}")

    # 接收推送消息
    async def __recv_msg(self, wss_app):
        try:
            while not self.__stop_flag:
                await asyncio.sleep(0.1)
                if wss_app:
                    # 接收数据并处理
                    data = await wss_app.recv()
                    self.get_dm_msg(data)
        except Exception as e:
            my_logger.info(f"[ASYNC REVMSG]: {e}")

    # 提取弹幕消息
    def get_dm_msg(self, data):
        # 获取数据包长度，协议类型和操作类型
        packet_len = int(data[:4].hex(), 16)
        proto = int(data[6:8].hex(), 16)
        op = int(data[8:12].hex(), 16)

        # 若数据包是连着的，则根据第一个数据包的长度进行切分
        if len(data) > packet_len:
            self.get_dm_msg(data[packet_len:])
            data = data[:packet_len]

        # 判断协议类型，若为2则用zlib解压
        if proto == 2:
            data = zlib.decompress(data[16:])
            self.get_dm_msg(data)
            return
        if op == 3:
            my_logger.info("HeartBeat")
        # 判断消息类型
        if op == 5:
            try:
                # 解析json
                content = json.loads(data[16:].decode())
                # 发送数据
                global_signal.MsgData.emit(content)
            except Exception as e:
                my_logger.error(f"[GETDATA ERROR]: {e}")
