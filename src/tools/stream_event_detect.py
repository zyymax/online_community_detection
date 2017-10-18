#!/usr/bin/env python
"""
Coder:  max.zhang
Date:   2015-01-17
Desc:   online event detection
"""

import sys
import math
import itertools
from copy import deepcopy as dcp
from zyy_ddc import Community


BURSTY_THRE = 5
T = 1  # time step
THRESHOLD = 1  # filter noise
ALFA = 1-math.exp(math.log(0.5)/(0.5*T))  # learning rate
BETA = THRESHOLD
word_dict = {}
# Generate all two-tuples of a list
# [1,2,3] ==> (1,2),(1,3),(2,3)
gene_pair = lambda l: list(itertools.chain.from_iterable([zip(l[:step+1], l[-step-1:]) for step in xrange(len(l)-1)]))


class WordStat(object):

    def __init__(self, name):
        self._name = name
        self._doc_list = []
        self._occur = 0
        self._ewma = 0.
        self._ewmvar = 0.

    def indexDoc(self, docid):
        self._doc_list.append(docid)
        self._occur += 1

    @property
    def _bursty(self):
        return (self._occur-max(BETA, self._ewma))/(BETA+math.sqrt(self._ewmvar))

    def clear(self):
        self._occur = 0
        self._doc_list = []

    def jc(self, word2_stat):
        inter_docs = set(self._doc_list).intersection(set(word2_stat._doc_list))
        return len(inter_docs)*1. / (self._occur+word2_stat._occur-len(inter_docs))

    def updateStat(self):
        tmp = self._occur-self._ewma
        self._ewma += ALFA*tmp
        self._ewmvar = (1-ALFA)*(self._ewmvar+ALFA*tmp*tmp)

    def __str__(self):
        return 'name:%s, occur:%.3f, ewma:%.3f, ewmvar%.3f' % (
            self._name, self._occur, self._ewma, self._ewmvar)


bw_set = set()


def updateModel(com_model, wedge_outs, edge_outs):
    for word, word_stat in word_dict.items():
        if word_stat._bursty > BURSTY_THRE:
            if word_stat not in bw_set:
                edge_outs.write('addNode\t%s\n' % word_stat._name)
                wedge_outs.write('addNode\t%s\n' % word_stat._name)
            bw_set.add(word_stat)
    tmp_list = []
    for word_stat in bw_set:
        if word_stat._occur < 1e-6:
            edge_outs.write('rmNode\t%s\n' % word_stat._name)
            wedge_outs.write('rmNode\t%s\n' % word_stat._name)
            tmp_list.append(word_stat)
    for word_stat in tmp_list:
        bw_set.remove(word_stat)
    print len(bw_set), len(word_dict)
    edge_count = 0
    for word1_stat, word2_stat in gene_pair(list(bw_set)):
        try:
            node1_str, node2_str, weight = word1_stat._name, word2_stat._name, word1_stat.jc(word2_stat)
        except:
            print word1_stat
            print word2_stat
            exit(0)

        if abs(weight) < 1e-6:
            continue
        edge_count += 1
        """
        print node1_str, node2_str, weight
        com_model.addEdge(node1_str, node2_str, weight)
        edge_outs.write('addEdge\t%s-%s\t%.3f-%.3f\t%.3f\n' % (
            node1_str, node2_str, word1_stat._ewma, word2_stat._ewma, weight))
        """
        edge_outs.write('addEdge\t%s-%s\t%.3f\n' % (node1_str, node2_str, weight))
        wedge_outs.write('addEdge\t%s-%s\t%.3f-%.3f\t%.3f\n' % (
            node1_str, node2_str, word1_stat._occur, word2_stat._occur, weight))
    print edge_count


def updateStat():
    for word_stat in word_dict.values():
        word_stat.updateStat()
        word_stat.clear()

PREFIX1 = 'data/0718_link/0718_edge.wlink.'
PREFIX2 = 'data/0718_link/0718_edge.link.'


def main():
    last_time = None
    com_model = Community()
    for lineid, line in enumerate(sys.stdin):
        try:
            time, token_list = line.strip().split('\t', 1)
        except:
            continue
        if last_time is None:
            last_time = time
        if last_time != time:
            print '[Model] at time:', last_time
            if last_time != '0':
                wedge_outs = open('%s%d' % (PREFIX1, int(last_time)), 'w')
                wedge_outs.write('TIME:\t%s\n' % time)
                edge_outs = open('%s%d' % (PREFIX2, int(last_time)), 'w')
                edge_outs.write('TIME:\t%s\n' % time)
                updateModel(com_model, wedge_outs, edge_outs)
                wedge_outs.close()
                edge_outs.close()
                com_model.show()
                com_model.clear()
            updateStat()
            last_time = time
        for word in token_list.split():
            if word not in word_dict:
                word_dict[word] = WordStat(word)
            word_dict[word].indexDoc(lineid)
    wedge_outs = open('%s%d' % (PREFIX1, int(last_time)), 'w')
    edge_outs = open('%s%d' % (PREFIX2, int(last_time)), 'w')
    wedge_outs.write('TIME:\t%s\n' % time)
    edge_outs.write('TIME:\t%s\n' % time)
    updateModel(com_model, wedge_outs, edge_outs)
    wedge_outs.close()
    edge_outs.close()


if __name__ == "__main__":
    main()
