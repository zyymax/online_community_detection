#!/usr/bin/env python
"""
Coder:  max.zhang
Date:   2015-01-13
Desc:   main structures of network
"""
from pprint import pprint
import numpy


class Network(object):

    def __init__(self, ori_nodenum=10, mul=2):
        self._mat = numpy.zeros((ori_nodenum, ori_nodenum))
        self._node_dict = {}
        self._ori_nodenum = ori_nodenum
        self._mul = mul

    @property
    def _cur_size(self):
        return len(self._mat)

    @property
    def _node_num(self):
        return len(self._node_dict)

    def _expand(self):
        ori_size = self._cur_size
        new_size = ori_size * self._mul
        tmp_mat = numpy.zeros((new_size, new_size))
        for idx in xrange(ori_size):
            tmp_mat[idx][:ori_size] = self._mat[idx][:ori_size]
        self._mat = tmp_mat

    def _getNodeIdx(self, node_str):
        node_idx = self._node_dict.setdefault(node_str, self._node_num)
        if self._cur_size < self._node_num:
            self._expand()
        return node_idx

    def addEdge(self, node1_str, node2_str, weight=1):
        weight = float(weight)
        node1_idx = self._getNodeIdx(node1_str)
        node2_idx = self._getNodeIdx(node2_str)
        self._mat[node1_idx][node2_idx] = weight
        self._mat[node2_idx][node1_idx] = weight

    def show(self):
        print('[NodeIdx]\t[NodeStr]')
        print('\n'.join(['%s\t%s' % item for item in
                         [(value, key) for key, value in
                          self._node_dict.items()]]))
        print('[NodeIdx]\t[NodeIdx/Weight]...')
        for idx1 in range(self._node_num):
            nw_list = []
            w_list = self._mat[idx1]
            for idx2 in range(self._node_num):
                weight = self._mat[idx1][idx2]
                if weight < 1e-6:
                    continue
                nw_list.append('%s/%s' % (idx2, weight))
            print('%s\t%s' % (idx1, ','.join(nw_list)))

    def clear(self):
        self._mat = numpy.zeros((self._ori_nodenum, self._ori_nodenum))
        self._node_dict = {}

if __name__ == "__main__":
    net = Network()
    with open('data/net.edge') as ins:
        for line in ins:
            node1_str, node2_str, weight = line.strip().split()
            net.addEdge(node1_str, node2_str, weight)
    net.show()
