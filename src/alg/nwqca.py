#!/usr/bin/env python
# -*- coding:utf8 -*-
"""
Coder:  max.zhang
Date:   2015-04-11
Desc:   node-weighted Adaptive Disjoint Community Detection
        based on implementation of QCA in INFOCOM'11
        read thesis for detail
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


class NWQCAImp(QCAWImp):

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

    def _delta_q(self, node_idx, dst_comidx):
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
        Algorithm 4-1
    """
    def _detBestCom(self, node, comno_set=None):
        if comno_set is None:
            comno_set = self._nr_comno_set(node._id)
        if len(comno_set) == 0:
            return node._com, node._com
        max_deltaq, nrt_comidx, ori_comidx = 0., node._com, node._com
        for com_idx in comno_set:
            tmp_deltaq = self._delta_q(node._id, com_idx)
            if tmp_deltaq > max_deltaq:
                max_deltaq = tmp_deltaq
                nrt_comidx = com_idx
        if nrt_comidx != ori_comidx:
            ori_com = self._com_list[node._com]
            best_com = self._com_list[nrt_comidx]
            best_com.addNode(node)
            node.setCom(nrt_comidx)
            ori_com.delNode(node._id)
            if ori_com._empty:
                self._com_list[ori_com._id] = None
        return ori_comidx, nrt_comidx

    """
        Algorithm 4-2
    """
    def _refineCom(self, rmv_node, src_comidx, dst_comidx):
        src_com = self._com_list[src_comidx]
        if src_com is None:
            return
        dst_com = self._com_list[dst_comidx]
        node_set = set()
        for node_idx in src_com._node.keys():
            if node_idx in rmv_node._nb:
                node_set.add(node_idx)
        while len(node_set) > 0:
            node_idx = node_set.pop()
            tmp_deltaq = self._delta_q(node_idx, dst_comidx)
            if tmp_deltaq > 0:
                node = self._node_list[node_idx]
                for nnode_idx in node._nb.keys():
                    if nnode_idx in src_com._node:
                        node_set.add(nnode_idx)
                dst_com.addNode(node)
                node.setCom(dst_comidx)
                src_com.delNode(node_idx)
                if src_com._empty:
                    self._com_list[src_com._id] = None

    """
        Extension of Algorithm 4-2
    """
    def _refineComExt(self, rmvnode_list, src_comidx):
        src_com = self._com_list[src_comidx]
        if src_com is None:
            return
        node_dict = defaultdict(set)
        for node_idx in src_com._node.keys():
            for rmv_node in rmvnode_list:
                if node_idx in rmv_node._nb:
                    node_dict[node_idx].add(rmv_node._com)
        while len(node_dict) > 0:
            node_idx, dstcom_set = node_dict.popitem()
            node = self._node_list[node_idx]
            ori_comidx, nrt_comidx = self._detBestCom(node, dstcom_set)
            if ori_comidx != nrt_comidx:
                for nnode_idx in node._nb.keys():
                    if nnode_idx in src_com._node:
                        node_dict[nnode_idx].add(nrt_comidx)

    """
        Algorithm 4-3
    """
    def _addNodeAdjust(self, node):
        self._detBestCom(node)
        for nnode_idx in node._nb.keys():
            nnode = self._node_list[nnode_idx]
            if nnode._com == node._com:
                continue
            com_set = {node._com}
            com = self._com_list[nnode._com]
            for dcom_idx in self._nr_comno_set(nnode._id):
                dcom = self._com_list[dcom_idx]
                if dcom._wtot < com._wtot-nnode._du:
                    com_set.add(dcom_idx)
            ori_comidx, nrt_comidx = self._detBestCom(nnode, com_set)
            if ori_comidx != nrt_comidx:
                self._refineCom(nnode, ori_comidx, nrt_comidx)

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
        self._addNodeAdjust(new_node)

    """
        Algorithm 4-4
    """
    def _rmNodeAdjust(self, node_set, ori_comidx):
        for node in node_set:
            if node._com != ori_comidx:
                continue
            o_comidx, n_comidx = self._detBestCom(node)
            if o_comidx != n_comidx:
                self._refineCom(node, o_comidx, n_comidx)

    @timing
    def rmNode(self, node_str):
        assert self._hasNodeName(node_str), 'node %s do not exist' % node_str
        node_idx, node = self._getNodeIdx(node_str)
        nnode_set = set()
        for nnode_idx, weight in node._nb.items():
            self._m -= weight
            nnode = self._node_list[nnode_idx]
            nnode.delNB(node_idx)
            if nnode._com == node._com:
                nnode_set.add(nnode)
        ori_com = self._com_list[node._com]
        ori_com.delNode(node_idx)
        self._node_list[node_idx] = None
        del self._nodestr_dict[node_str]
        if ori_com._empty:
            self._com_list[ori_com._id] = None
        else:
            self._rmNodeAdjust(nnode_set, ori_com._id)

    """
        Up weight of old node
        Using Algorithm 4-3: _addNodeAdjust
    """
    def upNodeWeight(self, node):
        self._addNodeAdjust(node)

    """
        Down weight of old node
        Using Algorithm 4-4: _rmNodeAdjust
    """
    def downNodeWeight(self, node):
        self._detBestCom(node)
        nnode_set = set()
        for nnode_idx, weight in node._nb.items():
            nnode = self._node_list[nnode_idx]
            if nnode._com == node._com:
                nnode_set.add(nnode)
        self._rmNodeAdjust(nnode_set, node._com)

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
            self.downNodeWeight(node)
        elif new_w > ori_w:
            # dy_outs.write('upNodeWeight\t%s\t%.3f\n' % (node_str, new_w))
            self.upNodeWeight(node)

    """
        Algorithm 4-5
    """
    def _addEdgeAdjust(self, node1, node2):
        if node1._com == node2._com:
            return
        com1 = self._com_list[node1._com]
        com2 = self._com_list[node2._com]
        com_set = {node2._com}
        for dcom_idx in self._nr_comno_set(node1._id):
            dcom = self._com_list[dcom_idx]
            if dcom._wtot < com1._wtot-node1._du:
                com_set.add(dcom_idx)
        ori_comidx1, nrt_comidx1 = self._detBestCom(node1, com_set)
        if ori_comidx1 != nrt_comidx1:
            self._refineCom(node1, ori_comidx1, nrt_comidx1)
        com_set = {node1._com}
        for dcom_idx in self._nr_comno_set(node2._id):
            dcom = self._com_list[dcom_idx]
            if dcom._wtot < com2._wtot-node2._du:
                com_set.add(dcom_idx)
        ori_comidx2, nrt_comidx2 = self._detBestCom(node2, com_set)
        if ori_comidx2 != nrt_comidx2:
            self._refineCom(node2, ori_comidx2, nrt_comidx2)
        # print 'com1', com1._id, ori_comidx1, nrt_comidx1
        # print 'com2', com2._id, ori_comidx2, nrt_comidx2

    """
        Algorithm 4-5
    """
    def _addEdgeAdjustv2(self, node1, node2):
        if node1._com == node2._com:
            return
        deltaq1 = self._delta_q(node1._id, node2._com)
        deltaq2 = self._delta_q(node2._id, node1._com)
        com1 = self._com_list[node1._com]
        com2 = self._com_list[node2._com]
        if deltaq1 < 0 and deltaq2 < 0:
            return
        # elif abs(deltaq1-deltaq2) < 1e-6:
        elif deltaq1 == deltaq2:
            new_com = Community(self._com_num)
            self._com_list.append(new_com)
            new_com.addNode(node1)
            new_com.addNode(node2)
            com1.delNode(node1._id)
            com2.delNode(node2._id)
            node1.setCom(new_com._id)
            node2.setCom(new_com._id)
            if com1._empty:
                self._com_list[com1._id] = None
            else:
                self._refineCom(node1, com1._id, new_com._id)
            if com2._empty:
                self._com_list[com2._id] = None
            else:
                self._refineCom(node2, com2._id, new_com._id)
        else:
            if deltaq1 < deltaq2:
                dst_com = com1
                src_node = node2
                src_com = com2
            # elif deltaq2 > 0 and (deltaq1 < 0 or abs(deltaq1) < 1e-6):
            # elif deltaq1 < deltaq2:
            elif deltaq2 < deltaq1:
                dst_com = com2
                src_node = node1
                src_com = com1
            src_com.delNode(src_node._id)
            dst_com.addNode(src_node)
            src_node.setCom(dst_com._id)
            if src_com._empty:
                self._com_list[src_com._id] = None
            else:
                """
                for nnode_idx in src_node._nb.keys():
                    self._detBestCom(self._node_list[nnode_idx])
                """
                self._refineCom(src_node, src_com._id, dst_com._id)

    """
        Up old edge weight
        Using algorithm 4-5: _addEdgeAdjust
    """
    def upEdgeWeight(self, node1, node2):
        self._addEdgeAdjust(node1, node2)

    """
        Algorithm 4-6
    """
    def _rmEdgeAdjust(self, node1, node2):
        if node1._com != node2._com:
            return
        src_com = self._com_list[node1._com]
        ori_comidx1, nrt_comidx1 = self._detBestCom(node1)
        ori_comidx2, nrt_comidx2 = self._detBestCom(node2)
        node_list = []
        if ori_comidx1 != nrt_comidx1:
            node_list.append(node1)
        if ori_comidx2 != nrt_comidx2:
            node_list.append(node2)
        self._refineComExt(node_list, ori_comidx1)
        """
        for node in src_com._node.values():
            if node._name not in node1._nb and node._name not in node2._nb:
                self._detBestCom(node)
        """
        """
        if ori_comidx1 != nrt_comidx1:
            self._refineCom(node1, ori_comidx1, nrt_comidx1)
        if ori_comidx2 != nrt_comidx2:
            self._refineCom(node2, ori_comidx2, nrt_comidx2)
        """

    """
        Down old edge weight
        Using algorithm 4-6: _rmEdgeAdjust
    """
    def downEdgeWeight(self, node1, node2):
        self._rmEdgeAdjust(node1, node2)

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
            # print 'upEdgeWeight', node1_str, node2_str, weight
            self.upEdgeWeight(node1, node2)
        elif weight < 0:
            """
            dy_outs.write('downEdgeWeight\t%s-%s\t%.3f\n' % (
                node1_str, node2_str, new_weight))
            """
            # print 'downEdgeWeight', node1_str, node2_str, weight
            self.downEdgeWeight(node1, node2)

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
        if len(node1._nb) == 0 and len(node2._nb) == 0:
            self._sepSingNode(node1)
        elif len(node1._nb) == 0:
            self._sepSingNode(node1)
        elif len(node2._nb) == 0:
            self._sepSingNode(node2)
        else:
            self.setEdgeWeight(node1_str, node2_str, 0.)


def main():
    dy_fname = sys.argv[1]
    com = NWQCAImp()
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
                open('data/weibo_data/03/%s.nc' % (timestamp-1), 'w').write(com.toComStruc())
    print('Average Cost: %.3f ms' % ((time()-before)*1e3))
    print(timestamp)
    com.show()
    open('data/weibo_data/03/%s.nc' % timestamp, 'w').write(com.toComStruc())

if __name__ == "__main__":
    assert len(sys.argv) == 2, 'Usage:\t%s <dy_fname>' % sys.argv[0]
    main()
    # cProfile.run('main()', '%s.stat' % sys.argv[0])
