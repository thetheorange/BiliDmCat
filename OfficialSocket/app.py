import asyncio
import json
import zlib

import jsonpath
import requests
import websockets
from aiohttp import ClientSession

import heartBeat
import proto
import sign

"""

Des=项目开启, 关闭接口
DateTime=2023.12.4
Author=theOrange

"""


class app:

    def __init__(self, code, app_id):
        # 开发者秘钥
        self.__key = ""
        self.__secret = ""

        # code为主播身份码, app_id为项目id
        self.code = code
        self.app_id = app_id
        # 统一域名
        self.url = "https://live-open.biliapi.com"
        # 获取心跳包
        self.heart = heartBeat.generate_heart()
        # wss服务器地址
        self.wss_address = None
        # 鉴权body
        self.auth_body = None
        # 场次id
        self.game_id = None
        # 项目关闭标志
        self.stop_flag = None

    # 发送鉴权包
    async def __send_auth_proto(self, ws_app):
        await ws_app.send(proto.generate_proto(self.auth_body))

    # 每隔20秒发送一次心跳包
    async def __send_heart_beat(self, ws_app):
        app_heart_beat_api = self.url + "/v2/app/heartbeat"
        heart_beat_data = heartBeat.generate_heart()
        # 发送项目心跳, 保证连接
        async with ClientSession() as Session:
            async with Session.post(url=app_heart_beat_api,
                                    headers=sign.generate_sign(params={"game_id": self.game_id}, access_key=self.__key,
                                                               secret=self.__secret),
                                    json={"game_id": self.game_id}) as r:
                heart_reply = await r.text()

        # 若服务器有回应, 则发送长连心跳
        if heart_reply:
            # 发送长连心跳
            await ws_app.send(heart_beat_data)
            await asyncio.sleep(20)

    # 长连
    async def __long_connect(self):
        handle_data_t = asyncio.create_task(self.__handle_data())
        print_data_t = asyncio.create_task(self.__print_data())
        Tasks = [handle_data_t, print_data_t]

        await asyncio.wait(Tasks)

        async with websockets.connect(uri=self.wss_address) as ws_app:
            # 发送鉴权包
            await self.__send_auth_proto(ws_app)
            print("[START]")
            # 每隔20秒发送一次心跳包
            while self.stop_flag is None:
                await self.__send_heart_beat(ws_app)
                # 接收wss服务器返回的数据
                self.ws_app_data = await ws_app.recv()
                # 处理数据handle_data(ws_app_data)
                await self.__handle_data()

    # 数据处理
    async def __handle_data(self):
        # 解析数据包
        # 整个包的长度
        PacketLength = int(self.ws_app_data[:4].hex(), 16)
        # 请求头的长度
        HeaderLength = int(self.ws_app_data[4:6].hex(), 16)
        # 版本信息
        Version = int(self.ws_app_data[6:8].hex(), 16)

        # 判断Version
        # 若为2则使用zlib解压数据包
        if Version == 2:
            # 使用zlib解压version为2的数据包
            self.ws_app_data = zlib.decompress(self.ws_app_data)

        # 若两个数据包连着发送
        if len(self.ws_app_data) > PacketLength:
            self.ws_app_data = self.ws_app_data[:PacketLength]

        await self.__print_data()

    # 打印弹幕信息
    async def __print_data(self):
        # 消息类型
        Operation = int(self.ws_app_data[8:12].hex(), 16)
        # 保留字段 可忽略
        Sequence = int(self.ws_app_data[12:16].hex(), 16)
        # 请求体 json字符串
        Body = self.ws_app_data[16:].decode()

        # Operation 3 服务器收到心跳包的回复
        if Operation == 3:
            print("[HeartBeat]")

        # Operation 5 服务器发送的弹幕消息包
        if Operation == 5:
            # 解析json
            Body = json.loads(Body)
            cmd = jsonpath.jsonpath(Body, "$.cmd")[0]

            # 判断cmd类型
            # 获取弹幕信息
            if cmd == "LIVE_OPEN_PLATFORM_DM":
                # 用户昵称
                uname = jsonpath.jsonpath(Body, "$..data.uname")
                # 弹幕内容
                msg = jsonpath.jsonpath(Body, "$..data.msg")
                # 粉丝勋章
                fans_medal = jsonpath.jsonpath(Body, "$..data.fans_medal_name")

                # 格式化打印
                print(f"[DM]{fans_medal}[{uname}]>>>{msg}")

            # 获取礼物信息
            if cmd == "LIVE_OPEN_PLATFORM_SEND_GIFT":
                # 用户昵称
                uname = jsonpath.jsonpath(Body, "$..data.uname")
                # 礼物名
                gift_name = jsonpath.jsonpath(Body, "$..data.gift_name")
                # 粉丝勋章
                fans_medal = jsonpath.jsonpath(Body, "$..data.fans_medal_name")

                # 格式化打印
                print(f"[GIFT]{fans_medal}[{uname}]>>>{gift_name}")

            # 获取付费留言
            if cmd == "LIVE_OPEN_PLATFORM_SUPER_CHAT":
                # 用户昵称
                uname = jsonpath.jsonpath(Body, "$..data.uname")[0]
                # sc内容
                sc_msg = jsonpath.jsonpath(Body, "$..data.message")
                # 支付费用
                sc_pay = jsonpath.jsonpath(Body, "$..data.rmb")

                # 格式化输出
                print(f"[SC]{sc_pay}[{uname}]>>>{sc_msg}")

            # 付费礼物下线
            if cmd == "LIVE_OPEN_PLATFORM_SUPER_CHAT_DEL":
                pass

            # 付费大航海
            if cmd == "LIVE_OPEN_PLATFORM_GUARD":
                pass

            # 点赞信息
            if cmd == "LIVE_OPEN_PLATFORM_LIKE":
                pass

    # 开启项目
    def start(self):
        # 项目开启接口
        app_start_api = self.url + "/v2/app/start"

        data = {
            "code": self.code,
            "app_id": self.app_id
        }

        # 连接
        r = requests.post(url=app_start_api,
                          headers=sign.generate_sign(params=data, access_key=self.__key, secret=self.__secret),
                          json=data)

        app_info = r.content.decode()
        app_info = json.loads(app_info)

        # 获取wss长连地址
        self.wss_address = jsonpath.jsonpath(app_info, "$.data.websocket_info.wss_link[0]")[0]
        # 获取用于鉴权的auth_body
        self.auth_body = jsonpath.jsonpath(app_info, "$.data.websocket_info.auth_body")[0]
        # 获取game_id
        self.game_id = jsonpath.jsonpath(app_info, "$.data.game_info.game_id")[0]

        # 调用异步长连方法
        asyncio.run(self.__long_connect())

    # 关闭项目
    def stop(self):
        # 项目关闭接口
        app_stop_api = self.url + "/v2/app/end"

        data = {
            "app_id": self.app_id,
            "game_id": self.game_id
        }

        # 启用项目关闭接口
        r = requests.post(url=app_stop_api,
                          headers=sign.generate_sign(params=data, access_key=self.__key, secret=self.__secret),
                          json=data, verify=False)

        app_stop_info = r.json()

        # 获取关闭成功的标识
        self.stop_flag = jsonpath.jsonpath(app_stop_info, "$.code")
