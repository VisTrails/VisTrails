###############################################################################
##
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
from core.modules.vistrails_module import Module
from core.modules.module_registry import get_module_registry
from core.modules.basic_modules import Boolean, String, Variant, List
from core.upgradeworkflow import UpgradeWorkflowHandler
import copy

from fold import Fold
from utils import Map, Filter, AreaFilter, SimilarityFilter
from conditional import If
from products import Dot, Cross
from order import ExecuteInOrder


#################################################################################
## An useful register function for control modules

def registerControl(module):
    """This function is used to register the control modules. In this way, all of
    them will have the same style and shape."""
    
    reg = get_module_registry()
    reg.add_module(module, moduleRightFringe=[(0.0,0.0),(0.25,0.5),(0.0,1.0)],\
                   moduleLeftFringe=[(0.0,0.0),(0.0,1.0)])

#################################################################################

def initialize(*args,**keywords):
    reg = get_module_registry()

    registerControl(Fold)
    registerControl(Map)
    registerControl(Filter)
    registerControl(AreaFilter)
    registerControl(SimilarityFilter)
    registerControl(If)

    reg.add_input_port(Fold, 'FunctionPort', (Module, ""))
    reg.add_input_port(Fold, 'InputList', (List, ""))
    reg.add_input_port(Fold, 'InputPort', (List, ""))
    reg.add_input_port(Fold, 'OutputPort', (String, ""))
    reg.add_output_port(Fold, 'Result', (Variant, ""))

##    reg.add_module(Sum)
##
##    reg.add_module(And)
##
##    reg.add_module(Or)

    reg.add_input_port(If, 'Condition', (Boolean, ""))
    reg.add_input_port(If, 'TruePort', (Module, ""))
    reg.add_input_port(If, 'FalsePort', (Module, ""))
    reg.add_input_port(If, 'TrueOutputPorts', (List, ""), optional=True)
    reg.add_input_port(If, 'FalseOutputPorts', (List, ""), optional=True)
    reg.add_output_port(If, 'Result', (Variant, ""))

    reg.add_module(Dot)
    reg.add_input_port(Dot, 'List_1', (List, ""))
    reg.add_input_port(Dot, 'List_2', (List, ""))
    reg.add_input_port(Dot, 'CombineTuple', (Boolean, ""), optional=True)
    reg.add_output_port(Dot, 'Result', (List, ""))

    reg.add_module(Cross)
    reg.add_input_port(Cross, 'List_1', (List, ""))
    reg.add_input_port(Cross, 'List_2', (List, ""))
    reg.add_input_port(Cross, 'CombineTuple', (Boolean, ""), optional=True)
    reg.add_output_port(Cross, 'Result', (List, ""))

    reg.add_module(ExecuteInOrder)
    reg.add_input_port(ExecuteInOrder, 'module1', (Module, ""))
    reg.add_input_port(ExecuteInOrder, 'module2', (Module, ""))

def handle_module_upgrade_request(controller, module_id, pipeline):
   reg = get_module_registry()

   # format is {<old module name>: (<new_module_klass>, <remap_dictionary>}}
   # where remap_dictionary is {<remap_type>: <name_changes>}
   # and <name_changes> is a map from <old_name> to <new_name> or 
   # <remap_function>
       
   module_remap = {'ListOfElements': (List, {}),
                   'Fold': (Fold, {}),
                   'If': (If, {}),
                   'Dot': (Dot, {}),
                   'Cross': (Cross, {}),
                   'Map': (Map, {}),
                   'Filter': (Filter, {}),
                   'AreaFilter': (AreaFilter, {}),
                   'SimilarityFilter': (SimilarityFilter, {}),
                   }
                   

   old_module = pipeline.modules[module_id]
   if old_module.name in module_remap:
       remap = module_remap[old_module.name]
       new_descriptor = reg.get_descriptor(remap[0])
       try:
           function_remap = remap[1].get('function_remap', {})
           src_port_remap = remap[1].get('src_port_remap', {})
           dst_port_remap = remap[1].get('dst_port_remap', {})
           annotation_remap = remap[1].get('annotation_remap', {})
           action_list = \
               UpgradeWorkflowHandler.replace_module(controller, pipeline,
                                                     module_id, new_descriptor,
                                                     function_remap,
                                                     src_port_remap,
                                                     dst_port_remap,
                                                     annotation_remap)
       except Exception, e:
           import traceback
           traceback.print_exc()
           raise

       return action_list

   # otherwise, just try to automatic upgrade
   # attempt_automatic_upgrade
   return UpgradeWorkflowHandler.attempt_automatic_upgrade(controller, 
                                                           pipeline,
                                                           module_id)
