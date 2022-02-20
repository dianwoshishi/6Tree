import os
import re
import time

import matplotlib.pyplot as plt

import numpy as np

from logger import MyLog

# def calcTime(func):
# 	def wrapper(*args,**kvargs):
# 		start_time=time.perf_counter()#----->函数运行前时间
# 		result = func(*args,**kvargs)
# 		end_time=time.perf_counter()#----->函数运行后时间
# 		cost_time=end_time-start_time#---->运行函数消耗时间
# 		MyLog.get_logger().info("\033[0;31;40m{} is: {:.8f}s\033[0m".format(func.__name__,cost_time))
# 		return result
# 	return wrapper#---->装饰器其实是对闭包的一个应用
import os
 
def mkdir(path):
 
	folder = os.path.exists(path)
 
	if not folder:                   #判断是否存在文件夹如果不存在则创建为文件夹
		os.makedirs(path)            #makedirs 创建文件时如果路径不存在会创建这个路径 

class CoastTime(object):
    def __init__(self, _desc):
        self.t = 0
        self.__desc = _desc

    def __enter__(self):
        self.t = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        MyLog.get_logger().info('{} coast time:{:.8f} s'.format(self.__desc, time.perf_counter() - self.t))

def my_plot(title, *hitrates):    
    x = range(len(hitrates))
    fig, ax = plt.subplots(1, 1) # 创建图实例
    for i, hitrate in enumerate(hitrates) :
        y1 = hitrate
        ax.plot(y1, label='hitrate{}'.format(i)) # 作y1 = x 图，并标记此线名为linear

    ax.set_xlabel('x label') #设置x轴名称 x label
    ax.set_ylabel('y label') #设置y轴名称 y label
    final_title  = '{}-{}-{}.png'.format(title.getTitle(), time.strftime("%Y_%m_%d_%H_%M_%S",time.localtime()), hitrates[0][-1:])
    ax.set_title(final_title) #设置图名为Simple Plot
    ax.legend() #自动检测要在图例中显示的元素，并且显示
    plt.grid()
    plt.ylim((0,0.7))
    # plt.show() #图形可视化
    plt.savefig('output/{}'.format(final_title) )

def checking(xi):
    MyLog.get_logger().info('checking..')
    for i_xi in range(0, len(xi)-1):
        i = xi[i_xi]
        for j_xi in range(i_xi + 1, len(xi)):
            j = xi[j_xi]
            for k in range(32):
                if i.pattern[k] >= 0 and j.pattern[k] >= 0:

                    if i.pattern[k] == j.pattern[k]:
                        continue
                    else:
                        break


                if i.pattern[k] >= 0 and j.pattern[k] == -1:
                    MyLog.get_logger().info(i.pattern, j.pattern)
                    break
                if j.pattern[k] >= 0 and i.pattern[k] == -1:
                    MyLog.get_logger().info(i.pattern, j.pattern)
                    break
    # checking(xi)
def sort_dict(di):
    return [(k,di[k]) for k in sorted(di.keys())]

    



