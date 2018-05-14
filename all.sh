#!/bin/bash

isDebug=0
if [ $isDebug -eq 1 ]; then
	filePath=/data0/web/loganalysis.258.com
else
	filePath=/data0/web/loganalysis.258.com
fi

if [ "$1" = "stop" ];then
	ps -ef |grep -v grep |grep monitorServer.py|cut -c 9-15|xargs kill -9
	ps -ef |grep -v grep |grep readServer.py|cut -c 9-15|xargs kill -9
	sleep  2
	i=$(ps -ef | grep monitorServer.py|grep -v grep|wc -l)
	if [ "$i" -lt 1 ];then
		echo -e "\033[32m monitorServer stop success \033[0m"
	else
		ps -ef |grep -v grep |grep monitorServer.py|cut -c 9-15|xargs kill -9
	fi
	i=$(ps -ef | grep readServer.py|grep -v grep|wc -l)
	if [ "$i" -lt 1 ];then
		echo -e "\033[32m readServer stop success \033[0m"
	else
		ps -ef |grep -v grep |grep readServer.py|cut -c 9-15|xargs kill -9
	fi
	exit 0
fi

if [ "$1" = "restart" ];then
	ps -ef |grep -v grep |grep readServer.py|cut -c 9-15|xargs kill -9
	ps -ef |grep -v grep |grep monitorServer.py|cut -c 9-15|xargs kill -9
fi

i=$(ps -ef | grep monitorServer.py|grep -v grep|wc -l)
if [ "$i" -lt 1 ];then
	/bin/cp -rf $filePath/Log/monit_server.file $filePath/Log/OldLog
	nohup python2.7 -u $filePath/monitorServer.py > $filePath/Log/monit_server.file 2>&1 &
	sleep  2
	j=$(ps -ef | grep monitorServer.py|grep -v grep|wc -l)
	if [ "$j" -lt 1 ];then
		echo -e "\033[31m monitorServer start error \033[0m"
	else
		echo -e "\033[32m monitorServer start success \033[0m"
	fi
fi
