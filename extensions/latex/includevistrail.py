#!/usr/bin/env python

# the input file format should follow this:
#   path=/Users/emanuele/code/vistrails/branches/v1.2/vistrails/vistrails.py
#   host=vistrails.sci.utah.edu
#   db=vistrails
#   version=598
#   vtid=8
#   buildalways=true
#   other=width=0.45\linewidth 
#
# the buildalways line is optional

import sys
import os.path
import os

def usage():
    print "Usage: "
    print "   %s path/to/options_file" % sys.argv[0]
    sys.exit(1)
    
def bool_conv(x):
    s = str(x).upper()
    if s == 'TRUE':
        return True
    if s == 'FALSE':
        return False
    
def build_vistrails_cmd_line(path_to_vistrails, host, db_name, vt_id, version,
                             path_to_figures):
    cmd_line = 'python "%s" -b -e "%s" -t %s -f %s -u vtserver "%s:%s" > vistrails.log'\
               % (path_to_vistrails,
                  path_to_figures,
                  host,
                  db_name,
                  vt_id,
                  version)
    return cmd_line


    cmd_line = build_vistrails_cmd_line (path_to_vistrails,
                  path_to_figures,
                  host,
                  db_name,
                  vt_id,
                  version)
    result = os.sytem(cmd_line)
    return result
        
def generate_latex(host, db_name, vt_id, version, path_to_figures,
                   graphics_options):
    url_params = "getvt=%s&version=%s&db=%s&host=%s" % (vt_id,
                                                        version,
                                                        db_name,
                                                        host)
    url = "http://www.vistrails.org/extensions/download.php?%s"% url_params
    href = "\href{%s}{" % url
    for root, dirs, file_names in os.walk(path_to_figures):
        break
    n = len(file_names)
    s = ''
    
    for f in file_names:
        if graphics_options:
            filename = os.path.join(path_to_figures,f)
            s += "\includegraphics[%s]{%s}\n" % (graphics_options, filename)
        else:
            s += "\includegraphics{%s}\n" % filename
    s += "}"
    return href+s

def generate_latex_error(cmd_line):
    
    s = """\PackageError{vistrails}{\% 
An error occurred when executing vistrails. \MessageBreak
\space Check vistrails.log for more details
}{\%
Oh dear! Something's gone wrong.
}""" % cmd_line
    return s

options_file = None
try:
    options_file = open(sys.argv[1])
except IndexError:
    usage()
    
lines = options_file.readlines()
path_to_vistrails = None
host = None
db_name = None
vt_id = None
version = None
graphics_options = None
build_always = False
for line in lines:
    args = line.split("=")
    if len(args) > 2:
        args[1] = "=".join(args[1:])
    if args[0] == "path":
        path_to_vistrails = os.path.realpath(args[1].strip(" \n"))
    elif args[0] == "host":
        host = args[1].strip(" \n")
    elif args[0] == "db":
        db_name = args[1].strip(" \n")
    elif args[0] == "vtid":
        vt_id = args[1].strip(" \n")
    elif args[0] == "version":
        version = args[1].strip(" \n")
    elif args[0] == "buildalways":
        build_always = bool_conv(args[1].strip(" \n"))
    elif args[0] == "other":
        graphics_options = args[1].strip(" \n")

path_to_figures = os.path.join("vistrails_images",
                               "%s_%s_%s_%s" % (host, db_name, vt_id, version))

cmd_line = build_vistrails_cmd_line(path_to_vistrails, host, db_name, vt_id,
                                    version, path_to_figures)

if not os.path.exists(path_to_figures):
    os.makedirs(path_to_figures)
    result = os.system(cmd_line)
    if result != 0:
        print generate_latex_error(cmd_line)
        os.rmdir(path_to_figures)
        sys.exit(1)
else:
    if build_always:
        result = os.system(cmd_line)
        if result != 0:
            print generate_latex_error(cmd_line)
            os.rmdir(path_to_figures)
            sys.exit(1)

print generate_latex(host, db_name, vt_id, version, path_to_figures,
                     graphics_options)
