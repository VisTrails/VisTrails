###############################################################################
##
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
import sys
import os

def run(py_dirname, in_dirname, out_dirname, filename='examples_list.txt'):
    f = open(filename)
    total = 0
    total_good = 0
    for line in f:
        # print line
        arr = line.rstrip().split(None, 2)
        total += 1
        if arr[1][0] == 'Y':
            total_good += 1

            vt_file = os.path.splitext(arr[0])[0] + '.vt'
            py_file = arr[0]

            vt_name = os.path.join(in_dirname, vt_file)
            out_vt_name = os.path.join(out_dirname, vt_file)
            py_name = os.path.join(py_dirname, py_file)
            
            py_name = os.path.join(os.path.dirname(py_name),
                                   "Python",
                                   os.path.basename(py_name))
            out_py_name = os.path.join(out_dirname, py_file)
            to_make_dirs = []
            a_dirname = os.path.dirname(out_vt_name)
            while not os.path.exists(a_dirname):
                to_make_dirs.append(a_dirname)
                a_dirname = os.path.dirname(a_dirname)
            for a_dirname in reversed(to_make_dirs):
                # print "os.mkdir('%s')" % a_dirname
                os.mkdir(a_dirname)
            
            # print "os.system('cp %s %s')" % (py_name, out_py_name)
            # print "os.system('cp %s %s')" % (vt_name, out_vt_name)
            os.system('cp %s %s' % (py_name, out_py_name))
            os.system('cp %s %s' % (vt_name, out_vt_name))
    print "%d of %d" % (total_good, total)

if __name__ == '__main__':
    if len(sys.argv) < 5:
        print "Usage: python %s " % sys.argv[0] + \
            "<python_dir> <in_dir> <out_dir> [examples_list]"
        sys.exit(-1)
    run(*sys.argv[1:])
