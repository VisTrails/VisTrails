############################################################################ ##
## Copyright (C) 2006-2009 University of Utah. All rights reserved.
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
"""
Dialog for web repository options
Includes login and upload tabs
"""

from PyQt4 import QtGui, QtCore
from core.configuration import get_vistrails_persistent_configuration
from core.repository.poster.encode import multipart_encode
from core.repository.poster.streaminghttp import register_openers
from core.vistrail.controller import VistrailController
import urllib, urllib2, cookielib
import os
import tempfile
import api

##############################################################################

class QRepositoryPushWidget(QtGui.QWidget):
    """ Tab that shows main repository options
        It currently only allows users to login and push
        VisTrails to the Repository """

    def __init__(self, parent, status_bar, dialog):
        QtGui.QWidget.__init__(self, parent)
        self._status_bar = status_bar
        self.dialog = dialog

        base_layout = QtGui.QHBoxLayout(self)

        right = QtGui.QFrame(self)

        base_layout.addWidget(right)

        self._repository_status = {}

        self.config = get_vistrails_persistent_configuration()

        ######################################################################
        # Push info
        right_layout = QtGui.QVBoxLayout(right)

        self._vistrail_status_label = QtGui.QLabel("")
        right_layout.addWidget(self._vistrail_status_label)

        self._details_label = QtGui.QLabel("")
        right_layout.addWidget(self._details_label)

        for lbl in [self._details_label, self._vistrail_status_label]:
            lbl.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
            lbl.setWordWrap(True)

        self._push_button = QtGui.QPushButton("&Push")
        self._push_button.setEnabled(False)
        self.connect(self._push_button,
                     QtCore.SIGNAL("clicked()"),
                     self.push_vistrail_to_repository)
        button_box = QtGui.QDialogButtonBox()
        button_box.addButton(self._push_button,
                             QtGui.QDialogButtonBox.ActionRole)
        right_layout.addWidget(button_box)

    def update_push_information(self):
        """ display push information text in this widget """
        self._vistrail_status_label.setText(self._repository_status['support_status'])
        self._details_label.setText(self._repository_status['details'])


    ##########################################################################
    # Signal handling

    def check_dependencies(self):
        """
        determines if current VisTrail will be
        supported by the repository's VisTrail server
        """

        # are we logged in?
        if not self.dialog.cookiejar:
            self._repository_status['support_status'] = "Please login"
            self._repository_status['details'] = ""
            self.update_push_information()
            self._push_button.setEnabled(False)
        else:
            self.repository_supports_vt = True
            # get packages supported by VisTrails repository
            packages_url = "%spackages/supported_packages/" % \
                    self.config.webRepositoryURL
            get_supported_packages = urllib2.urlopen(url=packages_url)
            server_packages = get_supported_packages.read().split('||')

            vistrail = api.get_current_vistrail()

            # get local packages and local data modules
            local_packages = []

            # XXX 100% accuracy for server support is not insured

            self.local_data_modules = ['File', 'FileSink', 'Path']
            self.unavailable_data = []
            for version_id in vistrail.tagMap.iterkeys():
                pipeline = vistrail.getPipeline(version_id)
                for module in pipeline.module_list:
                    # count modules that use data unavailable to web repository
                    on_repo = False
                    if module.name[-6:] == 'Reader' or \
                       module.name in self.local_data_modules:
                        for edge in pipeline.graph.edges_to(module.id):
                            if pipeline.modules[edge[0]].name in ['HTTPFile',
                                                                  'RepoSync']:
                                on_repo = True
                        if not on_repo and \
                           module.name not in self.unavailable_data:
                            self.unavailable_data.append(module.name)
                    # get all packages used in tagged versions of this VisTrail
                    if module.package not in local_packages:
                        local_packages.append(module.package)

            # display unsupported packages
            self.unsupported_packages = filter(lambda p: p not in server_packages, local_packages)
            self._repository_status['details'] = "Details:\n"
            if self.unsupported_packages:
                self.repository_supports_vt = False
                self._repository_status['details'] += \
                        "Packages uncompatible with web repository: %s\n" % \
                        (', '.join(self.unsupported_packages)[:-2])

            # display unsupported data modules
            if len(self.unavailable_data):
                self.repository_supports_vt = False
                self._repository_status['details'] += \
                        "Data sources not available on web repository: %s"%\
                        (', '.join(self.unavailable_data)[:-2])

            if self.repository_supports_vt:
                self._repository_status['support_status'] = \
                        ("All of this VisTrail's tagged versions are supported"
                         " on the VisTrails Repository.")
            else:
                self._repository_status['support_status'] = \
                        ("This VisTrail contains packages or modules that are"
                         " not supported by the VisTrails Repository.\n"
                         "You may still upload the VisTrail but it will "
                         "not be run by the Repository.")

            self._push_button.setEnabled(True)

            self.update_push_information()

    def push_vistrail_to_repository(self):
        """ uploads current VisTrail to web repository """

        self._repository_status['details'] = "Pushing to repository..."
        self.update_push_information()
        try:
            # create temp file
            self.directory = tempfile.mkdtemp(prefix='vt_tmp')
            (fd, filename) = tempfile.mkstemp(suffix='.vt', prefix='vt_tmp',
                                              dir=self.directory)
            os.close(fd)

            # vistrails magic: writing tmp vt and switching back to orginal vt 
            from core.db.locator import ZIPFileLocator
            locator = ZIPFileLocator(filename)
            controller = api.get_current_controller()
            tmp_controller = VistrailController()
            tmp_controller.set_vistrail(controller.vistrail.do_copy(), locator)
            tmp_controller.changed = True
            tmp_controller.write_vistrail(locator)

            # check if this vt is from the repository
            if controller.vistrail.get_annotation('repository_vt_id'):
                repository_vt_id = controller.vistrail.get_annotation('repository_vt_id').value
            else:
                repository_vt_id = -1

            # upload vistrail temp file to repository
            register_openers(cookiejar=self.dialog.cookiejar)

            params = {'vistrail_file': open(filename, 'rb'),
                      'action': 'upload',
                      'name': controller.locator.short_name,
                      'repository_vt_id': repository_vt_id,
                      'is_runnable': not bool(len(self.unsupported_packages)+ \
                                              len(self.local_data_modules)),
                      'vt_id': 0}

            upload_url = "%svistrails/remote_upload/" % \
                    self.config.webRepositoryURL

            datagen, headers = multipart_encode(params)
            request = urllib2.Request(upload_url, datagen, headers)
            result = urllib2.urlopen(request)

            os.unlink(filename)
            if result.code != 200:
                self._repository_status['details'] = "An error occurred"
            else:
                self._repository_status['details'] = \
                        "Push to repository was successful"
        except:
            self._repository_status['details'] = "An error occurred"
        self.update_push_information()

class QRepositoryLoginWidget(QtGui.QWidget):
    """ Tab that shows repository authentication """

    def __init__(self, parent, status_bar, dialog):
        QtGui.QWidget.__init__(self, parent)
        self._status_bar = status_bar
        self.dialog = dialog

        base_layout = QtGui.QHBoxLayout(self)

        main = QtGui.QFrame(self)

        base_layout.addWidget(main)

        ######################################################################
        # main half, Login info 
        base_layout = QtGui.QVBoxLayout(main)
        base_layout.setMargin(2)
        base_layout.setSpacing(2)

        base_layout.addWidget(QtGui.QLabel("Username:"))

        self.config = get_vistrails_persistent_configuration()
        if self.config.check('webRepositoryLogin'):
            self.loginUser = QtGui.QLineEdit(self.config.webRepositoryLogin)
        else:
            self.loginUser = QtGui.QLineEdit("")
        self.loginUser.setFixedWidth(200)
        self.loginUser.setSizePolicy(QtGui.QSizePolicy.Fixed,
                                     QtGui.QSizePolicy.Fixed)
        base_layout.addWidget(self.loginUser)

        base_layout.addWidget(QtGui.QLabel("Password:"))
        self.loginPassword = QtGui.QLineEdit("")
        self.loginPassword.setEchoMode(2)
        self.loginPassword.setFixedWidth(200)
        self.loginPassword.setSizePolicy(QtGui.QSizePolicy.Fixed,
                                     QtGui.QSizePolicy.Fixed)
        base_layout.addWidget(self.loginPassword)

        self.saveLogin = QtGui.QCheckBox("Save user login")
        if self.config.check('webRepositoryLogin'):
            self.saveLogin.setChecked(True)
        base_layout.addWidget(self.saveLogin)

        self._login_status_label= QtGui.QLabel("")
        base_layout.addWidget(self._login_status_label)

        self._login_button = QtGui.QPushButton("&Login")

        self.connect(self._login_button,
                     QtCore.SIGNAL("clicked()"),
                     self.clicked_on_login)

        self._logout_button = QtGui.QPushButton("Log&out")
        self.connect(self._logout_button,
                     QtCore.SIGNAL("clicked()"),
                     self.clicked_on_logout)
        button_box = QtGui.QDialogButtonBox()
        button_box.addButton(self._login_button,
                             QtGui.QDialogButtonBox.ActionRole)
        button_box.addButton(self._logout_button,
                             QtGui.QDialogButtonBox.ActionRole)

        base_layout.addWidget(button_box)

        self.loginUser.setEnabled(True)
        self.loginPassword.setEnabled(True)
        self._logout_button.setEnabled(False)
        self._login_button.setEnabled(True)
        self.saveLogin.setEnabled(True)

        if self.dialog.cookiejar and \
           'sessionid' in [cookie.name for cookie in self.dialog.cookiejar]:
            self.loginUser.setEnabled(False)
            self.loginPassword.setEnabled(False)
            self._login_button.setEnabled(False)
            self.saveLogin.setEnabled(False)
            self._logout_button.setEnabled(True)

    def show_login_information(self):
        """ display/update login info text """
        self._login_status_label.setText(self._login_status)


    ##########################################################################
    # Signal handling
    def clicked_on_login(self):
        """
        Attempts to log into web repository
        stores auth cookie for session
        """
        from gui.application import VistrailsApplication

        params = urllib.urlencode({'username':self.loginUser.text(),
                                   'password':self.loginPassword.text()})
        self.dialog.cookiejar =  cookielib.CookieJar()
        self.loginOpener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.dialog.cookiejar))

        # FIXME doesn't use https
        login_url = "%saccount/login/" % self.config.webRepositoryURL
        request = urllib2.Request(login_url, params)
        url = self.loginOpener.open(request)

        # login failed
        if not 'sessionid' in [cookie.name for cookie in self.dialog.cookiejar]:
            self._login_status = "incorrect username or password"

        else: # login successful
            self._login_status = "login successful"

            self.loginUser.setEnabled(False)
            self.loginPassword.setEnabled(False)
            self._login_button.setEnabled(False)
            self.saveLogin.setEnabled(False)
            self._logout_button.setEnabled(True)

            # add association between VisTrails user and web repository user
            if self.saveLogin.checkState():
                if self.config.check('webRepositoryLogin') and \
                   self.config.webRepositoryLogin == self.loginUser.text():
                    pass
                else:
                    self.config.webRepositoryLogin = str(self.loginUser.text())
                    VistrailsApplication.save_configuration()

            # remove assiciation between VisTrails user and web repository user
            else:
                self.config.webRepositoryLogin = ""
                VistrailsApplication.save_configuration()

        self.show_login_information()

    def clicked_on_logout(self):
        """ Reset cookie, text fields and gui buttons """
        self.loginUser.setEnabled(True)
        self.loginPassword.setEnabled(True)
        self._logout_button.setEnabled(False)
        self._login_button.setEnabled(True)
        self.saveLogin.setEnabled(True)
        self.dialog.cookiejar = None

class QRepositoryDialog(QtGui.QDialog):
    """ Dialog that shows repository options """

    cookiejar = None
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self._status_bar = QtGui.QStatusBar(self)
        self.setWindowTitle('VisTrails Repository')
        layout = QtGui.QHBoxLayout(self)
        layout.setMargin(0)
        layout.setSpacing(0)
        self.setLayout(layout)

        f = QtGui.QFrame()
        layout.addWidget(f)

        l = QtGui.QVBoxLayout(f)
        f.setLayout(l)

        self._tab_widget = QtGui.QTabWidget(f)
        l.addWidget(self._tab_widget)
        self._tab_widget.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                       QtGui.QSizePolicy.Expanding)

        self._login_tab = self.create_login_tab()
        self._tab_widget.addTab(self._login_tab, 'Login to Repository')

        self._push_tab = self.create_push_tab()
        self._tab_widget.addTab(self._push_tab, 'Push VisTrail to Repository')

        self._button_box = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Close,
                                                  QtCore.Qt.Horizontal,
                                                  f)
        self.connect(self._button_box,
                     QtCore.SIGNAL('clicked(QAbstractButton *)'),
                     self.close_dialog)

        self.connect(self._tab_widget,
                     QtCore.SIGNAL('currentChanged(int)'),
                     self.tab_changed)

        l.addWidget(self._button_box)
        l.addWidget(self._status_bar)

    def close_dialog(self):
        self.done(0)

    def create_push_tab(self):
        """ create_push_tab() -> QRepositoryPushWidget """
        return QRepositoryPushWidget(self, self._status_bar, self.__class__)

    def create_login_tab(self):
        """ create_login_tab() -> QRepositoryLoginWidget """
        return QRepositoryLoginWidget(self, self._status_bar, self.__class__)

    def tab_changed(self, index):
        """ tab_changed(index: int) -> None """
        if index == 1: # push tab
            self._push_tab.check_dependencies()

    def sizeHint(self):
        return QtCore.QSize(800, 600)
