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

from core.data_structures.graph import Graph
from core.utils import expression
from core.utils import trace_method
from core import debug
import copy
import parser

##############################################################################

class InternalTuple(object):
    """Tuple used internally for constant tuples."""

    def _get_length(self, length):
        return len(self._values)
    def _set_length(self, length):
        self._values = [None] * length
    length = property(_get_length, _set_length)

    def compute(self):
        return

    def set_input_port(self, index, connector):
        self._values[index] = connector()

    def get_output(self, port):
        return tuple(self._values)

    def update(self):
        pass
        

##############################################################################

class BaseInterpreter(object):

    def __init__(self):
        """ BaseInterpreter() -> BaseInterpreter
        Initialize class members
        
        """
        self.done_summon_hook = None
        self.done_update_hook = None

    def get_name_dependencies(self, astList):
        """get_name_dependencies(astList) -> list of something 
        
        """
        
        result = []
        if astList[0]==1: # NAME token
            result += [astList[1]]
        else:
            for e in astList:
                if type(e) is ListType:
                    result += self.get_name_dependencies(e)
        return result

#    def build_alias_dictionary(self, pipeline):
#        aliases = {}
#        for mid in pipeline.modules:
#            for f in pipeline.modules[mid].functions:
#                fsig = f.getSignature()
#                for pidx in xrange(len(f.params)):
#                    palias = f.params[pidx].alias
#                    if palias and palias!='':
#                        for f1 in reversed(pipeline.modules[mid].functions):
#                            if f1.getSignature()==fsig:
#                                p = f1.params[pidx]
#                                aliases[palias] = (p.type, expression.parse_expression(str(p.strValue)))
#                                break
#        return aliases

    def compute_evaluation_order(self, aliases):
        # Build the dependencies graph
        dp = {}
        for alias,(atype,(base,exp)) in aliases.items():
            edges = []
            for e in exp:
                edges += self.get_name_dependencies()
            dp[alias] = edges
            
        # Topological Sort to find the order to compute aliases
        # Just a slow implementation, O(n^3)...
        unordered = copy.copy(list(aliases.keys()))
        ordered = []
        while unordered:
            added = []
            for i in xrange(len(unordered)):
                ok = True
                u = unordered[i]
                for j in xrange(len(unordered)):
                    if i!=j:
                        for v in dp[unordered[j]]:
                            if u==v:
                                ok = False
                                break
                        if not ok: break
                if ok: added.append(i)
            if not added:
                debug.warning('Looping dependencies detected!')
                break
            for i in reversed(added):
                ordered.append(unordered[i])
                del unordered[i]
        return ordered

    def evaluate_exp(self, atype, base, exps, aliases):
        # FIXME: eval should pretty much never be used
        import datetime        
        for e in exps: base = (base[:e[0]] +
                               str(eval(e[1],
                                        {'datetime':locals()['datetime']},
                                        aliases)) +
                               base[e[0]:])
        if not atype in ['string', 'String']:
            if base=='':
                base = '0'
            try:
                base = eval(base,None,None)
            except:
                pass
        return base

    def resolve_aliases(self, pipeline,
                        customAliases=None):
        # We don't build the alias dictionary anymore because as we don't 
        # perform expression evaluation anymore, the values won't change.
        # We only care for custom aliases because they might have a value 
        # different from what it's stored.
        
        aliases = {}
        if customAliases:
            #customAliases can be only a subset of the aliases
            #so we need to build the Alias Dictionary always
            for k,v in customAliases.iteritems():
                aliases[k] = v
            # no support for expression evaluation. The code that does that is
            # ugly and dangerous.
#        ordered = self.compute_evaluation_order(aliases)
#        casting = {'int': int, 'float': float, 'double': float, 'string': str,
#                   'Integer': int, 'Float': float, 'String': str}
#        for alias in reversed(ordered):
#            (atype,base) = aliases[alias]
#            #no expression evaluation anymore
#            aliases[alias] = base
#            #value = self.evaluate_exp(atype,base,exps,aliases)
#            #aliases[alias] = value
        for alias in aliases:
            try:
                info = pipeline.aliases[alias]
                param = pipeline.db_get_object(info[0],info[1])
                param.strValue = str(aliases[alias])
            except KeyError:
                pass
                    
        return aliases
    
    def update_params(self, pipeline,
                        customParams=None):
        """update_params(pipeline: Pipeline, 
                         customParams=[(vttype, oId, strval)] -> None
        This will set the new parameter values in the pipeline before
        execution 
        
        """
        if customParams:
            for (vttype, oId, strval) in customParams:
                try:
                    param = pipeline.db_get_object(vttype,oId)
                    param.strValue = str(strval)
                except Exception, e:
                    debug.debug("Problem when updating params: %s"%str(e))

    def resolve_variables(self, controller, pipeline):
        #FIXME: This could be faster if we index variables by uuid.  Workaround could be constructing reverse dictionary.
        vars = controller.get_vistrail_variables()
        var_modules = [m for m in pipeline.module_list if m.has_annotation_with_key('__vistrail_var__')]
        for var_mod in var_modules:
            uuid = var_mod.get_annotation_by_key('__vistrail_var__').value
            strValue = [var_strValue for var_uuid, descriptor_info, var_strValue in vars.itervalues() if var_uuid == uuid][0]
            for func in var_mod.functions:
                if func.name == 'value':
                    func.params[0].strValue = strValue

    def set_done_summon_hook(self, hook):
        """ set_done_summon_hook(hook: function(pipeline, objects)) -> None
        Assign a function to call right after every objects has been
        summoned during execution
        
        """
        self.done_summon_hook = hook

    def set_done_update_hook(self, hook):
        """ set_done_update_hook(hook: function(pipeline, objects)) -> None
        Assign a function to call right after every objects has been
        updated
        
        """
        self.done_update_hook = hook

##############################################################################
