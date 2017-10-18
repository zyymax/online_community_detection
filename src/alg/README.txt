[Algorithm]代码说明

[基础类文件]
node.py:
	描述网络中结点类的层次结构：
	BaseNode
		--ConNode 含有邻接点的结点类
			--DisjointNode 不相交社区网络中的结点类
				--DisjointWeightedNode 带权重的结点类
			--OverlapNode 重叠社区网络中的结点类

community.py:
	描述网络中社区类的层次结构：
	BaseCommunity 仅包含结点信息的社区基类
		--EdgeCommunity 含有边信息的社区类
			--WeightCommunity 含有边权重信息的社区类

network.py:
	描述网络结构的基类
	成员：
	--nodestr_dict: <node_str, node_idx>存储结点标签的词典
	--node_list: 结点对象列表
	--com_list: 社区对象列表
	方法：
	--addEdge(node1_str, node2_str, weight): 添加边
	--show(): 输出网络信息
	--clear(): 清空网络信息，初始化成员
	--toNetStr()/fromNetStr(fname): 以字符串的形式序列化/反序列化网络信息
	私有方法：
	--_hasNodeName(node_str): 判断结点标签是否存在
	--_getNodeIdx(node_str): 根据标签返回结点ID和对象，若不存在则创建新节点



[社区发现算法类文件]

[重叠社区检测算法]

afocs.py:
	实现了 MOBICOM'11 Overlapping communities in dynamic networks: their detection and mobile applications 中的AFOCS算法
	用于在复杂网络中发现重叠的社区结构
	[待完善]


[QCA类不相交社区检测算法]

代码文件包括：qca.py/qcaw.py/zyy_qcaw.py/qcaw_rec.py/nwqca.py
运行：src/alg/源代码.py <dy_file>
dy_file由src/exp_py/geneWB*.py，src/exp_py/merge_dy.py和src/exp_py/batch_merge_dy.py生成

dy_file的格式要求：
1.文件描述带点权边权网络的8种动态变化：添加结点、删除结点、添加边、删除边、增加点权、减小点权、增加边权和减小边权
2.每行以TIME/addNode/rmNode/addEdge/rmEdge/upNode/downNode/upEdge/downEdge开头，格式分别为：
	(1) TIME行表示时间戳，格式为："TIME:\t时间戳"
		例如：TIME:\t10
	(2) addNode行格式为："addNode\t结点标签\t结点权重\t邻接点标签-边权重,邻接点标签-边权重,..."
		例如：addNode\t电视\t26.000\t学员-0.108,声音-0.110,独家-0.132,家庭-0.119
	(3) rmNode行格式为: "rmNode\t结点标签"
		例如：rmNode\t目击者
	(4) addEdge行格式为："addEdge\t结点标签-结点标签\t边权重"
		例如：addEdge\t产品-预约\t0.371
	(5) rmEdge行格式为："rmEdge\t结点标签-结点标签"
		例如：rmEdge\t产品-预约
	(6) upNode行格式为："upNode\t结点标签\t结点权重"
		例如：upNode\t伤员\t11.000
	(7) downNode行格式为："downNode\t结点标签\t结点权重"
		例如：downNode\t伤员\t1.000
	(8) upEdge行格式为："upEdge\t结点标签-结点标签\t边权重"
		例如：upEdge\t遇难-阿姆斯特丹\t0.126
	(9) downEdge行格式为："downEdge\t结点标签-结点标签\t边权重"
		例如：downEdge\t全程-节目\t0.257

qca.py(QCAImp:Network):
	实现了 INFOCOM'11 Adaptive Algorithms for Detecting Community Structure in Dynamic Social Networks 中的QCA算法
	用于在带边权网络中发现不相交的社区结构

qcaw.py(QCAWImp:QCAImp):
	基本策略与qca.py相同，但适用于带点权边权的网络

zyy_qcaw.py(ZyyQCAWImp:QCAWImp):
	对qcaw.py做了大量调整，主要增加了up/down-Node/Edge这四种变化的调整策略

qcaw_rec.py(QCAWRecImp:QCAWImp):
	类似于zyy_qcaw.py，但每次调整完毕后都要对受影响的社区进行refine

nwqca.py(NWQCAImp:QCAWImp):
	根据作用力概念设计出的算法，详见《2015硕士论文-面向微博突发事件发现的自适应社区检测算法研究及系统实现》


代码示例：
	1.由微博分词结果生成多个时段的dy_file文件：
		cat data/0718_weibo.token | src/exp_py/geneWBDyBase.py data/weibo_data/0718/nl_base_5
	2.合并为一个完整的dy_file文件：
		src/exp_py/merge_dy.sh data/weibo_data/0718/nl_base_5 data/weibo_data/0718_nl_base_5.all 0 23
	3.运行QCA社区检测算法
		src/alg/qca.py data/weibo_data/0718_nl_base_5.all


