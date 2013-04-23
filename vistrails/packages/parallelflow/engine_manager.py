import os
import subprocess
import sys
import time

from IPython.utils.path import get_ipython_dir, locate_profile
from IPython.parallel import Client
from IPython.parallel import error


try:
    from PyQt4 import QtCore, QtGui
    QtGui.QDialog
except Exception:
    qt_available = False
else:
    qt_available = True


class ProfileItem(QtGui.QListWidgetItem):
    def __init__(self, profile, text, italic=False):
        QtGui.QListWidgetItem.__init__(self, text)
        if italic:
            font = self.font()
            font.setItalic(True)
            self.setFont(font)
        self.profile = profile


def choose_profile(profiles):
    dialog = QtGui.QDialog()
    dialog.setWindowTitle("IPython profile selection")

    layout = QtGui.QVBoxLayout()
    profile_list = QtGui.QListWidget()
    profile_list.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
    for profile in profiles:
        profile_list.addItem(ProfileItem(profile, profile))

    # If no profiles are available, still provide an option to use the
    # 'default' profile
    if not profiles:
        profile_list.addItem(ProfileItem('default', "default (create)", True))

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


class EngineManager(object):
    def __init__(self):
        self.profile = None
        self.started_controller = None
        self.started_engines = set()
        self._client = None

    def _select_profile(self):
        # See IPython.core.profileapp:list_profile_in()
        profiles = []
        for filename in os.listdir(get_ipython_dir()):
            if filename.startswith('profile_'):
                profiles.append(filename[8:])

        if profiles == ['default'] and not qt_available:
            self.profile = 'default'
        elif not qt_available:
            raise ValueError("'default' IPython profile does not exist "
                             "and PyQt4 is not available")
        else:
            self.profile = choose_profile(profiles)

    def ensure_controller(self, connect_only=False):
        """Make sure a controller is available, else start a local one.
        """
        if self._client:
            return self._client

        if self.profile is None:
            self._select_profile()
        if self.profile is None:
            return None
        print "parallelflow: using IPython profile %r" % self.profile

        try:
            self._client = Client(profile=self.profile)
            print "parallelflow: connected to controller"
            return self._client
        except error.TimeoutError:
            print "parallelflow: timeout when connecting to controller"
            if connect_only:
                start_ctrl = False
            elif qt_available:
                res = QtGui.QMessageBox.question(
                        None,
                        "Start controller",
                        "Unable to connect to the configured IPython "
                        "controller. Do you want to start one?",
                        QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
                start_ctrl = res == QtGui.QMessageBox.Yes
            else:
                start_ctrl = True
        except IOError:
            print "parallelflow: didn't find a controller to connect to"
            if connect_only:
                start_ctrl = False
            elif qt_available:
                res = QtGui.QMessageBox.question(
                        None,
                        "Start controller",
                        "No controller is configured in this IPython profile. "
                        "Do you want to start one?",
                        QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
                start_ctrl = res == QtGui.QMessageBox.Yes
            else:
                start_ctrl = True

        if start_ctrl:
            ctrl_pid = os.path.join(
                    locate_profile(self.profile),
                    'pid',
                    'ipcontroller.pid')
            if os.path.exists(ctrl_pid):
                os.remove(ctrl_pid)
            print "parallelflow: starting controller"
            proc, code = self.start_process(
                    lambda: os.path.exists(ctrl_pid),
                    sys.executable,
                    '-m',
                    'IPython.parallel.apps.ipcontrollerapp',
                    '--profile=%s' % self.profile)
            if code is not None:
                if qt_available:
                    QtGui.QMessageBox.critical(
                            None,
                            "Error",
                            "Controller exited with code %d" % code)
                print ("parallelflow: controller process exited with "
                       "code %d" % code)
                return None
            else:
                self.started_controller = proc
                print "parallelflow: controller started, connecting"
                self._client = Client(profile=self.profile)
                return self._client

        return None

    @staticmethod
    def start_process(condition, *args):
        """Executes a file and waits for a condition.
        """
        print "Popen(%s)" % (', '.join(repr(a) for a in args))
        p = subprocess.Popen(args)
        while True:
            time.sleep(1)
            if condition():
                return p, None
            res = p.poll()
            if res is not None:
                return None, res

    def start_engines(self, nb=None, prompt_text="Number of engines to start"):
        """Start some engines locally
        """
        c = self.ensure_controller()
        if c is None:
            if qt_available:
                QtGui.QMessageBox.warning(
                        None,
                        "No controller",
                        "Can't start engines: couldn't connect to a "
                        "controller")
            print "parallelflow: no controller, not starting engines"
        else:
            if not nb and qt_available:
                nb, res = QtGui.QInputDialog.getInt(
                        None,
                        "Start engines",
                        prompt_text,
                        1,  # value
                        1,  # min
                        16) # max
                if not res:
                    return
            elif nb is None:
                nb = 1
            print "parallelflow: about to start %d engines" % nb
            init_engines = set(c.ids)
            if qt_available:
                bar = QtGui.QProgressDialog(
                        "Starting engines...",
                        "Stop",
                        0, nb)
                def progress(n):
                    bar.setValue(n)
                def canceled():
                    return bar.wasCanceled()
                bar.show()
            else:
                def progress(n): pass
                def canceled(): return False
            progress(0)
            for i in xrange(nb):
                proc, res = self.start_process(
                        lambda: set(c.ids) - init_engines,
                        sys.executable,
                        '-m',
                        'IPython.parallel.apps.ipengineapp',
                        '--profile=%s' % self.profile)
                if res is not None:
                    if qt_available:
                        QtGui.QMessageBox.critical(
                                None,
                                "Error",
                                "Engine exited with code %d" % res)
                    print ("parallelflow: engine %d/%d exited with code %d" % (
                           i + 1, nb, res))
                    break
                self.started_engines.add(proc)
                progress(i + 1)
                if canceled():
                    break
            if qt_available:
                bar.hide()
                bar.deleteLater()
            print "parallelflow: %d engines started" % (i + 1)

    def info(self):
        """Show some information on the cluster.
        """
        client = self.ensure_controller(connect_only=True)

        print "----- IPython information -----"
        print "profile: %s" % self.profile
        connected = client is not None
        print "connected to controller: %s" % (
                "yes" if connected else "no")
        st_ctrl = (self.started_controller is not None and
                        self.started_controller.poll() is None)
        print "controller started from VisTrails: %s" % (
                "running" if st_ctrl else "no")
        st_engines = sum(1 for p in self.started_engines if p.poll() is None)
        print "engines started from VisTrails: %d" % st_engines
        if client is not None:
            nb_engines = len(client.ids)
        else:
            nb_engines = None
        print "total engines in cluster: %s" % (
                nb_engines if nb_engines is not None else "(unknown)")
        if connected:
            dview = client[:]
            with dview.sync_imports():
                import os
                import platform
                import socket
            engines = dview.apply_async(
                    eval,
                    '(os.getpid(), platform.system(), socket.getfqdn())'
            ).get_dict()
            engines = sorted(
                    engines.items(),
                    key=lambda (ip_id, (pid, system, fqdn)): (fqdn, ip_id))
            print "engines:"
            print "\tid\tsystem\tPID\tnode FQDN"
            print "\t--\t------\t---\t---------"
            for ip_id, (pid, system, fqdn) in engines:
                print "\t%d\t%s\t%d\t%s" % (ip_id, system, pid, fqdn)
        print ""

        if qt_available:
            dialog = QtGui.QDialog()
            layout = QtGui.QVBoxLayout()
            form = QtGui.QFormLayout()
            form.addRow(
                    "Profile:",
                    QtGui.QLabel(self.profile))
            form.addRow(
                    "Connected:",
                    QtGui.QLabel("yes" if connected else "no"))
            form.addRow(
                    "Controller started from VisTrails:",
                    QtGui.QLabel("running" if st_ctrl else "no"))
            form.addRow(
                    "Engines started from VisTrails:",
                    QtGui.QLabel(str(st_engines)))
            form.addRow(
                    "Total engines in cluster:",
                    QtGui.QLabel(str(nb_engines)
                                 if nb_engines is not None
                                 else "(unknown)"))
            layout.addLayout(form)
            if connected:
                tree = QtGui.QTreeWidget()
                tree.setHeaderHidden(False)
                tree.setHeaderLabels(["IPython id", "PID", "System type"])
                engine_tree = dict()
                for ip_id, (pid, system, fqdn) in engines:
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
                layout.addWidget(tree)

            ok = QtGui.QPushButton("Ok")
            QtCore.QObject.connect(ok, QtCore.SIGNAL('clicked()'),
                                   dialog, QtCore.SLOT('accept()'))
            layout.addWidget(ok, 1, QtCore.Qt.AlignHCenter)
            dialog.setLayout(layout)
            dialog.exec_()

    def change_profile(self):
        self.cleanup()

        old_profile = self.profile
        self._select_profile()
        if not self.profile:
            self.profile = old_profile

        if self.profile != old_profile:
            # Here, the processes that were started but the user didn't want to
            # clean up are abandonned
            # They will continue running but later cleanups won't ask for these
            # ones
            self.started_engines = set()
            self.started_controller = None

    def cleanup(self):
        """Shut down the started processes (with user confirmation).
        """
        engines = sum(1 for p in self.started_engines if p.poll() is None)
        ctrl = (self.started_controller is not None and
                self.started_controller.poll() is None)
        print ("parallelflow: cleanup: %s, %d engines running" % (
               "controller running" if ctrl else "no controller",
               engines))

        if engines > 0:
            if qt_available:
                if self._client is not None:
                    total = " (among %d total)" % len(self._client.ids)
                else:
                    total = ''
                res = QtGui.QMessageBox.question(
                        None,
                        "Shutdown engines",
                        "%d engines started here%s are still "
                        "running. Do you want to stop them?" % (
                                engines,
                                total),
                        QtGui.QMessageBox.Yes,
                        QtGui.QMessageBox.No)
                res = res == QtGui.QMessageBox.Yes
            else:
                res = True
            if res:
                for engine in self.started_engines:
                    engine.terminate()
                    engine.wait()
                print ("parallelflow: %d engines terminated" %
                       len(self.started_engines))
                self.started_engines = set()

        if ctrl:
            if qt_available:
                res = QtGui.QMessageBox.question(
                        None,
                        "Shutdown controller",
                        "The controller is still running. Do you want to stop "
                        "it?",
                        QtGui.QMessageBox.Yes,
                        QtGui.QMessageBox.No)
                res = res == QtGui.QMessageBox.Yes
            else:
                res = True
            if res:
                self.started_controller.terminate()
                self.started_controller.wait()
                self.started_controller = None
                print "parallelflow: controller terminated"

        if self._client is not None:
            print "parallelflow: closing client"
            self._client.close()
            self._client = None

    def shutdown_cluster(self):
        """Use the client to request a shutdown of the whole cluster.
        """
        client = self.ensure_controller(connect_only=True)
        if client is None:
            if qt_available:
                QtGui.QMessageBox.information(
                        None,
                        "Couldn't connect",
                        "Couldn't connect to a controller. Is the cluster "
                        "down already?")
            print ("parallelflow: shutdown_cluster requested, but could "
                   "not connect to a controller")
            return

        if qt_available:
            res = QtGui.QMessageBox.question(
                    None,
                    "Shutdown cluster",
                    "This will use the client connection to request the hub "
                    "and every engine to shutdown. Continue?",
                    QtGui.QMessageBox.Ok,
                    QtGui.QMessageBox.Cancel)
            if res != QtGui.QMessageBox.Ok:
                return

        self._client.shutdown(
                targets='all',
                restart=False,
                hub=True,
                block=False)
        print "parallelflow: cluster shutdown requested"
        self._client = None

EngineManager = EngineManager()
