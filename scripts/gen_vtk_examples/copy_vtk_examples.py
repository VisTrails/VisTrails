############################################################################
##
## Copyright (C) 2006-2007 University of Utah. All rights reserved.
##
## This file is part of VisTrails.
##
## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of
## this file.  Please review the following to ensure GNU General Public
## Licensing requirements will be met:
## http://www.opensource.org/licenses/gpl-license.php
##
## If you are unsure which license is appropriate for your use (for
## instance, you are interested in developing a commercial derivative
## of VisTrails), please contact us at vistrails@sci.utah.edu.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################

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
