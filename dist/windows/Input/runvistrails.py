import os
import sys

#1st argument is path to python executable
#2nd argument is path to python file
#3rd argument is the start in directory
#4th argument is the vistrails file to open

args = sys.argv

if len(args) > 3:
    python = args[1]
    pyfile = args[2]
    path = args[3]
    filenames = ""
    if len(args) > 4:
        filenames = " ".join(args[4:])
    os.chdir(path)
    cmdline = '"%s" "%s" "%s"' % (python, pyfile, filenames)
    cmdline = "\"%s" % cmdline
    path += os.getenv('PATH')
    os.putenv('PATH', path)
    os.system(cmdline)
