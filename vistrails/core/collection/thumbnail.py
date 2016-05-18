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

import os
import stat
from time import localtime
from datetime import datetime
from vistrails.core.thumbnails import ThumbnailCache

from entity import Entity

class ThumbnailEntity(Entity):
    type_id = 4

    def __init__(self, thumbnail=None):
        Entity.__init__(self)
        self.id = None
        self.update(thumbnail)

    @staticmethod
    def create(*args):
        entity = ThumbnailEntity()
        entity.load(*args)
        return entity

    def update(self, thumbnail):
        self.thumbnail = thumbnail
        if self.thumbnail is not None:
            # store in cache if not already there
            cache = ThumbnailCache.getInstance()
            cache._copy_thumbnails([thumbnail])
            self.name = os.path.basename(thumbnail)
            statinfo = os.stat(self.thumbnail)
            self.user = statinfo[stat.ST_UID]
            self.size = statinfo[stat.ST_SIZE]
            time = datetime(*localtime(statinfo[stat.ST_MTIME])[:6])
            self.mod_time = time
            self.create_time = time
            self.description = ""
            self.url = 'test'
            self.was_updated = True
