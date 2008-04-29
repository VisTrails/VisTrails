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

import os

def run(filename, in_dirname, py_dirname, out_dirname):
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
    import sys
    if len(sys.argv) <= 4:
        print "Usage: python %s " % sys.argv[0] + \
            "<examples_list> <in_dir> <python_dir> <out_dir>"
        sys.exit(-1)
    run(*sys.argv[1:])
