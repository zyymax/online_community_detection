#!/usr/bin/env python
"""
Coder:  max.zhang
Date:   2015-03-17
Desc:   experiments on upNodeWeight method
"""
import sys
import os
sys.path.append('/home/maxzhang/exp/OnlineCD_exp_0113/src/alg')
from qca import QCAImp
from qcaw import QCAWImp
from zyy_qcaw import ZyyQCAWImp
from qcaw_rec import QCAWRecImp
from nwqca import NWQCAImp


def main():
    assert len(sys.argv) == 2, 'Usage:\t%s <test_type>' % sys.argv[0]
    test_type = sys.argv[1]
    assert test_type in ['upNode', 'downNode']
    qca_com = QCAImp()
    qcaw_com = QCAWImp()
    zqcaw_com = ZyyQCAWImp()
    rqcaw_com = QCAWRecImp()
    nwqca_com = NWQCAImp()
    print("[EXP on %s]" % test_type)
    head_list = []
    dycount_list = []
    qcaw_list = []
    rqcaw_list = []
    zqcaw_list = []
    nwqca_list = []
    for idx in range(1, 11):
        head_list.append('[%s-%s]' % (idx, idx+1))
        qcaw_com.fromNetStr('data/net_data/%s.qcaw' % idx)
        rqcaw_com.fromNetStr('data/net_data/%s.qcaw' % idx)
        zqcaw_com.fromNetStr('data/net_data/%s.qcaw' % idx)
        nwqca_com.fromNetStr('data/net_data/%s.qcaw' % idx)
        qcaw_com.fromComStruc('data/ncpair_data/%s.baseline' % idx)
        rqcaw_com.fromComStruc('data/ncpair_data/%s.baseline' % idx)
        zqcaw_com.fromComStruc('data/ncpair_data/%s.baseline' % idx)
        nwqca_com.fromComStruc('data/ncpair_data/%s.baseline' % idx)
        dy_count = 0
        with open('data/dy_data/%s.dy' % (idx+1)) as ins:
            for line in ins:
                if not line.startswith(test_type):
                    continue
                dy_count += 1
                node_str, node_w = line.strip().split()[1:]
                if qcaw_com._hasNodeName(node_str):
                    qcaw_com._setOldNodeWeight(node_str, float(node_w))
                    rqcaw_com.setNodeWeight(node_str, float(node_w))
                    zqcaw_com.setNodeWeight(node_str, float(node_w))
                    nwqca_com.setNodeWeight(node_str, float(node_w))
                else:
                    qcaw_com.addNode(node_str, float(node_w), {})
                    rqcaw_com.addNode(node_str, float(node_w), {})
                    zqcaw_com.addNode(node_str, float(node_w), {})
                    nwqca_com.addNode(node_str, float(node_w), {})
        qcaw_com.checkCom()
        rqcaw_com.checkCom()
        zqcaw_com.checkCom()
        nwqca_com.checkCom()
        open('data/net_data/%s.%s' % (idx, test_type), 'w').write(qcaw_com.toNetStr())
        dycount_list.append('%d' % dy_count)
        qcaw_list.append('%.4f' % qcaw_com._modularity())
        rqcaw_list.append('%.4f' % rqcaw_com._modularity())
        zqcaw_list.append('%.4f' % zqcaw_com._modularity())
        nwqca_list.append('%.4f' % nwqca_com._modularity())
    print('\t%s' % '\t'.join(head_list))
    print('%s\t%s' % (test_type, '\t'.join(dycount_list)))
    print('QCAW\t%s' % '\t'.join(qcaw_list))
    print('QCAWRec\t%s' % '\t'.join(rqcaw_list))
    print('ZyyQCAW\t%s' % '\t'.join(zqcaw_list))
    print('NWQCA\t%s' % '\t'.join(nwqca_list))

if __name__ == "__main__":
    main()
