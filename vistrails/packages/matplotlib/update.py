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

from __future__ import division

import os
import shutil

from parse import run as run_parse
from diff import compute_diff, apply_diff
from generate import run as run_generate

_bases = ["artists", "plots"]

def backup():
    if not os.path.exists("backup"):
        os.mkdir("backup")
    backup_files = ["mpl_%s_raw.xml", "mpl_%s.xml", "mpl_%s_diff.xml"]
    for base in _bases:
        for fname_base in backup_files:
            fname = fname_base % base
            shutil.copy(fname, "backup")

def run(which="all"):
    backup()
    if which == "all":
        bases = _bases
    else:
        bases = [which]
    for base in bases:
        compute_diff("mpl_%s_raw.xml" % base, 
                     "mpl_%s.xml" % base, 
                     "mpl_%s_diff.xml" % base)
        run_parse(base)
        apply_diff("mpl_%s_raw.xml" % base,
                   "mpl_%s_diff.xml" % base,
                   "mpl_%s.xml" % base)
        run_generate(base)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == 'backup':
            backup()
        else:
            run(sys.argv[1])
    else:
        run()
