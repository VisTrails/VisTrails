#!/usr/bin/env python
###############################################################################
##
## Copyright (C) 2014-2015, New York University.
## Copyright (C) 2011-2014, NYU-Poly.
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
##  - Neither the name of the New York University nor the names of its
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

from __future__ import division


import importlib
import os.path

from vistrails.core.wrapper.diff import apply_diff
from vistrails.core.wrapper.specs import SpecList, ClassSpec, \
    FunctionSpec
from vistrails.core.wrapper.python_parser import PythonParser

def parse():
    parser = PythonParser(instance_type='basic:List')
    this_dir = os.path.dirname(os.path.realpath(__file__))

    ##########################################################################
    # wrap classes

    class_spec_name = os.path.join(this_dir,'classes.xml')
    raw_class_spec_name = class_spec_name[:-4] + '-raw.xml'
    class_spec_diff = class_spec_name[:-4] +  '-diff.xml'

    # generate specs
    classes = []
    class_names = []
    functions = []
    func_names = []
    def add(base, clist, namespace):
        if isinstance(clist, basestring):
            clist = clist.split(',')
        for c in clist:
            klass = base + '.' + c
            if klass in class_names:
                print "Skipping duplicate:", klass
                continue
            class_names.append(klass)
            classes.append(parser.parse_class(klass,
                                              namespace=namespace,
                                              attribute_parsing=False))
            inspector = parser.parse_class(klass,
                                           name=c+'Inspector',
                                           namespace=namespace,
                                           argument_parsing=False)
            if (len(inspector.input_port_specs) > 1 or
                len(inspector.output_port_specs) > 1):
                classes.append(inspector)
            for f in parser.parse_class_methods(klass,
                                         namespace=namespace+'|'+c+'Methods'):
                fname = (f.namespace, f.module_name)
                if fname in func_names:
                    print "Skipping duplicate:", fname
                    continue
                func_names.append(fname)
                functions.append(f)

    def add_all(lib):
        m = importlib.import_module(lib)
        to_add = []
        for f in (m.__all__ if hasattr(m,'__all__') else
                [s for s in dir(m) if not s.startswith('_')]):
            try:
                typename = type(getattr(m, f)).__name__
                if typename in ['type']:
                    to_add.append(f)
                #else:
                #    print "Skipped non-class: %s(%s)" % (f, typename)

            except AttributeError:
                print "No such class:", f
        add(lib, to_add, lib.split('.', 1)[-1].replace('.','|'))

    add_all('scipy.interpolate')
    add_all('scipy.odr')
    add_all('scipy.spatial')

    class_list = SpecList(classes)
    class_list.write_to_xml(raw_class_spec_name)
    apply_diff(ClassSpec, raw_class_spec_name, class_spec_diff,
               class_spec_name)


    ##########################################################################
    # wrap functions

    fun_spec_name = os.path.join(this_dir, 'functions.xml')
    raw_fun_spec_name = fun_spec_name[:-4] + '-raw.xml'
    fun_spec_diff = fun_spec_name[:-4] + '-diff.xml'

    # generate specs

    def add(base, flist, namespace):
        if isinstance(flist, basestring):
            flist = flist.split(',')
        for f in flist:
            functions.append(parser.parse_function(base + '.' + f,
                                                   namespace=namespace))

    def add_all(lib):
        m = importlib.import_module(lib)
        to_add = []
        for f in (m.__all__ if hasattr(m,'__all__') else
                [s for s in dir(m) if not s.startswith('_')]):
            try:
                typename = type(getattr(m, f)).__name__
                if 'function' in typename:
                    to_add.append(f)
                #else:
                #    print "Skipped non-function: %s(%s)" % (f, typename)
            except AttributeError:
                print "No such function:", f
        add(lib, to_add, lib.split('.', 1)[-1].replace('.','|'))

    for L in 'cluster.vq,cluster.hierarchy,fftpack,fftpack.convolve,' \
             'integrate,interpolate,io,linalg,misc,ndimage,odr,optimize,' \
             'signal,sparse,sparse.linalg,sparse.csgraph,spatial.distance,' \
             'special,stats,stats.mstats,weave'.split(','):
        add_all('scipy.' + L)

    fun_list = SpecList(functions)
    fun_list.write_to_xml(raw_fun_spec_name)
    apply_diff(FunctionSpec, raw_fun_spec_name, fun_spec_diff, fun_spec_name)
    return class_list, fun_list

if __name__ == '__main__':
    parse()
