#!/usr/bin/env python
"""
Coder:  max.zhang
Date:   2015-04-13
Desc:   generate data for experiments
"""
import sys
import random
import time
import numpy as np
import cProfile


class WNetGene(object):
    def __init__(self, size):
        self._size = size
        self._nw = [0.]*size
        self._W = np.zeros((size, size))

    def _initNodeW(self):
        random.seed(time.time())
        for idx in xrange(self._size):
            self._nw[idx] = random.random()*9+1  # [1, 10)
            # self._nw[idx] = 1.

    def _initEdgeW(self):
        random.seed(time.time())
        edge_count = random.randint(0, self._size*self._size)
        print 'Edge Count:', edge_count
        while edge_count > 0:
            node1_idx = random.randint(0, self._size-1)
            node2_idx = node1_idx
            while node2_idx == node1_idx:
                node2_idx = random.randint(0, self._size-1)
            # if self._W[node1_idx][node2_idx] > 0:
            #     continue
            # edge_weight = random.random()  # [0, 1)
            edge_weight = 1.
            self._W[node1_idx][node2_idx], self._W[node2_idx][node1_idx] = [edge_weight] * 2
            edge_count -= 1

    def _initCliqEdgeW(self):
        random.seed(time.time())
        # Build Clique
        for node_idx in xrange(self._size):
            # for each node generate a clique with random size
            cliq_size = random.randint(3, 5)
            nodeidx_set = {node_idx}
            while len(nodeidx_set) < cliq_size:
                rand_node_idx = random.randint(0, self._size-1)
                nodeidx_set.add(rand_node_idx)
            # set edges
            for nid1 in nodeidx_set:
                for nid2 in nodeidx_set:
                    if nid1 < nid2:
                        self._W[nid1][nid2] = 1
        for nid1 in xrange(self._size):
            for nid2 in xrange(nid1+1, self._size):
                if self._W[nid1][nid2] == 1:
                    edgew = 1-random.random()  # (0, 1]
                    # edgew = 1.
                    self._W[nid1][nid2], self._W[nid2][nid1] = [edgew] * 2

    def toWNetStr(self):
        s_list = []
        for node_idx, node_weight in enumerate(self._nw):
            s_list.append('node\t%s\t%.3f' % (node_idx, node_weight))
        for node1_idx, row_data in enumerate(self._W):
            for node2_idx, edge_weight in enumerate(row_data):
                if node1_idx < node2_idx and abs(self._W[node1_idx][node2_idx]) > 1e-6:
                    s_list.append('edge\t%s-%s\t%.3f' % (
                        node1_idx, node2_idx, edge_weight*self._nw[node1_idx]*self._nw[node2_idx]))
        return '\n'.join(s_list)

    def initNet(self):
        self._initNodeW()
        # self._initEdgeW()
        self._initCliqEdgeW()


def main():
    assert len(sys.argv) == 3, "Usage:\t%s<size> <wnet_file>"
    wng = WNetGene(int(sys.argv[1]))
    wng.initNet()
    open(sys.argv[2], 'w').write(wng.toWNetStr())

if __name__ == "__main__":
    main()
    # cProfile.run('main()', 'geneExpData.stat')
