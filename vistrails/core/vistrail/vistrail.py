###############################################################################
##
## Copyright (C) 2014-2016, New York University.
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
##  - Neither the name of the New York University nor the names of its
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
from __future__ import division

from vistrails.core.paramexplore.paramexplore import ParameterExploration

import copy
import datetime
import getpass

from vistrails.db.domain import DBVistrail
from vistrails.db.services.io import open_vt_log_from_db, open_log_from_xml
from vistrails.core.db.locator import DBLocator
from vistrails.core.log.log import Log
from vistrails.core.data_structures.graph import Graph
from vistrails.core.data_structures.bijectivedict import Bidict
from vistrails.core import debug
import vistrails.core.db.io
from vistrails.core.utils import VistrailsInternalError, \
     InvalidPipeline
from vistrails.core.vistrail.action import Action
from vistrails.core.vistrail.action_annotation import ActionAnnotation
from vistrails.core.vistrail.vistrailvariable import VistrailVariable
from vistrails.core.vistrail.annotation import Annotation
from vistrails.core.vistrail.connection import Connection
from vistrails.core.vistrail.location import Location
from vistrails.core.vistrail.module import Module
from vistrails.core.vistrail.module_function import ModuleFunction
from vistrails.core.vistrail.module_param import ModuleParam
from vistrails.core.vistrail.operation import AddOp, ChangeOp, DeleteOp
from vistrails.core.vistrail.plugin_data import PluginData
from vistrails.core.vistrail.port import Port

import unittest
import copy
import random

""" This file contains the definition of the class Vistrail """


################################################################################

class Vistrail(DBVistrail):
    """Vistrail is the base class for storing versioned pipelines.

    Because of the automatic loading from the db layer, the fields in
    the class will seem mysterious.

    self.currentVersion: version of the schema being used for this vistrail
    (Do not confuse with the currently selected version on the controller)

    self.actions: list of core/vistrail/action/Action objects

    self.actionMap: dictionary from version number to action object.

    Simple use cases:

    To get a version number given a tag name, use
    get_tag_str(tag_name).action_id

    """

    def __init__(self, locator=None):
        DBVistrail.__init__(self)

        self.set_defaults()
        self.locator = locator

    def __copy__(self):
        """ __copy__() -> Vistrail - Returns a clone of itself """ 
        return Vistrail.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBVistrail.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = Vistrail
        cp.locator = copy.copy(self.locator)
        cp.set_defaults(self)
        return cp

    def set_defaults(self, other=None):
        if other is None:
            self.changed = False
            self.currentVersion = -1
            self.savedQueries = []
            self.is_abstraction = False
            self.locator = None
            self.meta_vistrail = None
        else:
            self.changed = other.changed
            self.currentVersion = other.currentVersion
            self.savedQueries = copy.copy(other.savedQueries)
            self.is_abstraction = other.is_abstraction
            self.locator = other.locator
            self.meta_vistrail = other.meta_vistrail

        # object to keep explicit expanded 
        # version tree always updated
        self.tree = ExplicitExpandedVersionTree(self)
        # add all versions to the trees
        for action in sorted(self.actions, key=lambda a: a.id):
            self.tree.addVersion(action.id, action.prevId)

    @staticmethod
    def convert(_vistrail):
        _vistrail.__class__ = Vistrail

        for action in _vistrail.actions:
            Action.convert(action)
#        for tag in _vistrail.tags:
#            Tag.convert(tag)
        for annotation in _vistrail.annotations:
            Annotation.convert(annotation)
        for annotation in _vistrail.action_annotations:
            ActionAnnotation.convert(annotation)

        for variable in _vistrail.vistrail_variables:
            VistrailVariable.convert(variable)

        for pe in _vistrail.parameter_explorations:
            ParameterExploration.convert(pe)

        _vistrail.set_defaults()

    ##########################################################################
    # Constants

    TAG_ANNOTATION = '__tag__'
    NOTES_ANNOTATION = '__notes__'
    PARAMEXP_ANNOTATION = '__paramexp__'
    THUMBNAIL_ANNOTATION = '__thumb__'
    PRUNE_ANNOTATION = '__prune__'
    UPGRADE_ANNOTATION = '__upgrade__'
#    VARIABLES_ANNOTATION = '__vistrail_vars__'

    ##########################################################################
    # Properties

    id = DBVistrail.db_id
    actions = DBVistrail.db_actions # This is now read-write
    annotations = DBVistrail.db_annotations
    action_annotations = DBVistrail.db_actionAnnotations
    vistrail_variables = DBVistrail.db_vistrailVariables
    vistrail_vars = vistrail_variables
    parameter_explorations = DBVistrail.db_parameter_explorations
    
    def _get_actionMap(self):
        return self.db_actions_id_index
    actionMap = property(_get_actionMap)
    
    def get_annotation(self, key):
        if self.db_has_annotation_with_key(key):
            return self.db_get_annotation_by_key(key)
        return None
    
    def set_annotation(self, key, value):
        if self.db_has_annotation_with_key(key):
            old_annotation = self.db_get_annotation_by_key(key)
            if old_annotation.value == value:
                return False
            self.db_delete_annotation(old_annotation)
        if not (value is None or (isinstance(value, str) and value.strip() == '')):
            annotation = Annotation(id=self.idScope.getNewId(Annotation.vtType),
                                    key=key,
                                    value=value,
                                    )
            self.db_add_annotation(annotation)
        return True

    def _get_plugin_info(self):
        annotation = self.get_annotation("__plugin_info__")
        if annotation is not None:
            return annotation.value
        else:
            return ""
#         return annotation.value if annotation is not None else ""
    def _set_plugin_info(self, value):
        return self.set_annotation("__plugin_info__", value)
    plugin_info = property(_get_plugin_info, _set_plugin_info)

    def _get_database_info(self):
        annotation = self.get_annotation("__database_info__")
        if annotation is not None:
            return annotation.value
        else:
            return ""
#         return annotation.value if annotation is not None else ""
    def _set_database_info(self, value):
        return self.set_annotation("__database_info__", value)
    database_info = property(_get_database_info, _set_database_info)
    
    def has_vistrail_var(self, name):
        return self.db_has_vistrailVariable_with_name(name)
    
    def get_vistrail_var(self, name):
        if self.has_vistrail_var(name):
            return self.db_get_vistrailVariable_by_name(name)
        return None
    
    def set_vistrail_var(self, name, var):
        if self.db_has_vistrailVariable_with_name(name):
            old_var = self.db_get_vistrailVariable_by_name(name)
            if var and old_var == var:
                return False
            self.db_delete_vistrailVariable(old_var)
        if var:
            self.db_add_vistrailVariable(var)
        return True

    def getVersionName(self, version):
        """ getVersionName(version) -> str 
        Returns the name of a version, if it exists. Returns an empty string
        if it doesn't. 
        
        """
        if self.has_tag(version):
            return self.get_tag(version)
        return ""

    def get_pipeline_name(self, version):
        tag_map = self.get_tagMap()
        action_map = self.actionMap
        count = 0
        if version == -1:
            return None
        while True:
            if version in tag_map or version == Vistrail.ROOT_VERSION:
                if version in tag_map:
                    name = tag_map[version]
                else:
                    name = "ROOT"
                count_str = ""
                if count > 0:
                    count_str = " + " + str(count)
                return name + count_str
            if version not in action_map:
                raise KeyError("Cannot locate name for version %s" % \
                                str(version))
            version = action_map[version].parent
            count += 1

    def get_version_count(self):
        """get_version_count() -> Integer
        Returns the total number of versions in this vistrail.

        """
        return len(self.actionMap)

    def get_version_id(self, version):
        """get_version_number(version) -> Integer
        Returns the version number given a tag.

        """
        if self.has_tag_str(version):
            return self.get_tag_str(version).action_id
        if version in self.actionMap or version == -1: # -1 is no version
            return version
        raise KeyError("Cannot find version %s" % version)

    def get_ordered_actions(self):
        """get_ordered_actions() -> [Action]
        Returns all actions sorted by date (ids are not sequential with uuids)
        """
        return sorted(self.actions.itervalues(), key=lambda a: a.date)

    def find_action(self, leaf_version, obj_type, obj_id,
                    parent_obj_type=None, parent_obj_id=None):
        # print "FINDING ACTION", leaf_version, obj_type, obj_id, \
        #     parent_obj_type, parent_obj_id
        action_id = None
        op_id = None
        action_ids = self.tree.path_to_root(leaf_version)
        for action_id in action_ids:
            if action_id == Vistrail.ROOT_VERSION:
                continue
            for op in self.actionMap[action_id].operations:
                if op.vtType == 'add' or op.vtType == 'change':
                    if (op.what == obj_type and
                        op.new_obj_id == obj_id and
                        op.parentObjType == parent_obj_type and
                        op.parentObjId == parent_obj_id):
                        op_id = op.id
                        break
            # break out of outer loop if inner loop broke
            if op_id is not None:
                break
        if op_id is not None:
            return (action_id, op_id)
        return (None, None)

    def get_latest_version(self):
        """get_latest_version() -> Integer
        Returns the latest version id for the vistrail.

        FIXME: Running time O(|versions|)

        FIXME: Check if pruning is handled correctly here.

        """
        # use only sinks here (monotonicity, not valid for meta-vistrail)
        sinks = self.tree.getVersionTree().sinks()

        desc_key = Action.ANNOTATION_DESCRIPTION
        def has_upgrade(v_id):
            return (self.actionMap[v_id].has_annotation_with_key(desc_key) and
                    self.actionMap[v_id].get_annotation_by_key(desc_key).value == 'Upgrade')
        # Get the max id of all sinks (excluding upgrade actions)
        max_ver = max((v_id for v_id in sinks if not self.is_pruned(v_id) and not has_upgrade(v_id)),
                      key=lambda action_id: self.actionMap[action_id].date)
        # If that action has an upgrade, use it
        if self.has_upgrade(max_ver):
            max_ver = self.get_upgrade(max_ver)
        return max_ver

    def getPipeline(self, version):
        """getPipeline(number or tagname) -> Pipeline
        Return a pipeline object given a version number or a version name. 

        """
        try:
            if self.has_tag_str(str(version)):
                return self.getPipelineVersionName(str(version))
            else:
                return self.getPipelineVersionNumber(version)
        except Exception, e:
            raise InvalidPipeline([e])
    
    def getPipelineVersionName(self, version):
        """getPipelineVersionName(version:str) -> Pipeline
        Returns a pipeline given a version name. If version name doesn't exist
        it will return None.

        """
        if self.has_tag_str(version):
            number = self.get_tag_str(version).action_id
            return self.getPipelineVersionNumber(number)
        else:
            return None

    def getPipelineVersionNumber(self, version):
        """getPipelineVersionNumber(version:int) -> Pipeline
        Returns a pipeline given a version number.

        """
        workflow = vistrails.core.db.io.get_workflow(self, version)
        return workflow

    def get_pipeline_diff_with_connections(self, v1, v2):
        """like get_pipeline_diff but returns connection info
        Keyword arguments:
        v1     --- the first version number
        v2     --- the second version number
        return --- (p1, p2: VistrailPipeline,
                    [shared modules (id in v1, id in v2) ...],
                    [shared modules [heuristic match] (id in v1, id in v2)],
                    [v1 not v2 modules],
                    [v2 not v1 modules],
                    [parameter-changed modules (see-below)],
                    [controlParameter-changed modules (see-below)],
                    [annotation-changed modules (see-below)],
                    [shared connections (id in v1, id in v2) ...],
                    [shared connections [heuristic] (id in v1, id in v2)],
                    [c1 not in v2 connections],
                    [c2 not in v1 connections])

        parameter-changed modules = [((module id in v1, module id in v2),
                                      [(function in v1, function in v2)...]),
                                      ...]
        controlParameter-changed modules = [((module id in v1, module id in v2),
                                             [(cparam in v1, cparam in v2)...]),
                                             ...]
        annotation-changed modules = [((module id in v1, module id in v2),
                                      [(annotation in v1, annotation in v2)...]),
                                      ...]
        
        """
        return vistrails.core.db.io.get_workflow_diff_with_connections((self, v1), 
                                                             (self, v2))
        
    def get_pipeline_diff(self, v1, v2):
        """ get_pipeline_diff(v1: int, v2: int) -> tuple        
        Perform a diff between 2 versions, this will obtain the shared
        modules by getting shared nodes on the version tree. After,
        that, it will perform a heuristic algorithm to match
        signatures of modules to get more shared/diff modules. The
        heuristic is O(N^2), where N = the number of modules

        Keyword arguments:
        v1     --- the first version number
        v2     --- the second version number
        return --- (p1, p2: VistrailPipeline,
                    [shared modules (id in v1, id in v2) ...],
                    [shared modules [heuristic match] (id in v1, id in v2)],
                    [v1 not v2 modules],
                    [v2 not v1 modules],
                    [parameter-changed modules (see-below)],
                    [controlParameter-changed modules (see-below)],
                    [annotation-changed modules (see-below)])

        parameter-changed modules = [((module id in v1, module id in v2),
                                      [(function in v1, function in v2)...]),
                                      ...]
        controlParameter-changed modules = [((module id in v1, module id in v2),
                                             [(cparam in v1, cparam in v2)...]),
                                             ...]
        annotation-changed modules = [((module id in v1, module id in v2),
                                       [(annotation in v1, annotation in v2)...]),
                                       ...]

        
        """
        return vistrails.core.db.io.get_workflow_diff((self, v1), (self, v2))
                        
    def getFirstCommonVersion(self, v1, v2):
        """ Returns the first version that it is common to both v1 and v2 
        Parameters
        ----------
        - v1 : 'int'
         version number 1

        - v2 : 'int'
         version number 2

        """
        if (v1<=0 or v2<=0):
            return 0
        
        t1 = set()
        t1.add(v1)
        t = self.actionMap[v1].parent
        while  t != Vistrail.ROOT_VERSION:
            t1.add(t)
            t = self.actionMap[t].parent
        
        t = v2
        while t != Vistrail.ROOT_VERSION:
            if t in t1:
                return t
            t = self.actionMap[t].parent
        return 0

    def general_action_chain(self, v1, v2):
        """general_action_chain(v1, v2): Returns an action that turns
        pipeline v1 into v2."""

        return vistrails.core.db.io.getPathAsAction(self, v1, v2)
    
    def actionChain(self, t, start=0):
        """ actionChain(t:int, start=0) -> [Action]  
        Returns the action chain (list of Action)  necessary to recreate a 
        pipeline from a  certain time
                      
        """
        assert t >= start
        if t == start:
            return []
        result = []
        action = self.actionMap[t]
        
        while 1:
            result.append(action)
            if action.timestep == start:
                break
            if action.parent == start:
                if start != 0:
                    action = self.actionMap[action.parent]
                break
            action = self.actionMap[action.parent]
        result.reverse()
        return result
    
    def update_object(self, obj, **kwargs):
        self.db_update_object(obj, **kwargs)

    def add_action(self, action, parent, session=None):
        # FIXME: this should go to core.db.io
        Action.convert(action)
        if action.id < 0:
            action.id = self.idScope.getNewId(action.vtType)
        action.prevId = parent
        action.date = self.getDate()
        action.user = self.getUser()
        if session is not None:
            action.session = session
        for op in action.operations:
            if op.id < 0:
                op.id = self.idScope.getNewId('operation')
                if op.vtType == 'add' or op.vtType == 'change':
                    self.db_add_object(op.db_data)
        self.addVersion(action)

#     def add_abstraction(self, abstraction):
#         Abstraction.convert(abstraction)
#         if abstraction.id < 0:
#             abstraction.id = self.idScope.getNewId(abstraction.vtType)
#             action_remap = {}
#             for action in abstraction.actions.itervalues():
#                 if action.id < 0:
#                     new_id = abstraction.idScope.getNewId(action.vtType)
#                     action_remap[action.id] = new_id
#                     action.id = new_id
#                 action.date = self.getDate()
#                 action.user = self.getUser()
#                 for op in action.operations:
#                     if op.id < 0:
#                         op.id = self.idScope.getNewId('operation')
#             for action in abstraction.actions.itervalues():
#                 if action.prevId < 0:
#                     action.prevId = action_remap[action.prevId]

#         self.db_add_abstraction(abstraction)

    def getLastActions(self, n):
        """ getLastActions(n: int) -> list of ids
        Returns the last n actions performed
        """
        last_n = []
        num_actions = len(self.actionMap)
        if num_actions < n:
            n = num_actions
        if n > 0:
            sorted_items = sorted(self.actionMap.iteritems(), key=lambda a: a[1].date)
            last_n = [k for (k,v) in sorted_items[num_actions-n:num_actions-1]]
        return last_n

    def hasVersion(self, version):
        """hasVersion(version:int) -> boolean
        Returns True if version with given timestamp exists

        """
        return version in self.actionMap
    
    def addVersion(self, action):
        """ addVersion(action: Action) -> None 
        Adds new version to vistrail
          
        """
        if action.timestep in self.actionMap:
            raise VistrailsInternalError("existing timestep: %d" % 
                                         action.timestep)
        self.db_add_action(action)
        self.changed = True

        # signal to update explicit tree
        self.tree.addVersion(action.id, action.prevId)

    def hasTag(self, tag):
        """ hasTag(tag) -> boolean 
        Returns True if a tag with given name or number exists
       
        """
        if isinstance(tag, (int, long)):
            return self.has_tag(tag)
        elif isinstance(tag, basestring):
            return self.has_tag_str(tag)
        
    def addTag(self, version_name, version_number):
        """addTag(version_name, version_number) -> None
        Adds new tag to vistrail
          
        """
        if version_name == '':
            return None
        if self.has_tag(version_number):
            debug.log("Version is already tagged")
            raise VersionAlreadyTagged()
        if self.has_tag_str(version_name):
            debug.log("Tag already exists")
            raise TagExists()
        self.set_tag(version_number, version_name)
        
    def changeTag(self, version_name, version_number):
        """changeTag(version_name, version_number) -> None        
        Changes the old tag of version_number to version_name in the
        vistrail.  If version_name is empty, this version will be
        untagged.
                  
        """
        if not self.has_tag(version_number):
            debug.log("Version is not tagged")
            raise VersionNotTagged()
        if self.get_tag(version_number) == version_name:
            return None
        if self.has_tag_str(version_name):
            debug.log("Tag already exists")
            raise TagExists()
        self.set_tag(version_number, version_name)

    def has_action_annotation(self, action_id, key):
        return self.db_has_actionAnnotation_with_action_id((action_id, key))
    
    def get_action_annotation(self, action_id, key):
        if self.has_action_annotation(action_id, key):
            return self.db_get_actionAnnotation_by_action_id((action_id, key))
        return None

    def delete_action_annotation(self, action_id, key):
        annotation = self.get_action_annotation(action_id, key)
        self.db_delete_actionAnnotation(annotation)

    def set_action_annotation(self, action_id, key, value):
        changed = False
        if self.has_action_annotation(action_id, key):
            annotation = self.get_action_annotation(action_id, key)
            if annotation.value == value:
                return False
            self.db_delete_actionAnnotation(annotation)
            changed = True
        if value is not None and value.strip() != '':
            new_id = self.idScope.getNewId(ActionAnnotation.vtType)
            annotation = ActionAnnotation(id=new_id,
                                          action_id=action_id,
                                          key=key,
                                          value=value,
                                          date=self.getDate(),
                                          user=self.getUser())
            #print 'doing addAnnotation', action_id, key, value
            self.db_add_actionAnnotation(annotation)
            changed = True
        if changed:
            self.changed = True
            return True
        return False

    def get_tagMap(self):
        tagMap = {}
        for annotation in self.action_annotations:
            if annotation.db_key == Vistrail.TAG_ANNOTATION:
                tagMap[annotation.db_action_id] = annotation.db_value
        return tagMap
    def has_tag_str(self, value):
        return self.db_has_actionAnnotation_with_key((Vistrail.TAG_ANNOTATION,
                                                      value))
    def get_tag_str(self, value):
        return self.db_get_actionAnnotation_by_key((Vistrail.TAG_ANNOTATION,
                                                     value))
    def has_tag(self, action_id):
        return self.has_action_annotation(action_id, Vistrail.TAG_ANNOTATION)
    def get_tag(self, action_id):
        a = self.get_action_annotation(action_id, Vistrail.TAG_ANNOTATION)
        if a is not None:
            return a.value
        return None
    def set_tag(self, action_id, value):
        return self.set_action_annotation(action_id, Vistrail.TAG_ANNOTATION,
                                          value)

    def has_notes(self, action_id):
        return self.has_action_annotation(action_id, Vistrail.NOTES_ANNOTATION)
    def get_notes(self, action_id):
        a = self.get_action_annotation(action_id, Vistrail.NOTES_ANNOTATION)
        if a is not None:
            return a.value
        return None
    def set_notes(self, action_id, value):
        return self.set_action_annotation(action_id, Vistrail.NOTES_ANNOTATION,
                                          value)

    def has_paramexp(self, action_id):
        """ Check if vistrail has a latest paramexp for action action_id
        """
        return len(self.get_paramexps(action_id))>0
    def get_paramexp(self, action_id):
        """ Check if vistrail has a default paramexp for action action_id
            and returns it (using latest id)
        """
        if self.has_named_paramexp(action_id):
            return self.get_named_paramexp(action_id)
        pes = self.get_paramexps(action_id)
        if not len(pes):
            return None
        pes.sort(key=lambda x: x.id)
        return pes[-1]
    def get_paramexps(self, action_id):
        """ return all pe:s for this action
        """
        return [pe for pe in self.parameter_explorations if pe.action_id == action_id]
    def has_named_paramexp(self, name):
        """ Check if vistrail has a paramexp named "name"
        """
        if not name:
            return False
        for pe in self.parameter_explorations:
            if pe.name == name:
                return True 
        return False
    def get_named_paramexp(self, name):
        """ Returns the paramexp named "name" or None
        """
        for pe in self.parameter_explorations:
            if pe.name == name:
                return pe 
        return None
    def delete_paramexp(self, param_exp):
        self.db_delete_parameter_exploration(param_exp)
    def add_paramexp(self, param_exp):
        param_exp.id = self.idScope.getNewId(param_exp.vtType)
        self.db_add_parameter_exploration(param_exp)

    def has_thumbnail(self, action_id):
        return self.has_action_annotation(action_id,
                                          Vistrail.THUMBNAIL_ANNOTATION)
    def get_thumbnail(self, action_id):
        a = self.get_action_annotation(action_id, 
                                       Vistrail.THUMBNAIL_ANNOTATION)
        if a is not None:
            return a.value
        return None
    def set_thumbnail(self, action_id, value):
        return self.set_action_annotation(action_id,
                                          Vistrail.THUMBNAIL_ANNOTATION,
                                          value)

    def has_prune(self, action_id):
        return self.has_action_annotation(action_id, Vistrail.PRUNE_ANNOTATION)
    def get_prune(self, action_id):
        a = self.get_action_annotation(action_id, Vistrail.PRUNE_ANNOTATION)
        if a is not None:
            return a.value
        return None
    def set_prune(self, action_id, value):
        if isinstance(value, bool):
            value = str(value)
        return self.set_action_annotation(action_id, Vistrail.PRUNE_ANNOTATION,
                                          value)
    def is_pruned(self, action_id):
        return self.get_prune(action_id) == str(True)

    def has_upgrade(self, action_id):
        return self.has_action_annotation(action_id, 
                                          Vistrail.UPGRADE_ANNOTATION)
    def get_upgrade(self, action_id, root_level=True):
        a = self.get_action_annotation(action_id, Vistrail.UPGRADE_ANNOTATION)
        if a is not None:
            # Recurse to get the newest upgrade in case there are
            # multiple chained upgrades
            return self.get_upgrade(a.value, False)
        if root_level:
            return None
        return action_id
    def set_upgrade(self, action_id, value):
        return self.set_action_annotation(action_id, 
                                          Vistrail.UPGRADE_ANNOTATION,
                                          value)
    
    def change_annotation(self, key, value, version_number):
        """ change_annotation(key:str, value:str, version_number:long) -> None 
        Changes the annotation of (key, value) for version version_number
                  
        """
        
        if version_number in self.actionMap:
            action = self.actionMap[version_number]
            if action.has_annotation_with_key(key):
                old_annotation = action.get_annotation_by_key(key)
                if old_annotation.value == value:
                    return False
                action.delete_annotation(old_annotation)
            if value.strip() != '':
                annotation = \
                    Annotation(id=self.idScope.getNewId(Annotation.vtType),
                               key=key,
                               value=value,
                               )
                action.add_annotation(annotation)
            self.changed = True
            return True
        return False

    def change_description(self, description, version_number): 
        """ change_description(description:str, version_number:int) -> None 
        Changes the description of a version
                  
        """
       
        return self.change_annotation(Action.ANNOTATION_DESCRIPTION, 
                                      description, version_number)

    def change_analogy_info(self, analogy_info, version_number):
        """ change_analogy_info(analogy_info:str, version_number:int) -> None 
        Changes the analogy information of a version
                  
        """

        return self.change_annotation(Action.ANNOTATION_ANALOGY_INFO,
                                      analogy_info, version_number)

    def get_description(self, version_number):
        """ get_description(version_number: int) -> str
        Compute the description of a version
        
        """
        description = "Other action"
        if version_number == self.ROOT_VERSION:
            description = "" # Root node
        elif version_number in self.actionMap:
            action = self.actionMap[version_number]
            # if a description has been manually set, return that value
            if action.description is not None:
                return action.description
            ops = action.operations
            added_modules = 0
            added_functions = 0
            added_parameters = 0
            added_connections = 0
            added_annotations = 0
            added_control_parameters = 0
            added_ports = 0
            moved_modules = 0
            changed_parameters = 0
            changed_annotations = 0
            changed_control_parameters = 0
            deleted_modules = 0
            deleted_connections = 0
            deleted_parameters = 0
            deleted_functions = 0
            deleted_annotations = 0
            deleted_control_parameters = 0
            deleted_ports = 0
            for op in ops:
                if op.vtType == 'add':
                    if op.what == 'module':
                        added_modules+=1
                    elif op.what == 'connection':
                        added_connections+=1
                    elif op.what == 'function':
                        added_functions+=1
                    elif op.what == 'parameter':
                        added_parameters+=1
                    elif op.what == 'controlParameter':
                        added_control_parameters+=1
                    elif op.what == 'annotation':
                        added_annotations+=1
                    elif op.what == 'portSpec':
                        added_ports += 1
                elif op.vtType == 'change':
                    if op.what == 'parameter':
                        changed_parameters+=1
                    elif op.what == 'location':
                        moved_modules+=1
                    elif op.what == 'annotation':
                        changed_annotations+=1
                    elif op.what == 'controlParameter':
                        changed_control_parameters+=1
                elif op.vtType == 'delete':
                    if op.what == 'module':
                        deleted_modules+=1
                    elif op.what == 'connection':
                        deleted_connections+=1
                    elif op.what == 'function':
                        deleted_functions+=1
                    elif op.what == 'parameter':
                        deleted_parameters+=1
                    elif op.what == 'annotation':
                        deleted_annotations+=1
                    elif op.what == 'controlParameter':
                        deleted_control_parameters+=1
                    elif op.what == 'portSpec':
                        deleted_ports += 1
                else:
                    raise TypeError("Unknown operation type '%s'" % op.vtType)

            if added_modules:
                description = "Added module"
                if added_modules > 1:
                    description += "s"
            elif added_connections:
                description = "Added connection"
                if added_connections > 1:
                    description += "s"
            elif added_functions or added_parameters:
                description = "Added parameter"
                if added_functions > 1 or added_parameters > 1:
                    description += "s"
            elif added_control_parameters:
                description = "Added control parameter"
                if added_control_parameters > 1:
                    description += "s"
            elif added_annotations:
                description = "Added annotation"
                if added_annotations > 1:
                    description += "s"
            elif added_ports:
                description = "Added port"
                if added_ports > 1:
                    description += "s"
            elif changed_parameters:
                description = "Changed parameter"
                if changed_parameters > 1:
                    description += "s"
            elif changed_control_parameters:
                description = "Changed control parameter"
                if changed_control_parameters > 1:
                    description += "s"
            elif moved_modules:
                description = "Moved module"
                if moved_modules > 1:
                    description += "s"
            elif changed_annotations:
                description = "Changed annotation"
                if changed_annotations > 1:
                    description += "s"
            elif deleted_modules:
                description = "Deleted module"
                if deleted_modules > 1:
                    description += "s"
            elif deleted_connections:
                description = "Deleted connection"
                if deleted_connections > 1:
                    description += "s"
            elif deleted_parameters or deleted_functions:
                description = "Deleted parameter"
                if deleted_parameters > 1 or deleted_functions > 1:
                    description += "s"
            elif deleted_control_parameters:
                description = "Deleted control parameter"
                if deleted_control_parameters > 1:
                    description += "s"
            elif deleted_annotations:
                description = "Deleted annotation"
                if deleted_annotations > 1:
                    description += "s"
            elif deleted_ports:
                description = "Deleted port"
                if deleted_ports > 1:
                    description += "s"
        return description

    def getDate(self):
        """ getDate() -> str - Returns the current date and time. """
        return datetime.datetime.now()
    
    def getUser(self):
        """ getUser() -> str - Returns the username. """
        return getpass.getuser()

    def serialize(self, filename):
        pass

    def hideVersion(self, version):
        """ hideVersion(version: int) -> None
        Set the prune flag for the version

        """
        if version != self.ROOT_VERSION:
            self.set_prune(version, str(True))

    def showVersion(self, version):
        """ showVersion(version: int) -> None
        Set the prune flag for the version

        """
        if version != self.ROOT_VERSION:
            self.set_prune(version, str(False))

    def expandVersion(self, version):
        """ expandVersion(version: int) -> None
        Set the expand flag for the version
        
        """
        if version != self.ROOT_VERSION: # not root
            self.actionMap[version].expand = 1

    def collapseVersion(self, version):
        """ collapseVersion(version: int) -> None
        Reset the expand flag for the version
        
        """
        if version != self.ROOT_VERSION:
            self.actionMap[version].expand = 0

    def setSavedQueries(self, savedQueries):
        """ setSavedQueries(savedQueries: list of (str, str, str)) -> None
        Set the saved queries of this vistrail
        
        """
        self.savedQueries = savedQueries

    class InvalidAbstraction(Exception):
        pass

    def get_persisted_log(self):
        """
        Returns the log object for this vistrail if available
        """
        # need this because we might have loaded this to translate a bundle
        if self.log is not None:
            return self.log

        log = Log()
        if isinstance(self.locator, vistrails.core.db.locator.ZIPFileLocator):
            if self.db_log_filename is not None:
                log = open_log_from_xml(self.db_log_filename, True)
        if isinstance(self.locator, vistrails.core.db.locator.DBLocator):
            connection = self.locator.get_connection()
            log = open_vt_log_from_db(connection, self.db_id)
        Log.convert(log)
        self.log = log
        return log
    
    def get_used_packages(self):
        package_list = {}
        for action in self.actions:
            for op in action.operations:
                try:
                    if isinstance(op, AddOp) and op.what == 'module':
                        package_list[op.data.package] = op.data.package
                except AttributeError, e:
                    debug.unexpected_exception(e)
        return package_list

    def get_base_upgrade_version(self, version):
        """Finds the base version in the upgrade chain.
        """
        # TODO: use this in search_upgrade_versions(), once the map is cached
        upgrade_rev_map = {}
        for ann in self.action_annotations:
            if ann.key == Vistrail.UPGRADE_ANNOTATION:
                upgrade_rev_map[ann.value] = ann.action_id

        while version in upgrade_rev_map:
            version = upgrade_rev_map[version]
        return version

    def search_upgrade_versions(self, base_version, getter,
                                start_at_base=None):
        """Search all upgrades from a version for a specific value.

        :param base_version: version from which to search (upgrades from this
        version will be recursively searched)
        :param getter: function that returns the value you are looking for, or
        None to continue searching
        :param start_at_base: if None (default), start from given version, then
        if nothing is found start again from original version. If True, search
        from the original action (the one that's not an upgrade). If False, go
        down from given version only.
        :returns: The result from getter, or None if all upgrades were exhausted
        """
        # TODO: cache these maps somewhere
        upgrade_map = {}
        upgrade_rev_map = {}
        for ann in self.action_annotations:
            if ann.key == Vistrail.UPGRADE_ANNOTATION:
                upgrade_map[ann.action_id] = ann.value
                upgrade_rev_map[ann.value] = ann.action_id

        if start_at_base is True:
            while base_version in upgrade_rev_map:
                base_version = upgrade_rev_map[base_version]

        version = base_version
        walked_versions = set()
        while version is not None and version not in walked_versions:
            ret = getter(self, version, base_version)
            if ret is not None:
                return ret
            walked_versions.add(version)
            version = upgrade_map.get(version)
            if version is None and start_at_base is None:
                start_at_base = True
                version = base_version
                while version in upgrade_rev_map:
                    version = upgrade_rev_map[version]
        return None

    def get_upgrade_chain(self, base_version, start_at_base=False):
        """Returns upgrade chain for version.

        :param base_version: a version in the upgrade chain
        :param start_at_base: if False (default), return chain starting with
        given version. If True, start from the original action (the one that's
        not an upgrade). If False, go down from given version only.
        :returns: The list version ids in the upgrade chain
        """
        # TODO: cache these maps somewhere
        upgrade_map = {}
        upgrade_rev_map = {}
        for ann in self.action_annotations:
            if ann.key == Vistrail.UPGRADE_ANNOTATION:
                upgrade_map[ann.action_id] = ann.value
                upgrade_rev_map[ann.value] = ann.action_id
        if start_at_base is True:
            while base_version in upgrade_rev_map:
                base_version = upgrade_rev_map[base_version]

        chain = []
        version = base_version
        walked_versions = set()
        while version is not None and version not in walked_versions:
            chain.append(version)
            walked_versions.add(version)
            version = upgrade_map.get(version)
        return chain

class MetaVistrail(Vistrail):
    """Instead of generating pipelines, this class generates Vistrails"""

    def getVistrail(self, version):
        """getPipeline(number or tagname) -> Pipeline
        Return a pipeline object given a version number or a version name. 

        """
        if self.has_tag_str(str(version)):
            return self.getVistrailVersionName(str(version))
        else:
            return self.getVistrailVersionNumber(version)

    def getVistrailVersionName(self, version):
        """getPipelineVersionName(version:str) -> Pipeline
        Returns a pipeline given a version name. If version name doesn't exist
        it will return None.

        """
        if self.has_tag_str(version):
            number = self.get_tag_str(version).action_id
            return self.getVistrailVersionNumber(number)
        else:
            return None

    def getVistrailVersionNumber(self, version):
        """getPipelineVersionNumber(version:int) -> Pipeline
        Returns a pipeline given a version number.

        """
        vistrail = vistrails.core.db.io.get_vistrail(self, version)
        # make sure the vistrail knows its meta_vistrail
        vistrail.meta_vistrail = self
        return vistrail

    def add_action(self, action, parent, session=None, init_inner=False):
        # want to have sub-actions be valid actions...
        # TODO should we assign the same date/user/session info as meta-action?
        if init_inner:
            for op in action.operations:
                if op.db_what == 'action' and (op.vtType == 'change' or
                                               op.vtType == 'add'):
                    sub_action = op.db_data
                    if sub_action.id < 0:
                        sub_action.id = self.idScope.getNewId(sub_action.vtType)
                    sub_action.date = self.getDate()
                    sub_action.user = self.getUser()
                    if session is not None:
                        sub_action.session = session

        super(MetaVistrail, self).add_action(action, parent, session)


##############################################################################

class ExplicitExpandedVersionTree(object):
    """
    Keep explicit expanded and tersed version 
    trees.
    """
    def __init__(self, vistrail):
        self.vistrail = vistrail
        self.expandedVersionTree = Graph()
        self.expandedVersionTree.add_vertex(Vistrail.ROOT_VERSION)
        self.tersedVersionTree = Graph()

    def addVersion(self, id, prevId):
        # print "add version %d child of %d" % (id, prevId)
        self.expandedVersionTree.add_vertex(id)
        self.expandedVersionTree.add_edge(prevId,id,0)
    
    def getVersionTree(self):
        return self.expandedVersionTree

    def path_to_root(self, v):
        """Returns the ids along the path from a node back up to the root"""
        tree = self.expandedVersionTree
        path = []
        try:
            while True:
                path.append(v)
                v = tree.parent(v)
        except tree.VertexHasNoParentError:
            pass
        return path

##############################################################################

class VersionAlreadyTagged(Exception):
    def __str__(self):
        return "Version is already tagged"
    pass

class TagExists(Exception):
    def __str__(self):
        return "Tag already exists"
    pass

class VersionNotTagged(Exception):
    def __str__(self):
        return "Version is not tagged"
    pass

##############################################################################
# Testing

from vistrails.core.system import get_vistrails_basic_pkg_id
from vistrails.tests.utils import reproducible_uuid_context, uuids_sim

class TestVistrail(unittest.TestCase):

    def create_vistrail(self):
        vistrail = Vistrail()

        m = Module(id=vistrail.idScope.getNewId(Module.vtType),
                   name='Float',
                   package=get_vistrails_basic_pkg_id())
        add_op = AddOp(id=vistrail.idScope.getNewId(AddOp.vtType),
                       what=Module.vtType,
                       objectId=m.id,
                       data=m)
        function_id = vistrail.idScope.getNewId(ModuleFunction.vtType)
        function = ModuleFunction(id=function_id,
                                  name='value')
        change_op = ChangeOp(id=vistrail.idScope.getNewId(ChangeOp.vtType),
                             what=ModuleFunction.vtType,
                             oldObjId=2,
                             newObjId=function.real_id,
                             parentObjId=m.id,
                             parentObjType=Module.vtType,
                             data=function)
        param = ModuleParam(id=vistrail.idScope.getNewId(ModuleParam.vtType),
                            type='Integer',
                            val='1')
        delete_op = DeleteOp(id=vistrail.idScope.getNewId(DeleteOp.vtType),
                             what=ModuleParam.vtType,
                             objectId=param.real_id,
                             parentObjId=function.real_id,
                             parentObjType=ModuleFunction.vtType)

        action1 = Action(id=vistrail.idScope.getNewId(Action.vtType),
                         operations=[add_op])
        action2 = Action(id=vistrail.idScope.getNewId(Action.vtType),
                         operations=[change_op, delete_op])

        vistrail.add_action(action1, 0)
        vistrail.add_action(action2, action1.id)
        vistrail.addTag('first action', action1.id)
        vistrail.addTag('second action', action2.id)
        return vistrail

    def test_get_tag_str(self):
        v = self.create_vistrail()
        self.failUnlessRaises(KeyError, lambda: v.get_tag_str('not here'))
        v.get_tag_str('first action')
        v.get_tag_str('second action')

    def test_copy(self):
        v1 = self.create_vistrail()
        v2 = copy.copy(v1)
        v3 = v1.do_copy(True, v1.idScope, {})
        # FIXME add checks for equality

    def test_serialization(self):
        import vistrails.core.db.io
        v1 = self.create_vistrail()
        xml_str = vistrails.core.db.io.serialize(v1)
        v2 = vistrails.core.db.io.unserialize(xml_str, Vistrail)
        # FIXME add checks for equality

    def test1(self):
        from vistrails.core.db.locator import XMLFileLocator
        import vistrails.core.system
        v = XMLFileLocator(vistrails.core.system.vistrails_root_directory() +
                           '/tests/resources/dummy-uuid.xml').load()
        #testing nodes in different branches
        v1 = v.get_version_id("int chain") # 36
        v2 = v.get_version_id("float chain") # 41
        p1 = v.getFirstCommonVersion(v1,v2)
        p2 = v.getFirstCommonVersion(v2,v1)
        self.assertEquals(p1,p2)
        
        #testing nodes in the same branch
        v1 = "61b3df67-2e13-40fd-a776-3676ec1f71f2" #15 -- 14 down
        v2 = v.get_version_id("int chain") # 36
        p1 = v.getFirstCommonVersion(v1,v2)
        p2 = v.getFirstCommonVersion(v2,v1)
        self.assertEquals(p1,p2)

        if p1 == 0 or p2 == 0:
            self.fail("vistrails tree is not single rooted.")

    def test2(self):
        from vistrails.core.db.locator import XMLFileLocator
        import vistrails.core.system
        v = XMLFileLocator(vistrails.core.system.vistrails_root_directory() +
                           '/tests/resources/dummy-uuid.xml').load()
        #testing diff
        v1 = "86c60887-b1c0-424e-b481-27b8979aab29" # 17 -- 16 down
        v2 = "1adc47dd-9ba7-40c9-aada-b7543e92ece1" # 27 -- 26 down
        v3 = "0dff5a48-6bcd-43e7-948e-71045f40a971" # 22 -- 21 down
        v.get_pipeline_diff(v1,v2)
        v.get_pipeline_diff(v1,v3)
        v.get_pipeline_diff_with_connections(v1,v2)
        v.get_pipeline_diff_with_connections(v1,v3)

    def test_empty_action_chain(self):
        """Tests calling action chain on empty version."""
        v = Vistrail()
        p = v.getPipeline(Vistrail.ROOT_VERSION)

    def test_empty_action_chain_2(self):
        from vistrails.core.db.locator import XMLFileLocator
        import vistrails.core.system
        v = XMLFileLocator(vistrails.core.system.vistrails_root_directory() +
                           '/tests/resources/dummy.xml').load()
        assert v.actionChain(17, 17) == []

    def test_get_version_negative_one(self):
        """Tests getting the 'no version' vistrail. This should raise
        VistrailsDBException.

        """
        v = Vistrail()
        self.assertRaises(InvalidPipeline, lambda: v.getPipeline(-1))

    def test_plugin_info(self):
        import vistrails.core.db.io
        plugin_info_str = "this is a test of plugin_info"
        v1 = self.create_vistrail()
        v1.plugin_info = plugin_info_str
        xml_str = vistrails.core.db.io.serialize(v1)
        v2 = vistrails.core.db.io.unserialize(xml_str, Vistrail)
        assert plugin_info_str == v2.plugin_info

    def test_database_info(self):
        import vistrails.core.db.io
        database_info_str = "db.hostname.edu:3306:TABLE_NAME"
        v1 = self.create_vistrail()
        v1.database_info = database_info_str
        xml_str = vistrails.core.db.io.serialize(v1)
        v2 = vistrails.core.db.io.unserialize(xml_str, Vistrail)
        assert database_info_str == v2.database_info

    def test_plugin_data(self):
        import vistrails.core.db.io
        v1 = self.create_vistrail()
        plugin_data_str = "testing plugin_data"
        p = PluginData(id=v1.idScope.getNewId(PluginData.vtType),
                       data=plugin_data_str)
        add_op = AddOp(id=v1.idScope.getNewId(AddOp.vtType),
                       what=PluginData.vtType,
                       objectId=p.id,
                       data=p)
        action = Action(id=v1.idScope.getNewId(Action.vtType),
                        operations=[add_op])
        v1.add_action(action, Vistrail.ROOT_VERSION)
        workflow = v1.getPipeline(action.id)
        # FIXME why is this just accessed as a list?
        p2 = workflow.plugin_datas[0]
        assert plugin_data_str == p2.data

    def test_inverse(self):
        """Test if inverses and general_action_chain are working by
        doing a lot of action-based transformations on a pipeline and
        checking against another way of getting the same one."""
        def check_pipelines(p, p2):
            if p != p2:
                p.show_comparison(p2)
                return False
            return True
        from vistrails.core.db.locator import XMLFileLocator
        from vistrails.core.db.locator import FileLocator
        import vistrails.core.system
        import sys

        def do_test(filename, locator_class, old_v=None, new_v=None):
            v = locator_class(vistrails.core.system.vistrails_root_directory() +
                              filename).load()
            if not isinstance(v, Vistrail):
                v = v.vistrail
            version_ids = v.actionMap.keys()
            if old_v is None:
                old_v = random.choice(version_ids)
            p = v.getPipeline(old_v)

            def do_single_test(start_v, end_v):
                p2 = v.getPipeline(end_v)
                a = v.general_action_chain(start_v, end_v)
                p.perform_action(a)
                #if not check_pipelines(p, p2):
                #    print start_v, end_v

                assert p == p2

            if new_v is not None:
                do_single_test(old_v, new_v)
            else:
                for i in xrange(10):
                    new_v = random.choice(version_ids)
                    do_single_test(old_v, new_v)
                    old_v = new_v
                    

        do_test('/tests/resources/dummy.xml', XMLFileLocator)
        do_test('/tests/resources/terminator.vt', FileLocator)

    def test_ids(self):
        with reproducible_uuid_context:
            v = Vistrail()
            action1 = Action(id=v.idScope.getNewId(Action.vtType),
                             operations=[])
            action2 = Action(id=v.idScope.getNewId(Action.vtType),
                             operations=[])
            v.add_action(action1, Vistrail.ROOT_VERSION)
            v.add_action(action2, Vistrail.ROOT_VERSION)
            print "ACTION 1 ID:", action1.id
            print "ACTION 2 ID:", action2.id
            self.assertTrue(uuids_sim(action1.prevId, Vistrail.ROOT_VERSION))
            self.assertTrue(uuids_sim(action1.id, '360de7dd'))
            self.assertTrue(uuids_sim(action2.id, 'cc0d23a4'))


class TestMetaVistrail(unittest.TestCase):
    def create_vistrail(self):
        vistrail = MetaVistrail()

        def update_ids(actions):
            for action in actions:
                if action.id < 0:
                    action.id = vistrail.idScope.getNewId('action')
                for op in action.operations:
                    if op.id < 0:
                        op.id = vistrail.idScope.getNewId('operation')
                        # if op.vtType == 'add' or op.vtType == 'change':
                        #     vistrail.db_add_object(op.db_data)

        def link_versions(links):
            for (parent, child) in links:
                if parent is None:
                    parent_id = Vistrail.ROOT_VERSION
                else:
                    parent_id = parent.id
                child.parent = parent_id

        def create_action_annotation(action_id, key, value):
            new_id = vistrail.idScope.getNewId(ActionAnnotation.vtType)
            annotation = ActionAnnotation(id=new_id,
                                          action_id=action_id,
                                          key=key,
                                          value=value,
                                          date=vistrail.getDate(),
                                          user=vistrail.getUser())
            return annotation

        p1 = ModuleParam(
            id=vistrail.idScope.getNewId(),
            type='Integer',
            val='2')
        f1 = ModuleFunction(id=vistrail.idScope.getNewId(),
                            name='value',
                            parameters=[p1])
        m = Module(id=vistrail.idScope.getNewId(Module.vtType),
                   name='Float',
                   package=get_vistrails_basic_pkg_id(),
                   location=Location(id=vistrail.idScope.getNewId(),x=12,y=12),
                   functions=[f1])
        a1 = vistrails.core.db.io.create_action([('add', m)])

        p2 = ModuleParam(id=vistrail.idScope.getNewId(),
                         type='Integer',
                         val='1')
        a2 = vistrails.core.db.io.create_action(
            [('change', p1, p2, 'function', f1.real_id)])
        f1.parameters = [p2]
        a3 = vistrails.core.db.io.create_action(
            [('delete', f1, 'module', m.id)])

        p3 = ModuleParam(
            id=p2.real_id,
            type='Integer',
            val='3')
        f2 = ModuleFunction(id=f1.real_id,
                            name='value',
                            parameters=[p3])
        m2 = Module(id=vistrail.idScope.getNewId(Module.vtType),
                   name='Integer',
                   package=get_vistrails_basic_pkg_id(),
                   location=Location(id=vistrail.idScope.getNewId(), x=12, y=12),
                   functions=[f2])
        a4 = vistrails.core.db.io.create_action([('add', m2)])

        m3 = Module(id=vistrail.idScope.getNewId(Module.vtType),
                   name='StandardOutput',
                   package=get_vistrails_basic_pkg_id(),
                   location=Location(id=vistrail.idScope.getNewId(), x=16, y=16))

        from vistrails.core.modules.basic_modules import identifier as basic_pkg
        source = Port(id=vistrail.idScope.getNewId(),
                      type='source',
                      moduleId=m2.id,
                      moduleName='Integer',
                      name='value',
                      signature='(%s:Float)' % basic_pkg)
        destination = Port(id=vistrail.idScope.getNewId(),
                           type='destination',
                           moduleId=m3.id,
                           moduleName='Module',
                           name='value',
                           signature='(%s:Module)' % basic_pkg)
        c = Connection(id=vistrail.idScope.getNewId(Connection.vtType),
                       ports=[source, destination])



        a5 = vistrails.core.db.io.create_action([('add', m3),
                                                 ('add', c)])
        update_ids([a1,a2,a3,a4,a5])
        a4.id = a1.id
        link_versions([(None, a1), (a1, a2), (a2, a3), (None, a4), (a2, a5)])

        for num, action in enumerate([a1,a2,a3,a4, a5]):
            print "ACTION", num, action, [(op.vtType, op.what, op.old_obj_id, op.new_obj_id) for op in action.operations]

        tag_a2 = create_action_annotation(a2.id,
                                          Vistrail.TAG_ANNOTATION,
                                          "float")
        tag_a2_new = create_action_annotation(a2.id,
                                          Vistrail.TAG_ANNOTATION,
                                          "integer")
        tag_a5 = create_action_annotation(a5.db_id,
                                          Vistrail.TAG_ANNOTATION,
                                          "connected")

        meta_a1 = vistrails.core.db.io.create_action([('add', a1)], False)
        meta_a2 = vistrails.core.db.io.create_action([('add', a2)], False)
        meta_a3 = vistrails.core.db.io.create_action([('add', a3)], False)
        meta_a4 = vistrails.core.db.io.create_action([('change', a1, a4)], False)
        meta_a5 = vistrails.core.db.io.create_action([('delete', tag_a2),
                                                      ('delete', a2)], False)
        meta_a6 = vistrails.core.db.io.create_action([('add', a5)], False)

        meta_a7 = vistrails.core.db.io.create_action([('add', tag_a2)], False)
        # move tag to updated version
        meta_a8 = vistrails.core.db.io.create_action([('change', tag_a2, tag_a2_new)], False)
        meta_a9 = vistrails.core.db.io.create_action([('add', tag_a5)], False)


        vistrail.add_action(meta_a1, Vistrail.ROOT_VERSION, init_inner=True)
        # print("MW:", len(vistrail.actions), vistrail.actions)
        vistrail.add_action(meta_a2, meta_a1.id, init_inner=True)
        vistrail.add_action(meta_a3, meta_a2.id, init_inner=True)
        vistrail.add_action(meta_a7, meta_a2.id)
        vistrail.add_action(meta_a4, meta_a7.id, init_inner=True)
        vistrail.add_action(meta_a8, meta_a4.id)
        vistrail.add_action(meta_a5, meta_a7.id, init_inner=True)
        vistrail.add_action(meta_a6, meta_a8.id, init_inner=True)
        vistrail.add_action(meta_a9, meta_a6.id)

        vistrail.addTag('meta_a3', meta_a3.id)
        vistrail.addTag('meta_a4', meta_a4.id)
        vistrail.addTag('meta_a5', meta_a5.id)
        vistrail.addTag('meta_a6', meta_a6.id)
        vistrail.addTag('meta_a7', meta_a7.id)
        vistrail.addTag('meta_a8', meta_a8.id)
        vistrail.addTag('meta_a9', meta_a9.id)

        return vistrail


    def test_meta_vistrail(self):
        mvt = self.create_vistrail()

        # for a in mvt.actions:
        #     print(a.id, a.parent, [[op.vtType, op.what] for op in a.operations])

        vt = mvt.getVistrail("meta_a7")
        self.assertEqual(len(vt.actions), 2)
        # self.assertEqual(vt.actions[0].operations[0].data.name, 'Float')
        # print("MATERIALIZING PIPELINE", [[[a.id, op.vtType, op.what, op.old_obj_id, op.new_obj_id, op.parentObjId] for op in a.operations] for a in vt.actions])
        wf = vt.getPipeline(vt.get_latest_version())
        self.assertEqual(wf.module_list[0].name, "Float")
        self.assertEqual(len(vt.action_annotations), 1)
        self.assertTrue(vt.has_tag_str("float"))

        vt2 = mvt.getVistrail("meta_a8")
        self.assertEqual(len(vt2.actions), 2)
        # self.assertEqual(vt2.actions[0].operations[0].data.name, 'Integer')
        wf2 = vt2.getPipeline(vt2.get_latest_version())
        self.assertEqual(wf2.module_list[0].name, "Integer")
        self.assertEqual(len(vt2.action_annotations), 1)
        self.assertFalse(vt2.has_tag_str("float"))
        self.assertTrue(vt2.has_tag_str("integer"))

        vt3 = mvt.getVistrail("meta_a5")
        self.assertEqual(len(vt3.actions), 1)
        self.assertEqual(vt3.actions[0].operations[0].data.name, 'Float')
        wf3 = vt3.getPipeline(vt3.get_latest_version())
        self.assertEqual(wf3.module_list[0].name, "Float")
        self.assertEqual(len(vt3.action_annotations), 0)

        vt4 = mvt.getVistrail("meta_a9")
        self.assertEqual(len(vt4.actions), 3)
        # self.assertEqual(vt4.actions[0].operations[0].data.name, 'Integer')
        wf4 = vt4.getPipeline(vt4.get_latest_version())
        self.assertListEqual([m.name for m in wf4.module_list], ["Integer", "StandardOutput"])
        self.assertEqual(len(vt4.action_annotations), 2)
        self.assertTrue(vt4.has_tag_str("connected"))
        self.assertTrue(vt4.has_tag_str("integer"))
        self.assertFalse(vt4.has_tag_str("float"))


def load_tests(loader, tests, pattern):
    return loader.loadTestsFromName('vistrails.core.vistrail.vistrail.TestMetaVistrail')

if __name__ == '__main__':
    unittest.main()
