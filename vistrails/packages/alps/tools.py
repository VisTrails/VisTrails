# VisTrails package for ALPS, Algorithms and Libraries for Physics Simulations
#
# Copyright (C) 2009 - 2010 by Matthias Troyer <troyer@itp.phys.ethz.ch>,
#                              Synge Todo <wistaria@comp-phys.org>,
#                              Bela Bauer <bauerb@phys.ethz.ch>
#
# Distributed under the Boost Software License, Version 1.0. (See accompany-
# ing file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
#
#
##############################################################################

from vistrails.core.modules.vistrails_module import Module, ModuleError, NotCacheable
from core.configuration import ConfigurationObject
import core.bundles
import vistrails.core.modules.basic_modules
import vistrails.core.modules.module_registry
from packages.HTTP.init import HTTPFile
import os
import os.path
import tempfile
import copy
import glob
import zipfile
import datetime

import platform
import codecs

import parameters
import alpscore
import system
from parameters import Parameters

import pyalps
import pyalps.pytools # the C++ conversion functions


basic = vistrails.core.modules.basic_modules

##############################################################################

from pyalps import ResultFile
from dataset import ResultFiles
from dataset.dataset_exceptions import EmptyInputPort, InvalidInput

class UnzipDirectory(Module):
    """ Unzip a zipped directory """
    _input_ports = [('zipfile',[basic.File])]
    _output_ports = [('output_dir', [basic.Directory])]
    
    def compute(self):
        o = self.interpreter.filePool.create_file()
        os.unlink(o.name)
        os.mkdir(o.name)
        dir = basic.Directory
        dir.name = o.name
        current_directory = os.getcwd()
        os.chdir(dir.name)
        
        input_file = self.getInputFromPort('zipfile').name
        zf = zipfile.ZipFile(input_file,'r')
        zf.extractall()
        zf.close()
        # chdir outside of the temporary directories to let VisTrails clean up
        os.chdir(current_directory)
        
        self.setResult('output_dir',dir)

class ZipDirectory(Module):
    """Zip a directory"""
    
    _input_ports = [('dir',[basic.Directory])]
    _output_ports = [('zipfile', [basic.File])]
    
    def compute(self):
        inpath = self.getInputFromPort('dir').name
        
        outfile = self.interpreter.filePool.create_file()
        zf = zipfile.ZipFile(outfile.name,'w')
        fileList = []
        arcList = []
        for root, subFolders, files in os.walk(inpath):
            for file in files:
                fileList.append(os.path.join(root,file))
        for file in fileList:
            arcname = file.replace(inpath,'')
            if arcname[0] == os.path.sep:
                arcname = arcname[1:]
            arcname = os.path.join(os.path.split(inpath)[-1], arcname)
            arcList.append(arcname)
            zf.write(file,arcname)
        zf.close()
        
        self.setResult('zipfile',outfile)

class WriteParameterFile(Module):
     """Creates a parameter file.
     """
     def compute(self):
         o = self.interpreter.filePool.create_file()
         if self.hasInputFromPort('simulationid'):
             o = self.interpreter.filePool.create_file()
             o.name = os.path.join(os.path.dirname(o.name),self.getInputFromPort('simulationid'))
         f = file(o.name,'w')
         if self.hasInputFromPort('parms'):
           input_values = self.forceGetInputListFromPort('parms')
           for p in input_values:
             res = parameters.make_parameter_data(p)
             res.write(f);
         f.close()
         self.setResult('file', o)
         self.setResult('simulationid',os.path.basename(o.name))
     _input_ports = [('parms', [Parameters]),
                     ('simulationid',[basic.String])]
     _output_ports=[('file', [basic.File]),
                    ('simulationid',[basic.String])]


class WriteInputFiles(Module):
     """ This module writes the XML input files for ALPS"""
         
     def compute(self):
         of = self.interpreter.filePool.create_file()
         os.unlink(of.name)
         os.mkdir(of.name)
         dir = basic.Directory
         dir.name = of.name
         o = self.interpreter.filePool.create_file()
         if self.hasInputFromPort('simulationid'):
           base_name = self.getInputFromPort('simulationid')
         else:
           base_name = os.path.basename(o.name)

         print(base_name);


         ofile = basic.File()
         ofile.name = os.path.join(dir.name,base_name + '.in.xml')

         if self.hasInputFromPort('parms'):
           input_values = self.forceGetInputListFromPort('parms')
           l = []
           for p in input_values:
             if isinstance(p,list):
               l += p
             else:
               l += [p]

           if self.hasInputFromPort('baseseed'):
             baseseed = self.getInputFromPort('baseseed')
           else:
             baseseed = pyalps.generateSeed()
             
           Module.annotate(self,{'baseseed':baseseed})
           
           pyalps.writeInputFiles(os.path.join(dir.name,base_name),l,baseseed)
           pyalps.copyStylesheet(dir.name)
           
         self.setResult("output_dir", dir)
         self.setResult("output_file", ofile)
     _input_ports = [('parms', [Parameters]),
                     ('baseseed',[basic.Integer],True),
                     ('simulationid',[basic.String])]
     _output_ports = [('output_file', [basic.File]),
                     ('output_dir', [basic.Directory])]


class WriteTEBDInputFiles(Module):
     """ This module writes the tebd input files for ALPS"""
         
     def compute(self):
         of = self.interpreter.filePool.create_file()
         os.unlink(of.name)
         os.mkdir(of.name)
         dir = basic.Directory
         dir.name = of.name
         o = self.interpreter.filePool.create_file()
         if self.hasInputFromPort('simulationid'):
           base_name = self.getInputFromPort('simulationid')
         else:
           base_name = os.path.basename(o.name)

         input_values = self.forceGetInputListFromPort('parms')
         if type(input_values[0])==list:
                 input_values=input_values[0]
         nmlList=pyalps.writeTEBDfiles(input_values, os.path.join(dir.name,base_name))
         pyalps.copyStylesheet(dir.name)
           
         self.setResult("output_dir", dir)
         self.setResult("output_files", nmlList)
     _input_ports = [('parms', [Parameters]),
                     ('baseseed',[basic.Integer],True),
                     ('simulationid',[basic.String])]
     _output_ports = [('output_files', [basic.File]),
                     ('output_dir', [basic.Directory])]


class Parameter2XML(alpscore.SystemCommandLogged):
    def compute(self):
        o = self.interpreter.filePool.create_file()
        os.unlink(o.name)
        os.mkdir(o.name)
        input_file = self.getInputFromPort("file")
        base_name = os.path.basename(input_file.name)
        dir = basic.Directory
        dir.name = o.name
        self.execute(['cd',o.name,';', alpscore._get_path('parameter2xml'),
                            input_file.name, base_name])
        # Things would be easier on our side if ALPS somehow
        # advertised all the files it creates. Right now, it will be
        # hard to make sure all temporary files that are created will
        # be cleaned up. We are trying to keep all the temporaries
        # inside a temp directory, but the lack of control over where
        # the files are created hurt.
        ofile = basic.File()
        ofile.name = os.path.join(o.name,base_name + '.in.xml')
        self.setResult("output_dir", dir)
        self.setResult("output_file", ofile)
    _input_ports = [('file', [basic.File]),
                    ('output_dir', [basic.File],True)]
    _output_ports = [('output_file', [basic.File]),
                     ('output_dir', [basic.Directory]),
                     ('log_file',[basic.File])]


class Glob(Module):
    def expand(self,name):
        l = recursive_glob(name)
        self.setResult('value',l)
    def compute(self):
      self.expand(self.getInputFromPort('input_file').name)
    _input_ports = [('input_file',[basic.File])]
    _output_ports = [('value',[basic.List])]

class GetCloneFiles(Module):
     """ 
     This module gets all ALPS clone files of MC simulations in a given directory.
     The tasks, runs, and prefix inputs take regular expressions limiting the task numbers, prefix of the simulation, and run (clone) numbers. They default to '*', meaning all.
     """
     def compute(self):
         tasks = '*'
         runs = '*[0-9]'
         prefix = '*'
         d = self.getInputFromPort('dir')
         dirname = d.name
         if (self.hasInputFromPort('tasks')):
           tasks = str(self.getInputFromPort('tasks'))
         if (self.hasInputFromPort('runs')):
           runs = str(self.getInputFromPort('runs'))
         if (self.hasInputFromPort('prefix')):
           prefix = str(self.getInputFromPort('prefix'))+'*'
         files = glob.glob(os.path.join(dirname,prefix+ '.task' + tasks + '.out.run' +runs))
# remove HDF5 files from the list
         res = []
         for f in files:
           if f[-3:]!='.h5':
             res.append(f)
         self.setResult('value',res)
     _input_ports = [('dir',[basic.Directory]), 
                     ('prefix',[basic.String]), 
                     ('tasks',[basic.String]),
                     ('runs',[basic.String])]
     _output_ports = [('value',[basic.List])]

class GetResultFiles(Module):
    """ 
    This module gets all ALPS resuls files recursively scanning the given directory and all its subdirectories.
    The prefix and tasks input ports can be used to specify regular expressions limiting the prefix and task number of result files using the ALPS naming convention. 
    Alternatively the pattern port can be used to specify an arbitrary regular expression that the result files have to match.
    """
    def compute(self):
        if self.hasInputFromPort('pattern') and self.hasInputFromPort('dir'):
            dir = self.getInputFromPort('dir').name
            # try several ways to match the pattern
            pattern = self.getInputFromPort('pattern')
            pattern = os.path.expanduser(pattern)
            pattern = os.path.expandvars(pattern)
            # result = glob.glob(pattern)
            result = pyalps.recursiveGlob(dir,pattern)
            self.setResult('value',result)
            self.setResult('resultfiles', [ResultFile(x) for x in result])
        else:
            prefix = '*'
            tasks = '*'
            d = self.getInputFromPort('dir')
            dirname = d.name
            if self.hasInputFromPort('tasks'):
                tasks = self.getInputFromPort('tasks')
            if self.hasInputFromPort('prefix'):
                prefix = self.getInputFromPort('prefix')
            if self.hasInputFromPort('format'):
                fm = self.getInputFromPort('format')
                if fm == 'hdf5':
                    result = pyalps.recursiveGlob(dirname, prefix+ '.task' + tasks + '.out.h5')
                else:
                    result = pyalps.recursiveGlob(dirname, prefix+ '.task' + tasks + '.out.xml')
            else:
                result = pyalps.recursiveGlob(dirname, prefix+ '.task' + tasks + '.out.xml')
            self.setResult('value', result)
            self.setResult('resultfiles', [ResultFile(x) for x in result])

    _input_ports = [('dir',[basic.Directory]), 
        ('prefix',[basic.String]), 
        ('tasks',[basic.String]),
        ('pattern',[basic.String]),
        ('format',[basic.String])]
    _output_ports = [('value',[basic.List]),
        ('resultfiles',[ResultFiles])]

class GetCheckpointFiles(Module):
     """ 
     This module gets all ALPS checkpoint files of MPS simulations in a given directory.
     The tasks, and prefix inputs take regular expressions limiting the task numbers and prefix of the simulation. They default to '*', meaning all.
     
     """
     def compute(self):
         tasks = '*'
         prefix = '*'
         d = self.getInputFromPort('dir')
         dirname = d.name
         if (self.hasInputFromPort('tasks')):
           tasks = str(self.getInputFromPort('tasks'))
         if (self.hasInputFromPort('prefix')):
           prefix = str(self.getInputFromPort('prefix'))+'*'
         files = glob.glob(os.path.join(dirname,prefix+ '.task' + tasks + '.out.chkp'))
         self.setResult('value',files)
     _input_ports = [('dir',[basic.Directory]), 
                     ('prefix',[basic.String]), 
                     ('tasks',[basic.String])]
     _output_ports = [('value',[basic.List])]


class Convert2XML(Module):
    """
    This module takes a list of ALPS result or clone files and converts each of them to XML. It returns a list of the converted XML files. 
    """
    def compute(self):
        input_files = self.getInputFromPort('input_file')
        olist = []
        for f in input_files:
          olist.append(pyalps.pytools.convert2xml(str(f)))
          pyalps.copyStylesheet(os.path.dirname(f))
        self.setResult('value', olist)
    _input_ports = [('input_file', [basic.List])]
    _output_ports = [('value', [basic.List])]
 

class ConvertXML2HTML(alpscore.SystemCommand):
    """
    This module takes an XML file or a list of XML files and converts each of them to HTML. 
    """
    def convert(self,input_file):
        output_file = self.interpreter.filePool.create_file(suffix='.html')
        if platform.system() == 'Windows':
          cmdlist = ['msxsl.exe',input_file] + self.style + ['-o', output_file.name]
        if platform.system() != 'Windows':
          cmdlist = [alpscore._get_path('xslttransform')] + self.style + [input_file, '>' , output_file.name]
        self.execute(cmdlist)
        if platform.system() == 'Windows': # need to convert to UTF-8
          fin = codecs.open(output_file.name,"r","utf-16")
          u = fin.read()
          fin.close()
          fout = file(output_file.name,"w")
          fout.write(u.encode("utf-8"))
          fout.close()
        return output_file

    def compute(self):
        if self.hasInputFromPort('stylesheet'):
          self.style = [self.getInputFromPort('stylesheet').name]
        else:
          self.style = [pyalps.xslPath()]
        if (self.hasInputFromPort('input_file')):
            self.setResult('output_file',self.convert(self.getInputFromPort('input_file').name))
        if (self.hasInputFromPort('input_files')):
            input_files = self.getInputFromPort('input_files')
            output_files = []
            for f in input_files:
                output_files.append(self.convert(f).name)
            self.setResult('output_files', output_files)
    _input_ports = [('input_file', [basic.File]),
                    ('input_files', [basic.List]),
                    ('stylesheet',[basic.File])]
    _output_ports = [('output_file', [basic.File]),
                     ('output_files', [basic.List])]

class Convert2Text(alpscore.SystemCommand):
    def compute(self):
        input_file = self.getInputFromPort('input_file')
        output_file = self.interpreter.filePool.create_file(suffix='.txt')
        self.execute([alpscore._get_path('convert2text'), input_file.name, '>' , output_file.name])
        self.setResult('output_file', output_file)
    _input_ports = [('input_file', [basic.File])]
    _output_ports = [('output_file', [basic.File])]

class GetSimName:
    def get_sim_name(self,dirname):
        l = glob.glob(os.path.join(dirname,'*.out.xml'))
        l.sort()
        return l[0]


class GetJobFile(basic.Module,GetSimName):
    """ This module returns the name of the ALPS job output file in the specified directory. It assumes that there is only one such job file in any directory. """
    def compute(self):
        dir = self.getInputFromPort("dir")
        o = basic.File
        o.name = self.get_sim_name(dir.name)
        self.setResult("file",o)
        self.setResult("output_file",o)
    _input_ports = [('dir', [basic.Directory])]
    _output_ports = [('file', [basic.File]),
                     ('output_file', [basic.File],True)]
                     
class PickFileFromList(basic.Module):
    """ This module picks a specified file (index) from a list of files """
    def compute(self):
        f=basic.File()
        ind = 0
        if self.hasInputFromPort('index'):
          ind = self.getInputFromPort('index')
        f.name = self.getInputFromPort('files')[ind]
        self.setResult('file',f)
    _input_ports = [('files', [basic.List]),
                    ('index', [basic.Integer])]
    _output_ports = [('file', [basic.File])]

class ArchiveDirectory(basic.Module):
    """
    Retrieves the path to an archive directory. 
    
    To be portable between machines an archive is specified as a URL. The mapping from URL to
    local path (typically the mount point of the archive disk can be specified in the configuration
    preferences as a dict named archives.
    
    Optionally a local path can be directly specified, but is only used if the archive was not
    specified or no mapping from archive to a local path is given.
    """
    _input_ports = [
        ('archive', [basic.String]),
        ('path', [basic.Directory])
    ]
    _output_ports = [('output', [basic.Directory])]
    
    check_file = False
    
    def compute(self):
        fixpath = lambda path: os.path.normpath(path.replace('/', os.path.sep))
        listify = lambda l: l if type(l) == list else [l]
        
        replace_dict = {}
        if alpscore.config.check('archives'):
            replace_dict = basic.Dictionary.translate_to_python(alpscore.config.archives)
        else:
            raise InvalidInput("Check configuration!")
        replace_dict = dict([(k,listify(v)) for k,v in replace_dict.items()])
        replace_dict = dict([(k,[vv+os.path.sep for vv in v]) for k,v in replace_dict.items()])
        
        fpath = None
        
        if self.hasInputFromPort('archive'):
            path = self.getInputFromPort('archive')
            for k,v in replace_dict.items():
                for qq in v:
                    testpath = fixpath(path.replace(k, qq))
                    if os.path.exists(testpath):
                        fpath = testpath
                        break
            if self.check_file and fpath == None:
                try:
                    print 'Attempting HTTP'
                    loader = HTTPFile()
                    errcode, f, fn = loader.download(path)
                    if errcode == 0 or errcode == 1:
                        fpath = fn
                except Exception, e:
                    print e
        
        if self.hasInputFromPort('path') and fpath == None:
            lp = self.getInputFromPort('path').name
            if os.path.exists(lp):
                fpath = lp
        
        if fpath == None:
            raise InvalidInput("Can't locate file at any location.")
        
        fpath = os.path.normpath(fpath)
        
        if self.check_file:
            f = basic.File()
            f.name = fpath
            self.setResult('output', f)
        else:
            dir = basic.Directory()
            dir.name = fpath
            self.setResult('output', dir)

class ArchiveFile(ArchiveDirectory):
    _input_ports = [
        ('archive', [basic.String]),
        ('path', [basic.File])
    ]
    _output_ports = [('output', [basic.File])]
    check_file = True

def initialize(): pass

def selfRegister():

  reg = vistrails.core.modules.module_registry.get_module_registry()
  
  reg.add_module(WriteParameterFile,namespace="Tools",abstract=True)
  reg.add_module(WriteTEBDInputFiles,namespace="Tools")
  reg.add_module(Parameter2XML,namespace="Tools",abstract=True)
  reg.add_module(WriteInputFiles,namespace="Tools")
  
  reg.add_module(Glob,namespace="Tools",abstract=True)
  reg.add_module(GetCloneFiles,namespace="Tools")
  reg.add_module(GetResultFiles,namespace="Tools")
  reg.add_module(GetCheckpointFiles,namespace="Tools")
  
  reg.add_module(Convert2XML,namespace="Tools")
  reg.add_module(Convert2Text,namespace="Tools",abstract=True)
  reg.add_module(ConvertXML2HTML,namespace="Tools")

  reg.add_module(UnzipDirectory,namespace="Tools")
  reg.add_module(ZipDirectory,namespace="Tools")
  reg.add_module(ArchiveDirectory,namespace="Tools")
  reg.add_module(ArchiveFile,namespace="Tools")

  reg.add_module(GetJobFile,namespace="Tools")

  reg.add_module(PickFileFromList,namespace="Tools")
