"""
Des 程序主文件
@Author thetheOrange
Time 2023/12/12
"""

import asyncio
import os.path
import sys
from threading import Thread

import jsonpath
from PyQt5.QtWidgets import QWidget, QApplication, QLineEdit, QFontComboBox, QPlainTextEdit, QTextBrowser, QMessageBox, \
    QSpinBox, QDoubleSpinBox, QFileDialog

from Logger.Logger import my_logger
from Windows.menu import TrayMenu
from Windows.settingWindow import SettingWindow
from Windows.showMsgWindow import showMsgWindow
from staticData import global_signal, ban_words_contain, modify_config, font_size, opacity, read_config, init_config
from BiliWebSocket.BiliSocket import BiliSocket


# 创建一个子线程，用于爬取B站直播弹幕
class GetData(Thread):
    def __init__(self, room_id):
        super().__init__()
        # 子线程开启标志位
        self.__run_flag = True
        self.room_id = room_id
        # 创建爬虫对象
        self.BiliSocket = BiliSocket(room_id=room_id)

    def run(self):
        if self.__run_flag:
            try:
                asyncio.run(self.BiliSocket.start())
            except Exception as e:
                my_logger.error(f"[WEBSOCKET ERROR]: {e}")

    # 关闭子线程
    def stop(self):
        try:
            self.__run_flag = False
            self.BiliSocket.stop()
        except KeyboardInterrupt:
            print("stop")


class App(QWidget):
    def __init__(self, sys_arg):
        super().__init__()
        # 获取项目对象
        self.__app = QApplication(sys_arg)
        self.__app.setQuitOnLastWindowClosed(False)
        # 设置连接和断开转换标志
        self.__change_flag = True
        # 获取屏蔽词容器
        self.__ban_words_contain = ban_words_contain

        self.file_dialog = QFileDialog(self)
        self.file_dialog.setWindowTitle("Bili-cat")

        # 获取设置窗口及相关控件
        self.set_w = SettingWindow()
        # 修改字体栏
        self.font_change = self.set_w.findChild(QFontComboBox, "fontEdit")
        # 获取字体修改控件
        self.font_size_box = self.set_w.findChild(QSpinBox, "fontSizeEdit")
        self.font_size_box.setValue(font_size)
        self.font_style_box = self.set_w.findChild(QFontComboBox, "fontEdit")
        # 获取窗口透明度修改控件
        self.opacity_box = self.set_w.findChild(QDoubleSpinBox, "opacityEdit")
        self.opacity_box.setValue(opacity)
        # 屏蔽词展示窗口
        self.ban_word_show = self.set_w.findChild(QPlainTextEdit, "showBanWord")
        self.ban_word_show.setReadOnly(True)
        self.ban_word_show.setPlainText(str(ban_words_contain))

        # 获取显示窗口
        self.show_w = showMsgWindow()
        self.msg_show = self.show_w.findChild(QTextBrowser, "showMsg")

        # 获取托盘
        self.menu = TrayMenu()

        # 处理各窗口传来的状态信号
        global_signal.Operation.connect(self.__handle_signals)
        # 接收原始弹幕数据
        global_signal.MsgData.connect(self.__out_put)
        # 字体大小修改处理
        self.font_size_box.valueChanged.connect(self.__modify_font_size)
        # 窗口透明度修改处理
        self.opacity_box.valueChanged.connect(self.__modify_opacity)
        # 字体样式修改处理
        self.font_style_box.currentFontChanged.connect(self.__modify_font_style)

    # 尝试查找配置文件，若没有则报错
    def __find_config(self):
        try:
            if not os.path.exists(".//config.json"):
                self.__fix_config()
            else:
                my_logger.info("配置文件config.json存在")
        except Exception as e:
            my_logger.error(f"程序自检，恢复默认配置失败! {e}")
            msg_box = QMessageBox(QMessageBox.Critical, '错误', '程序自动恢复默认配置失败!')
            msg_box.exec_()

    # 处理状态信号
    def __handle_signals(self, value):
        if value == "Start":
            self.__connect()
        if value == "DisConnect":
            self.__dis_connect()
        if value == "Ban/Free":
            self.__ban_words()
        if value == "ClearAll":
            self.__clear_word()
        if value == "LoadConfig":
            self.__load_config()
        if value == "OutConfig":
            self.__out_config()
        if value == "FixConfig":
            self.__fix_config()
        if value == "SettingWindow":
            self.set_w.show()
        if value == "Exit":
            self.__exit_app()

    # 获取直播房间号，开启连接
    def __connect(self):
        # 直播房间号
        room_id = self.set_w.findChild(QLineEdit, "roomLine").text()
        try:
            room_id = int(room_id)
            if room_id is not None and self.__change_flag:
                # 创建子线程，负责接收原始数据
                self.get_data_t = GetData(room_id=room_id)
                # 设置为守护线程
                self.get_data_t.start()
                self.__change_flag = False
                self.set_w.setWindowTitle("BiliDmCat-Setting(connecting...)")
        except Exception as e:
            my_logger.error(f"[ROOM ID] ERROR: {e}")
            msg_box = QMessageBox(QMessageBox.Critical, '错误', '请输入正确的房间号!')
            msg_box.exec_()

    # 关闭连接
    def __dis_connect(self):
        try:
            if self.get_data_t:
                self.get_data_t.stop()
                self.msg_show.clear()
                self.show_w.init_ui()
                self.__change_flag = True
                self.set_w.setWindowTitle("BiliDmCat-Setting")
        except Exception as e:
            my_logger.error(f"关闭连接失败: {e}")

    # 修改字体大小
    def __modify_font_size(self, value):
        try:
            # 将新的字体大小写入配置文件
            modify_config(key="font_size", value=value)
            # 重新初始化展示窗口
            self.show_w.init_ui()
        except Exception as e:
            my_logger.error(f"尝试修改字体失败: {e}")

    # 修改字体样式
    def __modify_font_style(self, font):
        self.msg_show.setFont(font)

    # 修改窗口透明度
    def __modify_opacity(self, value):
        # 将新的透明度写入配置文件
        modify_config(key="opacity", value=value)
        # 重新初始化展示窗口
        self.show_w.init_ui()

    # 将屏蔽词加入配置文件中
    def __ban_words(self):
        try:
            # 获取屏蔽词
            ban_word = self.set_w.findChild(QLineEdit, "banWord").text()
            if ban_word != "":
                if ban_word not in self.__ban_words_contain:
                    self.__ban_words_contain.append(ban_word)
                elif ban_word in self.__ban_words_contain:
                    self.__ban_words_contain.remove(ban_word)
                # 将屏蔽词写入配置文件中
                modify_config(key="ban_words", value=self.__ban_words_contain)
                # 显示屏蔽词在窗口
                self.ban_word_show.setPlainText(str(self.__ban_words_contain))
            else:
                msg_box = QMessageBox(QMessageBox.Critical, '错误', '屏蔽词不能为空!')
                msg_box.exec_()
        except Exception as e:
            my_logger.error(f"[BAN WORD] ERROR: {e}")

    # 清除所有屏蔽词
    def __clear_word(self):
        self.__ban_words_contain = []
        # 将屏蔽词写入配置文件中
        modify_config(key="ban_words", value=self.__ban_words_contain)
        # 显示屏蔽词在窗口
        self.ban_word_show.setPlainText(str(self.__ban_words_contain))

    # 判断屏蔽词是否在弹幕消息中
    def __is_ban_msg(self, msg):
        for ban_word in self.__ban_words_contain:
            if ban_word in msg:
                return True
        return False

    # 导入配置文件
    def __load_config(self):
        if self.file_dialog.exec_() == QFileDialog.Accepted:
            selected_file = self.file_dialog.selectedFiles()[0]
            if "config.json" not in selected_file:
                msg_box = QMessageBox(QMessageBox.Critical, '错误', '请选择文件名为config.json的配置文件!')
                msg_box.exec_()
            else:
                # 读取新的配置文件
                with open(selected_file, "r") as f:
                    content = f.read()
                # 将新的配置文件写入
                with open(".//config.json", "w") as f:
                    f.write(content)
                # 获取新的数据
                config = read_config()
                # 字体大小
                new_font_size = config.get("font_size")
                # 显示窗体透明度参数
                new_opacity = config.get("opacity")
                # 屏蔽词容器
                new_ban_words_contain = config.get("ban_words")
                # 初始化设置窗口的ui
                self.font_size_box.setValue(new_font_size)
                self.opacity_box.setValue(new_opacity)
                self.ban_word_show.setPlainText(str(new_ban_words_contain))
                # 提示导入成功
                success_message = QMessageBox()
                success_message.setIcon(QMessageBox.Information)
                success_message.setText("导入配置成功！")
                success_message.setWindowTitle("Success")
                success_message.exec_()

    # 导出配置文件
    @staticmethod
    def __out_config():
        try:
            if os.path.exists("./TempConfig"):
                # 读取config文件
                with open(".//config.json", "r") as f:
                    content = f.read()
                # 写入指定的文件夹中
                with open(".//TempConfig//config.json", "w") as f:
                    f.write(content)
                # 提示导出成功
                success_message = QMessageBox()
                success_message.setIcon(QMessageBox.Information)
                success_message.setText("导出配置成功！")
                success_message.setWindowTitle("Success")
                success_message.exec_()
            else:
                os.mkdir("./TempConfig")
        except Exception as e:
            my_logger.error(f"导出配置文件失败 {e}")

    # 修复/恢复默认配置
    def __fix_config(self):
        try:
            with open("./config.json", "w") as f:
                f.write(init_config)
            # 提示恢复成功
            success_message = QMessageBox()
            success_message.setIcon(QMessageBox.Information)
            success_message.setText("恢复默认配置成功！")
            success_message.setWindowTitle("Success")
            success_message.exec_()
            # 获取新的数据
            config = read_config()
            # 字体大小
            new_font_size = config.get("font_size")
            # 显示窗体透明度参数
            new_opacity = config.get("opacity")
            # 屏蔽词容器
            new_ban_words_contain = config.get("ban_words")
            # 初始化设置窗口的ui
            self.font_size_box.setValue(new_font_size)
            self.opacity_box.setValue(new_opacity)
            self.ban_word_show.setPlainText(str(new_ban_words_contain))
        except Exception as e:
            my_logger.error(f"恢复默认配置失败: {e}")
            msg_box = QMessageBox(QMessageBox.Critical, '错误', '恢复默认配置失败!')
            msg_box.exec_()

    # 格式化输出弹幕信息
    def __out_put(self, data):
        try:
            # 展示显示窗口
            self.show_w.show()
            # 获取消息类型
            cmd = jsonpath.jsonpath(data, "$.cmd")[0]

            # 弹幕消息
            if cmd == "DANMU_MSG":
                # 用户名
                user_name = jsonpath.jsonpath(data, "$.info[0]..user.base.name")[0]
                # 弹幕信息
                dm_msg = jsonpath.jsonpath(data, "$.info[1]")[0]
                if not self.__is_ban_msg(dm_msg):
                    self.msg_show.append("<p><font color='white'>%s</font><font color='white'>: %s</font></p>" %
                                         (user_name, dm_msg))

            # 付费留言
            elif cmd == "SUPER_CHAT_MESSAGE":
                # 用户名
                user_name = jsonpath.jsonpath(data, "$.data.user_info.uname")[0]
                # 付费留言
                sc_msg = jsonpath.jsonpath(data, "$.data.message")[0]
                self.msg_show.append("<h1><font color='white'>[SC]%s</font><font color='white'>: %s</font></h1>" %
                                     (user_name, sc_msg))

            # 上舰通知
            elif cmd == "GUARD_BUY":
                # 用户名
                user_name = jsonpath.jsonpath(data, "$.data.username")[0]
                # 礼物名字
                gift_name = jsonpath.jsonpath(data, "$.data.gift_name")[0]
                self.msg_show.append("<font color='white'>[GUARD]%s</font><font color='white'> 购买了%s</font>" %
                                     (user_name, gift_name))

        except Exception as e:
            my_logger.error(f"[HANDLE DM MSG] ERROR:{e}")

    # 退出程序
    def __exit_app(self):
        try:
            self.set_w.close()
            self.show_w.close()
            self.__app.quit()
            raise KeyboardInterrupt
        except Exception as e:
            my_logger.error(f"EXIT APP ERROR: {e}")
