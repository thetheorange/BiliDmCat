import sys

from PyQt5.QtWidgets import QApplication

from BiliDmMachine import App

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App(sys_arg=sys.argv)
    window.set_w.show()
    app.exec()

