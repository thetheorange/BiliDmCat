
"""
Des 弹幕显示窗口，应具有无边框、可拖动、可拉伸、半透明效果
@Author thetheOrange
Time 2023/12/9
"""
import sys

from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QMouseEvent, QColor
from PyQt5.QtWidgets import QApplication, QTextBrowser, QWidget, QGraphicsDropShadowEffect, QDesktopWidget
from PyQt5.uic import loadUi

from staticData import read_config


class showMsgWindow(QWidget):
    def __init__(self):
        super().__init__()

        # 鼠标偏移量
        self.__change_pos = None
        # 鼠标起始值
        self.__start_pos = None
        # 鼠标移动标志
        self.__move_flag = False
        # 判断鼠标在哪个边界处的标志
        self.__right_flag = False
        self.__bottom_flag = False
        self.__corner_flag = False
        # 设置边界宽度
        self.__pad = 20
        # 设置边界范围
        self.__right_edge = None
        self.__bottom_edge = None
        self.__corner_edge = None

        # 设置窗口的初始大小，获取TextBrowser控件
        loadUi("ui/ShowMsg.ui", self)
        self.showMsg = self.findChild(QTextBrowser, "showMsg")
        self.resize(400, 500)
        # 获取屏幕的大小
        screen = QDesktopWidget().screenGeometry()
        screen_width = screen.width()
        screen_height = screen.height()
        # 计算窗口的坐标使其显示在屏幕右上角靠下
        window_width = self.width()
        window_height = self.height()
        window_x = screen_width - window_width
        self.setGeometry(window_x-50, 50, window_width, window_height)
        self.setMinimumSize(400, 500)

        # 设置窗口无边框
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        # 设置窗口透明化
        self.setAttribute(Qt.WA_TranslucentBackground)
        # 设置窗口边缘阴影
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(15)
        self.shadow.setColor(QColor(0, 0, 0, 150))
        self.shadow.setOffset(0, 0)
        self.setGraphicsEffect(self.shadow)
        # 设置窗口鼠标追踪
        self.showMsg.setMouseTracking(True)

        self.init_ui()

    # 初始化ui
    def init_ui(self):
        # 读取配置文件
        config = read_config()
        # 字体大小
        font_size = config.get("font_size")
        # 显示窗体透明度参数
        opacity = config.get("opacity")
        # 为TextBrowser加入鼠标事件处理
        self.showMsg.mousePressEvent = self.mousePressEvent
        self.showMsg.mouseMoveEvent = self.mouseMoveEvent
        self.showMsg.mouseReleaseEvent = self.mouseReleaseEvent
        # 为控件设置半透明效果和默认字体大小
        self.showMsg.setStyleSheet(f"background-color: rgba(128, 128, 128, {opacity});font-size: {font_size}px;")

    # 重写监听鼠标的三个方法: 移动、点击、释放
    def mouseMoveEvent(self, event: QMouseEvent):

        # 获取窗口的边界范围
        # 右侧边缘
        self.__right_edge = [QPoint(x, y) for x in range(self.width() - self.__pad, self.width() + 1)
                             for y in range(0, self.height() - self.__pad)]
        # 底部边缘
        self.__bottom_edge = [QPoint(x, y) for x in range(0, self.width() - self.__pad)
                              for y in range(self.height() - self.__pad, self.height() + 1)]
        # 右下角边缘
        self.__corner_edge = [QPoint(x, y) for x in range(self.width() - self.__pad, self.width() + 1)
                              for y in range(self.height() - self.__pad, self.height() + 1)]

        if self.__move_flag:
            # 计算鼠标偏移量
            self.__change_pos = event.pos() - self.__start_pos
            # 移动窗口
            self.move(self.pos() + self.__change_pos)

        # 检测鼠标在窗口的位置，改变鼠标手势
        if event.pos() in self.__right_edge:
            self.setCursor(Qt.SizeHorCursor)
        elif event.pos() in self.__bottom_edge:
            self.setCursor(Qt.SizeVerCursor)
        elif event.pos() in self.__corner_edge:
            self.setCursor(Qt.SizeFDiagCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

        # 根据鼠标的方向改变窗口大小
        if self.__right_flag and Qt.LeftButton:
            self.resize(event.pos().x(), self.height())
            event.accept()
        elif self.__bottom_flag and Qt.LeftButton:
            self.resize(self.width(), event.pos().y())
            event.accept()
        elif self.__corner_flag and Qt.LeftButton:
            self.resize(event.pos().x(), event.pos().y())
            event.accept()

    def mousePressEvent(self, event: QMouseEvent):
        if Qt.LeftButton:
            # 获取鼠标当前位置
            self.__start_pos = QPoint(event.x(), event.y())
            # 设置鼠标移动状态为True
            self.__move_flag = True

            if event.pos() in self.__right_edge:
                self.__right_flag = True
                self.__move_flag = False
                event.accept()
            elif event.pos() in self.__bottom_edge:
                self.__bottom_flag = True
                self.__move_flag = False
                event.accept()
            elif event.pos() in self.__corner_edge:
                self.__corner_flag = True
                self.__move_flag = False
                event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            # 释放鼠标位置信息并将移动状态改为False
            self.__move_flag = False
            self.__start_pos = None
            self.__change_pos = None
            self.__right_flag = False
            self.__bottom_flag = False
            self.__corner_flag = False
