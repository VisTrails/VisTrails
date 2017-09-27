#!/usr/bin/env python
# pragma: no testimport
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

# Installs a package through APT, showing progress.
from __future__ import division

import apt
import apt_pkg
import locale
import sys
import time

from apt_pkg import gettext as _
from apt.progress.base import InstallProgress, OpProgress, AcquireProgress

from PyQt5 import QtCore, QtGui, QtWidgets


package_name = sys.argv[1]

##############################################################################

def smart_decode(msg):
    if isinstance(msg, bytes):
        encoding = locale.getpreferredencoding() or 'utf-8'
        msg = msg.decode(encoding, 'replace').replace(u'\xFFFD', '?')
    return msg

class GuiOpProgress(OpProgress):
    def __init__(self, pbar):
        OpProgress.__init__(self)
        self.pbar = pbar

    def update(self, percent):
        self.pbar.setValue(int(percent))
        QtWidgets.QApplication.processEvents()
        OpProgress.update(self, percent)

    def done(self):
        OpProgress.done(self)

class GUIAcquireProgress(AcquireProgress):
    def __init__(self, pbar, status_label):
        AcquireProgress.__init__(self)
        self.pbar = pbar
        self.status_label = status_label
        self.percent = 0.0

    def pulse(self, owner):
        current_item = self.current_items + 1
        if current_item > self.total_items:
            current_item = self.total_items
        if self.current_cps > 0:
            text = (_("Downloading file %(current)li of %(total)li with "
                      "%(speed)s/s") %
                      {"current": current_item,
                       "total": self.total_items,
                       "speed": apt_pkg.size_to_str(self.current_cps)})
        else:
            text = (_("Downloading file %(current)li of %(total)li") %
                      {"current": current_item,
                       "total": self.total_items})
        self.status_label.setText(text)
        percent = (((self.current_bytes + self.current_items) * 100.0) /
                        float(self.total_bytes + self.total_items))
        self.pbar.setValue(int(percent))
        QtWidgets.QApplication.processEvents()
        return True

    def start(self):
        self.status_label.setText("Started downloading.")
        QtWidgets.QApplication.processEvents()

    def stop(self):
        self.status_label.setText("Finished downloading.")
        QtWidgets.QApplication.processEvents()

    def done(self, item):
        print "[Fetched] %s" % item.shortdesc
        self.status_label.setText("[Fetched] %s" % item.shortdesc)
        QtWidgets.QApplication.processEvents()

    def fail(self, item):
        print "[Failed] %s" % item.shortdesc

    def ims_hit(self, item):
        print "[Hit] %s" % item.shortdesc
        self.status_label.setText("[Hit] %s" % item.shortdesc)
        QtWidgets.QApplication.processEvents()

    def media_change(self, media, drive):
        print "[Waiting] Please insert media '%s' in drive '%s'" % (
                media, drive)

class GUIInstallProgress(InstallProgress):
    def __init__(self, pbar, status_label):
        InstallProgress.__init__(self)
        self.pbar = pbar
        self.status_label = status_label
        self.last = 0.0

    def status_change(self, pkg, percent, status):
        if self.last >= percent:
            return
        self.status_label.setText(smart_decode(status))
        self.pbar.setValue(int(percent))
        self.last = percent
        QtWidgets.QApplication.processEvents()

    def pulse(self):
        QtWidgets.QApplication.processEvents()
        return InstallProgress.pulse(self)

    def finish_update(self):
        pass

    def processing(self, pkg, stage):
        print "starting '%s' stage for %s" % (stage, pkg)

    def conffile(self,current,new):
        print "WARNING: conffile prompt: %s %s" % (current, new)

    def error(self, errorstr):
        print "ERROR: got dpkg error: '%s'" % errorstr

##############################################################################

class Window(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)

        mainlayout = QtWidgets.QVBoxLayout()
        self.setLayout(mainlayout)
        desktop = QtWidgets.QApplication.desktop()
        geometry = desktop.screenGeometry(self)
        h = 200
        w = 300
        self.setGeometry(geometry.left() + (geometry.width() - w)//2,
                         geometry.top() + (geometry.height() - h)//2,
                         w, h)
        self.setWindowTitle('VisTrails APT interface')
        lbl = QtWidgets.QLabel(self)
        mainlayout.addWidget(lbl)
        lbl.setText("VisTrails is about to install '%s'."
                    "Continue?" % package_name)
        lbl.resize(self.width(), 150)
        lbl.setAlignment(QtCore.Qt.AlignHCenter)
        lbl.setWordWrap(True)
        layout = QtWidgets.QHBoxLayout()
        self.allowBtn = QtWidgets.QPushButton("Install")
        self.denyBtn = QtWidgets.QPushButton("Cancel")
        layout.addWidget(self.allowBtn)
        layout.addWidget(self.denyBtn)
        self.layout().addLayout(layout)

        self.allowBtn.clicked.connect(self.perform_install)
        self.denyBtn.clicked.connect(self.fail_quit)
        pbarlayout = QtWidgets.QVBoxLayout()
        pbar = QtWidgets.QProgressBar()
        pbar.setMinimum(0)
        pbar.setMaximum(100)
        pbarlayout.addWidget(pbar)
        self.layout().addLayout(pbarlayout)
        pbar.show()
        self.pbar = pbar
        self.pbar.setValue(0)
        self.status_label = QtWidgets.QLabel(self)
        mainlayout.addWidget(self.status_label)
        self.layout().addStretch()

        self.op_progress = None #GuiOpProgress(self.pbar)
        self.status_label.setText('Waiting for decision...')

    def fail_quit(self):
        sys.exit(-1)

    def perform_install(self):
        self.allowBtn.setEnabled(False)
        self.denyBtn.setEnabled(False)

        self.status_label.setText('Reading package cache')
        QtWidgets.QApplication.processEvents()
        apt_pkg.init()
        cache = apt.cache.Cache(self.op_progress)
        pkg = None
        try:
            pkg = cache[package_name]
        except KeyError:
            self.status_label.setText('Package not found: updating cache')
            QtWidgets.QApplication.processEvents()
            cache.update(self.op_progress)
            try:
                pkg = cache[package_name]
            except KeyError:
                self.show_quit('Package not found!')
        if pkg.is_installed:
            self.show_quit('Package already installed!', result=0)
        self.status_label.setText('Marking for install')
        pkg.mark_install()
        self.status_label.setText('Installing')
        QtWidgets.QApplication.processEvents()
        try:
            aprogress = GUIAcquireProgress(self.pbar, self.status_label)
            iprogress = GUIInstallProgress(self.pbar, self.status_label)
            cache.commit(aprogress, iprogress)
        except Exception:
            import traceback; traceback.print_exc()
            self.show_quit('Error installing package!')
        print "Installation successful, back to VisTrails..."
        self.show_quit("Success, exiting...", result=0)

    def show_quit(self, message, t=2, result=1):
        self.status_label.setText(message)
        QtWidgets.QApplication.processEvents()
        time.sleep(t)
        sys.exit(result)

##############################################################################

app = QtWidgets.QApplication(sys.argv)

window = Window()
window.show()
app.exec_()
sys.exit(0)
