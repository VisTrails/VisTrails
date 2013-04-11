from vistrails.core.modules.vistrails_module import Module
from vistrails.core.modules.module_registry import get_module_registry
from vistrails.core.modules.basic_modules import String, Variant, List

import socket

from ipython_set import IPythonSet, QWarningDialog, QAddEnginesDialog

from map import Map

ipythonSet = None
profile_dir = None


def initialize(*args,**keywords):
    reg = get_module_registry()

    reg.add_module(Map)
    reg.add_input_port(Map, 'FunctionPort', (Module, ""))
    reg.add_input_port(Map, 'InputList', (List, ""))
    reg.add_input_port(Map, 'InputPort', (List, ""))
    reg.add_input_port(Map, 'OutputPort', (List, ""))
    reg.add_output_port(Map, 'Result', (Variant, ""))
    
#################################################################################

def start_local_controller():
    """
    Starts a local IPython controller.
    """
    global ipythonSet, profile_dir
    
    if not ipythonSet:
        ip = socket.gethostbyname(socket.gethostname())
        ipythonSet = IPythonSet(ip)
        profile_dir = ipythonSet.profile_dir
        
        
def add_engines(engine_type):
    """
    Adds engines to an IPython set.
    """
    global ipythonSet, profile_dir
    
    def add_engines_ipython_set(engine_type):
        n_engines = 0
        engines_widget = QAddEnginesDialog()
        if engines_widget.exec_():
            try:
                n_engines = int(engines_widget.get_answer())
            except:
                 warning_widget = QWarningDialog("Invalid number of engines: '%s'" %engines_widget.get_answer(),
                                                 button_cancel=False)
                 warning_widget.exec_()
            ipythonSet.add_engines(n=n_engines,
                                   engine_type=engine_type)
    
    if not ipythonSet:
        start_local_controller()
        add_engines_ipython_set(engine_type)
    else:
        if (ipythonSet.engine_type != engine_type) and (ipythonSet.engine_type != None):
            warning_widget = QWarningDialog("Existing engines are of type '%s'." %ipythonSet.engine_type,
                                            button_cancel=False)
            warning_widget.exec_()
        else:
            add_engines_ipython_set(engine_type)
            

def add_local_engines():
    """
    Adds local engines in the IPython set.
    """
    add_engines('local')
       
       
def add_ssh_engines():
    """
    Adds SSH engines in the IPython set.
    """
    add_engines('ssh')
        
        
def restart_engines():
    """
    Restarts the engines.
    """
    global ipythonSet, profile_dir
    
    if not ipythonSet:
        warning_widget = QWarningDialog('No engines have been started.',
                                        button_cancel=False)
        warning_widget.exec_()
    else:
        ipythonSet.restart_controller()
        ipythonSet.restart_engines()
        
    
def stop_controller():
    """
    Stops the controller.
    Note that stopping the controller also stops the engines and clear the set!
    """
    global ipythonSet, profile_dir
    
    if not ipythonSet:
        warning_widget = QWarningDialog('No engines found.',
                                        button_cancel=False)
        warning_widget.exec_()
    else:
        ipythonSet.stop_engines()
        ipythonSet.stop_controller()
        ipythonSet = None
        profile_dir = None
        

def menu_items():
    """menu_items() -> tuple of (str,function)
    It returns a list of pairs containing text for the menu and a
    callback function that will be executed when that menu item is selected.
    
    """
    lst = []
    lst.append(("Add Local Engines", add_local_engines))
    lst.append(("Add SSH Engines", add_ssh_engines))
    lst.append(("Restart Engines", restart_engines))
    lst.append(("Stop Engines", stop_controller))
    return tuple(lst)