#!/usr/bin/env python
"""
Coder:  max.zhang
Date:   2015-04-16
Desc:   generate dynamics with streaming weibo by word-pair
"""

import sys
import math
import time
import itertools
from collections import defaultdict
from copy import deepcopy as dcp


BURSTY_THRE = 5
T = 1  # time step
THRESHOLD = 5  # filter noise
ALFA = 1-math.exp(math.log(0.5)/(0.5*T))  # learning rate
BETA = THRESHOLD
JC_THRE = 0.1
OCCUR_THRE = THRESHOLD
# Generate all two-tuples of a list
# [1,2,3] ==> (1,2),(1,3),(2,3)
gene_pair = lambda l: list(itertools.chain.from_iterable(
    [zip(l[:step+1], l[-step-1:]) for step in xrange(len(l)-1)]))


def utf8(uni_str):
    assert isinstance(uni_str, unicode)
    return uni_str.encode('utf8')


def gbk(uni_str):
    assert isinstance(uni_str, unicode)
    return uni_str.encode('gbk')


class WordStat(object):

    def __init__(self, name):
        self._name = name
        self._occur = 0
        self._ewma = 0.
        self._ewmvar = 0.

    def addDoc(self):
        self._occur += 1

    @property
    def _bursty(self):
        return (self._occur-max(BETA, self._ewma))/(BETA+math.sqrt(self._ewmvar))

    def updateStat(self):
        tmp = self._occur-self._ewma
        self._ewma += ALFA*tmp
        self._ewmvar = (1-ALFA)*(self._ewmvar+ALFA*tmp*tmp)
        self._occur = 0

    def __str__(self):
        return 'name:%s, bursty:%.3f, occur:%.3f, ewma:%.3f, ewmvar:%.3f' % (
            utf8(self._name), self._bursty, self._occur, self._ewma, self._ewmvar)

    def __repr__(self):
        return 'name:%s, bursty:%.3f, occur:%.3f, ewma:%.3f, ewmvar:%.3f' % (
            utf8(self._name), self._bursty, self._occur, self._ewma, self._ewmvar)


class InvertedIndex(object):

    def __init__(self):
        self._dl_dict = defaultdict(set)

    def docCount(self, word_str):
        assert word_str in self._dl_dict
        return len(self._dl_dict[word_str])

    def hasWord(self, word_str):
        return word_str in self._dl_dict

    def indexDoc(self, word_str, docid):
        self._dl_dict[word_str].add(docid)

    def clearDocList(self):
        self._dl_dict = defaultdict(set)

    def jc(self, word1_str, word2_str):
        if word1_str not in self._dl_dict:
            return 0.
        if word2_str not in self._dl_dict:
            return 0.
        set1 = self._dl_dict[word1_str]
        set2 = self._dl_dict[word2_str]
        inter_docs = set1.intersection(set2)
        return len(inter_docs)*1. / (len(set1)+len(set2)-len(inter_docs))

    def __str__(self):
        s_list = []
        for word_str, doc_set in self._dl_dict.items():
            s_list.append('%s\t%s' % (word_str, ','.join([str(docid) for docid in doc_set])))
        return '\n'.join(s_list)

    def __repr__(self):
        s_list = []
        for word_str, doc_set in self._dl_dict.items():
            s_list.append('%s\t%s' % (word_str, ','.join([str(docid) for docid in doc_set])))
        return '\n'.join(s_list)


class WBDyBaseGene(object):
    def __init__(self, dy_prefix):
        self._w_dict = {}
        self._pre_ws = {}
        self._idx = InvertedIndex()
        self._W = {}
        self._ts = ''
        self._dy_prefix = dy_prefix
        self._pre_time = None

    def _updateTokens(self, docid, tokens):
        for word1, word2 in gene_pair(tokens):
            assert isinstance(word1, unicode)
            if word1 == word2 or len(word1) < 2 or len(word2) < 2:
                continue
            elif word1 > word2:
                word_pair = u'%s-%s' % (word2, word1)
            elif word1 < word2:
                word_pair = u'%s-%s' % (word1, word2)
            self._w_dict.setdefault(word_pair, WordStat(word_pair))
            word_stat = self._w_dict[word_pair]
            word_stat.addDoc()
            self._idx.indexDoc(word1, docid)
            self._idx.indexDoc(word2, docid)

    def _geneNewWord(self):
        new_ws = {}
        # Get new word from bursty word-pair
        for word_pair, word_stat in self._w_dict.items():
            if word_stat._bursty > BURSTY_THRE:
                for word_str in word_stat._name.split(u'-'):
                    if word_str not in self._pre_ws:
                        occur = self._idx.docCount(word_str)
                        if occur > OCCUR_THRE:
                            new_ws[word_str] = occur
        return new_ws

    def addDoc(self, docid, tokens, timestamp):
        if timestamp != self._ts:
            if self._ts != '':
                self.geneCurDy()
            self._pre_time = time.time()
            for ws in self._w_dict.values():
                ws.updateStat()
            self._idx.clearDocList()
            self._ts = timestamp
        self._updateTokens(docid, tokens)

    def geneCurDy(self):
        # print '%s\t%.3f' % (self._ts, (time.time()-self._pre_time)*1e3)
        new_ws = self._geneNewWord()
        self._geneDy(new_ws)

    def _geneDy(self, new_ws):
        dy_outs = open(self._dy_prefix+'.'+self._ts, 'w')
        rm_list = []
        # Remove shading word
        for word_str in self._pre_ws:
            # if not self._idx.hasWord(word_str) or
            # self._idx.docCount(word_str) < OCCUR_THRE:  # last
            if word_str not in new_ws:  # no last
                rm_list.append(word_str)
        for word_str in rm_list:
            del self._pre_ws[word_str]
            dy_outs.write('rmNode\t%s\n' % utf8(word_str))
            for edge_str in self._W.keys():
                name1, name2 = edge_str.split(u'-')
                if word_str in [name1, name2]:
                    del self._W[edge_str]
        # Add new word
        for word1_str in new_ws.keys():
            edge_list = []
            for word2_str in self._pre_ws.keys():
                weight = self._idx.jc(word1_str, word2_str)
                if weight < JC_THRE:
                    continue
                edge_list.append('%s-%.3f' % (utf8(word2_str), weight))
                if word1_str > word2_str:
                    self._W[u'%s-%s' % (word2_str, word1_str)] = weight
                else:
                    self._W[u'%s-%s' % (word1_str, word2_str)] = weight
            dy_outs.write('addNode\t%s\t%.3f\t%s\n' % (utf8(word1_str),
                                                       self._idx.docCount(word1_str),
                                                       ','.join(edge_list)))
        # Add new edge
        for word1_str, word2_str in gene_pair(new_ws.keys()):
            weight = self._idx.jc(word1_str, word2_str)
            if weight < JC_THRE:
                continue
            if word1_str > word2_str:
                edge_str = u'%s-%s' % (word2_str, word1_str)
            else:
                edge_str = u'%s-%s' % (word1_str, word2_str)
            dy_outs.write('addEdge\t%s\t%.3f\n' % (utf8(edge_str), weight))
            self._W[edge_str] = weight

        # Modify old word weight
        for word_str, pre_w in self._pre_ws.items():
            cur_w = self._idx.docCount(word_str)
            if cur_w > pre_w:
                dy_outs.write('upNode\t%s\t%.3f\n' % (utf8(word_str), cur_w))
            elif cur_w < pre_w:
                dy_outs.write('downNode\t%s\t%.3f\n' % (utf8(word_str), cur_w))
            self._pre_ws[word_str] = cur_w
        # Modify old edge weight
        # Add new edge
        for word1_str, word2_str in gene_pair(self._pre_ws.keys()):
            weight = self._idx.jc(word1_str, word2_str)
            if weight < JC_THRE:
                continue
            if word1_str > word2_str:
                edge_str = u'%s-%s' % (word2_str, word1_str)
            else:
                edge_str = u'%s-%s' % (word1_str, word2_str)
            if edge_str not in self._W:
                dy_outs.write('addEdge\t%s\t%.3f\n' % (utf8(edge_str), weight))
            elif weight > self._W[edge_str]:
                dy_outs.write('upEdge\t%s\t%.3f\n' % (utf8(edge_str), weight))
            elif weight < self._W[edge_str]:
                dy_outs.write('downEdge\t%s\t%.3f\n' % (utf8(edge_str), weight))
            self._W[edge_str] = weight
        self._pre_ws.update(new_ws)

    def __str__(self):
        s_list = []
        s_list.append('[Previous Word Stat]')
        for ws, w in self._pre_ws.items():
            s_list.append('%s\t%s' % (w, ws))
        s_list.append('[Previous Edge List]')
        for edge_str, weight in self._W.items():
            s_list.append('%s\t%s' % (utf8(edge_str), weight))
        s_list.append('[Word Dict]')
        s_list.append(utf8(u','.join(self._w_dict.keys())))
        return '\n'.join(s_list)

    def __repr__(self):
        s_list = []
        s_list.append('[Previous Word Stat]')
        for ws, w in self._pre_ws.items():
            s_list.append('%s\t%s' % (w, ws))
        s_list.append('[Previous Edge List]')
        for edge_str, weight in self._W.items():
            s_list.append('%s\t%s' % utf8(edge_str), weight)
        s_list.append('[Word Dict]')
        s_list.append(utf8(u','.join(self._w_dict.keys())))
        return '\n'.join(s_list)


def main():
    assert len(sys.argv) == 2, 'Usage:\t%s <dy_prefix>' % sys.argv[0]
    wbg = WBDyBaseGene(sys.argv[1])
    for lineid, line in enumerate(sys.stdin):
        try:
            time, token_list = line.strip().split('\t', 1)
        except:
            continue
        wbg.addDoc(lineid, token_list.decode('utf8').split(), time)
        # print wbg
    wbg.geneCurDy()
    # print wbg


if __name__ == "__main__":
    main()
