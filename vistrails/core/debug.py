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
import inspect
# from core.utils import VersionTooLow
# from core import system
import time

################################################################################

class DebugPrint:
    """ Class to be used for debugging information.

    Verboseness can be set in the following way:
        - DebugPrint.Critical
            Only critical messages will be shown
        - DebugPrint.Warning
            Warning and critical messages will be shown
        - DebugPrint.Log
            Information, warning and Critical messages will be shown
            
    It uses information such as file name and line number only when printing
    to files and consoles, a stream can be registered to be used in gui.debug.
    Also, it goes up only one level in the traceback stack,
    so it will only get information of who called the DebugPrint functions.

    Example of usage:
        >>> from core import debug
        >>> debug.DebugPrint.getInstance().set_message_level(
                                                     debug.DebugPrint.Warning)
        # the following messages will be shown
        >>> debug.critical('This is an error message')
        >>> debug.warning('This is a warning message')
        #only warnings and above are shown
        >>> debug.log('This is a log message and it will not be shown')
        
    """
    (Critical, Warning, Log) = (logging.CRITICAL,
                                logging.WARNING,
                                logging.INFO) #python logging levels
    #Singleton technique
    _instance = None
    class DebugPrintSingleton():
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
        self.format = logging.Formatter("%(levelname)s: %(asctime)s %(pathname)s"+\
                                ":%(lineno)s\n  %(message)s")
        # first we define a handler for logging to a file
        if f:
            self.set_logfile(f)
        
        #then we define a handler to log to the console
        self.console = logging.StreamHandler()
        self.console.setFormatter(self.format)
        self.console.setLevel(logging.CRITICAL)
        self.logger.addHandler(self.console)
        self.handlers.append(self.console)
        
#    if system.python_version() <= (2,4,0,'',0):
#        raise VersionTooLow('Python', '2.4.0')
                
    def __init__(self):
        self.handlers = []
        self.make_logger()
        self.level = logging.CRITICAL
        self.debug = self.logger.debug # low importance debugging messages
        self.log = self.logger.info # low importance info messages
        self.warning = self.logger.warning # medium importance warning messages
        self.critical = self.logger.critical # high importance error messages
        self.app = None

    def set_logfile(self, f):
        """set_logfile(file) -> None. Redirects debugging
        output to file."""
        try:
            handler = logging.handlers.RotatingFileHandler(f, maxBytes=1024*1024, 
                                                           backupCount=5)
            handler.setFormatter(self.format)
            handler.setLevel(logging.DEBUG)
            if self.fhandler:
                self.logger.removeHandler(self.fhandler)
            self.fhandler = handler
            self.logger.addHandler(handler)

        except Exception, e:
            self.critical("Could not set log file %s: %s"%(f,str(e)))

    def set_stream(self, stream):
        """set_stream(stream) -> None. Redirects debugging
        output to a stream object."""
        try:
        #then we define a handler to log to the console
            format = logging.Formatter('%(levelname)s: %(message)s')
            handler = logging.StreamHandler(stream)
            handler.setFormatter(format)
            handler.setLevel(self.level)
            self.handlers.append(handler)
            self.logger.addHandler(handler)
        except Exception, e:
            self.critical("Could not set stream %s: %s"%(stream,str(e)))
            
    def set_message_level(self,level):
        """self.set_message_level(level) -> None. Sets the logging
        verboseness.  level must be one of (DebugPrint.Critical,
        DebugPrint.Warning, DebugPrint.Log)."""
        self.level = level
        [h.setLevel(level) for h in self.handlers]

    def register_splash(self, app):
        """ Registers a method splashMessage(message)
        """
        self.app = app

    def splashMessage(self, msg):
        """ Writes a splashmessage if app is registered
        """
        if self.app:
            self.app.splashMessage(msg)

    
splashMessage = DebugPrint.getInstance().splashMessage
critical = DebugPrint.getInstance().critical
warning  = DebugPrint.getInstance().warning
log      = DebugPrint.getInstance().log
debug    = DebugPrint.getInstance().debug

################################################################################

def timecall(method):
    """timecall is a method decorator that wraps any call in timing calls
    so we get the total time taken by a function call as a debugging message."""
    def call(self, *args, **kwargs):
        caller = inspect.currentframe().f_back
        start = time.time()
        method(self, *args, **kwargs)
        end = time.time()
        critical("time: %.5s" % (end-start))
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
