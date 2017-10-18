#!/usr/bin/env python
"""
Coder:  max.zhang
Date:   2015-01-29
Desc:   classes of hierarchical communities
"""
from node import OverlapNode as ONode, DisjointNode as DNode

TOPK = 50


class BaseCommunity(object):
    """
    Desc:   Base class of community
    Data:   _id|int: community id
            _node|dict: node dict
    """
    def __init__(self, com_idx):
        self._id = com_idx
        self._node = {}

    @property
    def _node_num(self):
        return len(self._node)

    @property
    def _empty(self):
        return len(self._node) == 0

    def addNode(self, node):
        self._node[node._id] = node

    def delNode(self, node_idx):
        del self._node[node_idx]

    def hasNode(self, node_idx):
        return node_idx in self._node

    def __repr__(self):
        return 'id:%s,node_list:%s' % (
            self._id, '-'.join([node._name for node in self._node.values()]))

    def __str__(self):
        return 'id:%s,node_list:%s' % (
            self._id, '-'.join([node._name for node in self._node.values()]))


class EdgeCommunity(BaseCommunity):
    """
    Desc:   community with edge
    Data:   _ein|int: count of inner edges
            _etot|float: sum of nb_count of inner nodes
            _c2|float: node_num*(node_num-1)/2.
    """

    @property
    def _ein(self):
        s = 0
        for node in self._node.values():
            for node_idx in node._nb.keys():
                if node_idx not in self._node:
                    continue
                s += 1
        return s/2.

    @property
    def _etot(self):
        s = 0
        for node in self._node.values():
            s += len(node._nb)
        return s

    @property
    def _c2(self):
        return self._node_num*(self._node_num-1)/2.

    def __repr__(self):
        return '%s,ein:%.3f,etot:%.3f' % (
            BaseCommunity.__repr__(self), self._ein, self._etot)

    def __str__(self):
        return '%s,ein:%.3f,etot:%.3f' % (
            BaseCommunity.__str__(self), self._ein, self._etot)


class WeightCommunity(EdgeCommunity):
    """
    Desc:   community with edge weight
    Data:   _win|float: sum of weight of inner edges
            _wtot|float: sum of _du of inner nodes
            _ints|float: intensity of edge-weighted network
    """

    @property
    def _ints(self):
        # NJP'07 Weighted network modules
        edgew_list = []
        for node1_idx, node1 in self._node.items():
            for node2_idx, node2 in self._node.items():
                if node1_idx >= node2_idx or node2_idx not in node1._nb:
                    continue
                edgew_list.append(node1._nb[node2_idx])
        intensity = 1.
        for edgew in edgew_list:
            intensity *= pow(edgew, 1./len(edgew_list))
        return intensity
        """
        if self._wtot < 1e-6:
            # BUG
            node_list = []
            for node in self._node.values():
                w = 0.
                for node_idx, weight in node._nb.items():
                    if node_idx in self._node:
                        w += weight
                node_list.append((w, node))
                print node
            node_list = sorted(node_list, reverse=True)
            # topK_nodes = '-'.join(['%s:%.3f' % (node._name, w) for w, node in node_list[:TOPK]])
            topK_nodes = ' '.join([node._name for _, node in node_list[:TOPK]])
            print self._win, self._ein, self._etot, topK_nodes
            return 0.
        return self._win/self._wtot
        """

    @property
    def _win(self):
        s = 0.
        for node in self._node.values():
            for node_idx, weight in node._nb.items():
                if node_idx not in self._node:
                    continue
                s += weight
        return s/2.

    @property
    def _wtot(self):
        s = 0.
        for node in self._node.values():
            s += node._du
        return s

    def __repr__(self):
        node_list = []
        for node in self._node.values():
            w = 0.
            for node_idx, weight in node._nb.items():
                if node_idx in self._node:
                    w += weight
            node_list.append((w, node))
        node_list = sorted(node_list, reverse=True)
        topK_nodes = '-'.join(['%s:%.3f' % (node._name, w) for w, node in node_list[:TOPK]])
        return '%s,win:%.3f,wtot:%.3f,ints:%.3f,TOPK:%s' % (
            EdgeCommunity.__repr__(self), self._win, self._wtot, self._ints, topK_nodes)

    def __str__(self):
        node_list = []
        for node in self._node.values():
            w = 0.
            for node_idx, weight in node._nb.items():
                if node_idx in self._node:
                    w += weight
            node_list.append((w, node))
        node_list = sorted(node_list, reverse=True)
        # topK_nodes = '-'.join(['%s:%.3f' % (node._name, w) for w, node in node_list[:TOPK]])
        topK_nodes = ' '.join([node._name for _, node in node_list[:TOPK]])
        return '%s,win:%.3f,wtot:%.3f,ints:%.3f,TOPK:%s' % (
            EdgeCommunity.__str__(self), self._win, self._wtot, self._ints, topK_nodes)

