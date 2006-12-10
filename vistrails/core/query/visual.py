from core import query
from core.utils import appendToDictOfLists
import copy

################################################################################

class VisualQuery(query.Query):

    def __init__(self, pipeline):
        self.queryPipeline = copy.copy(pipeline)

    def heuristicDAGIsomorphism(self,
                                target, template,
                                target_ids, template_ids):
        resultIds = set()
        while 1:
#            print "round starting", target, template, target_ids, template_ids
            templateNames = set([(i, template.modules[i].name)
                                 for i in template_ids])
            targetNames = {}
            for i in target_ids:
                appendToDictOfLists(targetNames, target.modules[i].name, i)

            nextTargetIds = set()
            nextTemplateIds = set()

            for (i, templateName) in templateNames:
                if templateName not in targetNames:
#                    print "Template",templateName,"is not in",targetNames
                    return (False, resultIds)
                else:
                    resultIds.update(targetNames[templateName])
                    for matchedTargetId in targetNames[templateName]:
                        nextTargetIds.update([moduleId for
                                              (moduleId, edgeId) in
                                              target.graph.edgesFrom(matchedTargetId)])
                    nextTemplateIds.update([moduleId for
                                            (moduleId, edgeId) in
                                            template.graph.edgesFrom(i)])

            if not len(nextTemplateIds):
#                print "No more templates to be matched, ok!"
                return (True, resultIds)

            target_ids = nextTargetIds
            template_ids = nextTemplateIds

    def run(self, vistrail, name):
        result = []
        self.tupleLength = 2
        versions = vistrail.tagMap.values()
        for version in versions:
            p = vistrail.getPipeline(version)
            matches = set()
            queryModuleNameIndex = {}
            for moduleId, module in p.modules.iteritems():
                appendToDictOfLists(queryModuleNameIndex, module.name, moduleId)
            for querySourceId in self.queryPipeline.graph.sources():
                querySourceName = self.queryPipeline.modules[querySourceId].name
                if not queryModuleNameIndex.has_key(querySourceName):
                    continue
                candidates = queryModuleNameIndex[querySourceName]
                for candidateSourceId in candidates:
#                    print querySourceName
#                    print p.modules[candidateSourceId].name
                    (match, targetIds) = self.heuristicDAGIsomorphism \
                                             (template = self.queryPipeline, 
                                              target = p,
                                              template_ids = [querySourceId],
                                              target_ids = [candidateSourceId])
                    if match:
                        matches.update(targetIds)
#                        print matches
            for m in matches:
                result.append((version, m))
        self.queryResult = result
#        print result
        self.computeIndices()
        return result
                
    def __call__(self):
        """Returns a copy of itself. This needs to be implemented so that
        a visualquery object looks like a class that can be instantiated
        once per vistrail."""
        return VisualQuery(self.queryPipeline)
