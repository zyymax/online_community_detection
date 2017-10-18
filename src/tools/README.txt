[Tools]代码说明

[基于词典的数据格式转换脚本]

bpair2edge.py:
	文本格式转换，由"单词1-单词2\t突发程度" ==> "单词id1\t单词id2\t突发程度"
	运行：
		cat bursty.s | src/tools/bpair2edge.py <word_dict>
	其中，word_dict由build_dict.py生成

ncstr2ncid.py:
	根据词典文件将nc_file转换为ncid_file，即由"node_str\tcom_id" ==> "node_id\tcom_id"
	运行：
		cat nc_file | src/tools/ncstr2ncid.py <dict_file>

ncid2ncstr.py:
	根据词典文件将ncid_file转换为nc_file，即由"node_id\tcom_id" ==> "node_str\tcom_id"
	运行：
		cat ncid_file | src/tools/ncid2ncstr.py <dict_file>

gp2event.py:
	根据社区检测结果和单词词典生成事件信息
	运行：
		cat ncid_file | src/tools/gp2event.py <word_dict>
	要求：
		ncid_file格式为"node_id\tcommunity_id"，由nodeid2str.py生成
		word_dict格式为"node_id\tnode_str"


[数据生成脚本]

build_dict.py:
	根据分词结果生成词典
	运行：
		cat weibo.token | src/tools/build_dict.py > word_dict

PairValueMapper.py:
	原本用在Hadoop下统计二元词对的TF值，此处仅用于生成一条微博分词结果中的所有二元词对组合
	运行：
		cat weibo.token | src/tools/PairValueMapper.py

clust_doc_by_nc.py:
	根据词图网络的社区检测结果（ncpair文件）生成文档的聚类结果
	运行：
		src/tools/clust_doc_by_nc.py <nc_file> <token_file> <content_file>
	其中：
		nc_file为社区检测结果，每行的格式为"node_str\tcommunity_id"
		token_file为分词结果，每行代表一条微博
		content_file为微博原文，每行代表一条微博，且与token_file中微博的顺序一致


[调用第三方库的脚本]

comdet_baseline.sh:
	采用https://sites.google.com/site/findcommunities/算法进行社区检测
	运行：
		src/tools/comdet_baseline.sh <wnet_file>
	其中：
		wnet_file为src/exp_py/geneExpData.py生成的随机网络
	必需文件：
		src/community/: 该社区检测算法的源码目录
		./build_dict.py, ./bpair2edge.py


[生成可视化工具输入文件的脚本]

generate_gephi_input.sh:
	生成gephi可视化工具所需的结点和边CSV文件
	运行：
		src/tools/generate_gephi_input.sh <bw_file>
	其中：
		bw_file由comdet_baseline.sh生成
	必需文件：
		dict_file, jcnum_file和wnet_file，文件名要求详见此脚本

generate_gephi_node.py:
	生成gephi可视化工具所需的结点CSV文件
	运行：
		src/tools/generate_gephi_node.py <dict_file> <wnet_file>


stream_event_detect.py:
	无用

