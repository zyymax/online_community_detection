#!/usr/bin/env python
"""
Coder:  max.zhang
Date:   2015-01-20
Desc:   implementation of AFOCS in MOBICOM'11
        Overlapping communities in dynamic networks: their detection and mobile applications
        by Nam P. Nguyen et.al.
"""
from pprint import pprint
from collections import defaultdict
import random
import itertools
from copy import deepcopy as dcp
import sys
from time import clock
from network import Network
from community import WeightCommunity as Community
from node import OverlapNode as Node
import cProfile

INTS_THRE = 100.
BETA = 1.8
COM_MIN_SIZE = 4
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


sigma = lambda x: pow(x, 1-1./x) if x >= 1 else pow(x, 1+x)

psi = lambda inner, total: inner/total

tau = lambda total: sigma(total)/total


def satisWtComCond(com):
    inner = com._win*2
    total = inner + (com._wtot-2*com._win)
    # return psi(inner, total) > tau(total)
    return com._ints > INTS_THRE


def satisUwtComCond(com):
    inner = com._ein
    total = com._c2
    return psi(inner, total) > tau(total)


class FOCSImp(Network):

    def __init__(self, cond):
        Network.__init__(self)
        self._beta = BETA
        self._satisComCond = cond

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
                ov = len(node1._com)
                for node2_idx in com._node.keys():
                    node2 = self._node_list[node2_idx]
                    ow = len(node2._com)
                    weight = node1._nb.get(node2_idx, 0)
                    tmp_modul += (weight-node1._du*node2._du/(2*m*ov*ow))
            modul += tmp_modul
        return modul/(2*m)

    def _checkNewCom(self, node_set):
        if len(node_set) >= COM_MIN_SIZE:
            new_com = Community(self._com_num)
            for node_idx in node_set:
                new_com.addNode(self._node_list[node_idx])
            if self._satisComCond(new_com):
                for node_idx in node_set:
                    self._node_list[node_idx].addCom(new_com._id)
                self._com_list.append(new_com)
                return new_com
        return None

    def _getNodeIdx(self, node_str):
        if node_str in self._nodestr_dict:
            node_idx = self._nodestr_dict[node_str]
        else:
            node_idx = self._node_num
            self._nodestr_dict[node_str] = node_idx
            node = Node(node_idx, node_str)
            self._node_list.append(node)
        return node_idx, self._node_list[node_idx]

    def commonCom(self, node1_idx, node2_idx):
        com1_set = self._node_list[node1_idx]._com
        com2_set = self._node_list[node2_idx]._com
        return com1_set.intersection(com2_set)

    def commonNode(self, com1_idx, com2_idx):
        node1_set = set(self._com_list[com1_idx]._node.keys())
        node2_set = set(self._com_list[com2_idx]._node.keys())
        return node1_set.intersection(node2_set)

    def commonNB(self, node1_idx, node2_idx):
        node1_set = set(self._node_list[node1_idx]._nb.keys())
        node2_set = set(self._node_list[node2_idx]._nb.keys())
        return node1_set.intersection(node2_set)

    def overlap_score(self, com1, com2):
        cmn_node = self.commonNode(com1._id, com2._id)
        com = Community(-1)
        for node_idx in cmn_node:
            com.addNode(self._node_list[node_idx])
        node_frac = 1.*com._node_num/min(com1._node_num, com2._node_num)
        link_frac = 1.*com._ein/min(com1._ein, com2._ein) if min(com1._ein, com2._ein) > 0 else 0
        return node_frac+link_frac

    def merge(self, comidx_set):
        if len(comidx_set) < 2:
            return
        comidx_list = list(set(comidx_set))
        done = False
        while not done:
            done = True
            for com1_idx, com2_idx in gene_pair(comidx_list):
                com1 = self._com_list[com1_idx]
                com2 = self._com_list[com2_idx]
                if com1 is None or com2 is None:
                    continue
                os = self.overlap_score(com1, com2)
                if os >= self._beta:
                    for node in com2._node.values():
                        node.delCom(com2._id)
                        node.addCom(com1._id)
                        com1.addNode(node)
                    self._com_list[com2._id] = None
                    done = False
        # print filter(lambda idx: self._com_list[idx] is not None, comidx_list)
        return

    def findLocalCom(self):
        for node1_idx, node in enumerate(self._node_list):
            for node2_idx, weight in node._nb.items():
                if node1_idx > node2_idx:
                    continue
                cmn_com = self.commonCom(node1_idx, node2_idx)
                if len(cmn_com) != 0:
                    continue
                cmn_nb = self.commonNB(node1_idx, node2_idx)
                new_node_set = cmn_nb.union({node1_idx, node2_idx})
                new_com = self._checkNewCom(new_node_set)

    def run(self):
        self.findLocalCom()
        com_list = filter(lambda idx: self._com_list[idx] is not None,
                          range(len(self._com_list)))
        print("Got %d local communities" % len(com_list))
        self.merge(com_list)

    def show(self):
        Network.show(self)
        print('Totally: %d nodes, %d communities, %d outlier nodes' % (
            self._node_num, len(
                filter(lambda idx: self._com_list[idx] is not None, range(self._com_num))), len(
                    filter(lambda idx: len(self._node_list[idx]._com) == 0, range(self._node_num)))))
        print('Overlap Modularity: %.6f' % self._overlap_modul())

    def checkCom(self):
        for node in self._node_list:
            for com_idx in node._com:
                if node._id not in self._com_list[com_idx]._node:
                    return False
        for com in self._com_list:
            if com is None:
                continue
            for node_idx in com._node:
                if not self._node_list[node_idx].hasCom(com._id):
                    return False
        return True


class AFOCSImp(FOCSImp):

    def __init__(self, focs_imp, cond):
        FOCSImp.__init__(self, cond)
        self._focs_imp = focs_imp
        self._node_list = focs_imp._node_list
        self._com_list = focs_imp._com_list
        self._nodestr_dict = focs_imp._nodestr_dict

    def addNode(self, new_node_str, edge_dict):
        new_nodeidx, new_node = self._getNodeIdx(new_node_str)
        adjcom_dict = {}
        for old_nodestr, weight in edge_dict.items():
            old_nodeidx, old_node = self._getNodeIdx(old_nodestr)
            for comidx in old_node._com:
                if comidx not in adjcom_dict:
                    adjcom_dict[comidx] = weight
                else:
                    adjcom_dict[comidx] += weight
            new_node.addNB(old_nodeidx, weight)
            old_node.addNB(new_nodeidx, weight)
        merge_comidx_list = adjcom_dict.keys()
        for adjcom_idx, weight in adjcom_dict.items():
            adjcom = self._com_list[adjcom_idx]
            if weight*(adjcom._node_num-1) > 2*adjcom._win:
                adjcom.addNode(new_node)
                new_node.addCom(adjcom_idx)
            else:
                node_set = set(new_node._nb.keys())
                node_set.intersection(adjcom._node.keys())
                new_com = self._checkNewCom(node_set)
                if new_com is not None:
                    merge_comidx_list.append(new_com._id)
        for node_idx, node in enumerate(self._node_list):
            if len(node._com) == 0:
                cmn_nb = self.commonNB(node_idx, new_nodeidx)
                new_com = self._checkNewCom(cmn_nb)
                if new_com is not None:
                    merge_comidx_list.append(new_com._id)
        self.merge(set(merge_comidx_list))

    def addEdge(self, node1_str, node2_str, weight):
        node1_idx, node1 = self._getNodeIdx(node1_str)
        node2_idx, node2 = self._getNodeIdx(node2_str)
        node1.addNB(node2_idx, weight)
        node2.addNB(node1_idx, weight)
        # print 'New Edge:', node1_idx, node2_idx, weight
        cmn_com = self.commonCom(node1_idx, node2_idx)
        for com_idx in node1._com:
            if self._com_list[com_idx].hasNode(node2_idx):
                # case 1, 2
                return
        if len(cmn_com) == 0:
            # case 3
            cmn_nb = self.commonNB(node1_idx, node2_idx)
            new_com = self._checkNewCom(cmn_nb)
            merge_com_set = set()
            if new_com is not None:
                merge_com_set.update(node1._com)
                merge_com_set.update(node2._com)
                merge_com_set.add(new_com._id)
                # not from paper
                for node_idx in cmn_nb:
                    merge_com_set.update(
                        self._node_list[node_idx]._com)
            else:
                for com_idx in node1._com:
                    com = self._com_list[com_idx]
                    com.addNode(node2)
                    if not self._satisComCond(com):
                        com.delNode(node2_idx)
                    else:
                        node2.addCom(com_idx)
                        merge_com_set.add(com_idx)
            self.merge(set(merge_com_set))

    def rmNode(self, node_str):
        pass

    def rmEdge(self, node1_str, node2_str):
        pass

    def clear(self):
        self._node_list = self._focs_imp._node_list
        self._com_list = self._focs_imp._com_list
        self._nodestr_dict = self._focs_imp._nodestr_dict


def main():
    com = FOCSImp(satisWtComCond)
    # com = FOCSImp(satisUwtComCond)
    # with open('data/edge.link.8') as ins:
    with open('data/qcaw.jc') as ins:
        for line in ins:
            nodes_pair, weight = line.strip().split()
            weight = float(weight)
            # weight = 1.
            node1_str, node2_str = nodes_pair.split('-')
            com.addEdge(node1_str, node2_str, weight)
    com.run()
    if not com.checkCom():
        return
    com.show()
    return
    # acom = AFOCSImp(com, satisWtComCond)
    acom = AFOCSImp(com, satisUwtComCond)
    edge_list = []
    with open('data/edge.link.9') as ins:
        for line in ins:
            nodes_pair, weight = line.strip().split()
            weight = float(weight)
            # weight = 100.
            node1_str, node2_str = nodes_pair.split('-')
            edge_list.append((node1_str, node2_str, weight))
    for time in xrange(1):
        begin = clock()
        print '[TIMES]:', time
        # l = edge_list
        # l = randList(l)
        for node1_str, node2_str, weight in edge_list:
            if acom._hasNodeName(node1_str) and acom._hasNodeName(node2_str):
                acom.addEdge(node1_str, node2_str, weight)
            elif acom._hasNodeName(node1_str) or acom._hasNodeName(node2_str):
                if acom._hasNodeName(node1_str):
                    acom.addNode(node2_str, {node1_str: weight})
                else:
                    acom.addNode(node1_str, {node2_str: weight})
            else:
                acom.addNode(node1_str, {})
                acom.addNode(node2_str, {node1_str: weight})
            """
            if not acom.checkCom():
                sys.stderr.write('Consistence ERROR: node-community not match!')
                return
            """
        acom.show()
        acom.clear()

if __name__ == "__main__":
    cProfile.run('main()', 'prof.stat')

