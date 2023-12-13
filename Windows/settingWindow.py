
"""
Des 设置窗口，包括连接的房间号，登录UID，设置字体及大小，设置屏蔽词，导出导入设置
@Author thetheOrange
Time 2023/12/9
"""
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QSpinBox, QDoubleSpinBox
from PyQt5.uic import loadUi

from staticData import global_signal, icon_path


class SettingWindow(QWidget):
    def __init__(self):
        super().__init__()
        loadUi("ui/SettingWindow.ui", self)
        # 设置标题、图标
        self.setWindowTitle("BiliDmCat-Setting")
        self.setWindowIcon(QIcon(icon_path))
        # 获取字体大小修改控件和窗口透明度修改控件
        self.font_size_edit = self.findChild(QSpinBox, "fontSizeEdit")
        self.opacity_edit = self.findChild(QDoubleSpinBox, "opacityEdit")

        self.init_ui()

    # 初始化ui，绑定对应的信号
    def init_ui(self):
        # 连接重载按钮
        self.findChild(QPushButton, "loadButton").clicked.connect(lambda: global_signal.Operation.emit("Start"))
        # 断开按钮
        self.findChild(QPushButton, "disConnect").clicked.connect(lambda: global_signal.Operation.emit("DisConnect"))
        # 加入屏蔽词/删除屏蔽词按钮
        self.findChild(QPushButton, "addDeleteButton").clicked.connect(lambda: global_signal.Operation.emit("Ban/Free"))
        # 清空屏蔽词
        self.findChild(QPushButton, "clearWord").clicked.connect(lambda: global_signal.Operation.emit("ClearAll"))
        # 导入配置
        self.findChild(QPushButton, "loadSetting").clicked.connect(lambda: global_signal.Operation.emit("LoadConfig"))
        # 导出配置
        self.findChild(QPushButton, "outSetting").clicked.connect(lambda: global_signal.Operation.emit("OutConfig"))
        # 修复/恢复默认配置
        self.findChild(QPushButton, "fixSetting").clicked.connect(lambda: global_signal.Operation.emit("FixConfig"))

        # 初始化设置字体大小控件和窗口透明度控件
        self.font_size_edit.setRange(20, 40)
        self.opacity_edit.setRange(0.0, 1.0)
        self.opacity_edit.setSingleStep(0.1)
