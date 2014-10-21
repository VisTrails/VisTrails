#!/bin/sh
###############################################################################
##
## Copyright (C) 2011-2014, NYU-Poly.
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
rm -rf debian
mkdir -p debian/usr/local/bin
mkdir -p debian/usr/local/vistrails
mkdir -p debian/usr/share/vistrails/examples/data
mkdir -p debian/DEBIAN
cp _debian/* debian/DEBIAN

(cat <<EOF
#!/bin/sh
python /usr/local/vistrails/run.py -l
EOF
) >> debian/usr/local/bin/vistrails

chmod 755 debian/usr/local/bin/vistrails

cp -R ../../vistrails debian/usr/local
find debian/usr/local/vistrails -name '.svn' -exec rm -rf {} \; 2>/dev/null
find debian/usr/local/vistrails -name '*~' -exec rm {} \; 2>/dev/null
find debian/usr/local/vistrails -name '*.pyc' -exec rm {} \; 2>/dev/null

cp ../../examples/*.xml debian/usr/share/vistrails/examples
cp ../../examples/data/carotid.vtk debian/usr/share/vistrails/examples/data
cp ../../examples/data/gktbhFA.vtk debian/usr/share/vistrails/examples/data
cp ../../examples/data/gktbhL123.vtk debian/usr/share/vistrails/examples/data
cp ../../examples/data/head.120.vtk debian/usr/share/vistrails/examples/data
cp ../../examples/data/mummy.128.vtk debian/usr/share/vistrails/examples/data
cp ../../examples/data/spx.vtk debian/usr/share/vistrails/examples/data
cp ../../examples/data/torus.vtk debian/usr/share/vistrails/examples/data
cp ../../examples/data/vslice_circ1.bp debian/usr/share/vistrails/examples/data

dpkg-deb --build debian
mv debian.deb vistrails.deb
rm -rf debian
