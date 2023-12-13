
"""
Des 实现托盘效果，托盘应具有重载与直播房间号的连接，开启设置界面，退出程序的功能
@Author thetheOrange
Time 2023/12/10
"""

from PyQt5.QtCore import QObject
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QSystemTrayIcon, QAction, QMenu

from staticData import global_signal, tray_icon


class TrayMenu(QObject):
    def __init__(self):
        super().__init__()
        # 初始化ui
        # 设置托盘图标
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(QIcon(tray_icon))
        # 设置悬浮提示
        self.tray.setToolTip("BiliDmCat\nver 1.0")

        # 设置托盘菜单
        self.reload_a = QAction("重载", triggered=lambda: global_signal.Operation.emit("Start"))
        self.disconnect_a = QAction("断开", triggered=lambda: global_signal.Operation.emit("DisConnect"))
        self.setting_a = QAction("设置窗口", triggered=lambda: global_signal.Operation.emit("SettingWindow"))
        self.exit_a = QAction("退出", triggered=lambda: global_signal.Operation.emit("Exit"))
        self.tray_menu = QMenu()
        # 设置菜单格式
        self.tray_menu.setStyleSheet("""
                    background-color: #333;
                    color: white;
                    selection-background-color: #555;
                    selection-color: yellow;
                """)

        self.tray_menu.addAction(self.reload_a)
        self.tray_menu.addAction(self.disconnect_a)
        self.tray_menu.addAction(self.setting_a)
        self.tray_menu.addAction(self.exit_a)
        self.tray.setContextMenu(self.tray_menu)
        # 绑定鼠标点击图标的信号
        self.tray.activated.connect(self.on_click)
        self.tray.show()

    @staticmethod
    def on_click(reason: int):
        # 1 表示单击右键，2 表示双击，3 表示单击左键，4 表示鼠标中键点击
        # 双击打开设置窗口
        if reason == 2:
            global_signal.Operation.emit("SettingWindow")
