#!/bin/bash

for B in 5 15; do
	for D in 5 15; do
		for J in 01 001; do
			fname=data/weibo_data/0718/dy_sing_B"$B"_D"$D"_J"$J"
			echo $fname
			for dy_type in 'addNode' 'rmNode' 'addEdge' 'rmEdge' 'upNode' 'downNode' 'upEdge' 'downEdge'; do
				for idx in `seq 0 23`; do
					echo -n `grep $dy_type $fname.$idx | wc -l`
					echo -n ' '
				done
				echo ''
			done
		done
	done
done
