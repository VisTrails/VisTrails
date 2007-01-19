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
from core.utils import expression
import sys
import copy

class EnsemblePipelines(object):
    def __init__(self, pipelines=None):
        if pipelines == None:
            self.pipelines = {}
            self.sources = []
        else:
            self.pipelines = copy.copy(pipelines)
        self.aliases = {}

    def update(self, name, value):
        """update(nam: str, value: str) -> None
        Propagates changes of the value of an alias through a list of 
        pipelines

        name - the name of the variable and key into the alias dictionary
        value - the new value of the variable
        returns - void
        """
        self.changeParameter(name, value)
        for id,pipeline in self.pipelines.iteritems():
            for pa in self.aliases:
                if pa in self.sources.keys():
                    for (pi, mid, f, pidx) in self.sources[pa]:
                        if pi == id:
                            f = pipeline.modules[mid].functions[f]
                            f.params[pidx].strValue = self.aliases[pa][1][0]
            
    def assembleAliases(self):
        """assembleAliases() -> None
        Generate a list of all aliases across the pipelines
        in self.pipelines, which is stored in self.aliases
        Also, for each key in self.aliases, self.sources has the same key,
        mapped to a tuple of the type (p, m, f, pa)
        where p is the index of the pipeline in self.pipelines, m is the
        index of the module, f of the function, and pa of the parameter
         
        """
        union = {}
        sources = {}
        for pi,pipeline in self.pipelines.iteritems():
            modules = pipeline.modules
            for mid in modules:
                functions = modules[mid].functions
                for fidx in range(len(functions)):
                    f = functions[fidx]
                    fsig = f.getSignature()
                    for pidx in range(len(f.params)):
                        palias = f.params[pidx].alias
                        if palias and palias!='':
                            for f1 in reversed(functions):
                                if f1.getSignature()==fsig:
                                    p = f1.params[pidx]
                                    if not union.has_key(palias):
                                        value = str(p.strValue)
                                        e = expression.parseExpression(value)
                                        union[palias] = (p.type, e)
                                        sources[palias] = [(pi, mid, 
                                                            fidx, pidx)] 
                                    else:
                                        sources[palias].append((pi, mid, 
                                                                fidx, pidx))
                                    break            

        self.sources = sources
        self.aliases = union

    def changeParameter (self, name, value):
        """changeParameter(name:str, value:str) -> None
        Changes a parameter in the internal alias dictionary.
        In order to have the changes propagated in the pipelines, call 
        update(name,value) instead.
        
        """
        if self.aliases.has_key(name):
            info = self.aliases[name]
            #tuples don't allow changing in place
            self.aliases[name] = (info[0],(value,info[1][1]))
    

