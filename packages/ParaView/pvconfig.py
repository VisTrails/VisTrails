from PyQt4 import QtCore, QtGui
import sys
import paraview.simple as pv
from configuration import configuration

class QPVConfigWindow(QtGui.QWidget):

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setWindowTitle('ParaView Local Server')
        vbox = QtGui.QVBoxLayout()
        self.setLayout(vbox)

        hbox = QtGui.QHBoxLayout()
        vbox.addLayout(hbox)
        
        hbox.addWidget(QtGui.QLabel('# Procs'))
        self.procSpin = QtGui.QSpinBox()
        self.procSpin.setRange(1, 1024*1024)
        self.procSpin.setValue(4)
        hbox.addWidget(self.procSpin)
        
        hbox.addWidget(QtGui.QLabel('Port'))
        self.portSpin = QtGui.QSpinBox()
        self.portSpin.setRange(0, 64*1024)
        self.portSpin.setValue(11111)
        hbox.addWidget(self.portSpin)
        
        hbox.addStretch()
        
        self.cmdOut = QtGui.QTextEdit()
        self.cmdOut.setReadOnly(True)
        vbox.addWidget(self.cmdOut)

        self.runButton = QtGui.QPushButton('Start')
        vbox.addWidget(self.runButton)

        self.pvProcess = QtCore.QProcess()
        self.pvProcess.setProcessChannelMode(QtCore.QProcess.MergedChannels)
        self.connect(self.pvProcess, QtCore.SIGNAL('readyReadStandardOutput()'), self.updateLogs)
        self.connect(self.pvProcess, QtCore.SIGNAL('error()'), self.updateError)
        self.connect(self.pvProcess, QtCore.SIGNAL('finished(int,QProcess::ExitStatus)'), self.pvServerFinished)
        
        self.connect(self.runButton, QtCore.SIGNAL('clicked()'), self.togglePVServer)

    def buildArguments(self):
        #defaults
        mpiexec_bin = '/usr/bin/mpiexec'
        pvserver_bin = '/usr/local/bin/pvserver'
        
        if configuration.check('mpiexec_bin'):
            mpiexec_bin = configuration.mpiexec_bin
        if configuration.check("pvserver_bin"):
            pvserver_bin = configuration.pvserver_bin
            
        return (mpiexec_bin, ['-n', str(self.procSpin.value()), pvserver_bin, '--server-port=%s' % self.portSpin.value()])

    def sizeHint(self):
        return QtCore.QSize(384, 512)

    def togglePVServer(self):
        if self.pvProcess.state()==QtCore.QProcess.NotRunning:
            self.runButton.setEnabled(False)
            self.cmdOut.append('Starting...\n')
            self.pvProcess.start(*self.buildArguments())
            self.pvProcess.waitForStarted()
            if self.pvProcess.state()==QtCore.QProcess.Running:
                self.runButton.setText('Stop')
                pv.Connect('localhost', self.portSpin.value())
            self.runButton.setEnabled(True)
        else:
            self.pvProcess.terminate()
            self.pvProcess.waitForFinished()

    def updateLogs(self):
        self.cmdOut.append(QtCore.QString(self.pvProcess.readAllStandardOutput()))

    def updateError(self, error):
        self.cmdOut.append('ERROR %s\n' % error)

    def pvServerFinished(self, exitCode, exitStatus):
        self.cmdOut.append('Exited\n')
        self.runButton.setText('Start')

if __name__=='__main__':
    app = QtGui.QApplication(sys.argv)
    window = QPVConfigWindow()
    window.show()
    app.exec_()
