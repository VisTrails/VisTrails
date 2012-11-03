###############################################################################
##
## Copyright (C) 2011-2012, NYU-Poly.
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

"""generated automatically by auto_dao.py"""

from core.system import get_elementtree_library
ElementTree = get_elementtree_library()

from xml_dao import XMLDAO
from db.versions.v1_0_3.domain import *

class DBOpmProcessIdEffectXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'effect':
            return None
        
        # read attributes
        data = node.get('id', None)
        id = self.convertFromStr(data, 'str')
        
        obj = DBOpmProcessIdEffect(id=id)
        obj.is_dirty = False
        return obj
    
    def toXML(self, opm_process_id_effect, node=None):
        if node is None:
            node = ElementTree.Element('effect')
        
        # set attributes
        node.set('id',self.convertToStr(opm_process_id_effect.db_id, 'str'))
        
        return node

class DBVistrailVariableXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'vistrailVariable':
            return None
        
        # read attributes
        data = node.get('name', None)
        name = self.convertFromStr(data, 'str')
        data = node.get('uuid', None)
        uuid = self.convertFromStr(data, 'str')
        data = node.get('package', None)
        package = self.convertFromStr(data, 'str')
        data = node.get('module', None)
        module = self.convertFromStr(data, 'str')
        data = node.get('namespace', None)
        namespace = self.convertFromStr(data, 'str')
        data = node.get('value', None)
        value = self.convertFromStr(data, 'str')
        
        obj = DBVistrailVariable(name=name,
                                 uuid=uuid,
                                 package=package,
                                 module=module,
                                 namespace=namespace,
                                 value=value)
        obj.is_dirty = False
        return obj
    
    def toXML(self, vistrailVariable, node=None):
        if node is None:
            node = ElementTree.Element('vistrailVariable')
        
        # set attributes
        node.set('name',self.convertToStr(vistrailVariable.db_name, 'str'))
        node.set('uuid',self.convertToStr(vistrailVariable.db_uuid, 'str'))
        node.set('package',self.convertToStr(vistrailVariable.db_package, 'str'))
        node.set('module',self.convertToStr(vistrailVariable.db_module, 'str'))
        node.set('namespace',self.convertToStr(vistrailVariable.db_namespace, 'str'))
        node.set('value',self.convertToStr(vistrailVariable.db_value, 'str'))
        
        return node

class DBOpmWasGeneratedByXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'wasGeneratedBy':
            return None
        
        effect = None
        role = None
        cause = None
        accounts = []
        opm_times = []
        
        # read children
        for child in node.getchildren():
            if child.tag[0] == "{":
                child_tag = child.tag.split("}")[1]
            else:
                child_tag = child.tag
            if child_tag == 'effect':
                _data = self.getDao('opm_artifact_id_effect').fromXML(child)
                effect = _data
            elif child_tag == 'role':
                _data = self.getDao('opm_role').fromXML(child)
                role = _data
            elif child_tag == 'cause':
                _data = self.getDao('opm_process_id_cause').fromXML(child)
                cause = _data
            elif child_tag == 'account':
                _data = self.getDao('opm_account_id').fromXML(child)
                accounts.append(_data)
            elif child_tag == 'time':
                _data = self.getDao('opm_time').fromXML(child)
                opm_times.append(_data)
            elif child.text is None or child.text.strip() == '':
                pass
            else:
                print '*** ERROR *** tag = %s' % child.tag
        
        obj = DBOpmWasGeneratedBy(effect=effect,
                                  role=role,
                                  cause=cause,
                                  accounts=accounts,
                                  opm_times=opm_times)
        obj.is_dirty = False
        return obj
    
    def toXML(self, opm_was_generated_by, node=None):
        if node is None:
            node = ElementTree.Element('wasGeneratedBy')
        
        # set elements
        effect = opm_was_generated_by.db_effect
        if effect is not None:
            childNode = ElementTree.SubElement(node, 'effect')
            self.getDao('opm_artifact_id_effect').toXML(effect, childNode)
        role = opm_was_generated_by.db_role
        if role is not None:
            childNode = ElementTree.SubElement(node, 'role')
            self.getDao('opm_role').toXML(role, childNode)
        cause = opm_was_generated_by.db_cause
        if cause is not None:
            childNode = ElementTree.SubElement(node, 'cause')
            self.getDao('opm_process_id_cause').toXML(cause, childNode)
        accounts = opm_was_generated_by.db_accounts
        for account in accounts:
            childNode = ElementTree.SubElement(node, 'account')
            self.getDao('opm_account_id').toXML(account, childNode)
        opm_times = opm_was_generated_by.db_opm_times
        for opm_time in opm_times:
            childNode = ElementTree.SubElement(node, 'time')
            self.getDao('opm_time').toXML(opm_time, childNode)
        
        return node

class DBOpmAccountsXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'accounts':
            return None
        
        accounts = []
        opm_overlapss = []
        
        # read children
        for child in node.getchildren():
            if child.tag[0] == "{":
                child_tag = child.tag.split("}")[1]
            else:
                child_tag = child.tag
            if child_tag == 'account':
                _data = self.getDao('opm_account').fromXML(child)
                accounts.append(_data)
            elif child_tag == 'overlaps':
                _data = self.getDao('opm_overlaps').fromXML(child)
                opm_overlapss.append(_data)
            elif child.text is None or child.text.strip() == '':
                pass
            else:
                print '*** ERROR *** tag = %s' % child.tag
        
        obj = DBOpmAccounts(accounts=accounts,
                            opm_overlapss=opm_overlapss)
        obj.is_dirty = False
        return obj
    
    def toXML(self, opm_accounts, node=None):
        if node is None:
            node = ElementTree.Element('accounts')
        
        # set elements
        accounts = opm_accounts.db_accounts
        for account in accounts:
            childNode = ElementTree.SubElement(node, 'account')
            self.getDao('opm_account').toXML(account, childNode)
        opm_overlapss = opm_accounts.db_opm_overlapss
        for opm_overlaps in opm_overlapss:
            childNode = ElementTree.SubElement(node, 'overlaps')
            self.getDao('opm_overlaps').toXML(opm_overlaps, childNode)
        
        return node

class DBPortSpecXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'portSpec':
            return None
        
        # read attributes
        data = node.get('id', None)
        id = self.convertFromStr(data, 'long')
        data = node.get('name', None)
        name = self.convertFromStr(data, 'str')
        data = node.get('type', None)
        type = self.convertFromStr(data, 'str')
        data = node.get('optional', None)
        optional = self.convertFromStr(data, 'int')
        data = node.get('sortKey', None)
        sort_key = self.convertFromStr(data, 'int')
        data = node.get('minConns', None)
        min_conns = self.convertFromStr(data, 'int')
        data = node.get('maxConns', None)
        max_conns = self.convertFromStr(data, 'int')
        
        portSpecItems = []
        
        # read children
        for child in node.getchildren():
            if child.tag[0] == "{":
                child_tag = child.tag.split("}")[1]
            else:
                child_tag = child.tag
            if child_tag == 'portSpecItem':
                _data = self.getDao('portSpecItem').fromXML(child)
                portSpecItems.append(_data)
            elif child.text is None or child.text.strip() == '':
                pass
            else:
                print '*** ERROR *** tag = %s' % child.tag
        
        obj = DBPortSpec(id=id,
                         name=name,
                         type=type,
                         optional=optional,
                         sort_key=sort_key,
                         portSpecItems=portSpecItems,
                         min_conns=min_conns,
                         max_conns=max_conns)
        obj.is_dirty = False
        return obj
    
    def toXML(self, portSpec, node=None):
        if node is None:
            node = ElementTree.Element('portSpec')
        
        # set attributes
        node.set('id',self.convertToStr(portSpec.db_id, 'long'))
        node.set('name',self.convertToStr(portSpec.db_name, 'str'))
        node.set('type',self.convertToStr(portSpec.db_type, 'str'))
        node.set('optional',self.convertToStr(portSpec.db_optional, 'int'))
        node.set('sortKey',self.convertToStr(portSpec.db_sort_key, 'int'))
        node.set('minConns',self.convertToStr(portSpec.db_min_conns, 'int'))
        node.set('maxConns',self.convertToStr(portSpec.db_max_conns, 'int'))
        
        # set elements
        portSpecItems = portSpec.db_portSpecItems
        for portSpecItem in portSpecItems:
            childNode = ElementTree.SubElement(node, 'portSpecItem')
            self.getDao('portSpecItem').toXML(portSpecItem, childNode)
        
        return node

class DBModuleXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'module':
            return None
        
        # read attributes
        data = node.get('id', None)
        id = self.convertFromStr(data, 'long')
        data = node.get('cache', None)
        cache = self.convertFromStr(data, 'int')
        data = node.get('name', None)
        name = self.convertFromStr(data, 'str')
        data = node.get('namespace', None)
        namespace = self.convertFromStr(data, 'str')
        data = node.get('package', None)
        package = self.convertFromStr(data, 'str')
        data = node.get('version', None)
        version = self.convertFromStr(data, 'str')
        
        location = None
        functions = []
        annotations = []
        portSpecs = []
        
        # read children
        for child in node.getchildren():
            if child.tag[0] == "{":
                child_tag = child.tag.split("}")[1]
            else:
                child_tag = child.tag
            if child_tag == 'location':
                _data = self.getDao('location').fromXML(child)
                location = _data
            elif child_tag == 'function':
                _data = self.getDao('function').fromXML(child)
                functions.append(_data)
            elif child_tag == 'annotation':
                _data = self.getDao('annotation').fromXML(child)
                annotations.append(_data)
            elif child_tag == 'portSpec':
                _data = self.getDao('portSpec').fromXML(child)
                portSpecs.append(_data)
            elif child.text is None or child.text.strip() == '':
                pass
            else:
                print '*** ERROR *** tag = %s' % child.tag
        
        obj = DBModule(id=id,
                       cache=cache,
                       name=name,
                       namespace=namespace,
                       package=package,
                       version=version,
                       location=location,
                       functions=functions,
                       annotations=annotations,
                       portSpecs=portSpecs)
        obj.is_dirty = False
        return obj
    
    def toXML(self, module, node=None):
        if node is None:
            node = ElementTree.Element('module')
        
        # set attributes
        node.set('id',self.convertToStr(module.db_id, 'long'))
        node.set('cache',self.convertToStr(module.db_cache, 'int'))
        node.set('name',self.convertToStr(module.db_name, 'str'))
        node.set('namespace',self.convertToStr(module.db_namespace, 'str'))
        node.set('package',self.convertToStr(module.db_package, 'str'))
        node.set('version',self.convertToStr(module.db_version, 'str'))
        
        # set elements
        location = module.db_location
        if location is not None:
            childNode = ElementTree.SubElement(node, 'location')
            self.getDao('location').toXML(location, childNode)
        functions = module.db_functions
        for function in functions:
            childNode = ElementTree.SubElement(node, 'function')
            self.getDao('function').toXML(function, childNode)
        annotations = module.db_annotations
        for annotation in annotations:
            childNode = ElementTree.SubElement(node, 'annotation')
            self.getDao('annotation').toXML(annotation, childNode)
        portSpecs = module.db_portSpecs
        for portSpec in portSpecs:
            childNode = ElementTree.SubElement(node, 'portSpec')
            self.getDao('portSpec').toXML(portSpec, childNode)
        
        return node

class DBModuleDescriptorXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'moduleDescriptor':
            return None
        
        # read attributes
        data = node.get('id', None)
        id = self.convertFromStr(data, 'long')
        data = node.get('name', None)
        name = self.convertFromStr(data, 'str')
        data = node.get('package', None)
        package = self.convertFromStr(data, 'str')
        data = node.get('namespace', None)
        namespace = self.convertFromStr(data, 'str')
        data = node.get('packageVersion', None)
        package_version = self.convertFromStr(data, 'str')
        data = node.get('version', None)
        version = self.convertFromStr(data, 'str')
        data = node.get('baseDescriptorId', None)
        base_descriptor_id = self.convertFromStr(data, 'long')
        
        portSpecs = []
        
        # read children
        for child in node.getchildren():
            if child.tag[0] == "{":
                child_tag = child.tag.split("}")[1]
            else:
                child_tag = child.tag
            if child_tag == 'portSpec':
                _data = self.getDao('portSpec').fromXML(child)
                portSpecs.append(_data)
            elif child.text is None or child.text.strip() == '':
                pass
            else:
                print '*** ERROR *** tag = %s' % child.tag
        
        obj = DBModuleDescriptor(id=id,
                                 name=name,
                                 package=package,
                                 namespace=namespace,
                                 package_version=package_version,
                                 version=version,
                                 base_descriptor_id=base_descriptor_id,
                                 portSpecs=portSpecs)
        obj.is_dirty = False
        return obj
    
    def toXML(self, module_descriptor, node=None):
        if node is None:
            node = ElementTree.Element('moduleDescriptor')
        
        # set attributes
        node.set('id',self.convertToStr(module_descriptor.db_id, 'long'))
        node.set('name',self.convertToStr(module_descriptor.db_name, 'str'))
        node.set('package',self.convertToStr(module_descriptor.db_package, 'str'))
        node.set('namespace',self.convertToStr(module_descriptor.db_namespace, 'str'))
        node.set('packageVersion',self.convertToStr(module_descriptor.db_package_version, 'str'))
        node.set('version',self.convertToStr(module_descriptor.db_version, 'str'))
        node.set('baseDescriptorId',self.convertToStr(module_descriptor.db_base_descriptor_id, 'long'))
        
        # set elements
        portSpecs = module_descriptor.db_portSpecs
        for portSpec in portSpecs:
            childNode = ElementTree.SubElement(node, 'portSpec')
            self.getDao('portSpec').toXML(portSpec, childNode)
        
        return node

class DBTagXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'tag':
            return None
        
        # read attributes
        data = node.get('id', None)
        id = self.convertFromStr(data, 'long')
        data = node.get('name', None)
        name = self.convertFromStr(data, 'str')
        
        obj = DBTag(id=id,
                    name=name)
        obj.is_dirty = False
        return obj
    
    def toXML(self, tag, node=None):
        if node is None:
            node = ElementTree.Element('tag')
        
        # set attributes
        node.set('id',self.convertToStr(tag.db_id, 'long'))
        node.set('name',self.convertToStr(tag.db_name, 'str'))
        
        return node

class DBOpmRoleXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'role':
            return None
        
        # read attributes
        data = node.get('value', None)
        value = self.convertFromStr(data, 'str')
        
        obj = DBOpmRole(value=value)
        obj.is_dirty = False
        return obj
    
    def toXML(self, opm_role, node=None):
        if node is None:
            node = ElementTree.Element('role')
        
        # set attributes
        node.set('value',self.convertToStr(opm_role.db_value, 'str'))
        
        return node

class DBOpmProcessesXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'processes':
            return None
        
        processs = []
        
        # read children
        for child in node.getchildren():
            if child.tag[0] == "{":
                child_tag = child.tag.split("}")[1]
            else:
                child_tag = child.tag
            if child_tag == 'process':
                _data = self.getDao('opm_process').fromXML(child)
                processs.append(_data)
            elif child.text is None or child.text.strip() == '':
                pass
            else:
                print '*** ERROR *** tag = %s' % child.tag
        
        obj = DBOpmProcesses(processs=processs)
        obj.is_dirty = False
        return obj
    
    def toXML(self, opm_processes, node=None):
        if node is None:
            node = ElementTree.Element('processes')
        
        # set elements
        processs = opm_processes.db_processs
        for process in processs:
            childNode = ElementTree.SubElement(node, 'process')
            self.getDao('opm_process').toXML(process, childNode)
        
        return node

class DBOpmAccountIdXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'account':
            return None
        
        # read attributes
        data = node.get('id', None)
        id = self.convertFromStr(data, 'str')
        
        obj = DBOpmAccountId(id=id)
        obj.is_dirty = False
        return obj
    
    def toXML(self, opm_account_id, node=None):
        if node is None:
            node = ElementTree.Element('account')
        
        # set attributes
        node.set('id',self.convertToStr(opm_account_id.db_id, 'str'))
        
        return node

class DBPortXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'port':
            return None
        
        # read attributes
        data = node.get('id', None)
        id = self.convertFromStr(data, 'long')
        data = node.get('type', None)
        type = self.convertFromStr(data, 'str')
        data = node.get('moduleId', None)
        moduleId = self.convertFromStr(data, 'long')
        data = node.get('moduleName', None)
        moduleName = self.convertFromStr(data, 'str')
        data = node.get('name', None)
        name = self.convertFromStr(data, 'str')
        data = node.get('signature', None)
        signature = self.convertFromStr(data, 'str')
        
        obj = DBPort(id=id,
                     type=type,
                     moduleId=moduleId,
                     moduleName=moduleName,
                     name=name,
                     signature=signature)
        obj.is_dirty = False
        return obj
    
    def toXML(self, port, node=None):
        if node is None:
            node = ElementTree.Element('port')
        
        # set attributes
        node.set('id',self.convertToStr(port.db_id, 'long'))
        node.set('type',self.convertToStr(port.db_type, 'str'))
        node.set('moduleId',self.convertToStr(port.db_moduleId, 'long'))
        node.set('moduleName',self.convertToStr(port.db_moduleName, 'str'))
        node.set('name',self.convertToStr(port.db_name, 'str'))
        node.set('signature',self.convertToStr(port.db_signature, 'str'))
        
        return node

class DBProvActivitiesXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'activities':
            return None
        
        prov_activitys = []
        
        # read children
        for child in node.getchildren():
            if child.tag[0] == "{":
                child_tag = child.tag.split("}")[1]
            else:
                child_tag = child.tag
            if child_tag == 'prov:Activity':
                _data = self.getDao('prov_activity').fromXML(child)
                prov_activitys.append(_data)
            elif child.text is None or child.text.strip() == '':
                pass
            else:
                print '*** ERROR *** tag = %s' % child.tag
        
        obj = DBProvActivities(prov_activitys=prov_activitys)
        obj.is_dirty = False
        return obj
    
    def toXML(self, prov_activities, node=None):
        if node is None:
            node = ElementTree.Element('activities')
        
        # set elements
        prov_activitys = prov_activities.db_prov_activitys
        for prov_activity in prov_activitys:
            childNode = ElementTree.SubElement(node, 'prov:Activity')
            self.getDao('prov_activity').toXML(prov_activity, childNode)
        
        return node

class DBOpmArtifactXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'artifact':
            return None
        
        # read attributes
        data = node.get('id', None)
        id = self.convertFromStr(data, 'str')
        
        value = None
        accounts = []
        
        # read children
        for child in node.getchildren():
            if child.tag[0] == "{":
                child_tag = child.tag.split("}")[1]
            else:
                child_tag = child.tag
            if child_tag == 'value':
                _data = self.getDao('opm_artifact_value').fromXML(child)
                value = _data
            elif child_tag == 'account':
                _data = self.getDao('opm_account_id').fromXML(child)
                accounts.append(_data)
            elif child.text is None or child.text.strip() == '':
                pass
            else:
                print '*** ERROR *** tag = %s' % child.tag
        
        obj = DBOpmArtifact(id=id,
                            value=value,
                            accounts=accounts)
        obj.is_dirty = False
        return obj
    
    def toXML(self, opm_artifact, node=None):
        if node is None:
            node = ElementTree.Element('artifact')
        
        # set attributes
        node.set('id',self.convertToStr(opm_artifact.db_id, 'str'))
        
        # set elements
        value = opm_artifact.db_value
        if value is not None:
            childNode = ElementTree.SubElement(node, 'value')
            self.getDao('opm_artifact_value').toXML(value, childNode)
        accounts = opm_artifact.db_accounts
        for account in accounts:
            childNode = ElementTree.SubElement(node, 'account')
            self.getDao('opm_account_id').toXML(account, childNode)
        
        return node

class DBGroupXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'group':
            return None
        
        # read attributes
        data = node.get('id', None)
        id = self.convertFromStr(data, 'long')
        data = node.get('cache', None)
        cache = self.convertFromStr(data, 'int')
        data = node.get('name', None)
        name = self.convertFromStr(data, 'str')
        data = node.get('namespace', None)
        namespace = self.convertFromStr(data, 'str')
        data = node.get('package', None)
        package = self.convertFromStr(data, 'str')
        data = node.get('version', None)
        version = self.convertFromStr(data, 'str')
        
        workflow = None
        location = None
        functions = []
        annotations = []
        
        # read children
        for child in node.getchildren():
            if child.tag[0] == "{":
                child_tag = child.tag.split("}")[1]
            else:
                child_tag = child.tag
            if child_tag == 'workflow':
                _data = self.getDao('workflow').fromXML(child)
                workflow = _data
            elif child_tag == 'location':
                _data = self.getDao('location').fromXML(child)
                location = _data
            elif child_tag == 'function':
                _data = self.getDao('function').fromXML(child)
                functions.append(_data)
            elif child_tag == 'annotation':
                _data = self.getDao('annotation').fromXML(child)
                annotations.append(_data)
            elif child.text is None or child.text.strip() == '':
                pass
            else:
                print '*** ERROR *** tag = %s' % child.tag
        
        obj = DBGroup(id=id,
                      workflow=workflow,
                      cache=cache,
                      name=name,
                      namespace=namespace,
                      package=package,
                      version=version,
                      location=location,
                      functions=functions,
                      annotations=annotations)
        obj.is_dirty = False
        return obj
    
    def toXML(self, group, node=None):
        if node is None:
            node = ElementTree.Element('group')
        
        # set attributes
        node.set('id',self.convertToStr(group.db_id, 'long'))
        node.set('cache',self.convertToStr(group.db_cache, 'int'))
        node.set('name',self.convertToStr(group.db_name, 'str'))
        node.set('namespace',self.convertToStr(group.db_namespace, 'str'))
        node.set('package',self.convertToStr(group.db_package, 'str'))
        node.set('version',self.convertToStr(group.db_version, 'str'))
        
        # set elements
        workflow = group.db_workflow
        if workflow is not None:
            childNode = ElementTree.SubElement(node, 'workflow')
            self.getDao('workflow').toXML(workflow, childNode)
        location = group.db_location
        if location is not None:
            childNode = ElementTree.SubElement(node, 'location')
            self.getDao('location').toXML(location, childNode)
        functions = group.db_functions
        for function in functions:
            childNode = ElementTree.SubElement(node, 'function')
            self.getDao('function').toXML(function, childNode)
        annotations = group.db_annotations
        for annotation in annotations:
            childNode = ElementTree.SubElement(node, 'annotation')
            self.getDao('annotation').toXML(annotation, childNode)
        
        return node

class DBLogXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'log':
            return None
        
        # read attributes
        data = node.get('id', None)
        id = self.convertFromStr(data, 'long')
        data = node.get('version', None)
        version = self.convertFromStr(data, 'str')
        data = node.get('name', None)
        name = self.convertFromStr(data, 'str')
        data = node.get('vistrail_id', None)
        vistrail_id = self.convertFromStr(data, 'long')
        
        workflow_execs = []
        machines = []
        
        # read children
        for child in node.getchildren():
            if child.tag[0] == "{":
                child_tag = child.tag.split("}")[1]
            else:
                child_tag = child.tag
            if child_tag == 'workflowExec':
                _data = self.getDao('workflow_exec').fromXML(child)
                workflow_execs.append(_data)
            elif child_tag == 'machine':
                _data = self.getDao('machine').fromXML(child)
                machines.append(_data)
            elif child.text is None or child.text.strip() == '':
                pass
            else:
                print '*** ERROR *** tag = %s' % child.tag
        
        obj = DBLog(id=id,
                    version=version,
                    name=name,
                    workflow_execs=workflow_execs,
                    machines=machines,
                    vistrail_id=vistrail_id)
        obj.is_dirty = False
        return obj
    
    def toXML(self, log, node=None):
        if node is None:
            node = ElementTree.Element('log')
        
        # set attributes
        node.set('id',self.convertToStr(log.db_id, 'long'))
        node.set('version',self.convertToStr(log.db_version, 'str'))
        node.set('name',self.convertToStr(log.db_name, 'str'))
        node.set('vistrail_id',self.convertToStr(log.db_vistrail_id, 'long'))
        
        # set elements
        workflow_execs = log.db_workflow_execs
        for workflow_exec in workflow_execs:
            childNode = ElementTree.SubElement(node, 'workflowExec')
            self.getDao('workflow_exec').toXML(workflow_exec, childNode)
        machines = log.db_machines
        for machine in machines:
            childNode = ElementTree.SubElement(node, 'machine')
            self.getDao('machine').toXML(machine, childNode)
        
        return node

class DBOpmAgentsXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'agents':
            return None
        
        agents = []
        
        # read children
        for child in node.getchildren():
            if child.tag[0] == "{":
                child_tag = child.tag.split("}")[1]
            else:
                child_tag = child.tag
            if child_tag == 'agent':
                _data = self.getDao('opm_agent').fromXML(child)
                agents.append(_data)
            elif child.text is None or child.text.strip() == '':
                pass
            else:
                print '*** ERROR *** tag = %s' % child.tag
        
        obj = DBOpmAgents(agents=agents)
        obj.is_dirty = False
        return obj
    
    def toXML(self, opm_agents, node=None):
        if node is None:
            node = ElementTree.Element('agents')
        
        # set elements
        agents = opm_agents.db_agents
        for agent in agents:
            childNode = ElementTree.SubElement(node, 'agent')
            self.getDao('opm_agent').toXML(agent, childNode)
        
        return node

class DBOpmProcessIdCauseXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'cause':
            return None
        
        # read attributes
        data = node.get('id', None)
        id = self.convertFromStr(data, 'str')
        
        obj = DBOpmProcessIdCause(id=id)
        obj.is_dirty = False
        return obj
    
    def toXML(self, opm_process_id_cause, node=None):
        if node is None:
            node = ElementTree.Element('cause')
        
        # set attributes
        node.set('id',self.convertToStr(opm_process_id_cause.db_id, 'str'))
        
        return node

class DBProvGenerationXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'prov:Generation':
            return None
        
        # read attributes
        data = node.get('id', None)
        id = self.convertFromStr(data, 'str')
        data = node.get('prov:hadRole', None)
        prov_hadRole = self.convertFromStr(data, 'str')
        data = node.get('prov:Activity', None)
        prov_activity = self.convertFromStr(data, 'str')
        
        obj = DBProvGeneration(id=id,
                               prov_hadRole=prov_hadRole,
                               prov_activity=prov_activity)
        obj.is_dirty = False
        return obj
    
    def toXML(self, prov_generation, node=None):
        if node is None:
            node = ElementTree.Element('prov:Generation')
        
        # set attributes
        node.set('id',self.convertToStr(prov_generation.db_id, 'str'))
        node.set('prov:hadRole',self.convertToStr(prov_generation.db_prov_hadRole, 'str'))
        node.set('prov:Activity',self.convertToStr(prov_generation.db_prov_activity, 'str'))
        
        return node

class DBPortSpecItemXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'portSpecItem':
            return None
        
        # read attributes
        data = node.get('id', None)
        id = self.convertFromStr(data, 'long')
        data = node.get('pos', None)
        pos = self.convertFromStr(data, 'long')
        data = node.get('module', None)
        module = self.convertFromStr(data, 'str')
        data = node.get('package', None)
        package = self.convertFromStr(data, 'str')
        data = node.get('namespace', None)
        namespace = self.convertFromStr(data, 'str')
        data = node.get('label', None)
        label = self.convertFromStr(data, 'str')
        data = node.get('default', None)
        default = self.convertFromStr(data, 'str')
        data = node.get('values', None)
        values = self.convertFromStr(data, 'str')
        data = node.get('entryType', None)
        entry_type = self.convertFromStr(data, 'str')
        
        obj = DBPortSpecItem(id=id,
                             pos=pos,
                             module=module,
                             package=package,
                             namespace=namespace,
                             label=label,
                             default=default,
                             values=values,
                             entry_type=entry_type)
        obj.is_dirty = False
        return obj
    
    def toXML(self, portSpecItem, node=None):
        if node is None:
            node = ElementTree.Element('portSpecItem')
        
        # set attributes
        node.set('id',self.convertToStr(portSpecItem.db_id, 'long'))
        node.set('pos',self.convertToStr(portSpecItem.db_pos, 'long'))
        node.set('module',self.convertToStr(portSpecItem.db_module, 'str'))
        node.set('package',self.convertToStr(portSpecItem.db_package, 'str'))
        node.set('namespace',self.convertToStr(portSpecItem.db_namespace, 'str'))
        node.set('label',self.convertToStr(portSpecItem.db_label, 'str'))
        node.set('default',self.convertToStr(portSpecItem.db_default, 'str'))
        node.set('values',self.convertToStr(portSpecItem.db_values, 'str'))
        node.set('entryType',self.convertToStr(portSpecItem.db_entry_type, 'str'))
        
        return node

class DBMachineXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'machine':
            return None
        
        # read attributes
        data = node.get('id', None)
        id = self.convertFromStr(data, 'long')
        data = node.get('name', None)
        name = self.convertFromStr(data, 'str')
        data = node.get('os', None)
        os = self.convertFromStr(data, 'str')
        data = node.get('architecture', None)
        architecture = self.convertFromStr(data, 'str')
        data = node.get('processor', None)
        processor = self.convertFromStr(data, 'str')
        data = node.get('ram', None)
        ram = self.convertFromStr(data, 'int')
        
        obj = DBMachine(id=id,
                        name=name,
                        os=os,
                        architecture=architecture,
                        processor=processor,
                        ram=ram)
        obj.is_dirty = False
        return obj
    
    def toXML(self, machine, node=None):
        if node is None:
            node = ElementTree.Element('machine')
        
        # set attributes
        node.set('id',self.convertToStr(machine.db_id, 'long'))
        node.set('name',self.convertToStr(machine.db_name, 'str'))
        node.set('os',self.convertToStr(machine.db_os, 'str'))
        node.set('architecture',self.convertToStr(machine.db_architecture, 'str'))
        node.set('processor',self.convertToStr(machine.db_processor, 'str'))
        node.set('ram',self.convertToStr(machine.db_ram, 'int'))
        
        return node

class DBAddXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'add':
            return None
        
        # read attributes
        data = node.get('id', None)
        id = self.convertFromStr(data, 'long')
        data = node.get('what', None)
        what = self.convertFromStr(data, 'str')
        data = node.get('objectId', None)
        objectId = self.convertFromStr(data, 'long')
        data = node.get('parentObjId', None)
        parentObjId = self.convertFromStr(data, 'long')
        data = node.get('parentObjType', None)
        parentObjType = self.convertFromStr(data, 'str')
        
        data = None
        
        # read children
        for child in node.getchildren():
            if child.tag[0] == "{":
                child_tag = child.tag.split("}")[1]
            else:
                child_tag = child.tag
            if child_tag == 'module':
                _data = self.getDao('module').fromXML(child)
                data = _data
            elif child_tag == 'location':
                _data = self.getDao('location').fromXML(child)
                data = _data
            elif child_tag == 'annotation':
                _data = self.getDao('annotation').fromXML(child)
                data = _data
            elif child_tag == 'function':
                _data = self.getDao('function').fromXML(child)
                data = _data
            elif child_tag == 'connection':
                _data = self.getDao('connection').fromXML(child)
                data = _data
            elif child_tag == 'port':
                _data = self.getDao('port').fromXML(child)
                data = _data
            elif child_tag == 'parameter':
                _data = self.getDao('parameter').fromXML(child)
                data = _data
            elif child_tag == 'portSpec':
                _data = self.getDao('portSpec').fromXML(child)
                data = _data
            elif child_tag == 'abstraction':
                _data = self.getDao('abstraction').fromXML(child)
                data = _data
            elif child_tag == 'group':
                _data = self.getDao('group').fromXML(child)
                data = _data
            elif child_tag == 'other':
                _data = self.getDao('other').fromXML(child)
                data = _data
            elif child_tag == 'plugin_data':
                _data = self.getDao('plugin_data').fromXML(child)
                data = _data
            elif child.text is None or child.text.strip() == '':
                pass
            else:
                print '*** ERROR *** tag = %s' % child.tag
        
        obj = DBAdd(data=data,
                    id=id,
                    what=what,
                    objectId=objectId,
                    parentObjId=parentObjId,
                    parentObjType=parentObjType)
        obj.is_dirty = False
        return obj
    
    def toXML(self, add, node=None):
        if node is None:
            node = ElementTree.Element('add')
        
        # set attributes
        node.set('id',self.convertToStr(add.db_id, 'long'))
        node.set('what',self.convertToStr(add.db_what, 'str'))
        node.set('objectId',self.convertToStr(add.db_objectId, 'long'))
        node.set('parentObjId',self.convertToStr(add.db_parentObjId, 'long'))
        node.set('parentObjType',self.convertToStr(add.db_parentObjType, 'str'))
        
        # set elements
        data = add.db_data
        if data is not None:
            if data.vtType == 'module':
                childNode = ElementTree.SubElement(node, 'module')
                self.getDao('module').toXML(data, childNode)
            elif data.vtType == 'location':
                childNode = ElementTree.SubElement(node, 'location')
                self.getDao('location').toXML(data, childNode)
            elif data.vtType == 'annotation':
                childNode = ElementTree.SubElement(node, 'annotation')
                self.getDao('annotation').toXML(data, childNode)
            elif data.vtType == 'function':
                childNode = ElementTree.SubElement(node, 'function')
                self.getDao('function').toXML(data, childNode)
            elif data.vtType == 'connection':
                childNode = ElementTree.SubElement(node, 'connection')
                self.getDao('connection').toXML(data, childNode)
            elif data.vtType == 'port':
                childNode = ElementTree.SubElement(node, 'port')
                self.getDao('port').toXML(data, childNode)
            elif data.vtType == 'parameter':
                childNode = ElementTree.SubElement(node, 'parameter')
                self.getDao('parameter').toXML(data, childNode)
            elif data.vtType == 'portSpec':
                childNode = ElementTree.SubElement(node, 'portSpec')
                self.getDao('portSpec').toXML(data, childNode)
            elif data.vtType == 'abstraction':
                childNode = ElementTree.SubElement(node, 'abstraction')
                self.getDao('abstraction').toXML(data, childNode)
            elif data.vtType == 'group':
                childNode = ElementTree.SubElement(node, 'group')
                self.getDao('group').toXML(data, childNode)
            elif data.vtType == 'other':
                childNode = ElementTree.SubElement(node, 'other')
                self.getDao('other').toXML(data, childNode)
            elif data.vtType == 'plugin_data':
                childNode = ElementTree.SubElement(node, 'plugin_data')
                self.getDao('plugin_data').toXML(data, childNode)
        
        return node

class DBOtherXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'other':
            return None
        
        # read attributes
        data = node.get('id', None)
        id = self.convertFromStr(data, 'long')
        data = node.get('key', None)
        key = self.convertFromStr(data, 'str')
        
        value = None
        
        # read children
        for child in node.getchildren():
            if child.tag[0] == "{":
                child_tag = child.tag.split("}")[1]
            else:
                child_tag = child.tag
            if child_tag == 'value':
                _data = self.convertFromStr(child.text,'str')
                value = _data
            elif child.text is None or child.text.strip() == '':
                pass
            else:
                print '*** ERROR *** tag = %s' % child.tag
        
        obj = DBOther(id=id,
                      key=key,
                      value=value)
        obj.is_dirty = False
        return obj
    
    def toXML(self, other, node=None):
        if node is None:
            node = ElementTree.Element('other')
        
        # set attributes
        node.set('id',self.convertToStr(other.db_id, 'long'))
        node.set('key',self.convertToStr(other.db_key, 'str'))
        
        # set elements
        value = other.db_value
        childNode = ElementTree.SubElement(node, 'value')
        childNode.text = self.convertToStr(value, 'str')
        
        return node

class DBLocationXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'location':
            return None
        
        # read attributes
        data = node.get('id', None)
        id = self.convertFromStr(data, 'long')
        data = node.get('x', None)
        x = self.convertFromStr(data, 'float')
        data = node.get('y', None)
        y = self.convertFromStr(data, 'float')
        
        obj = DBLocation(id=id,
                         x=x,
                         y=y)
        obj.is_dirty = False
        return obj
    
    def toXML(self, location, node=None):
        if node is None:
            node = ElementTree.Element('location')
        
        # set attributes
        node.set('id',self.convertToStr(location.db_id, 'long'))
        node.set('x',self.convertToStr(location.db_x, 'float'))
        node.set('y',self.convertToStr(location.db_y, 'float'))
        
        return node

class DBOpmOverlapsXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'overlaps':
            return None
        
        opm_account_ids = []
        
        # read children
        for child in node.getchildren():
            if child.tag[0] == "{":
                child_tag = child.tag.split("}")[1]
            else:
                child_tag = child.tag
            if child_tag == 'account':
                _data = self.getDao('opm_account_id').fromXML(child)
                opm_account_ids.append(_data)
            elif child.text is None or child.text.strip() == '':
                pass
            else:
                print '*** ERROR *** tag = %s' % child.tag
        
        obj = DBOpmOverlaps(opm_account_ids=opm_account_ids)
        obj.is_dirty = False
        return obj
    
    def toXML(self, opm_overlaps, node=None):
        if node is None:
            node = ElementTree.Element('overlaps')
        
        # set elements
        opm_account_ids = opm_overlaps.db_opm_account_ids
        for opm_account_id in opm_account_ids:
            childNode = ElementTree.SubElement(node, 'account')
            self.getDao('opm_account_id').toXML(opm_account_id, childNode)
        
        return node

class DBOpmArtifactsXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'artifacts':
            return None
        
        artifacts = []
        
        # read children
        for child in node.getchildren():
            if child.tag[0] == "{":
                child_tag = child.tag.split("}")[1]
            else:
                child_tag = child.tag
            if child_tag == 'artifact':
                _data = self.getDao('opm_artifact').fromXML(child)
                artifacts.append(_data)
            elif child.text is None or child.text.strip() == '':
                pass
            else:
                print '*** ERROR *** tag = %s' % child.tag
        
        obj = DBOpmArtifacts(artifacts=artifacts)
        obj.is_dirty = False
        return obj
    
    def toXML(self, opm_artifacts, node=None):
        if node is None:
            node = ElementTree.Element('artifacts')
        
        # set elements
        artifacts = opm_artifacts.db_artifacts
        for artifact in artifacts:
            childNode = ElementTree.SubElement(node, 'artifact')
            self.getDao('opm_artifact').toXML(artifact, childNode)
        
        return node

class DBOpmDependenciesXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'causalDependencies':
            return None
        
        dependencys = []
        
        # read children
        for child in node.getchildren():
            if child.tag[0] == "{":
                child_tag = child.tag.split("}")[1]
            else:
                child_tag = child.tag
            if child_tag == 'used':
                _data = self.getDao('opm_used').fromXML(child)
                dependencys.append(_data)
            elif child_tag == 'wasGeneratedBy':
                _data = self.getDao('opm_was_generated_by').fromXML(child)
                dependencys.append(_data)
            elif child_tag == 'wasTriggeredBy':
                _data = self.getDao('opm_was_triggered_by').fromXML(child)
                dependencys.append(_data)
            elif child_tag == 'wasDerivedFrom':
                _data = self.getDao('opm_was_derived_from').fromXML(child)
                dependencys.append(_data)
            elif child_tag == 'wasControlledBy':
                _data = self.getDao('opm_was_controlled_by').fromXML(child)
                dependencys.append(_data)
            elif child.text is None or child.text.strip() == '':
                pass
            else:
                print '*** ERROR *** tag = %s' % child.tag
        
        obj = DBOpmDependencies(dependencys=dependencys)
        obj.is_dirty = False
        return obj
    
    def toXML(self, opm_dependencies, node=None):
        if node is None:
            node = ElementTree.Element('causalDependencies')
        
        # set elements
        dependencys = opm_dependencies.db_dependencys
        for dependency in dependencys:
            if dependency.vtType == 'opm_used':
                childNode = ElementTree.SubElement(node, 'used')
                self.getDao('opm_used').toXML(dependency, childNode)
            elif dependency.vtType == 'opm_was_generated_by':
                childNode = ElementTree.SubElement(node, 'wasGeneratedBy')
                self.getDao('opm_was_generated_by').toXML(dependency, childNode)
            elif dependency.vtType == 'opm_was_triggered_by':
                childNode = ElementTree.SubElement(node, 'wasTriggeredBy')
                self.getDao('opm_was_triggered_by').toXML(dependency, childNode)
            elif dependency.vtType == 'opm_was_derived_from':
                childNode = ElementTree.SubElement(node, 'wasDerivedFrom')
                self.getDao('opm_was_derived_from').toXML(dependency, childNode)
            elif dependency.vtType == 'opm_was_controlled_by':
                childNode = ElementTree.SubElement(node, 'wasControlledBy')
                self.getDao('opm_was_controlled_by').toXML(dependency, childNode)
        
        return node

class DBParameterXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'parameter':
            return None
        
        # read attributes
        data = node.get('id', None)
        id = self.convertFromStr(data, 'long')
        data = node.get('pos', None)
        pos = self.convertFromStr(data, 'long')
        data = node.get('name', None)
        name = self.convertFromStr(data, 'str')
        data = node.get('type', None)
        type = self.convertFromStr(data, 'str')
        data = node.get('val', None)
        val = self.convertFromStr(data, 'str')
        data = node.get('alias', None)
        alias = self.convertFromStr(data, 'str')
        
        obj = DBParameter(id=id,
                          pos=pos,
                          name=name,
                          type=type,
                          val=val,
                          alias=alias)
        obj.is_dirty = False
        return obj
    
    def toXML(self, parameter, node=None):
        if node is None:
            node = ElementTree.Element('parameter')
        
        # set attributes
        node.set('id',self.convertToStr(parameter.db_id, 'long'))
        node.set('pos',self.convertToStr(parameter.db_pos, 'long'))
        node.set('name',self.convertToStr(parameter.db_name, 'str'))
        node.set('type',self.convertToStr(parameter.db_type, 'str'))
        node.set('val',self.convertToStr(parameter.db_val, 'str'))
        node.set('alias',self.convertToStr(parameter.db_alias, 'str'))
        
        return node

class DBProvModelXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'provModel':
            return None
        
        entities = None
        activities = None
        agents = None
        connections = None
        
        # read children
        for child in node.getchildren():
            if child.tag[0] == "{":
                child_tag = child.tag.split("}")[1]
            else:
                child_tag = child.tag
            if child_tag == 'entities':
                _data = self.getDao('prov_entities').fromXML(child)
                entities = _data
            elif child_tag == 'activities':
                _data = self.getDao('prov_activities').fromXML(child)
                activities = _data
            elif child_tag == 'agents':
                _data = self.getDao('prov_agents').fromXML(child)
                agents = _data
            elif child_tag == 'connections':
                _data = self.getDao('vt_connections').fromXML(child)
                connections = _data
            elif child.text is None or child.text.strip() == '':
                pass
            else:
                print '*** ERROR *** tag = %s' % child.tag
        
        obj = DBProvModel(entities=entities,
                          activities=activities,
                          agents=agents,
                          connections=connections)
        obj.is_dirty = False
        return obj
    
    def toXML(self, prov_model, node=None):
        if node is None:
            node = ElementTree.Element('provModel')
        
        # set elements
        entities = prov_model.db_entities
        if entities is not None:
            childNode = ElementTree.SubElement(node, 'entities')
            self.getDao('prov_entities').toXML(entities, childNode)
        activities = prov_model.db_activities
        if activities is not None:
            childNode = ElementTree.SubElement(node, 'activities')
            self.getDao('prov_activities').toXML(activities, childNode)
        agents = prov_model.db_agents
        if agents is not None:
            childNode = ElementTree.SubElement(node, 'agents')
            self.getDao('prov_agents').toXML(agents, childNode)
        connections = prov_model.db_connections
        if connections is not None:
            childNode = ElementTree.SubElement(node, 'connections')
            self.getDao('vt_connections').toXML(connections, childNode)
        
        return node

class DBOpmUsedXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'used':
            return None
        
        effect = None
        role = None
        cause = None
        accounts = []
        opm_times = []
        
        # read children
        for child in node.getchildren():
            if child.tag[0] == "{":
                child_tag = child.tag.split("}")[1]
            else:
                child_tag = child.tag
            if child_tag == 'effect':
                _data = self.getDao('opm_process_id_effect').fromXML(child)
                effect = _data
            elif child_tag == 'role':
                _data = self.getDao('opm_role').fromXML(child)
                role = _data
            elif child_tag == 'cause':
                _data = self.getDao('opm_artifact_id_cause').fromXML(child)
                cause = _data
            elif child_tag == 'account':
                _data = self.getDao('opm_account_id').fromXML(child)
                accounts.append(_data)
            elif child_tag == 'time':
                _data = self.getDao('opm_time').fromXML(child)
                opm_times.append(_data)
            elif child.text is None or child.text.strip() == '':
                pass
            else:
                print '*** ERROR *** tag = %s' % child.tag
        
        obj = DBOpmUsed(effect=effect,
                        role=role,
                        cause=cause,
                        accounts=accounts,
                        opm_times=opm_times)
        obj.is_dirty = False
        return obj
    
    def toXML(self, opm_used, node=None):
        if node is None:
            node = ElementTree.Element('used')
        
        # set elements
        effect = opm_used.db_effect
        if effect is not None:
            childNode = ElementTree.SubElement(node, 'effect')
            self.getDao('opm_process_id_effect').toXML(effect, childNode)
        role = opm_used.db_role
        if role is not None:
            childNode = ElementTree.SubElement(node, 'role')
            self.getDao('opm_role').toXML(role, childNode)
        cause = opm_used.db_cause
        if cause is not None:
            childNode = ElementTree.SubElement(node, 'cause')
            self.getDao('opm_artifact_id_cause').toXML(cause, childNode)
        accounts = opm_used.db_accounts
        for account in accounts:
            childNode = ElementTree.SubElement(node, 'account')
            self.getDao('opm_account_id').toXML(account, childNode)
        opm_times = opm_used.db_opm_times
        for opm_time in opm_times:
            childNode = ElementTree.SubElement(node, 'time')
            self.getDao('opm_time').toXML(opm_time, childNode)
        
        return node

class DBPluginDataXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'plugin_data':
            return None
        
        # read attributes
        data = node.get('id', None)
        id = self.convertFromStr(data, 'long')
        data = node.get('data', None)
        data = self.convertFromStr(data, 'str')
        
        obj = DBPluginData(id=id,
                           data=data)
        obj.is_dirty = False
        return obj
    
    def toXML(self, plugin_data, node=None):
        if node is None:
            node = ElementTree.Element('plugin_data')
        
        # set attributes
        node.set('id',self.convertToStr(plugin_data.db_id, 'long'))
        node.set('data',self.convertToStr(plugin_data.db_data, 'str'))
        
        return node

class DBFunctionXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'function':
            return None
        
        # read attributes
        data = node.get('id', None)
        id = self.convertFromStr(data, 'long')
        data = node.get('pos', None)
        pos = self.convertFromStr(data, 'long')
        data = node.get('name', None)
        name = self.convertFromStr(data, 'str')
        
        parameters = []
        
        # read children
        for child in node.getchildren():
            if child.tag[0] == "{":
                child_tag = child.tag.split("}")[1]
            else:
                child_tag = child.tag
            if child_tag == 'parameter':
                _data = self.getDao('parameter').fromXML(child)
                parameters.append(_data)
            elif child.text is None or child.text.strip() == '':
                pass
            else:
                print '*** ERROR *** tag = %s' % child.tag
        
        obj = DBFunction(id=id,
                         pos=pos,
                         name=name,
                         parameters=parameters)
        obj.is_dirty = False
        return obj
    
    def toXML(self, function, node=None):
        if node is None:
            node = ElementTree.Element('function')
        
        # set attributes
        node.set('id',self.convertToStr(function.db_id, 'long'))
        node.set('pos',self.convertToStr(function.db_pos, 'long'))
        node.set('name',self.convertToStr(function.db_name, 'str'))
        
        # set elements
        parameters = function.db_parameters
        for parameter in parameters:
            childNode = ElementTree.SubElement(node, 'parameter')
            self.getDao('parameter').toXML(parameter, childNode)
        
        return node

class DBActionAnnotationXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'actionAnnotation':
            return None
        
        # read attributes
        data = node.get('id', None)
        id = self.convertFromStr(data, 'long')
        data = node.get('key', None)
        key = self.convertFromStr(data, 'str')
        data = node.get('value', None)
        value = self.convertFromStr(data, 'str')
        data = node.get('actionId', None)
        action_id = self.convertFromStr(data, 'long')
        data = node.get('date', None)
        date = self.convertFromStr(data, 'datetime')
        data = node.get('user', None)
        user = self.convertFromStr(data, 'str')
        
        obj = DBActionAnnotation(id=id,
                                 key=key,
                                 value=value,
                                 action_id=action_id,
                                 date=date,
                                 user=user)
        obj.is_dirty = False
        return obj
    
    def toXML(self, actionAnnotation, node=None):
        if node is None:
            node = ElementTree.Element('actionAnnotation')
        
        # set attributes
        node.set('id',self.convertToStr(actionAnnotation.db_id, 'long'))
        node.set('key',self.convertToStr(actionAnnotation.db_key, 'str'))
        node.set('value',self.convertToStr(actionAnnotation.db_value, 'str'))
        node.set('actionId',self.convertToStr(actionAnnotation.db_action_id, 'long'))
        node.set('date',self.convertToStr(actionAnnotation.db_date, 'datetime'))
        node.set('user',self.convertToStr(actionAnnotation.db_user, 'str'))
        
        return node

class DBVtConnectionsXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'connections':
            return None
        
        vt_connections = []
        
        # read children
        for child in node.getchildren():
            if child.tag[0] == "{":
                child_tag = child.tag.split("}")[1]
            else:
                child_tag = child.tag
            if child_tag == 'vt:connection':
                _data = self.getDao('vt_connection').fromXML(child)
                vt_connections.append(_data)
            elif child.text is None or child.text.strip() == '':
                pass
            else:
                print '*** ERROR *** tag = %s' % child.tag
        
        obj = DBVtConnections(vt_connections=vt_connections)
        obj.is_dirty = False
        return obj
    
    def toXML(self, vt_connections, node=None):
        if node is None:
            node = ElementTree.Element('connections')
        
        # set elements
        vt_connections = vt_connections.db_vt_connections
        for vt_connection in vt_connections:
            childNode = ElementTree.SubElement(node, 'vt:connection')
            self.getDao('vt_connection').toXML(vt_connection, childNode)
        
        return node

class DBAbstractionXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'abstraction':
            return None
        
        # read attributes
        data = node.get('id', None)
        id = self.convertFromStr(data, 'long')
        data = node.get('cache', None)
        cache = self.convertFromStr(data, 'int')
        data = node.get('name', None)
        name = self.convertFromStr(data, 'str')
        data = node.get('namespace', None)
        namespace = self.convertFromStr(data, 'str')
        data = node.get('package', None)
        package = self.convertFromStr(data, 'str')
        data = node.get('version', None)
        version = self.convertFromStr(data, 'str')
        data = node.get('internalVersion', None)
        internal_version = self.convertFromStr(data, 'str')
        
        location = None
        functions = []
        annotations = []
        
        # read children
        for child in node.getchildren():
            if child.tag[0] == "{":
                child_tag = child.tag.split("}")[1]
            else:
                child_tag = child.tag
            if child_tag == 'location':
                _data = self.getDao('location').fromXML(child)
                location = _data
            elif child_tag == 'function':
                _data = self.getDao('function').fromXML(child)
                functions.append(_data)
            elif child_tag == 'annotation':
                _data = self.getDao('annotation').fromXML(child)
                annotations.append(_data)
            elif child.text is None or child.text.strip() == '':
                pass
            else:
                print '*** ERROR *** tag = %s' % child.tag
        
        obj = DBAbstraction(id=id,
                            cache=cache,
                            name=name,
                            namespace=namespace,
                            package=package,
                            version=version,
                            internal_version=internal_version,
                            location=location,
                            functions=functions,
                            annotations=annotations)
        obj.is_dirty = False
        return obj
    
    def toXML(self, abstraction, node=None):
        if node is None:
            node = ElementTree.Element('abstraction')
        
        # set attributes
        node.set('id',self.convertToStr(abstraction.db_id, 'long'))
        node.set('cache',self.convertToStr(abstraction.db_cache, 'int'))
        node.set('name',self.convertToStr(abstraction.db_name, 'str'))
        node.set('namespace',self.convertToStr(abstraction.db_namespace, 'str'))
        node.set('package',self.convertToStr(abstraction.db_package, 'str'))
        node.set('version',self.convertToStr(abstraction.db_version, 'str'))
        node.set('internalVersion',self.convertToStr(abstraction.db_internal_version, 'str'))
        
        # set elements
        location = abstraction.db_location
        if location is not None:
            childNode = ElementTree.SubElement(node, 'location')
            self.getDao('location').toXML(location, childNode)
        functions = abstraction.db_functions
        for function in functions:
            childNode = ElementTree.SubElement(node, 'function')
            self.getDao('function').toXML(function, childNode)
        annotations = abstraction.db_annotations
        for annotation in annotations:
            childNode = ElementTree.SubElement(node, 'annotation')
            self.getDao('annotation').toXML(annotation, childNode)
        
        return node

class DBWorkflowXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'workflow':
            return None
        
        # read attributes
        data = node.get('id', None)
        id = self.convertFromStr(data, 'long')
        data = node.get('name', None)
        name = self.convertFromStr(data, 'str')
        data = node.get('version', None)
        version = self.convertFromStr(data, 'str')
        data = node.get('vistrail_id', None)
        vistrail_id = self.convertFromStr(data, 'long')
        
        connections = []
        annotations = []
        plugin_datas = []
        others = []
        modules = []
        
        # read children
        for child in node.getchildren():
            if child.tag[0] == "{":
                child_tag = child.tag.split("}")[1]
            else:
                child_tag = child.tag
            if child_tag == 'connection':
                _data = self.getDao('connection').fromXML(child)
                connections.append(_data)
            elif child_tag == 'annotation':
                _data = self.getDao('annotation').fromXML(child)
                annotations.append(_data)
            elif child_tag == 'plugin_data':
                _data = self.getDao('plugin_data').fromXML(child)
                plugin_datas.append(_data)
            elif child_tag == 'other':
                _data = self.getDao('other').fromXML(child)
                others.append(_data)
            elif child_tag == 'module':
                _data = self.getDao('module').fromXML(child)
                modules.append(_data)
            elif child_tag == 'abstraction':
                _data = self.getDao('abstraction').fromXML(child)
                modules.append(_data)
            elif child_tag == 'group':
                _data = self.getDao('group').fromXML(child)
                modules.append(_data)
            elif child.text is None or child.text.strip() == '':
                pass
            else:
                print '*** ERROR *** tag = %s' % child.tag
        
        obj = DBWorkflow(modules=modules,
                         id=id,
                         name=name,
                         version=version,
                         connections=connections,
                         annotations=annotations,
                         plugin_datas=plugin_datas,
                         others=others,
                         vistrail_id=vistrail_id)
        obj.is_dirty = False
        return obj
    
    def toXML(self, workflow, node=None):
        if node is None:
            node = ElementTree.Element('workflow')
        
        # set attributes
        node.set('id',self.convertToStr(workflow.db_id, 'long'))
        node.set('name',self.convertToStr(workflow.db_name, 'str'))
        node.set('version',self.convertToStr(workflow.db_version, 'str'))
        node.set('vistrail_id',self.convertToStr(workflow.db_vistrail_id, 'long'))
        
        # set elements
        connections = workflow.db_connections
        for connection in connections:
            childNode = ElementTree.SubElement(node, 'connection')
            self.getDao('connection').toXML(connection, childNode)
        annotations = workflow.db_annotations
        for annotation in annotations:
            childNode = ElementTree.SubElement(node, 'annotation')
            self.getDao('annotation').toXML(annotation, childNode)
        plugin_datas = workflow.db_plugin_datas
        for plugin_data in plugin_datas:
            childNode = ElementTree.SubElement(node, 'plugin_data')
            self.getDao('plugin_data').toXML(plugin_data, childNode)
        others = workflow.db_others
        for other in others:
            childNode = ElementTree.SubElement(node, 'other')
            self.getDao('other').toXML(other, childNode)
        modules = workflow.db_modules
        for module in modules:
            if module.vtType == 'module':
                childNode = ElementTree.SubElement(node, 'module')
                self.getDao('module').toXML(module, childNode)
            elif module.vtType == 'abstraction':
                childNode = ElementTree.SubElement(node, 'abstraction')
                self.getDao('abstraction').toXML(module, childNode)
            elif module.vtType == 'group':
                childNode = ElementTree.SubElement(node, 'group')
                self.getDao('group').toXML(module, childNode)
        
        return node

class DBOpmArtifactIdCauseXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'cause':
            return None
        
        # read attributes
        data = node.get('id', None)
        id = self.convertFromStr(data, 'str')
        
        obj = DBOpmArtifactIdCause(id=id)
        obj.is_dirty = False
        return obj
    
    def toXML(self, opm_artifact_id_cause, node=None):
        if node is None:
            node = ElementTree.Element('cause')
        
        # set attributes
        node.set('id',self.convertToStr(opm_artifact_id_cause.db_id, 'str'))
        
        return node

class DBProvAgentXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'prov:Agent':
            return None
        
        # read attributes
        data = node.get('id', None)
        id = self.convertFromStr(data, 'str')
        data = node.get('vt:id', None)
        vt_id = self.convertFromStr(data, 'str')
        data = node.get('prov:type', None)
        prov_type = self.convertFromStr(data, 'str')
        data = node.get('prov:label', None)
        prov_label = self.convertFromStr(data, 'str')
        data = node.get('vt:machine_os', None)
        vt_machine_os = self.convertFromStr(data, 'str')
        data = node.get('vt:machine_architecture', None)
        vt_machine_architecture = self.convertFromStr(data, 'str')
        data = node.get('vt:machine_processor', None)
        vt_machine_processor = self.convertFromStr(data, 'str')
        data = node.get('vt:machine_ram', None)
        vt_machine_ram = self.convertFromStr(data, 'str')
        
        obj = DBProvAgent(id=id,
                          vt_id=vt_id,
                          prov_type=prov_type,
                          prov_label=prov_label,
                          vt_machine_os=vt_machine_os,
                          vt_machine_architecture=vt_machine_architecture,
                          vt_machine_processor=vt_machine_processor,
                          vt_machine_ram=vt_machine_ram)
        obj.is_dirty = False
        return obj
    
    def toXML(self, prov_agent, node=None):
        if node is None:
            node = ElementTree.Element('prov:Agent')
        
        # set attributes
        node.set('id',self.convertToStr(prov_agent.db_id, 'str'))
        node.set('vt:id',self.convertToStr(prov_agent.db_vt_id, 'str'))
        node.set('prov:type',self.convertToStr(prov_agent.db_prov_type, 'str'))
        node.set('prov:label',self.convertToStr(prov_agent.db_prov_label, 'str'))
        node.set('vt:machine_os',self.convertToStr(prov_agent.db_vt_machine_os, 'str'))
        node.set('vt:machine_architecture',self.convertToStr(prov_agent.db_vt_machine_architecture, 'str'))
        node.set('vt:machine_processor',self.convertToStr(prov_agent.db_vt_machine_processor, 'str'))
        node.set('vt:machine_ram',self.convertToStr(prov_agent.db_vt_machine_ram, 'str'))
        
        return node

class DBProvActivityXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'prov:Activity':
            return None
        
        # read attributes
        data = node.get('id', None)
        id = self.convertFromStr(data, 'str')
        data = node.get('vt:id', None)
        vt_id = self.convertFromStr(data, 'str')
        data = node.get('prov:startedAtTime', None)
        startTime = self.convertFromStr(data, 'str')
        data = node.get('prov:endedAtTime', None)
        endTime = self.convertFromStr(data, 'str')
        data = node.get('vt:type', None)
        vt_type = self.convertFromStr(data, 'str')
        data = node.get('vt:cached', None)
        vt_cached = self.convertFromStr(data, 'str')
        data = node.get('vt:completed', None)
        vt_completed = self.convertFromStr(data, 'str')
        data = node.get('vt:machine_id', None)
        vt_machine_id = self.convertFromStr(data, 'str')
        data = node.get('vt:error', None)
        vt_error = self.convertFromStr(data, 'str')
        data = node.get('dcterms:isPartOf', None)
        isPartOf = self.convertFromStr(data, 'str')
        
        usages = []
        associations = []
        
        # read children
        for child in node.getchildren():
            if child.tag[0] == "{":
                child_tag = child.tag.split("}")[1]
            else:
                child_tag = child.tag
            if child_tag == 'prov:Usage':
                _data = self.getDao('prov_usage').fromXML(child)
                usages.append(_data)
            elif child_tag == 'prov:Association':
                _data = self.getDao('prov_association').fromXML(child)
                associations.append(_data)
            elif child.text is None or child.text.strip() == '':
                pass
            else:
                print '*** ERROR *** tag = %s' % child.tag
        
        obj = DBProvActivity(id=id,
                             vt_id=vt_id,
                             startTime=startTime,
                             endTime=endTime,
                             vt_type=vt_type,
                             vt_cached=vt_cached,
                             vt_completed=vt_completed,
                             vt_machine_id=vt_machine_id,
                             vt_error=vt_error,
                             isPartOf=isPartOf,
                             usages=usages,
                             associations=associations)
        obj.is_dirty = False
        return obj
    
    def toXML(self, prov_activity, node=None):
        if node is None:
            node = ElementTree.Element('prov:Activity')
        
        # set attributes
        node.set('id',self.convertToStr(prov_activity.db_id, 'str'))
        node.set('vt:id',self.convertToStr(prov_activity.db_vt_id, 'str'))
        node.set('prov:startedAtTime',self.convertToStr(prov_activity.db_startTime, 'str'))
        node.set('prov:endedAtTime',self.convertToStr(prov_activity.db_endTime, 'str'))
        node.set('vt:type',self.convertToStr(prov_activity.db_vt_type, 'str'))
        node.set('vt:cached',self.convertToStr(prov_activity.db_vt_cached, 'str'))
        node.set('vt:completed',self.convertToStr(prov_activity.db_vt_completed, 'str'))
        node.set('vt:machine_id',self.convertToStr(prov_activity.db_vt_machine_id, 'str'))
        node.set('vt:error',self.convertToStr(prov_activity.db_vt_error, 'str'))
        node.set('dcterms:isPartOf',self.convertToStr(prov_activity.db_isPartOf, 'str'))
        
        # set elements
        usages = prov_activity.db_usages
        for usage in usages:
            childNode = ElementTree.SubElement(node, 'prov:Usage')
            self.getDao('prov_usage').toXML(usage, childNode)
        associations = prov_activity.db_associations
        for association in associations:
            childNode = ElementTree.SubElement(node, 'prov:Association')
            self.getDao('prov_association').toXML(association, childNode)
        
        return node

class DBProvEntitiesXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'entities':
            return None
        
        prov_entitys = []
        
        # read children
        for child in node.getchildren():
            if child.tag[0] == "{":
                child_tag = child.tag.split("}")[1]
            else:
                child_tag = child.tag
            if child_tag == 'prov:Entity':
                _data = self.getDao('prov_entity').fromXML(child)
                prov_entitys.append(_data)
            elif child.text is None or child.text.strip() == '':
                pass
            else:
                print '*** ERROR *** tag = %s' % child.tag
        
        obj = DBProvEntities(prov_entitys=prov_entitys)
        obj.is_dirty = False
        return obj
    
    def toXML(self, prov_entities, node=None):
        if node is None:
            node = ElementTree.Element('entities')
        
        # set elements
        prov_entitys = prov_entities.db_prov_entitys
        for prov_entity in prov_entitys:
            childNode = ElementTree.SubElement(node, 'prov:Entity')
            self.getDao('prov_entity').toXML(prov_entity, childNode)
        
        return node

class DBProvUsageXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'prov:Usage':
            return None
        
        # read attributes
        data = node.get('id', None)
        id = self.convertFromStr(data, 'str')
        data = node.get('prov:hadRole', None)
        prov_hadRole = self.convertFromStr(data, 'str')
        data = node.get('prov:Entity', None)
        prov_entity = self.convertFromStr(data, 'str')
        
        obj = DBProvUsage(id=id,
                          prov_hadRole=prov_hadRole,
                          prov_entity=prov_entity)
        obj.is_dirty = False
        return obj
    
    def toXML(self, prov_usage, node=None):
        if node is None:
            node = ElementTree.Element('prov:Usage')
        
        # set attributes
        node.set('id',self.convertToStr(prov_usage.db_id, 'str'))
        node.set('prov:hadRole',self.convertToStr(prov_usage.db_prov_hadRole, 'str'))
        node.set('prov:Entity',self.convertToStr(prov_usage.db_prov_entity, 'str'))
        
        return node

class DBOpmArtifactValueXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'value':
            return None
        
        value = None
        
        # read children
        for child in node.getchildren():
            if child.tag[0] == "{":
                child_tag = child.tag.split("}")[1]
            else:
                child_tag = child.tag
            if child_tag == 'portSpec':
                _data = self.getDao('portSpec').fromXML(child)
                value = _data
            elif child_tag == 'function':
                _data = self.getDao('function').fromXML(child)
                value = _data
            elif child.text is None or child.text.strip() == '':
                pass
            else:
                print '*** ERROR *** tag = %s' % child.tag
        
        obj = DBOpmArtifactValue(value=value)
        obj.is_dirty = False
        return obj
    
    def toXML(self, opm_artifact_value, node=None):
        if node is None:
            node = ElementTree.Element('value')
        
        # set elements
        value = opm_artifact_value.db_value
        if value is not None:
            if value.vtType == 'portSpec':
                childNode = ElementTree.SubElement(node, 'portSpec')
                self.getDao('portSpec').toXML(value, childNode)
            elif value.vtType == 'function':
                childNode = ElementTree.SubElement(node, 'function')
                self.getDao('function').toXML(value, childNode)
        
        return node

class DBOpmArtifactIdEffectXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'effect':
            return None
        
        # read attributes
        data = node.get('id', None)
        id = self.convertFromStr(data, 'str')
        
        obj = DBOpmArtifactIdEffect(id=id)
        obj.is_dirty = False
        return obj
    
    def toXML(self, opm_artifact_id_effect, node=None):
        if node is None:
            node = ElementTree.Element('effect')
        
        # set attributes
        node.set('id',self.convertToStr(opm_artifact_id_effect.db_id, 'str'))
        
        return node

class DBOpmGraphXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'opmGraph':
            return None
        
        accounts = None
        processes = None
        artifacts = None
        agents = None
        dependencies = None
        
        # read children
        for child in node.getchildren():
            if child.tag[0] == "{":
                child_tag = child.tag.split("}")[1]
            else:
                child_tag = child.tag
            if child_tag == 'accounts':
                _data = self.getDao('opm_accounts').fromXML(child)
                accounts = _data
            elif child_tag == 'processes':
                _data = self.getDao('opm_processes').fromXML(child)
                processes = _data
            elif child_tag == 'artifacts':
                _data = self.getDao('opm_artifacts').fromXML(child)
                artifacts = _data
            elif child_tag == 'agents':
                _data = self.getDao('opm_agents').fromXML(child)
                agents = _data
            elif child_tag == 'causalDependencies':
                _data = self.getDao('opm_dependencies').fromXML(child)
                dependencies = _data
            elif child.text is None or child.text.strip() == '':
                pass
            else:
                print '*** ERROR *** tag = %s' % child.tag
        
        obj = DBOpmGraph(accounts=accounts,
                         processes=processes,
                         artifacts=artifacts,
                         agents=agents,
                         dependencies=dependencies)
        obj.is_dirty = False
        return obj
    
    def toXML(self, opm_graph, node=None):
        if node is None:
            node = ElementTree.Element('opmGraph')
        
        # set elements
        accounts = opm_graph.db_accounts
        if accounts is not None:
            childNode = ElementTree.SubElement(node, 'accounts')
            self.getDao('opm_accounts').toXML(accounts, childNode)
        processes = opm_graph.db_processes
        if processes is not None:
            childNode = ElementTree.SubElement(node, 'processes')
            self.getDao('opm_processes').toXML(processes, childNode)
        artifacts = opm_graph.db_artifacts
        if artifacts is not None:
            childNode = ElementTree.SubElement(node, 'artifacts')
            self.getDao('opm_artifacts').toXML(artifacts, childNode)
        agents = opm_graph.db_agents
        if agents is not None:
            childNode = ElementTree.SubElement(node, 'agents')
            self.getDao('opm_agents').toXML(agents, childNode)
        dependencies = opm_graph.db_dependencies
        if dependencies is not None:
            childNode = ElementTree.SubElement(node, 'causalDependencies')
            self.getDao('opm_dependencies').toXML(dependencies, childNode)
        
        return node

class DBRegistryXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'registry':
            return None
        
        # read attributes
        data = node.get('id', None)
        id = self.convertFromStr(data, 'long')
        data = node.get('version', None)
        version = self.convertFromStr(data, 'str')
        data = node.get('rootDescriptorId', None)
        root_descriptor_id = self.convertFromStr(data, 'long')
        
        packages = []
        
        # read children
        for child in node.getchildren():
            if child.tag[0] == "{":
                child_tag = child.tag.split("}")[1]
            else:
                child_tag = child.tag
            if child_tag == 'package':
                _data = self.getDao('package').fromXML(child)
                packages.append(_data)
            elif child.text is None or child.text.strip() == '':
                pass
            else:
                print '*** ERROR *** tag = %s' % child.tag
        
        obj = DBRegistry(id=id,
                         version=version,
                         root_descriptor_id=root_descriptor_id,
                         packages=packages)
        obj.is_dirty = False
        return obj
    
    def toXML(self, registry, node=None):
        if node is None:
            node = ElementTree.Element('registry')
        
        # set attributes
        node.set('id',self.convertToStr(registry.db_id, 'long'))
        node.set('version',self.convertToStr(registry.db_version, 'str'))
        node.set('rootDescriptorId',self.convertToStr(registry.db_root_descriptor_id, 'long'))
        
        # set elements
        packages = registry.db_packages
        for package in packages:
            childNode = ElementTree.SubElement(node, 'package')
            self.getDao('package').toXML(package, childNode)
        
        return node

class DBVtConnectionXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'vt:connection':
            return None
        
        # read attributes
        data = node.get('id', None)
        id = self.convertFromStr(data, 'str')
        data = node.get('vt:source', None)
        vt_source = self.convertFromStr(data, 'str')
        data = node.get('vt:dest', None)
        vt_dest = self.convertFromStr(data, 'str')
        data = node.get('vt:source_port', None)
        vt_source_port = self.convertFromStr(data, 'str')
        data = node.get('vt:dest_port', None)
        vt_dest_port = self.convertFromStr(data, 'str')
        data = node.get('vt:source_signature', None)
        vt_source_signature = self.convertFromStr(data, 'str')
        data = node.get('vt:dest_signature', None)
        vt_dest_signature = self.convertFromStr(data, 'str')
        
        obj = DBVtConnection(id=id,
                             vt_source=vt_source,
                             vt_dest=vt_dest,
                             vt_source_port=vt_source_port,
                             vt_dest_port=vt_dest_port,
                             vt_source_signature=vt_source_signature,
                             vt_dest_signature=vt_dest_signature)
        obj.is_dirty = False
        return obj
    
    def toXML(self, vt_connection, node=None):
        if node is None:
            node = ElementTree.Element('vt:connection')
        
        # set attributes
        node.set('id',self.convertToStr(vt_connection.db_id, 'str'))
        node.set('vt:source',self.convertToStr(vt_connection.db_vt_source, 'str'))
        node.set('vt:dest',self.convertToStr(vt_connection.db_vt_dest, 'str'))
        node.set('vt:source_port',self.convertToStr(vt_connection.db_vt_source_port, 'str'))
        node.set('vt:dest_port',self.convertToStr(vt_connection.db_vt_dest_port, 'str'))
        node.set('vt:source_signature',self.convertToStr(vt_connection.db_vt_source_signature, 'str'))
        node.set('vt:dest_signature',self.convertToStr(vt_connection.db_vt_dest_signature, 'str'))
        
        return node

class DBOpmAccountXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'account':
            return None
        
        # read attributes
        data = node.get('id', None)
        id = self.convertFromStr(data, 'str')
        
        value = None
        
        # read children
        for child in node.getchildren():
            if child.tag[0] == "{":
                child_tag = child.tag.split("}")[1]
            else:
                child_tag = child.tag
            if child_tag == 'value':
                _data = self.convertFromStr(child.text,'str')
                value = _data
            elif child.text is None or child.text.strip() == '':
                pass
            else:
                print '*** ERROR *** tag = %s' % child.tag
        
        obj = DBOpmAccount(id=id,
                           value=value)
        obj.is_dirty = False
        return obj
    
    def toXML(self, opm_account, node=None):
        if node is None:
            node = ElementTree.Element('account')
        
        # set attributes
        node.set('id',self.convertToStr(opm_account.db_id, 'str'))
        
        # set elements
        value = opm_account.db_value
        childNode = ElementTree.SubElement(node, 'value')
        childNode.text = self.convertToStr(value, 'str')
        
        return node

class DBProvEntityXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'prov:Entity':
            return None
        
        # read attributes
        data = node.get('id', None)
        id = self.convertFromStr(data, 'str')
        data = node.get('vt:id', None)
        vt_id = self.convertFromStr(data, 'str')
        data = node.get('prov:type', None)
        prov_type = self.convertFromStr(data, 'str')
        data = node.get('prov:label', None)
        prov_label = self.convertFromStr(data, 'str')
        data = node.get('prov:value', None)
        prov_value = self.convertFromStr(data, 'str')
        data = node.get('vt:type', None)
        vt_type = self.convertFromStr(data, 'str')
        data = node.get('vt:desc', None)
        vt_desc = self.convertFromStr(data, 'str')
        data = node.get('vt:package', None)
        vt_package = self.convertFromStr(data, 'str')
        data = node.get('vt:version', None)
        vt_version = self.convertFromStr(data, 'str')
        data = node.get('vt:cache', None)
        vt_cache = self.convertFromStr(data, 'str')
        data = node.get('vt:location_x', None)
        vt_location_x = self.convertFromStr(data, 'str')
        data = node.get('vt:location_y', None)
        vt_location_y = self.convertFromStr(data, 'str')
        data = node.get('dcterms:isPartOf', None)
        isPartOf = self.convertFromStr(data, 'str')
        
        prov_generations = []
        
        # read children
        for child in node.getchildren():
            if child.tag[0] == "{":
                child_tag = child.tag.split("}")[1]
            else:
                child_tag = child.tag
            if child_tag == 'prov:Generation':
                _data = self.getDao('prov_generation').fromXML(child)
                prov_generations.append(_data)
            elif child.text is None or child.text.strip() == '':
                pass
            else:
                print '*** ERROR *** tag = %s' % child.tag
        
        obj = DBProvEntity(id=id,
                           vt_id=vt_id,
                           prov_type=prov_type,
                           prov_label=prov_label,
                           prov_value=prov_value,
                           vt_type=vt_type,
                           vt_desc=vt_desc,
                           vt_package=vt_package,
                           vt_version=vt_version,
                           vt_cache=vt_cache,
                           vt_location_x=vt_location_x,
                           vt_location_y=vt_location_y,
                           isPartOf=isPartOf,
                           prov_generations=prov_generations)
        obj.is_dirty = False
        return obj
    
    def toXML(self, prov_entity, node=None):
        if node is None:
            node = ElementTree.Element('prov:Entity')
        
        # set attributes
        node.set('id',self.convertToStr(prov_entity.db_id, 'str'))
        node.set('vt:id',self.convertToStr(prov_entity.db_vt_id, 'str'))
        node.set('prov:type',self.convertToStr(prov_entity.db_prov_type, 'str'))
        node.set('prov:label',self.convertToStr(prov_entity.db_prov_label, 'str'))
        node.set('prov:value',self.convertToStr(prov_entity.db_prov_value, 'str'))
        node.set('vt:type',self.convertToStr(prov_entity.db_vt_type, 'str'))
        node.set('vt:desc',self.convertToStr(prov_entity.db_vt_desc, 'str'))
        node.set('vt:package',self.convertToStr(prov_entity.db_vt_package, 'str'))
        node.set('vt:version',self.convertToStr(prov_entity.db_vt_version, 'str'))
        node.set('vt:cache',self.convertToStr(prov_entity.db_vt_cache, 'str'))
        node.set('vt:location_x',self.convertToStr(prov_entity.db_vt_location_x, 'str'))
        node.set('vt:location_y',self.convertToStr(prov_entity.db_vt_location_y, 'str'))
        node.set('dcterms:isPartOf',self.convertToStr(prov_entity.db_isPartOf, 'str'))
        
        # set elements
        prov_generations = prov_entity.db_prov_generations
        for prov_generation in prov_generations:
            childNode = ElementTree.SubElement(node, 'prov:Generation')
            self.getDao('prov_generation').toXML(prov_generation, childNode)
        
        return node

class DBAnnotationXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'annotation':
            return None
        
        # read attributes
        data = node.get('id', None)
        id = self.convertFromStr(data, 'long')
        data = node.get('key', None)
        key = self.convertFromStr(data, 'str')
        data = node.get('value', None)
        value = self.convertFromStr(data, 'str')
        
        obj = DBAnnotation(id=id,
                           key=key,
                           value=value)
        obj.is_dirty = False
        return obj
    
    def toXML(self, annotation, node=None):
        if node is None:
            node = ElementTree.Element('annotation')
        
        # set attributes
        node.set('id',self.convertToStr(annotation.db_id, 'long'))
        node.set('key',self.convertToStr(annotation.db_key, 'str'))
        node.set('value',self.convertToStr(annotation.db_value, 'str'))
        
        return node

class DBChangeXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'change':
            return None
        
        # read attributes
        data = node.get('id', None)
        id = self.convertFromStr(data, 'long')
        data = node.get('what', None)
        what = self.convertFromStr(data, 'str')
        data = node.get('oldObjId', None)
        oldObjId = self.convertFromStr(data, 'long')
        data = node.get('newObjId', None)
        newObjId = self.convertFromStr(data, 'long')
        data = node.get('parentObjId', None)
        parentObjId = self.convertFromStr(data, 'long')
        data = node.get('parentObjType', None)
        parentObjType = self.convertFromStr(data, 'str')
        
        data = None
        
        # read children
        for child in node.getchildren():
            if child.tag[0] == "{":
                child_tag = child.tag.split("}")[1]
            else:
                child_tag = child.tag
            if child_tag == 'module':
                _data = self.getDao('module').fromXML(child)
                data = _data
            elif child_tag == 'location':
                _data = self.getDao('location').fromXML(child)
                data = _data
            elif child_tag == 'annotation':
                _data = self.getDao('annotation').fromXML(child)
                data = _data
            elif child_tag == 'function':
                _data = self.getDao('function').fromXML(child)
                data = _data
            elif child_tag == 'connection':
                _data = self.getDao('connection').fromXML(child)
                data = _data
            elif child_tag == 'port':
                _data = self.getDao('port').fromXML(child)
                data = _data
            elif child_tag == 'parameter':
                _data = self.getDao('parameter').fromXML(child)
                data = _data
            elif child_tag == 'portSpec':
                _data = self.getDao('portSpec').fromXML(child)
                data = _data
            elif child_tag == 'abstraction':
                _data = self.getDao('abstraction').fromXML(child)
                data = _data
            elif child_tag == 'group':
                _data = self.getDao('group').fromXML(child)
                data = _data
            elif child_tag == 'other':
                _data = self.getDao('other').fromXML(child)
                data = _data
            elif child_tag == 'plugin_data':
                _data = self.getDao('plugin_data').fromXML(child)
                data = _data
            elif child.text is None or child.text.strip() == '':
                pass
            else:
                print '*** ERROR *** tag = %s' % child.tag
        
        obj = DBChange(data=data,
                       id=id,
                       what=what,
                       oldObjId=oldObjId,
                       newObjId=newObjId,
                       parentObjId=parentObjId,
                       parentObjType=parentObjType)
        obj.is_dirty = False
        return obj
    
    def toXML(self, change, node=None):
        if node is None:
            node = ElementTree.Element('change')
        
        # set attributes
        node.set('id',self.convertToStr(change.db_id, 'long'))
        node.set('what',self.convertToStr(change.db_what, 'str'))
        node.set('oldObjId',self.convertToStr(change.db_oldObjId, 'long'))
        node.set('newObjId',self.convertToStr(change.db_newObjId, 'long'))
        node.set('parentObjId',self.convertToStr(change.db_parentObjId, 'long'))
        node.set('parentObjType',self.convertToStr(change.db_parentObjType, 'str'))
        
        # set elements
        data = change.db_data
        if data is not None:
            if data.vtType == 'module':
                childNode = ElementTree.SubElement(node, 'module')
                self.getDao('module').toXML(data, childNode)
            elif data.vtType == 'location':
                childNode = ElementTree.SubElement(node, 'location')
                self.getDao('location').toXML(data, childNode)
            elif data.vtType == 'annotation':
                childNode = ElementTree.SubElement(node, 'annotation')
                self.getDao('annotation').toXML(data, childNode)
            elif data.vtType == 'function':
                childNode = ElementTree.SubElement(node, 'function')
                self.getDao('function').toXML(data, childNode)
            elif data.vtType == 'connection':
                childNode = ElementTree.SubElement(node, 'connection')
                self.getDao('connection').toXML(data, childNode)
            elif data.vtType == 'port':
                childNode = ElementTree.SubElement(node, 'port')
                self.getDao('port').toXML(data, childNode)
            elif data.vtType == 'parameter':
                childNode = ElementTree.SubElement(node, 'parameter')
                self.getDao('parameter').toXML(data, childNode)
            elif data.vtType == 'portSpec':
                childNode = ElementTree.SubElement(node, 'portSpec')
                self.getDao('portSpec').toXML(data, childNode)
            elif data.vtType == 'abstraction':
                childNode = ElementTree.SubElement(node, 'abstraction')
                self.getDao('abstraction').toXML(data, childNode)
            elif data.vtType == 'group':
                childNode = ElementTree.SubElement(node, 'group')
                self.getDao('group').toXML(data, childNode)
            elif data.vtType == 'other':
                childNode = ElementTree.SubElement(node, 'other')
                self.getDao('other').toXML(data, childNode)
            elif data.vtType == 'plugin_data':
                childNode = ElementTree.SubElement(node, 'plugin_data')
                self.getDao('plugin_data').toXML(data, childNode)
        
        return node

class DBOpmWasDerivedFromXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'wasDerivedFrom':
            return None
        
        effect = None
        role = None
        cause = None
        accounts = []
        opm_times = []
        
        # read children
        for child in node.getchildren():
            if child.tag[0] == "{":
                child_tag = child.tag.split("}")[1]
            else:
                child_tag = child.tag
            if child_tag == 'effect':
                _data = self.getDao('opm_artifact_id_effect').fromXML(child)
                effect = _data
            elif child_tag == 'role':
                _data = self.getDao('opm_role').fromXML(child)
                role = _data
            elif child_tag == 'cause':
                _data = self.getDao('opm_artifact_id_cause').fromXML(child)
                cause = _data
            elif child_tag == 'account':
                _data = self.getDao('opm_account_id').fromXML(child)
                accounts.append(_data)
            elif child_tag == 'time':
                _data = self.getDao('opm_time').fromXML(child)
                opm_times.append(_data)
            elif child.text is None or child.text.strip() == '':
                pass
            else:
                print '*** ERROR *** tag = %s' % child.tag
        
        obj = DBOpmWasDerivedFrom(effect=effect,
                                  role=role,
                                  cause=cause,
                                  accounts=accounts,
                                  opm_times=opm_times)
        obj.is_dirty = False
        return obj
    
    def toXML(self, opm_was_derived_from, node=None):
        if node is None:
            node = ElementTree.Element('wasDerivedFrom')
        
        # set elements
        effect = opm_was_derived_from.db_effect
        if effect is not None:
            childNode = ElementTree.SubElement(node, 'effect')
            self.getDao('opm_artifact_id_effect').toXML(effect, childNode)
        role = opm_was_derived_from.db_role
        if role is not None:
            childNode = ElementTree.SubElement(node, 'role')
            self.getDao('opm_role').toXML(role, childNode)
        cause = opm_was_derived_from.db_cause
        if cause is not None:
            childNode = ElementTree.SubElement(node, 'cause')
            self.getDao('opm_artifact_id_cause').toXML(cause, childNode)
        accounts = opm_was_derived_from.db_accounts
        for account in accounts:
            childNode = ElementTree.SubElement(node, 'account')
            self.getDao('opm_account_id').toXML(account, childNode)
        opm_times = opm_was_derived_from.db_opm_times
        for opm_time in opm_times:
            childNode = ElementTree.SubElement(node, 'time')
            self.getDao('opm_time').toXML(opm_time, childNode)
        
        return node

class DBOpmWasControlledByXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'wasControlledBy':
            return None
        
        effect = None
        role = None
        cause = None
        accounts = []
        starts = []
        ends = []
        
        # read children
        for child in node.getchildren():
            if child.tag[0] == "{":
                child_tag = child.tag.split("}")[1]
            else:
                child_tag = child.tag
            if child_tag == 'effect':
                _data = self.getDao('opm_process_id_effect').fromXML(child)
                effect = _data
            elif child_tag == 'role':
                _data = self.getDao('opm_role').fromXML(child)
                role = _data
            elif child_tag == 'agent':
                _data = self.getDao('opm_agent_id').fromXML(child)
                cause = _data
            elif child_tag == 'account':
                _data = self.getDao('opm_account_id').fromXML(child)
                accounts.append(_data)
            elif child_tag == 'time':
                _data = self.getDao('opm_time').fromXML(child)
                starts.append(_data)
            elif child_tag == 'time':
                _data = self.getDao('opm_time').fromXML(child)
                ends.append(_data)
            elif child.text is None or child.text.strip() == '':
                pass
            else:
                print '*** ERROR *** tag = %s' % child.tag
        
        obj = DBOpmWasControlledBy(effect=effect,
                                   role=role,
                                   cause=cause,
                                   accounts=accounts,
                                   starts=starts,
                                   ends=ends)
        obj.is_dirty = False
        return obj
    
    def toXML(self, opm_was_controlled_by, node=None):
        if node is None:
            node = ElementTree.Element('wasControlledBy')
        
        # set elements
        effect = opm_was_controlled_by.db_effect
        if effect is not None:
            childNode = ElementTree.SubElement(node, 'effect')
            self.getDao('opm_process_id_effect').toXML(effect, childNode)
        role = opm_was_controlled_by.db_role
        if role is not None:
            childNode = ElementTree.SubElement(node, 'role')
            self.getDao('opm_role').toXML(role, childNode)
        cause = opm_was_controlled_by.db_cause
        if cause is not None:
            childNode = ElementTree.SubElement(node, 'agent')
            self.getDao('opm_agent_id').toXML(cause, childNode)
        accounts = opm_was_controlled_by.db_accounts
        for account in accounts:
            childNode = ElementTree.SubElement(node, 'account')
            self.getDao('opm_account_id').toXML(account, childNode)
        starts = opm_was_controlled_by.db_starts
        for start in starts:
            childNode = ElementTree.SubElement(node, 'time')
            self.getDao('opm_time').toXML(start, childNode)
        ends = opm_was_controlled_by.db_ends
        for end in ends:
            childNode = ElementTree.SubElement(node, 'time')
            self.getDao('opm_time').toXML(end, childNode)
        
        return node

class DBOpmAgentIdXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'agent':
            return None
        
        # read attributes
        data = node.get('id', None)
        id = self.convertFromStr(data, 'str')
        
        obj = DBOpmAgentId(id=id)
        obj.is_dirty = False
        return obj
    
    def toXML(self, opm_agent_id, node=None):
        if node is None:
            node = ElementTree.Element('agent')
        
        # set attributes
        node.set('id',self.convertToStr(opm_agent_id.db_id, 'str'))
        
        return node

class DBGroupExecXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'groupExec':
            return None
        
        # read attributes
        data = node.get('id', None)
        id = self.convertFromStr(data, 'long')
        data = node.get('tsStart', None)
        ts_start = self.convertFromStr(data, 'datetime')
        data = node.get('tsEnd', None)
        ts_end = self.convertFromStr(data, 'datetime')
        data = node.get('cached', None)
        cached = self.convertFromStr(data, 'int')
        data = node.get('moduleId', None)
        module_id = self.convertFromStr(data, 'long')
        data = node.get('groupName', None)
        group_name = self.convertFromStr(data, 'str')
        data = node.get('groupType', None)
        group_type = self.convertFromStr(data, 'str')
        data = node.get('completed', None)
        completed = self.convertFromStr(data, 'int')
        data = node.get('error', None)
        error = self.convertFromStr(data, 'str')
        data = node.get('machine_id', None)
        machine_id = self.convertFromStr(data, 'long')
        
        annotations = []
        item_execs = []
        
        # read children
        for child in node.getchildren():
            if child.tag[0] == "{":
                child_tag = child.tag.split("}")[1]
            else:
                child_tag = child.tag
            if child_tag == 'annotation':
                _data = self.getDao('annotation').fromXML(child)
                annotations.append(_data)
            elif child_tag == 'moduleExec':
                _data = self.getDao('module_exec').fromXML(child)
                item_execs.append(_data)
            elif child_tag == 'groupExec':
                _data = self.getDao('group_exec').fromXML(child)
                item_execs.append(_data)
            elif child_tag == 'loopExec':
                _data = self.getDao('loop_exec').fromXML(child)
                item_execs.append(_data)
            elif child.text is None or child.text.strip() == '':
                pass
            else:
                print '*** ERROR *** tag = %s' % child.tag
        
        obj = DBGroupExec(item_execs=item_execs,
                          id=id,
                          ts_start=ts_start,
                          ts_end=ts_end,
                          cached=cached,
                          module_id=module_id,
                          group_name=group_name,
                          group_type=group_type,
                          completed=completed,
                          error=error,
                          machine_id=machine_id,
                          annotations=annotations)
        obj.is_dirty = False
        return obj
    
    def toXML(self, group_exec, node=None):
        if node is None:
            node = ElementTree.Element('groupExec')
        
        # set attributes
        node.set('id',self.convertToStr(group_exec.db_id, 'long'))
        node.set('tsStart',self.convertToStr(group_exec.db_ts_start, 'datetime'))
        node.set('tsEnd',self.convertToStr(group_exec.db_ts_end, 'datetime'))
        node.set('cached',self.convertToStr(group_exec.db_cached, 'int'))
        node.set('moduleId',self.convertToStr(group_exec.db_module_id, 'long'))
        node.set('groupName',self.convertToStr(group_exec.db_group_name, 'str'))
        node.set('groupType',self.convertToStr(group_exec.db_group_type, 'str'))
        node.set('completed',self.convertToStr(group_exec.db_completed, 'int'))
        node.set('error',self.convertToStr(group_exec.db_error, 'str'))
        node.set('machine_id',self.convertToStr(group_exec.db_machine_id, 'long'))
        
        # set elements
        annotations = group_exec.db_annotations
        for annotation in annotations:
            childNode = ElementTree.SubElement(node, 'annotation')
            self.getDao('annotation').toXML(annotation, childNode)
        item_execs = group_exec.db_item_execs
        for item_exec in item_execs:
            if item_exec.vtType == 'module_exec':
                childNode = ElementTree.SubElement(node, 'moduleExec')
                self.getDao('module_exec').toXML(item_exec, childNode)
            elif item_exec.vtType == 'group_exec':
                childNode = ElementTree.SubElement(node, 'groupExec')
                self.getDao('group_exec').toXML(item_exec, childNode)
            elif item_exec.vtType == 'loop_exec':
                childNode = ElementTree.SubElement(node, 'loopExec')
                self.getDao('loop_exec').toXML(item_exec, childNode)
        
        return node

class DBOpmTimeXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'time':
            return None
        
        # read attributes
        data = node.get('noLaterThan', None)
        no_later_than = self.convertFromStr(data, 'datetime')
        data = node.get('noEarlierThan', None)
        no_earlier_than = self.convertFromStr(data, 'datetime')
        data = node.get('clockId', None)
        clock_id = self.convertFromStr(data, 'str')
        
        obj = DBOpmTime(no_later_than=no_later_than,
                        no_earlier_than=no_earlier_than,
                        clock_id=clock_id)
        obj.is_dirty = False
        return obj
    
    def toXML(self, opm_time, node=None):
        if node is None:
            node = ElementTree.Element('time')
        
        # set attributes
        node.set('noLaterThan',self.convertToStr(opm_time.db_no_later_than, 'datetime'))
        node.set('noEarlierThan',self.convertToStr(opm_time.db_no_earlier_than, 'datetime'))
        node.set('clockId',self.convertToStr(opm_time.db_clock_id, 'str'))
        
        return node

class DBPackageXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'package':
            return None
        
        # read attributes
        data = node.get('id', None)
        id = self.convertFromStr(data, 'long')
        data = node.get('name', None)
        name = self.convertFromStr(data, 'str')
        data = node.get('identifier', None)
        identifier = self.convertFromStr(data, 'str')
        data = node.get('codepath', None)
        codepath = self.convertFromStr(data, 'str')
        data = node.get('loadConfiguration', None)
        load_configuration = self.convertFromStr(data, 'int')
        data = node.get('version', None)
        version = self.convertFromStr(data, 'str')
        data = node.get('description', None)
        description = self.convertFromStr(data, 'str')
        
        module_descriptors = []
        
        # read children
        for child in node.getchildren():
            if child.tag[0] == "{":
                child_tag = child.tag.split("}")[1]
            else:
                child_tag = child.tag
            if child_tag == 'moduleDescriptor':
                _data = self.getDao('module_descriptor').fromXML(child)
                module_descriptors.append(_data)
            elif child.text is None or child.text.strip() == '':
                pass
            else:
                print '*** ERROR *** tag = %s' % child.tag
        
        obj = DBPackage(id=id,
                        name=name,
                        identifier=identifier,
                        codepath=codepath,
                        load_configuration=load_configuration,
                        version=version,
                        description=description,
                        module_descriptors=module_descriptors)
        obj.is_dirty = False
        return obj
    
    def toXML(self, package, node=None):
        if node is None:
            node = ElementTree.Element('package')
        
        # set attributes
        node.set('id',self.convertToStr(package.db_id, 'long'))
        node.set('name',self.convertToStr(package.db_name, 'str'))
        node.set('identifier',self.convertToStr(package.db_identifier, 'str'))
        node.set('codepath',self.convertToStr(package.db_codepath, 'str'))
        node.set('loadConfiguration',self.convertToStr(package.db_load_configuration, 'int'))
        node.set('version',self.convertToStr(package.db_version, 'str'))
        node.set('description',self.convertToStr(package.db_description, 'str'))
        
        # set elements
        module_descriptors = package.db_module_descriptors
        for module_descriptor in module_descriptors:
            childNode = ElementTree.SubElement(node, 'moduleDescriptor')
            self.getDao('module_descriptor').toXML(module_descriptor, childNode)
        
        return node

class DBWorkflowExecXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'workflowExec':
            return None
        
        # read attributes
        data = node.get('id', None)
        id = self.convertFromStr(data, 'long')
        data = node.get('user', None)
        user = self.convertFromStr(data, 'str')
        data = node.get('ip', None)
        ip = self.convertFromStr(data, 'str')
        data = node.get('session', None)
        session = self.convertFromStr(data, 'long')
        data = node.get('vtVersion', None)
        vt_version = self.convertFromStr(data, 'str')
        data = node.get('tsStart', None)
        ts_start = self.convertFromStr(data, 'datetime')
        data = node.get('tsEnd', None)
        ts_end = self.convertFromStr(data, 'datetime')
        data = node.get('parentId', None)
        parent_id = self.convertFromStr(data, 'long')
        data = node.get('parentType', None)
        parent_type = self.convertFromStr(data, 'str')
        data = node.get('parentVersion', None)
        parent_version = self.convertFromStr(data, 'long')
        data = node.get('completed', None)
        completed = self.convertFromStr(data, 'int')
        data = node.get('name', None)
        name = self.convertFromStr(data, 'str')
        
        annotations = []
        item_execs = []
        
        # read children
        for child in node.getchildren():
            if child.tag[0] == "{":
                child_tag = child.tag.split("}")[1]
            else:
                child_tag = child.tag
            if child_tag == 'annotation':
                _data = self.getDao('annotation').fromXML(child)
                annotations.append(_data)
            elif child_tag == 'moduleExec':
                _data = self.getDao('module_exec').fromXML(child)
                item_execs.append(_data)
            elif child_tag == 'groupExec':
                _data = self.getDao('group_exec').fromXML(child)
                item_execs.append(_data)
            elif child_tag == 'loopExec':
                _data = self.getDao('loop_exec').fromXML(child)
                item_execs.append(_data)
            elif child.text is None or child.text.strip() == '':
                pass
            else:
                print '*** ERROR *** tag = %s' % child.tag
        
        obj = DBWorkflowExec(item_execs=item_execs,
                             id=id,
                             user=user,
                             ip=ip,
                             session=session,
                             vt_version=vt_version,
                             ts_start=ts_start,
                             ts_end=ts_end,
                             parent_id=parent_id,
                             parent_type=parent_type,
                             parent_version=parent_version,
                             completed=completed,
                             name=name,
                             annotations=annotations)
        obj.is_dirty = False
        return obj
    
    def toXML(self, workflow_exec, node=None):
        if node is None:
            node = ElementTree.Element('workflowExec')
        
        # set attributes
        node.set('id',self.convertToStr(workflow_exec.db_id, 'long'))
        node.set('user',self.convertToStr(workflow_exec.db_user, 'str'))
        node.set('ip',self.convertToStr(workflow_exec.db_ip, 'str'))
        node.set('session',self.convertToStr(workflow_exec.db_session, 'long'))
        node.set('vtVersion',self.convertToStr(workflow_exec.db_vt_version, 'str'))
        node.set('tsStart',self.convertToStr(workflow_exec.db_ts_start, 'datetime'))
        node.set('tsEnd',self.convertToStr(workflow_exec.db_ts_end, 'datetime'))
        node.set('parentId',self.convertToStr(workflow_exec.db_parent_id, 'long'))
        node.set('parentType',self.convertToStr(workflow_exec.db_parent_type, 'str'))
        node.set('parentVersion',self.convertToStr(workflow_exec.db_parent_version, 'long'))
        node.set('completed',self.convertToStr(workflow_exec.db_completed, 'int'))
        node.set('name',self.convertToStr(workflow_exec.db_name, 'str'))
        
        # set elements
        annotations = workflow_exec.db_annotations
        for annotation in annotations:
            childNode = ElementTree.SubElement(node, 'annotation')
            self.getDao('annotation').toXML(annotation, childNode)
        item_execs = workflow_exec.db_item_execs
        for item_exec in item_execs:
            if item_exec.vtType == 'module_exec':
                childNode = ElementTree.SubElement(node, 'moduleExec')
                self.getDao('module_exec').toXML(item_exec, childNode)
            elif item_exec.vtType == 'group_exec':
                childNode = ElementTree.SubElement(node, 'groupExec')
                self.getDao('group_exec').toXML(item_exec, childNode)
            elif item_exec.vtType == 'loop_exec':
                childNode = ElementTree.SubElement(node, 'loopExec')
                self.getDao('loop_exec').toXML(item_exec, childNode)
        
        return node

class DBParameterExplorationXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'parameter_exploration':
            return None
        
        # read attributes
        data = node.get('id', None)
        id = self.convertFromStr(data, 'long')
        data = node.get('actionId', None)
        action_id = self.convertFromStr(data, 'long')
        data = node.get('name', None)
        name = self.convertFromStr(data, 'str')
        data = node.get('user', None)
        user = self.convertFromStr(data, 'str')
        data = node.get('dims', None)
        dims = self.convertFromStr(data, 'str')
        data = node.get('layout', None)
        layout = self.convertFromStr(data, 'str')
        
        functions = []
        
        # read children
        for child in node.getchildren():
            if child.tag[0] == "{":
                child_tag = child.tag.split("}")[1]
            else:
                child_tag = child.tag
            if child_tag == 'function':
                _data = self.getDao('function').fromXML(child)
                functions.append(_data)
            elif child.text is None or child.text.strip() == '':
                pass
            else:
                print '*** ERROR *** tag = %s' % child.tag
        
        obj = DBParameterExploration(id=id,
                                     action_id=action_id,
                                     name=name,
                                     user=user,
                                     dims=dims,
                                     layout=layout,
                                     functions=functions)
        obj.is_dirty = False
        return obj
    
    def toXML(self, parameter_exploration, node=None):
        if node is None:
            node = ElementTree.Element('parameter_exploration')
        
        # set attributes
        node.set('id',self.convertToStr(parameter_exploration.db_id, 'long'))
        node.set('actionId',self.convertToStr(parameter_exploration.db_action_id, 'long'))
        node.set('name',self.convertToStr(parameter_exploration.db_name, 'str'))
        node.set('user',self.convertToStr(parameter_exploration.db_user, 'str'))
        node.set('dims',self.convertToStr(parameter_exploration.db_dims, 'str'))
        node.set('layout',self.convertToStr(parameter_exploration.db_layout, 'str'))
        
        # set elements
        functions = parameter_exploration.db_functions
        for function in functions:
            childNode = ElementTree.SubElement(node, 'function')
            self.getDao('function').toXML(function, childNode)
        
        return node

class DBLoopExecXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'loopExec':
            return None
        
        # read attributes
        data = node.get('id', None)
        id = self.convertFromStr(data, 'long')
        data = node.get('tsStart', None)
        ts_start = self.convertFromStr(data, 'datetime')
        data = node.get('tsEnd', None)
        ts_end = self.convertFromStr(data, 'datetime')
        data = node.get('iteration', None)
        iteration = self.convertFromStr(data, 'int')
        data = node.get('completed', None)
        completed = self.convertFromStr(data, 'int')
        data = node.get('error', None)
        error = self.convertFromStr(data, 'str')
        
        item_execs = []
        
        # read children
        for child in node.getchildren():
            if child.tag[0] == "{":
                child_tag = child.tag.split("}")[1]
            else:
                child_tag = child.tag
            if child_tag == 'moduleExec':
                _data = self.getDao('module_exec').fromXML(child)
                item_execs.append(_data)
            elif child_tag == 'groupExec':
                _data = self.getDao('group_exec').fromXML(child)
                item_execs.append(_data)
            elif child_tag == 'loopExec':
                _data = self.getDao('loop_exec').fromXML(child)
                item_execs.append(_data)
            elif child.text is None or child.text.strip() == '':
                pass
            else:
                print '*** ERROR *** tag = %s' % child.tag
        
        obj = DBLoopExec(item_execs=item_execs,
                         id=id,
                         ts_start=ts_start,
                         ts_end=ts_end,
                         iteration=iteration,
                         completed=completed,
                         error=error)
        obj.is_dirty = False
        return obj
    
    def toXML(self, loop_exec, node=None):
        if node is None:
            node = ElementTree.Element('loopExec')
        
        # set attributes
        node.set('id',self.convertToStr(loop_exec.db_id, 'long'))
        node.set('tsStart',self.convertToStr(loop_exec.db_ts_start, 'datetime'))
        node.set('tsEnd',self.convertToStr(loop_exec.db_ts_end, 'datetime'))
        node.set('iteration',self.convertToStr(loop_exec.db_iteration, 'int'))
        node.set('completed',self.convertToStr(loop_exec.db_completed, 'int'))
        node.set('error',self.convertToStr(loop_exec.db_error, 'str'))
        
        # set elements
        item_execs = loop_exec.db_item_execs
        for item_exec in item_execs:
            if item_exec.vtType == 'module_exec':
                childNode = ElementTree.SubElement(node, 'moduleExec')
                self.getDao('module_exec').toXML(item_exec, childNode)
            elif item_exec.vtType == 'group_exec':
                childNode = ElementTree.SubElement(node, 'groupExec')
                self.getDao('group_exec').toXML(item_exec, childNode)
            elif item_exec.vtType == 'loop_exec':
                childNode = ElementTree.SubElement(node, 'loopExec')
                self.getDao('loop_exec').toXML(item_exec, childNode)
        
        return node

class DBProvAgentsXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'agents':
            return None
        
        prov_agents = []
        
        # read children
        for child in node.getchildren():
            if child.tag[0] == "{":
                child_tag = child.tag.split("}")[1]
            else:
                child_tag = child.tag
            if child_tag == 'prov:Agent':
                _data = self.getDao('prov_agent').fromXML(child)
                prov_agents.append(_data)
            elif child.text is None or child.text.strip() == '':
                pass
            else:
                print '*** ERROR *** tag = %s' % child.tag
        
        obj = DBProvAgents(prov_agents=prov_agents)
        obj.is_dirty = False
        return obj
    
    def toXML(self, prov_agents, node=None):
        if node is None:
            node = ElementTree.Element('agents')
        
        # set elements
        prov_agents = prov_agents.db_prov_agents
        for prov_agent in prov_agents:
            childNode = ElementTree.SubElement(node, 'prov:Agent')
            self.getDao('prov_agent').toXML(prov_agent, childNode)
        
        return node

class DBConnectionXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'connection':
            return None
        
        # read attributes
        data = node.get('id', None)
        id = self.convertFromStr(data, 'long')
        
        ports = []
        
        # read children
        for child in node.getchildren():
            if child.tag[0] == "{":
                child_tag = child.tag.split("}")[1]
            else:
                child_tag = child.tag
            if child_tag == 'port':
                _data = self.getDao('port').fromXML(child)
                ports.append(_data)
            elif child.text is None or child.text.strip() == '':
                pass
            else:
                print '*** ERROR *** tag = %s' % child.tag
        
        obj = DBConnection(id=id,
                           ports=ports)
        obj.is_dirty = False
        return obj
    
    def toXML(self, connection, node=None):
        if node is None:
            node = ElementTree.Element('connection')
        
        # set attributes
        node.set('id',self.convertToStr(connection.db_id, 'long'))
        
        # set elements
        ports = connection.db_ports
        for port in ports:
            childNode = ElementTree.SubElement(node, 'port')
            self.getDao('port').toXML(port, childNode)
        
        return node

class DBOpmProcessXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'process':
            return None
        
        # read attributes
        data = node.get('id', None)
        id = self.convertFromStr(data, 'str')
        
        value = None
        accounts = []
        
        # read children
        for child in node.getchildren():
            if child.tag[0] == "{":
                child_tag = child.tag.split("}")[1]
            else:
                child_tag = child.tag
            if child_tag == 'value':
                _data = self.getDao('opm_process_value').fromXML(child)
                value = _data
            elif child_tag == 'account':
                _data = self.getDao('opm_account_id').fromXML(child)
                accounts.append(_data)
            elif child.text is None or child.text.strip() == '':
                pass
            else:
                print '*** ERROR *** tag = %s' % child.tag
        
        obj = DBOpmProcess(id=id,
                           value=value,
                           accounts=accounts)
        obj.is_dirty = False
        return obj
    
    def toXML(self, opm_process, node=None):
        if node is None:
            node = ElementTree.Element('process')
        
        # set attributes
        node.set('id',self.convertToStr(opm_process.db_id, 'str'))
        
        # set elements
        value = opm_process.db_value
        if value is not None:
            childNode = ElementTree.SubElement(node, 'value')
            self.getDao('opm_process_value').toXML(value, childNode)
        accounts = opm_process.db_accounts
        for account in accounts:
            childNode = ElementTree.SubElement(node, 'account')
            self.getDao('opm_account_id').toXML(account, childNode)
        
        return node

class DBOpmWasTriggeredByXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'wasTriggeredBy':
            return None
        
        effect = None
        role = None
        cause = None
        accounts = []
        opm_times = []
        
        # read children
        for child in node.getchildren():
            if child.tag[0] == "{":
                child_tag = child.tag.split("}")[1]
            else:
                child_tag = child.tag
            if child_tag == 'effect':
                _data = self.getDao('opm_process_id_effect').fromXML(child)
                effect = _data
            elif child_tag == 'role':
                _data = self.getDao('opm_role').fromXML(child)
                role = _data
            elif child_tag == 'cause':
                _data = self.getDao('opm_process_id_cause').fromXML(child)
                cause = _data
            elif child_tag == 'account':
                _data = self.getDao('opm_account_id').fromXML(child)
                accounts.append(_data)
            elif child_tag == 'time':
                _data = self.getDao('opm_time').fromXML(child)
                opm_times.append(_data)
            elif child.text is None or child.text.strip() == '':
                pass
            else:
                print '*** ERROR *** tag = %s' % child.tag
        
        obj = DBOpmWasTriggeredBy(effect=effect,
                                  role=role,
                                  cause=cause,
                                  accounts=accounts,
                                  opm_times=opm_times)
        obj.is_dirty = False
        return obj
    
    def toXML(self, opm_was_triggered_by, node=None):
        if node is None:
            node = ElementTree.Element('wasTriggeredBy')
        
        # set elements
        effect = opm_was_triggered_by.db_effect
        if effect is not None:
            childNode = ElementTree.SubElement(node, 'effect')
            self.getDao('opm_process_id_effect').toXML(effect, childNode)
        role = opm_was_triggered_by.db_role
        if role is not None:
            childNode = ElementTree.SubElement(node, 'role')
            self.getDao('opm_role').toXML(role, childNode)
        cause = opm_was_triggered_by.db_cause
        if cause is not None:
            childNode = ElementTree.SubElement(node, 'cause')
            self.getDao('opm_process_id_cause').toXML(cause, childNode)
        accounts = opm_was_triggered_by.db_accounts
        for account in accounts:
            childNode = ElementTree.SubElement(node, 'account')
            self.getDao('opm_account_id').toXML(account, childNode)
        opm_times = opm_was_triggered_by.db_opm_times
        for opm_time in opm_times:
            childNode = ElementTree.SubElement(node, 'time')
            self.getDao('opm_time').toXML(opm_time, childNode)
        
        return node

class DBOpmProcessValueXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'value':
            return None
        
        value = None
        
        # read children
        for child in node.getchildren():
            if child.tag[0] == "{":
                child_tag = child.tag.split("}")[1]
            else:
                child_tag = child.tag
            if child_tag == 'moduleExec':
                _data = self.getDao('module_exec').fromXML(child)
                value = _data
            elif child_tag == 'groupExec':
                _data = self.getDao('group_exec').fromXML(child)
                value = _data
            elif child_tag == 'loopExec':
                _data = self.getDao('loop_exec').fromXML(child)
                value = _data
            elif child.text is None or child.text.strip() == '':
                pass
            else:
                print '*** ERROR *** tag = %s' % child.tag
        
        obj = DBOpmProcessValue(value=value)
        obj.is_dirty = False
        return obj
    
    def toXML(self, opm_process_value, node=None):
        if node is None:
            node = ElementTree.Element('value')
        
        # set elements
        value = opm_process_value.db_value
        if value is not None:
            if value.vtType == 'module_exec':
                childNode = ElementTree.SubElement(node, 'moduleExec')
                self.getDao('module_exec').toXML(value, childNode)
            elif value.vtType == 'group_exec':
                childNode = ElementTree.SubElement(node, 'groupExec')
                self.getDao('group_exec').toXML(value, childNode)
            elif value.vtType == 'loop_exec':
                childNode = ElementTree.SubElement(node, 'loopExec')
                self.getDao('loop_exec').toXML(value, childNode)
        
        return node

class DBActionXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'action':
            return None
        
        # read attributes
        data = node.get('id', None)
        id = self.convertFromStr(data, 'long')
        data = node.get('prevId', None)
        prevId = self.convertFromStr(data, 'long')
        data = node.get('date', None)
        date = self.convertFromStr(data, 'datetime')
        data = node.get('session', None)
        session = self.convertFromStr(data, 'long')
        data = node.get('user', None)
        user = self.convertFromStr(data, 'str')
        
        annotations = []
        operations = []
        
        # read children
        for child in node.getchildren():
            if child.tag[0] == "{":
                child_tag = child.tag.split("}")[1]
            else:
                child_tag = child.tag
            if child_tag == 'annotation':
                _data = self.getDao('annotation').fromXML(child)
                annotations.append(_data)
            elif child_tag == 'add':
                _data = self.getDao('add').fromXML(child)
                operations.append(_data)
            elif child_tag == 'delete':
                _data = self.getDao('delete').fromXML(child)
                operations.append(_data)
            elif child_tag == 'change':
                _data = self.getDao('change').fromXML(child)
                operations.append(_data)
            elif child.text is None or child.text.strip() == '':
                pass
            else:
                print '*** ERROR *** tag = %s' % child.tag
        
        obj = DBAction(operations=operations,
                       id=id,
                       prevId=prevId,
                       date=date,
                       session=session,
                       user=user,
                       annotations=annotations)
        obj.is_dirty = False
        return obj
    
    def toXML(self, action, node=None):
        if node is None:
            node = ElementTree.Element('action')
        
        # set attributes
        node.set('id',self.convertToStr(action.db_id, 'long'))
        node.set('prevId',self.convertToStr(action.db_prevId, 'long'))
        node.set('date',self.convertToStr(action.db_date, 'datetime'))
        node.set('session',self.convertToStr(action.db_session, 'long'))
        node.set('user',self.convertToStr(action.db_user, 'str'))
        
        # set elements
        annotations = action.db_annotations
        for annotation in annotations:
            childNode = ElementTree.SubElement(node, 'annotation')
            self.getDao('annotation').toXML(annotation, childNode)
        operations = action.db_operations
        for operation in operations:
            if operation.vtType == 'add':
                childNode = ElementTree.SubElement(node, 'add')
                self.getDao('add').toXML(operation, childNode)
            elif operation.vtType == 'delete':
                childNode = ElementTree.SubElement(node, 'delete')
                self.getDao('delete').toXML(operation, childNode)
            elif operation.vtType == 'change':
                childNode = ElementTree.SubElement(node, 'change')
                self.getDao('change').toXML(operation, childNode)
        
        return node

class DBOpmAgentXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'agent':
            return None
        
        # read attributes
        data = node.get('id', None)
        id = self.convertFromStr(data, 'str')
        
        value = None
        accounts = []
        
        # read children
        for child in node.getchildren():
            if child.tag[0] == "{":
                child_tag = child.tag.split("}")[1]
            else:
                child_tag = child.tag
            if child_tag == 'value':
                _data = self.convertFromStr(child.text,'str')
                value = _data
            elif child_tag == 'account':
                _data = self.getDao('opm_account_id').fromXML(child)
                accounts.append(_data)
            elif child.text is None or child.text.strip() == '':
                pass
            else:
                print '*** ERROR *** tag = %s' % child.tag
        
        obj = DBOpmAgent(id=id,
                         value=value,
                         accounts=accounts)
        obj.is_dirty = False
        return obj
    
    def toXML(self, opm_agent, node=None):
        if node is None:
            node = ElementTree.Element('agent')
        
        # set attributes
        node.set('id',self.convertToStr(opm_agent.db_id, 'str'))
        
        # set elements
        value = opm_agent.db_value
        childNode = ElementTree.SubElement(node, 'value')
        childNode.text = self.convertToStr(value, 'str')
        accounts = opm_agent.db_accounts
        for account in accounts:
            childNode = ElementTree.SubElement(node, 'account')
            self.getDao('opm_account_id').toXML(account, childNode)
        
        return node

class DBDeleteXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'delete':
            return None
        
        # read attributes
        data = node.get('id', None)
        id = self.convertFromStr(data, 'long')
        data = node.get('what', None)
        what = self.convertFromStr(data, 'str')
        data = node.get('objectId', None)
        objectId = self.convertFromStr(data, 'long')
        data = node.get('parentObjId', None)
        parentObjId = self.convertFromStr(data, 'long')
        data = node.get('parentObjType', None)
        parentObjType = self.convertFromStr(data, 'str')
        
        obj = DBDelete(id=id,
                       what=what,
                       objectId=objectId,
                       parentObjId=parentObjId,
                       parentObjType=parentObjType)
        obj.is_dirty = False
        return obj
    
    def toXML(self, delete, node=None):
        if node is None:
            node = ElementTree.Element('delete')
        
        # set attributes
        node.set('id',self.convertToStr(delete.db_id, 'long'))
        node.set('what',self.convertToStr(delete.db_what, 'str'))
        node.set('objectId',self.convertToStr(delete.db_objectId, 'long'))
        node.set('parentObjId',self.convertToStr(delete.db_parentObjId, 'long'))
        node.set('parentObjType',self.convertToStr(delete.db_parentObjType, 'str'))
        
        return node

class DBProvAssociationXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'prov:Association':
            return None
        
        # read attributes
        data = node.get('id', None)
        id = self.convertFromStr(data, 'str')
        data = node.get('prov:hadRole', None)
        prov_hadRole = self.convertFromStr(data, 'str')
        data = node.get('prov:hadPlan', None)
        prov_hadPlan = self.convertFromStr(data, 'str')
        data = node.get('prov:Agent', None)
        prov_agent = self.convertFromStr(data, 'str')
        
        obj = DBProvAssociation(id=id,
                                prov_hadRole=prov_hadRole,
                                prov_hadPlan=prov_hadPlan,
                                prov_agent=prov_agent)
        obj.is_dirty = False
        return obj
    
    def toXML(self, prov_association, node=None):
        if node is None:
            node = ElementTree.Element('prov:Association')
        
        # set attributes
        node.set('id',self.convertToStr(prov_association.db_id, 'str'))
        node.set('prov:hadRole',self.convertToStr(prov_association.db_prov_hadRole, 'str'))
        node.set('prov:hadPlan',self.convertToStr(prov_association.db_prov_hadPlan, 'str'))
        node.set('prov:Agent',self.convertToStr(prov_association.db_prov_agent, 'str'))
        
        return node

class DBVistrailXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'vistrail':
            return None
        
        # read attributes
        data = node.get('id', None)
        id = self.convertFromStr(data, 'long')
        data = node.get('version', None)
        version = self.convertFromStr(data, 'str')
        data = node.get('name', None)
        name = self.convertFromStr(data, 'str')
        
        actions = []
        tags = []
        annotations = []
        vistrailVariables = []
        parameter_explorations = []
        actionAnnotations = []
        
        # read children
        for child in node.getchildren():
            if child.tag[0] == "{":
                child_tag = child.tag.split("}")[1]
            else:
                child_tag = child.tag
            if child_tag == 'action':
                _data = self.getDao('action').fromXML(child)
                actions.append(_data)
            elif child_tag == 'tag':
                _data = self.getDao('tag').fromXML(child)
                tags.append(_data)
            elif child_tag == 'annotation':
                _data = self.getDao('annotation').fromXML(child)
                annotations.append(_data)
            elif child_tag == 'vistrailVariable':
                _data = self.getDao('vistrailVariable').fromXML(child)
                vistrailVariables.append(_data)
            elif child_tag == 'parameter_exploration':
                _data = self.getDao('parameter_exploration').fromXML(child)
                parameter_explorations.append(_data)
            elif child_tag == 'actionAnnotation':
                _data = self.getDao('actionAnnotation').fromXML(child)
                actionAnnotations.append(_data)
            elif child.text is None or child.text.strip() == '':
                pass
            else:
                print '*** ERROR *** tag = %s' % child.tag
        
        obj = DBVistrail(id=id,
                         version=version,
                         name=name,
                         actions=actions,
                         tags=tags,
                         annotations=annotations,
                         vistrailVariables=vistrailVariables,
                         parameter_explorations=parameter_explorations,
                         actionAnnotations=actionAnnotations)
        obj.is_dirty = False
        return obj
    
    def toXML(self, vistrail, node=None):
        if node is None:
            node = ElementTree.Element('vistrail')
        
        # set attributes
        node.set('id',self.convertToStr(vistrail.db_id, 'long'))
        node.set('version',self.convertToStr(vistrail.db_version, 'str'))
        node.set('name',self.convertToStr(vistrail.db_name, 'str'))
        
        # set elements
        actions = vistrail.db_actions
        for action in actions:
            childNode = ElementTree.SubElement(node, 'action')
            self.getDao('action').toXML(action, childNode)
        tags = vistrail.db_tags
        for tag in tags:
            childNode = ElementTree.SubElement(node, 'tag')
            self.getDao('tag').toXML(tag, childNode)
        annotations = vistrail.db_annotations
        for annotation in annotations:
            childNode = ElementTree.SubElement(node, 'annotation')
            self.getDao('annotation').toXML(annotation, childNode)
        vistrailVariables = vistrail.db_vistrailVariables
        for vistrailVariable in vistrailVariables:
            childNode = ElementTree.SubElement(node, 'vistrailVariable')
            self.getDao('vistrailVariable').toXML(vistrailVariable, childNode)
        parameter_explorations = vistrail.db_parameter_explorations
        for parameter_exploration in parameter_explorations:
            childNode = ElementTree.SubElement(node, 'parameter_exploration')
            self.getDao('parameter_exploration').toXML(parameter_exploration, childNode)
        actionAnnotations = vistrail.db_actionAnnotations
        for actionAnnotation in actionAnnotations:
            childNode = ElementTree.SubElement(node, 'actionAnnotation')
            self.getDao('actionAnnotation').toXML(actionAnnotation, childNode)
        
        return node

class DBModuleExecXMLDAOBase(XMLDAO):

    def __init__(self, daoList):
        self.daoList = daoList

    def getDao(self, dao):
        return self.daoList[dao]

    def fromXML(self, node):
        if node.tag[0] == "{":
            node_tag = node.tag.split("}")[1]
        else:
            node_tag = node.tag
        if node_tag != 'moduleExec':
            return None
        
        # read attributes
        data = node.get('id', None)
        id = self.convertFromStr(data, 'long')
        data = node.get('tsStart', None)
        ts_start = self.convertFromStr(data, 'datetime')
        data = node.get('tsEnd', None)
        ts_end = self.convertFromStr(data, 'datetime')
        data = node.get('cached', None)
        cached = self.convertFromStr(data, 'int')
        data = node.get('moduleId', None)
        module_id = self.convertFromStr(data, 'long')
        data = node.get('moduleName', None)
        module_name = self.convertFromStr(data, 'str')
        data = node.get('completed', None)
        completed = self.convertFromStr(data, 'int')
        data = node.get('error', None)
        error = self.convertFromStr(data, 'str')
        data = node.get('machine_id', None)
        machine_id = self.convertFromStr(data, 'long')
        
        annotations = []
        loop_execs = []
        
        # read children
        for child in node.getchildren():
            if child.tag[0] == "{":
                child_tag = child.tag.split("}")[1]
            else:
                child_tag = child.tag
            if child_tag == 'annotation':
                _data = self.getDao('annotation').fromXML(child)
                annotations.append(_data)
            elif child_tag == 'loopExec':
                _data = self.getDao('loop_exec').fromXML(child)
                loop_execs.append(_data)
            elif child.text is None or child.text.strip() == '':
                pass
            else:
                print '*** ERROR *** tag = %s' % child.tag
        
        obj = DBModuleExec(id=id,
                           ts_start=ts_start,
                           ts_end=ts_end,
                           cached=cached,
                           module_id=module_id,
                           module_name=module_name,
                           completed=completed,
                           error=error,
                           machine_id=machine_id,
                           annotations=annotations,
                           loop_execs=loop_execs)
        obj.is_dirty = False
        return obj
    
    def toXML(self, module_exec, node=None):
        if node is None:
            node = ElementTree.Element('moduleExec')
        
        # set attributes
        node.set('id',self.convertToStr(module_exec.db_id, 'long'))
        node.set('tsStart',self.convertToStr(module_exec.db_ts_start, 'datetime'))
        node.set('tsEnd',self.convertToStr(module_exec.db_ts_end, 'datetime'))
        node.set('cached',self.convertToStr(module_exec.db_cached, 'int'))
        node.set('moduleId',self.convertToStr(module_exec.db_module_id, 'long'))
        node.set('moduleName',self.convertToStr(module_exec.db_module_name, 'str'))
        node.set('completed',self.convertToStr(module_exec.db_completed, 'int'))
        node.set('error',self.convertToStr(module_exec.db_error, 'str'))
        node.set('machine_id',self.convertToStr(module_exec.db_machine_id, 'long'))
        
        # set elements
        annotations = module_exec.db_annotations
        for annotation in annotations:
            childNode = ElementTree.SubElement(node, 'annotation')
            self.getDao('annotation').toXML(annotation, childNode)
        loop_execs = module_exec.db_loop_execs
        for loop_exec in loop_execs:
            childNode = ElementTree.SubElement(node, 'loopExec')
            self.getDao('loop_exec').toXML(loop_exec, childNode)
        
        return node

"""generated automatically by auto_dao.py"""

class XMLDAOListBase(dict):

    def __init__(self, daos=None):
        if daos is not None:
            dict.update(self, daos)

        if 'opm_process_id_effect' not in self:
            self['opm_process_id_effect'] = DBOpmProcessIdEffectXMLDAOBase(self)
        if 'vistrailVariable' not in self:
            self['vistrailVariable'] = DBVistrailVariableXMLDAOBase(self)
        if 'opm_was_generated_by' not in self:
            self['opm_was_generated_by'] = DBOpmWasGeneratedByXMLDAOBase(self)
        if 'opm_accounts' not in self:
            self['opm_accounts'] = DBOpmAccountsXMLDAOBase(self)
        if 'portSpec' not in self:
            self['portSpec'] = DBPortSpecXMLDAOBase(self)
        if 'module' not in self:
            self['module'] = DBModuleXMLDAOBase(self)
        if 'module_descriptor' not in self:
            self['module_descriptor'] = DBModuleDescriptorXMLDAOBase(self)
        if 'tag' not in self:
            self['tag'] = DBTagXMLDAOBase(self)
        if 'opm_role' not in self:
            self['opm_role'] = DBOpmRoleXMLDAOBase(self)
        if 'opm_processes' not in self:
            self['opm_processes'] = DBOpmProcessesXMLDAOBase(self)
        if 'opm_account_id' not in self:
            self['opm_account_id'] = DBOpmAccountIdXMLDAOBase(self)
        if 'port' not in self:
            self['port'] = DBPortXMLDAOBase(self)
        if 'prov_activities' not in self:
            self['prov_activities'] = DBProvActivitiesXMLDAOBase(self)
        if 'opm_artifact' not in self:
            self['opm_artifact'] = DBOpmArtifactXMLDAOBase(self)
        if 'group' not in self:
            self['group'] = DBGroupXMLDAOBase(self)
        if 'log' not in self:
            self['log'] = DBLogXMLDAOBase(self)
        if 'opm_agents' not in self:
            self['opm_agents'] = DBOpmAgentsXMLDAOBase(self)
        if 'opm_process_id_cause' not in self:
            self['opm_process_id_cause'] = DBOpmProcessIdCauseXMLDAOBase(self)
        if 'prov_generation' not in self:
            self['prov_generation'] = DBProvGenerationXMLDAOBase(self)
        if 'portSpecItem' not in self:
            self['portSpecItem'] = DBPortSpecItemXMLDAOBase(self)
        if 'machine' not in self:
            self['machine'] = DBMachineXMLDAOBase(self)
        if 'add' not in self:
            self['add'] = DBAddXMLDAOBase(self)
        if 'other' not in self:
            self['other'] = DBOtherXMLDAOBase(self)
        if 'location' not in self:
            self['location'] = DBLocationXMLDAOBase(self)
        if 'opm_overlaps' not in self:
            self['opm_overlaps'] = DBOpmOverlapsXMLDAOBase(self)
        if 'opm_artifacts' not in self:
            self['opm_artifacts'] = DBOpmArtifactsXMLDAOBase(self)
        if 'opm_dependencies' not in self:
            self['opm_dependencies'] = DBOpmDependenciesXMLDAOBase(self)
        if 'parameter' not in self:
            self['parameter'] = DBParameterXMLDAOBase(self)
        if 'prov_model' not in self:
            self['prov_model'] = DBProvModelXMLDAOBase(self)
        if 'opm_used' not in self:
            self['opm_used'] = DBOpmUsedXMLDAOBase(self)
        if 'plugin_data' not in self:
            self['plugin_data'] = DBPluginDataXMLDAOBase(self)
        if 'function' not in self:
            self['function'] = DBFunctionXMLDAOBase(self)
        if 'actionAnnotation' not in self:
            self['actionAnnotation'] = DBActionAnnotationXMLDAOBase(self)
        if 'vt_connections' not in self:
            self['vt_connections'] = DBVtConnectionsXMLDAOBase(self)
        if 'abstraction' not in self:
            self['abstraction'] = DBAbstractionXMLDAOBase(self)
        if 'workflow' not in self:
            self['workflow'] = DBWorkflowXMLDAOBase(self)
        if 'opm_artifact_id_cause' not in self:
            self['opm_artifact_id_cause'] = DBOpmArtifactIdCauseXMLDAOBase(self)
        if 'prov_agent' not in self:
            self['prov_agent'] = DBProvAgentXMLDAOBase(self)
        if 'prov_activity' not in self:
            self['prov_activity'] = DBProvActivityXMLDAOBase(self)
        if 'prov_entities' not in self:
            self['prov_entities'] = DBProvEntitiesXMLDAOBase(self)
        if 'prov_usage' not in self:
            self['prov_usage'] = DBProvUsageXMLDAOBase(self)
        if 'opm_artifact_value' not in self:
            self['opm_artifact_value'] = DBOpmArtifactValueXMLDAOBase(self)
        if 'opm_artifact_id_effect' not in self:
            self['opm_artifact_id_effect'] = DBOpmArtifactIdEffectXMLDAOBase(self)
        if 'opm_graph' not in self:
            self['opm_graph'] = DBOpmGraphXMLDAOBase(self)
        if 'registry' not in self:
            self['registry'] = DBRegistryXMLDAOBase(self)
        if 'vt_connection' not in self:
            self['vt_connection'] = DBVtConnectionXMLDAOBase(self)
        if 'opm_account' not in self:
            self['opm_account'] = DBOpmAccountXMLDAOBase(self)
        if 'prov_entity' not in self:
            self['prov_entity'] = DBProvEntityXMLDAOBase(self)
        if 'annotation' not in self:
            self['annotation'] = DBAnnotationXMLDAOBase(self)
        if 'change' not in self:
            self['change'] = DBChangeXMLDAOBase(self)
        if 'opm_was_derived_from' not in self:
            self['opm_was_derived_from'] = DBOpmWasDerivedFromXMLDAOBase(self)
        if 'opm_was_controlled_by' not in self:
            self['opm_was_controlled_by'] = DBOpmWasControlledByXMLDAOBase(self)
        if 'opm_agent_id' not in self:
            self['opm_agent_id'] = DBOpmAgentIdXMLDAOBase(self)
        if 'group_exec' not in self:
            self['group_exec'] = DBGroupExecXMLDAOBase(self)
        if 'opm_time' not in self:
            self['opm_time'] = DBOpmTimeXMLDAOBase(self)
        if 'package' not in self:
            self['package'] = DBPackageXMLDAOBase(self)
        if 'workflow_exec' not in self:
            self['workflow_exec'] = DBWorkflowExecXMLDAOBase(self)
        if 'parameter_exploration' not in self:
            self['parameter_exploration'] = DBParameterExplorationXMLDAOBase(self)
        if 'loop_exec' not in self:
            self['loop_exec'] = DBLoopExecXMLDAOBase(self)
        if 'prov_agents' not in self:
            self['prov_agents'] = DBProvAgentsXMLDAOBase(self)
        if 'connection' not in self:
            self['connection'] = DBConnectionXMLDAOBase(self)
        if 'opm_process' not in self:
            self['opm_process'] = DBOpmProcessXMLDAOBase(self)
        if 'opm_was_triggered_by' not in self:
            self['opm_was_triggered_by'] = DBOpmWasTriggeredByXMLDAOBase(self)
        if 'opm_process_value' not in self:
            self['opm_process_value'] = DBOpmProcessValueXMLDAOBase(self)
        if 'action' not in self:
            self['action'] = DBActionXMLDAOBase(self)
        if 'opm_agent' not in self:
            self['opm_agent'] = DBOpmAgentXMLDAOBase(self)
        if 'delete' not in self:
            self['delete'] = DBDeleteXMLDAOBase(self)
        if 'prov_association' not in self:
            self['prov_association'] = DBProvAssociationXMLDAOBase(self)
        if 'vistrail' not in self:
            self['vistrail'] = DBVistrailXMLDAOBase(self)
        if 'module_exec' not in self:
            self['module_exec'] = DBModuleExecXMLDAOBase(self)
