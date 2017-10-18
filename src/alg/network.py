#!/usr/bin/env python
"""
Coder:  max.zhang
Date:   2015-01-29
Desc:   main structures of network
        Note: _getNodeIdx is not implemented as it depends on the specific Class of Node
"""
import time


def timing(func):
    def inner(*args, **kwargs):
        before = time.time()
        func(*args, **kwargs)
        return time.time()-before
    return inner


class Network(object):

    def __init__(self):
        self._nodestr_dict = {}
        self._node_list = []
        self._com_list = []

    @property
    def _node_num(self):
        return len(self._node_list)

    @property
    def _com_num(self):
        return len(self._com_list)

    def _hasNodeName(self, node_str):
        return node_str in self._nodestr_dict

    def _getNodeIdx(self, node_str):
        raise NotImplemented

    def addEdge(self, node1_str, node2_str, weight):
        node1_idx, node1 = self._getNodeIdx(node1_str)
        node2_idx, node2 = self._getNodeIdx(node2_str)
        node1.addNB(node2_idx, weight)
        node2.addNB(node1_idx, weight)

    def show(self):
        """
        print('[NodeIdx]\t[NodeStr]')
        print('\n'.join(['%s\t%s' % item for item in
                         sorted([(value, key) for key, value in
                                 self._nodestr_dict.items()])]))
        print('[NodeIdx]\t[NodeIdx/Weight]...')
        for node1_idx, node1 in enumerate(self._node_list):
            if node1 is None:
                continue
            nb_list = []
            for node2_idx, weight in node1._nb.items():
                nb_list.append('%s/%s' % (node2_idx, weight))
            print('%s\t%s' % (node1_idx, ','.join(nb_list)))
        print('[ComIdx]\t[NodeIdx]...')
        """
        com_list = []
        for com_idx, com in enumerate(self._com_list):
            if com is None or len(com._node) < 3:
                continue
            if hasattr(com, '_ints'):
                com_list.append((com._ints, com))
            else:
                com_list.append((0., com))
        for rank, (ints, com) in enumerate(sorted(com_list, reverse=True)):
            print rank, ints, com

    def clear(self):
        self._nodestr_dict = {}
        self._node_list = []
        self._com_list = []

    def toNetStr(self):
        s_list = []
        for node1_idx, node1 in enumerate(self._node_list):
            if node1 is None:
                continue
            for node2_idx, weight in node1._nb.items():
                if node1_idx < node2_idx:
                    s_list.append('%s-%s\t%.3f' % (
                        node1._name, self._node_list[node2_idx]._name, weight))
        return '\n'.join(s_list)

    """
        load network from output of toNetStr
    """
    def fromNetStr(self, fname):
        self.clear()
        with open(fname) as ins:
            for line in ins:
                nodestr_pair, weight = line.strip().split()[1:]
                node1_str, node2_str = nodestr_pair.split('-')
                assert self._hasNodeName(node1_str) and self._hasNodeName(node2_str)
                node1_idx, node1 = self._getNodeIdx(node1_str)
                node2_idx, node2 = self._getNodeIdx(node2_str)
                node1.addNB(node2_idx, float(weight))
                node2.addNB(node1_idx, float(weight))
