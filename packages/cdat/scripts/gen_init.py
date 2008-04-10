############################################################################
##
## Copyright (C) 2006-2008 University of Utah. All rights reserved.
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

import os, sys
sys.path.append('../../../vistrails')
from parse_cdat_xml_file import parse_cdat_xml_file



#cdat package identifiers
cp_version = '0.1'
cp_identifier = 'edu.utah.sci.vistrails.cdat'
cp_name = 'CDAT'

def write_init(output_file, classes_lines, init_lines):
    """write_init(output_file: str, classes_lines: list, init_lines: list)
                                -> None
       Writes the necessary contents for the package init file"""

    # cdat dependencies
    init_lines.append("\n\n")
    init_lines.append("def package_dependencies():\n")
    init_lines.append("  return ['edu.utah.sci.vistrails.numpyscipy']\n")
    init_lines.append("\n\n")

    header = open("init_inc.py").readlines()
    header.append("\n\n")
    header.append('version = "' + cp_version + '"\n')
    header.append('identifier = "' + cp_identifier + '"\n')
    header.append('name = "' + cp_name + '"\n\n')

    outfile = open(output_file, "w")
    outfile.writelines(header)
    outfile.writelines(classes_lines)
    outfile.writelines(init_lines)
    outfile.close()

def parse_files(input_files):
    modules = []
    for f in input_files:
        modules.append(parse_cdat_xml_file(f))
    return modules

def add_canvas_ports_to_canvas_modules(canvas, lines):
    canvas.add_extra_input_port_to_all_modules(lines,
                                               port_name='canvas',
                                               port_type='Canvas',
                                               doc='Canvas object',
                                               optional=False
                                               )
    canvas.add_extra_output_port_to_all_modules(lines,
                                               port_name='canvas',
                                               port_type='Canvas',
                                               doc='Canvas object',
                                               optional=False
                                               )

def add_canvas_module(canvas,init_lines,class_lines):
    canvas.write_extra_module_definition(class_lines,'Canvas')
    canvas.register_extra_vistrails_module(init_lines,'Canvas')

if __name__ == '__main__':
    # usage:
    args = sys.argv
    if len(args) > 2:
        root_dir = args[1]
        output_file = args[2]
    else:
        print "Usage: %s root_dir output_file" % args[0]
        sys.exit(0)

    xmlfiles = []
    input_files = os.walk(root_dir)
    for (d, tree, files) in input_files:
        for f in files:
            if os.path.isfile(os.path.join(d,f)) and f.endswith(".xml"):
                xmlfiles.append(os.path.join(d,f))

    modules = parse_files(xmlfiles)

    extra_init_lines = []
    init_lines = []
    extra_init_lines.append("\ndef initialize(*args, **keywords):\n")
    extra_init_lines.append("    reg = core.modules.module_registry\n\n")


    class_lines = []
    extra_class_lines = []

    print "%s file(s) found."% len(modules)
    for m in modules:
        print "codepath: %s has %s Vistrails Modules."%(m._codepath, len(m._actions))
        m.register_vistrails_modules(init_lines)
        m.write_module_definitions(class_lines)
        if m._codepath == 'vcs.Canvas.Canvas':
            add_canvas_ports_to_canvas_modules(m,init_lines)
            add_canvas_module(m,extra_init_lines, extra_class_lines)
            
        m.write_extra_module_definitions(extra_class_lines)
        m.register_extra_vistrails_modules(extra_init_lines)

    extra_init_lines.extend(init_lines)
    extra_class_lines.extend(class_lines)
    write_init(output_file, extra_class_lines, extra_init_lines)