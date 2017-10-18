#!/usr/bin/env python
# -*-coding:utf8-*-
"""
Coder:	max.zhang
Date:	2015-4-14
Desc:	turn partition of baseline-community to ncpair
        "node_id\tcom_id" ==> "node_str\tcom_id"
"""

import sys
import collections

word_dict = {}


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print 'Usage:', sys.argv[0], '<word_dict>'
        exit(1)
    with open(sys.argv[1]) as ins:
        for line in ins:
            wordid, word = line.split()
            word_dict[int(wordid)] = word
    for line in sys.stdin:
        wordid_str, comid_str = line.strip().split()
        print '%s\t%s' % (word_dict[int(wordid_str)], comid_str)
