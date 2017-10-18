#!/usr/bin/env python
"""
Coder:  max.zhang
Date:   2015-01-13
Desc:   main structures of community
"""
from pprint import pprint
from collections import defaultdict
import random
from copy import deepcopy as dcp
from time import clock
import numpy
from zyy_network import Network
import cProfile

mov_dict = defaultdict(int)


def randList(ori_data):
    random.seed(None)
    ran_data = dcp(ori_data)
    size = len(ran_data)
    for idx1 in xrange(size):
        idx2 = random.randint(idx1, size-1)
        ran_data[idx1], ran_data[idx2] = ran_data[idx2], ran_data[idx1]
    return ran_data


class Community(Network):

    def __init__(self, ori_nodenum=10, mul=2):
        Network.__init__(self, ori_nodenum, mul)
        self._m = 0
        # Node data
        self._k = numpy.zeros(ori_nodenum)
        self._kin = numpy.zeros(ori_nodenum)
        # Community data
        self._in = numpy.zeros(ori_nodenum)
        self._tot = numpy.zeros(ori_nodenum)
        self._com = numpy.array(range(ori_nodenum))
        self._com_dict = defaultdict(dict)

    def modularity(self, comno_set=None):
        if comno_set is None:
            comno_set = set(self._com[:self._node_num])
        modul = 0.
        for com_no in comno_set:
            modul += self._in[com_no]/self._m - pow(self._tot[com_no]/(2*self._m), 2)
        return modul

    def _expandArr(self, ori_arr, old_size, new_size):
        tmp_arr = numpy.zeros(new_size)
        tmp_arr[:old_size] = ori_arr[:old_size]
        return tmp_arr

    def _expand(self):
        ori_size = self._cur_size
        Network._expand(self)
        new_size = ori_size * self._mul
        tmp_arr = numpy.array(range(new_size))
        tmp_arr[:ori_size] = self._com[:ori_size]
        self._com = tmp_arr
        self._k = self._expandArr(self._k, ori_size, new_size)
        self._kin = self._expandArr(self._kin, ori_size, new_size)
        self._in = self._expandArr(self._in, ori_size, new_size)
        self._tot = self._expandArr(self._tot, ori_size, new_size)

    def _updateWeight(self, node1_idx, node2_idx, weight):
        ori_weight = self._mat[node1_idx][node2_idx]
        delta_weight = weight-ori_weight
        self._m += delta_weight
        self._k[node1_idx] += delta_weight
        self._k[node2_idx] += delta_weight
        self._mat[node1_idx][node2_idx] += delta_weight
        self._mat[node2_idx][node1_idx] += delta_weight
        com1_no, com2_no = self._com[node1_idx], self._com[node2_idx]
        self._com_dict[com1_no][node1_idx] = 1
        self._com_dict[com2_no][node2_idx] = 1
        if com1_no == com2_no:
            self._in[com1_no] += delta_weight
            self._kin[node1_idx] += delta_weight
            self._kin[node2_idx] += delta_weight
        self._tot[com1_no] += delta_weight
        self._tot[com2_no] += delta_weight
        return delta_weight

    def mergeModul(self, node1_idx, node2_idx, weight):
        com1_no, com2_no = self._com[node1_idx], self._com[node2_idx]
        if com1_no > com2_no:
            com1_no, com2_no = com2_no, com1_no
        ori_in1, ori_in2 = self._in[com1_no], self._in[com2_no]
        ori_tot1, ori_tot2 = self._tot[com1_no], self._tot[com2_no]
        self._in[com1_no] = ori_in1 + ori_in2 + weight
        self._tot[com1_no] = ori_tot1 + ori_tot2
        Q_merge = self.modularity({com1_no})
        self._in[com1_no], self._tot[com1_no] = ori_in1, ori_tot1
        return Q_merge

    def mergeCom(self, node1_idx, node2_idx, weight):
        com1_no, com2_no = self._com[node1_idx], self._com[node2_idx]
        if com1_no > com2_no:
            com1_no, com2_no = com2_no, com1_no
        ori_in1, ori_in2 = self._in[com1_no], self._in[com2_no]
        ori_tot1, ori_tot2 = self._tot[com1_no], self._tot[com2_no]
        self._in[com1_no] = ori_in1 + ori_in2 + weight
        self._tot[com1_no] = ori_tot1 + ori_tot2
        self._in[com2_no], self._tot[com2_no] = 0., 0.
        self._kin[node1_idx] += weight
        self._kin[node2_idx] += weight
        for node_idx in self._com_dict[com2_no].keys():
            self._com[node_idx] = com1_no
            del self._com_dict[com2_no][node_idx]
            self._com_dict[com1_no][node_idx] = 1

    def extrInterModul(self, node1_idx, node2_idx, weight):
        com1_no, com2_no = self._com[node1_idx], self._com[node2_idx]
        new_comno = com1_no
        for tmp_com in xrange(self._node_num):
            if len(self._com_dict[tmp_com]) == 0:
                new_comno = tmp_com
                break
        ori_in1, ori_in2 = self._in[com1_no], self._in[com2_no]
        ori_tot1, ori_tot2 = self._tot[com1_no], self._tot[com2_no]
        self._in[new_comno] = weight
        self._tot[new_comno] = self._k[node1_idx] + self._k[node2_idx]
        self._in[com1_no] = ori_in1 - self._kin[node1_idx]
        self._tot[com1_no] = ori_tot1-self._k[node1_idx]
        self._in[com2_no] = ori_in2 - self._kin[node2_idx]
        self._tot[com2_no] = ori_tot2-self._k[node2_idx]
        Q_ext = self.modularity({com1_no, com2_no, new_comno})
        self._in[new_comno], self._tot[new_comno] = 0, 0
        self._in[com1_no], self._tot[com1_no] = ori_in1, ori_tot1
        self._in[com2_no], self._tot[com2_no] = ori_in2, ori_tot2
        return Q_ext, new_comno

    def extrInterCom(self, node1_idx, node2_idx, weight, new_comno):
        com1_no, com2_no = self._com[node1_idx], self._com[node2_idx]
        ori_in1, ori_in2 = self._in[com1_no], self._in[com2_no]
        ori_tot1, ori_tot2 = self._tot[com1_no], self._tot[com2_no]
        self._in[new_comno] = weight
        self._tot[new_comno] = self._k[node1_idx] + self._k[node2_idx]
        self._in[com1_no] = ori_in1 - self._kin[node1_idx]
        self._tot[com1_no] = ori_tot1-self._k[node1_idx]
        self._in[com2_no] = ori_in2 - self._kin[node2_idx]
        self._tot[com2_no] = ori_tot2-self._k[node2_idx]
        self._kin[node1_idx], self._kin[node2_idx] = [weight]*2
        self._com[node1_idx], self._com[node2_idx] = [new_comno]*2
        self._com_dict[new_comno][node1_idx] = 1
        self._com_dict[new_comno][node2_idx] = 1
        del self._com_dict[com1_no][node1_idx]
        del self._com_dict[com2_no][node2_idx]

    def extrIntraModul(self, node1_idx, node2_idx, weight):
        com_no = self._com[node1_idx]
        for tmp_com in xrange(self._node_num):
            if len(self._com_dict[tmp_com]) == 0:
                new_comno = tmp_com
                break
        ori_in = self._in[com_no]
        ori_tot = self._tot[com_no]
        self._in[new_comno] = weight
        self._tot[new_comno] = self._k[node1_idx] + self._k[node2_idx]
        self._in[com_no] = ori_in-self._kin[node1_idx]-self._kin[node2_idx]+weight
        self._tot[com_no] = ori_tot-self._k[node1_idx]-self._k[node2_idx]
        Q_ext = self.modularity({com_no, new_comno})
        self._in[new_comno], self._tot[new_comno] = 0, 0
        self._in[com_no], self._tot[com_no] = ori_in, ori_tot
        return Q_ext, new_comno

    def extrIntraCom(self, node1_idx, node2_idx, weight, new_comno):
        com_no = self._com[node1_idx]
        ori_in = self._in[com_no]
        ori_tot = self._tot[com_no]
        self._in[new_comno] = weight
        self._tot[new_comno] = self._k[node1_idx] + self._k[node2_idx]
        self._in[com_no] = ori_in-self._kin[node1_idx]-self._kin[node2_idx]+weight
        self._tot[com_no] = ori_tot-self._k[node1_idx]-self._k[node2_idx]

    def pullModul(self, node1_idx, node2_idx, weight):
        com1_no, com2_no = self._com[node1_idx], self._com[node2_idx]
        ori_in1, ori_in2 = self._in[com1_no], self._in[com2_no]
        ori_tot1, ori_tot2 = self._tot[com1_no], self._tot[com2_no]
        # edge weight from node1 to com2's nodes except node2
        kp = 0.
        for node_idx in self._com_dict[com2_no].keys():
            if node_idx == node2_idx:
                continue
            kp += self._mat[node1_idx][node_idx]
        self._in[com1_no] = ori_in1 - self._kin[node1_idx]
        self._tot[com1_no] = ori_tot1-self._k[node1_idx]
        self._in[com2_no] = ori_in2 + weight + kp
        self._tot[com2_no] = ori_tot2+self._k[node1_idx]
        Q_pull = self.modularity({com1_no, com2_no})
        self._in[com1_no], self._tot[com1_no] = ori_in1, ori_tot1
        self._in[com2_no], self._tot[com2_no] = ori_in2, ori_tot2
        return Q_pull, kp

    def pullCom(self, node1_idx, node2_idx, weight, kp):
        com1_no, com2_no = self._com[node1_idx], self._com[node2_idx]
        ori_in1, ori_in2 = self._in[com1_no], self._in[com2_no]
        ori_tot1, ori_tot2 = self._tot[com1_no], self._tot[com2_no]
        self._in[com1_no] = ori_in1 - self._kin[node1_idx]
        self._tot[com1_no] = ori_tot1-self._k[node1_idx]
        self._in[com2_no] = ori_in2 + weight + kp
        self._tot[com2_no] = ori_tot2+self._k[node1_idx]
        self._kin[node1_idx] = kp + weight
        self._kin[node2_idx] += weight
        self._com[node1_idx] = com2_no

    def updateIntraCom(self, node1_idx, node2_idx, weight):
        com_no = self._com[node1_idx]
        # Merge community
        Q_merge = self.modularity({com_no})
        # Extract two nodes
        Q_ext, new_comno = -1, com_no
        if len(self._com_dict[com_no]) != 2:
            Q_ext, new_comno = self.extrIntraModul(node1_idx, node2_idx, weight)
        if Q_ext > Q_merge:
            print Q_merge, Q_ext
            # print 'Extract'
            # print('Extracting %s and %s:%.6f' % (node1_idx, node2_idx, Q_ext))
            self.extrIntraCom(node1_idx, node2_idx, weight, new_comno)

    def updateInterCom(self, node1_idx, node2_idx, weight):
        com1_no, com2_no = self._com[node1_idx], self._com[node2_idx]
        # Seperate communities
        Q_sep = self.modularity({com1_no, com2_no})
        # Merge community
        Q_merge = self.mergeModul(node1_idx, node2_idx, weight)
        # Extract two nodes
        Q_ext, new_comno = -1, com1_no
        if not (len(self._com_dict[com1_no]) == 1 and len(self._com_dict[com2_no]) == 1):
            Q_ext, new_comno = self.extrInterModul(node1_idx, node2_idx, weight)
        Q_1to2, Q_2to1 = -1, -1
        kp_1to2, kp_2to1 = 0, 0
        if len(self._com_dict[com1_no]) != 1 and len(self._com_dict[com2_no]) != 1:
            # Move node1 to com2
            Q_1to2, kp_1to2 = self.pullModul(node1_idx, node2_idx, weight)
            # Move node2 to com1
            Q_2to1, kp_2to1 = self.pullModul(node2_idx, node1_idx, weight)
        q_max = max([Q_sep, Q_merge, Q_ext, Q_1to2, Q_2to1])
        # print Q_sep, Q_merge, Q_ext, Q_1to2, Q_2to1
        if abs(q_max-Q_merge) < 1e-6:
            mov_dict['Merge'] += 1
            # print 'Merge'
            # print('Merging %s and %s:%.6f' % (node1_idx, node2_idx, Q_merge))
            self.mergeCom(node1_idx, node2_idx, weight)
        elif abs(q_max-Q_ext) < 1e-6:
            mov_dict['Extract'] += 1
            # print 'Extract'
            # print('Extracting %s and %s:%.6f' % (node1_idx, node2_idx, Q_ext))
            self.extrInterCom(node1_idx, node2_idx, weight, new_comno)
        elif abs(q_max-Q_1to2) < 1e-6:
            mov_dict['1to2'] += 1
            # print '1to2'
            # print('add node:%s to com:%s:\t%.6f' %
            #       (node1_idx, com2_no, Q_1to2))
            self.pullCom(node1_idx, node2_idx, weight, kp_1to2)
        elif abs(q_max-Q_2to1) < 1e-6:
            mov_dict['2to1'] += 1
            # print '2to1'
            # print('add node:%s to com:%s:\t%.6f' %
            #       (node2_idx, com1_no, Q_2to1))
            self.pullCom(node2_idx, node1_idx, weight, kp_2to1)
        else:
            mov_dict['Seperate'] += 1

    def addEdge(self, node1_str, node2_str, weight):
        weight = float(weight)
        node1_idx = self._getNodeIdx(node1_str)
        node2_idx = self._getNodeIdx(node2_str)
        # print '[Before UpdateWeight]'
        delta_weight = self._updateWeight(node1_idx, node2_idx, weight)
        if delta_weight <= 0:
            return
        com1_no, com2_no = self._com[node1_idx], self._com[node2_idx]
        # print '[After UpdateWeight]'
        if com1_no != com2_no:
            self.updateInterCom(node1_idx, node2_idx, weight)
        """
        # Little improvement
        else:
            self.updateIntraCom(node1_idx, node2_idx, weight)
        """
        # print '[After UpdateCom]'
        # print '='*88

    def addNodeComno(self, node_idx, com_no):
        self._com[int(node_idx)] = int(com_no)
        self._com_dict[int(com_no)][int(com_no)] = 1

    def printInfo(self):
        print self._com
        print self._in
        print self._tot
        print self._com_dict

    def show(self):
        # Network.show(self)
        # print('[NodeIdx]\t[CommunityNo]')
        nodestr_list = ['']*self._node_num
        for node_str, node_idx in self._node_dict.items():
            nodestr_list[node_idx] = node_str
        com_dict = defaultdict(list)
        for idx in xrange(self._node_num):
            # print('%s\t%d' % (idx, self._com[idx]))
            com_dict[self._com[idx]].append(nodestr_list[idx])
        print('[CommunityNo]\t[Nodes]')
        for com_no, node_list in com_dict.items():
            print('%d\t%s' % (com_no, ','.join(node_list)))
        print('[Modularity]\n%.6f' % self.modularity())

    def clear(self):
        Network.clear(self)
        self._m = 0
        # Node data
        self._k = numpy.zeros(self._ori_nodenum)
        self._kin = numpy.zeros(self._ori_nodenum)
        # Community data
        self._in = numpy.zeros(self._ori_nodenum)
        self._tot = numpy.zeros(self._ori_nodenum)
        self._com = numpy.array(range(self._ori_nodenum))
        self._com_dict = defaultdict(dict)


def main():
    com = Community()
    edge1_list = []  # old_node <-> old_node
    edge2_list = []  # old_node <-> new_node
    edge3_list = []  # new_node <-> new_node
    with open('data/qcaw.jc') as ins:
        for line in ins:
            nodes_pair, weight = line.strip().split()
            node1_str, node2_str = nodes_pair.split('-')
            if node1_str in com._node_dict and node2_str in com._node_dict:
                edge1_list.append((node1_str, node2_str, weight))
            elif node1_str in com._node_dict or node2_str in com._node_dict:
                edge2_list.append((node1_str, node2_str, weight))
            else:
                edge3_list.append((node1_str, node2_str, weight))
    edge_list = []
    edge_list += edge1_list
    edge_list += edge2_list
    edge_list += edge3_list
    edge_list = [(n1, n2, w) for w, n1, n2 in
                 sorted([(float(w), n1, n2) for n1, n2, w in edge_list])]

    max_modul = 0
    for time in xrange(1):
        """
        for args in randList(edge1_list):
            com.addEdge(*args)
            com.show()
        for args in randList(edge2_list):
            com.addEdge(*args)
            com.show()
        for args in randList(edge3_list):
            com.addEdge(*args)
            com.show()
        """
        begin = clock()
        print '[TIMES]:', time
        l = edge_list
        l = randList(l)
        for idx, args in enumerate(l):
            com.addEdge(*args)
            # print('\radd %s edges in %ss' % (idx+1, (clock()-begin)/(idx+1))),
        # print
        tmp_modul = com.modularity()
        if tmp_modul > max_modul:
            max_modul = tmp_modul
        com.show()
        print mov_dict
        mov_dict.clear()
        com.clear()
    print "[MAX_MODULARITY]:", max_modul
    """
    with open('data/simple.par') as ins:
        for line in ins:
            node_idx, com_no = line.strip().split()
            com.addNodeComno(node_idx, com_no)
    """

if __name__ == "__main__":
    cProfile.run('main()', 'prof.stat')

