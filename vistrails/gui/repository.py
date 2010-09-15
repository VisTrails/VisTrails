############################################################################
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
"""
Dialog for web repository options
Includes login and upload tabs
"""

from PyQt4 import QtGui, QtCore
from core.configuration import get_vistrails_configuration
from core.repository.poster.encode import multipart_encode
from core.repository.poster.streaminghttp import register_openers
from core.vistrail.controller import VistrailController
from core.db.locator import ZIPFileLocator, FileLocator
from core.db.io import load_vistrail
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

        self._default_perm_label = QtGui.QLabel("Default Global Permissions:")
        top_layout.addWidget(self._default_perm_label)
        self.perm_view = QtGui.QCheckBox("view")
        self.perm_download = QtGui.QCheckBox("download")
        self.perm_edit = QtGui.QCheckBox("edit")
        top_layout.addWidget(self.perm_view)
        top_layout.addWidget(self.perm_download)
        top_layout.addWidget(self.perm_edit)
        self.perm_view.setEnabled(True)

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

    def check_dependencies(self):
        """
        determines if current VisTrail will be
        supported by the repository's VisTrail server
        """

        self._unrunnable_wfs = {}

        # are we logged in?
        if not self.dialog.cookiejar:
            self._repository_status['support_status'] = "Please login"
            self._repository_status['details'] = ""
            self.update_push_information()
            self._push_button.setEnabled(False)
            self._branch_button.hide()
        else:
            self._branch_button.hide()
            self.repository_supports_vt = True
            # get packages supported by VisTrails repository
            packages_url = "%s/packages/supported_packages/" % \
                    self.config.webRepositoryURL
            try:
                get_supported_packages = urllib2.urlopen(url=packages_url)
            except urllib2.HTTPError, e:
                self._repository_status['support_status'] = ""
                self._repository_status['details'] = ""
                if e.code == 500:
                    self._repository_status['support_status'] = \
                            ("Error connecting to repository (server side issues)")
                else:
                    print str(e)

                self._push_button.setEnabled(False)
                self.update_push_information()
                return
            server_packages = get_supported_packages.read().split('||')

            vistrail = api.get_current_vistrail()

            # get local packages and local data modules
            local_packages = []

            self.local_data_modules = ['File', 'FileSink', 'Path']
            self.unavailable_data = set()
            self.unsupported_packages = set()
            has_python_source = False

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
                            if pipeline.modules[edge[0]].name in ['HTTPFile',
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
            self.unsupported_packages = filter(lambda p: p not in \
                                               server_packages, local_packages)
            if self.unsupported_packages:
                self.repository_supports_vt = False
                self._repository_status['details'] += \
                        "Packages uncompatible with web repository: %s\n\n" % \
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
            controller = api.get_current_controller()
            if controller.vistrail.get_annotation('repository_vt_id'):
                # TODO: allow user to create own version instead of updating
                # updating vistrail, so disable permissions

                # TODO: get permissions settings for vistrail to be updated

                # Since repository_vt_id doesn't mirror crowdlabs vt id
                # get the crowdlabs vt id for linkage
                vt_url = "%s/vistrails/details/%s" % \
                        (self.config.webRepositoryURL,
                         controller.vistrail.get_annotation('repository_vt_id').value)
                try:
                    request = urllib2.urlopen(url=vt_url)
                    if request.code == 200:
                        # the vistrail exists on the repository, setup merge settings
                        self._default_perm_label.setText("Default Global Permissions "
                                                         "(only applicable to branching):")
                        self._push_button.setText("Commit changes")
                        self._branch_button.setEnabled(True)
                        self._branch_button.show()

                        vistrail_link = "%s/vistrails/details/%s" % \
                                (self.config.webRepositoryURL,
                                 controller.vistrail.get_annotation('repository_vt_id').value)

                        self._repository_status['support_status'] = \
                                ("You are attempting to update this vistrail: "
                                 "<a href='%s'>%s</a>. This will possibly update your local version with changes from the web repository<br><br>") % \
                                (vistrail_link, vistrail_link)

                except urllib2.HTTPError:
                    # the vistrail has *probably* been deleted or doesn't exist
                    # remove repository_vt_id annotation
                    repo_annotation = controller.vistrail.get_annotation('repository_vt_id')
                    if repo_annotation:
                        controller.vistrail.db_delete_annotation(repo_annotation)
                    print "the vistrail has been deleted or doesn't exist"



            if self.repository_supports_vt:
                self._repository_status['support_status'] += \
                        ("All of this VisTrail's tagged versions are supported"
                         " on the VisTrails Repository.")
            else:
                self._repository_status['support_status'] += \
                        ("This VisTrail contains packages or modules that are"
                         " not supported by the VisTrails Repository.<br>"
                         "You may still upload the VisTrail but it will "
                         "not be run by the Repository.")


            self._push_button.setEnabled(True)

            self.update_push_information()

    def push_vistrail_to_repository(self, branching=False):
        """ uploads current VisTrail to web repository """

        self._repository_status['details'] = "Pushing to repository..."
        self._push_button.setEnabled(False)
        self._branch_button.setEnabled(False)
        self.update_push_information()
        try:
            # create temp file
            self.directory = tempfile.mkdtemp(prefix='vt_tmp')
            (fd, filename) = tempfile.mkstemp(suffix='.vt', prefix='vt_tmp',
                                              dir=self.directory)
            os.close(fd)

            # writing tmp vt and switching back to orginal vt
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
                      'repository_vt_id': repository_vt_id if not branching else -1,
                      'is_runnable': not bool(len(self.unsupported_packages)+ \
                                              len(self.local_data_modules)),
                      'vt_id': 0,
                      'branched_from': "" if not branching else repository_vt_id,
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

            print "before check"
            if updated_response[:6] == "upload":
                # No update, just upload
                if result.code != 200:
                    self._repository_status['details'] = \
                            "Push to repository failed"
                else:
                    repository_vt_id = int(updated_response[8:])
                    controller.vistrail.set_annotation('repository_vt_id',
                                                       repository_vt_id)
                    controller.vistrail.set_annotation('repository_creator',
                                                       self.dialog.loginUser.text())
                    # ensure that the annotations get saved
                    controller.set_changed(True)
                    self._repository_status['details'] = \
                            "Push to repository was successful"
            else:
                # update, load updated vistrail
                if result.code != 200:
                    self._repository_status['details'] = "Update Failed"
                else:
                    print "getting version from web"
                    # request file to download
                    download_url = "%s/vistrails/download/%s/" % \
                            (self.config.webRepositoryURL, updated_response)

                    request = urllib2.Request(download_url)
                    result = urllib2.urlopen(request)
                    updated_file = result.read()

                    # create temp file of updated vistrail
                    self.directory = tempfile.mkdtemp(prefix='vt_tmp')
                    (fd, updated_filename) = tempfile.mkstemp(suffix='.vtl',
                                                              prefix='vtl_tmp',
                                                              dir=self.directory)
                    os.close(fd)
                    updated_vt = open(updated_filename, 'w')
                    updated_vt.write(updated_file)
                    updated_vt.close()

                    # switch vistrails to updated one
                    controller = api.get_current_controller()

                    updated_locator = FileLocator(updated_filename)

                    (up_vistrail, abstractions, thumbnails) = \
                            load_vistrail(updated_locator)

                    controller.set_vistrail(up_vistrail,
                                            controller.vistrail.locator,
                                            abstractions, thumbnails)

                    # update version tree drawing
                    controller.recompute_terse_graph()
                    controller.invalidate_version_tree()

                    os.remove(updated_filename)
                    os.remove(updated_filename[:-1])
                    os.rmdir(self.directory)

                    self._repository_status['details'] = \
                            "Update to repository was successful"

        except Exception, e:
            print e
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

        self.config = get_vistrails_configuration()
        # TODO: this '/' check should probably be done in core/configuration.py
        if self.config.webRepositoryURL[-1] == '/':
            self.config.webRepositoryURL = self.config.webRepositoryURL[:-1]

        ######################################################################
        # main half, Login info
        base_layout = QtGui.QVBoxLayout(main)

        base_layout.addWidget(
            QtGui.QLabel("Repository location: %s" % \
                         self.config.webRepositoryURL))

        base_layout.addWidget(QtGui.QLabel("Username:"))

        if self.config.check('webRepositoryLogin'):
            self.dialog.loginUser = QtGui.QLineEdit(self.config.webRepositoryLogin)
        else:
            self.dialog.loginUser = QtGui.QLineEdit("")

        self.dialog.loginUser.setFixedWidth(200)
        self.dialog.loginUser.setSizePolicy(QtGui.QSizePolicy.Fixed,
                                     QtGui.QSizePolicy.Fixed)
        base_layout.addWidget(self.dialog.loginUser)

        base_layout.addWidget(QtGui.QLabel("Password:"))
        self.loginPassword = QtGui.QLineEdit("")
        self.loginPassword.setEchoMode(2)
        self.loginPassword.setFixedWidth(200)
        self.loginPassword.setSizePolicy(QtGui.QSizePolicy.Fixed,
                                     QtGui.QSizePolicy.Fixed)
        base_layout.addWidget(self.loginPassword)

        self.saveLogin = QtGui.QCheckBox("Save username")
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

        self.dialog.loginUser.setEnabled(True)
        self.loginPassword.setEnabled(True)
        self._logout_button.setEnabled(False)
        self._login_button.setEnabled(True)
        self.saveLogin.setEnabled(True)

        if self.dialog.cookiejar and \
           'sessionid' in [cookie.name for cookie in self.dialog.cookiejar]:
            self.dialog.loginUser.setEnabled(False)
            self.loginPassword.setEnabled(False)
            self._login_button.setEnabled(False)
            self.saveLogin.setEnabled(False)
            self._logout_button.setEnabled(True)
        else:
            self.clicked_on_logout()

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

        params = urllib.urlencode({'username':self.dialog.loginUser.text(),
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
            self._login_status = "incorrect username or password"

        else: # login successful
            self._login_status = "login successful"

            self.dialog.loginUser.setEnabled(False)
            self.loginPassword.setEnabled(False)
            self._login_button.setEnabled(False)
            self.saveLogin.setEnabled(False)
            self._logout_button.setEnabled(True)

            # add association between VisTrails user and web repository user
            if self.saveLogin.checkState():
                if self.config.check('webRepositoryLogin') and \
                   self.config.webRepositoryLogin == self.dialog.loginUser.text():
                    pass
                else:
                    self.config.webRepositoryLogin = str(self.dialog.loginUser.text())
                    VistrailsApplication.save_configuration()

            # remove assiciation between VisTrails user and web repository user
            else:
                self.config.webRepositoryLogin = ""
                VistrailsApplication.save_configuration()

        self.show_login_information()

    def clicked_on_logout(self):
        """ Reset cookie, text fields and gui buttons """
        self.dialog.loginUser.setEnabled(True)
        self.loginPassword.setEnabled(True)
        self._logout_button.setEnabled(False)
        self._login_button.setEnabled(True)
        self.saveLogin.setEnabled(True)
        self.dialog.cookiejar = None

class QRepositoryDialog(QtGui.QDialog):
    """ Dialog that shows repository options """

    cookiejar = None
    cookie_url = None
    loginUser = None
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self._status_bar = QtGui.QStatusBar(self)
        self.setWindowTitle('Web Repository Options')
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

        self._push_tab = self.create_push_tab()
        self._login_tab = self.create_login_tab()

        self._tab_widget.addTab(self._login_tab, 'Login to Repository')
        self._tab_widget.addTab(self._push_tab, 'Push VisTrails to Repository')

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
            self._push_tab.populate_table()

    def sizeHint(self):
        return QtCore.QSize(800, 600)
