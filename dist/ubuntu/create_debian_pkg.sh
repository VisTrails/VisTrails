#!/bin/sh
rm -rf debian
mkdir -p debian/usr/local/bin
mkdir -p debian/usr/local/vistrails
mkdir -p debian/usr/share/vistrails/examples/data
mkdir -p debian/DEBIAN
cp _debian/* debian/DEBIAN

(cat <<EOF
#!/bin/sh
python /usr/local/vistrails/vistrails.py -l
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
