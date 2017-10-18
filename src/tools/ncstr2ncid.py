#!/usr/bin/env python
# -*-coding:utf8-*-
"""
Coder:	max.zhang
Date:	2015-4-14
Desc:	"node_str\tcom_id" ==> "node_id\tcom_id"
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
            word_dict[word] = wordid
    for line in sys.stdin:
        word_str, comid_str = line.strip().split()
        print '%s\t%s' % (word_dict[word_str], comid_str)
