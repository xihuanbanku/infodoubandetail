#!/bin/bash

cd /home/hadoop/deploy/spider/infodoubandetail

html=`curl -L movie.douban.com`
error_msg="检测到有异常请求"
if [[ ${html} =~ ${error_msg} ]]
then
    echo `date`"[IP被限制]" >> nohup.out
    echo `date`"[停止爬虫]" >> nohup.out
    pkill -ef "douban_info"
    echo
    sleep 3
    echo `date`"[停止完成]" >> nohup.out
else
    echo `date`"[IP解除限制, 检查是否已经启动过爬虫...]"
    pid=`pgrep -f "douban_info"`
    sleep 3
    if [ ${pid} > 0 ]
    then
        echo `date`"[爬虫已经启动pid[${pid}], 直接退出...]"
    else
        echo `date`"[爬虫没有启动, starting...]"
        sh start.sh
        sleep 3
        echo `date`"[启动成功]" >> nohup.out
    fi

fi