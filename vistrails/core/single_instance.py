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

"""This provides the single-instance mechanism in VisTrails.

When running in single-instance mode, apps will try to connect to an already
existing instance ("server") and get it to process their command-line instead
of doing it themselves ("client").

This has a number of benefits:

* Double-clicking on a VT file will open as a new tab in an existing VisTrails
instance
* Respects MacOS conventions
* Faster start up since clients don't have to load packages again

For the GUI application, single instance is provided through a Qt QLocalServer.

When running in headless mode, single instance can be provided through a TCP or
UNIX socket.

Configuration parameters:

* singleInstance: Whether to try and enforce single-instance. This will only do
  something if running in GUI mode or singleInstanceSocket is set.
* singleInstanceSocket: The socket to use for instance communication. If unset
  and running in GUI mode, use the QLocalServer machinery. If set, always use
  that instead.
"""

import getpass
try:
    import fcntl
except ImportError:
    fcntl = None
try:
    import msvcrt
except ImportError:
    msvcrt = None
import os
import sys
import time

from vistrails.core import debug
from vistrails.core import system


windows = (sys.platform == "win32")


class SingleInstanceError(EnvironmentError):
    """Error while trying to set up the app for single-instance."""


class SingleInstance(object):
    """Single-instance logic.
    """
    def __init__(self, recv_callback):
        self.recv_callback = recv_callback

    def start(self, msg):
        """Do the single-instance dance, trying to connect to a server.

        Returns None if we are the single-instance, or whatever the server sent
        if we managed to connect (what send_message() returned).
        """
        while True:
            if not self.lock():
                sent, ret = self.send_message(msg)
                if sent:
                    debug.warning("Message processed by single instance")
                    return ret
            else:
                if self.listen():
                    break
                else:
                    self.unlock()
                    if self.lock():
                        if self.listen():
                            break
                        else:
                            raise SingleInstanceError("Cannot listen")
            time.sleep(1)
        self.listen()
        debug.log("Single instance created")
        return None

    def stop(self):
        """Stop listening then release the lock.
        """
        self.stop_listen()
        self.unlock()

    def lock(self):
        """Try to acquire the single instance lock.

        :returns: True if we have the lock, False if someone else has it.
        """
        raise NotImplementedError

    def unlock(self):
        """Release the lock.
        """
        raise NotImplementedError

    def listen(self):
        """We have the lock; start listening for other instances.

        Should arrange for self.recv_callback to be called with the message
        when one is received from another instance.
        """
        raise NotImplementedError

    def stop_listen(self):
        """Stop listening so another app may.
        """
        raise NotImplementedError

    def send_message(self, msg):
        """Try to contact single instance (which is holding the lock).

        :returns: A tuple ``(sent, ret)`` where sent is `True` if we managed to
        communicate, and `ret` is the response from the server.
        """
        raise NotImplementedError


class UniqueFilenameMixin(object):
    def __init__(self, **kwargs):
        self._filename = os.path.join(system.home_directory(),
                                      'vistrails-single-instance-%s' %
                                      getpass.getuser())
        super(UniqueFilenameMixin, self).__init__(**kwargs)


class TCPSingleInstance(SingleInstance, UniqueFilenameMixin):
    # Inspired by https://github.com/benediktschmitt/py-filelock

    _file = None

    if windows and msvcrt is not None:
        def lock(self):
            open_mode = os.O_RDWR | os.O_CREAT | os.O_TRUNC
            try:
                fd = os.open(self._filename, open_mode)
            except OSError:
                return False

            try:
                msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
            except (IOError, OSError):
                os.close(fd)
                return False
            else:
                self._file = fd
                return True

        def unlock(self):
            if self._file is not None:
                msvcrt.locking(self._file, msvcrt.LK_UNLCK, 1)
                os.close(self._file)
                self._file = None
                try:
                    os.remove(self._filename)
                except OSError:
                    pass
    elif not windows and fcntl is not None:
        def lock(self):
            open_mode = os.O_RDWR | os.O_CREAT | os.O_TRUNC
            fd = os.open(self._filename, open_mode)

            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except (IOError, OSError):
                os.close(fd)
                return False
            else:
                self._file = fd
                return True

        def unlock(self):
            if self._file is not None:
                fcntl.flock(self._file, fcntl.LOCK_UN)
                os.close(self._file)
                self._file = None
    else:
        def lock(self):
            open_mode = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_TRUNC
            try:
                fd = os.open(self._filename, open_mode)
            except (IOError, OSError):
                return False
            else:
                self._file = fd
                return True

        def unlock(self):
            if self._file is not None:
                os.close(self._file)
                self._file = None

                try:
                    os.remove(self._filename)
                except OSError:
                    pass

    def listen(self):
        TODO

    def stop_listen(self):
        TODO

    def send_message(self, msg):
        TODO


from PyQt4 import QtCore, QtNetwork


class QtSingleInstance(SingleInstance, UniqueFilenameMixin):
    _server = None
    _shared_memory = None
    _timeout = 60000

    def lock(self):
        self._shared_memory = QtCore.QSharedMemory(self._filename)
        if self._shared_memory.attach():
            return False
        else:
            if self._shared_memory.create(1):
                return True
        return False  # retry

    def unlock(self):
        if self._shared_memory is not None:
            self._shared_memory.detach()
            self._shared_memory = None

    def listen(self):
        self._server = QtNetwork.QLocalServer()
        self._server.newConnection.connect(self._msg_received)
        if self._server.listen(self._filename):
            return True
        self._server.close()
        self._server = None
        try:
            os.remove(self._filename)
        except OSError:
            pass
        return False

    def _msg_received(self):
        socket = self._server.nextPendingConnection()
        if not socket.waitForReadyRead(self._timeout):
            debug.critical("Error receiving message: %s" % socket.errorString())
            return
        msg = bytes(socket.readAll())
        rep = self.recv_callback(msg)
        socket.write(rep)
        if not socket.waitForBytesWritten(self._timeout):
            debug.critical("Error sending reply: %s" % socket.errorString())
        socket.disconnectFromServer()

    def stop_listen(self):
        if self._server is not None:
            self._server.close()
            self._server = None

    def send_message(self, msg):
        socket = QtNetwork.QLocalSocket()
        socket.connectToServer(self._filename)
        if not socket.waitForConnected(self._timeout):
            try:
                os.remove(self._filename)
            except OSError:
                pass
        else:
            try:
                socket.write(msg)
                if not socket.waitForBytesWritten(self._timeout):
                    raise SingleInstanceError("Error sending message: %s" %
                                              socket.errorString())
                if not socket.waitForReadyRead(self._timeout):
                    raise SingleInstanceError("Error receiving reply: %s" %
                                              socket.errorString())
                rep = bytes(socket.readAll())
                return True, rep
            finally:
                socket.disconnectFromServer()
        return False, None
