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
import re
import subprocess
import sys


re_setup = re.compile(r'setup\(')
re_version = re.compile(r'(?<=\bversion=[\'"])([0-9a-zA-Z._+-]+)')


if __name__ == '__main__':
    # Get version from git describe
    version = subprocess.check_output(['git', 'describe',
                                       '--always', '--tags']).strip()

    setup_py = sys.argv[1]

    # Update setup.py file
    with open(setup_py, 'rb') as fp:
        lines = fp.readlines()

    i = 0
    setup_found = False
    version_replaced = False
    while i < len(lines):
        line = lines[i]
        if not setup_found and re_setup.search(line):
            setup_found = True
        if setup_found:
            m = re_version.search(line)
            if m is not None:
                lines[i] = re_version.sub(version, line)
                version_replaced = True
                break
        i += 1

    if not version_replaced:
        sys.stderr.write("Didn't find version number to replace\n")
        sys.exit(1)

    with open(setup_py, 'wb') as fp:
        for line in lines:
            fp.write(line)
