# Finds all files matching extensions recursively in current directory (.)
# and updates tthe contact e-mail address

import re
import os

OLD_EMAIL = "vistrails@sci.utah.edu"
NEW_EMAIL = "contact@vistrails.org"
EXTENSIONS = [".py", ".xml", ".xsd", ".php", ".sql", ".sh", ".rst", ".tex"]
IGNORE_LIST = ["update_email_contact.py"]

files = []
for (path, dnames, fnames) in os.walk('.'):
    for fn in fnames:
        for ext in EXTENSIONS:
            if fn.endswith(ext) and fn not in IGNORE_LIST:
                files.append(os.path.join(path, fn))
                break

print len(files), " files will be processed."

count = 0
for fname in files:
    fin = open(fname)
    all_lines = fin.read()
    fin.close()
    pos = all_lines.find(OLD_EMAIL)
    if pos > -1:
        print "Updating: %s"%fname
        newlines = all_lines.replace(OLD_EMAIL, NEW_EMAIL)
        fout = file(fname, 'w')
        fout.write(newlines)
        fout.close()
        count += 1
print count, " files updated "
 