#!/usr/bin/env python
# -*-coding:utf8-*-
"""
Coder:	max.zhang
Date:	2014-12-26
Desc:	build bursty pair edge file (gephi input format) with *.predict(.s/.b)
"""

import sys

if len(sys.argv) < 2:
    print 'Usage:', sys.argv[0], 'word_dict'
    exit(1)

word_dict = {}
with open(sys.argv[1]) as ins:
    for line in ins:
        wordid, word = line.strip().split()
        word_dict[word] = int(wordid)

for line in sys.stdin:
    word_pair, bursty = line.strip().split('\t')
    word1, word2 = word_pair.split('-')
    try:
        print '%s\t%s\t%s' % (word_dict[word1.strip()], word_dict[word2.strip()], bursty)
    except KeyError, e:
        continue
