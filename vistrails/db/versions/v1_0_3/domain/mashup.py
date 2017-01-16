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

from auto_gen import DBMashuptrail as _DBMashuptrail
from id_scope import IdScope


class DBMashuptrail(_DBMashuptrail):
    def __init__(self, *args, **kwargs):
        _DBMashuptrail.__init__(self, *args, **kwargs)
        self.idScope = IdScope(1L)

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBMashuptrail()
        new_obj = _DBMashuptrail.update_version(old_obj, trans_dict, new_obj)
        new_obj.update_id_scope()
        return new_obj

    def update_id_scope(self):
        for action in self.db_actions:
            self.idScope.updateBeginId('mashup_action', action.db_id+1)
            for alias in action.db_mashup.db_aliases:
                self.idScope.updateBeginId('mashup_alias', alias.db_id+1)
                self.idScope.updateBeginId('mashup_component', alias.db_component.db_id+1)
        for annotation in self.db_annotations:
            self.idScope.updateBeginId('annotation', annotation.db_id+1)
        for aannotation in self.db_actionAnnotations:
            self.idScope.updateBeginId('mashup_actionAnnotation', aannotation.db_id+1)

