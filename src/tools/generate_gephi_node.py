#!/usr/bin/env python
import sys


def main():
    assert len(sys.argv) == 3, "Usage: %s <dict_file> <wnet_file>" % sys.argv[0]
    dict_file, wnet_file = sys.argv[1:]
    word_dict = {}
    with open(dict_file) as ins:
        for line in ins:
            wordid, word = line.strip().split()
            word_dict[word] = wordid
    print 'Nodes\tId\tLabel'
    with open(wnet_file) as ins:
        for line in ins:
            if not line.startswith('node'):
                continue
            word, weight = line.strip().split()[1:]
            print '%s\t%s\t%s' % (word, word_dict[word], weight)

if __name__ == "__main__":
    main()
