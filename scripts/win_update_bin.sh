#!/bin/bash
SRC_PATH="vistrails"
BIN_PATH="vistrails"

if [ -z "$1" ] || [ -z "$2" ]
then
    echo "usage: $0 <src_dir> <bin_dir>"
    exit 65
fi
curdir=`pwd`
cd "$1/$SRC_PATH"
ELEMENTS="*"
for elem in $ELEMENTS
do
    if [ -e "$2/$BIN_PATH/$elem" ]
    then
	rm -r "$2/$BIN_PATH/$elem"
    fi
    cp -r "$1/$SRC_PATH/$elem" "$2/$BIN_PATH/$elem"
done
cd "$curdir"

if [ -e "$2/$BIN_PATH/.svn" ]
then
    rm -r "$2/$BIN_PATH/.svn"
fi
cp -r "$1/$SRC_PATH/.svn" "$2/$BIN_PATH/.svn"
exit 0
