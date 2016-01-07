#!/usr/bin/env python
###############################################################################
##
## Copyright (C) 2014-2016, New York University.
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
##  - Neither the name of the New York University nor the names of its
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

"""Finds all .py files recursively in current directory (.) and updates 2007
year with 2008 in the file header.
"""

from itertools import izip
import os
import re


# The new copyright: the found copyright line will be replaced by this
NEW_COPYRIGHT = ["## Copyright (C) 2014-2016, New York University.\n"]

# The old copyright line: the first matching line in a file will be replaced
# by NEW_COPYRIGHT
RE_COPYRIGHT = re.compile(r"\s*## Copyright \(C\) 20\d\d-20\d\d, "
                          r"New York University\.\s*")

# Number of lines in which to search for the old copyright
NB_SEARCHED_LINES = 5

# List of file names to ignore
IGNORE_LIST = ["update_copyright_year.py"]

files = []
for (path, dnames, fnames) in os.walk('.'):
    for fn in fnames:
        if fn not in IGNORE_LIST and fn.endswith(".py"):
            files.append(os.path.join(path, fn))

# Go through files and update them
print "%d files found" % len(files)
count = 0
for fname in files:
    fp = open(fname, 'rb')
    try:
        # Search only in the first few lines
        for line_num, line in izip(xrange(NB_SEARCHED_LINES), fp):
            if RE_COPYRIGHT.search(line):
                print "Updating %s" % fname
                fp.seek(0)
                lines = fp.readlines()
                fp.close()
                lines[line_num:line_num + 1] = NEW_COPYRIGHT
                fp = file(fname, 'wb')
                fp.writelines(lines)
                count += 1
                break
    finally:
        fp.close()
print "%d files updated" % count
