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
                    print >>out_file, 'sys.path.append' + \
                        '("/vistrails/src/trunk/scripts/gen_vtk_examples")'
                    print >>out_file, 'import vtk_imposter'
                    print >>out_file, 'from colors import *'
                    print >>out_file, 'vtk = vtk_imposter.vtk()'
                    print >>out_file, 'VTK_DATA_ROOT = ""'
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
    
