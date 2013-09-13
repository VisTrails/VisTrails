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

from vistrails.core.modules.module_registry import get_module_registry
from constant_configuration import StandardConstantWidget, \
    StandardConstantEnumWidget
from query_configuration import BaseQueryWidget

def load_cls(cls_item):
    path = None
    if isinstance(cls_item, basestring):
        [path, cls_name] = cls_item.split(':')[:2]
    elif isinstance(cls_item, tuple):
        (path, cls_name) = cls_item
    if path is not None:
        module = __import__(path, globals(), locals(), [cls_name])
        return getattr(module, cls_name)
    return cls_item

def get_widget_class(descriptor, widget_type=None, widget_use=None,
                     return_default=True):        
    reg = get_module_registry()
    cls = reg.get_constant_config_widget(descriptor, widget_type, 
                                         widget_use)
    if cls is None and return_default:
        if descriptor.module is not None and \
           hasattr(descriptor.module, 'get_widget_class'):
            cls = descriptor.module.get_widget_class()
        if cls is None:
            if widget_type == "enum":
                return StandardConstantEnumWidget
            else:
                return StandardConstantWidget
    return load_cls(cls)
        
def get_query_widget_class(descriptor, widget_type=None):
    cls = get_widget_class(descriptor, widget_type, "query", False)
    if cls is None:
        if descriptor.module is not None and \
           hasattr(descriptor.module, 'get_query_widget_class'):
            cls = descriptor.module.get_query_widget_class()
        if cls is None:
            class DefaultQueryWidget(BaseQueryWidget):
                def __init__(self, param, parent=None):
                    BaseQueryWidget.__init__(self, 
                                             get_widget_class(descriptor), 
                                             ["==", "!="],
                                             param, parent)
            return DefaultQueryWidget
    return load_cls(cls)

def get_param_explore_widget_list(descriptor, widget_type=None):
    widget_list = []
    reg = get_module_registry()
    cls_list = reg.get_all_constant_config_widgets(descriptor, "paramexp")
    for cls in cls_list:
        if cls is None:
            pass
        widget_list.append(load_cls(cls))
    return widget_list


