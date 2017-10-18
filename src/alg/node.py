#!/usr/bin/env python
"""
Coder:  max.zhang
Date:   2015-01-29
Desc:   classes of hierarchical nodes
"""


class BaseNode(object):
    """
    Desc:   Base class of Node
    Data:   _id|int: id
            _name|str: name
    """
    def __init__(self, node_idx, node_str):
        self._id = node_idx
        self._name = node_str

    def __repr__(self):
        return 'id:%s,name:%s' % (self._id, self._name)

    def __str__(self):
        return 'id:%s,name:%s' % (self._id, self._name)


class ConNode(BaseNode):
    """
    Desc:   Node with connects and neighbours
    Data:   _nb|dict: neighbour dict
            _du|float: sum of weight of all connected edges
    """
    def __init__(self, node_idx, node_str):
        BaseNode.__init__(self, node_idx, node_str)
        self._nb = {}
        self._du = 0.

    def addNB(self, node_idx, weight):
        ori_weight = self._nb.get(node_idx, 0.)
        self._du += weight-ori_weight
        if self._du < 0:
            print 'addNB', self
            print node_idx, weight, ori_weight
            exit(1)
        self._nb[node_idx] = weight

    def delNB(self, node_idx):
        weight = self._nb[node_idx]
        self._du -= weight
        del self._nb[node_idx]
        return weight

    def __repr__(self):
        return '%s,nb:%s,du:%.3f' % (
            BaseNode.__repr__(self),
            ','.join(['%s/%.3f' % (key, value) for key, value in self._nb.items()]),
            self._du)

    def __str__(self):
        return '%s,nb:%s,du:%.3f' % (
            BaseNode.__str__(self),
            ','.join(['%s/%.3f' % (key, value) for key, value in self._nb.items()]),
            self._du)


class DisjointNode(ConNode):
    """
    Desc:   Node of Disjoint Network
    Data:   _com|int: community id
    """

    def __init__(self, node_idx, node_str):
        ConNode.__init__(self, node_idx, node_str)
        self._com = -1

    def setCom(self, com_idx):
        self._com = com_idx

    def clrCom(self):
        self._com = 0

    def __repr__(self):
        return '%s,com_idx:%s' % (
            ConNode.__repr__(self), self._com)

    def __str__(self):
        return '%s,com_idx:%s' % (
            ConNode.__str__(self), self._com)


class OverlapNode(ConNode):
    """
    Desc:   Node of Overlap Network
    Data:   _com|set: community id set
    """

    def __init__(self, node_idx, node_str):
        ConNode.__init__(self, node_idx, node_str)
        self._com = set()

    def addCom(self, com_idx):
        self._com.add(com_idx)

    def delCom(self, com_idx):
        self._com.remove(com_idx)

    def hasCom(self, com_idx):
        return com_idx in self._com

    def __repr__(self):
        return '%s,com_list:%s' % (
            ConNode.__repr__(self), ','.join([str(com_idx) for com_idx in self._com]))

    def __str__(self):
        return '%s,com_list:%s' % (
            ConNode.__str__(self), ','.join([str(com_idx) for com_idx in self._com]))


class DisjointWeightedNode(DisjointNode):
    """
    Desc:   Weighted Node of Disjoint Network
    Data:   _w|float: node weight
    """

    def __init__(self, node_idx, node_str, w=1.):
        DisjointNode.__init__(self, node_idx, node_str)
        self._w = w

    def setW(self, w):
        if abs(self._w-w) < 1e-6:
            return
        self._du *= w/self._w
        for node_idx, weight in self._nb.items():
            self._nb[node_idx] = weight*w/self._w
        self._w = w

    def __repr__(self):
        return '%s,w:%.3f' % (
            DisjointNode.__repr__(self), self._w)

    def __str__(self):
        return '%s,w:%.3f' % (
            DisjointNode.__str__(self), self._w)

