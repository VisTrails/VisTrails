#!/bin/bash

if [ -z "$1" ]
then
    echo "usage: $0 <app_path>"
    exit 65
fi

APP_PATH=$1
shift
THIS_DIR=`dirname $0`
PYTHON_EXEC_PATH="Contents/MacOS/python"
RESOURCES_PATH="Contents/Resources"

if [ ! -e "$APP_PATH/$RESOURCES_PATH" ]
then
    echo "$APP_PATH/$RESOURCES_PATH does not exist"
    exit 66
fi

if [ ! -e "$APP_PATH/$PYTHON_EXEC_PATH" ]
then
    echo "$APP_PATH/$PYTHON_EXEC_PATH does not exist"
    exit 67
fi

PYTHONHOME="$APP_PATH/$RESOURCES_PATH" ${APP_PATH}/${PYTHON_EXEC_PATH} ${THIS_DIR}/runtestsuite.py $@
