from core.vis_pipeline import *
import sys
import copy

class EnsemblePipelines(object):
    def __init__(self, pipelines=None):
        if pipelines == None:
            self.pipelines = []
            self.sources = []
        else:
            self.pipelines = copy.copy(pipelines)
        self.aliases = {}

    def update(self, name, value):
        """Propogates changes of a shared aliased variable through
        a list of pipelines

        name - the name of the variable and key into the alias dictionary
        value - the new value of the variable
        returns - void
        """
        self.assembleCommonAliases() #self.aliases contains only common aliases
        changeParameter(self.aliases, name, value)
        for i in range(0,len(self.pipelines)):
            a = self.pipelines[i].buildAliasDictionary()
            changeParameter(a, name, value)
            self.pipelines[i].resolveAliases(a)
            for pa in a:
                if pa in self.sources.keys():
                    for (pi, mid, f, pidx) in self.sources[pa]:
                        if pi == i:
                            f = self.pipelines[i].modules[mid].functions[f]
                            f.params[pidx].strValue = a[pa][1][0]
            
    def assembleCommonAliases(self):
        """Generate a list of all common aliases across the pipelines
        in self.pipelines, which is stored in self.aliases
        Also, for each key in self.aliases, self.sources has the same key,
        mapped to a tuple of the type (p, m, f, pa)
        where p is the index of the pipeline in self.pipelines, m is the
        index of the module, f of the function, and pa of the parameter
        
        Returns
        -------
        'Dictionary'

        """
        common = {}
        sources = {}
        notcommon = []
        for pi in range(len(self.pipelines)):
            from gui.qmodulefunctiongroupbox import QPythonValueLineEdit
            for mid in self.pipelines[pi].modules:
                for fidx in range(len(self.pipelines[pi].modules[mid].functions)):
                    f = self.pipelines[pi].modules[mid].functions[fidx]
                    fsig = f.getSignature()
                    for pidx in range(len(f.params)):
                        palias = f.params[pidx].alias
                        if palias and palias!='':
                            functs = self.pipelines[pi].modules[mid].functions
                            for f1 in reversed(functs):
                                if f1.getSignature()==fsig:
                                    p = f1.params[pidx]
                                    if pi == 0:
                                        common[palias] = (p.type, QPythonValueLineEdit.parseExpression(str(p.strValue)))
                                        sources[palias]= [(pi, mid, fidx, pidx)]
                                    elif palias in common.keys():
                                        sources[palias].append((pi, mid, fidx, pidx))
                                    break            
        for p in self.pipelines:
            aliases = p.buildAliasDictionary().keys()
            for a in common.keys():
                if not a in aliases:
                    notcommon.append(a)
        for n in notcommon:
            if n in common.keys():
                del common[n]
            if n in sources.keys():
                del sources[n]
        self.sources = sources
        self.aliases = common
        return common

def changeParameter (aliasDic, name, value):
    """Changes a parameter in the aliasDic"""
    if aliasDic.has_key(name):
        prevKey = aliasDic[name]
        aliasDic[name] = (prevKey[0], (str(value), prevKey[1][1]))
    

