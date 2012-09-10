#!/bin/bash

if [ -z "$1" ]
then
    echo "usage: $0 <app_path>"
    exit 65
fi

THIS_DIR=`dirname $0`
PYTHON_EXEC_PATH="Contents/MacOS/python"
RESOURCES_PATH="Contents/Resources"

if [ ! -e "$1/$RESOURCES_PATH" ]
then
    echo "$1/$RESOURCES_PATH does not exist"
    exit 66
fi

if [ ! -e "$1/$PYTHON_EXEC_PATH" ]
then
    echo "$1/$PYTHON_EXEC_PATH does not exist"
    exit 67
fi

PYTHONHOME="$1/$RESOURCES_PATH" ${1}/${PYTHON_EXEC_PATH} ${THIS_DIR}/runtestsuite.py
