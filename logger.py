import time
import logging


class IColor(object):
    def front_color(self, content):
        raise NotImplementedError
    def back_color(self, content):
        raise NotImplementedError

class NoColor(IColor):
    def set_color(self, content):
        return content

class Color(IColor):
    def __init__(self, display_type=1, front_color=32, back_color=44):
        self.display_type = display_type
        self.front_color = front_color
        self.back_color = back_color
    def set_color(self, content):
        return '\033[{};{};{}m'.format(self.display_type, self.front_color, self.back_color) + content + '\033[0m'

class logger(object):
    def __init__(self, color=NoColor()):
        self.color = color

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            content = "the function {func}() is running...".format(func=func.__name__)
            content = self.color.set_color(content)
            print(content)

            start_time=time.perf_counter()#----->函数运行前时间
            result = func(*args,**kwargs)
            end_time=time.perf_counter()#----->函数运行后时间
            cost_time=end_time-start_time#---->运行函数消耗时间

            content = "{} is: {:.8f}s".format(func.__name__,cost_time)
            content = self.color.set_color(content)
            print(content)
            return result
        return wrapper


# @logger(color=Color())
# def say(something):
    # print("say {}!".format(something))

# say("hello")
import os
class MyLog(object):

    @staticmethod
    def get_logger():
        modelPath = os.path.dirname(__file__)
        logger = logging.getLogger(__name__)
        logger.setLevel(10)
        if not logger.handlers:
            handler = logging.FileHandler(os.path.join(modelPath, '../output/log.txt'),encoding='utf-8')
            formatter = logging.Formatter('%(asctime)s - [%(filename)s  -->line:%(lineno)d] - %(levelname)s: %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)

            console = logging.StreamHandler(stream=None)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
            console.setFormatter(formatter)
            logger.addHandler(console)
        return logger
#     handler名称：位置；作用
 
# StreamHandler：logging.StreamHandler；日志输出到流，可以是sys.stderr，sys.stdout或者文件
# FileHandler：logging.FileHandler；日志输出到文件
# BaseRotatingHandler：logging.handlers.BaseRotatingHandler；基本的日志回滚方式
# RotatingHandler：logging.handlers.RotatingHandler；日志回滚方式，支持日志文件最大数量和日志文件回滚
# TimeRotatingHandler：logging.handlers.TimeRotatingHandler；日志回滚方式，在一定时间区域内回滚日志文件
# SocketHandler：logging.handlers.SocketHandler；远程输出日志到TCP/IP sockets
# DatagramHandler：logging.handlers.DatagramHandler；远程输出日志到UDP sockets
# SMTPHandler：logging.handlers.SMTPHandler；远程输出日志到邮件地址
# SysLogHandler：logging.handlers.SysLogHandler；日志输出到syslog
# NTEventLogHandler：logging.handlers.NTEventLogHandler；远程输出日志到Windows NT/2000/XP的事件日志
# MemoryHandler：logging.handlers.MemoryHandler；日志输出到内存中的指定buffer
# HTTPHandler：logging.handlers.HTTPHandler；通过"GET"或者"POST"远程输出到HTTP服务器
