# Finds all .py files recursively in current directory (.)
# and updates 2007 year with 2008 in the file header. 
import re
import os
new_copyright = ["## Copyright (C) 2006-2010 University of Utah. All rights reserved.\n"]

re_copyright = re.compile(r"\s+## Copyright \(C\) 2006-2009 University of Utah\. All rights reserved\.\s+")

files = []
for (path, dnames, fnames) in os.walk('.'):
    for fn in fnames:
        if fn.endswith(".py"):
            files.append(os.path.join(path, fn))

print len(files), " files found"
count = 0
for fname in files:
    fin = open(fname)
    lines = fin.readlines()
    fin.seek(0)
    all_lines = fin.read()
    fin.close()
    if re_copyright.search(all_lines) > 0:
        newlines = lines[:2]
        newlines.extend(new_copyright)
        cropped = lines[3:]
        newlines.extend(cropped)
        fout = file(fname, 'w')
        fout.writelines(newlines)
        fout.close()
        count += 1
print count, " files updated"
