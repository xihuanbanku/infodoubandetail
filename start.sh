#!/bin/bash

source /etc/profile
cd /home/hadoop/deploy/spider/infodoubandetail/
date >> nohup.out
today=`date -d "a day ago" +%Y-%m-%d`
echo $today" 获取豆瓣可播放连接开始..." >> nohup.out

nohup python douban_info/run.py &