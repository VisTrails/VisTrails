#!/bin/sh
rm -rf debian
mkdir -p debian/usr/local/bin
mkdir -p debian/usr/local/vistrails
mkdir -p debian/DEBIAN
cp _debian/* debian/DEBIAN

(cat <<EOF
#!/bin/sh
python /usr/local/vistrails/vistrails.py -l
EOF
) >> debian/usr/local/bin/vistrails

chmod 755 debian/usr/local/bin/vistrails

cp -R ../vistrails debian/usr/local
find debian/usr/local/vistrails -name '.svn' -exec rm -rf {} \; 2>/dev/null
find debian/usr/local/vistrails -name '*~' -exec rm {} \; 2>/dev/null
find debian/usr/local/vistrails -name '*.pyc' -exec rm {} \; 2>/dev/null

dpkg-deb --build debian
mv debian.deb vistrails.deb
rm -rf debian
