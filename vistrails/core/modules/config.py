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

from collections import namedtuple as _namedtuple, Mapping

def namedtuple(typename, field_names, default_values=None):
    T = _namedtuple(typename, field_names)
    if default_values is not None:
        T.__new__.__defaults__ = default_values
    return T

def subnamedtuple(typename, cls, default_values=None):
    return namedtuple(typename, cls._fields, default_values)

ConstantWidgetConfig = namedtuple('ConstantWidgetConfig',
                                  ['widget', 'widget_type', 'widget_use'],
                                  (None, None))

QueryWidgetConfig = subnamedtuple('QueryWidgetConfig', ConstantWidgetConfig, 
                                  (None, 'query'))
ParamExpWidgetConfig = subnamedtuple('ParamExpWidgetConfig', 
                                     ConstantWidgetConfig, (None, 'paramexp'))

ModuleSettings = namedtuple('ModuleSettings',
                          ['name', 'configureWidgetType', 'constantWidget',
                           'constantWidgets', 'signatureCallable', 
                           'constantSignatureCallable', 'moduleColor', 
                           'moduleFringe', 'moduleLeftFringe',
                           'moduleRightFringe', 'abstract', 'package', 
                           'namespace', 'version', 'package_version', 
                           'hide_namespace', 'hide_descriptor', 'is_root', 
                           'ghost_package', 'ghost_package_version', 
                           'ghost_namespace'],
                          (None, None, None, None, None, None, None, None, 
                           None, None, False, None, None, None, None, False, 
                           False, False, None, None, None))

Port = namedtuple('Port',
                  ['name', 'signature', 'optional', 'sort_key',
                   'label', 'default', 'values', 'entry_type',
                   'docstring', 'shape', 'min_conns', 'max_conns'],
                  (False, -1, None, None, None, None, None, None, None, None))

OutputPort = namedtuple('OutputPort',
                        ['name', 'signature', 'optional', 'sort_key',
                         'docstring', 'shape', 'min_conns', 'max_conns'])

CompoundPort = namedtuple('CompoundPort',
                          ['name', 'signature', 'optional', 'sort_key', 
                           'labels', 'defaults', 'values', 'entry_types',
                           'docstring', 'shape', 'min_conns', 
                           'max_conns', 'items'],
                          (None, False, -1, None, None, None, None, None, 
                           None, None, None, None))

PortItem = namedtuple('PortItem',
                      ['signature', 'label', 'default', 'values', 'entry_type'],
                      (None, None, None, None))
OutputPortItem = namedtuple('OutputPortItem', ['signature'], (None))
