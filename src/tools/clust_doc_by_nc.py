#!/usr/bin/env python
# -*-coding:utf8-*-
"""
Coder:	max.zhang
Date:	2015-4-28
Desc:	cluster document by node-community pair file
"""


import sys
import os
import collections

FILTER_WORDCOUNT = 5
FILTER_EVENTTHRE = 0.5
EVENT_THRE = 2


assert len(sys.argv) == 4, 'Usage:\t%s <nc_file> <token_file> <content_file>' % sys.argv[0]
node_comid_dict = {}
nc_file, token_file, content_file = sys.argv[1:]
with open(nc_file) as ins:
    for lineid, line in enumerate(ins):
        node_str, comid = line.strip().decode('utf8').split()
        node_comid_dict[node_str] = int(comid)
token_list = open(token_file)
content_list = open(content_file).readlines()
for lineid, line in enumerate(token_list):
    eventid_list = [0]*(max(node_comid_dict.values())+1)
    eventword_count = 0
    eventword_dict = {}
    for word in set(line.strip().decode('utf8').split()):
        try:
            eventid_list[node_comid_dict[word]] += 1
            eventword_count += 1
            eventword_dict[word] = node_comid_dict[word]
        except KeyError:
            pass
    if eventword_count == 0 or len(line.strip().split()) < FILTER_WORDCOUNT:
        print 'Filtered by FILTER_WORDCOUNT', line,
    else:
        eventid = 0
        max_value = 0
        for idx, value in enumerate(eventid_list):
            if value > max_value:
                max_value = value
                eventid = idx
        event_count = sum([1 if value else 0 for value in eventid_list])
        if max_value*1.0/eventword_count < FILTER_EVENTTHRE:
            print 'Filtered by FILTER_EVENTTHRE', line,
        else:
            print '%s\tEvent\t%s' % (eventid, content_list[lineid])
        # print max_value*1.0/eventword_count, eventid_list, line.strip()
