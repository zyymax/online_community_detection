#!/usr/bin/env python
# -*- coding:utf8 -*-
"""
Coder:  max.zhang
Date:   2015-03-12
Desc:   node-weighted Adaptive Disjoint Community Detection
        based on implementation of QCA in INFOCOM'11
        recursive version of zyy_qcaw
"""
from pprint import pprint
from collections import defaultdict
import random
import itertools
from copy import deepcopy as dcp
import sys
from time import time
from network import Network, timing
from qcaw import QCAWImp
from community import WeightCommunity as Community
from node import DisjointWeightedNode as Node
import cProfile

DY_PREFIX = 'data/dy_data/'
dy_outs = None


class QCAWRecImp(QCAWImp):

    def __init__(self):
        Network.__init__(self)
        self._m = 0.

    def _overlap_modul(self):
        m = 0.
        for node1 in self._node_list:
            for node2_idx, weight in node1._nb.items():
                m += weight
        m /= 2.
        modul = 0.
        for com_idx, com in enumerate(self._com_list):
            if com is None:
                continue
            tmp_modul = 0
            for node1_idx in com._node.keys():
                node1 = self._node_list[node1_idx]
                ov = 1.
                for node2_idx in com._node.keys():
                    node2 = self._node_list[node2_idx]
                    ow = 1.
                    weight = node1._nb.get(node2_idx, 0)
                    tmp_modul += (weight-node1._du*node2._du/(2*m*ov*ow))
            modul += tmp_modul
        return modul/(2*m)

    def _refineCom(self, com_idx):
        com = self._com_list[com_idx]
        if com is None:
            return
        nodeidx_list = com._node.keys()
        for node_idx in nodeidx_list:
            self._detBestCom(self._node_list[node_idx])

    def _detBestComAndRefine(self, node):
        ori_comidx, nrt_comidx = self._detBestCom(node)
        if ori_comidx is not None and ori_comidx != nrt_comidx:
            self._refineCom(ori_comidx)

    """
        Up weight of old node
        1. detBestCom of node
        2. check each nnode in other communities with delta_q
    """
    def upNodeWeight(self, node_str):
        node_idx, node = self._getNodeIdx(node_str)
        out_nb_set = set()
        # self._detBestComAndRefine(node)
        self._detBestCom(node_idx)
        for nnode_idx in node._nb.keys():
            if self._node_list[nnode_idx]._com != node._com:
                out_nb_set.add(nnode_idx)
        comidx_set = set()
        for nnode_idx in out_nb_set:
            delt_q = self._extract_delta_q(nnode_idx, node._com)
            if delt_q > 0:
                # move nnode to community of node
                nnode = self._node_list[nnode_idx]
                ori_com = self._com_list[nnode._com]
                new_com = self._com_list[node._com]
                new_com.addNode(nnode)
                nnode.setCom(new_com._id)
                ori_com.delNode(nnode._id)
                if ori_com._empty:
                    self._com_list[ori_com._id] = None
                comidx_set.add(ori_com._id)
        for com_idx in comidx_set:
            self._refineCom(com_idx)

    """
        Up weight of old node
        1. detBestCom of node
        2. detBestCom of nnode in other communities
    """
    def upNodeWeightv2(self, node_str):
        node_idx, node = self._getNodeIdx(node_str)
        self._detBestCom(node)
        out_nb_set = set()
        for nnode_idx in node._nb.keys():
            if self._node_list[nnode_idx]._com != node._com:
                out_nb_set.add(nnode_idx)
        comidx_set = set()
        for nnode_idx in out_nb_set:
            ori_comidx, nrt_comidx = self._detBestCom(self._node_list[nnode_idx])
            if ori_comidx != nrt_comidx:
                comidx_set.add(ori_comidx)
        for com_idx in comidx_set:
            self._refineCom(com_idx)

    """
        Up weight of old node
        1. detBestCom of node
        2. call upEdgeWeight
    """
    def upNodeWeightv3(self, node_str):
        node_idx, node = self._getNodeIdx(node_str)
        self._detBestCom(node_idx)
        out_nb_set = set()
        for nnode_idx in node._nb.keys():
            if self._node_list[nnode_idx]._com != node._com:
                out_nb_set.add(nnode_idx)
        for nnode_idx in out_nb_set:
            nnode_str = self._node_list[nnode_idx]._name
            self.upEdgeWeight(nnode_str, node_str)

    """
        Down weight of old node
        1. remove node
        2. add node with edge_dict
    """
    def downNodeWeight(self, node_str):
        node_idx, node = self._getNodeIdx(node_str)
        node_w = node._w
        edge_dict = {}
        for nnode_idx, weight in node._nb.items():
            nnode = self._node_list[nnode_idx]
            nnode.delNB(node_idx)
            edge_dict[nnode._name] = weight/(node._w*nnode._w)
        com = self._com_list[node._com]
        com.delNode(node_idx)
        if com._empty:
            self._com_list[com._id] = None
        self._node_list[node._id] = None
        del self._nodestr_dict[node_str]
        self._m -= node._du
        self.addNode(node_str, node_w, edge_dict)

    """
        Down weight of old node by rmNode, addNode and addEdge
        1. remove node
        2. add singleton node
        3. add edge_list
    """
    def downNodeWeightv2(self, node_str):
        node_idx, node = self._getNodeIdx(node_str)
        node_w = node._w
        edge_list = []
        for nnode_idx, weight in node._nb.items():
            nnode = self._node_list[nnode_idx]
            nnode.delNB(node_idx)
            edge_list.append((nnode, weight/(node._w*nnode._w)))
        com = self._com_list[node._com]
        com.delNode(node_idx)
        if com._empty:
            self._com_list[com._id] = None
        self._node_list[node._id] = None
        del self._nodestr_dict[node_str]
        self._m -= node._du
        self.addNode(node_str, node_w, {})
        for nnode, weight in edge_list:
            self.addEdge(node_str, nnode._name, node_w, nnode._w, weight)

    """
        Down weight of old node
        1. detBestCom of nnode in the same community
        2. detBestCom of node
    """
    def downNodeWeightv3(self, node_str):
        node_idx, node = self._getNodeIdx(node_str)
        out_nb_set = set()
        for nnode_idx in node._nb.keys():
            if self._node_list[nnode_idx]._com == node._com:
                out_nb_set.add(nnode_idx)
        for nnode_idx in out_nb_set:
            self._detBestCom(self._node_list[nnode_idx])
        self._detBestComAndRefine(node)

    """
        Set Weight to old node
    """
    @timing
    def setNodeWeight(self, node_str, new_w):
        assert self._hasNodeName(node_str), 'node %s do not exist' % node_str
        node_idx, node = self._getNodeIdx(node_str)
        ori_w = node._w
        if abs(new_w-ori_w) < 1e-6:
            return
        self._setOldNodeWeight(node_str, new_w)
        if new_w < ori_w:
            # dy_outs.write('downNodeWeight\t%s\t%.3f\n' % (node_str, new_w))
            self.downNodeWeightv3(node_str)
        elif new_w > ori_w:
            # dy_outs.write('upNodeWeight\t%s\t%.3f\n' % (node_str, new_w))
            self.upNodeWeightv2(node_str)

    @timing
    def addNode(self, new_node_str, new_node_w, edge_dict):
        new_nodeidx, new_node = self._getNodeIdx(new_node_str)
        new_node.setW(new_node_w)
        com = Community(self._com_num)
        self._com_list.append(com)
        com.addNode(new_node)
        new_node.setCom(com._id)
        nnodeidx_list = []
        for nnode_str, weight in edge_dict.items():
            nnode_idx, nnode = self._getNodeIdx(nnode_str)
            weight *= new_node_w*nnode._w
            new_node.addNB(nnode_idx, weight)
            nnode.addNB(new_node._id, weight)
            nnodeidx_list.append(nnode_idx)
            self._m += weight
        if abs(self._m) < 1e-6:
            return
        for nnode_idx in nnodeidx_list:
            self._detBestCom(self._node_list[nnode_idx])
        self._detBestCom(new_node)

    """
        Set Weight to new/old edge
    """
    @timing
    def setEdgeWeight(self, node1_str, node2_str, weight):
        node1_idx, node1 = self._getNodeIdx(node1_str)
        node2_idx, node2 = self._getNodeIdx(node2_str)
        ori_weight = node1._nb.get(node2_idx, 0.)
        new_weight = weight
        weight *= node1._w*node2._w
        if abs(weight-ori_weight) < 1e-6:
            return
        node1.addNB(node2_idx, weight)
        node2.addNB(node1_idx, weight)
        weight -= ori_weight
        self._m += weight
        if weight > 0:
            """
            dy_outs.write('upEdgeWeight\t%s-%s\t%.3f\n' % (
                node1_str, node2_str, new_weight))
            """
            self.upEdgeWeight(node1_str, node2_str)
        elif weight < 0:
            """
            dy_outs.write('downEdgeWeight\t%s-%s\t%.3f\n' % (
                node1_str, node2_str, new_weight))
            """
            self.downEdgeWeight(node1_str, node2_str)

    def _extract_delta_qv2(self, node_idx, dst_comidx):
        node = self._node_list[node_idx]
        src_com = self._com_list[node._com]
        dst_com = self._com_list[dst_comidx]
        n2c_dict = self._buildN2C(node_idx)
        src_n2c = n2c_dict[src_com._id]
        dst_n2c = n2c_dict[dst_comidx]
        src_tot = src_com._wtot
        dst_tot = dst_com._wtot
        return self._m*2*(dst_n2c-src_n2c)-node._du*(
            node._du+dst_tot-src_tot)

    """
        param weight: delta weight (new_weight-ori_weight)
    """
    def upEdgeWeight(self, node1_str, node2_str):
        node1_idx, node1 = self._getNodeIdx(node1_str)
        node2_idx, node2 = self._getNodeIdx(node2_str)
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
            # self._refineCom(ori_com._id)
            for nnode_idx in src_node._nb.keys():
                self._detBestCom(self._node_list[nnode_idx])

    """
        Down old edge weight
        1. remove edge
        2. setEdgeWeight
    """
    def downEdgeWeight(self, node1_str, node2_str):
        node1_idx, node1 = self._getNodeIdx(node1_str)
        node2_idx, node2 = self._getNodeIdx(node2_str)
        weight = node1._nb[node2_idx]
        if node1._com != node2._com:
            return
        self.rmEdge(node1_str, node2_str)
        self.setEdgeWeight(node1_str, node2_str, weight/(node1._w*node2._w))

    @timing
    def addEdge(self, node1_str, node2_str, weight):
        node1_idx, node1 = self._getNodeIdx(node1_str)
        node2_idx, node2 = self._getNodeIdx(node2_str)
        assert node1_idx not in node2._nb
        self.setEdgeWeight(node1_str, node2_str, weight)

    @timing
    def rmEdge(self, node1_str, node2_str):
        node1_idx, node1 = self._getNodeIdx(node1_str)
        node2_idx, node2 = self._getNodeIdx(node2_str)
        assert node1_idx in node2._nb
        self.setEdgeWeight(node1_str, node2_str, 0.)


def main():
    dy_fname = sys.argv[1]
    com = QCAWRecImp()
    before = None
    with open(dy_fname) as ins:
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
                timestamp = int(line.strip().split()[-1])
                if before is not None:
                    print('Average Cost: %.3f ms' % ((time()-before)*1e3))
                    print(timestamp-1)
                """
                global dy_outs
                if dy_outs is not None:
                    dy_outs.close()
                dy_outs = open(DY_PREFIX+'%s.dy' % time, 'w')
                dy_outs.write(line)
                """
                com.checkCom()
                com.show()
                before = time()
                # open('data/ncpair_data/%s.rqcaw' % (time-1), 'w').write(com.toComStruc())
    com.show()
    # open('data/ncpair_data/%s.rqcaw' % time, 'w').write(com.toComStruc())

if __name__ == "__main__":
    assert len(sys.argv) == 2, 'Usage:\t%s <dy_fname>' % sys.argv[0]
    main()
    # cProfile.run('main()', '%s.stat' % sys.argv[0])

