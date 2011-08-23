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

from auto_gen import DBWorkflow as _DBWorkflow
from id_scope import IdScope

import copy

class DBWorkflow(_DBWorkflow):

    def __init__(self, *args, **kwargs):
	_DBWorkflow.__init__(self, *args, **kwargs)
	self.objects = {}
        self.tmp_id = IdScope(1)

    def __copy__(self):
        return DBWorkflow.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = _DBWorkflow.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = DBWorkflow
        # need to go through and reset the index to the copied objects
        cp.objects = {}
        for (child, _, _) in cp.db_children():
            cp.addToIndex(child)
        cp.tmp_id = copy.copy(self.tmp_id)
        return cp        

    def addToIndex(self, object):
        self.objects[(object.vtType, object.getPrimaryKey())] = object

    def deleteFromIndex(self, object):
	del self.objects[(object.vtType, object.getPrimaryKey())]

    def capitalizeOne(self, str):
	return str[0].upper() + str[1:]

    def db_print_objects(self):
        for k,v in self.objects.iteritems():
            print '%s: %s' % (k, v)

    def db_get_object(self, type, id):
        return self.objects[(type, id)]

    def db_add_object(self, object, parentObjType=None, parentObjId=None):
	if parentObjType is None or parentObjId is None:
	    parentObj = self
	else:
	    try:
		parentObj = self.objects[(parentObjType, parentObjId)]
	    except KeyError:
		msg = "Cannot find object of type '%s' with id '%s'" % \
		    (parentObjType, parentObjId)
		raise Exception(msg)
	funname = 'db_add_%s' % object.vtType
	objCopy = copy.copy(object)
	getattr(parentObj, funname)(objCopy)
	self.addToIndex(objCopy)

    def db_change_object(self, object, parentObjType=None, parentObjId=None):
	if parentObjType is None or parentObjId is None:
	    parentObj = self
	else:
	    try:
		parentObj = self.objects[(parentObjType, parentObjId)]
	    except KeyError:
		msg = "Cannot find object of type '%s' with id '%s'" % \
		    (parentObjType, parentObjId)
		raise Exception(msg)
	funname = 'db_change_%s' % object.vtType
	objCopy = copy.copy(object)
	getattr(parentObj, funname)(objCopy)
	self.addToIndex(objCopy)

    def db_delete_object(self, objId, objType, 
                         parentObjType=None, parentObjId=None):
	if parentObjType is None or parentObjId is None:
	    parentObj = self
	else:
	    try:
		parentObj = self.objects[(parentObjType, parentObjId)]
	    except KeyError:
		msg = "Cannot find object of type '%s' with id '%s'" % \
		    (parentObjType, parentObjId)
		raise Exception(msg)
	funname = 'db_get_%s' % objType
        try:
            object = getattr(parentObj, funname)(objId)
        except AttributeError:
            attr_name = 'db_%s' % objType
            object = getattr(parentObj, attr_name)
	funname = 'db_delete_%s' % objType
	getattr(parentObj, funname)(object)
	self.deleteFromIndex(object)
