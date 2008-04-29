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

class ConvertVTKToVT(object):
    def __init__(self, in_filename, out_py_file):
        self.in_filename = in_filename
        self.out_py_file = out_py_file
        
        
    def run(self):
        in_file = file(self.in_filename)
        out_file = file(self.out_py_file, 'w')

        does_continue = False
        line_count = 0
        found_starter = False
        for line in in_file:
            if line_count == 0:
                if line.startswith('#!'):
                    found_starter = True
                else:
                    print >> out_file, \
                        "# This file produced automatically by convert_to_vt.py\n# "
            elif line_count == 1 and found_starter:
                print >> out_file, \
                    "# This file produced automatically by convert_to_vt.py\n# "
                found_starter = False
                
            if (line.find('import ') != -1 and line.find('vtk') != -1) or \
                    line.find('VTK_DATA_ROOT = ') != -1 or \
                    does_continue:
                if line.rstrip() == 'import vtk':
                    print >>out_file, 'import sys'
                    print >>out_file, \
                        'sys.path.append("/vistrails/vtk_examples")'
                    print >>out_file, 'import vtk_imposter'
                    print >>out_file, 'from colors import *'
                    print >>out_file, 'vtk = vtk_imposter.vtk()'
                    print >>out_file, 'VTK_DATA_ROOT = "/scratch/vtkdata-5.0.4"'
                    print >>out_file, ''
                    print >>out_file, '#', line[:-1]
                else:
                    if line.rstrip()[-1] == '\\':
                        does_continue = True
                    else:
                        does_continue = False
                    print >>out_file, '#', line[:-1]
            else:
                out_file.write(line)
            line_count += 1
        print >>out_file, '\nif len(sys.argv) > 1:'
        print >>out_file, '    out_filename = sys.argv[1]'
        print >>out_file, 'else:'
        print >>out_file, '    out_filename = None'
        print >>out_file, 'vtk.to_vt(out_filename)'
        out_file.close()
            

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print 'Usage: %s <in_file> <out_py_file>' % sys.argv[0]
        sys.exit(0)
    converter = ConvertVTKToVT(*sys.argv[1:])
    converter.run()
    
