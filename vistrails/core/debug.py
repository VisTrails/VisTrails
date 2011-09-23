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
import logging
import logging.handlers
import inspect
import os
import os.path
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
        self.format = logging.Formatter("%(asctime)s %(levelname)s:\n%(message)s")
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
        self.app = None

    def set_logfile(self, f):
        """set_logfile(file) -> None. Redirects debugging
        output to file."""
        def rotate_file_if_necessary(filename):
            statinfo = os.stat(filename)
            if statinfo.st_size > 1024*1024:
                #rotate file
                mincount = 1
                maxcount = 5
                count = maxcount
                newfile = "%s.%s"%(filename, count)
                while not os.path.exists(newfile) and count >= mincount:
                    count = count - 1
                    newfile = "%s.%s"%(filename, count)
                if count == 5:
                    os.unlink("%s.%s"%(filename, count))
                    count = 4
                while count >= mincount:
                    os.rename("%s.%s"%(filename, count), "%s.%s"%(filename, count+1))
                    count = count -1
                os.rename(filename, "%s.%s"%(filename, mincount))
        
        try:
            # there's a problem on Windows with RotatingFileHandler and that 
            # happens when VisTrails starts child processes (it seems related
            # to the way Windows manages file handlers)
            # see http://bugs.python.org/issue4749
            # in this case we will deal with log files differently on Windows:
            # we will check if we need to rotate the file at the beginning of 
            # the session.
            import core.system
            if core.system.systemType in ["Windows", "Microsoft"]:
                if not os.path.exists(f):
                    open(f,'w').close()
                rotate_file_if_necessary(f)
                handler = logging.FileHandler(f)
            else:
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
            format = logging.Formatter('%(levelname)s\n%(asctime)s\n%(message)s')
            handler = logging.StreamHandler(stream)
            handler.setFormatter(format)
            handler.setLevel(self.level)
            self.handlers.append(handler)
            self.logger.addHandler(handler)
        except Exception, e:
            self.critical("Could not set message stream %s: %s"%(stream,str(e)))
            
    def set_message_level(self,level):
        """self.set_message_level(level) -> None. Sets the logging
        verboseness.  level must be one of (DebugPrint.Critical,
        DebugPrint.Warning, DebugPrint.Log)."""
        self.level = level
        [h.setLevel(level) for h in self.handlers]

    def register_splash(self, app):
        """ register_splash(self, classname)
        Registers a method splashMessage(message)
        """
        self.app = app

    def splashMessage(self, msg):
        """ splashMessage(self, string)
        Writes a splashmessage if app is registered
        """
        if self.app:
            self.app.splashMessage(msg)

    def message(self, caller, msg, details=''):
        """self.message(caller, str, str) -> str. Returns a string with a
        formatted message to be send to the debugging output. This
        should not be called explicitly from userland. Consider using
        self.log(), self.warning() or self.critical() instead."""
        msg = (msg + '\n' + details) if details else msg 
        source = inspect.getsourcefile(caller)
        line = caller.f_lineno
        if source and line:
            return source + ", line " + str(line) + "\n" + msg
        else:
            return "(File info not available)\n" + msg
        
    def debug(self, msg, details = ''):
        """self.log(str, str) -> None. Send information message (low
        importance) to log with appropriate call site information."""
        caller = inspect.currentframe().f_back # who called us?
        self.logger.debug(self.message(caller, msg, details))
        
    def log(self, msg, details = ''):
        """self.log(str, str) -> None. Send information message (low
        importance) to log with appropriate call site information."""
        caller = inspect.currentframe().f_back # who called us?
        self.logger.info(self.message(caller, msg, details))
        
    def warning(self, msg, details = ''):
        """self.warning(str, str) -> None. Send warning message (medium
        importance) to log with appropriate call site information."""
        caller = inspect.currentframe().f_back # who called us?
        self.logger.warning(self.message(caller, msg, details))
        
    def critical(self, msg, details = ''):
        """self.critical(str, str) -> None. Send critical message (high
        importance) to log with appropriate call site information."""
        caller = inspect.currentframe().f_back # who called us?
        self.logger.critical(self.message(caller, msg, details))
            
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
