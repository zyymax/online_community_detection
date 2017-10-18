#!/bin/bash

if false; then
for idx in `seq 1 31`;do
	# echo $idx
	if [ $idx -ge 10 ]
	then
		:
		# cat data/0718_link/0718_edge.wlink."$idx" >> 0718.wlink
		# cat data/0718_link/0718_edge.link."$idx" >> 0718.link
		# src/qca.py data/0718_link/0718_edge.link."$idx" > data/0718_com/qca.txt."$idx"
		# cat  ~/exp/eventgp_exp_1215/data/token/0718/"$idx"_short.token | awk '{print '$idx'"\t"$0}' >> data/0718_weibo.token
		cat  /mnt/storage/zyy/token/03/2014-03-"$idx"_short.token | awk '{print '$idx'"\t"$0}' >> data/03_weibo.token
	else
		:
		# cat data/0718_link/0718_edge.wlink."$idx" >> 0718.wlink
		# cat data/0718_link/0718_edge.link."$idx" >> 0718.link
		# src/qca.py data/0718_link/0718_edge.link."$idx" > data/0718_com/qca.txt."$idx"
		# cat  ~/exp/eventgp_exp_1215/data/token/0718/0"$idx"_short.token | awk '{print '$idx'"\t"$0}' >> data/0718_weibo.token
		cat  /mnt/storage/zyy/token/03/2014-03-0"$idx"_short.token | awk '{print '$idx'"\t"$0}' >> data/03_weibo.token
	fi
done


	:
# Generate network and communities by "baseline"
# for idx in 1000 5000 10000; do 
for idx in 100; do 
	echo 'Network of size:' $idx
	src/exp_py/geneExpData.py $idx data/random_data/wnet_str.$idx
	cp data/random_data/wnet_str.$idx data/jc_data/$idx.wnet
	src/tools/comdet_baseline.sh data/jc_data/$idx.wnet
	cat data/jc_data/$idx.par| src/tools/par2ncpair.py data/jc_data/$idx.dict > data/random_data/nc_pair.$idx
done;

fi

# Generate dynamics and experiment on them
DY_TIMES=30
for test_type in 'addNode' 'rmNode' 'upNode' 'downNode' 'addEdge' 'rmEdge' 'upEdge' 'downEdge'; do
# for test_type in 'rmEdge' 'upEdge' 'downEdge'; do
# for test_type in 'addNode'; do
	# for idx in 1000; do 
	for idx in 1000 5000 10000; do 
		# src/exp_py/geneDyData.py $idx data/random_data/wnet_str.$idx $test_type $DY_TIMES data/random_data/"$test_type"_$DY_TIMES.$idx
		src/exp_py/expDy.py $test_type $idx $DY_TIMES
	done;
done;

