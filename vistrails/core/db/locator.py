############################################################################
##
## Copyright (C) 2006-2007 University of Utah. All rights reserved.
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

import os.path
from core.configuration import get_vistrails_configuration
from core.vistrail.vistrail import Vistrail
from core.system import vistrails_default_file_type
from db.services.locator import XMLFileLocator as _XMLFileLocator, \
    DBLocator as _DBLocator, ZIPFileLocator as _ZIPFileLocator
import core.configuration

class CoreLocator(object):

    @staticmethod
    def load_from_gui(parent_widget):
        pass # Opens a dialog that the user will be able to use to
             # show the right values, and returns a locator suitable
             # for loading a file

    @staticmethod
    def save_from_gui(parent_widget, locator):
        pass # Opens a dialog that the user will be able to use to
             # show the right values, and returns a locator suitable
             # for saving a file

class XMLFileLocator(_XMLFileLocator, CoreLocator):

    def __init__(self, filename):
        _XMLFileLocator.__init__(self, filename)
        
    def load(self):
        vistrail = _XMLFileLocator.load(self)
        Vistrail.convert(vistrail)
        vistrail.locator = self
        return vistrail

    def save(self, vistrail):
        vistrail = _XMLFileLocator.save(self, vistrail, False)
        Vistrail.convert(vistrail)
        vistrail.locator = self
        return vistrail

    def save_as(self, vistrail):
        vistrail = _XMLFileLocator.save(self, vistrail, True)
        Vistrail.convert(vistrail)
        vistrail.locator = self
        return vistrail

    ##########################################################################

    def __eq__(self, other):
        if type(other) != XMLFileLocator:
            return False
        return self._name == other._name

    ##########################################################################

    @staticmethod
    def load_from_gui(parent_widget):
        import gui.extras.core.db.locator as db_gui
        return db_gui.get_load_file_locator_from_gui(parent_widget)

    @staticmethod
    def save_from_gui(parent_widget, locator=None):
        import gui.extras.core.db.locator as db_gui
        return db_gui.get_save_file_locator_from_gui(parent_widget, 
                                                         locator)

class DBLocator(_DBLocator, CoreLocator):

    def __init__(self, host, port, database, user, passwd, name=None,
                 vistrail_id=None, connection_id=None):
        _DBLocator.__init__(self, host, port, database, user, passwd, name,
                            vistrail_id, connection_id)

    def load(self):
        vistrail = _DBLocator.load(self)
        Vistrail.convert(vistrail)
        vistrail.locator = self
        return vistrail

    def save(self, vistrail):
        vistrail = _DBLocator.save(self, vistrail, False)
        Vistrail.convert(vistrail)
        vistrail.locator = self
        return vistrail

    def save_as(self, vistrail):
        vistrail = _DBLocator.save(self, vistrail, True)
        Vistrail.convert(vistrail)
        vistrail.locator = self
        return vistrail

    ##########################################################################

    def __eq__(self, other):
        if type(other) != type(self):
            return False
        return (self._host == other._host and
                self._port == other._port and
                self._db == other._db and
                self._user == other._user and
                self._vt_name == other._vt_name and
                self._vt_id == other._vt_id)

    ##########################################################################
        
    @staticmethod
    def load_from_gui(parent_widget):
        import gui.extras.core.db.locator as db_gui
        return db_gui.get_load_db_locator_from_gui(parent_widget)

    @staticmethod
    def save_from_gui(parent_widget, locator=None):
        import gui.extras.core.db.locator as db_gui
        return db_gui.get_save_db_locator_from_gui(parent_widget, locator)

class ZIPFileLocator(_ZIPFileLocator, CoreLocator):

    def __init__(self, filename):
        _ZIPFileLocator.__init__(self, filename)
        
    def load(self):
        vistrail = _ZIPFileLocator.load(self)
        Vistrail.convert(vistrail)
        vistrail.locator = self
        return vistrail

    def save(self, vistrail):
        vistrail = _ZIPFileLocator.save(self, vistrail, False)
        Vistrail.convert(vistrail)
        vistrail.locator = self
        return vistrail

    def save_as(self, vistrail):
        vistrail = _ZIPFileLocator.save(self, vistrail, True)
        Vistrail.convert(vistrail)
        vistrail.locator = self
        return vistrail

    ##########################################################################

    def __eq__(self, other):
        if type(other) != ZIPFileLocator:
            return False
        return self._name == other._name

    ##########################################################################

    @staticmethod
    def load_from_gui(parent_widget):
        import gui.extras.core.db.locator as db_gui
        return db_gui.get_load_file_locator_from_gui(parent_widget)

    @staticmethod
    def save_from_gui(parent_widget, locator=None):
        import gui.extras.core.db.locator as db_gui
        return db_gui.get_save_file_locator_from_gui(parent_widget, 
                                                         locator)

class FileLocator(CoreLocator):
    def __new__(self, *args):
        if len(args) > 0:
            filename = args[0]
            if filename.endswith('.vt'):
                return ZIPFileLocator(filename)
            else:
                return XMLFileLocator(filename)
        else:
            #return class based on default file type
            if vistrails_default_file_type() == '.vt':
                return ZIPFileLocator
            else:
                return XMLFileLocator
    
    @staticmethod
    def load_from_gui(parent_widget):
        import gui.extras.core.db.locator as db_gui
        return db_gui.get_load_file_locator_from_gui(parent_widget)

    @staticmethod
    def save_from_gui(parent_widget, locator=None):
        import gui.extras.core.db.locator as db_gui
        return db_gui.get_save_file_locator_from_gui(parent_widget, 
                                                         locator)

    @staticmethod
    def parse(element):
        """ parse(element) -> XMLFileLocator
        Parse an XML object representing a locator and returns an
        XMLFileLocator or a ZIPFileLocator object.

        """
        if str(element.getAttribute('type')) == 'file':
            for n in element.childNodes:
                if n.localName == "name":
                    filename = str(n.firstChild.nodeValue).strip(" \n\t")
                    return FileLocator(filename)
            return None
        else:
            return None

def untitled_locator():
    basename = 'untitled' + vistrails_default_file_type()
    config = get_vistrails_configuration()
    if config:
        dot_vistrails = config.dotVistrails
    else:
        dot_vistrails = core.system.default_dot_vistrails()
    fullname = os.path.join(dot_vistrails, basename)
    return FileLocator(fullname)
