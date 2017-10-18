#!/bin/bash

DY_PREFIX=$1
MERGE_FNAME=$2
START_TIME=$3
STOP_TIME=$4

rm $MERGE_FNAME
for ts in `seq $START_TIME $STOP_TIME`; do
	echo "TIME:"$'\t'$ts >> $MERGE_FNAME
	cat "$DY_PREFIX"."$ts" >> $MERGE_FNAME
	echo '' >> $MERGE_FNAME
done;
