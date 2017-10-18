#!/usr/bin/env python
# -*-coding:utf8-*-
"""
Coder:	max.zhang
Date:	2014-11-20
Desc:	build word dict by words from stdin
"""


import sys
import os
import collections

word_dict = {}
for line in sys.stdin:
    for word in line.strip().split():
        word_dict.setdefault(word, len(word_dict))
for word, word_id in word_dict.items():
    print '%s\t%s' % (word_id, word)
