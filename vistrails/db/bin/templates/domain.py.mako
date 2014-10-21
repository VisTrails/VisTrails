<%
def getIndexName(index):
    if type(index) == type([]):
        # return '_'.join(index)
        if index[0][0] == '!':
            return index[0][1:]
        return index[0]
    else:
        if index[0] == '!':
            return index[1:]
        return index

def getIndexKey(field_str, index):
    if type(index) == type([]):
        if index[0][0] == '!':
            index = [index[0][1:]] + index[1:]
        return '(' + field_str + '.db_' + \
            (',' + field_str + '.db_').join(index) + ')'
    else:
        if index[0] == '!':
            index = index[1:]
        return field_str + '.db_' + index

def shouldIgnoreIndexDelete(index):
    if type(index) == type([]):
        return index[0][0] == '!'
    return index[0] == '!'
%> \\
<%text>###############################################################################
##
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
</%text>
"""generated automatically by auto_dao.py"""

import copy

% for obj in objs:
class ${obj.getClassName()}(object):

    vtType = '${obj.getRegularName()}'

    def __init__(self, ${', '.join(['%s=None' % n \
                                    for n in obj.getConstructorNames()])}):
        % for field in obj.getPythonFields():
        % if field.isReference() and not field.isInverse():
        self.db_deleted_${field.getRegularName()} = []
        % endif
        % if field.isPlural():
        % for index in field.getAllIndices():
        self.db_${field.getRegularName()}_${getIndexName(index)}_index = {}
        % endfor
        if ${field.getRegularName()} is None:
            % if field.getPythonType() == 'hash':
            self.${field.getPrivateName()} = {}
            % else:
            self.${field.getPrivateName()} = []
            % endif
        else:
            self.${field.getPrivateName()} = ${field.getRegularName()}
            % if len(field.getAllIndices()) > 0:
            % if field.getPythonType() == 'hash':
            for v in self.${field.getPrivateName()}.itervalues():
            % else:
            for v in self.${field.getPrivateName()}:
            % endif
                % for index in field.getAllIndices():
                self.db_${field.getRegularName()}_${getIndexName(index)}_ \!
                    index[${getIndexKey('v', index)}] = v
                % endfor
            % endif
        % else:
        self.${field.getPrivateName()} = ${field.getRegularName()}
        % endif
        % endfor
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return ${obj.getClassName()}.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = ${obj.getClassName()}( \!
            ${',\n'.join(['%s=self.%s' % f for f in obj.getCopyNames()])})
        % for field in obj.getPythonFields():
        % if field.isPlural():
        if self.${field.getPrivateName()} is None:
            % if field.getPythonType() == 'hash':
            cp.${field.getPrivateName()} = {}
            % else:
            cp.${field.getPrivateName()} = []
            % endif
        else:
            % if field.getPythonType() == 'hash':
            % if field.shouldExpand():
            cp.${field.getPrivateName()} = \
                dict([(k, v.do_copy(new_ids, id_scope, id_remap)) \
                      for (k,v) in self.${field.getPrivateName()}.iteritems()])
            % else:
            cp.${field.getPrivateName()} = \
                dict([(k, v.do_copy()) \
                      for (k,v) in self.${field.getPrivateName()}.iteritems()])
            % endif
            % else:
            % if field.shouldExpand():
            cp.${field.getPrivateName()} = \
                [v.do_copy(new_ids, id_scope, id_remap) \
                     for v in self.${field.getPrivateName()}]
            % else:
            cp.${field.getPrivateName()} = \
                [v.do_copy() for v in self.${field.getPrivateName()}]
            % endif
            % endif
        % else:
        % if field.isReference():
        if self.${field.getPrivateName()} is not None:
            % if field.shouldExpand():
            cp.${field.getPrivateName()} = \
                self.${field.getPrivateName()}.do_copy(new_ids, id_scope, \
                                                           id_remap)
            % else:
            cp.${field.getPrivateName()} = \
                self.${field.getPrivateName()}.do_copy()
            % endif
        % endif
        % endif
        % endfor
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
            % if len(obj.getForeignKeys()) > 0:
            % for field in obj.getForeignKeys():
            <% 
            if field.hasDiscriminator():
                disc_prop = obj.getDiscriminatorProperty( \
                    field.getDiscriminator())
                lookup_str = "self.%s" % disc_prop.getPrivateName()
            else:
                ref_obj = field.getReferencedObject()
                lookup_str = "'%s'" % ref_obj.getRegularName()
            %> \\
            if hasattr(self, '${field.getFieldName()}') and \
                    (${lookup_str}, self.${field.getPrivateName()}) in id_remap:
                cp.${field.getPrivateName()} = \
                         id_remap[(${lookup_str}, \
                                        self.${field.getPrivateName()})]
            % endfor
            % endif
        
        # recreate indices and set flags
        % for field in obj.getPythonFields():
        % if len(field.getAllIndices()) > 0:
        % for index in field.getAllIndices():
        cp.db_${field.getRegularName()}_${getIndexName(index)}_index = \
            dict((${getIndexKey('v', index)}, v) \
                     for v in cp.${field.getPrivateIterator()})
        % endfor
        % endif
        % endfor
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    ## create static update_version
    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = ${obj.getClassName()}()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        % for field in obj.getPythonFields():
        if '${field.getRegularName()}' in class_dict:
            res = class_dict['${field.getRegularName()}'](old_obj, trans_dict)
            % if field.isPlural():
            for obj in res:
                new_obj.${field.getAppender()}(obj)
            % else:
            new_obj.${field.getFieldName()} = res
            % endif
        elif hasattr(old_obj, '${field.getFieldName()}') and \
                old_obj.${field.getFieldName()} is not None:
            % if field.isReference():
            ## refObj = field.getReferencedObject()
            % if field.isPlural():
            for obj in old_obj.${field.getIterator()}:
                % if field.isChoice():
                <% cond = 'if' %> \\
                % for prop in field.properties:
                ## if prop.isReference():
                ## propRefObj = prop.getReferencedObject()
                ${cond} obj.vtType == \
                    '${prop.getReferencedObject().getRegularName()}':
                    new_obj.${field.getAppender()}( \!
                        ${prop.getReferencedObject().getClassName()}. \!
                         update_version(obj, trans_dict))
                <% cond = 'elif' %> \\
                % endfor
                % else:
                new_obj.${field.getAppender()}( \!
                    ${field.getReferencedObject().getClassName()}. \!
                     update_version(obj, trans_dict))
                % endif
            % else:
            obj = old_obj.${field.getFieldName()}
            % if field.isChoice():
            <% cond = 'if' %> \\
            % for prop in field.properties:
            ## if prop.isReference():
            ## propRefObj = prop.getReferencedObject()
            ${cond} obj.vtType == \
                '${prop.getReferencedObject().getRegularName()}':
                new_obj.${field.getAppender()}( \!
                    ${prop.getReferencedObject().getClassName()}. \!
                     update_version(obj, trans_dict))
            <% cond = 'elif' %> \\
            % endfor
            % else:
            new_obj.${field.getAppender()}( \!
                ${field.getReferencedObject().getClassName()}. \!
                 update_version(obj, trans_dict))
            % endif
            % endif
        % if not field.isInverse():
        if hasattr(old_obj, 'db_deleted_${field.getRegularName()}') \
                and hasattr(new_obj, 'db_deleted_${field.getRegularName()}'):
            ## refObj = field.getReferencedObject()
            for obj in old_obj.db_deleted_${field.getRegularName()}:
                % if field.isChoice():
                <% cond = 'if' %> \\
                % for prop in field.properties:
                ## if prop.isReference():
                ## propRefObj = prop.getReferencedObject()
                ${cond} obj.vtType == \
                    '${prop.getReferencedObject().getRegularName()}':
                    n_obj = ${prop.getReferencedObject().getClassName()}. \!
                        update_version(obj, trans_dict)
                    new_obj.db_deleted_${field.getRegularName()}.append(n_obj)
                <% cond = 'elif' %> \\
                % endfor
                % else:
                n_obj = ${field.getReferencedObject().getClassName()}. \!
                    update_version(obj, trans_dict)
                new_obj.db_deleted_${field.getRegularName()}.append(n_obj)
                % endif
        % endif
        % else:
            new_obj.${field.getFieldName()} = old_obj.${field.getFieldName()}
        % endif
        % endfor
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    ## create child methods
    def ${obj.getChildren()}(self, parent=(None,None), orphan=False, for_action=False):
        % if not any([not ref.isInverse() and ref.shouldExpand() \
                      for ref in obj.getReferences()]):
        return [(self, parent[0], parent[1])]
        % else:
        children = []
        % for ref in obj.getReferences():
        % if not ref.isInverse() and ref.shouldExpand():
        ## refObj = ref.getReferencedObject()
        % if not ref.shouldExpandAction():
        if not for_action:
            % if not ref.isPlural():
            if self.${ref.getPrivateName()} is not None:
                children.extend(self.${ref.getPrivateName()}. \!
                                ${ref.getReferencedObject().getChildren()}( \!
                                (self.vtType, self.db_id), orphan, for_action))
            % else:
            for child in self.${ref.getIterator()}:
                children.extend(child.${ref.getReferencedObject().getChildren()}( \!
                                (self.vtType, self.db_id), orphan, for_action))
            % endif
        % else:
        % if not ref.isPlural():
        if self.${ref.getPrivateName()} is not None:
            children.extend(self.${ref.getPrivateName()}. \!
                            ${ref.getReferencedObject().getChildren()}( \!
                                (self.vtType, self.db_id), orphan, for_action))
            if orphan:
                self.${ref.getPrivateName()} = None
        % else:
        to_del = []
        for child in self.${ref.getIterator()}:
            children.extend(child.${ref.getReferencedObject().getChildren()}( \!
                                (self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.${ref.getRemover()}(child)
        % endif
        % endif
        % endif
        % endfor
        children.append((self, parent[0], parent[1]))
        return children
        % endif
    ## get deleted method
    def db_deleted_children(self, remove=False):
        children = []
        % if len(obj.getNonInverseReferences()) > 0:
        % for ref in obj.getNonInverseReferences():
        children.extend(self.db_deleted_${ref.getRegularName()})
        % endfor
        if remove:
            % for ref in obj.getNonInverseReferences():
            self.db_deleted_${ref.getRegularName()} = []
            % endfor
        % endif
        return children
    ## dirty method
    def has_changes(self):
        if self.is_dirty:
            return True
        % for ref in obj.getNonInverseReferences():
        % if not ref.isPlural():
        if self.${ref.getPrivateName()} is not None and \
                self.${ref.getPrivateName()}.has_changes():
            return True
        % else:
        for child in self.${ref.getPrivateIterator()}:
            if child.has_changes():
                return True
        % endif
        % endfor
        return False
    ## create methods
    % for field in obj.getPythonFields():
    def ${field.getDefineAccessor()}(self):
        return self.${field.getPrivateName()}
    def ${field.getDefineMutator()}(self, ${field.getRegularName()}):
        self.${field.getPrivateName()} = ${field.getRegularName()}
        self.is_dirty = True
    ${field.getFieldName()} = property(${field.getDefineAccessor()}, \
                                            ${field.getDefineMutator()})
    % if not field.isPlural():
    def ${field.getAppender()}(self, ${field.getName()}):
        self.${field.getPrivateName()} = ${field.getName()}
    def ${field.getModifier()}(self, ${field.getName()}):
        self.${field.getPrivateName()} = ${field.getName()}
    def ${field.getRemover()}(self, ${field.getName()}):
        % if field.isReference() and not field.isInverse():
        if not self.is_new:
            self.db_deleted_${field.getRegularName()}.append( \!
                self.${field.getPrivateName()})
        % endif
        self.${field.getPrivateName()} = None
    % else:
    def ${field.getList()}(self):
        return self.${field.getListValues()}
    def ${field.getAppender()}(self, ${field.getName()}):
        self.is_dirty = True
        % if field.getPythonType() == 'hash':
        self.${field.getPrivateName()}[${field.getName()}. \!
            ${field.getReferencedObject().getKey().getPythonName()}] = \
                ${field.getName()}
        % else:
        self.${field.getPrivateName()}.append(${field.getName()})
        % endif
        % for index in field.getAllIndices():
        self.db_${field.getRegularName()}_${getIndexName(index)}_index[ \!
            ${getIndexKey(field.getName(), index)}] = ${field.getName()}
        % endfor
    def ${field.getModifier()}(self, ${field.getName()}):
        self.is_dirty = True
        % if field.getPythonType() == 'hash':
        ## childObj = field.getReferencedObject()
        self.${field.getPrivateName()}[${field.getName()}. \!
            ${field.getReferencedObject().getKey().getPythonName()}] = \
                ${field.getName()}
        % else:
        ## childObj = field.getReferencedObject()
        % if field.getReferencedObject().getKey() is not None:
        found = False
        for i in xrange(len(self.${field.getPrivateName()})):
            if self.${field.getPrivateName()}[i]. \!
                ${field.getReferencedObject().getKey().getPythonName()} == \
                    ${field.getName()}. \!
                    ${field.getReferencedObject().getKey().getPythonName()}:
                self.${field.getPrivateName()}[i] = ${field.getName()}
                found = True
                break
        if not found:
            self.${field.getPrivateName()}.append(${field.getName()})
        % else:
        self.${field.getPrivateName()}.append(${field.getName()})
        % endif
        % endif
        % for index in field.getAllIndices():
        self.db_${field.getRegularName()}_${getIndexName(index)}_index[ \!
            ${getIndexKey(field.getName(), index)}] = ${field.getName()}
        % endfor
    def ${field.getRemover()}(self, ${field.getName()}):
        self.is_dirty = True
        % if field.getPythonType() == 'hash':
        ## childObj = field.getReferencedObject()
        if not self.${field.getPrivateName()}[${field.getName()}. \!
            ${field.getReferencedObject().getKey().getPythonName()}].is_new:
            self.db_deleted_${field.getRegularName()}.append( \!
                self.${field.getPrivateName()}[${field.getName()}. \!
                    ${field.getReferencedObject().getKey().getPythonName()}])
        del self.${field.getPrivateName()}[${field.getName()}. \!
            ${field.getReferencedObject().getKey().getPythonName()}]
        % else:
        % if field.getReferencedObject().getKey() is None:
        raise Exception('Cannot delete a non-keyed object')
        % else:
        for i in xrange(len(self.${field.getPrivateName()})):
            if self.${field.getPrivateName()}[i]. \!
                ${field.getReferencedObject().getKey().getPythonName()} == \
                    ${field.getName()}. \!
                    ${field.getReferencedObject().getKey().getPythonName()}:
                if not self.${field.getPrivateName()}[i].is_new:
                    self.db_deleted_${field.getRegularName()}.append( \!
                        self.${field.getPrivateName()}[i])
                del self.${field.getPrivateName()}[i]
                break
        % endif
        % endif
        % if field.getPythonType() == 'hash' or field.getReferencedObject().getKey() is not None:
        % for index in field.getAllIndices():
        % if shouldIgnoreIndexDelete(index):
        try:
            del self.db_${field.getRegularName()}_${getIndexName(index)}_ \!
                index[${getIndexKey(field.getName(), index)}]
        except KeyError:
            pass
        % else:
        del self.db_${field.getRegularName()}_${getIndexName(index)}_ \!
            index[${getIndexKey(field.getName(), index)}]
        % endif
        % endfor
        % endif
    def ${field.getLookup()}(self, key):
        % if field.getPythonType() == 'hash':
        if key in self.${field.getPrivateName()}:
            return self.${field.getPrivateName()}[key]
        return None
        % else:
        % if field.getReferencedObject().getKey() is not None:
        for i in xrange(len(self.${field.getPrivateName()})):
            if self.${field.getPrivateName()}[i]. \!
                ${field.getReferencedObject().getKey().getPythonName()} == key:
                return self.${field.getPrivateName()}[i]
        % endif
        return None
        % endif
    % endif
    % for index in field.getAllIndices():
    def db_get_${field.getSingleName()}_by_${getIndexName(index)}(self, key):
        return self.db_${field.getRegularName()}_ \!
            ${getIndexName(index)}_index[key]
    def db_has_${field.getSingleName()}_with_${getIndexName(index)}(self, key):
        return key in self.db_${field.getRegularName()}_ \!
            ${getIndexName(index)}_index
    % endfor
    
    % endfor
    % if obj.getKey() is not None:
    def getPrimaryKey(self):
        return self.${obj.getKey().getPrivateName()}
    % else:

    % endif

% endfor
