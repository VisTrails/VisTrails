import os

from PyQt4 import QtGui

def parse_meminfo():
   """parse_meminfo() -> dictionary
Parses /proc/meminfo and returns appropriate dictionary. Only available on Linux."""
   result = {}
   for line in file('/proc/meminfo'):
      (key, value) = line.split(':')
      value = value[:-1]
      if value.endswith(' kB'):
         value = int(value[:-3]) * 1024
      else:
         try:
            value = int(value)
         except ValueError:
            raise VistrailsInternalError("I was expecting '%s' to be an int" % value)
      result[key] = value
   return result

def guessTotalMemory():
   return parse_meminfo()['MemTotal']

def temporaryDirectory():
   return "/tmp/"

def homeDirectory():
   return os.getenv('HOME')

def remoteCopyProgram():
   return "scp -p"

def remoteShellProgram():
   return "ssh -p"

def graphVizDotCommandLine():
   return 'dot -Tplain -o '

def removeGraphvizTemporaries():
   os.unlink(temporaryDirectory() + "dot_output_vistrails.txt")
   os.unlink(temporaryDirectory() + "dot_tmp_vistrails.txt")

import shutil

def link_or_copy(fr, to):
   # Links if possible, but we're across devices, we need to copy.
   try:
      os.link(fr, to)
   except OSError, e:
      if e.errno == 18:
         # Across-device linking is not possible. Let's copy.
         shutil.copyfile(fr, to)
      else:
         raise e

def getClipboard():
   return QtGui.QClipboard.Selection
