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

from core.configuration import get_vistrails_persistent_configuration, \
        get_vistrails_configuration
from core.db.locator import FileLocator
import core.system
import os

from javax.swing import JFileChooser, JOptionPane
from javax.swing.filechooser import FileFilter, FileNameExtensionFilter

from extras.core.db.locator import LocatorHelperProvider


class JavaLocatorHelperProvider(LocatorHelperProvider):
    """Provides the Java implementations of locator-related helpers.
    """
    def __init__(self, parent_window):
        self.parent_window = parent_window

##############################################################################
# DB dialogs

    @staticmethod
    def get_load_db_locator_from_gui(obj_type):
        # TODO : DB dialog
        return None

    @staticmethod
    def get_save_db_locator_from_gui(obj_type, locator=None):
        # TODO : DB dialog
        return None

##############################################################################

    def get_db_connection_from_gui(self, id, name, host, port, user, passwd,
                                   database):
        # TODO : DB connection dialog
        return None

##############################################################################
# File dialogs

    suffix_map = {'vistrail': ['vt', 'xml', 'vtl'],
                  'workflow': ['xml'],
                  'log': ['xml'],
                  'registry': ['xml'],
                  'opm_graph': ['xml'],
                  }

    class AllFileFilter(FileFilter):
        # @Override
        def getDescription(self):
            return "Other files (*)"

        # @Override
        def accept(self, f):
            return True

    def get_load_file_locator_from_gui(self, obj_type):
        readable = "*" + " *".join(JavaLocatorHelperProvider.suffix_map[obj_type])
        suffixes = JavaLocatorHelperProvider.suffix_map[obj_type]
        chooser = JFileChooser()
        chooser.setFileFilter(FileNameExtensionFilter(
                "VisTrails files (%s)" % readable, *suffixes))
        chooser.addChoosableFileFilter(JavaLocatorHelperProvider.AllFileFilter())

        if chooser.showOpenDialog(self.parent_window) == JFileChooser.APPROVE_OPTION:
            filename = chooser.getSelectedFile().getAbsolutePath()
            dirname = os.path.dirname(filename)
            setattr(get_vistrails_persistent_configuration(), 'fileDirectory', dirname)
            setattr(get_vistrails_configuration(), 'fileDirectory', dirname)
            core.system.set_vistrails_file_directory(dirname)
            return FileLocator(filename)
        else:
            return None

    def get_save_file_locator_from_gui(self, obj_type, locator=None):
        # Ignore current locator for now
        # In the future, use locator to guide GUI for better starting directory

        readable = "*" + " *".join(
                JavaLocatorHelperProvider.suffix_map[obj_type])
        suffixes = JavaLocatorHelperProvider.suffix_map[obj_type]
        chooser = JFileChooser()
        chooser.setFileFilter(FileNameExtensionFilter(
                "VisTrails files (%s)" % readable, suffixes))
        if chooser.showSaveDialog(self.parent_window) != JFileChooser.APPROVE_OPTION:
            return None

        f = chooser.getSelectedFile().getAbsolutePath()

        # check for proper suffix
        found_suffix = False
        for suffix in JavaLocatorHelperProvider.suffix_map[obj_type]:
            if f.endswith(suffix):
                found_suffix = True
                break
        if not found_suffix:
            if obj_type == 'vistrail':
                f += get_vistrails_configuration().defaultFileType
            else:
                f += JavaLocatorHelperProvider.suffix_map[obj_type][0]

        if os.path.isfile(f):
            result = JOptionPane.showConfirmDialog(
                    self.parent_window,
                    "File exists. Overwrite?", "VisTrails",
                    JOptionPane.YES_NO_OPTION)
            if result == JOptionPane.NO_OPTION:
                return None

        dirname = os.path.dirname(str(f))
        setattr(get_vistrails_persistent_configuration(), 'fileDirectory', dirname)
        setattr(get_vistrails_configuration(), 'fileDirectory', dirname)
        core.system.set_vistrails_file_directory(dirname)
        return FileLocator(f)

    def get_autosave_prompt(self):
        """ get_autosave_prompt(parent: QWidget) -> bool

        """
        result = JOptionPane.showConfirmDialog(
                    self.parent_window,
                    "Autosave data has been found.\nDo you want to open "
                    "autosave data?", "AutoSave", JOptionPane.YES_NO_OPTION)
        return result == JOptionPane.YES_OPTION

    def ask_to_overwrite_file(self, obj_type='vistrail'):
        overwrite = True
        fname = None
        result = JOptionPane.showConfirmDialog(
                    self.parent_window,
                    "File exists and contains changes. Overwrite?",
                    "VisTrails", JOptionPane.YES_NO_OPTION)
        if result == JOptionPane.NO_OPTION:
            overwrite = False
            locator = JavaLocatorHelperProvider.get_save_file_locator_from_gui(
                    self.parent_widget, obj_type)
            if locator:
                fname = locator._name
        return (overwrite, fname)
