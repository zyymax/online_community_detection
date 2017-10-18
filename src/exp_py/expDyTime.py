#!/usr/bin/env python
"""
Coder:  max.zhang
Date:   2015-04-15
Desc:   experiments on computation time of 8 dynamics
"""
import sys
import os
import subprocess
sys.path.append('/home/maxzhang/exp/OnlineCD_exp_0113/src/alg')
from qca import QCAImp
from qcaw import QCAWImp
from zyy_qcaw import ZyyQCAWImp
from qcaw_rec import QCAWRecImp
from nwqca import NWQCAImp


WNET_FILE = "data/random_data/wnet_str.IDX"
NC_FILE = "data/random_data/nc_pair.IDX"
DY_FILE = "data/random_data/TYPE_TIMES.IDX"
SIZE_LIST = [1000, 5000, 10000]
# SIZE_LIST = [1000]
TIMES_LIST = [10, 30, 50, 100, 1000]
# TIMES_LIST = [10]


def main():
    assert len(sys.argv) == 2, 'Usage:\t%s <test_type>' % sys.argv[0]
    test_type = sys.argv[1]
    assert test_type in ['upNode', 'downNode', 'addNode', 'rmNode', 'upEdge', 'downEdge', 'addEdge', 'rmEdge']
    qcaw_com = QCAWImp()
    zqcaw_com = ZyyQCAWImp()
    rqcaw_com = QCAWRecImp()
    nwqca_com = NWQCAImp()
    print("[EXP-TIME on %s]" % test_type)
    for idx in SIZE_LIST:
        qcaw_list = []
        rqcaw_list = []
        zqcaw_list = []
        nwqca_list = []
        for times in TIMES_LIST:
            qcaw_time = 0.
            rqcaw_time = 0.
            zqcaw_time = 0.
            nwqca_time = 0.
            wnet_file = WNET_FILE.replace('IDX', str(idx))
            qcaw_com.fromNetStr(wnet_file)
            rqcaw_com.fromNetStr(wnet_file)
            zqcaw_com.fromNetStr(wnet_file)
            nwqca_com.fromNetStr(wnet_file)
            nc_file = NC_FILE.replace('IDX', str(idx))
            qcaw_com.fromComStruc(nc_file)
            rqcaw_com.fromComStruc(nc_file)
            zqcaw_com.fromComStruc(nc_file)
            nwqca_com.fromComStruc(nc_file)
            dy_file = DY_FILE.replace(
                'TYPE', test_type).replace(
                    'TIMES', str(times)).replace(
                        'IDX', str(idx))
            # print test_type, times, idx
            with open(dy_file) as ins:
                for line in ins:
                    if not line.startswith(test_type):
                        continue
                    if test_type in ['upNode', 'downNode']:
                        node_str, node_w = line.strip().split()[1:]
                        qcaw_time += qcaw_com.setNodeWeight(node_str, float(node_w))
                        rqcaw_time += rqcaw_com.setNodeWeight(node_str, float(node_w))
                        zqcaw_time += zqcaw_com.setNodeWeight(node_str, float(node_w))
                        nwqca_time += nwqca_com.setNodeWeight(node_str, float(node_w))
                    elif test_type == 'addNode':
                        node_str, node_w, edges_str = line.strip().split()[1:]
                        edge_dict = {}
                        for edge_str in edges_str.split(','):
                            nnode_str, edgew = edge_str.split('-')
                            edge_dict[nnode_str] = float(edgew)
                        qcaw_time += qcaw_com.addNode(node_str, float(node_w), edge_dict)
                        rqcaw_time += rqcaw_com.addNode(node_str, float(node_w), edge_dict)
                        zqcaw_time += zqcaw_com.addNode(node_str, float(node_w), edge_dict)
                        nwqca_time += nwqca_com.addNode(node_str, float(node_w), edge_dict)
                    elif test_type == 'rmNode':
                        node_str = line.strip().split()[1]
                        qcaw_time += qcaw_com.rmNode(node_str)
                        rqcaw_time += rqcaw_com.rmNode(node_str)
                        zqcaw_time += zqcaw_com.rmNode(node_str)
                        nwqca_time += nwqca_com.rmNode(node_str)
                    elif test_type in ['upEdge', 'downEdge']:
                        nodestr_pair, weight = line.strip().split()[1:]
                        node1_str, node2_str = nodestr_pair.split('-')
                        qcaw_time += qcaw_com.setEdgeWeight(node1_str, node2_str, float(weight))
                        rqcaw_time += rqcaw_com.setEdgeWeight(node1_str, node2_str, float(weight))
                        zqcaw_time += zqcaw_com.setEdgeWeight(node1_str, node2_str, float(weight))
                        nwqca_time += nwqca_com.setEdgeWeight(node1_str, node2_str, float(weight))
                    elif test_type == 'addEdge':
                        nodestr_pair, weight = line.strip().split()[1:]
                        node1_str, node2_str = nodestr_pair.split('-')
                        qcaw_time += qcaw_com.addEdge(node1_str, node2_str, float(weight))
                        rqcaw_time += rqcaw_com.addEdge(node1_str, node2_str, float(weight))
                        zqcaw_time += zqcaw_com.addEdge(node1_str, node2_str, float(weight))
                        nwqca_time += nwqca_com.addEdge(node1_str, node2_str, float(weight))
                    elif test_type == 'rmEdge':
                        nodestr_pair = line.strip().split()[1]
                        node1_str, node2_str = nodestr_pair.split('-')
                        qcaw_time += qcaw_com.rmEdge(node1_str, node2_str)
                        rqcaw_time += rqcaw_com.rmEdge(node1_str, node2_str)
                        zqcaw_time += zqcaw_com.rmEdge(node1_str, node2_str)
                        nwqca_time += nwqca_com.rmEdge(node1_str, node2_str)
                    qcaw_com.checkCom()
                    rqcaw_com.checkCom()
                    zqcaw_com.checkCom()
                    nwqca_com.checkCom()
            qcaw_list.append(qcaw_time*1e3/times)
            rqcaw_list.append(rqcaw_time*1e3/times)
            zqcaw_list.append(zqcaw_time*1e3/times)
            nwqca_list.append(nwqca_time*1e3/times)
        print('%d\t%s' % (idx, '\t'.join([str(times) for times in TIMES_LIST])))
        print('QCAW\t%s' % '\t'.join(['%.3f' % item for item in qcaw_list]))
        print('NWQCA\t%s' % '\t'.join(['%.3f' % item for item in nwqca_list]))
        print('QCAWRec\t%s' % '\t'.join(['%.3f' % item for item in rqcaw_list]))
        print('ZyyQCAW\t%s' % '\t'.join(['%.3f' % item for item in zqcaw_list]))
        print('')

if __name__ == "__main__":
    main()
