import core.modules.module_registry
import core.modules.vistrails_module
from logging import debug, warn
from core.vistrail.connection import Connection
from core.vistrail.port import Port
from PyQt4 import QtGui, QtCore
import api
import vcs
import os

cdat_id = "edu.utah.sci.vistrails.cdat"

# Module names
# Note: open_name, quickplot_name, etc... are used in cdat_window.py
# and graphics_method_controller.py
open_name = 'open'
quickplot_name = 'Quickplot'
variable_name = 'Variable'
cdatcell_name = 'CDATCell'
gm_name = 'GraphicsMethod'

# Port names


# Module Namespaces
namespace = {}
namespace[open_name] = 'cdms2'
namespace[quickplot_name] = 'cdat'
namespace[variable_name] = 'cdat'
namespace[cdatcell_name] = 'cdat'
namespace[gm_name] = 'cdat'

# MAJOR TODO: Support for multiple workflows

class Workflow():
    """ A Workflow contains a dict of modules belonging to the workflow. Workflow
    manages the updating of its modules connections / values """
    
    def __init__(self):
        """ Workflow contains a dictionary of modules in the workflow.
        * Key - if module is a variable then the key is the name of the variable
        otherwise the key is the name of the module. ***** IMPORTANT *****
        * Value - module object
        """
        self.modules = {}
        self.variableNames = [] # Names of the variables in this workflow
        self.filename = None # Name of the cdms file associated with this workflow
        
    def moduleExists(self, key):
        return key in list(self.modules)

    def addModule(self, name, module, isVariable=False):
        self.modules[name] = module

        # If the module is a variable save the name and connect the variable
        # module to the open module
        if isVariable:
            self.variableNames.append(name)
            self.connectPorts(self.modules[open_name], 'dataset', module,
                              'cdmsfile')

    def updatePorts(self, var1, var2):
        """ updatePorts(var1: str, var2: str)

        updatePorts connects the output ports of Variable modules with vars
        var1 and var2 to the input ports of Graphics Method and then connects
        the output of Graphics Method to the input of CDATCell.
        """
        m_open = self.modules[open_name]
        m_variable1 = self.modules[var1]
        m_gm = self.modules[gm_name]
        m_cdatcell = self.modules[cdatcell_name]

        # Connect the variable module being plotted to the graphics method
        # module and store the connection
        self.connectPorts(m_variable1, 'variable', m_gm, 'slab1')

        # Connect graphics method module & cdatcell module
        self.connectPorts(m_gm, 'canvas', m_cdatcell, 'canvas')
        self.connectPorts(m_gm, 'slab1', m_cdatcell, 'slab1')

        # Connect the second variable module (if given) to graphics method
        # and Graphics Method to CDATCell
        if var2 is not None:
            m_var2 = self.modules[var2]
            self.connectPorts(m_var2, 'variable', m_gm, 'slab2')
            self.connectPorts(m_gm, 'slab2', m_cdatcell, 'slab2')

    def connectPorts(self, moduleA, outputPortName, moduleB, inputPortName):
        """ connectPorts(moduleA: Module, outputPortName: str, moduleB: Module,
                         inputPortName: str) -> Connection
                         
        connectPorts connects moduleA's outputPort to moduleB's inputPort.
        """
        reg = api.get_module_registry()
        in_port = moduleA.get_port_spec(outputPortName, 'output')
        out_port = moduleB.get_port_spec(inputPortName, 'input')

        return api.add_connection(moduleA.id, outputPortName, moduleB.id,
                                  inputPortName)

    def updateModule(self, name, portName, value):
        """ updateModule(name: str, portName: str, value: *)

        updateModule updates the vistrail module given the module name, input
        port name, and value
        """
        if name not in list(self.modules):
            return

        # Set the filename associated w/ this workflow
        if name == open_name:
            self.filename = value
        
        module = self.modules[name]
        api.get_current_controller().update_function(module, portName, [value])

    def updateModuleOps(self, name, args):
        """ updateModule(name: str, args: list)

        updateModule updates the vistrail module given the module name and a
        list of tuples where each tuple = (input port name, value)
        """
        if name not in list(self.modules):
            return
        
        module = self.modules[name]
        for portName, value in args:
            api.get_current_controller().update_function(module, portName,
                                                         [value])

class GuiController(QtCore.QObject):
    """ GuiController calls vistrails functions and handles recording and
    displaying teaching commands.

    The two most important functions that GuiController provides are:
    'createModule' and 'updateModule'.  'createModule' creates a new box.
    'updateModule' updates the input of a box.  Widgets interact with
    GuiController by sending signals (which is why GuiController inherits
    from QObject).
    """

    def __init__(self, fileWidget, defVarWidget, varWidget):
        """ __init__(fileWidget: QCDATFileWidget, defVarWidget:QDefinedVariable,
                     varWidget: QVariableView)
        """
        QtCore.QObject.__init__(self)
        self.teachingCommands = ''
        self.editorPid = 0
        self.recordCommands = True

        self.workflows = [] # List of workflows

        # X coordinates of open, variable, and plot related modules
        self.openX = -300
        self.variableX = -300
        self.plotX = -320
        
        self.m_open = None 
        self.m_variable = None 
        self.m_graphics_method = None 
        self.m_cdat_cell = None

        # Connect the 3 main widgets to the primary GuiController
        # functionality.  If a childwidget of the 3 main widgets wants to
        # send signals to GuiController, then it must send it through one of the
        # main widgets to try to keep things less messy
        self.connect(fileWidget, QtCore.SIGNAL('createModule'),
                     self.createModule)            
        self.connect(fileWidget, QtCore.SIGNAL('updateModule'),
                     self.updateModule)
        self.connect(fileWidget, QtCore.SIGNAL('recordTeachingCommand'),
                     self.recordTeachingCommand)        

        self.connect(defVarWidget, QtCore.SIGNAL('createModule'),
                     self.createModule)            
        self.connect(defVarWidget, QtCore.SIGNAL('updateModule'),
                     self.updateModule)
        self.connect(defVarWidget, QtCore.SIGNAL('recordTeachingCommand'),
                     self.recordTeachingCommand)                

        self.connect(varWidget, QtCore.SIGNAL('recordTeachingCommand'),
                     self.recordTeachingCommand)                
        self.connect(varWidget, QtCore.SIGNAL('createModule'),
                     self.createModule)
        self.connect(varWidget, QtCore.SIGNAL('updateModule'),
                     self.updateModule)
        self.connect(varWidget, QtCore.SIGNAL('updateModuleOps'),
                     self.updateModuleOps)
        self.connect(varWidget, QtCore.SIGNAL('plot'),
                     self.plot)

    def createNewWorkflow(self):
        """ createnewWorkflow(filename: str)

        createNewWorkflow is called when the user selects a new file. It makes
        a new workflow and appends it to the workflow list.
        """
        if self.workflows == []:
            api.get_current_controller().change_selected_version(0)
        
        self.currentWorkflow = Workflow()
        self.workflows.append(self.currentWorkflow)

    def getCoordinates(self, name):
        """ getCoordinates(name: str) -> x: int, y: int

        Return the x, y coordinate of where to place the new module given the
        name.
        """
        if name == open_name: 
            self.openX += 100
            return self.openX, 170
        elif name == variable_name or name == quickplot_name:
            self.variableX += 120
            return self.variableX, 70
        elif name == gm_name:
            self.plotX += 160
            return self.plotX, -70
        elif name == cdatcell_name:
            return self.plotX, -170

    def createModule(self, name, key=None):
        """ createModule(name: str, key: str)

        createModule creates a new module given the name and adds it to the
        current workflow.  If key is specified, use the key instead of the name
        as the key into the workflow's module dictionary.

        Note: For Variable modules I pass key = variabe name (the tabName)
        """
        # If module is the 'open' module, create a new workflow
        if name == open_name:
            self.createNewWorkflow()
            
        # If module is 'quickplot' module, and it already exists, do nothing
        if name == quickplot_name:
            if self.currentWorkflow.moduleExists(quickplot_name.lower()):
                return

        # Create & add the module
        x, y = self.getCoordinates(name)
        module = api.add_module(x, y, cdat_id, name, namespace[name])
        
        if key is not None:
            self.currentWorkflow.addModule(key, module, isVariable=True)
        else:
            self.currentWorkflow.addModule(name, module)

    def updateModule(self, name, portName, value):
        """ updateModule(name: str, portName: str, value: *)

        updateModule updates the vistrail module given the module name, input
        port name, and value
        """
        self.currentWorkflow.updateModule(name, portName, value)

    def updateModuleOps(self, name, args):
        """ updateModule(name: str, args: list)

        updateModule updates the vistrail module given the module name and a
        list of tuples where each tuple = (input port name, value)
        """
        self.currentWorkflow.updateModuleOps(name, args)

    def plot(self, var1, var2):
        """ Connect / disconnect the necessary ports and exec workflow -> plot
        into the cell
        """
        self.currentWorkflow.updatePorts(var1, var2)
        api.get_current_controller().execute_current_workflow()

    def initTeachingCommands(self):
        """  The initial teaching commands still have 4 canvases like the old
        vcdat.  This allows you to run the teaching commands independently
        of vistrails' spreadsheets.
        """
        self.teachingCommands += 'import cdms2, vcs, cdutil, genutil, os, sys\n'
        self.teachingCommands += 'import MV2\n'

        self.teachingCommands += '\n# Initialize the four VCS Canvases by creating\n'
        self.teachingCommands += '# a list to hold the 4 VCS Canvas\n'
        self.teachingCommands += 'vcs_canvas_list = []\n'

        self.teachingCommands += '\n# Loop (from 0 to 3) to create VCS Canvas 1, 2, 3, and 4\n'
        self.teachingCommands += 'for i in range(4):\n'
        self.teachingCommands += '    vcs_canvas_list.append(vcs.init())\n'

        self.teachingCommands += '\n# Set the Command Line VCS Canvas hooks\n'
        self.teachingCommands += 'vcs_hook1 = vcs_canvas_list[0]\n'
        self.teachingCommands += 'vcs_hook2 = vcs_canvas_list[1]\n'
        self.teachingCommands += 'vcs_hook3 = vcs_canvas_list[2]\n'
        self.teachingCommands += 'vcs_hook4 = vcs_canvas_list[3]\n'

        self.writeTeachingCommands()

    def recordTeachingCommand(self, command):
        if (self.recordCommands == True):
            self.teachingCommands += command
            self.writeTeachingCommands()

    def setRecordCommands(self, recordCommands):
        self.recordCommands = recordCommands

    def writeTeachingCommands(self):
        try:
            fn = '%s/PCMDI_GRAPHICS' % os.environ['HOME']
        except:
            print "Could not find the $HOME directory. Set your environment variable 'HOME'"
            print "to your home directory. (e.g., 'setenv HOME /home/user')."
            sys.exit()
        
        # Create PCMDI_GRAPHICS directory if it does not exist                                  
        if (os.access(fn, os.X_OK) == 0):
            try:
                os.mkdir(fn)
            except:
                print 'Do not have write permission for home directory. Must have write permissions.'
                sys.exit()

        # Write teaching commands to vcdat_recording_script_file.py
        self.teachingScript = fn + '/vcdat_recording_script_file.py'
        file = open(self.teachingScript, 'w')
        file.write(self.teachingCommands)
        file.flush()

    def viewTeachingCommands(self):
        """ Open the teaching commands script in a child process """
        self.editorPid = os.fork()

        if (self.editorPid == 0):
            editor = 'idle'

            # If idle editor is found, view teaching commands with idle
            for path in os.environ["PATH"].split(os.pathsep):
                file = os.path.join(path, editor)
                if (os.path.exists(file)):
                    args = (editor, self.teachingScript)
                    os.execvp(editor, args)
                    return

            # If idle editor is not found, use default editor
            secondaryEditor = os.environ['EDITOR']
            args = (secondaryEditor, self.teachingScript)
            os.execvp(secondaryEditor, args)

    def closeTeachingCommands(self):
        if (self.editorPid != 0):
            os.kill(self.editorPid, 9)
            self.editorPid = 0
