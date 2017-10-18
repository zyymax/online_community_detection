#!/usr/bin/env python
"""
Coder:  max.zhang
Date:   2015-01-29
Desc:   node-weighted Adaptive Disjoint Community Detection
        based on implementation of QCA in INFOCOM'11
"""
from pprint import pprint
from collections import defaultdict
import random
import itertools
from copy import deepcopy as dcp
import sys
from time import clock
from network import Network, timing
from qca import QCAImp
from community import WeightCommunity as Community
from node import DisjointWeightedNode as Node
import cProfile


def randList(ori_data):
    random.seed(None)
    ran_data = dcp(ori_data)
    size = len(ran_data)
    for idx1 in xrange(size):
        idx2 = random.randint(idx1, size-1)
        ran_data[idx1], ran_data[idx2] = ran_data[idx2], ran_data[idx1]
    return ran_data


class QCAWImp(QCAImp):

    def __init__(self):
        QCAImp.__init__(self)

    def _getNodeIdx(self, node_str):
        if node_str in self._nodestr_dict:
            node_idx = self._nodestr_dict[node_str]
            if self._node_list[node_idx] is None:
                self._node_list[node_idx] = Node(node_idx, node_str)
        else:
            node_idx = self._node_num
            self._nodestr_dict[node_str] = node_idx
            node = Node(node_idx, node_str)
            self._node_list.append(node)
        return node_idx, self._node_list[node_idx]

    """
        Set Weight to old node
    """
    def _setOldNodeWeight(self, node_str, new_w):
        assert self._hasNodeName(node_str), 'node %s do not exist' % node_str
        node_idx, node = self._getNodeIdx(node_str)
        ori_w = node._w
        if abs(new_w-ori_w) < 1e-6:
            return
        # modify weight in nnode._nb
        delta_m = 0
        for node2_idx, ori_weight in node._nb.items():
            node2 = self._node_list[node2_idx]
            weight = ori_weight*new_w/ori_w
            node2.addNB(node_idx, weight)
            delta_m += weight-ori_weight
        # modify weight in node
        node.setW(new_w)
        self._m += delta_m

    @timing
    def addNode(self, new_node_str, new_node_w, edge_dict):
        assert not self._hasNodeName(new_node_str), 'node %s already exist' % new_node_str
        new_nodeidx, new_node = self._getNodeIdx(new_node_str)
        new_node.setW(new_node_w)
        com = Community(self._com_num)
        self._com_list.append(com)
        com.addNode(new_node)
        new_node.setCom(com._id)
        nnodeidx_list = []
        for nnode_str, weight in edge_dict.items():
            nnode_idx, nnode = self._getNodeIdx(nnode_str)
            # print 'addNode', weight, new_node_w, nnode_w
            weight *= new_node_w*nnode._w
            new_node.addNB(nnode_idx, weight)
            nnode.addNB(new_node._id, weight)
            nnodeidx_list.append(nnode_idx)
            self._m += weight
        if abs(self._m) < 1e-6:
            return
        for nnode_idx in nnodeidx_list:
            self._detBestCom(self._node_list[nnode_idx])
        self._detBestCom(self._node_list[new_nodeidx])

    @timing
    def addEdge(self, node1_str, node2_str, weight):
        node1_idx, node1 = self._getNodeIdx(node1_str)
        node2_idx, node2 = self._getNodeIdx(node2_str)
        ori_weight = node1._nb.get(node2_idx, 0.)
        weight *= node1._w * node2._w
        node1.addNB(node2_idx, weight)
        node2.addNB(node1_idx, weight)
        weight -= ori_weight
        self._m += weight
        if weight < 0:
            return
        if node1._com != node2._com:
            dq_1to2 = self._extract_delta_q(node1_idx, node2._com)
            dq_2to1 = self._extract_delta_q(node2_idx, node1._com)
            if dq_1to2 < 0 and dq_2to1 < 0:
                return
            if dq_1to2 > dq_2to1:
                # move node1 to node2._com
                dst_com = self._com_list[node2._com]
                src_node = node1
            else:
                # move node2 to node1._com
                dst_com = self._com_list[node1._com]
                src_node = node2
            ori_com = self._com_list[src_node._com]
            ori_com.delNode(src_node._id)
            if ori_com._empty:
                self._com_list[ori_com._id] = None
            dst_com.addNode(src_node)
            src_node.setCom(dst_com._id)
            for nnode_idx in src_node._nb.keys():
                self._detBestCom(self._node_list[nnode_idx])

    @timing
    def setNodeWeight(self, node_str, new_nodew):
        node_idx, node = self._getNodeIdx(node_str)
        edge_dict = {}
        old_nodew = node._w
        for nnode_idx, weight in node._nb.items():
            nnode = self._node_list[nnode_idx]
            edge_dict[nnode._name] = weight/(old_nodew*nnode._w)
        self.rmNode(node._name)
        self.addNode(node._name, new_nodew, edge_dict)

    @timing
    def setEdgeWeight(self, node1_str, node2_str, new_edgew):
        self.rmEdge(node1_str, node2_str)
        self.addEdge(node1_str, node2_str, new_edgew)

    def checkCom(self):
        for com in self._com_list:
            if com is None:
                continue
            s = 0.
            for node in com._node.values():
                assert node._com == com._id, 'node:%s, com:%s' % (node, com)
                s += node._du
            assert abs(s-com._wtot) < 1e-3, 'com:%s, s:%.3f' % (com, s)
        tmp_m = 0.
        for node in self._node_list:
            if node is None:
                continue
            com = self._com_list[node._com]
            assert node._id in com._node, 'node:%s, com:%s' % (node, com)
            du = 0.
            for nb_idx, weight in node._nb.items():
                du += weight
            assert abs(du-node._du) < 1e-3, 'node:%s, du:%.3f' % (node, du)
            tmp_m += du
        assert abs(self._m-tmp_m/2.) < 1e-3, 'm:%.3f, tmp_m:%.3f' % (self._m, tmp_m)

    """
        Override toNetStr in Network
    """
    def toNetStr(self):
        s_list = []
        for node_idx, node in enumerate(self._node_list):
            if node is None:
                continue
            s_list.append('node\t%s\t%.3f' % (node._name, node._w))
        for node1_idx, node1 in enumerate(self._node_list):
            if node1 is None:
                continue
            for node2_idx, weight in node1._nb.items():
                node2 = self._node_list[node2_idx]
                if node1_idx < node2_idx:
                    s_list.append('edge\t%s-%s\t%.3f' % (
                        node1._name, node2._name, weight))
        return '\n'.join(s_list)

    """
        Override fromNetStr in Network
    """
    def fromNetStr(self, fname):
        self.clear()
        with open(fname) as ins:
            for line in ins:
                if line.startswith('node'):
                    node_str, w_str = line.strip().split()[1:]
                    node_idx, node = self._getNodeIdx(node_str)
                    node.setW(float(w_str))
                elif line.startswith('edge'):
                    nodestr_pair, weight = line.strip().split()[1:]
                    weight = float(weight)
                    node1_str, node2_str = nodestr_pair.split('-')
                    assert self._hasNodeName(node1_str) and self._hasNodeName(node2_str)
                    node1_idx, node1 = self._getNodeIdx(node1_str)
                    node2_idx, node2 = self._getNodeIdx(node2_str)
                    node1.addNB(node2_idx, weight)
                    node2.addNB(node1_idx, weight)
                    self._m += weight


def main():
    link_fname = sys.argv[1]
    com = QCAWImp()
    with open(link_fname) as ins:
        for line_no, line in enumerate(ins):
            if line.startswith('addEdge'):
                nodes_pair, weight = line.strip().split('\t')[1:]
                weight = float(weight)
                node1_str, node2_str = nodes_pair.split('-')
                com.addEdge(node1_str, node2_str, weight)
            elif line.startswith('addNode'):
                node_str, node_w, edges_str = line.strip('\n').split('\t')[1:]
                node_w = float(node_w)
                edge_dict = {}
                if len(edges_str.strip()) != 0:
                    for edge_str in edges_str.split(','):
                        nnode_str, weight = edge_str.split('-')
                        edge_dict[nnode_str] = float(weight)
                com.addNode(node_str, node_w, edge_dict)
            elif line.startswith('rmEdge'):
                nodes_pair = line.strip().split('\t')[-1]
                node1_str, node2_str = nodes_pair.split('-')
                com.rmEdge(node1_str, node2_str)
            elif line.startswith('rmNode'):
                com.rmNode(line.strip().split('\t')[-1])
            elif line.startswith('upNode') or line.startswith('downNode'):
                node_str, node_w = line.strip().split('\t')[1:]
                com.setNodeWeight(node_str, float(node_w))
            elif line.startswith('upEdge') or line.startswith('downEdge'):
                nodes_pair, weight = line.strip().split('\t')[1:]
                weight = float(weight)
                node1_str, node2_str = nodes_pair.split('-')
                com.setEdgeWeight(node1_str, node2_str, weight)
            elif line.startswith('TIME:'):
                time = int(line.strip().split()[-1])
                print(time)
                com.checkCom()
                com.show()
                # open('data/jc_data/%s.jc' % (time-1), 'w').write(Network.toNetStr(com))
                # open('data/net_data/%s.qcaw' % (time-1), 'w').write(com.toNetStr())
                # open('data/ncpair_data/%s.qcaw' % (time-1), 'w').write(com.toComStruc())
        com.show()
        # open('data/jc_data/%s.jc' % time, 'w').write(Network.toNetStr(com))
        # open('data/ncpair_data/%s.qcaw' % time, 'w').write(com.toComStruc())
        # open('data/net_data/%s.qcaw' % time, 'w').write(com.toNetStr())

if __name__ == "__main__":
    assert len(sys.argv) == 2, 'Usage:\t%s <dy_fname>' % sys.argv[0]
    main()
    # cProfile.run('main()', '%s.stat' % sys.argv[0])

