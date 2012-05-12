#!/usr/bin/env python
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

# Installs a package through APT, showing progress.

if __name__ != '__main__':
    import tests
    raise tests.NotModule('This should not be imported as a module')

import apt
import apt_pkg
import sys, os
import copy
import time

package_name = sys.argv[1]

from apt.progress import InstallProgress
from apt.progress import FetchProgress

cache = apt.Cache(apt.progress.OpTextProgress())

try:
    pkg = cache[package_name]
except KeyError:
    sys.exit(1)

if pkg.isInstalled:
    sys.exit(0)


##############################################################################

from PyQt4 import QtCore, QtGui

class GUIInstallProgress(InstallProgress):
    def __init__(self, pbar, status_label):
        apt.progress.InstallProgress.__init__(self)
        self.pbar = pbar
        self.status_label = status_label
        self.last = 0.0
    def updateInterface(self):
        InstallProgress.updateInterface(self)
        if self.last >= self.percent:
            return
        self.status_label.setText(self.status)
        self.pbar.setValue(int(self.percent))
        self.last = self.percent
        QtGui.qApp.processEvents()
    def pulse(self):
        QtGui.qApp.processEvents()
        return InstallProgress.pulse(self)
    def finishUpdate(self):
        InstallProgress.finishUpdate(self)
        self.quit()
    def conffile(self,current,new):
        print "WARNING: conffile prompt: %s %s" % (current,new)
    def error(self, errorstr):
        print "ERROR: got dpkg error: '%s'" % errorstr

class GUIFetchProgress(FetchProgress):

    def __init__(self, pbar, status_label):
        apt.progress.FetchProgress.__init__(self)
        self.pbar = pbar
        self.status_label = status_label

    def pulse(self):
        FetchProgress.pulse(self)
        if self.currentCPS > 0:
            s = "%sB/s %s" % (apt_pkg.SizeToStr(int(self.currentCPS)),
                              apt_pkg.TimeToStr(int(self.eta)))
        else:
            s = "[Working..]"
        self.status_label.setText(s)
        self.pbar.setValue(int(self.percent))
        QtGui.qApp.processEvents()
        return True

    def stop(self):
        self.status_label.setText("Finished downloading.")
        QtGui.qApp.processEvents()
    
    def updateStatus(self, uri, descr, shortDescr, status):
        if status != self.dlQueued:
            print "\r%s %s" % (self.dlStatusStr[status], descr)
    
        
class Window(QtGui.QWidget):

    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        
        mainlayout = QtGui.QVBoxLayout()
        self.setLayout(mainlayout)
        desktop = QtGui.qApp.desktop()
        print desktop.isVirtualDesktop()
        geometry = desktop.screenGeometry(self)
        h = 200
        w = 300
        self.setGeometry(geometry.left() + (geometry.width() - w)/2,
                         geometry.top() + (geometry.height() - h)/2,
                         w, h)
        self.setWindowTitle('VisTrails APT interface')
        lbl = QtGui.QLabel(self)
        mainlayout.addWidget(lbl)
        lbl.setText("VisTrails wants to use APT to install\
 package '%s'. Do you want to allow this?" % package_name) 
        lbl.resize(self.width(), 150)
        lbl.setAlignment(QtCore.Qt.AlignHCenter)
        lbl.setWordWrap(True)
        layout = QtGui.QHBoxLayout()
        self.allowBtn = QtGui.QPushButton("Yes, allow")
        self.denyBtn = QtGui.QPushButton("No, deny")
        layout.addWidget(self.allowBtn)
        layout.addWidget(self.denyBtn)
        self.layout().addLayout(layout)

        self.connect(self.allowBtn, QtCore.SIGNAL("clicked()"),
                     self.perform_install)
        self.connect(self.denyBtn, QtCore.SIGNAL("clicked()"),
                     QtGui.qApp, QtCore.SLOT("quit()"))

        pbarlayout = QtGui.QVBoxLayout()
        pbar = QtGui.QProgressBar()
        pbar.setMinimum(0)
        pbar.setMaximum(100)
        pbarlayout.addWidget(pbar)
        self.layout().addLayout(pbarlayout)
        pbar.show()
        self.pbar = pbar
        self.pbar.setValue(0)
        self.status_label = QtGui.QLabel(self)
        mainlayout.addWidget(self.status_label)
        self.status_label.setText('Waiting for decision...')
        self.layout().addStretch()

    def perform_install(self):
        pkg.markInstall()
        self.allowBtn.setEnabled(False)
        self.denyBtn.setEnabled(False)
        fprogress = GUIFetchProgress(self.pbar, self.status_label)
        iprogress = GUIInstallProgress(self.pbar, self.status_label)
        try:
            cache.commit(fprogress, iprogress)
        except OSError, e:
            pass
        except Exception, e:
            
            self._timeout = QtCore.QTimer()
            self.connect(self._timeout, QtCore.SIGNAL("timeout()"),
                         QtGui.qApp, QtCore.SLOT("quit()"))
            self._timeout.start(3000)
            self.status_label.setText("Success, exiting in 3 seconds.")

app = QtGui.QApplication(sys.argv)

window = Window()
window.show()
print app.exec_()
sys.exit(0)

