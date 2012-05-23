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
""" This file contains the definition of the class Vistrail """

import copy
import datetime
import getpass

from db.domain import DBVistrail
from db.services.io import open_vt_log_from_db, open_log_from_xml
from core.db.locator import DBLocator
from core.log.log import Log
from core.data_structures.graph import Graph
from core.data_structures.bijectivedict import Bidict
from core import debug
import core.db.io
from core.utils import VistrailsInternalError, \
     InvalidPipeline
from core.vistrail.action import Action
from core.vistrail.action_annotation import ActionAnnotation
from core.vistrail.annotation import Annotation
from core.vistrail.module import Module
from core.vistrail.module_function import ModuleFunction
from core.vistrail.module_param import ModuleParam
from core.vistrail.operation import AddOp, ChangeOp, DeleteOp
from core.vistrail.plugin_data import PluginData
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

        self.locator = locator
        self.set_defaults()

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
        else:
            self.changed = other.changed
            self.currentVersion = other.currentVersion
            self.savedQueries = copy.copy(other.savedQueries)
            self.is_abstraction = other.is_abstraction

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
# 	for tag in _vistrail.tags:
#             Tag.convert(tag)
        for annotation in _vistrail.annotations:
            Annotation.convert(annotation)
        for annotation in _vistrail.action_annotations:
            ActionAnnotation.convert(annotation)

        _vistrail.set_defaults()

    ##########################################################################
    # Constants

    TAG_ANNOTATION = '__tag__'
    NOTES_ANNOTATION = '__notes__'
    PARAMEXP_ANNOTATION = '__paramexp__'
    THUMBNAIL_ANNOTATION = '__thumb__'
    PRUNE_ANNOTATION = '__prune__'
    UPGRADE_ANNOTATION = '__upgrade__'
    VARIABLES_ANNOTATION = '__vistrail_vars__'

    ##########################################################################
    # Properties

    id = DBVistrail.db_id
    actions = DBVistrail.db_actions # This is now read-write
    tags = DBVistrail.db_tags # This is now read-write
    annotations = DBVistrail.db_annotations
    action_annotations = DBVistrail.db_actionAnnotations
    
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
        if not (value is None or (type(value) == str and value.strip() == '')):
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
    
    def _get_vistrail_vars(self):
        annotation = self.get_annotation(Vistrail.VARIABLES_ANNOTATION)
        if annotation is not None:
            return dict(eval(annotation.value))
        else:
            return {}
    
    def _set_vistrail_vars(self, value):
        if type(value) == type('') and value.strip() == '':
            value = '{}'
        return self.set_annotation(Vistrail.VARIABLES_ANNOTATION, str(value))
    vistrail_vars = property(_get_vistrail_vars, _set_vistrail_vars)
    
    def has_vistrail_var(self, name):
        return name in self.vistrail_vars
    
    def get_vistrail_var(self, name):
        if name in self.vistrail_vars:
            return self.vistrail_vars[name]
        return None
    
    def set_vistrail_var(self, name, value):
        vardict = self.vistrail_vars
        if name in vardict:
            if vardict[name] == value:
                return False
            if value is None:
                del vardict[name]
                self.vistrail_vars = vardict
                return True
        if value is None:
            return False
        vardict[name] = value
        self.vistrail_vars = vardict
        return True

    def getVersionName(self, version):
        """ getVersionName(version) -> str 
        Returns the name of a version, if it exists. Returns an empty string
        if it doesn't. 
        
        """
        if self.has_tag(version):
            return self.get_tag(version)
        return ""

    def get_version_count(self):
        """get_version_count() -> Integer
        Returns the total number of versions in this vistrail.

        """
        return len(self.actionMap)

    def get_version_number(self, version):
        """get_version_number(version) -> Integer
        Returns the version number given a tag.

        """
        return self.get_tag_str(version).action_id
    
    def get_latest_version(self):
        """get_latest_version() -> Integer
        Returns the latest version id for the vistrail.

        FIXME: Running time O(|versions|)

        FIXME: Check if pruning is handled correctly here.

        """
        try:
            desc_key = Action.ANNOTATION_DESCRIPTION
            # Get the max id of all actions (excluding upgrade actions)
            max_ver = max(v.id for v in self.actions if not self.is_pruned(v.id) and not (v.has_annotation_with_key(desc_key) and v.get_annotation_by_key(desc_key).value == 'Upgrade'))
            # If that action has an upgrade, use it
            if self.has_upgrade(max_ver):
                max_ver = long(self.get_upgrade(max_ver))
            return max_ver
        except:
            return 0
                   
    def getPipeline(self, version):
        """getPipeline(number or tagname) -> Pipeline
        Return a pipeline object given a version number or a version name. 

        """
        try:
            return Vistrail.getPipelineDispatcher[type(version)](self, version)
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
        workflow = core.db.io.get_workflow(self, version)
        return workflow

    def make_actions_from_diff(self, diff):
        """ make_actions_from_diff(diff) -> [action]
        Returns a sequence of actions that performs the diff.

        (The point is that this might be smaller than the
        algebra-based one).
        """
        (p1,
         p2,
         m_shared,
         m_to_be_deleted,
         m_to_be_added,
         parameter_changes,
         c_shared,
         c_to_be_deleted,
         c_to_be_added) = (diff.p1,
                           diff.p2,
                           diff.v1andv2,
                           diff.v1only,
                           diff.v2only,
                           diff.paramchanged,
                           diff.c1andc2,
                           diff.c1only,
                           diff.c2only)

        p1_c = copy.copy(p1)
        result = []

        module_id_remap = Bidict()
        module_id_remap.update(m_shared)

        connection_id_remap = Bidict()
        connection_id_remap.update(c_shared)
        
        for ((m_id_from, m_id_to), _) in parameter_changes:
            module_id_remap[m_id_from] = m_id_to

        # First all the modules to get the remap
        for p2_m_id in m_to_be_added:
            add_module = AddModuleAction()
            add_module.module = copy.copy(p2.modules[p2_m_id])
            add_module.module.id = p1_c.fresh_module_id()
            module_id_remap[add_module.module.id] = p2_m_id
            result.append(add_module)
            add_module.perform(p1_c)


        # Then all the connections using the remap
        for p2_c_id in c_to_be_added:
            c2 = p2.connections[p2_c_id]
            add_connection = AddConnectionAction()
            new_c = copy.copy(c2)
            add_connection.connection = new_c
            new_c.id = p1_c.fresh_connection_id()
            new_c.sourceId = module_id_remap.inverse[c2.sourceId]
            new_c.destinationId = module_id_remap.inverse[c2.destinationId]
            connection_id_remap[c2.id] = new_c.id
            result.append(add_connection)
            add_connection.perform(p1_c)


        # Now delete all connections:
        delete_conns = DeleteConnectionAction()
        delete_conns.ids = copy.copy(c_to_be_deleted)
        if len(delete_conns.ids) > 0:
            delete_conns.perform(p1_c)
            result.append(delete_conns)

        # And then all the modules
        delete_modules = DeleteModuleAction()
        delete_modules.ids = copy.copy(m_to_be_deleted)
        if len(delete_modules.ids) > 0:
            delete_modules.perform(p1_c)
            result.append(delete_modules)

        # From now on, module_id_remap is not necessary, we can act
        # on p1 ids without worry. (they still exist)

        # Now move everyone
        move_action = MoveModuleAction()
        for (p1_m_id, p2_m_id) in m_shared.iteritems():
            delta = p2.modules[p2_m_id].location - p1.modules[p1_m_id].location
            move_action.addMove(p1_m_id, delta.x, delta.y)
        move_action.perform(p1_c)
        result.append(move_action)

        # Now change parameters
        def make_param_change(fto_name, fto_params,
                              m_id, f_id, m):
            action = ChangeParameterAction()
            for (p_id, param) in enumerate(fto_params):
                p_name = m.functions[f_id].params[p_id].name
                p_alias = m.functions[f_id].params[p_id].alias
                (p_type, p_value) = param
                action.addParameter(m_id, f_id, p_id, fto_name,
                                    p_name, p_value, p_type, p_alias)
            return action
        
        if len(parameter_changes):
            # print parameter_changes
            for ((m_from_id, m_to_id), plist) in parameter_changes:
                m_from = p1.modules[m_to_id]
                for ((ffrom_name, ffrom_params),
                     (fto_name, fto_params)) in plist:
                    for (f_id, f) in enumerate(m_from.functions):
                        if f.name != fto_name: continue
                        new_action = make_param_change(fto_name,
                                                       fto_params,
                                                       m_from_id,
                                                       f_id,
                                                       m_from)
                        new_action.perform(p1_c)
                        result.append(new_action)

        return (result,
                module_id_remap,
                connection_id_remap)

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
                    [shared connections (id in v1, id in v2) ...],
                    [shared connections [heuristic] (id in v1, id in v2)],
                    [c1 not in v2 connections],
                    [c2 not in v1 connections])

        parameter-changed modules = [((module id in v1, module id in v2),
                                      [(function in v1, function in v2)...]),
                                      ...]
        
        """
        return core.db.io.get_workflow_diff_with_connections((self, v1), 
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
                    [parameter-changed modules (see-below)])

        parameter-changed modules = [((module id in v1, module id in v2),
                                      [(function in v1, function in v2)...]),
                                      ...]
        
        """
        return core.db.io.get_workflow_diff((self, v1), (self, v2))
                        
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
        while  t != 0:
            t1.add(t)
            t = self.actionMap[t].parent
        
        t = v2
        while t != 0:
            if t in t1:
                return t
            t = self.actionMap[t].parent
        return 0
    
    def getLastCommonVersion(self, v):
        """getLastCommonVersion(v: Vistrail) -> int
        Returns the last version that is common to this vistrail and v
	
        """
        # TODO:  There HAS to be a better way to do this...
        common = []
        for action in self.actionMap:
            if(v.hasVersion(action.timestep)):
                common.append(action.timestep)
                
        timestep = 0
        for time in common:
            if time > timestep:
                timestep = time

        return timestep	

    def general_action_chain(self, v1, v2):
        """general_action_chain(v1, v2): Returns an action that turns
        pipeline v1 into v2."""

        return core.db.io.getPathAsAction(self, v1, v2)
    
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
            sorted_keys = sorted(self.actionMap.keys())
            last_n = sorted_keys[num_actions-n:num_actions-1]
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
        if type(tag) == type(0) or type(tag) == type(0L):
            return self.has_tag(tag)
        elif type(tag) == type('str'):
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
        return self.has_action_annotation(action_id,
                                          Vistrail.PARAMEXP_ANNOTATION)
    def get_paramexp(self, action_id):
        a = self.get_action_annotation(action_id, 
                                       Vistrail.PARAMEXP_ANNOTATION)
        if a is not None:
            return a.value
        return None
    def set_paramexp(self, action_id, value):
        return self.set_action_annotation(action_id,
                                          Vistrail.PARAMEXP_ANNOTATION,
                                          value)

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
        if type(value) == type(True):
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
            # Recurse to get the newest upgrade in case there are multiple chained upgrades
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
        description = ""
        if version_number in self.actionMap:
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
            added_ports = 0
            moved_modules = 0
            changed_parameters = 0
            changed_annotations = 0
            deleted_modules = 0
            deleted_connections = 0
            deleted_parameters = 0
            deleted_functions = 0
            deleted_annotations = 0
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
                    elif op.what == 'port':
                        deleted_ports += 1
                else:
                    raise Exception("Unknown operation type '%s'" % op.vtType)

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
            elif deleted_annotations:
                description = "Deleted annotation"
                if deleted_annotations > 1:
                    description += "s"
            elif deleted_ports:
                description = "Deleted port"
                if deleted_ports > 1:
                    description += "s"
        return description

    # FIXME: remove this function (left here only for transition)
    def getVersionGraph(self):
        """getVersionGraph() -> Graph 
        Returns the version graph
        
        """
        result = Graph()
        result.add_vertex(0)

        # the sorting is for the display using graphviz
        # we want to always add nodes from left to right
        for action in sorted(self.actionMap.itervalues(), 
                             key=lambda x: x.timestep):
            # We need to check the presence of the parent's timestep
            # on the graph because it might have been previously
            # pruned. Remember that pruning is only marked for the
            # topmost invisible action.
            if (action.parent in result.vertices and
                not self.is_pruned(action.id)):
                result.add_edge(action.parent,
                                action.timestep,
                               0)
        return result

    def getDate(self):
        """ getDate() -> str - Returns the current date and time. """
    #	return time.strftime("%d %b %Y %H:%M:%S", time.localtime())
        return datetime.datetime.now()
    
    def getUser(self):
        """ getUser() -> str - Returns the username. """
        return getpass.getuser()

    def serialize(self, filename):
        pass

    def pruneVersion(self, version):
        """ pruneVersion(version: int) -> None
        Add a version into the prunedVersion set
        
        """
        tagMap = self.get_tagMap()
        if version!=0: # not root
            def delete_tag(version):
                if version in tagMap:
                    # delete tag
                    self.set_tag(version, '')
            current_graph = self.getVersionGraph()
            current_graph.dfs(vertex_set=[version], enter_vertex=delete_tag)
            self.set_prune(version, str(True))

            # self.prunedVersions.add(version)

    def hideVersion(self, version):
        """ hideVersion(version: int) -> None
        Set the prune flag for the version

        """
        if version != 0:
            self.set_prune(version, str(True))

    def showVersion(self, version):
        """ showVersion(version: int) -> None
        Set the prune flag for the version

        """
        if version != 0:
            self.set_prune(version, str(False))

    def expandVersion(self, version):
        """ expandVersion(version: int) -> None
        Set the expand flag for the version
        
        """
        if version!=0: # not root
            self.actionMap[version].expand = 1

    def collapseVersion(self, version):
        """ collapseVersion(version: int) -> None
        Reset the expand flag for the version
        
        """
        if version!=0:
            self.actionMap[version].expand = 0

    def setSavedQueries(self, savedQueries):
        """ setSavedQueries(savedQueries: list of (str, str, str)) -> None
        Set the saved queries of this vistrail
        
        """
        self.savedQueries = savedQueries

    # Dispatch in runtime according to type
    getPipelineDispatcher = {}
    getPipelineDispatcher[type(0)] = getPipelineVersionNumber
    getPipelineDispatcher[type(0L)] = getPipelineVersionNumber
    getPipelineDispatcher[type('0')] = getPipelineVersionName

    class InvalidAbstraction(Exception):
        pass

    def create_abstraction(self,
                           pipeline_version,
                           subgraph,
                           abstraction_name):
        pipeline = self.getPipeline(pipeline_version)
        current_graph = pipeline.graph
        if not current_graph.topologically_contractible(subgraph):
            msg = "Abstraction violates DAG constraints."
            raise self.InvalidAbstraction(msg)
        input_ports = current_graph.connections_to_subgraph(subgraph)
        output_ports = current_graph.connections_from_subgraph(subgraph)

        # Recreate pipeline from empty version
        sub_pipeline = pipeline.get_subpipeline(subgraph)
        actions = sub_pipeline.dump_actions()

        for (frm, to, conn_id) in input_ports:
            fresh_id = sub_pipeline.fresh_module_id()
            m = Module()
            m.id = fresh_id
            m.location = copy.copy(pipeline.modules[frm].location)
            m.name = "InputPort"
            actions.append(m)

            c = core.vistrail.connection.Connection()
            fresh_id = sub_pipeline.fresh_connection_id()
            c.id = fresh_id

        raise Exception("not finished")
    
    def get_persisted_log(self):
        """
        Returns the log object for this vistrail if available
        """
        log = Log()
        if type(self.locator) == core.db.locator.ZIPFileLocator:
            if self.db_log_filename is not None:
                log = open_log_from_xml(self.db_log_filename, True)
        if type(self.locator) == core.db.locator.DBLocator:
            connection = self.locator.get_connection()
            log = open_vt_log_from_db(connection, self.db_id)
        Log.convert(log)
        return log
    
    def get_used_packages(self):
        package_list = {}
        for action in self.actions:
            for op in action.operations:
                try:
                    if type(op) == AddOp and op.what == 'module':
                        package_list[op.data.package] = op.data.package
                except:
                    pass
        return package_list
                    

##############################################################################

class ExplicitExpandedVersionTree(object):
    """
    Keep explicit expanded and tersed version 
    trees.
    """
    def __init__(self, vistrail):
        self.vistrail = vistrail
        self.expandedVersionTree = Graph()
        self.expandedVersionTree.add_vertex(0)
        self.tersedVersionTree = Graph()

    def addVersion(self, id, prevId):
        # print "add version %d child of %d" % (id, prevId)
        self.expandedVersionTree.add_vertex(id)
        self.expandedVersionTree.add_edge(prevId,id,0)
    
    def getVersionTree(self):
        return self.expandedVersionTree
        
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

import unittest
import copy
import random

class TestVistrail(unittest.TestCase):

    def create_vistrail(self):
        vistrail = Vistrail()

        m = Module(id=vistrail.idScope.getNewId(Module.vtType),
                   name='Float',
                   package='edu.utah.sci.vistrails.basic')
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
        import core.db.io
        v1 = self.create_vistrail()
        xml_str = core.db.io.serialize(v1)
        v2 = core.db.io.unserialize(xml_str, Vistrail)
        # FIXME add checks for equality

    def test1(self):
        import core.vistrail
        from core.db.locator import XMLFileLocator
        import core.system
        v = XMLFileLocator(core.system.vistrails_root_directory() +
                           '/tests/resources/dummy.xml').load()
        #testing nodes in different branches
        v1 = 36
        v2 = 41
        p1 = v.getFirstCommonVersion(v1,v2)
        p2 = v.getFirstCommonVersion(v2,v1)
        self.assertEquals(p1,p2)
        
        #testing nodes in the same branch
        v1 = 15
        v2 = 36
        p1 = v.getFirstCommonVersion(v1,v2)
        p2 = v.getFirstCommonVersion(v2,v1)
        self.assertEquals(p1,p2)

        if p1 == 0 or p2 == 0:
            self.fail("vistrails tree is not single rooted.")

    def test2(self):
        import core.vistrail
        from core.db.locator import XMLFileLocator
        import core.system
        v = XMLFileLocator(core.system.vistrails_root_directory() +
                           '/tests/resources/dummy.xml').load()
        #testing diff
        v1 = 17
        v2 = 27
        v3 = 22
        v.get_pipeline_diff(v1,v2)
        v.get_pipeline_diff(v1,v3)

    def test_empty_action_chain(self):
        """Tests calling action chain on empty version."""
        v = Vistrail()
        p = v.getPipeline(0)

    def test_empty_action_chain_2(self):
        from core.db.locator import XMLFileLocator
        import core.system
        v = XMLFileLocator(core.system.vistrails_root_directory() +
                           '/tests/resources/dummy.xml').load()
        assert v.actionChain(17, 17) == []

    def test_get_version_negative_one(self):
        """Tests getting the 'no version' vistrail. This should raise
        VistrailsDBException.

        """
        v = Vistrail()
        self.assertRaises(InvalidPipeline, lambda: v.getPipeline(-1))

    def test_version_graph(self):
        from core.db.locator import XMLFileLocator
        import core.system
        v = XMLFileLocator(core.system.vistrails_root_directory() +
                           '/tests/resources/dummy.xml').load()
        v.getVersionGraph()

    def test_plugin_info(self):
        import core.db.io
        plugin_info_str = "this is a test of plugin_info"
        v1 = self.create_vistrail()
        v1.plugin_info = plugin_info_str
        xml_str = core.db.io.serialize(v1)
        v2 = core.db.io.unserialize(xml_str, Vistrail)
        assert plugin_info_str == v2.plugin_info

    def test_database_info(self):
        import core.db.io
        database_info_str = "db.hostname.edu:3306:TABLE_NAME"
        v1 = self.create_vistrail()
        v1.database_info = database_info_str
        xml_str = core.db.io.serialize(v1)
        v2 = core.db.io.unserialize(xml_str, Vistrail)
        assert database_info_str == v2.database_info

    def test_plugin_data(self):
        import core.db.io
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
        v1.add_action(action, 0)
        workflow = v1.getPipeline(action.id)
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
        from core.db.locator import XMLFileLocator
        from core.db.locator import FileLocator
        import core.system
        import sys

        def do_test(filename, locator_class, old_v=None, new_v=None):
            v = locator_class(core.system.vistrails_root_directory() +
                               filename).load()
            if type(v) != Vistrail:
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

#     def test_abstraction(self):
#         import core.vistrail
#         import core.xml_parser
#         parser = core.xml_parser.XMLParser()
#         parser.openVistrail(core.system.vistrails_root_directory() +
#                             '/tests/resources/ect.xml')
#         v = parser.getVistrail()
#         parser.closeVistrail()
#         #testing diff
#         p = v.getPipeline('WindowedSync (lambda-mu) Error')
#         version = v.get_version_number('WindowedSync (lambda-mu) Error')
#         sub = p.graph.subgraph([43, 45])
#         v.create_abstraction(version, sub, "FOOBAR")

if __name__ == '__main__':
    unittest.main()
