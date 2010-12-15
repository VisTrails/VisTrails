#!/bin/bash
THIS_DIR=`dirname $0`
# WATCH OUT!
# You have to change BASE_DIR so that it points to the bundle you're currently using.
BASE_DIR="${THIS_DIR}/../../../VisTrails Trunk Bundle/Vistrails Trunk.app/Contents"
LIB_DIR=${BASE_DIR}/Resources/lib/python2.6
DYLD_LIBRARY_PATH= PYTHONPATH=$PYTHONPATH:${LIB_DIR}:${LIB_DIR}/lib-dynload "${BASE_DIR}/MacOS/python" ${THIS_DIR}/runtestsuite.py
