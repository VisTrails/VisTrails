###############################################################################
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
"""
Dialog for web repository options
Includes login and upload tabs
"""
from PyQt4 import QtGui, QtCore
from vistrails.core.configuration import get_vistrails_configuration, get_vistrails_persistent_configuration
from vistrails.core.repository.poster.encode import multipart_encode
from vistrails.core.repository.poster.streaminghttp import register_openers
from vistrails.core.vistrail.controller import VistrailController
from vistrails.core.db.locator import ZIPFileLocator, FileLocator
from vistrails.core.db.io import load_vistrail
from vistrails.core import debug
import urllib, urllib2, cookielib
import os
import tempfile
import vistrails.api
import json

##############################################################################

class QRepositoryPushWidget(QtGui.QWidget):
    """ Tab that shows main repository options
        Allows users to login and push VisTrails to the Repository """

    def __init__(self, parent, status_bar, dialog):
        QtGui.QWidget.__init__(self, parent)
        self._status_bar = status_bar
        self.dialog = dialog

        base_layout = QtGui.QVBoxLayout(self)

        top = QtGui.QFrame(self)
        bottom = QtGui.QFrame(self)

        base_layout.addWidget(top)
        base_layout.addWidget(bottom, 1)

        # TODO: this '/' check should probably be done in core/configuration.py
        self.config = get_vistrails_configuration()
        if self.config.webRepositoryURL[-1] == '/':
            self.config.webRepositoryURL = self.config.webRepositoryURL[:-1]

        # check if the web repository url has changed while logged in
        if self.dialog.cookie_url and \
           self.dialog.cookie_url != self.config.webRepositoryURL:
            self.dialog.cookiejar = None



        ######################################################################
        # Detail Table
        bottom_layout = QtGui.QVBoxLayout(bottom)
        bottom_layout.setMargin(2)
        bottom_layout.setSpacing(2)

        # Show what workflows are unrunnble on the repository
        # and for what reasons
        self._unrunnable_table = QtGui.QTableWidget(0, 2, top)
        self._unrunnable_table.horizontalHeader().setStretchLastSection(True)

        bottom_layout.addWidget(self._unrunnable_table)

        self._repository_status = {}

        ######################################################################
        # Push info
        top_layout = QtGui.QVBoxLayout(top)

        self._vistrail_status_label = QtGui.QLabel("")
        self._vistrail_status_label.setWordWrap(True)
        top_layout.addWidget(self._vistrail_status_label)

        self.serverCombo = QtGui.QComboBox()
        self.connect(self.serverCombo,
                     QtCore.SIGNAL("currentIndexChanged(int)"),
                     self.check_dependencies)
        top_layout.addWidget(self.serverCombo)

        """
        self._default_perm_label = QtGui.QLabel("Default Global Permissions:")
        top_layout.addWidget(self._default_perm_label)
        self.perm_view = QtGui.QCheckBox("view")
        self.perm_download = QtGui.QCheckBox("download")
        self.perm_edit = QtGui.QCheckBox("edit")
        top_layout.addWidget(self.perm_view)
        top_layout.addWidget(self.perm_download)
        top_layout.addWidget(self.perm_edit)
        self.perm_view.setEnabled(True)
        """

        self.permission_gb = QtGui.QGroupBox(self)
        self.permission_gb.setTitle("Default Global Permissions")
        glayout = QtGui.QHBoxLayout()
        self.perm_view = QtGui.QCheckBox("view")
        self.perm_download = QtGui.QCheckBox("download")
        self.perm_edit = QtGui.QCheckBox("edit")
        glayout.addWidget(self.perm_view)
        glayout.addWidget(self.perm_download)
        glayout.addWidget(self.perm_edit)
        self.perm_view.setChecked(True)
        self.perm_download.setChecked(True)
        self.permission_gb.setLayout(glayout)
        top_layout.addWidget(self.permission_gb)

        self._details_label = QtGui.QLabel("")
        self._details_label.setWordWrap(True)
        top_layout.addWidget(self._details_label)

        for lbl in [self._details_label, self._vistrail_status_label]:
            lbl.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
            lbl.setWordWrap(True)

        self._push_button = QtGui.QPushButton("&Push")
        self._push_button.setEnabled(False)
        self.connect(self._push_button,
                     QtCore.SIGNAL("clicked()"),
                     self.push_vistrail_to_repository)
        self._branch_button = QtGui.QPushButton("&Branch")
        self._branch_button.hide()
        self.connect(self._branch_button,
                     QtCore.SIGNAL("clicked()"),
                     (lambda branching=True : self.push_vistrail_to_repository(branching)))
        button_box = QtGui.QDialogButtonBox()
        button_box.addButton(self._push_button,
                             QtGui.QDialogButtonBox.ActionRole)
        button_box.addButton(self._branch_button,
                             QtGui.QDialogButtonBox.ActionRole)
        bottom_layout.addWidget(button_box)

    def populate_table(self):
        self._unrunnable_table.clear()

        # set horizontal headers
        wf_title = QtGui.QTableWidgetItem('Workflow')
        wf_title.setTextAlignment(QtCore.Qt.AlignCenter)
        self._unrunnable_table.setHorizontalHeaderItem(0, wf_title)

        detail_title = QtGui.QTableWidgetItem('Unsupported Modules/Packages')
        detail_title.setTextAlignment(QtCore.Qt.AlignCenter)
        self._unrunnable_table.setHorizontalHeaderItem(1, detail_title)

        # populate table
        count = 0
        for wf in self._unrunnable_wfs.keys():
            details = \
                    QtGui.QTableWidgetItem(', '.join(self._unrunnable_wfs[wf]))
            details.setTextAlignment(QtCore.Qt.AlignCenter)

            wf_item = QtGui.QTableWidgetItem(str(wf))
            wf_item.setTextAlignment(QtCore.Qt.AlignCenter)

            if count >= self._unrunnable_table.rowCount():
                self._unrunnable_table.insertRow(count)
            self._unrunnable_table.setItem(count, 0, wf_item)
            self._unrunnable_table.setItem(count, 1, details)
            count += 1

        # delete vertical headers
        for i in range(self._unrunnable_table.rowCount()):
            self._unrunnable_table.setVerticalHeaderItem(i, QtGui.QTableWidgetItem())

    def update_push_information(self):
        """ display push information text in this widget """
        self._vistrail_status_label.setText(self._repository_status['support_status'])
        self._details_label.setText(self._repository_status['details'])


    ##########################################################################
    # Signal handling

    def check_user_projects(self):
        # are we logged in?
        if not self.dialog.cookiejar:
            self._repository_status['support_status'] = "Please login"
            self._repository_status['details'] = ""
            self.update_push_information()
            self._push_button.setEnabled(False)
            self._branch_button.setEnabled(False)
            self._branch_button.hide()
        else:
            self._branch_button.setEnabled(False)
            self._branch_button.hide()
            server_url = "%s/projects/get_user_projects/" % \
                    self.config.webRepositoryURL
            register_openers(cookiejar=self.dialog.cookiejar)
            try:
                request = urllib2.Request(server_url)
                get_servers = urllib2.urlopen(request)
            except urllib2.HTTPError, e:
                self._repository_status['support_status'] = ""
                self._repository_status['details'] = ""
                if e.code == 500:
                    self._repository_status['support_status'] = \
                            ("Error checking user projects (server side issues)")
                    debug.critical("Error checking user projects (server side issues)")
                else:
                    debug.critical("Exception checking user projects", e)

                self._push_button.setEnabled(False)
                self.update_push_information()
                return

            servers = json.loads(get_servers.read())
            if not self.serverCombo.count():
                self.serverCombo.addItem("Please Select a Project", 0)
                for prj, srvr in servers:
                    self.serverCombo.addItem("%s (%s)" % (prj, srvr), [prj, srvr])



    def check_dependencies(self, index):
        """
        determines if current VisTrail will be
        supported by the repository's VisTrail server
        """

        if not index: return

        self._unrunnable_wfs = {}

        # are we logged in?
        if not self.dialog.cookiejar:
            self._repository_status['support_status'] = "Please login"
            self._repository_status['details'] = ""
            self.update_push_information()
            self._push_button.setEnabled(False)
            self._branch_button.hide()
        else:
            self.repository_supports_vt = True
            # get packages supported by VisTrails repository
            server = self.serverCombo.itemData(index)[1]
            packages_url = "%s/packages/supported_packages/%s" % \
                    (self.config.webRepositoryURL, server)


            try:
                get_supported_packages = urllib2.urlopen(url=packages_url)
            except urllib2.HTTPError, e:
                self._repository_status['support_status'] = ""
                self._repository_status['details'] = ""
                if e.code == 500:
                    self._repository_status['support_status'] = \
                            ("Error when checking dependencies (server side issues)")
                    debug.critical("Error when checking dependencies (server side issues)")
                else:
                    debug.critical("Exception checking dependencies", e)

                self._push_button.setEnabled(False)
                self.update_push_information()
                self.populate_table()
                return
            server_packages = json.loads(get_supported_packages.read())

            # get local packages and local data modules
            local_packages = []

            self.local_data_modules = ['File', 'FileSink', 'Path']
            self.unavailable_data = set()
            self.unsupported_packages = set()
            has_python_source = False

            vistrail = vistrails.api.get_current_vistrail()

            for version_id in vistrail.get_tagMap():
                pipeline = vistrail.getPipeline(version_id)
                tag = vistrail.get_tagMap()[version_id]
                workflow_packages = []
                for module in pipeline.module_list:
                    # count modules that use data unavailable to web repository
                    on_repo = False
                    if module.name[-6:] == 'Reader' or \
                       module.name in self.local_data_modules:
                        for edge in pipeline.graph.edges_to(module.id):
                            if pipeline.modules[edge[0]].name in ['DownloadFile',
                                                                  'RepoSync']:
                                on_repo = True

                        if not on_repo:
                            if tag not in self._unrunnable_wfs.keys():
                                self._unrunnable_wfs[tag] = []
                            self._unrunnable_wfs[tag].append(module.name)
                            self.unavailable_data.add(module.name)

                    if module.name == "PythonSource":
                        if tag not in self._unrunnable_wfs.keys():
                            self._unrunnable_wfs[tag] = []
                        self._unrunnable_wfs[tag].append(module.name)
                        has_python_source = True

                    # get all packages used in tagged versions of this workflow
                    if module.package not in workflow_packages:
                        workflow_packages.append(module.package)

                # find unsupported packages
                wf_unsupported_packages = filter((lambda p: p not in \
                                                  server_packages),
                                                 workflow_packages)
                if wf_unsupported_packages:
                    if tag not in self._unrunnable_wfs.keys():
                        self._unrunnable_wfs[tag] = []
                    for package in wf_unsupported_packages:
                        self._unrunnable_wfs[tag].append(package)
                        self.unsupported_packages.add(package)

            # display unsupported packages
            self._repository_status['details'] = "Details:\n"
            if self.unsupported_packages:
                self.repository_supports_vt = False
                self._repository_status['details'] += \
                        "Packages incompatible with web repository: %s\n\n" % \
                        (', '.join(self.unsupported_packages)[:-2])

            # display unsupported data modules
            if len(self.unavailable_data):
                self.repository_supports_vt = False
                self._repository_status['details'] += \
                        "Data sources not available on web repository: %s\n"%\
                        (', '.join(self.unavailable_data)[:-2])

            if has_python_source:
                self.repository_supports_vt = False
                self._repository_status['details'] += \
                        ("This Vistrail contains PythonSource module(s) and "
                         "will have to be verified by admins before it can be "
                         "run on the web repository. You will be notified when"
                         " your workflows have been verfied")

            self._repository_status['support_status'] = ""
            controller = vistrails.api.get_current_controller()
            if controller.vistrail.get_annotation('repository_vt_id'):
                # Since repository_vt_id doesn't mirror crowdlabs vt id
                # get the crowdlabs vt id for linkage
                vt_url = "%s/vistrails/details/%s" % \
                        (self.config.webRepositoryURL,
                         controller.vistrail.get_annotation('repository_vt_id').value)
                try:
                    request = urllib2.urlopen(url=vt_url)
                    # TODO: check project that vistrail is part of and notify user
                    # that branching will add it to a different project
                    if request.code == 200:
                        # the vistrail exists on the repository, setup merge settings
                        self.permission_gb.setTitle(("Default Global Permissions "
                                                     "(only applicable to branching):"))
                        self._push_button.setText("Commit changes")
                        self._branch_button.setEnabled(True)
                        self._branch_button.show()

                        vistrail_link = "%s/vistrails/details/%s" % \
                                (self.config.webRepositoryURL,
                                 controller.vistrail.get_annotation('repository_vt_id').value)

                        self._repository_status['support_status'] = \
                                ("You are attempting to update this Vistrail: "
                                 "<a href='%s'>%s</a>. This will possibly update your local version with changes from the web repository<br><br>") % \
                                (vistrail_link, vistrail_link)

                except urllib2.HTTPError:
                    # the vistrail has *probably* been deleted or doesn't exist
                    # remove repository_vt_id annotation
                    repo_annotation = controller.vistrail.get_annotation('repository_vt_id')
                    if repo_annotation:
                        controller.vistrail.db_delete_annotation(repo_annotation)

            if self.repository_supports_vt:
                self._repository_status['support_status'] += \
                        ("All of this Vistrail's tagged versions are supported"
                         " by the Repository.")
            else:
                self._repository_status['support_status'] += \
                        ("This Vistrail contains packages or modules that are"
                         " not supported by the Repository.<br>"
                         "You may still upload the VisTrail but it will "
                         "not be run by the Repository.")


            self._push_button.setEnabled(True)

            self.update_push_information()
            self.populate_table()

    def push_vistrail_to_repository(self, branching=False):
        """ uploads current VisTrail to web repository """

        self._repository_status['details'] = "Pushing to repository..."
        self._push_button.setEnabled(False)
        self._branch_button.setEnabled(False)
        self.update_push_information()
        try:
            # create temp file
            (fd, filename) = tempfile.mkstemp(suffix='.vt', prefix='vt_tmp')
            os.close(fd)

            # writing tmp vt and switching back to original vt
            locator = ZIPFileLocator(filename)
            controller = vistrails.api.get_current_controller()
            controller.write_vistrail(locator, export=True)

            # check if this vt is from the repository
            if controller.vistrail.get_annotation('repository_vt_id'):
                repository_vt_id = controller.vistrail.get_annotation('repository_vt_id').value
            else:
                repository_vt_id = -1

            # upload vistrail temp file to repository
            register_openers(cookiejar=self.dialog.cookiejar)
            project = self.serverCombo.itemData(self.serverCombo.currentIndex())[0]
            if project == "Default": project = ""

            params = {'vistrail_file': open(filename, 'rb'),
                      'action': 'upload',
                      'name': controller.locator.short_name,
                      'repository_vt_id': repository_vt_id if not branching else -1,
                      'is_runnable': not bool(len(self.unsupported_packages)+ \
                                              len(self.local_data_modules)),
                      'vt_id': 0,
                      'branched_from': "" if not branching else repository_vt_id,
                      'project': project,
                      'everyone_can_view': self.perm_view.checkState(),
                      'everyone_can_edit': self.perm_edit.checkState(),
                      'everyone_can_download': self.perm_download.checkState()
                     }

            upload_url = "%s/vistrails/remote_upload/" % \
                    self.config.webRepositoryURL

            datagen, headers = multipart_encode(params)
            request = urllib2.Request(upload_url, datagen, headers)
            result = urllib2.urlopen(request)
            updated_response = result.read()

            os.unlink(filename)

            if updated_response[:6] == "upload":
                # No update, just upload
                if result.code != 200:
                    self._repository_status['details'] = \
                            "Push to repository failed"
                    debug.critical("Push to repository failed (Please contact an administrator)")
                else:
                    repository_vt_id = int(updated_response[8:])
                    controller.vistrail.set_annotation('repository_vt_id',
                                                       repository_vt_id)
                    controller.vistrail.set_annotation('repository_creator',
                                                       self.dialog.loginUser)
                    # ensure that the annotations get saved
                    controller.set_changed(True)
                    self._repository_status['details'] = \
                            "Push to repository was successful"
            else:
                # update, load updated vistrail
                if result.code != 200:
                    self._repository_status['details'] = "Update Failed"
                    debug.critical("Update vistrail in web repository failed (Please contact an administrator)")
                else:
                    debug.log("getting version from web")
                    # request file to download
                    download_url = "%s/vistrails/download/%s/" % \
                            (self.config.webRepositoryURL, updated_response)

                    request = urllib2.Request(download_url)
                    result = urllib2.urlopen(request)
                    updated_file = result.read()

                    # create temp file of updated vistrail
                    (fd, updated_filename) = tempfile.mkstemp(suffix='.vtl',
                                                              prefix='vtl_tmp')
                    os.close(fd)
                    updated_vt = open(updated_filename, 'w')
                    updated_vt.write(updated_file)
                    updated_vt.close()

                    # switch vistrails to updated one
                    controller = vistrails.api.get_current_controller()

                    updated_locator = FileLocator(updated_filename)

                    (up_vistrail, abstractions, thumbnails, mashups) = \
                            load_vistrail(updated_locator)

                    # FIXME need to figure out what to do with this !!!
                    current_version = controller.current_version
                    controller.set_vistrail(up_vistrail,
                                            controller.vistrail.locator,
                                            abstractions, thumbnails, mashups)
                    controller.change_selected_version(current_version)
                    # update version tree drawing
                    controller.recompute_terse_graph()
                    controller.invalidate_version_tree()

                    os.remove(updated_filename)
                    os.remove(updated_filename[:-1])

                    self._repository_status['details'] = \
                            "Update to repository was successful"

        except Exception, e:
            debug.critical("An error occurred", e)
            self._repository_status['details'] = "An error occurred"
        self.update_push_information()

class QRepositoryLoginPopup(QtGui.QDialog):
    """ Dialog that shows repository authentication """

    def __init__(self, parent, status_bar, dialog):
        QtGui.QDialog.__init__(self, parent)
        self._status_bar = status_bar
        self.dialog = dialog
        self.dialog.cookiejar = None

        self.config = get_vistrails_configuration()
        # TODO: this '/' check should probably be done in core/configuration.py
        if self.config.webRepositoryURL[-1] == '/':
            self.config.webRepositoryURL = self.config.webRepositoryURL[:-1]

        self.setWindowTitle('Log in to Web Repository')

        grid_layout = QtGui.QGridLayout(self)
        grid_layout.setSpacing(10)

        l1 = QtGui.QLabel("Repository location: %s" % \
                          self.config.webRepositoryURL, self)
        grid_layout.addWidget(l1, 0, 0, 1, 2)

        l2 = QtGui.QLabel("Username:", self)
        grid_layout.addWidget(l2, 1, 0)

        if self.config.check('webRepositoryUser'):
            self.loginUser = QtGui.QLineEdit(self.config.webRepositoryUser, self)
        else:
            self.loginUser = QtGui.QLineEdit("", self)

        self.loginUser.setFixedWidth(200)
        self.loginUser.setSizePolicy(QtGui.QSizePolicy.Fixed,
                                     QtGui.QSizePolicy.Fixed)
        grid_layout.addWidget(self.loginUser, 1, 1)

        l3 = QtGui.QLabel("Password:", self)
        grid_layout.addWidget(l3, 2, 0)

        self.loginPassword = QtGui.QLineEdit("", self)
        self.loginPassword.setEchoMode(2)
        self.loginPassword.setFixedWidth(200)
        self.loginPassword.setSizePolicy(QtGui.QSizePolicy.Fixed,
                                     QtGui.QSizePolicy.Fixed)
        grid_layout.addWidget(self.loginPassword, 2, 1)

        self.saveLogin = QtGui.QCheckBox("Save username", self)
        if self.config.check('webRepositoryUser'):
            self.saveLogin.setChecked(True)
        grid_layout.addWidget(self.saveLogin, 3, 0)

        self._login_status_label= QtGui.QLabel("", self)
        grid_layout.addWidget(self._login_status_label, 4, 0)

        self._login_button = QtGui.QPushButton("&Login", self)
        self._cancel_button = QtGui.QPushButton("&Cancel", self)

        self.connect(self._login_button,
                     QtCore.SIGNAL("clicked()"),
                     self.clicked_on_login)

        self.connect(self._cancel_button,
                     QtCore.SIGNAL("clicked()"),
                     self.clicked_on_cancel)

        button_box = QtGui.QDialogButtonBox()
        button_box.addButton(self._login_button,
                             QtGui.QDialogButtonBox.ActionRole)
        button_box.addButton(self._cancel_button,
                             QtGui.QDialogButtonBox.ActionRole)

        grid_layout.addWidget(button_box, 5, 0)

        for lbl in [l1, l2, l3, self.loginUser, self.loginPassword, self._login_status_label]:
            lbl.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)

        grid_layout.setRowStretch(1, 1)
        grid_layout.setColumnStretch(1, 1)

        self.loginUser.setEnabled(True)
        self.loginPassword.setEnabled(True)
        self._login_button.setEnabled(True)
        self.saveLogin.setEnabled(True)


        if self.dialog.cookiejar and \
           'sessionid' in [cookie.name for cookie in self.dialog.cookiejar]:
            self.loginUser.setEnabled(False)
            self.loginPassword.setEnabled(False)
            self._login_button.setEnabled(False)
            self.saveLogin.setEnabled(False)

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
        from vistrails.gui.application import get_vistrails_application

        self.dialog.loginUser = self.loginUser.text()
        params = urllib.urlencode({'username':self.dialog.loginUser,
                                   'password':self.loginPassword.text()})
        self.dialog.cookiejar = cookielib.CookieJar()

        # set base url used for cookie
        self.dialog.cookie_url = self.config.webRepositoryURL

        self.loginOpener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.dialog.cookiejar))

        # FIXME doesn't use https
        login_url = "%s/account/login/" % self.config.webRepositoryURL
        request = urllib2.Request(login_url, params)
        url = self.loginOpener.open(request)

        # login failed
        if not 'sessionid' in [cookie.name for cookie in self.dialog.cookiejar]:
            debug.critical("Incorrect username or password")
            self.dialog.cookiejar = None
        else: # login successful

            self._login_status = "login successful"

            self.loginUser.setEnabled(False)
            self.loginPassword.setEnabled(False)
            self._login_button.setEnabled(False)
            self.saveLogin.setEnabled(False)

            # add association between VisTrails user and web repository user
            if self.saveLogin.checkState():
                if not (self.config.check('webRepositoryUser') and self.config.webRepositoryUser == self.loginUser.text()):
                    self.config.webRepositoryUser = str(self.loginUser.text())
                    pers_config = get_vistrails_persistent_configuration()
                    pers_config.webRepositoryUser = self.config.webRepositoryUser
                    get_vistrails_application().save_configuration()

            # remove association between VisTrails user and web repository user
            else:
                if self.config.check('webRepositoryUser') and self.config.webRepositoryUser:
                    self.config.webRepositoryUser = ""
                    pers_config = get_vistrails_persistent_configuration()
                    pers_config.webRepositoryUser = ""
                    get_vistrails_application().save_configuration()
            self.close_dialog(0)

    def clicked_on_cancel(self):
        self.reject()
 
    def close_dialog(self, status=0):
        self.accept()

class QRepositoryDialog(QtGui.QDialog):
    """ Dialog that shows repository options """

    cookiejar = None
    cookie_url = None
    loginUser = None
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self._status_bar = QtGui.QStatusBar(self)
        self.setWindowTitle('Push vistrail to Web Repository')

        l = QtGui.QVBoxLayout(self)
        l.setMargin(0)
        l.setSpacing(0)

        widget = QtGui.QWidget(self)
        user_layout = QtGui.QHBoxLayout(widget)
        self._user_text = QtGui.QLabel('N/A')
        user_layout.addWidget(self._user_text)
        self._logout_button = QtGui.QPushButton('Log out')
        #self._logout_button.setFixedWidth(100)
        user_layout.addWidget(self._logout_button)
        user_layout.addStretch(1)
        l.addWidget(widget)
        self._push_widget = QRepositoryPushWidget(self, self._status_bar,
                                                  self.__class__)
        l.addWidget(self._push_widget)

        self._button_box = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Close,
                                                  QtCore.Qt.Horizontal,
                                                  self)
        
        self.connect(self._button_box,
                     QtCore.SIGNAL('clicked(QAbstractButton *)'),
                     self.close_dialog)

        self.connect(self._logout_button,
                     QtCore.SIGNAL('clicked()'),
                     self.clicked_on_logout)

        l.addWidget(self._button_box)
        l.addWidget(self._status_bar)

        self.show_login_dialog()

        self._push_widget.check_user_projects()

    def clicked_on_logout(self):
        """ Reset cookie and show login dialog """
        self.cookiejar = None
        self.show_login_dialog()

    def show_login_dialog(self):
        """ Prompt for login """
        if not self.cookiejar:
            loginDialog = QRepositoryLoginPopup(self, self._status_bar, self.__class__)
            res = loginDialog.exec_()
            if res == QtGui.QDialog.Rejected:
                self.close_dialog()
                return
        self._user_text.setText('Logged in as: %s@%s' % (self.loginUser, self.cookie_url))
        self._push_widget.check_user_projects()

    def close_dialog(self):
        self.done(0)

    def tab_changed(self, index):
        """ tab_changed(index: int) -> None """
        if index == 1: # push tab
            self._push_tab.check_user_projects()

    def sizeHint(self):
        return QtCore.QSize(800, 600)
