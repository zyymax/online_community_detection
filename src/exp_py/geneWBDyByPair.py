#!/usr/bin/env python
"""
Coder:  max.zhang
Date:   2015-04-16
Desc:   generate dynamics with streaming weibo
"""

import sys
import math
import itertools
from geneWBDyBase import InvertedIndex, WordStat, WBDyBaseGene
from geneWBDyBase import BURSTY_THRE, T, THRESHOLD, ALFA, BETA, JC_THRE, OCCUR_THRE
from geneWBDyBase import gene_pair, utf8, gbk
from copy import deepcopy as dcp


class WBDyPairGene(WBDyBaseGene):
    def _updateTokens(self, docid, tokens):
        for word1, word2 in gene_pair(tokens):
            assert isinstance(word1, unicode)
            if word1 == word2 or len(word1) < 2 or len(word2) < 2:
                continue
            elif word1 > word2:
                word_pair = u'%s/%s' % (word2, word1)
            elif word1 < word2:
                word_pair = u'%s/%s' % (word1, word2)
            self._w_dict.setdefault(word_pair, WordStat(word_pair))
            word_stat = self._w_dict[word_pair]
            word_stat.addDoc()
            self._idx.indexDoc(word_pair, docid)

    def _geneNewWord(self):
        new_ws = {}
        # Get new word from bursty word
        for word_str, word_stat in self._w_dict.items():
            if word_stat._bursty > BURSTY_THRE:
                if word_str not in self._pre_ws:
                    occur = self._idx.docCount(word_str)
                    if occur > OCCUR_THRE:
                        new_ws[word_str] = occur
        return new_ws


def main():
    assert len(sys.argv) == 2, 'Usage:\t%s <dy_prefix>' % sys.argv[0]
    wbg = WBDyPairGene(sys.argv[1])
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
