#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@date:      2014-11-25
@author:    max.zhang
@brief:     calculate value (tf/df/tf-idf) of word-pair on Hadoop

'''
import os
import sys


class ExtractorMapper(object):
    def extract(self, ins=sys.stdin, outs=sys.stdout):
        raise NotImplementedError


class PairTFExtractorMapper(ExtractorMapper):
    def extract(self, ins=sys.stdin, outs=sys.stdout):
        for line in ins:
            word_list = line.strip().split()
            for word1 in word_list:
                if len(word1) <= 3:
                    continue
                for word2 in word_list:
                    if word1 <= word2 or len(word2) <= 3:
                        continue
                    outs.write("%s-%s 1\n" % (word1, word2))


class PairDFExtractorMapper(ExtractorMapper):
    def extract(self, ins=sys.stdin, outs=sys.stdout):
        for line in ins:
            word_set = set(line.strip().decode('utf8').split())
            for word1 in word_set:
                if len(word1) <= 1:
                    continue
                for word2 in word_set:
                    if word1 >= word2 or len(word2) <= 2:
                        continue
                    key = u'%s-%s' % (word1, word2)
                    outs.write(key.encode('utf8')+'\n')


if __name__ == "__main__":
    ext = PairDFExtractorMapper()
    ext.extract()

