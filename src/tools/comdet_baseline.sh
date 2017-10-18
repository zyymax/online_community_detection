#!/bin/bash
# Use bursty_word(*.bw) and tokenid-transformed burstypair(*.s) to generate edge file and use algorithm in GEPHI to detect community

wnet_file=$1
prefix=`echo $wnet_file | sed 's/\.[^.]*$//g'`
# echo $prefix

bw_file="$prefix".bw
dict_file="$prefix".dict
bpair_file="$prefix".jc
edge_file="$prefix".edge
edgebin_file="$prefix".edgebin
weight_file="$prefix".weight
tree_file="$prefix".tree
event_file="$prefix".event
par_file="$prefix".par

# echo 'generating input edge file of gephi...'
cat $wnet_file | grep edge | awk '{print $2"\t"$3}' > $bpair_file
cat $bpair_file | cut -d $'\t' -f 1 | sed 's/-/\n/g' | awk '!a[$0]++{print $0}' > $bw_file
cat $bw_file | src/tools/build_dict.py > $dict_file
cat $bpair_file | src/tools/bpair2edge.py $dict_file  > $edge_file

# Detect Community depend on https://sites.google.com/site/findcommunities/
# echo 'detecting community...'
src/community/convert -i $edge_file -o $edgebin_file -w $weight_file
src/community/community $edgebin_file -l -1 -w $weight_file > $tree_file
levels=`src/community/hierarchy $tree_file | awk 'NR==1{print $NF}'`
src/community/hierarchy $tree_file -l $(($levels-1)) > $par_file
# src/community/hierarchy $tree_file -l $(($levels-1)) | src/gp2event.py $dict_file g > $event_file 
rm $edge_file
rm $edgebin_file
rm $weight_file
