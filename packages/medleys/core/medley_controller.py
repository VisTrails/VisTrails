############################################################################
##
## Copyright (C) 2006-2008 University of Utah. All rights reserved.
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
################################################################################
""" This file contains the MedleyController
     The MedleyController controls the communication to a medley

classes:
   MedleyController
   
"""
################################################################################

class WorkflowViewCollectionController(object):
    def __init__(self):
        """__init__() -> WorkflowViewCollectionController
        Creates WorkflowCollectionController
        """
        self.collection = BookmarkCollection()
        self.filename = ''
        self.pipelines = {}
        self.controllers = {}
        self.active_pipelines = []
        self.ensemble = EnsemblePipelines()
        self.loaded = False

#     def load_bookmarks(self):
#         """load_bookmarks() -> None
#         Load Bookmark collection and instantiate all pipelines

#         """

#         if os.path.exists(self.filename):
#             self.collection.parse(self.filename)
#             self.load_all_pipelines()
    def update(self):
        changed = self.parse_bookmarks()
        if changed:
            changed = self.load_pipelines()
        return changed

    def parse_bookmarks(self):
        """parse_bookmarks() -> Bool
        Load Bookmark collection without instantiating all pipelines

        """
        if not self.loaded:
            if os.path.exists(self.filename):
                self.collection.parse(self.filename)
            self.loaded = True
            return True
        return False

    def add_bookmark(self, parent, locator, pipeline, name=''):
        """add_bookmark(parent: int, locator: Locator, pipeline: int,
                       name: str) -> None
        creates a bookmark with the given information and adds it to the
        collection

        """
        id = self.collection.get_fresh_id()
        bookmark = Bookmark(parent, id, locator, pipeline, name,"item")
        self.collection.add_bookmark(bookmark)
        self.collection.serialize(self.filename)
        if not bookmark.error:
            self.load_pipeline(id)

    def remove_bookmark(self, id):
        """remove_bookmark(id: int) -> None
        Remove bookmark with id from the collection

        """
        bookmark = self.collection.bookmark_map[id]
        self.collection.remove_bookmark(id)
        if not bookmark.error:
            del self.pipelines[id]
            del self.ensemble.pipelines[id]
            if id in self.active_pipelines:
                del self.active_pipelines[id]
            if id in self.ensemble.active_pipelines:
                del self.ensemble.active_pipelines[id]
            self.ensemble.assemble_aliases()
        self.collection.serialize(self.filename)

    def update_alias(self, alias, value):
        """update_alias(alias: str, value: str) -> None
        Change the value of an alias and propagate changes in the pipelines

        """
        self.ensemble.update(alias,value)

    def reload_pipeline(self, id):
        """reload_pipeline(id: int) -> None
        Given a bookmark id, loads its original pipeline in the ensemble

        """
        if self.pipelines.has_key(id):
            self.ensemble.add_pipeline(id, self.pipelines[id])
            self.ensemble.assemble_aliases()

    def load_pipeline(self, id):
        """load_pipeline(id: int) -> None
        Given a bookmark id, loads its correspondent pipeline and include it in
        the ensemble

        """
        bookmark = self.collection.bookmark_map[id]
        v = bookmark.locator.load()
        if v.hasVersion(bookmark.pipeline):
            self.pipelines[id] = v.getPipeline(bookmark.pipeline)
            self.ensemble.add_pipeline(id, self.pipelines[id])
            self.ensemble.assemble_aliases()
        else:
            bookmark.error = BookmarkError(2,
                                           (bookmark.pipeline,
                                            bookmark.locator))

    def load_pipelines(self):
        """load_pipelines() -> Bool
        Loads bookmarks' pipelines if they aren't already loaded.
        It will return True if the state changed

        """
        result = False

        for id, bookmark in self.collection.bookmark_map.iteritems():
            if not self.pipelines.has_key(id):
                name = bookmark.locator.name
                if bookmark.locator and bookmark.locator.is_valid():
                    locstr = str(bookmark.locator)
                    if self.controllers.has_key(locstr):
                        v = self.controllers[locstr].vistrail
                    else:
                        try:
                            v = bookmark.locator.load()
                            c = VistrailController(v,False)
                            c.set_vistrail(v,bookmark.locator)
                            self.controllers[locstr] = c
                        except Exception, e:
                            bookmark.error = BookmarkError(3,(name,))

                    if v.hasVersion(bookmark.pipeline):
                        self.pipelines[id] = v.getPipeline(bookmark.pipeline)
                        self.ensemble.add_pipeline(id, self.pipelines[id])

                        result = True
                        bookmark.error = None
                    else:
                        bookmark.error = BookmarkError(2,
                                                       (bookmark.pipeline,
                                                        bookmark.locator.name))

                elif bookmark.locator:
                    if isinstance(bookmark.locator, DBLocator):
                        if not bookmark.locator.is_valid():
                            bookmark.error = BookmarkError(error_code = 4)
                        elif isinstance(bookmark.locator, FileLocator()):
                            bookmark.error = BookmarkError(1,(name,))
                else:
                    bookmark.error = BookmarkError(error_code = 0)
        if result:
            self.ensemble.assemble_aliases()
        return result

    def set_active_pipelines(self, ids):
        """ set_active_pipelines(ids: list) -> None
        updates the list of active pipelines

        """
        self.active_pipelines = ids
        self.ensemble.active_pipelines = ids
        self.ensemble.assemble_aliases()

    def write_bookmarks(self):
        """write_bookmarks() -> None - Write collection to disk."""
        self.collection.serialize(self.filename)

    def execute_workflows(self, ids):
        """execute_workflows(ids:list of Bookmark.id) -> None
        Execute the workflows bookmarked with the ids

        """
        view = DummyView()
        w_list = []
        for id in ids:
            bookmark = self.collection.bookmark_map[id]
            w_list.append((bookmark.locator,
                          bookmark.pipeline,
                          self.ensemble.pipelines[id],
                          view))

        self.execute_workflow_list(w_list)

    def execute_workflow_list(self, vistrails):
        """execute_workflow_list(vistrails: [(name, version,
                                            pipeline, view]) -> None
        Executes a list of pipelines, where:
         - name: str is the vistrails filename
         - version: int is the version number
         - pipeline: Pipeline object
         - view: interface to a QPipelineScene

        """
        interpreter = get_default_interpreter()
        for vis in vistrails:
            (locator, version, pipeline, view) = vis
            result = interpreter.execute(None,
                                         pipeline,
                                         locator,
                                         version,
                                         view)

    def parameter_exploration(self, ids, specs):
        """parameter_exploration(ids: list, specs: list) -> None
        Build parameter exploration in original format for each bookmark id.

        """
        view = DummyView()
        for id in ids:
            new_specs = []
            bookmark = self.collection.bookmark_map[id]
            new_specs = self.merge_parameters(id, specs)
            p = ParameterExploration(new_specs)
            pipeline_list = p.explore(self.ensemble.pipelines[id])
            vistrails = ()
            for pipeline in pipeline_list:
                vistrails += ((bookmark.locator.name,
                               bookmark.pipeline,
                               pipeline,
                               view),)
            self.execute_workflow_list(vistrails)

    def merge_parameters(self, id, specs):
        """merge_parameters(id: int, specs: list) -> list
        Identifies aliases in a common function and generates only one tuple
        for them

        """
        aliases = {}
        a_list = []
        for dim in xrange(len(specs)):
            specs_per_dim = specs[dim]
            for interpolator in specs_per_dim:
                #build alias dictionary
                 alias = interpolator[0]
                 info = self.ensemble.get_source(id,alias)
                 if info:
                     if aliases.has_key(alias):
                         aliases[alias].append((info,
                                                interpolator[2],
                                                interpolator[3],
                                                dim))
                     else:
                         aliases[alias] = [(info,
                                            interpolator[2],
                                            interpolator[3],
                                            dim)]
                     a_list.append((alias,info,
                                   interpolator[2],
                                   interpolator[3],
                                   dim))
        new_specs = []
        repeated = []
        new_specs_per_dim = {}
        for data in a_list:
            alias = data[0]
            if alias not in repeated:
                mId = data[1][0]
                fId = data[1][1]
                pId = data[1][2]
                common = {}
                common[pId] = alias
                for d in a_list:
                    a = d[0]
                    if a != alias:
                        if mId == d[1][0] and fId == d[1][1]:
                            #assuming that we cannot set the same parameter
                            #across the dimensions
                            common[d[1][2]] = a
                            repeated.append(a)
                pip = self.ensemble.pipelines[id]
                m = pip.get_module_by_id(mId)
                f = m.functions[fId]
                pCount = len(f.params)
                new_range = []
                for i in xrange(pCount):
                    if i not in common.keys():
                        p = f.params[i]
                        new_range.append((p.value(),p.value()))
                    else:
                        d_list = aliases[common[i]]
                        r = None
                        for d in d_list:
                            if d[0][2] == i:
                                r = d[1][0]
                        new_range.append(r)
                interpolator = InterpolateDiscreteParam(m,
                                                        f.name,
                                                        new_range,
                                                        data[3])
                if new_specs_per_dim.has_key(data[4]):
                    new_specs_per_dim[data[4]].append(interpolator)
                else:
                    new_specs_per_dim[data[4]] = [interpolator]
        for dim in sorted(new_specs_per_dim.keys()):
            l_inter = new_specs_per_dim[dim]
            l = []
            for inter in l_inter:
                l.append(inter)
            new_specs.append(l)
        return new_specs
