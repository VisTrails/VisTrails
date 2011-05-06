############################################################################
##
## Copyright (C) 2006-2010 University of Utah. All rights reserved.
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
import os
import stat
from time import localtime
from datetime import datetime
from core.thumbnails import ThumbnailCache

from entity import Entity

class ThumbnailEntity(Entity):
    type_id = 4

    def __init__(self, thumbnail=None):
        Entity.__init__(self)
        self.id = None
        self.update(thumbnail)

    @staticmethod
    def load(*args):
        entity = ThumbnailEntity()
        Entity.load(entity, *args)
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
            time = datetime(*localtime(statinfo[stat.ST_MTIME])[:6]).strftime('%d %b %Y %H:%M:%S')
            self.mod_time = ''
            self.create_time = time
            self.description = ""
            self.url = 'test'
            self.was_updated = True
