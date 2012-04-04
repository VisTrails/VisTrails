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

#!/usr/bin/python
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
import os
import sys
import urllib
import hashlib
import shutil
import subprocess

from lucene import FSDirectory, IndexWriter, StandardAnalyzer, initVM, CLASSPATH, Field, Document, Term, File

from vistrailanalyzer import vistrailAnalyzer
from __core import *
from spec_io import spec

lvm = initVM(CLASSPATH, maxheap='512m')

location = "/server/index"

class WorkflowIndexer:
    store = None
    writer = None
    def __init__(self):
        self.save = Field.Store.YES
        self.ddict = dict()

        lvm.attachCurrentThread()

        if not WorkflowIndexer.store and not WorkflowIndexer.writer:
            try:
                # open lucene index
                WorkflowIndexer.store = FSDirectory.open(File(location))
                # if the index directory does not exist, create it.
                WorkflowIndexer.writer = IndexWriter( WorkflowIndexer.store,
                    vistrailAnalyzer(), not len(WorkflowIndexer.store.list()))
            except Exception, e:
                print "EXCEPTION", e
                self.close()
                raise

    def close(self):
        if WorkflowIndexer.writer:
            WorkflowIndexer.writer.commit()

    def remove(self, id):
        print "removing index for", id
        spec.remove(id)
        # Delete old versions
        WorkflowIndexer.writer.deleteDocuments(
            [Term('workflow_id', id)] )
        print "done removing", id

    def index_vt_wf(self, wf_info, pipeline):
        # convert to general workflow model
        wf = self.convert_vt_wf(pipeline)
        wf.id = str(wf_info['crowdlabs_wf_id'])
        # add meta information
        wf.name = wf_info['name']
        wf.annotations.append(Annotation("title", wf_info['name']))
        wf.annotations.append(Annotation("user", wf_info['user']))
#value.strftime('%Y-%m-%d %H:%M:%S')
        wf.annotations.append(Annotation("date", wf_info['date']))
        wf.annotations.append(Annotation("note", wf_info['description']))
        if wf_info['thumbnail'] != '':
            wf.annotations.append(Annotation("__thumb__", wf_info['thumbnail']))
        return self.index_wf(wf)

    def index_wf(self, wf):
        # upload to database
        print "uploading", wf.name
        spec.add(wf)
        # index workflow using lucene
        print "indexing", wf.name
        self.write_index(wf)
        print "done indexing", wf.name

    #
    # Creates pickle workflow object from vistrails pipeline
    #
    def convert_vt_wf(self, wf):
        pipeline = Pipeline("", "vistrail", wf.db_version, "")

        # process modules
        mdict = {}
        for module in wf.db_modules:
            name = module.db_name
            for annotation in module.db_annotations:
                if annotation.db_key == "__desc__":
                    name = annotation.db_value
            m = Module(name, module.db_package, module.db_version, module.db_name)
            m.id = module.db_id
            mdict[m.id] = m
            pipeline.modules.append(m)

            # location x/y
            m.annotations.append(Annotation('loc_x', str(module.db_location.db_x)))
            m.annotations.append(Annotation('loc_y', str(module.db_location.db_y)))

            # add functions
            for function in module.db_functions:
                name = function.db_name
                for parameter in function.db_parameters:
                    value = urllib.unquote(parameter.db_val) # decode pythonsources
                    pos = str(parameter.db_pos)
                    name += ((':' + pos) if len(function.db_parameters)>1 else '')
                    m.parameters.append(Parameter(name, value, parameter.db_type))
                # empty parameter
                if len(function.db_parameters) == 0:
                    m.parameters.append(Parameter(name, '', ''))

        for connection in wf.db_connections:
            start = connection.db_get_port_by_type('source')
            startModuleId = start.db_moduleId
            end = connection.db_get_port_by_type('destination')
            endModuleId = end.db_moduleId

            # get the references
            startModule = mdict[startModuleId] if startModuleId in mdict else None
            endModule = mdict[endModuleId] if endModuleId in mdict else None

            if startModule and endModule:
                # redundant attribute: add a module chain for fast traversal
                if startModule not in endModule.up:
                    endModule.up.append(startModule)
                if endModule not in startModule.down:
                    startModule.down.append(endModule)
                pipeline.connections.append(Connection(startModule, endModule,
                                                   start.db_name, end.db_name))
            else:
                print "A broken connection was found"
        return pipeline

    def adddd(self, k, v):
        self.ddict[k] = self.ddict[k] + " " + v if self.ddict.has_key(k) else v

    def write_index(self, workflow, property = False):
        """
        adds all keywords in workflow to the index at the specified location
        types of the keywords can be preserved by setting (Property = True)
        """
        self.ddict = dict()
        # name is used as id in this case
        self.adddd("workflow_id", str(workflow.id))

        self.adddd("text", workflow.id)
        self.adddd("text", workflow.name)
        # this is a key for the workflow
        #adddd("workflow_source", workflow.source)
        #self.adddd("text", workflow.source)
        #adddd("workflow_type", workflow.type)
        self.adddd("text", workflow.type)
        # not very interesting
        #d.add( Field("workflow_version", workflow.version, save, Field.Index.UN_TOKENIZED))
        self.indexAnnotations(workflow.annotations, property)

        for module in workflow.modules:    
            self.adddd("module_name" if property else "text", module.name)
            self.adddd("package"     if property else "text", module.package)
            # not very interesting
            #d.add( Field("package_version", module.version, save, Field.Index.UN_TOKENIZED))
            self.adddd("module_type" if property else "text", module.type)
            self.indexAnnotations(module.annotations, property)
            for p in module.parameters:
                self.adddd("parameter_name" if property else "text", p.name)
                self.adddd("parameter_value" if property else "text", p.value)
                self.adddd("parameter_type" if property else "text", p.type)
                self.indexAnnotations(p.annotations, property)

        for c in workflow.connections:    
            self.adddd("port_name" if property else "text", c.startPort)
            self.adddd("port_name" if property else "text", c.endPort)
            self.indexAnnotations(c.annotations, property)

        d = Document()
        for (k, v) in self.ddict.iteritems():
            d.add(Field(k, v, self.save, Field.Index.TOKENIZED))

        # Delete old versions
        WorkflowIndexer.writer.deleteDocuments(
            [Term('workflow_id', str(workflow.id))] )
        # add new
        WorkflowIndexer.writer.addDocument(d)

    def indexAnnotations(self, annotations, p):
        """
        design choice: key and values are indexed separately,
        it would be possible to index them as the same type
    """
        for annotation in annotations:
            self.adddd("annotation_key" if p else "text", annotation.key)
            self.adddd("annotation_value" if p else "text", annotation.value)
            # annotations can be recursive
            self.indexAnnotations(annotation.annotations, p)
