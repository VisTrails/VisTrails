from PyQt4 import QtCore, QtGui

from vistrails.core.parallelization.parallel_ipython import EngineManager


class ProfileItem(QtGui.QListWidgetItem):
    def __init__(self, profile, text, italic=False):
        QtGui.QListWidgetItem.__init__(self, text)
        if italic:
            font = self.font()
            font.setItalic(True)
            self.setFont(font)
        self.profile = profile


def choose_profile():
    profiles = EngineManager.list_profiles()

    dialog = QtGui.QDialog()
    dialog.setWindowTitle("IPython profile selection")

    layout = QtGui.QVBoxLayout()
    profile_list = QtGui.QListWidget()
    profile_list.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
    for profile, connected in profiles:
        profile_list.addItem(ProfileItem(profile, profile))

    buttons = QtGui.QHBoxLayout()
    ok = QtGui.QPushButton("Select")
    QtCore.QObject.connect(ok, QtCore.SIGNAL('clicked()'),
                           dialog, QtCore.SLOT('accept()'))
    buttons.addWidget(ok)
    cancel = QtGui.QPushButton("Cancel")
    QtCore.QObject.connect(cancel, QtCore.SIGNAL('clicked()'),
                           dialog, QtCore.SLOT('reject()'))
    buttons.addWidget(cancel)

    def check_selection():
        selection = profile_list.selectedItems()
        ok.setEnabled(len(selection) == 1)
    QtCore.QObject.connect(
            profile_list, QtCore.SIGNAL('itemSelectionChanged()'),
            check_selection)
    check_selection()

    layout.addWidget(profile_list)
    layout.addLayout(buttons)
    dialog.setLayout(layout)

    if dialog.exec_() == QtGui.QDialog.Accepted:
        return profile_list.selectedItems()[0].profile
    else:
        return None


class QBaseIPythonWidget(QtGui.QWidget):
    def __init__(self, parent, target):
        QtGui.QWidget.__init__(self)

        self._parent = parent
        self._target = target

        layout = QtGui.QVBoxLayout()
        layout.addWidget(QtGui.QLabel(self.description))
        if self.standalone:
            warning_html = (
                    '<span style="color: blue;">'
                    "(Doesn't use VisTrails on engines)"
                    '</span>')
        else:
            warning_html = (
                    '<span style="color: red;">'
                    "Requires VisTrails on IPython engines"
                    '</span>')
        layout.addWidget(QtGui.QLabel(warning_html))

        params = QtGui.QGridLayout()

        ann = target.get_annotation('ipython-profile')
        if ann is not None and ann.value:
            self.profile = ann.value
        else:
            self.profile = None

        if self.profile is None:
            prof_txt = "Select profile"
            self.mngr = None
        else:
            prof_txt = "Profile: %s" % self.profile
            self.mngr = EngineManager(self.profile)
        self._profile_button = QtGui.QPushButton(prof_txt)
        self.connect(self._profile_button, QtCore.SIGNAL('clicked()'),
                     self.change_profile)
        params.addWidget(self._profile_button, 0, 0, 1, 2)

        info_button = QtGui.QPushButton("Show engines")
        self.connect(info_button, QtCore.SIGNAL('clicked()'),
                     self.info)
        params.addWidget(info_button, 1, 0)

        start_engines_button = QtGui.QPushButton("+")
        self.connect(start_engines_button, QtCore.SIGNAL('clicked()'),
                     self.start_engines)
        params.addWidget(start_engines_button, 1, 1, QtCore.Qt.AlignLeft)

        shutdown_cluster_button = QtGui.QPushButton("Shutdown cluster")
        self.connect(shutdown_cluster_button, QtCore.SIGNAL('clicked()'),
                     self.shutdown_cluster)
        params.addWidget(shutdown_cluster_button, 2, 0)

        cleanup_button = QtGui.QPushButton("Stop local processes")
        self.connect(cleanup_button, QtCore.SIGNAL('clicked()'),
                     self.cleanup)
        params.addWidget(cleanup_button, 2, 1)

        layout.addLayout(params)

        self.setLayout(layout)

    def remove(self):
        # TODO : Perhaps close Client if not used anymore?
        pass

    def _check_manager(self):
        if self.mngr is None:
            QtGui.QMessageBox.warning(
                    self,
                    u"No profile set",
                    u"Please choose an IPython profile")
            return False
        else:
            return True

    def change_profile(self):
        profile = choose_profile()
        if profile is not None and profile != self.profile:
            self.mngr = EngineManager(profile)
            self.profile = profile
            self._profile_button.setText("Profile: %s" % profile)

            self._target.set_annotation(
                    self._parent.vistrail.idScope,
                    'ipython-profile',
                    profile)
            self._parent.set_changed()

            if self.mngr.ensure_client(connect_only=True) is None:
                pass # TODO : Hmm, what to do here

    def info(self):
        if not self._check_manager():
            return

        info = self.mngr.info()

        dialog = QtGui.QDialog()
        layout = QtGui.QVBoxLayout()
        form = QtGui.QFormLayout()
        form.addRow(
                "Profile:",
                QtGui.QLabel(self.profile))
        form.addRow(
                "Connected:",
                QtGui.QLabel("yes" if info['connected'] else "no"))
        form.addRow(
                "Controller started from VisTrails:",
                QtGui.QLabel("running"
                             if info['started_controller']
                             else "no"))
        form.addRow(
                "Engines started from VisTrails:",
                QtGui.QLabel(str(info['started_engines'])))
        form.addRow(
                "Total engines in cluster:",
                QtGui.QLabel(str(info['started_engines'])
                             if info['started_engines'] is not None
                             else "(unknown)"))
        layout.addLayout(form)
        if info['engines']:
            tree = QtGui.QTreeWidget()
            tree.setHeaderHidden(False)
            tree.setHeaderLabels(["IPython id", "PID", "System type"])
            engine_tree = dict()
            for ip_id, (pid, system, fqdn) in info['engines']:
                engine_tree.setdefault(fqdn, []).append(
                        (ip_id, pid, system))
            for fqdn, info in engine_tree.iteritems():
                node = QtGui.QTreeWidgetItem([fqdn])
                tree.addTopLevelItem(node)
                for ip_id, pid, system in info:
                    node.addChild(QtGui.QTreeWidgetItem([
                            str(ip_id),
                            str(pid),
                            system]))
            for i in xrange(tree.columnCount()):
                tree.resizeColumnToContents(i)
            tree.expandAll()
            layout.addWidget(tree)

        ok = QtGui.QPushButton("Ok")
        QtCore.QObject.connect(ok, QtCore.SIGNAL('clicked()'),
                               dialog, QtCore.SLOT('accept()'))
        layout.addWidget(ok, 1, QtCore.Qt.AlignHCenter)
        dialog.setLayout(layout)
        dialog.exec_()

    def start_engines(self):
        if not self._check_manager():
            return

        self.mngr.start_engines()

    def shutdown_cluster(self):
        if not self._check_manager():
            return

        self.mngr.shutdown_cluster()

    def cleanup(self):
        if self.mngr is not None:
            self.mngr.cleanup()


class QParallelIPythonSettings(QBaseIPythonWidget):
    description = "VisTrails on IPython"
    standalone = False

    @staticmethod
    def describe(target):
        if target.scheme != 'ipython':
            raise ValueError

        profile = target.get_annotation('ipython-profile')
        if profile is not None:
            profile = profile.value
        if not profile:
            profile = "(unset)"
        return "VisTrails on IPython profile %s" % profile


class QParallelIPythonStandaloneSettings(QBaseIPythonWidget):
    description = "Standalone code on IPython"
    standalone = True

    @staticmethod
    def describe(target):
        if target.scheme != 'ipython-standalone':
            raise ValueError

        profile = target.get_annotation('ipython-profile')
        if profile is not None:
            profile = profile.value
        if not profile:
            profile = "(unset)"
        return "Standalone code on IPython profile %s" % profile
