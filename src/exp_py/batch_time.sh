#!/bin/bash

if false; then
# Generate networks and communities by "baseline"
for idx in 1000 5000 10000; do 
# for idx in 1000; do 
	echo 'Network of size:' $idx
	src/exp_py/geneExpData.py $idx data/random_data/wnet_str.$idx
	cp data/random_data/wnet_str.$idx data/jc_data/$idx.wnet
	src/tools/comdet_baseline.sh data/jc_data/$idx.wnet
	cat data/jc_data/$idx.par| src/tools/par2ncpair.py data/jc_data/$idx.dict > data/random_data/nc_pair.$idx
done;

# Generate dynamics: time consuming
for idx in 1000 5000 10000; do 
# for idx in 1000; do 
	for dy_type in 'addNode' 'rmNode' 'upNode' 'downNode' 'addEdge' 'rmEdge' 'upEdge' 'downEdge'; do
		for dy_times in 10 30 50 100 1000; do
		# for dy_times in 10; do
			echo $idx $dy_type $dy_times
			src/exp_py/geneDyData.py $idx data/random_data/wnet_str.$idx $dy_type $dy_times data/random_data/"$dy_type"_"$dy_times".$idx
		done;
	done;
done;
fi


for dy_type in 'addNode' 'rmNode' 'upNode' 'downNode' 'addEdge' 'rmEdge' 'upEdge' 'downEdge'; do
	src/exp_py/expDyTime.py $dy_type
done;
