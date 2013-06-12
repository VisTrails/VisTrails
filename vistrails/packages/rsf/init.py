###############################################################################
##
## Copyright (C) 2011-2013, NYU-Poly.
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
################################################################################
# Madagascar Package for VisTrails
################################################################################

from vistrails.core.debug import debug
from vistrails.core.modules.basic_modules import Integer, Float, String, File, \
     Boolean, List
from vistrails.core.modules.module_registry import get_module_registry
from vistrails.core.modules.vistrails_module import Module, new_module, ModuleError

import os, sys

# the actual wrappers
import m8r as sf
# the documentation
import rsf.doc

MAX_DIMENSIONS = 3

def splitall(path):
    allparts = []
    while 1:
        parts = os.path.split(path)
        if parts[0] == path:  # sentinel for absolute paths
            allparts.insert(0, parts[0])
            break
        elif parts[1] == path: # sentinel for relative paths
            allparts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            allparts.insert(0, parts[1])
    return allparts

def compute(self):
    prog = self.program
    e = getattr(sf, prog.name)
    infiles = []
    if '<' in prog.snps:
        # read input files
        infiles = self.forceGetInputListFromPort('file')
        infiles.extend(self.forceGetInputFromPort('files', []))
        print "infiles", infiles
    # read parameters
    params = {}
    for name in prog.pars:
        if name.endswith('#'):
            for i in xrange(1, MAX_DIMENSIONS+1):
                nname = name[:-1] + str(i)
                if self.hasInputFromPort(nname):
                    params[nname] = self.getInputFromPort(nname)
        else:
            if self.hasInputFromPort(name):
                params[name] = self.getInputFromPort(name)
    # use '0' if no infiles
    infiles = tuple(infiles) if infiles else 0
    #execute
    if e.plot:
        # assume a plot program
        print "Calling %s.%s(%s)" % (infiles[0], prog.name, params)
        result = getattr(infiles[0], prog.name[2:])(**params)
    else:
        print "Calling %s(%s)%s" % (prog.name, params, infiles)
        if params:
            p = e(**params)
        else:
            p = e
        print "prog:", p, type(p), p.__getitem__
        result = p.__getitem__(infiles)

    if e.stdout:
        # FIXME: strange file ports
        print type(result), result
        if type(result) in [sf.File, sf.Filter]:
            self.setResult('rsf_file', result)
        if type(result) == sf.Vplot:
            self.setResult('plot_file', result)

class Madagascar(Module):
    """ Madagascar is the base Module.
     We will create a Module for each method published by 
     rsf.doc.progs

    """
    compute = compute

    def __init__(self):
        Module.__init__(self)

    
typesDict = { 'string' : String,
              'int' : Integer,
              'integer' : Integer,
              'largeint' : Integer,
              'float': Float,
              'decimal': Float,
              'double': Float,
              'boolean': Boolean,
              'bool': Boolean,
              'file': File,
              'strings' : List, # unsure about this
              'ints' : List, # unsure about this
              'floats': List, # unsure about this
              'bools': List # unsure about this
            }

reg = get_module_registry()
reg.add_module(Madagascar, **{'abstract':True})

modules = {}
# Create all modules
print "RSF init"
for name, prog in sorted(rsf.doc.progs.items()):
    #print len(modules), "Adding", name, prog.file, prog.par
    if not hasattr(sf, name):
        print "Program not callable:", name
    # create dirs
    prev = Madagascar
    ns = ""
    for path in splitall(prog.file)[:-1]:
        # skip main paths
        if path == 'main':
            continue
        if path not in modules:
            M = new_module(prev, path, {})
            modules[path] = M
            reg.add_module(M, **{'abstract':True,
                                 'namespace':ns})
        ns += "|" + path if ns else path
        prev = modules[path]

    M = new_module(prev, str(name), {"program":prog,
                                     "__doc__":prog.text(None)})
    modules[name] = M
    reg.add_module(M, **{'namespace':ns})
    # add ports

    if '<' in prog.snps:
        # add single port and list file ports
        reg.add_input_port(M, "file", File)
        if not ('>' in prog.snps and "vpl" in prog.snps.split('>')[-1]):
            reg.add_input_port(M, "files", List, optional=True)

    # parameters
    for name, par in prog.pars.iteritems():
        desc = par.desc.strip()
        _type = typesDict[par.type.strip()] if par.type and par.type.strip() \
                                           else String
        default = (par.default,) if par.default else None 
        # defaults starts with =
        if default and par.default[0] == '=':
            default = default[1:]
        if not default:
            default = None

        #print "  adding", name, type, desc, default
        # check for dimension parameters
        if name.endswith('#'):
            [reg.add_input_port(M, name[:-1] + str(i), _type,
                                defaults=default,
                                optional=True)
             for i in xrange(1, MAX_DIMENSIONS+1)]
        else:
            reg.add_input_port(M, name, _type, defaults=default,
                                optional=True)

    if '>' in prog.snps:
        if "vpl" in prog.snps.split('>')[-1]:
            reg.add_output_port(M, "plot_file", File)
        else:
            reg.add_output_port(M, "rsf_file", File)
