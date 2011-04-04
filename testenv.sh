#!/usr/bin/env sh

echo "Using " $1 " environment"

# cleanup
unset NUKE_PATH
unset PYTHONPATH
unset MAYA_MODULE_PATH

# common python
export PYTHONPATH=`pwd`/lib

# maya's ui
if [ "${1}" = "maya" ]; then
	#export MAYA_MODULE_PATH=`pwd`/ui/maya
	#echo $MAYA_MODULE_PATH
	echo $PYTHONPATH
fi

# nuke's ui
if [ "${1}" = "nuke" ]; then
	#export NUKE_PATH=`pwd`/ui/nuke/tractorUI
	#export PYTHONPATH=`pwd`/ui/nuke/tractorUI/python:$PYTHONPATH
	echo $NUKE_PATH
	echo $PYTHONPATH
fi

# working at home proxy
if [ `hostname` = 'Lancelot' ]; then
	export http_proxy=http://127.0.0.1:8081 
fi