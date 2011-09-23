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
import re
from convert_to_vt import ConvertVTKToVT

def run(in_dir, out_dir):
    def collectFilenames(dir):
        # create the regular expression matcher machines
        fileNameParser = re.compile('.*\.py')

        result = []
        for file in os.listdir(dir):
            # print childDirOrFile
            childDirOrFile = os.path.join(dir,file)
            if os.path.isfile(childDirOrFile):
                # file does match?
                if fileNameParser.match(childDirOrFile):
                    result.append(childDirOrFile)
            elif os.path.isdir(childDirOrFile):
                result += collectFilenames(childDirOrFile)
        return result
    
    all_files = collectFilenames(in_dir)
    in_base = os.path.basename(in_dir)
    for fname in all_files:
        path_before = os.path.dirname(fname)
        path_end = ''
        while os.path.basename(path_before) != in_base:
            if os.path.basename(path_before) != 'Python':
                if path_end == '':
                    path_end = os.path.basename(path_before)
                else:
                    path_end = os.path.join(os.path.basename(path_before), 
                                            path_end)
            path_before = os.path.dirname(path_before)
        out_dirname = os.path.join(out_dir, path_end)

        to_make_dirs = []
        a_dirname = out_dirname
        while not os.path.exists(a_dirname):
            to_make_dirs.append(a_dirname)
            a_dirname = os.path.dirname(a_dirname)
        # print >>sys.stderr, 'to_make_dirs:', to_make_dirs
        for a_dirname in reversed(to_make_dirs):
            # print >>sys.stderr, 'making dir', a_dirname
            os.mkdir(a_dirname)

        script_name = os.path.basename(fname)
        vt_name = os.path.splitext(script_name)[0] + '.vt'
        out_py_name = os.path.join(out_dirname, script_name)
        out_vt_name = os.path.join(out_dirname, vt_name)

        converter = ConvertVTKToVT(fname, out_py_name)
        converter.run()

        print >>sys.stderr, "running 'python %s %s'..." % (out_py_name,
                                                           out_vt_name)
        os.system('python %s %s' % (out_py_name, out_vt_name))

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print 'Usage: %s <in_directory> <out_directory>' % sys.argv[0]
        sys.exit(-1)
    run(*sys.argv[1:])
