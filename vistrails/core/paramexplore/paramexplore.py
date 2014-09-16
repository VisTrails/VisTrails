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
""" This file contains the definition of the class ParameterExploration """

from xml.sax.saxutils import unescape

import vistrails.core.db.action

from vistrails.db.domain import DBParameterExploration, IdScope
from vistrails.core.paramexplore.function import PEFunction
from vistrails.core.vistrail.module_function import ModuleFunction
from vistrails.core.vistrail.module_param import ModuleParam
from vistrails.core.vistrail.module import Module
from vistrails.core.modules.paramexplore import IntegerLinearInterpolator, \
   FloatLinearInterpolator, RGBColorInterpolator, HSVColorInterpolator,\
   UserDefinedFunctionInterpolator

from ast import literal_eval
import unittest
import copy

###############################################################################

class ParameterExploration(DBParameterExploration):
    """ParameterExploration

    """

    def __init__(self, *args, **kwargs):
        DBParameterExploration.__init__(self, *args, **kwargs)

        self.set_defaults()

    def __copy__(self):
        """ __copy__() -> ParameterExploration - Returns a clone of itself """
        return ParameterExploration.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBParameterExploration.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = ParameterExploration
        cp.set_defaults(self)
        return cp

    def set_defaults(self, other=None):
        if other is None:
            self.changed = False
        else:
            self.changed = other.changed

    @staticmethod
    def convert(_parameter_exploration):
        _parameter_exploration.__class__ = ParameterExploration

        for function in _parameter_exploration.db_functions:
            PEFunction.convert(function)

        _parameter_exploration.set_defaults()

    ##########################################################################
    # Properties

    id = DBParameterExploration.db_id
    action_id = DBParameterExploration.db_action_id
    user = DBParameterExploration.db_user
    date = DBParameterExploration.db_date
    _dims = DBParameterExploration.db_dims
    _layout = DBParameterExploration.db_layout
    name = DBParameterExploration.db_name
    functions = DBParameterExploration.db_functions
    
    def get_dims(self):
        try:
            return literal_eval(self._dims)
        except Exception:
            return []
    def set_dims(self, d):
        try:
            _dims = repr(d)
        except Exception:
            _dims = []
    dims = property(get_dims, set_dims)

    def get_layout(self):
        try:
            return literal_eval(self._layout)
        except Exception:
            return {}
    def set_layout(self, l):
        try:
            _layout = repr(l)
        except Exception:
            _layout = '{}'
    layout = property(get_layout, set_layout)

    def collectParameterActions(self, pipeline):
        """ collectParameterActions() -> list
        Return a list of action lists corresponding to each dimension
        
        """
        if not pipeline:
            return
        unescape_dict = { "&apos;":"'", '&quot;':'"', '&#xa;':'\n' }
        from vistrails.core.modules.module_registry import get_module_registry
        reg = get_module_registry()
        parameterValues = [[], [], [], []]
        # a list of added functions [(module_id, function_name)] = function
        added_functions = {}
        vistrail_vars = []
        function_actions = []
        for i in xrange(len(self.functions)):
            pe_function = self.functions[i]
            module = pipeline.db_get_object(Module.vtType, pe_function.module_id)
            # collect overridden vistrail vars
            if module.is_vistrail_var():
                vistrail_vars.append(module.get_vistrail_var())
            port_spec = reg.get_input_port_spec(module, pe_function.port_name)
            tmp_f_id = -1L
            tmp_p_id = -1L
            for param in pe_function.parameters:
                port_spec_item = port_spec.port_spec_items[param.pos]
                dim = param.dimension
                if dim not in [0, 1, 2, 3]:
                    continue
                count = self.dims[dim]
                # find interpolator values
                values = []
                text = '%s' % unescape(param.value, unescape_dict)
                if param.interpolator == 'Linear Interpolation':
                    # need to figure out type
                    if port_spec_item.module == "Integer":
                        i_range = literal_eval(text)
                        p_min = int(i_range[0])
                        p_max =int(i_range[1])
                        values = IntegerLinearInterpolator(p_min, p_max,
                                                     count).get_values()
                    if port_spec_item.module == "Float":
                        i_range = literal_eval(text)
                        p_min = float(i_range[0])
                        p_max =float(i_range[1])
                        values = FloatLinearInterpolator(p_min, p_max,
                                                     count).get_values()
                elif param.interpolator == 'RGB Interpolation':
                    i_range = literal_eval(text)
                    p_min = str(i_range[0])
                    p_max =str(i_range[1])
                    values = RGBColorInterpolator(p_min, p_max,
                                                     count).get_values()
                elif param.interpolator == 'HSV Interpolation':
                    i_range = literal_eval(text)
                    p_min = str(i_range[0])
                    p_max =str(i_range[1])
                    values = HSVColorInterpolator(p_min, p_max,
                                                     count).get_values()
                elif param.interpolator == 'List':
                    p_module = port_spec_item.descriptor.module
                    values = [p_module.translate_to_python(m)
                              for m in literal_eval(text)]
                elif param.interpolator == 'User-defined Function':
                    p_module = port_spec_item.descriptor.module
                    values = UserDefinedFunctionInterpolator(p_module,
                            text, count).get_values()
                if not values:
                    return None
                # find parameter or create one
                function = [f for f in module.functions
                            if f.name == port_spec.name]
                if function:
                    function = function[0]
                else:
                    try:
                        function = added_functions[(module.id,port_spec.name)]
                    except KeyError:
                        # add to function list
                        params = []
                        for psi in port_spec.port_spec_items:
                            parameter = ModuleParam(id=tmp_p_id,
                                        pos=psi.pos,
                                        name='<no description>',
                                        val=psi.default,
                                        type=psi.descriptor.sigstring) 
                            params.append(parameter)
                            tmp_p_id -= 1
                        function = ModuleFunction(id=tmp_f_id,
                                                  pos=module.getNumFunctions(),
                                                  name=port_spec.name,
                                                  parameters=params)
                        tmp_f_id -= 1
                        added_functions[(module.id, port_spec.name)]=function 
                        action = vistrails.core.db.action.create_action([('add',
                                                                function,
                                                                module.vtType,
                                                                module.id)])
                        function_actions.append(action)
                parameter = function.params[port_spec_item.pos]
                # find old parameter
                old_param = parameter
                actions = []
                for v in values:
                    desc = port_spec_item.descriptor
                    if not isinstance(v, str):
                        str_value = desc.module.translate_to_string(v)
                    else:
                        str_value = v
                    new_param = ModuleParam(id=tmp_p_id,
                                            pos=old_param.pos,
                                            name=old_param.name,
                                            alias=old_param.alias,
                                            val=str_value,
                                            type=old_param.type)
                    tmp_p_id -= 1
                    action_spec = ('change', old_param, new_param,
                                   function.vtType, function.real_id)
                    action = vistrails.core.db.action.create_action([action_spec])
                    actions.append(action)
                parameterValues[dim].append(actions)
        return [zip(*p) for p in parameterValues], function_actions, vistrail_vars

    def __eq__(self, other):
        """ __eq__(other: ParameterExploration) -> boolean
        Returns True if self and other have the same attributes. Used by == 
        operator. 
        
        """
        if type(self) != type(other):
            return False
        if self.action_id != other.action_id:
            return False
        if self._dims != other._dims:
            return False
        if self._layout != other._layout:
            return False
        if len(self.functions) != len(other.functions):
            return False
        for p,q in zip(self.functions, other.functions):
            if p != q:
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

# Testing


class TestParameterExploration(unittest.TestCase):

    def create_pe(self, id_scope=IdScope()):
        pe = ParameterExploration(
                            id=id_scope.getNewId(ParameterExploration.vtType),
                            action_id=6,
                            user='tommy',
                            date='2007-11-23 12:48',
                            dims='[1,2]',
                            layout='{1:"normal"}',
                            name='test-pe',
                            functions=[])
        return pe

    def test_copy(self):        
        id_scope = IdScope()
        pe1 = self.create_pe(id_scope)
        pe2 = copy.copy(pe1)
        self.assertEquals(pe1, pe2)
        self.assertEquals(pe1.id, pe2.id)
        pe3 = pe1.do_copy(True, id_scope, {})
        self.assertEquals(pe1, pe3)
        self.assertNotEquals(pe1.id, pe3.id)

    def testComparisonOperators(self):
        """ Test comparison operators """
        p = self.create_pe()
        q = self.create_pe()
        self.assertEqual(p, q)
        q.action_id = 8
        self.assertNotEqual(p, q)
        q.action_id = 6
        q._dims = '[1,4]'
        self.assertNotEqual(p, q)
        q._dims = '[1,2]'
        q._layout = '{1:"different"}'
        self.assertNotEqual(p, q)
        q._layout = p._layout
        q.functions = [1]
        self.assertNotEqual(p, q)

if __name__ == '__main__':
    unittest.main()
