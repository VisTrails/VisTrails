############################################################################
##
## Copyright (C) 2006-2007 University of Utah. All rights reserved.
##
## This file is part of VisTrails.
##
## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of
## this file.  Please review the following to ensure GNU General Public
## Licensing requirements will be met:
## http://www.opensource.org/licenses/gpl-license.php
##
## If you are unsure which license is appropriate for your use (for
## instance, you are interested in developing a commercial derivative
## of VisTrails), please contact us at vistrails@sci.utah.edu.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################

from core.data_structures import Graph
from core.utils import expression
from core.utils import trace_method
import copy
import parser

##############################################################################

class BaseInterpreter(object):

    def getNameDependencies(self, astList):
        """getNameDependencies(astList) -> list of something 
        
        """
        
        result = []
        if astList[0]==1: # NAME token
            result += [astList[1]]
        else:
            for e in astList:
                if type(e) is ListType:
                    result += self.getNameDependencies(e)
        return result

    def buildAliasDictionary(self, pipeline):
        aliases = {}
        for mid in pipeline.modules:
            for f in pipeline.modules[mid].functions:
                fsig = f.getSignature()
                for pidx in range(len(f.params)):
                    palias = f.params[pidx].alias
                    if palias and palias!='':
                        for f1 in reversed(pipeline.modules[mid].functions):
                            if f1.getSignature()==fsig:
                                p = f1.params[pidx]
                                aliases[palias] = (p.type, expression.parseExpression(str(p.strValue)))
                                break
        return aliases

    def compute_evaluation_order(self, aliases):
        dp = Graph()
        for alias,(atype,(base,exp)) in aliases.iteritems():
            dp.addVertex(alias)
            for e in exp:
                astList = parser.expr(e[1]).tolist()
                for edge in self.getNameDependencies(astList):
                    dp.addEdge(alias, edge)
        return dp.vertices_topological_sort()

    def computeEvaluationOrder(self, aliases):
        # Build the dependencies graph
        dp = {}
        for alias,(atype,(base,exp)) in aliases.items():
            edges = []
            for e in exp:
                edges += self.getNameDependencies()
            dp[alias] = edges
            
        # Topological Sort to find the order to compute aliases
        # Just a slow implementation, O(n^3)...
        unordered = copy.copy(list(aliases.keys()))
        ordered = []
        while unordered:
            added = []
            for i in range(len(unordered)):
                ok = True
                u = unordered[i]
                for j in range(len(unordered)):
                    if i!=j:
                        for v in dp[unordered[j]]:
                            if u==v:
                                ok = False
                                break
                        if not ok: break
                if ok: added.append(i)
            if not added:
                print 'Looping dependencies detected!'
                break
            for i in reversed(added):
                ordered.append(unordered[i])
                del unordered[i]
        return ordered

    def evaluateExp(self, atype, base, exps, aliases):
        import datetime        
        for e in exps: base = (base[:e[0]] +
                               str(eval(e[1],
                                        {'datetime':locals()['datetime']},
                                        aliases)) +
                               base[e[0]:])
        if not atype in ['string', 'String']:
            if base=='':
                base = '0'
            base = eval(base,None,None)
        return base

    def resolveAliases(self, pipeline,
                       customAliases=None):
        # Compute the 'locals' dictionary by evaluating named expressions
        if not customAliases:
            aliases = self.buildAliasDictionary(pipeline)
        else:
            aliases = copy.copy(customAliases)
        ordered = self.computeEvaluationOrder(aliases)
        casting = {'int': int, 'float': float, 'double': float, 'string': str,
                   'Integer': int, 'Float': float, 'String': str}
        for alias in reversed(ordered):
            (atype,(base,exps)) = aliases[alias]
            value = self.evaluateExp(atype,base,exps,aliases)
            aliases[alias] = casting[atype](value)

        for mid in pipeline.modules:
            for f in pipeline.modules[mid].functions:
                for p in f.params:
                    if p.alias and p.alias!='':
                        p.evaluatedStrValue = str(aliases[p.alias])
                    else:
                        (base,exps) = expression.parseExpression(
                            str(p.strValue))
                        p.evaluatedStrValue = str(
                            self.evaluateExp(p.type,base,exps,aliases))
        return aliases
    

##############################################################################
