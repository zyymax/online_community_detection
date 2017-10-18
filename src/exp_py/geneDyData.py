#!/usr/bin/env python
"""
Coder:  max.zhang
Date:   2015-04-13
Desc:   generate dynamic data for experiments
"""
import sys
import random
import time
import numpy as np
import cProfile
from geneExpData import WNetGene


class WNetDyGene(WNetGene):
    def __init__(self, size):
        self._size = size
        self._nw = [0.]*size
        self._W = np.zeros((size, size))

    def _expandW(self, inc_size):
        self._new_W = np.zeros((self._size+inc_size, self._size+inc_size))
        for idx1, w_list in enumerate(self._W):
            for idx2, edgew in enumerate(w_list):
                self._new_W[idx1][idx2] = self._W[idx1][idx2]
        self._W = self._new_W
        self._size += inc_size

    def toWNetStr(self):
        s_list = []
        for node_idx, node_weight in enumerate(self._nw):
            s_list.append('node\t%s\t%.3f' % (node_idx, node_weight))
        for node1_idx, row_data in enumerate(self._W):
            for node2_idx, edge_weight in enumerate(row_data):
                if abs(self._W[node1_idx][node2_idx]) > 1e-6:
                    s_list.append('edge\t%s-%s\t%.3f' % (node1_idx, node2_idx, edge_weight))
        return '\n'.join(s_list)

    def fromWNetStr(self, wnet_file):
        with open(wnet_file) as ins:
            for line in ins:
                if line.startswith('node'):
                    _, nodeidx_str, nodew_str = line.strip().split()
                    self._nw[int(nodeidx_str)] = float(nodew_str)
                elif line.startswith('edge'):
                    _, nodepair_str, edgew_str = line.strip().split()
                    nodeidx1_str, nodeidx2_str = nodepair_str.split('-')
                    node1_idx = int(nodeidx1_str)
                    node2_idx = int(nodeidx2_str)
                    node1_w = self._nw[node1_idx]
                    node2_w = self._nw[node2_idx]
                    edgew = float(edgew_str)/(node1_w*node2_w)
                    self._W[node1_idx][node2_idx], self._W[node2_idx][node1_idx] = [edgew] * 2

    def _geneAddNode(self, times):
        random.seed(time.time())
        # self._expandW(times)
        s_list = []
        for idx in xrange(times):
            new_nodew = random.random()*9+1  # [1, 10)
            self._nw.append(new_nodew)
            nid1 = len(self._nw)-1
            cliq_size = random.randint(2, 4)
            nodeidx_set = set()
            while len(nodeidx_set) < cliq_size:
                rand_node_idx = random.randint(0, len(self._nw)-2)
                nodeidx_set.add(rand_node_idx)
            # set edges
            edge_list = []
            for nid2 in nodeidx_set:
                edgew = 1-random.random()  # (0, 1]
                # self._W[nid1][nid2], self._W[nid2][nid1] = [edgew]*2
                edge_list.append('%s-%.3f' % (nid2, edgew))
            s_list.append('addNode\t%s\t%.3f\t%s' % (nid1, new_nodew, ','.join(edge_list)))
        return '\n'.join(s_list)

    def _geneRmNode(self, times):
        random.seed(time.time())
        s_list = []
        nodeidx_set = set()
        for idx in xrange(times):
            node_idx = random.randint(0, self._size-1)
            while node_idx in nodeidx_set:
                node_idx = random.randint(0, self._size-1)
            nodeidx_set.add(node_idx)
            s_list.append('rmNode\t%s' % node_idx)
        return '\n'.join(s_list)

    def _geneAddEdge(self, times):
        random.seed(time.time())
        s_list = []
        for idx in xrange(times):
            node1_idx = random.randint(0, self._size-1)
            node2_idx = node1_idx
            while node1_idx == node2_idx or abs(self._W[node1_idx][node2_idx]) > 1e-6:
                node2_idx = random.randint(0, self._size-1)
            new_edgew = 1-random.random()  # (0, 1]
            self._W[node1_idx][node2_idx], self._W[node1_idx][node2_idx] = [new_edgew]*2
            s_list.append('addEdge\t%s-%s\t%.3f' % (node1_idx, node2_idx, new_edgew))
        return '\n'.join(s_list)

    def _geneRmEdge(self, times):
        random.seed(time.time())
        s_list = []
        edge_list = []
        for nid1, w_list in enumerate(self._W):
            for nid2, weight in enumerate(w_list):
                if nid1 >= nid2:
                    continue
                if abs(self._W[nid1][nid2]) > 1e-6:
                    edge_list.append((nid1, nid2))
        for idx in xrange(times):
            edgeid = random.randint(0, len(edge_list)-1)
            nid1, nid2 = edge_list[edgeid]
            edge_list.remove((nid1, nid2))
            self._W[nid1][nid2] = self._W[nid2][nid1] = 0
            s_list.append('rmEdge\t%s-%s' % (nid1, nid2))
        return '\n'.join(s_list)

    def _geneUpNode(self, times):
        random.seed(time.time())
        s_list = []
        for idx in xrange(times):
            node_idx = random.randint(0, self._size-1)
            old_nodew = self._nw[node_idx]
            new_nodew = 10-random.random()*(10-old_nodew)  # (old_nodew, 10]
            self._nw[node_idx] = new_nodew
            s_list.append('upNode\t%s\t%.3f' % (node_idx, new_nodew))
        return '\n'.join(s_list)

    def _geneDownNode(self, times):
        random.seed(time.time())
        s_list = []
        for idx in xrange(times):
            node_idx = random.randint(0, self._size-1)
            old_nodew = self._nw[node_idx]
            new_nodew = random.random()*(old_nodew-1)+1  # [1, old_nodew)
            self._nw[node_idx] = new_nodew
            s_list.append('downNode\t%s\t%.3f' % (node_idx, new_nodew))
        return '\n'.join(s_list)

    def _geneUpEdge(self, times):
        random.seed(time.time())
        s_list = []
        edge_list = []
        for nid1, w_list in enumerate(self._W):
            for nid2, weight in enumerate(w_list):
                if nid1 >= nid2:
                    continue
                if abs(self._W[nid1][nid2]) > 1e-6:
                    edge_list.append((nid1, nid2))
        for idx in xrange(times):
            edgeid = random.randint(0, len(edge_list)-1)
            nid1, nid2 = edge_list[edgeid]
            edge_list.remove((nid1, nid2))
            old_edgew = self._W[nid1][nid2]
            new_edgew = 1-random.random()*(1-old_edgew)  # (old_nodew, 1]
            self._W[nid1][nid2] = self._W[nid2][nid1] = new_edgew
            s_list.append('upEdge\t%s-%s\t%.3f' % (nid1, nid2, new_edgew))
        return '\n'.join(s_list)

    def _geneDownEdge(self, times):
        random.seed(time.time())
        s_list = []
        edge_list = []
        for nid1, w_list in enumerate(self._W):
            for nid2, weight in enumerate(w_list):
                if nid1 >= nid2:
                    continue
                if abs(self._W[nid1][nid2]) > 1e-6:
                    edge_list.append((nid1, nid2))
        for idx in xrange(times):
            edgeid = random.randint(0, len(edge_list)-1)
            nid1, nid2 = edge_list[edgeid]
            edge_list.remove((nid1, nid2))
            old_edgew = self._W[nid1][nid2]
            new_edgew = 0.
            while new_edgew < 1e-6:
                new_edgew = random.random()*old_edgew  # (0, old_nodew)
            self._W[nid1][nid2] = self._W[nid2][nid1] = new_edgew
            s_list.append('downEdge\t%s-%s\t%.3f' % (nid1, nid2, new_edgew))
        return '\n'.join(s_list)

    def geneDyType(self, type_str, times):
        if type_str == 'addNode':
            return self._geneAddNode(times)
        elif type_str == 'rmNode':
            return self._geneRmNode(times)
        elif type_str == 'addEdge':
            return self._geneAddEdge(times)
        elif type_str == 'rmEdge':
            return self._geneRmEdge(times)
        elif type_str == 'upNode':
            return self._geneUpNode(times)
        elif type_str == 'downNode':
            return self._geneDownNode(times)
        elif type_str == 'upEdge':
            return self._geneUpEdge(times)
        elif type_str == 'downEdge':
            return self._geneDownEdge(times)


def main():
    assert len(sys.argv) == 6, "Usage:\t%s <size> <wnet_file> <dy_type> <times> <dy_file>" % sys.argv[0]
    assert sys.argv[3] in ['addNode', 'rmNode', 'addEdge', 'rmEdge',
                           'upNode', 'downNode', 'upEdge', 'downEdge'], "Invalid dynamic type:%s" % (sys.argv[3])
    size, wnet_file, dy_type, times, dy_file = sys.argv[1:]
    wndg = WNetDyGene(int(size))
    wndg.fromWNetStr(wnet_file)
    open(dy_file, 'w').write(wndg.geneDyType(dy_type, int(times)))

if __name__ == "__main__":
    main()
    # cProfile.run('main()', 'geneDyData.stat')
