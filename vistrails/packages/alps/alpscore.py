# VisTrails package for ALPS, Algorithms and Libraries for Physics Simulations
#
# Copyright (C) 2009 - 2010 by Matthias Troyer <troyer@itp.phys.ethz.ch>,
#                              Synge Todo <wistaria@comp-phys.org>
#
# Distributed under the Boost Software License, Version 1.0. (See accompany-
# ing file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
#
#
##############################################################################

from vistrails.core.configuration import ConfigurationObject
from vistrails.core.modules.vistrails_module import Module, ModuleError, NotCacheable
from vistrails.core.system import list2cmdline
import vistrails.core.modules.basic_modules
import vistrails.core.modules.module_registry
import os
import os.path
import platform
import shutil
import sys
import copy

from PyQt4 import QtCore, QtGui
from vistrails.packages.spreadsheet.basic_widgets import SpreadsheetCell, CellLocation
from vistrails.packages.spreadsheet.spreadsheet_cell import QCellWidget
import vistrails.packages.spreadsheet

import pyalps

basic = vistrails.core.modules.basic_modules

config = ConfigurationObject()

##############################################################################
def _get_path(binary_file):
   
    if config.check('alpspath'):
        exename = os.path.join(config.alpspath, binary_file)
    else:
        exename = binary_file
    if platform.system()=='Windows':
        return exename +'.exe'
    else:
        return exename

def _get_tool_path(binary_file):
    if config.check('toolpath'):
        exename = os.path.join(config.toolpath, binary_file)
    else:
        exename = binary_file
    if platform.system()=='Windows':
        return exename +'.exe'
    else:
        return exename

def _get_default_mpi_procs():
    if config.check('mpiprocs'):
      return config.mpiprocs
    else:
      return 0

def _get_mpi_run():
    if config.check('mpirun'):
      cmd = "res =" + config.mpirun
      exec cmd
      return res
    else:
      return ['mpirun','-np']
      
def get_temporary_path(param):
    of = param.interpreter.filePool.create_file()
    os.unlink(of.name)
    os.mkdir(of.name)
    dir = basic.Directory
    dir.name = of.name
    return dir
   
class SystemCommand(Module):
    def execute(self,cmdline):
        if pyalps.executeCommand(cmdline) <> 0:
           raise ModuleError(self, 'Execution failed')

class SystemCommandLogged(Module):
    def execute(self,cmdline):
        logfile = self.interpreter.filePool.create_file(suffix='.log')
        result = pyalps.executeCommandLogged(cmdline,logfile.name)
        self.setResult('log_file', logfile)  
        if result <> 0:
          if platform.system()=='Darwin':
            pyalps.executeCommand(['open',logfile.name])
          else:
            print "Error log in ", logfile.name
            print "COmmand was: ", cmdline
          raise ModuleError(self, 'Execution failed')
    _output_ports = [('log_file',[basic.File])]


class DisplayInBrowser(NotCacheable, SystemCommand):
    """ 
    Show one or more files in a web browser. The path to the browser can be set up in the
    preferences panel of the ALPS package under the 'browser' entry.
    """
    def compute(self):
        cmdlist = 'false'
        if config.check('browser'):
          cmdlist = eval(config.browser)
        else:
          if platform.system() == 'Windows':
            cmdlist = ['start','C:\Program Files\Internet Explorer\iexplore.exe']
          if platform.system()=='Darwin':
            cmdlist = ['open', '-a', 'Safari']
        if self.hasInputFromPort('file'):
           cmdlist += [self.getInputFromPort('file').name]
        if self.hasInputFromPort('files'):
           cmdlist += self.getInputFromPort('files')
        self.execute(cmdlist)
    _input_ports = [('file', [basic.File]),
                    ('files', [basic.List])]
    _input_ports = [('file', [basic.File]),
                    ('files', [basic.List])]

class WriteTextFile(basic.Module):
    """ 
    Write a string into a text file. A suffix for the file name can optionally
    be specified through the suffix input port.
    """

    def compute(self):
        if self.hasInputFromPort('suffix'):
          f = self.interpreter.filePool.create_file(suffix=self.getInputFromPort('suffix'))
        else:
          f = self.interpreter.filePool.create_file()
        out = file(f.name,'w')
        out.write(self.getInputFromPort('text'))
        out.close()
        self.setResult('file',f)
    _input_ports = [('text', [basic.String]),
                    ('suffix', [basic.String])]
    _output_ports = [('file',[basic.File])]

class AlpsExecutablePath(basic.Module):
    """
    Returns the directory containing the ALPS executables. This directory can be set in the VisTrails 
    Preferences dialog by configuring alpspath in the ALPS module.
    """

    def compute(self):
        dir = basic.Directory()
        dir.name = config.alpspath
        self.setResult('dir',dir)
    _output_ports = [('dir',[basic.Directory])]


class TextCell(SpreadsheetCell):
    """
    TextCell is a custom Module to view plain text files in a spreadsheet.
    
    """
    def compute(self):
        """ compute() -> None
        Dispatch the text contents to the spreadsheet
        """
        if self.hasInputFromPort("File"):
            fileValue = self.getInputFromPort("File")
        else:
            fileValue = None
        self.display(TextCellWidget, (fileValue,))

class TextCellWidget(QCellWidget):
    """
  TextCellWidget has a QTextEdit to display plain text files
    
    """
    def __init__(self, parent=None):
        """ TextCellWidget(parent: QWidget) -> TextCellWidget
        Create a text cell without a toolbar and without editing capabilities
        
        """
        QCellWidget.__init__(self, parent)
        self.setLayout(QtGui.QVBoxLayout(self))
        self.browser = QtGui.QTextEdit()
        self.layout().addWidget(self.browser)
        self.browser.setReadOnly(True)
 #       self.browser.controlBarType = None

    def updateContents(self, inputPorts):
        """ updateContents(inputPorts: tuple) -> None
        Updates the contents with a new changed in filename
        
        """
        (fileValue,) = inputPorts
        if fileValue:
            try:
                fi = open(fileValue.name, "r")
            except IOError:
                self.browser.setText("Cannot load the text file!")
                return            
            self.browser.setText(fi.read())
            fi.close()
        else:
            self.browser.setText("No text file is specified!")

class DirectoryDoesNotExist: pass
class FileDoesNotExist: pass


class ConcatenatePath(Module):
    """
    This module concatentates two portions of a file or directory path.
    It returns a string for the concatenated name as well as file and directory
    objects. The latter two are there as convenience functions to avoid having
    to put the string into a File or Directory module. 
    Note that the module does not check the existence of these directories or
    files.
    """
    def compute(self):
      f = os.path.join(self.getInputFromPort('base').name,self.getInputFromPort('leaf'))
      self.setResult('path', f)
#      if os.path.isdir(f):
      dir = basic.Directory()
      dir.name =f
      self.setResult('directory', dir)
#      else:
#        self.setResult('directory', DirectoryDoesNotExist())
#      if os.path.isfile(f):
      file = basic.File()
      file.name =f
      self.setResult('file', file)
#      else:
#        self.setResult('file', FileDoesNotExist())
    _input_ports = [('base', [basic.Directory]),
                    ('leaf',[basic.String])]
    _output_ports = [('path', [basic.String]),
                     ('directory', [basic.Directory]),
                     ('file',[basic.File])]

class ConcatenatePathList(Module):
    """
    This module concatentates two portions of a file or directory path.
    It returns a string for the concatenated name as well as file and directory
    objects. The latter two are there as convenience functions to avoid having
    to put the string into a File or Directory module. 
    Note that the module does not check the existence of these directories or
    files.
    """
    def compute(self):
        base = self.getInputFromPort('base').name
        leafs = self.getInputFromPort('leafs')
        
        paths = [os.path.join(base, l) for l in leafs]
        
        self.setResult('paths', paths)
        
        def f(p):
            d = basic.Directory()
            d.name = p
            return d
        self.setResult('directories', [f(p) for p in paths])
        
        def f(p):
            d = basic.File()
            d.name = p
            return d
        self.setResult('files', [f(p) for p in paths])
    
    _input_ports = [('base', [basic.Directory]),
                 ('leafs',[basic.List])]
    _output_ports = [('paths', [basic.List]),
                  ('directories', [basic.List]),
                  ('files',[basic.List])]

class DirectorySink(Module,NotCacheable):
    """
    This module copies the contents of a specified directory to a new location
    given by the outputName. If overrideDirectory is turned on an already
    existing directory is first removed.
    """
    def compute(self):
      self.checkInputPort("directory")
      self.checkInputPort("outputName")
      v1 = self.getInputFromPort("directory").name
      v2 = self.getInputFromPort("outputName")
      is_dir = os.path.isdir(v1)
      if not os.path.isdir(v1):
        raise ModuleError(self,'Expected a directory, found file')
      if (self.hasInputFromPort("overrideDirectory") and
              self.getInputFromPort("overrideDirectory")):
        shutil.rmtree(v2)
      try:
        shutil.copytree(v1, v2)
      except OSError, e:
              msg = "Could not copy to directory '%s': %s" % (v2, e)
              raise ModuleError(self, msg)

    _input_ports = [('directory', [basic.Directory]),
                    ('outputName',[basic.String]),
                    ('overrideDirectory',[basic.Boolean])]


def initialize(): pass


def selfRegister():

    reg = vistrails.core.modules.module_registry.get_module_registry()

    reg.add_module(SystemCommand,namespace="Tools",abstract=True)
    reg.add_module(SystemCommandLogged,namespace="Tools",abstract=True)
    reg.add_module(DisplayInBrowser,namespace="Tools")
    reg.add_module(WriteTextFile,namespace="Tools")

    reg.add_module(TextCell,namespace="Tools")
    reg.add_input_port(TextCell, "Location", CellLocation)
    reg.add_input_port(TextCell, "File", basic.File)

    reg.add_module(ConcatenatePath,namespace="Tools")
    reg.add_module(ConcatenatePathList,namespace="Tools")
    reg.add_module(DirectorySink,namespace="Tools")

    reg.add_module(AlpsExecutablePath,namespace="Tools")
