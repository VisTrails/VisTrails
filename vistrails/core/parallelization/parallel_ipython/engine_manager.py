import os
import subprocess
import sys
import time

from IPython.utils.path import get_ipython_dir, locate_profile
from .ipython_callbacks import SafeClient
from IPython.parallel import error

from vistrails.core.system import vistrails_root_directory


try:
    from PyQt4 import QtGui
    QtGui.QDialog
except Exception:
    qt_available = False
else:
    qt_available = True


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


class IPythonProfile(object):
    """Info kept by EngineManager for a specific profile.

    Has useful methods to interact with a specific cluster.
    """
    def __init__(self, profile):
        self.profile = profile
        self.started_controller = None
        self.started_engines = set()
        self._client = None

    def ensure_client(self, connect_only=False):
        """Make sure a Client is available.

        If we can't connect and connect_only is False, start a local controller
        and connect to it.
        """
        # Already connected
        if self._client:
            return self._client

        print "ipython: %s: connecting" % self.profile

        try:
            self._client = SafeClient(profile=self.profile)
            print "ipython: %s: connected to controller" % self.profile
            return self._client
        except error.TimeoutError:
            print "ipython: %s: timeout when connecting" % self.profile
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
            print "ipython: %s: didn't find a controller" % self.profile
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
            print "ipython: %s: starting local controller" % self.profile
            proc, code = start_process(
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
                print ("ipython: %s: controller process exited with "
                       "code %d" % (self.profile, code))
                return None
            else:
                self.started_controller = proc
                print "ipython: %s: local controller started, connecting" % (
                        self.profile)
                self._client = SafeClient(profile=self.profile)
                return self._client

        return None

    @property
    def connected(self):
        return self._client is not None

    def info(self):
        """Show some information on the cluster.
        """
        client = self.ensure_client(connect_only=True)

        info = {}

        info['profile'] = self.profile
        info['connected'] = connected = self.connected
        info['started_controller'] = (self.started_controller is not None and
                                      self.started_controller.poll() is None)
        info['started_engines'] = sum(1 for p in self.started_engines if p.poll() is None)
        if client is not None:
            info['total_engines'] = len(client.ids)
            try:
                client.db_query({'msg_id': 'ae5f5276-1aad-40ef-ade9-a3175a3be7be'})
            except error.IPythonError:
                info['database'] = False
            else:
                info['database'] = True
        else:
            info['total_engines'] = None
            info['database'] = None
        if connected and client.ids:
            with client.direct_view() as dview:
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
        else:
            engines = []
        info['engines'] = engines

        return info

    def start_engines(self, nb=None, prompt="Number of engines to start"):
        """Start some engines locally
        """
        c = self.ensure_client()
        if c is None:
            if qt_available:
                QtGui.QMessageBox.warning(
                        None,
                        "No controller",
                        "Can't start engines: couldn't connect to a "
                        "controller")
            print "ipython: %s: not connected, not starting engines" % (
                    self.profile)
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
            elif not nb:
                nb = 1
            print "ipython: %s: about to start %d engines" % (self.profile, nb)
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
                proc, res = start_process(
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
                print "ipython: %s: %d engine(s) exited with codes: %s" % (
                        self.profile, nb_failed, failed)
            self.started_engines.update(starting)

            if qt_available:
                bar.hide()
                bar.deleteLater()
            print "ipython: %s: %d engines started" % (self.profile, i + 1)

    def cleanup(self, ask=True):
        """Shut down the started processes (with user confirmation).
        """
        engines = sum(1 for p in self.started_engines if p.poll() is None)
        ctrl = (self.started_controller is not None and
                self.started_controller.poll() is None)
        print ("ipython: %s: cleanup: %s, %d engines running" % (
               self.profile,
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
                    print "ipython: %s: requested hub shutdown" % self.profile
                else:
                    if self.started_controller.poll() is not None:
                        self.started_controller.terminate()
                        self.started_controller.wait()
                    print "ipython: %s: controller terminated" % self.profile
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
                print ("ipython: %s: %d engines terminated" % (
                       self.profile,
                       len(self.started_engines)))
            self.started_engines = set()

        if self._client is not None:
            print "ipython: %s: closing client" % self.profile
            self._client.close()
            self._client = None

    def shutdown_cluster(self):
        """Use the client to request a shutdown of the whole cluster.
        """
        client = self.ensure_client(connect_only=True)
        if client is None:
            if qt_available:
                QtGui.QMessageBox.information(
                        None,
                        "Couldn't connect",
                        "Couldn't connect to a controller. Is the cluster "
                        "down already?")
            print ("ipython: %s: shutdown_cluster requested, but could "
                   "not connect to controller" % self.profile)
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
        print "ipython: %s: cluster shutdown requested" % self.profile
        self._client = None


@apply
class EngineManager(object):
    """Singleton object keeping track of IPython connections.

    For each profile, this manager can obtain engines information, connect and
    disconnect, start a local controller, add a bunch of local engines, and
    request the whole cluster to shutdown. It also keeps track of locally
    started processes in order to optionally close them when VisTrails exits.
    """
    def __init__(self):
        self._profiles = {}

    def list_profiles(self):
        """Returns a list of available profile names.

        The items are (profile_name: str, connected: bool).
        """
        # See IPython.core.profileapp:list_profile_in()
        profiles = []
        for filename in os.listdir(get_ipython_dir()):
            if filename.startswith('profile_'):
                profile = filename[8:]
                try:
                    connected = self._profiles[profile].connected
                except KeyError:
                    connected = False
                profiles.append((profile, connected))
        return profiles

    def __call__(self, profile):
        """Get an IPythonProfile object for a specific profile name.

        If such an object doesn't exist, it is created.
        """
        try:
            locate_profile(profile)
        except IOError:
            raise KeyError("No IPython profile %r" % profile)
        try:
            return self._profiles[profile]
        except KeyError:
            profmngr = IPythonProfile(profile)
            self._profiles[profile] = profmngr
            return profmngr

    def finalize(self):
        if self._profiles:
            print "ipython: finalizing connections (%d profiles)" % (
                    len(self._profiles))
            for profmngr in self._profiles.itervalues():
                profmngr.cleanup(False)
            self._profiles = None
