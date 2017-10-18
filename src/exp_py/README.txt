[Experiment]代码说明


[数据生成脚本]

geneExpData.py:
	生成随机的带点权边权网络
	为保证生成的随机网络具有社区结构，每个结点至少归属于一个随机团
	运行：src/exp_py/geneExpData.py <size> <wnet_file>
	其中：
		size为网络大小
		wnet_file为待写入的网络文件

geneDyData.py:
	在geneExpData.py生成的随机网络基础上，随机生成8种网络变化
	运行：src/exp_py/geneDyData.py <size> <wnet_file> <dy_type> <times> <dy_file>
	其中：
		size为网络大小
		wnet_file为geneExpData.py生成的随机网络
		dy_type为8种动态变化[addNode/rmNode/addEdge/rmEdge/upNode/downNode/upEdge/downEdge]之一
		times为需生成的变化次数
		dy_file为待写入的动态变化文件

geneWBDyBase.py
	突发性估计+动态词图构建
	采用指数平滑估计模型来估计二元词对的突发程度
	以拆分后的单个词作为网络结点，生成该时段的网络变化
	运行：cat <weibo_token> | src/exp_py/geneWBDyBySing.py <dy_prefix>
	其中：
		weibo_token为微博的中文分词结果，每行代表一条微博，格式为"时间戳\t空格分割的单词列表"
			例如：10\t中文 单词 列表
		dy_prefix为输出文件的前缀，最终生成的文件为dy_prefix.时间戳

geneWBDyBySing.py
	基于geneWBDyBase.py，但以单个词为突发特征单元和网络结点

geneWBDyByPair.py
	基于geneWBDyBase.py，但以二元词对为突发特征单元和网络结点

merge_dy.sh
	将分散的dy_prefix.时间戳文件合并成一个完整的dy_file文件
	运行：
		src/exp_py/merge_dy.sh <dy_prefix> <merge_fname> <start_time> <stop_time>
	其中：
		dy_prefix为公有的文件名前缀
		merge_fname为合并后的完整文件
		start_time为开始时间戳
		stop_time为终止时间戳

batch_merge_dy.sh
	批调用merge_dy.sh


[实验代码]

expOnNode.py:
	测试qca/qcaw/zyy_qcaw/qcaw_rec/nwqca等算法对upNode/downNode变化的自适应能力
expOnEdge.py:
	测试qca/qcaw/zyy_qcaw/qcaw_rec/nwqca等算法对upEdge/downEdge变化的自适应能力
expDy.py:
	测试baseline/qcaw/zyy_qcaw/qcaw_rec/nwqca等算法对8种变化的自适应能力
	其中baseline算法来自https://sites.google.com/site/findcommunities/，源代码在src/community目录中
expDyTime.py:
	测试qcaw/zyy_qcaw/qcaw_rec/nwqca等算法对8种变化的自适应效率


[实验批处理脚本]
batch_dy.sh:
	测试不同算法在8种网络变化下的自适应能力
batch_para.sh:
	测试实验参数构建出的网络结构的影响
batch_time.sh:
	测试不同算法在8种网络变化下的自适应效率

