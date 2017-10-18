#!/usr/bin/env python
# -*-coding:utf8-*-
"""
Coder:	max.zhang
Date:	2014-12-15
Desc:	turn graph-partition file of metis to event result
"""

import sys
import collections

word_dict = {}


def gephi2event(ins):
    cluster_list = collections.defaultdict(list)
    for line in ins:
        wordid, eventid = line.strip().split()
        cluster_list[int(eventid)].append(word_dict[int(wordid)])
    for cid in sorted(cluster_list.keys()):
        print ','.join(cluster_list[cid])

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print 'Usage:', sys.argv[0], '<word_dict>'
        exit(1)
    with open(sys.argv[1]) as ins:
        for line in ins:
            # Line: wordid\tword
            wordid, word = line.split()
            word_dict[int(wordid)] = word
    gephi2event(sys.stdin)

