#!/bin/bash
###############################################################################
##
## Copyright (C) 2011-2012, NYU-Poly.
## Copyright (C) 2006-2011, University of Utah. 
## All rights reserved.
## Contact: contact@vistrails.org
##
## This file is part of VisTrails.
##
## "Redistribution and use in source and binary forms, with or without 
## modification, are permitted provided that the following conditions are met:
##
##  - Redistributions of source code must retain the above copyright notice, 
##    this list of conditions and the following disclaimer.
##  - Redistributions in binary form must reproduce the above copyright 
##    notice, this list of conditions and the following disclaimer in the 
##    documentation and/or other materials provided with the distribution.
##  - Neither the name of the University of Utah nor the names of its 
##    contributors may be used to endorse or promote products derived from 
##    this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
## AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
## THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR 
## PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR 
## CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; 
## OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
## WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR 
## OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF 
## ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
###############################################################################
ROOT_DIR_NAME="vistrails"
BIN_PATH_25="Contents/Resources/lib/python2.5"
BIN_PATH_26="Contents/Resources/lib/python2.6"
BIN_PATH_27="Contents/Resources/lib/python2.7"
OLD_DIRS="api core db gui packages tests"

if [ -z "$1" ] || [ -z "$2" ]
then
    echo "usage: $0 <src_dir> <bin_dir>"
    exit 65
fi

if [ -e "$2/$BIN_PATH_27" ]
then
    BIN_PATH=$BIN_PATH_27
elif [ -e "$2/$BIN_PATH_26" ]
then
    BIN_PATH=$BIN_PATH_26
elif [ -e "$2/$BIN_PATH_25" ]
then
    BIN_PATH=$BIN_PATH_25
fi

# remove the old lower-level symlinks if they exist
for dir in $OLD_DIRS
do
    if [ -e "$2/$BIN_PATH/$dir" ]
    then
        rm -r $2/$BIN_PATH/$dir
    fi
done

if [ -e "$2/$BIN_PATH/$ROOT_DIR_NAME" ]
then
    rm -r $2/$BIN_PATH/$ROOT_DIR_NAME
fi
ln -s -f -F $1/$ROOT_DIR_NAME $2/$BIN_PATH/$ROOT_DIR_NAME

if [ -e "$2/$BIN_PATH/../../vistrails.py" ]
then
    rm $2/$BIN_PATH/../../vistrails.py
fi
ln -s -f -F $1/$ROOT_DIR_NAME/vistrails.py $2/$BIN_PATH/../../vistrails.py

exit 0
