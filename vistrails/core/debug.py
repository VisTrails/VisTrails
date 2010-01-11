############################################################################
##
## Copyright (C) 2006-2010 University of Utah. All rights reserved.
##
## This file is part of VisTrails.
##
## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of
## this file.  Please review the following to ensure GNU General Public
## Licensing requirements will be met:
## http://www.opensource.org/licenses/gpl-license.php
##
## If you are unsure which license is appropriate for your use (for
## instance, you are interested in developing a commercial derivative
## of VisTrails), please contact us at vistrails@sci.utah.edu.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################
import logging
import logging.handlers
import sys
import inspect
from core.utils import VersionTooLow
import code
import threading
from core import system
import time
from PyQt4 import QtCore

################################################################################

class DebugPrint(QtCore.QObject):
    """ Class to be used for debugging information.

    Verboseness can be set in the following way:
        - DebugPrint.Critical
            Only critical messages will be shown
        - DebugPrint.Warning
            Warning and critical messages will be shown
        - DebugPrint.Log
            Information, warning and Critical messages will be shown
            
    As it uses information such as file name and line number, it should not be
    used interactively. Also, it goes up only one level in the traceback stack,
    so it will only get information of who called the DebugPrint functions. 

    Example of usage:
        >>> DebugPrint.getInstance().set_message_level(DebugPrint.Warning)
        # the following message will be shown
        >>> DebugPrint.getInstance().warning('This is a warning message') 
        #only warnings and above are shown
        >>> DebugPrint.getInstance().log('This is a log message and it will \
        not be shown') 
        
    """
    (Critical, Warning, Log) = (logging.CRITICAL,
                                logging.WARNING,
                                logging.INFO) #python logging levels
    #Singleton technique
    _instance = None
    class DebugPrintSingleton(QtCore.QObject):
        def __call__(self, *args, **kw):
            if DebugPrint._instance is None:
                obj = DebugPrint(*args, **kw)
                DebugPrint._instance = obj
            return DebugPrint._instance
        
    getInstance = DebugPrintSingleton()
    
    def make_logger(self, f=None):
        self.fhandler = None
        """self.make_logger_240(file) -> logger. Creates a logging object to
        be used within the DebugPrint class that sends the debugging
        output to file.
        We will configure log so it outputs to both stderr and a file. 
        
        """
        self.logger = logging.getLogger("VisLog")
        self.logger.setLevel(logging.INFO)
        self.format = logging.Formatter('VisTrails %(asctime)s %(levelname)s: %(message)s')
        # first we define a handler for logging to a file
        if f:
            self.fhandler = logging.handlers.RotatingFileHandler(f, 
                                                                 maxBytes=1024*1024, 
                                                                 backupCount=5)
        
            self.fhandler.setFormatter(self.format)
            self.fhandler.setLevel(logging.INFO)
            self.logger.addHandler(handler)
        
        #then we define a handler to log to the console
        self.console = logging.StreamHandler()
        self.console.setFormatter(self.format)
        self.console.setLevel(logging.CRITICAL)
        self.logger.addHandler(self.console)
        
    if system.python_version() <= (2,4,0,'',0):
        raise VersionTooLow('Python', '2.4.0')
                
    def __init__(self):
        QtCore.QObject.__init__(self)
        self.make_logger()
        self.level = logging.CRITICAL
        
    def set_logfile(self, f):
        """set_logfile(file) -> None. Redirects debugging
        output to file."""
        try:
            handler = logging.handlers.RotatingFileHandler(f, maxBytes=1024*1024, 
                                                           backupCount=5)
            handler.setFormatter(self.format)
            handler.setLevel(logging.INFO)
            if self.fhandler:
                self.logger.removeHandler(self.fhandler)
            self.fhandler = handler
            self.logger.addHandler(self.fhandler)

        except Exception, e:
            self.critical("Could not set log file %s: %s"%(f,str(e)))
            
    def set_message_level(self,level):
        """self.set_message_level(level) -> None. Sets the logging
        verboseness.  level must be one of (DebugPrint.Critical,
        DebugPrint.Warning, DebugPrint.Log)."""
        self.level = level
        self.console.setLevel(level)
        
    def message(self, caller, msg):
        """self.message(caller, msg) -> str. Returns a string with a
        formatted message to be send to the debugging output. This
        should not be called explicitly from userland. Consider using
        self.log(), self.warning() or self.critical() instead."""
        source = inspect.getsourcefile(caller)
        line = caller.f_lineno
        if source and line:
            return "File '" + source + "' at line " + str(line) + ": " + msg
        else:
            return "(File info not available): " + msg
        
    def debug(self,msg):
        """self.log(str) -> None. Send information message (low
        importance) to log with appropriate call site information."""
        caller = inspect.currentframe().f_back # who called us?
        self.logger.debug(self.message(caller, msg))
        
    def log(self,msg):
        """self.log(str) -> None. Send information message (low
        importance) to log with appropriate call site information."""
        caller = inspect.currentframe().f_back # who called us?
        self.logger.info(self.message(caller, msg))
        
    def warning(self,msg):
        """self.warning(str) -> None. Send warning message (medium
        importance) to log with appropriate call site information."""
        caller = inspect.currentframe().f_back # who called us?
        self.logger.warning(self.message(caller, msg))
        
    def critical(self,msg):
        """self.critical(str) -> None. Send critical message (high
        importance) to log with appropriate call site information."""
        caller = inspect.currentframe().f_back # who called us?
        self.logger.critical(self.message(caller, msg))

    def watch_signal(self, obj, sig):
        """self.watch_signal(QObject, QSignal) -> None. Connects a debugging
        call to a signal so that every time signal is emitted, it gets
        registered on the log."""
        self.connect(obj, sig, self.__debugSignal)

    def __debugSignal(self, *args):
        self.critical(str(args))

debug    = DebugPrint.getInstance().debug
critical = DebugPrint.getInstance().critical
warning  = DebugPrint.getInstance().warning
log      = DebugPrint.getInstance().log

################################################################################

def timecall(method):
    """timecall is a method decorator that wraps any call in timing calls
    so we get the total time taken by a function call as a debugging message."""
    def call(self, *args, **kwargs):
        caller = inspect.currentframe().f_back
        start = time.time()
        method(self, *args, **kwargs)
        end = time.time()
        critical(DebugPrint.message(caller, "time: %.5s" % (end-start)))
    call.__doc__ = method.__doc__
    return call

################################################################################

def object_at(desc):
    """object_at(id) -> object

    id is an int returning from id() or a hex string of id()

    Fetches all live objects, finds the one with given id, and returns
    it.  Warning: THIS IS FOR DEBUGGING ONLY. IT IS SLOW."""
    if type(desc) == int:
        target_id = desc
    elif type(desc) == str:
        target_id = int(desc, 16) # Reads desc as the hex address
    import gc
    for obj in gc.get_objects():
        if id(obj) == target_id:
            return obj
    raise Exception("Couldn't find object")
