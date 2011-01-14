import os
import stat
from time import localtime
from datetime import datetime
import urlparse
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
