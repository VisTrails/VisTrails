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
from core import query
from core.modules.module_registry import get_module_registry
from core.utils import append_to_dict_of_lists
import copy
import re

################################################################################

class VisualQuery(query.Query):

    def __init__(self, pipeline, versions_to_check):
        self.queryPipeline = copy.copy(pipeline)
        self.versions_to_check = versions_to_check

    def heuristicDAGIsomorphism(self,
                                target, template,
                                target_ids, template_ids):
        resultIds = set()
        while 1:
            templateNames = set([(i, template.modules[i].name)
                                 for i in template_ids])
            targetNames = {}
            for i in target_ids:
                append_to_dict_of_lists(targetNames, target.modules[i].name, i)

            nextTargetIds = set()
            nextTemplateIds = set()

            for (i, templateName) in templateNames:
                if templateName not in targetNames:
                    return (False, resultIds)
                else:
                    templateModule = template.modules[i]
                    matched = [tId
                               for tId in targetNames[templateName]
                               if self.matchQueryModule(target.modules[tId],
                                                        templateModule)]
                    resultIds.update(matched)
                    for matchedTargetId in matched:
                        nextTargetIds.update([moduleId for
                                              (moduleId, edgeId) in
                                              target.graph.edges_from(matchedTargetId)])
                    nextTemplateIds.update([moduleId for
                                            (moduleId, edgeId) in
                                            template.graph.edges_from(i)])

            if not len(nextTemplateIds):
                return (True, resultIds)

            target_ids = nextTargetIds
            template_ids = nextTemplateIds

    def run(self, vistrail, name):
        result = []
        self.tupleLength = 2
        for version in self.versions_to_check:
            p = vistrail.getPipeline(version)
            matches = set()
            queryModuleNameIndex = {}
            for moduleId, module in p.modules.iteritems():
                append_to_dict_of_lists(queryModuleNameIndex, module.name, moduleId)
            for querySourceId in self.queryPipeline.graph.sources():
                querySourceName = self.queryPipeline.modules[querySourceId].name
                if not queryModuleNameIndex.has_key(querySourceName):
                    # need to reset matches here!
                    matches = set()
                    continue
                candidates = queryModuleNameIndex[querySourceName]
                atLeastOneMatch = False
                for candidateSourceId in candidates:
                    querySource = self.queryPipeline.modules[querySourceId]
                    candidateSource = p.modules[candidateSourceId]
                    if not self.matchQueryModule(candidateSource,
                                                 querySource):
                        continue
                    (match, targetIds) = self.heuristicDAGIsomorphism \
                                             (template = self.queryPipeline, 
                                              target = p,
                                              template_ids = [querySourceId],
                                              target_ids = [candidateSourceId])
                    if match:
                        atLeastOneMatch = True
                        matches.update(targetIds)
                        
                # We always perform AND operation
                if not atLeastOneMatch:
                    matches = set()
                    break
                
            for m in matches:
                result.append((version, m))
        self.queryResult = result
        self.computeIndices()
        return result
                
    def __call__(self):
        """Returns a copy of itself. This needs to be implemented so that
        a visualquery object looks like a class that can be instantiated
        once per vistrail."""
        return VisualQuery(self.queryPipeline)

    def matchQueryModule(self, template, target):
        """ matchQueryModule(template, target: Module) -> bool        
        Return true if the target module can be matched to the
        template module
        
        """
        if target.name != template.name:
            return False
        if target.getNumFunctions()>template.getNumFunctions():
            return False
        candidateFunctions = {}
        for fid in xrange(template.getNumFunctions()):
            f = template.functions[fid]
            append_to_dict_of_lists(candidateFunctions, f.name, f)

        for f in target.functions:
            if f.name not in candidateFunctions:
                return False
            fNotMatch = True
            candidates = candidateFunctions[f.name]
            for cf in candidates:
                if len(cf.params)!=len(f.params):
                    continue
                pMatch = True
                for pid in xrange(len(cf.params)):
                    cp = cf.params[pid]
                    p = f.params[pid]                    
                    if not self.matchQueryParam(p, cp):
                        pMatch = False
                        break
                if pMatch:
                    fNotMatch = False
                    break
            if fNotMatch:
                return False
        return True

    def matchQueryParam(self, template, target):
        """ matchQueryParam(template: Param, target: Param) -> bool
        Check to see if target can match with a query template
        
        """
        if (template.type != target.type or
            template.identifier != target.identifier or 
            template.namespace != target.namespace):
            return False
        
        reg = get_module_registry()
        desc = reg.get_descriptor_by_name(template.identifier, template.type,
                                          template.namespace)
        return desc.module.query_compute(target.strValue, template.strValue,
                                         template.queryMethod)

        # if template.type=='String':
        #     op = template.queryMethod/2
        #     caseInsensitive = template.queryMethod%2==0
        #     templateStr = template.strValue
        #     targetStr = target.strValue
        #     if caseInsensitive:
        #         templateStr = templateStr.lower()
        #         targetStr = targetStr.lower()

        #     if op==0:
        #         return templateStr in targetStr
        #     if op==1:
        #         return templateStr==targetStr
        #     if op==2:
        #         try:
        #             mo = re.match(templateStr, targetStr)
        #             if mo!=None:
        #                 return mo.end()==len(targetStr)
        #             else:
        #                 return False
        #         except:
        #             return False
        # else:
        #     # FIXME: eval should pretty much never be used
        #     if template.strValue.strip()=='':
        #         return True
        #     realTypeDict = {'Integer': int, 'Float': float}
        #     realType = realTypeDict[template.type]
        #     try:
        #         return realType(template.strValue)==realType(target.strValue)
        #     except: # not a constant
        #         try:
        #             return bool(eval(target.strValue+' '+template.strValue))
        #         except: # not a '<', '>', or '==' expression
        #             try:
        #                 s = template.strValue.replace(' ', '')
        #                 if s[0]=='(':
        #                     mid1 = '<%s)' % target.strValue
        #                 if s[0]=='[':
        #                     mid1 = '<=%s)' % target.strValue
        #                 if s[-1]==')':
        #                     mid2 = '(%s<' % target.strValue
        #                 if s[-1]==']':
        #                     mid2 = '(%s<=' % target.strValue
                            
        #                 s = s.replace(',', '%s and %s' % (mid1, mid2))
        #                 s = '(' + s[1:-1] + ')'
        #                 return eval(s)
        #             except:
        #                 print 'Invalid query "%s".' % template.strValue
        #                 return False
