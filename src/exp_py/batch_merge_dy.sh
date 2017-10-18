#!/bin/bash


BUR_THRE=5
DY_FILE=data/weibo_data/0718/nl_base_$BUR_THRE
FNAME=data/weibo_data/0718_nl_base_$BUR_THRE.all
START_TIME=0
STOP_TIME=23
src/exp_py/merge_dy.sh $DY_FILE $FNAME $START_TIME $STOP_TIME


DY_FILE=data/weibo_data/0718/nl_pair_$BUR_THRE
FNAME=data/weibo_data/0718_nl_pair_$BUR_THRE.all
src/exp_py/merge_dy.sh $DY_FILE $FNAME $START_TIME $STOP_TIME

DY_FILE=data/weibo_data/0718/nl_sing_$BUR_THRE
FNAME=data/weibo_data/0718_nl_sing_$BUR_THRE.all
src/exp_py/merge_dy.sh $DY_FILE $FNAME $START_TIME $STOP_TIME

if false; then
DY_FILE=data/weibo_data/0301-0308/nolast_dy_sing_5
FNAME=data/weibo_data/0301-0308_nolast_dy_sing_5.all
START_TIME=1
STOP_TIME=8
src/exp_py/merge_dy.sh $DY_FILE $FNAME $START_TIME $STOP_TIME

DY_FILE=data/weibo_data/03/nolast_dy_sing_15
FNAME=data/weibo_data/03_nolast_dy_sing_15.all
START_TIME=1
STOP_TIME=31
src/exp_py/merge_dy.sh $DY_FILE $FNAME $START_TIME $STOP_TIME
fi;
