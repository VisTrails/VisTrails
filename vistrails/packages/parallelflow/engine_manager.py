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
import subprocess
import sys
import time

from IPython.utils.path import get_ipython_dir, locate_profile
from IPython.parallel import Client
from IPython.parallel import error

from vistrails.core.system import vistrails_root_directory


try:
    from PyQt4 import QtCore, QtGui
except ImportError:
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
        prev_dir = os.getcwd()
        os.chdir(os.path.join(vistrails_root_directory(), os.path.pardir))
        try:
            p = subprocess.Popen(args)
        finally:
            os.chdir(prev_dir)
        if condition is None:
            return p, None
        else:
            while True:
                time.sleep(0.5)
                if condition():
                    return p, None
                res = p.poll()
                if res is not None:
                    return None, res

    def start_engines(self, nb=None, prompt="Number of engines to start"):
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
                        prompt,
                        1,  # value
                        1,  # min
                        16) # max
                if not res:
                    return
            elif nb is None:
                nb = 1
            print "parallelflow: about to start %d engines" % nb
            if qt_available:
                bar = QtGui.QProgressDialog(
                        "Starting engines...",
                        None,
                        0, nb)
                def progress(n):
                    bar.setValue(n)
                bar.show()
            else:
                def progress(n): pass
            progress(0)

            init_engines = set(c.ids)
            # Start the processes
            starting = set()
            for i in xrange(nb):
                proc, res = self.start_process(
                        None,
                        sys.executable,
                        '-m',
                        'IPython.parallel.apps.ipengineapp',
                        '--profile=%s' % self.profile)
                starting.add(proc)
            # Wait for each one to either fail or connect
            failed = []
            connected = 0
            while connected < len(starting):
                connected = len(set(c.ids) - init_engines)
                progress(len(failed) + connected)
                time.sleep(0.5)
                for p in list(starting):
                    res = p.poll()
                    if res is not None:
                        failed.append(res)
                        starting.remove(p)
            if failed:
                nb_failed = len(failed)
                if nb_failed > 3:
                    failed = "%s, ..." % (', '.join('%d' % f for f in failed))
                else:
                    failed = ', '.join('%d' % f for f in failed)
                if qt_available:
                    QtGui.QMessageBox.critical(
                        None,
                        "Error",
                        "%d engine(s) exited with codes: %s" % (
                        nb_failed, failed))
                print "parallelflow: %d engine(s) exited with codes: %s" % (
                        nb_failed, failed)
            self.started_engines.update(starting)

            if qt_available:
                bar.hide()
                bar.deleteLater()
            print "parallelflow: %d engines started" % nb

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
        if connected and client.ids:
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
            if connected and client.ids:
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
                    tree.setFirstItemColumnSpanned(node, True)
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

        hub_shutdown = False

        if ctrl:
            if qt_available:
                res = QtGui.QMessageBox.question(
                        None,
                        "Shutdown controller",
                        "The controller is still running. Do you want to stop "
                        "it?",
                        QtGui.QMessageBox.Yes,
                        QtGui.QMessageBox.No)
                res = res != QtGui.QMessageBox.No
            else:
                res = True
            if res:
                if self._client is not None:
                    self._client.shutdown(
                            targets='all',
                            restart=False,
                            hub=True,
                            block=False)
                    hub_shutdown = True
                    print "parallelflow: requested hub shutdown"
                else:
                    if self.started_controller.poll() is not None:
                        self.started_controller.terminate()
                        self.started_controller.wait()
                    print "parallelflow: controller terminated"
            self.started_controller = None

        if engines > 0 and not hub_shutdown:
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
                res = res != QtGui.QMessageBox.No
            else:
                res = True
            if res:
                for engine in self.started_engines:
                    if engine.poll() is not None:
                        engine.terminate()
                        engine.wait()
                print ("parallelflow: %d engines terminated" %
                       len(self.started_engines))
            self.started_engines = set()

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
