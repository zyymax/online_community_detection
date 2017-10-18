#!/usr/bin/env python
# -*-coding:utf8-*-
"""
Coder:  max.zhang
Date:   2015-01-23
Desc:   implementation of QCA in INFOCOM'11
        Adaptive Algorithms for Detecting Community Structure in Dynamic Social Networks
        by Nam P. Nguyen et.al.
"""
from pprint import pprint
from collections import defaultdict
import random
import itertools
from copy import deepcopy as dcp
import sys
from time import clock
from network import Network, timing
from community import WeightCommunity as Community
from node import DisjointNode as Node
import cProfile


gene_pair = lambda l: list(
    itertools.chain.from_iterable(
        [zip(l[:step+1], l[-step-1:])
         for step in xrange(len(l)-1)]))


def randList(ori_data):
    random.seed(None)
    ran_data = dcp(ori_data)
    size = len(ran_data)
    for idx1 in xrange(size):
        idx2 = random.randint(idx1, size-1)
        ran_data[idx1], ran_data[idx2] = ran_data[idx2], ran_data[idx1]
    return ran_data


class QCAImp(Network):

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

    def _modularity(self, comno_set=None):
        if self._m < 1e-6:
            return 0.
        if comno_set is None:
            comno_set = filter(
                lambda idx: self._com_list[idx] is not None,
                range(self._com_num))
        else:
            comno_set = set(comno_set)
        modul = 0.
        for com_no in comno_set:
            com = self._com_list[com_no]
            modul += com._win/self._m - pow(com._wtot/(2*self._m), 2)
        return modul

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

    def _nr_comno_set(self, node_idx):
        com_set = set()
        node = self._node_list[node_idx]
        for nb_idx in node._nb.keys():
            com_idx = self._node_list[nb_idx]._com
            if com_idx != node._com:
                com_set.add(com_idx)
        return com_set

    def _buildN2C(self, node_idx):
        tot_weight = 0.
        node = self._node_list[node_idx]
        n2c_dict = defaultdict(float)
        for nb_idx, weight in self._node_list[node_idx]._nb.items():
            com_idx = self._node_list[nb_idx]._com
            n2c_dict[com_idx] += weight
        return n2c_dict

    def _in_force(self, node_du, com_wtot, n2c_weight):
        return n2c_weight - node_du*(com_wtot-node_du)/(2*self._m)

    def _out_force(self, node_du, com_wtot, n2c_weight):
        return n2c_weight - node_du*com_wtot/(2*self._m)

    def _nrtCom(self, node_idx, comno_set=None):
        if comno_set is None:
            comno_set = set(filter(lambda idx: self._com_list is not None,
                                   range(self._com_num)))
        else:
            comno_set = set(comno_set)
        node = self._node_list[node_idx]
        n2c_dict = self._buildN2C(node_idx)
        max_force = self._in_force(node._du, self._com_list[node._com]._wtot, n2c_dict[node._com])
        nrtcom_idx = node._com
        for com_idx in comno_set:
            tmp_force = self._out_force(node._du, self._com_list[com_idx]._wtot, n2c_dict[com_idx])
            if tmp_force > max_force:
                max_force = tmp_force
                nrtcom_idx = com_idx
        return max_force, nrtcom_idx

    """
        Set of nodes in one community
    """
    def _nrtComofNodeSet(self, nodeidx_set, ori_comidx, comno_set=None):
        if comno_set is None:
            comno_set = set(filter(lambda idx: self._com_list is not None,
                                   range(self._com_num)))
        else:
            comno_set = set(comno_set)
        n2c_dict = defaultdict(float)
        node_du = 0.
        for node_idx in nodeidx_set:
            node = self._node_list[node_idx]
            node_du += node._du
            for nnode_idx, weight in node._nb.items():
                com_idx = self._node_list[nnode_idx]._com
                n2c_dict[com_idx] += weight
        max_force = self._in_force(node_du, self._com_list[ori_comidx]._wtot, n2c_dict[ori_comidx])
        nrtcom_idx = ori_comidx
        for com_idx in comno_set:
            tmp_force = self._out_force(node_du, self._com_list[com_idx]._wtot, n2c_dict[com_idx])
            if tmp_force > max_force:
                max_force = tmp_force
                nrtcom_idx = com_idx
        # print '_nrtComofNodeSet', nodeidx_set, ori_comidx, comno_set, max_force, nrtcom_idx
        return max_force, nrtcom_idx

    def _detBestCom(self, node):
        node_idx = node._id
        comno_set = self._nr_comno_set(node_idx)
        if len(comno_set) == 0:
            return None, None
        max_force, nrt_comidx = self._nrtCom(node_idx, comno_set)
        ori_comidx = node._com
        if nrt_comidx != ori_comidx:
            ori_com = self._com_list[node._com]
            best_com = self._com_list[nrt_comidx]
            best_com.addNode(node)
            node.setCom(nrt_comidx)
            ori_com.delNode(node_idx)
            if ori_com._empty:
                self._com_list[ori_com._id] = None
        return ori_comidx, nrt_comidx

    """
        Set of nodes in one community
    """
    def _detBestComofNodeSet(self, nodeidx_set, ori_comidx):
        comno_set = set()
        for node_idx in nodeidx_set:
            comno_set.update(self._nr_comno_set(node_idx))
        if len(comno_set) == 0:
            return
        max_force, nrt_comidx = self._nrtComofNodeSet(nodeidx_set, ori_comidx, comno_set)
        if nrt_comidx != ori_comidx:
            ori_com = self._com_list[ori_comidx]
            for node_idx in nodeidx_set:
                node = self._node_list[node_idx]
                best_com = self._com_list[nrt_comidx]
                best_com.addNode(node)
                node.setCom(nrt_comidx)
                ori_com.delNode(node_idx)
                if ori_com._empty:
                    self._com_list[ori_com._id] = None
        return nrt_comidx
        # print '_detBestComofNodeSet', nodeidx_set, max_force, nrt_comidx

    """
        Delta modularity of putting src_node into dst_com
        self._m, src_node._du, dst_com._tot not updated
        param node_idx: node
        param dst_comidx: dest community
        param weight: delta weight
    """
    def _delta_q(self, node_idx, dst_comidx, weight):
        node = self._node_list[node_idx]
        src_com = self._com_list[node._com]
        dst_com = self._com_list[dst_comidx]
        n2c_dict = self._buildN2C(node_idx)
        src_n2c = n2c_dict[src_com._id]
        dst_n2c = n2c_dict[dst_comidx]
        src_tot = src_com._wtot
        dst_tot = dst_com._wtot
        return 4*(self._m+weight)*(dst_n2c+weight-src_n2c)+src_n2c*(
            2*dst_tot-2*node._du-src_n2c)-2*(node._du+weight)*(
                node._du+weight+dst_tot-src_tot)

    """
        Delta modularity of putting src_node into dst_com
        self._m, src_node._du already updated
        param node_idx: node
        param dst_comidx: dest community
    """
    def _extract_delta_q(self, srcnode_idx, dst_comidx):
        return self._delta_q(srcnode_idx, dst_comidx, 0.)

    def _findCliq(self, node, node_set):
        for nnode1_idx in node._nb.keys():
            if nnode1_idx not in node_set:
                continue
            nnode1 = self._node_list[nnode1_idx]
            for nnode2_idx in nnode1._nb.keys():
                if nnode2_idx not in node_set:
                    continue
                return nnode1_idx, nnode2_idx
        return None

    def _cliqPerco(self, cliq, node_set):
        tmp_set = dcp(node_set)
        for node3_idx in tmp_set:
            if node3_idx in cliq:
                continue
            node3 = self._node_list[node3_idx]
            for node1_idx, node2_idx in gene_pair(list(cliq)):
                node2 = self._node_list[node2_idx]
                if node1_idx in node2._nb and node1_idx in node3._nb and node2_idx in node3._nb:
                    cliq.add(node3_idx)
                    node_set.remove(node3_idx)
                    self._cliqPerco(cliq, node_set)
                    break

    @timing
    def addNode(self, new_node_str, edge_dict):
        new_nodeidx, new_node = self._getNodeIdx(new_node_str)
        com = Community(self._com_num)
        self._com_list.append(com)
        com.addNode(new_node)
        new_node.setCom(com._id)
        nnodeidx_list = []
        for nnode_str, weight in edge_dict.items():
            nnode_idx, nnode = self._getNodeIdx(nnode_str)
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
        node1.addNB(node2_idx, weight)
        node2.addNB(node1_idx, weight)
        weight -= ori_weight
        self._m += weight
        if weight < 0:
            return
        if node1._com != node2._com:
            # dq_1to2 = self._delta_q(node1_idx, node2._com, weight)
            # dq_2to1 = self._delta_q(node2_idx, node1._com, weight)
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
    def rmNode(self, node_str):
        assert self._hasNodeName(node_str), 'node %s do not exist' % node_str
        node_idx, node = self._getNodeIdx(node_str)
        nnode_set = set()
        for nnode_idx, weight in node._nb.items():
            self._m -= weight
            nnode = self._node_list[nnode_idx]
            nnode.delNB(node_idx)
            if nnode._com == node._com:
                nnode_set.add(nnode_idx)
        ori_com = self._com_list[node._com]
        ori_com.delNode(node_idx)
        if ori_com._empty:
            self._com_list[ori_com._id] = None
        self._node_list[node_idx] = None
        del self._nodestr_dict[node_str]
        subcom_list = []
        while len(nnode_set) > 0:
            cur_nodeidx = nnode_set.pop()
            subcom = self._findCliq(self._node_list[cur_nodeidx], nnode_set)
            if subcom is None:
                subcom = {cur_nodeidx}
            else:
                nnode_set.remove(subcom[0])
                nnode_set.remove(subcom[1])
                subcom = {subcom[0], subcom[1], cur_nodeidx}
                self._cliqPerco(subcom, nnode_set)
            subcom_list.append(subcom)
            # print cur_nodeidx, subcom, self._node_list[cur_nodeidx]
        for subcom in subcom_list:
            if len(subcom) == 1:
                self._detBestCom(self._node_list[subcom.pop()])
            else:
                self._detBestComofNodeSet(subcom, node._com)

    """
        Seperate single node from its original community
    """
    def _sepSingNode(self, node):
        ori_com = self._com_list[node._com]
        if len(ori_com._node) == 1:
            return
        new_com = Community(self._com_num)
        self._com_list.append(new_com)
        new_com.addNode(node)
        node.setCom(new_com._id)
        ori_com.delNode(node._id)
        if ori_com._empty:
            self._com_list[ori_com._id] = None

    """
        Seprate single community by edge removal
        Split as 3 parts, detBestCom of 2 node set and other singleton nodes
    """
    def _sepSingComByEdge(self, node1_str, node2_str):
        node1_idx, node1 = self._getNodeIdx(node1_str)
        node2_idx, node2 = self._getNodeIdx(node2_str)
        assert node1._com == node2._com, 'Seperate community by inter-edge'
        com = self._com_list[node1._com]
        # find 'quasi-clique's and singleton nodes in original community
        node1_set = set()
        node2_set = set()
        onode_set = set()
        for node_idx, node in com._node.items():
            if node_idx == node1_idx or node_idx in node1._nb:
                if node_idx in node2._nb:
                    onode_set.add(node_idx)
                else:
                    node1_set.add(node_idx)
            elif node_idx == node2_idx or node_idx in node2._nb:
                node2_set.add(node_idx)
            else:
                onode_set.add(node_idx)
        # detect best community of 'quasi-clique' in node1_set
        self._detBestComofNodeSet(node1_set, com._id)
        # detect best community of 'quasi-clique' in node2_set
        self._detBestComofNodeSet(node2_set, com._id)
        # detect best community of singleton nodes in onode_set
        for node_idx in onode_set:
            ocd, nrd = self._detBestCom(self._node_list[node_idx])

    """
        Seprate single community by edge removal
        Split as 3 communities, detBestCom of 3 node set
    """
    def _sepSingComByEdgev2(self, node1_str, node2_str):
        node1_idx, node1 = self._getNodeIdx(node1_str)
        node2_idx, node2 = self._getNodeIdx(node2_str)
        assert node1._com == node2._com, 'Seperate community by inter-edge'
        com = self._com_list[node1._com]
        # find 'quasi-clique's and singleton nodes in original community
        node1_set = set()
        node2_set = set()
        onode_set = set()
        for node_idx, node in com._node.items():
            if node_idx == node1_idx or node_idx in node1._nb:
                if node_idx in node2._nb:
                    onode_set.add(node_idx)
                else:
                    node1_set.add(node_idx)
            elif node_idx == node2_idx or node_idx in node2._nb:
                node2_set.add(node_idx)
            else:
                onode_set.add(node_idx)
        new_com1 = Community(self._com_num)
        self._com_list.append(new_com1)
        for node_idx in node2_set:
            node = self._node_list[node_idx]
            node.setCom(new_com1._id)
            new_com1.addNode(node)
            com.delNode(node._id)
        for node_idx in onode_set:
            new_com = Community(self._com_num)
            self._com_list.append(new_com)
            node = self._node_list[node_idx]
            node.setCom(new_com._id)
            new_com.addNode(node)
            com.delNode(node._id)
        # detect best community of singleton nodes in onode_set
        for node_idx in onode_set:
            self._detBestCom(self._node_list[node_idx])
        # detect best community of 'quasi-clique' in node1_set
        self._detBestComofNodeSet(node1_set, com._id)
        # detect best community of 'quasi-clique' in node2_set
        self._detBestComofNodeSet(node2_set, new_com1._id)

    """
        Seprate single community by edge removal
        Split as singleton nodes, detBestCom of all nodes
    """
    def _sepSingComByEdgev3(self, node1_str, node2_str):
        node1_idx, node1 = self._getNodeIdx(node1_str)
        node2_idx, node2 = self._getNodeIdx(node2_str)
        assert node1._com == node2._com, 'Seperate community by inter-edge'
        com = self._com_list[node1._com]
        node_list = com._node.keys()
        for node_idx in node_list:
            new_com = Community(self._com_num)
            self._com_list.append(new_com)
            node = self._node_list[node_idx]
            node.setCom(new_com._id)
            new_com.addNode(node)
            com.delNode(node._id)
        if com._empty:
            self._com_list[com._id] = None
        for node_idx in node_list:
            self._detBestCom(self._node_list[node_idx])

    @timing
    def rmEdge(self, node1_str, node2_str):
        node1_idx, node1 = self._getNodeIdx(node1_str)
        node2_idx, node2 = self._getNodeIdx(node2_str)
        assert node2_idx in node1._nb, 'edge %s-%s do not exist' % (node1_str, node2_str)
        weight = node1._nb[node2_idx]
        self._m -= weight
        node1.delNB(node2_idx)
        node2.delNB(node1_idx)
        if node1._com != node2._com:
            return
        ori_com = self._com_list[node1._com]
        if len(node1._nb) == 0 and len(node2._nb) == 0:
            self._sepSingNode(node1)
        elif len(node1._nb) == 0:
            self._sepSingNode(node1)
            # self._detBestComofNodeSet(set(ori_com._node.keys()), ori_com._id)
        elif len(node2._nb) == 0:
            self._sepSingNode(node2)
            # self._detBestComofNodeSet(set(ori_com._node.keys()), ori_com._id)
        else:
            # find maximal quasi-cliques
            # detBestCom of singletons and quasi-cliques
            self._sepSingComByEdgev3(node1_str, node2_str)

    def clear(self):
        Network.clear(self)
        self._m = 0.

    def checkCom(self):
        for com in self._com_list:
            if com is None:
                continue
            s = 0.
            for node in com._node.values():
                s += node._du
            assert abs(s-com._wtot) < 1e-6, 'com:%s, s:%.3f' % (com, s)
        for node in self._node_list:
            if node is None:
                continue
            du = 0.
            for nb_idx, weight in node._nb.items():
                du += weight
            assert abs(du-node._du) < 1e-6, 'node:%s, du:%.3f' % (node, du)

    def show(self):
        Network.show(self)
        print('Totally: %d nodes, %d communities, %d outlier nodes' % (
            len(filter(lambda idx: self._node_list[idx] is not None,
                       range(self._node_num))),
            len(filter(lambda idx: self._com_list[idx] is not None,
                       range(self._com_num))),
            len(filter(lambda idx: self._node_list[idx] is not None and len(self._com_list[self._node_list[idx]._com]._node) == 1,
                       range(self._node_num)))))
        print('M:%.3f' % self._m)
        print('Modularity:%.6f' % self._modularity())

    def toComStruc(self):
        s_list = []
        for node in self._node_list:
            if node is None:
                continue
            s_list.append('%s\t%d' % (node._name, node._com))
        return '\n'.join(s_list)

    """
        Load community structure from output of toComStruc
    """
    def fromComStruc(self, fname):
        com_node_dict = {}
        nodeidx_set = set()
        with open(fname) as ins:
            for line in ins:
                node_str, com_idx = line.strip().split()
                com_idx = int(com_idx)
                if com_idx not in com_node_dict:
                    com_node_dict[com_idx] = [node_str]
                else:
                    com_node_dict[com_idx].append(node_str)
        if len(com_node_dict) == 0:
            return
        self._com_list = [None] * (max(com_node_dict.keys())+1)
        for com_idx, nodestr_list in com_node_dict.items():
            com = Community(com_idx)
            self._com_list[com_idx] = com
            for node_str in nodestr_list:
                assert self._hasNodeName(node_str)
                node_idx, node = self._getNodeIdx(node_str)
                nodeidx_set.add(node_idx)
                node.setCom(com_idx)
                com.addNode(node)
        for node in self._node_list:
            if node._id not in nodeidx_set:
                com = Community(self._com_num)
                self._com_list.append(com)
                node.setCom(com._id)
                com.addNode(node)


def main():
    dy_fname = sys.argv[1]
    com = QCAImp()
    with open(dy_fname) as ins:
        for line_no, line in enumerate(ins):
            if line.startswith('addEdge'):
                nodes_pair, weight = line.strip().split('\t')[1:]
                weight = float(weight)
                weight = 1.
                node1_str, node2_str = nodes_pair.split('-')
                com.addEdge(node1_str, node2_str, weight)
            elif line.startswith('addNode'):
                node_str, node_w, edges_str = line.strip('\n').split('\t')[1:]
                edge_dict = {}
                if len(edges_str.strip()) != 0:
                    for edge_str in edges_str.split(','):
                        nnode_str, weight = edge_str.split('-')
                        weight = 1.
                        edge_dict[nnode_str] = float(weight)
                com.addNode(node_str, edge_dict)
            elif line.startswith('rmEdge'):
                nodes_pair = line.strip().split('\t', 1)[-1]
                node1_str, node2_str = nodes_pair.split('-')
                com.rmEdge(node1_str, node2_str)
            elif line.startswith('rmNode'):
                com.rmNode(line.strip().split('\t')[-1])
            elif line.startswith('TIME:'):
                time = int(line.strip().split()[-1])
                print(time)
                com.checkCom()
                com.show()
        com.show()

if __name__ == "__main__":
    assert len(sys.argv) == 2, 'Usage:\t%s <dy_fname>' % sys.argv[0]
    main()
    # cProfile.run('main()', '%s.stat' % sys.argv[0])

