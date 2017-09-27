from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import paraview.simple as pv
from configuration import configuration

try:
    QString = unicode
except NameError:
    # Python 3
    QString = str

class QPVConfigWindow(QtWidgets.QWidget):

    def __init__(self, proc_num=4, port=11111, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setWindowTitle('ParaView Local Server')
        vbox = QtWidgets.QVBoxLayout()
        self.setLayout(vbox)

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        
        hbox.addWidget(QtWidgets.QLabel('# Procs'))
        self.procSpin = QtWidgets.QSpinBox()
        self.procSpin.setRange(1, 1024*1024)
        self.procSpin.setValue(proc_num)
        hbox.addWidget(self.procSpin)
        
        hbox.addWidget(QtWidgets.QLabel('Port'))
        self.portSpin = QtWidgets.QSpinBox()
        self.portSpin.setRange(0, 64*1024)
        self.portSpin.setValue(port)
        hbox.addWidget(self.portSpin)
        
        hbox.addStretch()
        
        self.cmdOut = QtWidgets.QTextEdit()
        self.cmdOut.setReadOnly(True)
        vbox.addWidget(self.cmdOut)

        self.runButton = QtWidgets.QPushButton('Start')
        vbox.addWidget(self.runButton)

        self.pvProcess = QtCore.QProcess()
        self.pvProcess.setProcessChannelMode(QtCore.QProcess.MergedChannels)
        self.pvProcess.readyReadStandardOutput.connect(self.updateLogs)
        self.pvProcess.error.connect(self.updateError)
        self.pvProcess.finished[int, QProcess.ExitStatus].connect(self.pvServerFinished)
        
        self.runButton.clicked.connect(self.togglePVServer)

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
        self.cmdOut.append(QString(self.pvProcess.readAllStandardOutput()))

    def updateError(self, error):
        self.cmdOut.append('ERROR %s\n' % error)

    def pvServerFinished(self, exitCode, exitStatus):
        self.cmdOut.append('Exited\n')
        self.runButton.setText('Start')

if __name__=='__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = QPVConfigWindow()
    window.show()
    app.exec_()
