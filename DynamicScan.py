#!/usr/bin/python3.6
# encoding:utf-8
from Definitions import Intersection
from AddrsToSeq import InputAddrs, SeqToAddrs
from DHC import SpaceTreeGen, OutputSpaceTree
from ScanPre import ScanPre
from ActiveScan import Scan
import AliasDetection
from copy import deepcopy
import argparse
import time, os, re
from utility import *

from logger import MyLog 
from Title import Title
from Result import Results
"""
sudo python3 DynamicScan.py --input=/home/liguo/6Tree_no_APD_new/c1.hex  --output=/home/liguo/6Tree_no_APD_new/files --budget=500  --IPv6=2001:da8:ff:212::10:3
"""

from loguru import logger

logger.add(sink='../output/error.log', format="{time} - {level} - {message}", level="INFO")

def DynamicScan(root, V, budget, source_ip, output_dir,t,  args):
    """
    动态扫描空间树

    Args：
        root：空间树的根结点
        V：种子地址向量序列
        budget：扫描开销上限（最多扫描的地址数量）
        source_ip：主机源IPv6地址
        output_dir：输出文件目录

    Return：
        R：经扫描发现的活跃地址集合（每个成员为真实的IPv6地址字符串）【序列？】
        P：检测到的别名前缀集合
        budget：剩余扫描次数
    """

    ScanPre(root, V)
    # R = set()
    R = set()
    P = set()
    T = set()
    init_budget = deepcopy(budget)
    suffix = t.getTitle()
    active_file = output_dir + '/result_{}_{}'.format(time.strftime("%Y_%m_%d_%H_%M_%S",time.localtime()), suffix)
    target_file = output_dir + '/result_{}_{}'.format(time.strftime("%Y_%m_%d_%H_%M_%S",time.localtime()), suffix)
    with open(active_file, 'w', encoding = 'utf-8') as f:
        f.seek(0)
        f.truncate()
    with open(target_file, 'w', encoding = 'utf-8') as f:
        f.seek(0)
        f.truncate()
    xi = [] # 待扫描结点队列ξ
    InitializeNodeQueue(root, xi)

    result = Results()
    result.set_title(t)
    xi, budget, R, T, active_addrs, unique_addrs, iter_total = Scan_Feedback(xi, init_budget, budget, R, T, V, source_ip, output_dir, target_file, args)

    MyLog.get_logger().info('[+]Hit rate:{}  \n\
            iter_Hit rate:{} \n\
            iter_find_rate:{} \n\
            Remaining scan times:{}    \n\
            gen_total:{}     \n\
            活跃地址{}|{}\n'.format(
                                    float(len(R)/(init_budget - budget)),
                                    float((len(active_addrs) )/iter_total), 
                                    float((len(unique_addrs))/iter_total), 
                                    budget, (init_budget - budget), 
                                    len(R), 
                                    len(R)/init_budget))

    hit_rate = float(len(R))/(init_budget - budget)
    result.hitrates.append(hit_rate)

    hit_rate1 = float(len(active_addrs))/iter_total
    result.iter_hitrates.append(hit_rate1)

    find_rate1 = float(len(unique_addrs))/iter_total
    result.iter_findrates.append(find_rate1)

    result.final_hit_rate = float(len(R))/(init_budget - budget)

    while budget > 0:
        xi_h = TakeOutFrontSegment(xi, int(0.1 * len(xi)))  # 每次迭代需要扫描的结点
        ReplaceDescendants(xi, xi_h)
        xi_h, budget, R, T , active_addrs, unique_addrs, iter_total= Scan_Feedback(xi_h, init_budget, budget, R, T, V, source_ip, output_dir, target_file, args)
        xi = MergeSort(xi_h, xi)    #!! 原本位于队伍后部的别名结点经过一次MergeSort又会到队伍首部去，
                                        #!! 导致对其进行重复的别名检测
                                    
        MyLog.get_logger().info('[+]Hit rate:{}  \n\
                iter_Hit rate:{} \n\
                iter_find_rate:{} \n\
                Remaining scan times:{}    \n\
                gen_total:{}     \n\
                活跃地址{}|{}\n'.format(
                                        float(len(R)/(init_budget - budget)),
                                        float((len(active_addrs) )/iter_total), 
                                        float((len(unique_addrs))/iter_total), 
                                        budget, iter_total, 
                                        len(R), 
                                        len(R)/init_budget))
        hit_rate = float(len(R))/(init_budget - budget)
        result.hitrates.append(hit_rate)

        hit_rate1 = float(len(active_addrs))/iter_total
        result.iter_hitrates.append(hit_rate1)

        find_rate1 = float(len(unique_addrs))/iter_total
        result.iter_findrates.append(find_rate1)

        result.final_hit_rate = float(len(R))/(init_budget - budget)
    

    result.plot()
    
    
    with open(active_file, 'a', encoding='utf-8') as f:
        for addr in R:
            f.write(addr + '\n')
    with open(target_file, 'a', encoding='utf-8') as f:
        for target in T:
            f.write(target + '\n')
    hit_rate = float(len(R))/(init_budget - budget)
    return R, P, init_budget - budget, len(R), hit_rate


def InitializeNodeQueue(root, xi):
    """
    层次遍历空间树，将结点队列ξ初始化为空间树的叶子结点

    Args：
        root:空间树的根结点
        xi：结点队列ξ
    """
    # pdb.set_trace()
    q = []
    q.append(root)
    while q != []:
        node = q.pop(0)
        if node.childs != []:
            q += node.childs
        else:
            xi.append(node)


def Scan_Feedback(xi, init_budget, budget, R, T, V, source_ip, output_dir, target_file, args):
    """
    对队列xi中的所有结点进行一次扫描，
    并根据扫描得到的活跃地址密度对队列重新排序

    Args：
        xi：结点队列ξ
        init_budget：扫描次数上限
        budget：剩余的扫描次数
        R：经扫描发现的活跃地址集合
        T
        V:种子地址向量集合
        source_ip
        output_dir
        target_file

    Return:
        xi:重新排序后的结点队列ξ
        budget:经过一次迭代扫描之后剩余的扫描次数
        R：更新后的活跃地址集合
        T：预测地址集合
    """

    # pdb.set_trace()

    TS_addr_union = list()
    SS_addr_union = list()
    for i in range(len(xi)):
        # if i % 100 == 0:
        #     print(i)
        node = xi[i]
        TS_addr_union += SeqToAddrs(node.TS)
        SS_addr_union += list(node.SS)

    C = set(TS_addr_union).difference(set(SS_addr_union)) #本次需要扫描的地址集合
    budget -= len(C)
    if budget <= 0:
        C = LimitBudget(budget, C)
        budget = 0

    total = len(C)
    T.update(C)
    # with open(target_file, 'a', encoding='utf-8') as f:
    #     for target in C:
    #         f.write(target + '\n')
    active_addrs = set(Scan(C, source_ip, output_dir, 0, args))   #扫描并得到活跃的地址集合

    # 查看重复地址
    intersec = R & (active_addrs)
    # MyLog.get_logger().info(len(intersec), list(intersec)[:10])
    MyLog.get_logger().info('[+]duplication {}'.format(len(intersec)))
    # 新的地址
    unique_addrs  = active_addrs - intersec


    R.update(active_addrs)

    MyLog.get_logger().info('[+]Hit rate:{}   Remaining scan times:{}\n'
       .format(float(len(R)/(init_budget - budget)), budget))

    for i in range(len(xi)):
        # if(i % 100 == 0):
        #     print(i)
        node = xi[i]
        node.SS = set(SeqToAddrs(node.TS))
        new_active_addrs = active_addrs.intersection(node.SS)
        node.NDA += len(new_active_addrs)
        node.AAD = float(node.NDA)/len(node.SS)
        delta = node.DS.pop()
        node.ExpandTS(delta, V)

    xi = sorted(xi, key=lambda node: node.AAD, reverse=True)
    
    return xi, budget, R, T, active_addrs, unique_addrs, total


def TakeOutFrontSegment(xi, m):
    """
    提取结点队列xi中的前m个结点，作为下次扫描的目标结点队列

    Args：
        xi:待分割的队列
        m：新目标队列的结点数

    Return：
        xi_h：新的目标队列
    """

    # xi_h = deepcopy(xi[:m])
    # pdb.set_trace()

    if m <= len(xi):
        xi_h = xi[:m]
        del xi[:m]
    else:
        xi_h = xi[:]
        del xi[:]

    return xi_h


def ReplaceDescendants(xi, xi_h):
    """
    经过一次扫描后，若某结点与其父结点有相同的DS，在xi和xi_h队列中，
    需要将该结点及其所有的兄弟结点删除，并插入它们的父结点【证  明见Theorom3】

    Args：
        xi：未被扫描的，但在下次扫描中不会被扫描的结点队列
        xi_h：下次将会被扫描的结点队列
    """

    # pdb.set_trace()

    new_nodes = set()   #将要被加入队列的结点集合
    for node in xi_h:
        if node.parent == None:
            break   #注释！！！！！
        if node.parent.DS.stack == node.DS.stack:
            node.parent.TS = node.TS
            new_nodes.add(node.parent)

    complete_queue = set(xi_h + xi)
    # xi_h_set = set(xi_h)
    # xi_set = set(xi)    #将优先队列先转换为结点集合，方便后续并、交等运算的进行
    count = 0
    for node in new_nodes:
        # childs = set(node.cohilds)
        count += 1
        #if count % 100 == 0:
        #    print("new node {}".format(count))
        childs = set(node.childs)
        retired = complete_queue.intersection(childs)
        # retired = Intersection(childs, complete_queue)
        for retired_node in retired:
            node.SS = node.SS.union(retired_node.SS) 
            # node.SS  = list(node.SS) + list(retired_node.SS)
            node.NDA += retired_node.NDA
        # node.SS = set(node.SS)
        node.AAD = float(node.NDA)/len(node.SS)

        #分别需要从两个队列和new_nodes集合中删除的结点
        xi_h_remove = Intersection(retired, xi_h)
        xi_remove = Intersection(retired, xi)
        new_nodes_remove = Intersection(retired, new_nodes)
        for v in xi_h_remove:
            xi_h.remove(v)
        for v in xi_remove:
            xi.remove(v)
        for v in new_nodes_remove:
            new_nodes.remove(v)

    for new_node in new_nodes:
        xi_h.append(new_node)

def InsertAliasNodes(alias_queue, new_queue):
    """
    将alias_queue中的别名结点的NDA设为1（降低扫描优先级），插入new_queue的正常结点中后恢复其AAD

    Args:
        alias_queue：别名结点队列
        new_queue：正常结点队列
    """

    id_AAD_dict = {}    # 暂存别名结点的id->AAD字典

    for node in alias_queue:    # 将别名结点插入队列的后部
        id_AAD_dict[node.node_id] = node.AAD
        node.AAD = 1 / len(node.SS)
        AliasDetection.InsertNode(new_queue, node)

    for node in new_queue:  # 恢复别名结点的AAD
        if node.node_id in id_AAD_dict.keys():
            node.AAD = id_AAD_dict[node.node_id]


def MergeSort(xi_h, xi):
    """
    将两个有序的结点队列合并为一个

    Args：
        xi_h：队列1
        xi：队列2

    Return：
        queue：合并后的有序队列
    """

    queue = []
    i1 = 0
    i2 = 0
    while i1 < len(xi_h) or i2 < len(xi):
        if i1 >= len(xi_h):
            queue += xi[i2:]
            break
        elif i2 >= len(xi):
            queue += xi_h[i1:]
            break
        elif xi_h[i1].AAD >= xi[i2].AAD:
            queue.append(xi_h[i1])
            i1 += 1
        else:
            queue.append(xi[i2])
            i2 += 1

    return queue


def LimitBudget(budget, C):
    """
    将C中超出预算部分的地址删除

    Args:
        budget: 超过预算的地址数的相反数
        C：下次将要扫描的目标地址集合

    Return:
        C：经过处理后的目标地址集合
    """

    C = list(C)
    del C[:-budget]
    return set(C)

def getIPv6Address():
    """
    https://blog.csdn.net/COCO56/article/details/106725406
    """
    output = os.popen("ifconfig").read()
    # MyLog.get_logger().info(output)
    result = re.findall(r"(([a-f0-9]{1,4}:){7}[a-f0-9]{1,4})", output, re.I)
    return result[0][0]

@logger.catch
def Start():

    global t # global var, used to set the output suffix
    t = Title()

    parse=argparse.ArgumentParser()
    parse.add_argument('--input', type=str, help='input IPv6 addresses', default="./ouput/seed.txt")
    parse.add_argument('--output',type=str,help='output directory name', default="./output/")
    parse.add_argument('--budget',type=int,help='the upperbound of scan times', default=1000000)
    parse.add_argument('--range', type=int, help='seed range', default=1000000)
    parse.add_argument('--seedn', type=int, help='seed range', default=5000)
    parse.add_argument('--probetool',type=str,help='the probe tool:zmap/xmap/xmap_echo', default='zmap')
    parse.add_argument('--tree',type=str,help='the tree algo:dhc or trie', default='trie')
    parse.add_argument('--IPv6',type=str,help='local IPv6 address')
    parse.add_argument('--eth',type=str,help='the eth', default='eth0')
    parse.add_argument('--speed',type=str,help='the scan speed', default='1M')

    args=parse.parse_args()

    t.setRangeBudgetSeedn(args.range, args.budget, args.seedn)
    # args.input = '/home/sgl/6Tree_no_APD/files/source_copy.hex'
    # args.output = '/home/sgl/6Tree_no_APD/files2'
    # args.budget = 50000
    # args.IPv6 = '2001:da8:ff:212::20:5'
    args.IPv6 = getIPv6Address()

    V = InputAddrs(args.input, beta=16)

    root = SpaceTreeGen(V,beta=16)
    MyLog.get_logger().info('Space tree generated with {} seeds!'.format(len(V)))    

    t.setScannerName("Zmap_Echo")
    t.setTreeName("Tree_6tree")
    
    R, P, target_len, result_len, hit_rates = DynamicScan(root, V, args.budget, args.IPv6, args.output, t, args)

    with open(args.output + '/6Tree.alias', 'w', encoding = 'utf-8') as f:
        f.seek(0)
        f.truncate()
        for p in P:
            f.write(p + '\n')
    MyLog.get_logger().info('Over!')

    
    # hit_rate = float(len(R))/(init_budget - budget)
    # return init_budget - budget, len(R), hit_rate
    return target_len, result_len, hit_rates


if __name__ == '__main__':
    target, result, hit_rate = Start()
    
