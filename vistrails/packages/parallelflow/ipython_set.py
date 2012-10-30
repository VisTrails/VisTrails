import os
import sys
import time
import logging
import socket
from IPython.config.loader import Config
from IPython.parallel.apps.launcher import LocalControllerLauncher,\
                                           LocalEngineLauncher, \
                                           SSHEngineLauncher
                                           
from PyQt4 import QtCore, QtGui

local_profile_dir = os.path.join(os.getenv('HOME'), '.ipython/profile_default')

class IPythonSet:
    """
    This class represents a set containing one IPython Controller and n
    IPython Engines.
    This class is used to start, re-start and stop the controller / engines
    using the gui.
    """
    
    def __init__(self, ip, controller_type='local'):
        """
        Init method for IPythonSet.
        'ip'              --> ip where engines will be started (external interface
                              where the controller will listen for connections)
        'controller_type' --> local, ssh 
        """
        
        # controller and set of engines
        self.controller = None
        self.controller_type = controller_type
        self.engines = []
        self.number_engines = 0
        self.engine_type = None
        self.ip = ip
        self.hostname = socket.gethostbyaddr(ip)[0]
        
        # IPython information
        self.config = None
        self.profile_dir = None
        
        # logger
        self.logger = logging.Logger('vt-ipython')
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(logging.StreamHandler(sys.stdout))
        
        # creating and starting the controller
        self.create_controller()
        
        print "Controller started!"


    def create_controller(self):
        """
        Creates and starts the controller.
        """
        
        if self.controller_type == 'local':
            # IPython information
            self.config = Config(ProfileDir={})
            self.profile_dir = local_profile_dir
            
            # controller
            self.controller = LocalControllerLauncher(ip=self.ip,
                                                      config=self.config,
                                                      log=self.logger,
                                                      profile_dir=self.profile_dir)
            self.controller.start()
        else:
            # TODO: Do we need controllers that are not local?
            pass
        
    def restart_controller(self):
        """
        Restarts the controller.
        """
        
        self.controller.stop()
        self.create_controller()
        
        print "Controller restarted!"
        
        
    def stop_controller(self):
        """
        Stops the controller.
        """
        
        self.controller.stop()
        
        print "Controller stopped!"
        
        
    def create_engine(self):
        """
        Creates and starts an engine.
        """

        e = None
        if self.engine_type == 'local':
            e = LocalEngineLauncher(config=self.config,
                                    log=self.logger,
                                    profile_dir=self.profile_dir)
        elif self.engine_type == 'ssh':
            e = SSHEngineLauncher(config=self.config,
                                  log=self.logger,
                                  profile_dir=self.profile_dir,
                                  hostname=self.hostname)
        else:
            #TODO: deal with other cases
            pass
        
        self.engines.append(e)
        e.start()
        
        
    def add_engines(self, n, engine_type='local'):
        """
        Adds engines to the IPython set.
        'n'           --> number of engines to be started
        'engine_type' --> local, ssh
        """
        
        if self.engine_type:
            if self.engine_type != engine_type:
                raise Exception("Engine type '%s' different from '%s'." %(engine_type,
                                                                          self.engine_type))
        else:
            self.engine_type = engine_type
            
        for i in range(n):
            self.create_engine()
        time.sleep(2)
            
        self.number_engines += n
        
        print "Engines created!"
        
        
    def restart_engines(self):
        """
        Restarts the engines of the IPython set.
        """
        
        self.stop_engines()
        self.engines = []
        
        for i in range(self.number_engines):
            self.create_engine()
        time.sleep(2)
            
        print "Engines restarted!"
        
    def stop_engines(self):
        """
        Stops the engines of the IPython set.
        There should not be an error if there are no engines running.
        """
        
        [e.stop() for e in self.engines]
        
        print "Engines stopped!"
        

class QWarningDialog(QtGui.QDialog):
    """
    QWarningDialog already comes with two buttons: 'OK' and 'Cancel'.
    """
    
    def __init__(self, text, button_cancel=True, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setModal(True)
        self.setWindowTitle("IPython Warning")
        self.setLayout(QtGui.QVBoxLayout())
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(QtGui.QLabel(text))
        self.layout().addLayout(hbox)

        bbox = QtGui.QHBoxLayout()
        ok = QtGui.QPushButton("OK")
        if button_cancel:
            cancel = QtGui.QPushButton("Cancel")
            cancel.setDefault(True)
            bbox.addWidget(cancel, 1, QtCore.Qt.AlignRight)
        bbox.addWidget(ok, 0, QtCore.Qt.AlignRight)
        self.layout().addLayout(bbox)
        self.connect(ok, QtCore.SIGNAL("clicked(bool)"), self.accept)
        if button_cancel:
            self.connect(cancel, QtCore.SIGNAL("clicked(bool)"), self.reject)
        
    def is_ok(self):
        return self.accept
    
    def is_cancel(self):
        return self.reject
    
class QuestionDialog(QtGui.QDialog):
    """
    A dialog to get information from the user.
    """
    
    def __init__(self, title, label, default, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setModal(True)
        self.setWindowTitle(title)
        self.setLayout(QtGui.QVBoxLayout())
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(QtGui.QLabel(label))
        self.line_edit = QtGui.QLineEdit()
        self.line_edit.setText(default)
        hbox.addWidget(self.line_edit)
        self.layout().addLayout(hbox)

        bbox = QtGui.QHBoxLayout()
        cancel = QtGui.QPushButton("Cancel")
        ok = QtGui.QPushButton("OK")
        ok.setDefault(True)
        bbox.addWidget(cancel, 1, QtCore.Qt.AlignRight)
        bbox.addWidget(ok, 0, QtCore.Qt.AlignRight)
        self.layout().addLayout(bbox)
        self.connect(ok, QtCore.SIGNAL("clicked(bool)"), self.accept)
        self.connect(cancel, QtCore.SIGNAL("clicked(bool)"), self.reject)

    def get_answer(self):
        return str(self.line_edit.text())
    
class QIpDialog(QuestionDialog):
    """
    Gets the ip where the engines are located.
    """
    
    def __init__(self, parent=None):
        QuestionDialog.__init__(self,
                                title="What is the IP for the engines?",
                                label="IP where engines are located:",
                                default="127.0.0.1",
                                parent=parent)
    
class QAddEnginesDialog(QuestionDialog):
    """
    Gets the number of engines to be added.
    """
    
    def __init__(self, parent=None):
        QuestionDialog.__init__(self,
                                title="How many engines?",
                                label="Number of Engines:",
                                default="4",
                                parent=parent)
        