############################################################################
##
## Copyright (C) 2006-2007 University of Utah. All rights reserved.
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
""" This file specifies the configuration widget for Tuple
module. This should be used as a template for creating a configuration
for other modules. The widget here should inherit from
core.modules.module_configure.StandardModuleConfigurationWidget, which
is also a QWidget.

"""
from PyQt4 import QtCore, QtGui
from core.modules.module_configure import StandardModuleConfigurationWidget, \
     PortTable
from core.modules.module_registry import registry
from core.utils import any

############################################################################
class TupleConfigurationWidget(StandardModuleConfigurationWidget):
    """
    TupleConfigurationWidget is the configuration widget for Tuple
    module, we want to build an interface for specifying a number of
    input ports and the type of each port. Then compose a tuple of
    those input as a result.

    When subclassing StandardModuleConfigurationWidget, there are
    only a few things we care about:
    
    1) The builder will provide the VistrailController (through the
       constructor) associated with the pipeline the module is in. The
       configuration widget can use the controller to change the
       current vistrail such as delete connections, add/delete module
       port...

    2) The builder also provide the current Module object (through the
       constructor) of the module. This is the instance of the module
       in the pipeline. Changes to this Module object usually will not
       result a new version in the current Vistrail. Such changes are
       change the visibility of input/output ports on the builder,
       change module color.

       Each module has a local registry which is exactly like the
       global modules.module_registry.registry. However, it holds
       module information (ports) changing in time. The same module
       can have different types of input ports at two different time
       in the same vistrail.

    3) After updating the controller and finish the configuration,
       remember to emit the signal 'doneConfigure()' (if the module
       has been modified) so that the builder can update itself to
       reflect the new controller and module

    That's it, the rest of the widget will be just like a regular Qt
    widget.
    
    """
    def __init__(self, module, controller, parent=None):
        """ MplPlotConfigurationWidget(module: Module,
                                       controller: VistrailController,
                                       parent: QWidget)
                                       -> MplPlotConfigurationWidget                                       
        Let StandardModuleConfigurationWidget constructor store the
        controller/module object from the builder and set up the
        configuration widget.        
        After StandardModuleConfigurationWidget constructor, all of
        these will be available:
        self.module : the Module object int the pipeline        
        self.moduleThing: the Module type registered in the registry,
                          i.e. Tuple
        self.controller: the current vistrail controller
                                       
        """
        StandardModuleConfigurationWidget.__init__(self, module,
                                                   controller, parent)

        # Give it a nice window title
        self.setWindowTitle('Tuple Configuration')

        # Add an empty vertical layout
        centralLayout = QtGui.QVBoxLayout()
        centralLayout.setMargin(0)
        centralLayout.setSpacing(0)
        self.setLayout(centralLayout)
        
        # Then add a PortTable to our configuration widget
        self.portTable = PortTable(self)
        self.portTable.setHorizontalHeaderLabels(
            QtCore.QStringList() << 'Input Port Name' << 'Type')
        
        # We know that the Tuple module initially doesn't have any
        # input port, we just use the local registry to see what ports
        # it has at the time of configuration.
        if self.module.registry:
            iPorts = self.module.registry.destinationPorts(
                self.moduleThing)
            self.portTable.initializePorts(iPorts)
        else:
            self.portTable.fixGeometry()
        centralLayout.addWidget(self.portTable)

        # We need a padded widget to take all vertical white space away
        paddedWidget = QtGui.QWidget(self)
        paddedWidget.setSizePolicy(QtGui.QSizePolicy.Ignored,
                                   QtGui.QSizePolicy.Expanding)
        centralLayout.addWidget(paddedWidget, 1)

        # Then we definitely need an Ok & Cancel button
        self.createButtons()

    def createButtons(self):
        """ createButtons() -> None
        Create and connect signals to Ok & Cancel button
        
        """
        self.buttonLayout = QtGui.QHBoxLayout()
        self.buttonLayout.setMargin(5)
        self.okButton = QtGui.QPushButton('&OK', self)
        self.okButton.setAutoDefault(False)
        self.okButton.setFixedWidth(100)
        self.buttonLayout.addWidget(self.okButton)
        self.cancelButton = QtGui.QPushButton('&Cancel', self)
        self.cancelButton.setAutoDefault(False)
        self.cancelButton.setShortcut('Esc')
        self.cancelButton.setFixedWidth(100)
        self.buttonLayout.addWidget(self.cancelButton)
        self.layout().addLayout(self.buttonLayout)
        self.connect(self.okButton, QtCore.SIGNAL('clicked(bool)'),
                     self.okTriggered)
        self.connect(self.cancelButton, QtCore.SIGNAL('clicked(bool)'),
                     self.close)        

    def sizeHint(self):
        """ sizeHint() -> QSize
        Return the recommended size of the configuration window
        
        """
        return QtCore.QSize(384, 256)

    def okTriggered(self, checked = False):
        """ okTriggered(checked: bool) -> None
        Update vistrail controller and module when the user click Ok
        
        """
        self.updateVistrail()
        self.emit(QtCore.SIGNAL('doneConfigure()'))
        self.close()

    def newInputPorts(self):
        """ newInputPorts() -> [port]        
        Return the set of ports specify in the port table
        
        """
        ports = []
        for i in range(self.portTable.rowCount()):
            model = self.portTable.model()
            name = str(model.data(model.index(i, 0),
                                  QtCore.Qt.DisplayRole).toString())
            typeName = str(model.data(model.index(i, 1),
                                      QtCore.Qt.DisplayRole).toString())
            if name!='' and typeName!='':
                ports.append(('input', name, '('+typeName+')'))
        return ports

    def registryChanges(self, newPorts):
        """ registryChanges(ports: [port]) -> (deletePorts, addPorts)        
        Check the module registry to see if we need to delete or add
        which ports
        
        """
        if self.module.registry:
            dstPorts = self.module.registry.destinationPorts(self.moduleThing)
            oldIn = [('input', p.name,
                      '('+registry.getDescriptorByThing(p.spec[0][0][0]).name+
                      ')') for p in dstPorts[0][1]]
        else:
            oldIn = []
        deletePorts = [p for p in oldIn if not p in newPorts]
        addPorts = [p for p in newPorts
                    if (not p in oldIn)]
        return (deletePorts, addPorts)
    
    def updateVistrail(self):
        """ updateVistrail() -> None
        Update Vistrail to contain changes in the port table
        
        """
        newPorts = self.newInputPorts()
        (deletePorts, addPorts) = self.registryChanges(newPorts)

        # Remove all deletePorts and its connection
        for (cid, c) in self.controller.currentPipeline.connections.items():
            if ((c.sourceId==self.module.id and
                 any([c.source.name==p[1] for p in deletePorts])) or
                (c.destinationId==self.module.id and
                 any([c.destination.name==p[1] for p in deletePorts]))):
                self.controller.deleteConnection(cid)
        for p in deletePorts:
            self.controller.deleteModulePort(self.module.id, p)

        # Add all addPorts
        for p in addPorts:
            self.controller.addModulePort(self.module.id, p)

        # If output spec change, remove all connections
        prevPortSpec = self.module.registry.getOutputPortSpec(self.module, 'value')
        if prevPortSpec:
            prevPortSpec = [registry.getDescriptor(p[0]).name for p in prevPortSpec[0]]
        spec = [p[2][1:-1] for p in newPorts]
        if prevPortSpec!=spec:
            for (cid, c) in self.controller.currentPipeline.connections.items():
                if (c.sourceId==self.module.id and c.source.name=='value'):
                    self.controller.deleteConnection(cid)

        # Remove the current output port and add a new one                    
        self.controller.deleteModulePort(self.module.id, ('output', 'value'))
        self.moduleThing.INPUTPORTS = [p[1] for p in newPorts]
        spec = '('+','.join(spec)+')'
        self.controller.addModulePort(self.module.id,
                                      ('output', 'value', spec))
