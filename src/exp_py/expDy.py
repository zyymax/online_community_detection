#!/usr/bin/env python
"""
Coder:  max.zhang
Date:   2015-04-14
Desc:   experiments on node dynamic
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


def main():
    assert len(sys.argv) == 4, 'Usage:\t%s <test_type> <net_size> <dy_times>' % sys.argv[0]
    test_type, net_size, dy_times = sys.argv[1:]
    assert test_type in ['upNode', 'downNode', 'addNode', 'rmNode', 'upEdge', 'downEdge', 'addEdge', 'rmEdge']
    qcaw_com = QCAWImp()
    zqcaw_com = ZyyQCAWImp()
    rqcaw_com = QCAWRecImp()
    nwqca_com = NWQCAImp()
    print("[EXP on %s]" % test_type)
    for idx in [net_size]:
        head_list = []
        baseline_list = []
        qcaw_list = []
        rqcaw_list = []
        zqcaw_list = []
        nwqca_list = []
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
                'IDX', str(idx)).replace(
                    'TIMES', dy_times)
        dy_count = 0
        open('tmp.net', 'w').write(qcaw_com.toNetStr())
        pipe = subprocess.Popen(['src/tools/comdet_baseline.sh', 'tmp.net'],
                                stderr=subprocess.PIPE)
        bl_mod = float(pipe.stderr.read())
        head_list.append(str(dy_count))
        baseline_list.append('%.4f' % bl_mod)
        qcaw_list.append('%.4f' % qcaw_com._modularity())
        rqcaw_list.append('%.4f' % rqcaw_com._modularity())
        zqcaw_list.append('%.4f' % zqcaw_com._modularity())
        nwqca_list.append('%.4f' % nwqca_com._modularity())
        with open(dy_file) as ins:
            for line in ins:
                if not line.startswith(test_type):
                    continue
                dy_count += 1
                head_list.append(str(dy_count))
                if test_type in ['upNode', 'downNode']:
                    node_str, node_w = line.strip().split()[1:]
                    qcaw_com.setNodeWeight(node_str, float(node_w))
                    rqcaw_com.setNodeWeight(node_str, float(node_w))
                    zqcaw_com.setNodeWeight(node_str, float(node_w))
                    nwqca_com.setNodeWeight(node_str, float(node_w))
                elif test_type == 'addNode':
                    node_str, node_w, edges_str = line.strip().split()[1:]
                    edge_dict = {}
                    for edge_str in edges_str.split(','):
                        nnode_str, edgew = edge_str.split('-')
                        edge_dict[nnode_str] = float(edgew)
                    qcaw_com.addNode(node_str, float(node_w), edge_dict)
                    rqcaw_com.addNode(node_str, float(node_w), edge_dict)
                    zqcaw_com.addNode(node_str, float(node_w), edge_dict)
                    nwqca_com.addNode(node_str, float(node_w), edge_dict)
                elif test_type == 'rmNode':
                    node_str = line.strip().split()[1]
                    qcaw_com.rmNode(node_str)
                    rqcaw_com.rmNode(node_str)
                    zqcaw_com.rmNode(node_str)
                    nwqca_com.rmNode(node_str)
                elif test_type in ['upEdge', 'downEdge']:
                    nodestr_pair, weight = line.strip().split()[1:]
                    node1_str, node2_str = nodestr_pair.split('-')
                    qcaw_com.setEdgeWeight(node1_str, node2_str, float(weight))
                    rqcaw_com.setEdgeWeight(node1_str, node2_str, float(weight))
                    zqcaw_com.setEdgeWeight(node1_str, node2_str, float(weight))
                    nwqca_com.setEdgeWeight(node1_str, node2_str, float(weight))
                elif test_type == 'addEdge':
                    nodestr_pair, weight = line.strip().split()[1:]
                    node1_str, node2_str = nodestr_pair.split('-')
                    qcaw_com.addEdge(node1_str, node2_str, float(weight))
                    rqcaw_com.addEdge(node1_str, node2_str, float(weight))
                    zqcaw_com.addEdge(node1_str, node2_str, float(weight))
                    nwqca_com.addEdge(node1_str, node2_str, float(weight))
                elif test_type == 'rmEdge':
                    nodestr_pair = line.strip().split()[1]
                    node1_str, node2_str = nodestr_pair.split('-')
                    qcaw_com.rmEdge(node1_str, node2_str)
                    rqcaw_com.rmEdge(node1_str, node2_str)
                    zqcaw_com.rmEdge(node1_str, node2_str)
                    nwqca_com.rmEdge(node1_str, node2_str)
                qcaw_com.checkCom()
                rqcaw_com.checkCom()
                zqcaw_com.checkCom()
                nwqca_com.checkCom()
                open('tmp.net', 'w').write(qcaw_com.toNetStr())
                pipe = subprocess.Popen(['src/tools/comdet_baseline.sh', 'tmp.net'],
                                        stderr=subprocess.PIPE)
                bl_mod = float(pipe.stderr.read())
                baseline_list.append('%.4f' % bl_mod)
                qcaw_list.append('%.4f' % qcaw_com._modularity())
                rqcaw_list.append('%.4f' % rqcaw_com._modularity())
                zqcaw_list.append('%.4f' % zqcaw_com._modularity())
                nwqca_list.append('%.4f' % nwqca_com._modularity())
        print('%s\t%s' % (idx, '\t'.join(head_list)))
        print('BL\t%s' % '\t'.join(baseline_list))
        print('QCAW\t%s' % '\t'.join(qcaw_list))
        print('NWQCA\t%s' % '\t'.join(nwqca_list))
        print('QCAWRec\t%s' % '\t'.join(rqcaw_list))
        print('ZyyQCAW\t%s' % '\t'.join(zqcaw_list))

if __name__ == "__main__":
    main()
