#!/bin/sh

file_list=$1
shift

for i in `cat $file_list`; do
    DIR=`dirname $i`
    VT_FILE=$DIR/`basename $i .vt`_fixed.vt
    echo $i
    echo -- UNZIPPING
    unzip $i
    echo -- PRETTY PRINTING
    xmlpp.pl vistrail > vistrail_pp
    echo -- FIXING
    ../fix_file.py vistrail_pp $* > vistrail
    echo -- ZIPPING
    zip fixed_vistrail.zip vistrail
    echo -- MOVING
    mv fixed_vistrail.zip $VT_FILE
    echo -- CLEANING
    rm vistrail
    rm vistrail_pp
    echo $i
done
