#!/bin/bash

bw_file=$1
prefix=`echo $bw_file | sed 's/\.[^.]*$//g'`
echo $prefix
dict_file="$prefix".dict
jcnum_file="$prefix".jcnum
wnet_file="$prefix".wnet
awk 'BEGIN{print "Source\tTarget\tType\tId\tWeight"} {split($1, arr, "-"); print arr[1]"\t"arr[2]"\tUndirected\t"NR"\t"$2}' $jcnum_file > "$prefix"_edges.csv
src/generate_gephi_node.py $dict_file $wnet_file > "$prefix"_nodes.csv
# awk 'BEGIN{print "Nodes\tId\tLabel"} {print $2"\t"$1"\t"$2}' $dict_file  > "$prefix"_nodes.csv
# awk '{split($1, arr, "-"); print arr[1]"\t"arr[2]"\t"$2}' $jcnum_file > "$prefix"_com_edges.txt
