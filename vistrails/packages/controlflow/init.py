###############################################################################
##
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
from vistrails.core.modules.vistrails_module import Module
from vistrails.core.modules.module_registry import get_module_registry
from vistrails.core.modules.basic_modules import Boolean, String, Variant, \
    List, Not, Integer, Float
from vistrails.core.upgradeworkflow import UpgradeWorkflowHandler

from fold import Fold, FoldWithModule
from utils import Map, Filter, Sum, And, Or
from conditional import If, Default
from products import ElementwiseProduct, Dot, Cross, CartesianProduct
from order import ExecuteInOrder
from looping import For, While


#################################################################################
## An useful register function for control modules

def registerControl(module, **kwargs):
    """This function is used to register the control modules. In this way, all of
    them will have the same style and shape."""

    reg = get_module_registry()
    reg.add_module(module,
                   moduleRightFringe=[(0.0,0.0),(0.25,0.5),(0.0,1.0)],
                   moduleLeftFringe=[(0.0,0.0),(0.0,1.0)],
                   **kwargs)

#################################################################################

def initialize(*args,**keywords):
    reg = get_module_registry()

    registerControl(Fold, abstract=True)
    registerControl(FoldWithModule, abstract=True)
    registerControl(Map)
    registerControl(Filter)
    registerControl(Sum)
    registerControl(And)
    registerControl(Or)
    registerControl(If)
    registerControl(Default)
    registerControl(ExecuteInOrder)
    registerControl(While)
    registerControl(For)

    reg.add_output_port(Or, 'Result', (Boolean, ""))
    reg.add_output_port(And, 'Result', (Boolean, ""))

    reg.add_input_port(Fold, 'InputList', (List, ""))
    reg.add_output_port(Fold, 'Result', (Variant, ""))

    reg.add_input_port(FoldWithModule, 'FunctionPort', (Module, ""))
    reg.add_input_port(FoldWithModule, 'InputPort', (List, ""))
    reg.add_input_port(FoldWithModule, 'OutputPort', (String, ""))

    reg.add_output_port(Map, 'Result', (List, ""))

    reg.add_output_port(Filter, 'Result', (List, ""))

    reg.add_input_port(If, 'Condition', (Boolean, ""))
    reg.add_input_port(If, 'TruePort', (Module, ""))
    reg.add_input_port(If, 'FalsePort', (Module, ""))
    reg.add_input_port(If, 'TrueOutputPorts', (List, ""), optional=True)
    reg.add_input_port(If, 'FalseOutputPorts', (List, ""), optional=True)
    reg.add_output_port(If, 'Result', (Variant, ""))

    reg.add_input_port(Default, 'Input', (Variant, ""))
    reg.add_input_port(Default, 'Default', (Variant, ""))
    reg.add_output_port(Default, 'Result', (Variant, ""))

    reg.add_module(ElementwiseProduct)
    reg.add_input_port(ElementwiseProduct, 'List1', (List, ""))
    reg.add_input_port(ElementwiseProduct, 'List2', (List, ""))
    reg.add_input_port(ElementwiseProduct, 'NumericalProduct', (Boolean, ""),
                       optional=True, defaults="['True']")
    reg.add_output_port(ElementwiseProduct, 'Result', (List, ""))

    reg.add_module(Dot)
    reg.add_input_port(Dot, 'List1', (List, ""))
    reg.add_input_port(Dot, 'List2', (List, ""))
    reg.add_output_port(Dot, 'Result', (List, ""))

    reg.add_module(Cross)
    reg.add_input_port(Cross, 'List1', (List, ""))
    reg.add_input_port(Cross, 'List2', (List, ""))
    reg.add_output_port(Cross, 'Result', (List, ""))

    reg.add_module(CartesianProduct)
    reg.add_input_port(CartesianProduct, 'List1', (List, ""))
    reg.add_input_port(CartesianProduct, 'List2', (List, ""))
    reg.add_input_port(CartesianProduct, 'CombineTuple', (Boolean, ""),
                       optional=True, defaults="['True']")
    reg.add_output_port(CartesianProduct, 'Result', (List, ""))

    reg.add_input_port(ExecuteInOrder, 'module1', (Module, ""))
    reg.add_input_port(ExecuteInOrder, 'module2', (Module, ""))

    reg.add_input_port(While, 'FunctionPort', (Module, ""))
    reg.add_input_port(While, 'OutputPort', (String, ""),
                       optional=True, defaults="['self']")
    reg.add_input_port(While, 'ConditionPort', (String, ""))
    reg.add_input_port(While, 'StateInputPorts', (List, ""),
                       optional=True)
    reg.add_input_port(While, 'StateOutputPorts', (List, ""),
                       optional=True)
    reg.add_input_port(While, 'MaxIterations', (Integer, ""),
                       optional=True, defaults="['20']")
    reg.add_input_port(While, 'Delay', (Float, ""),
                       optional=True)
    reg.add_output_port(While, 'Result', (Variant, ""))

    reg.add_input_port(For, 'FunctionPort', (Module, ""))
    reg.add_input_port(For, 'InputPort', (String, ""),
                       optional=True)
    reg.add_input_port(For, 'OutputPort', (String, ""),
                       optional=True, defaults="['self']")
    reg.add_input_port(For, 'LowerBound', (Integer, ""),
                       optional=True, defaults="['0']")
    reg.add_input_port(For, 'HigherBound', (Integer, ""))
    reg.add_output_port(For, 'Result', (List, ""))

def handle_module_upgrade_request(controller, module_id, pipeline):
    reg = get_module_registry()

    # Product modules had a CombineTuple port, which has been replaced with
    # NumericalProduct, with the opposite meaning
    def product_change_connection(old_conn, new_module):
        src_module = pipeline.modules[old_conn.source.moduleId]
        new_x = (src_module.location.x + new_module.location.x) / 2.0
        new_y = (src_module.location.y + new_module.location.y) / 2.0
        Not_desc = reg.get_descriptor(Not)
        not_mod = controller.create_module_from_descriptor(Not_desc,
                                                           new_x, new_y)
        conn1 = UpgradeWorkflowHandler.create_new_connection(
                controller,
                src_module, old_conn.source,
                not_mod, 'input')
        conn2 = UpgradeWorkflowHandler.create_new_connection(
                controller,
                not_mod, 'value',
                new_module, 'NumericalProduct')
        return [('add', not_mod), ('add', conn1), ('add', conn2)]
    def product_change_function(function, new_module):
        parameter = function.parameters[0]
        if parameter.value():
            value = 'False'
        else:
            value = 'True'
        return controller.update_function_ops(
                new_module, 'NumericalProduct',
                [value])

    module_remap = {
            'ListOfElements': [
                # Any 'ListOfElements' before 0.2.2 gets replaced with List
                (None, '0.2.2', List, {}),
            ],
            'Dot': [
                # The Dot module in 0.2.1 was in fact ElementwiseProduct
                (None, '0.2.2', ElementwiseProduct, {
                    'dst_port_remap': {
                        'List_1': 'List1',
                        'List_2': 'List2',
                        'CombineTuple': product_change_connection,
                    },
                    'function_remap': {
                        'CombineTuple': product_change_function,
                    },
                }),
            ],
            'Cross': [
                (None, '0.2.2', CartesianProduct, {
                    'dst_port_remap': {
                        'List_1': 'List1',
                        'List_2': 'List2',
                    },
                }),
            ],
            'Map': [
                (None, '0.2.4', None, {
                    'src_port_remap': {'Result': 'Result'}
                }),
            ],
            'Filter': [
                (None, '0.2.4', None, {
                    'src_port_remap': {'Result': 'Result'}
                }),
            ],
        }

    return UpgradeWorkflowHandler.remap_module(controller,
                                               module_id,
                                               pipeline,
                                               module_remap)
