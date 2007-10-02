#!/bin/bash

mkdir $2
zipfile=`basename $1 .vt`.zip
cp $1 $2/$zipfile
pushd $2
unzip $zipfile
xmlpp.pl vistrail >vistrail_pp
popd
