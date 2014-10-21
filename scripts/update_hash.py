#!/usr/bin/env python

import glob
import sys

if len(sys.argv)<3:
    print "Usage: ./update_hash.py old_hash new_hash"
    sys.exit(-1)

files = ["release_notes.py",
         "create_release_wiki_table.py",
         "../vistrails/core/system/__init__.py",
         "../dist/source/make-vistrails-src-release.py",
         "../doc/usersguide/conf.py"]

for path in files:
    for f in glob.glob(path):
        print "Updating", f
        file = open(f)
        text = file.read()
        file.close()
        
        text = text.replace(sys.argv[1], sys.argv[2])
        
        file = open(f, "w")
        file.write(text)
        file.close()

print "These files need to be updated manually:"
print "  ../dist/mac/Input/README"
print "  ../dist/windows/Input/releaseNotes.txt"
