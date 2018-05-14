#!/bin/bash

isDebug=0
if [ $isDebug -eq 1 ]; then
	filePath=/data0/web/loganalysis.258.com
else
	filePath=/data0/web/loganalysis.258.com
fi

if [ "$1" = "restart" ];then
	ps -ef |grep -v grep |grep readServer.py|cut -c 9-15|xargs kill -9
fi
i=$(ps -ef | grep readServer.py|grep -v grep|wc -l)
if [ "$i" -lt 1 ];then
	/bin/cp -rf $filePath/Log/read_server.file $filePath/Log/OldLog
	nohup python2.7 -u $filePath/readServer.py > $filePath/Log/read_server.file 2>&1 &
	sleep  0.1
	j=$(ps -ef | grep readServer.py|grep -v grep|wc -l)
	if [ "$j" -lt 1 ];then
		echo -e "\033[31m readServer start error \033[0m"
	else
		echo -e "\033[32m readServer start success \033[0m"
	fi
fi
if [ "$1" = "stop" ];then
	ps -ef |grep -v grep |grep readServer.py|cut -c 9-15|xargs kill -9
	i=$(ps -ef | grep readServer.py|grep -v grep|wc -l)
	if [ "$i" -lt 1 ];then
		echo -e "\033[32m readServer stop success \033[0m"
	else
		ps -ef |grep -v grep |grep readServer.py|cut -c 9-15|xargs kill -9
	fi
	exit 0
fi
