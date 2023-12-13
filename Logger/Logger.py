"""
Des 项目日志对象
@Author thetheOrange
Time 2023/12/11
"""

import logging


def create_logger():
    # 创建logger对象
    logger = logging.getLogger("mylogger")
    # 定义logger等级
    logger.setLevel(logging.DEBUG)
    # 创建formatter
    formatter = logging.Formatter('%(asctime)s | %(levelname)s -> %(message)s')

    # 创建handler，用于存放logger的位置
    file_handler = logging.FileHandler("Logger/logFile.log")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # 绑定logger对象
    logger.addHandler(file_handler)

    return logger


my_logger = create_logger()
