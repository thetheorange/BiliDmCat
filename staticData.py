"""
Des 项目全局变量，包含自定义信号，个性化选项参数(如窗口透明度等)及websocket连接时所需的必要参数
@Author thetheOrange
Time 2023/12/11
"""

import json
import os

import jsonpath
from PyQt5.QtCore import QObject, pyqtSignal

from Logger import Logger
from Logger.Logger import my_logger

# 默认配置
init_config = {
    "icon_path": "ui\\television.ico",
    "tray_icon_path": "ui\\tray_icon.png",
    "opacity": 0.2,
    "font_size": 20,
    "ban_words": [],
    "BiliSocket": {
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
            "Origin": "https://live.bilibili.com",
            "Accept": "application/json",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Content-Type": "application/json"
        },
        "cookies": "",
        "wss_addr": "wss://broadcastlv.chat.bilibili.com/sub",
        "UID": 0
    }
}
init_config = json.dumps(init_config)


# 自定义信号
class Signals(QObject):
    # 操作类型信号
    Operation = pyqtSignal(str)
    # 弹幕数据信号
    MsgData = pyqtSignal(dict)


# 全局信号
global_signal = Signals()


# 读取配置文件
def read_config():
    try:
        if not os.path.exists("config.json"):
            with open("config.json", "w") as f:
                f.write(init_config)
        else:
            with open("config.json", "r") as f:
                content = f.read()
                content = json.loads(content)
                return content
    except FileNotFoundError as e:
        Logger.my_logger.error(e)


# 修改配置文件函数
def modify_config(key, value):
    try:
        if not os.path.exists("config.json"):
            with open("config.json", "w") as f:
                f.write(init_config)
        else:
            # 读取旧数据
            with open("config.json", "r") as f:
                content = json.load(f)

            if key in content:
                content[key] = value
            else:
                my_logger.info("not found key to update")

            # 写入新数据
            with open("config.json", "w") as f:
                json.dump(content, f, indent=2)
    except Exception as e:
        my_logger.error(f"[MODIFY CONFIG] ERROR: {e}")


config = read_config()

# icon路径
icon_path = config.get("icon_path")
# 托盘icon路径
tray_icon = config.get("tray_icon_path")
# 字体大小
font_size = config.get("font_size")
# 显示窗体透明度参数
opacity = config.get("opacity")
# 屏蔽词容器
ban_words_contain = config.get("ban_words")
# 请求头
headers = jsonpath.jsonpath(config, "$.BiliSocket.headers")[0]
# cookies
cookies_str = jsonpath.jsonpath(config, "$.BiliSocket.cookies")[0]
cookies_dict = {temp[:temp.find("=")]: temp[temp.find("=") + 1:] for temp in cookies_str.split("; ")}
# UID
UID = jsonpath.jsonpath(config, "$.BiliSocket.UID")[0]
