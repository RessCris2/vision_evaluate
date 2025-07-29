import logging
import os
from logging.handlers import TimedRotatingFileHandler

# dirname = os.path.dirname(os.path.dirname(__file__))

def create_logger(dirname, name: str) -> logging.Logger:
    """
    创建并返回一个统一的 Logger 对象
    
    :param name: Logger 名称，通常为模块名
    :return: 配置好的 logger 对象
    """
    # 创建一个 logger 对象
    logger = logging.getLogger(name)
    
    # 设置日志的最低级别
    logger.setLevel(logging.DEBUG)
    
    # 创建控制台输出 Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    
    filename = os.path.join(dirname, 'app.log')
    # 创建文件输出 Handler
    # file_handler = logging.FileHandler(filename)
    file_handler = TimedRotatingFileHandler(
        filename, when='midnight', backupCount=7, encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)  # 设置文件日志级别为 INFO
    
    # 创建格式化器并将其添加到 handler 中
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # 将 Handler 添加到 Logger 中
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger