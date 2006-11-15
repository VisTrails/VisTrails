################################################################################
# VTK plugin for VisTrails Spreadsheet
################################################################################
from QVTKWidget import VTKCell

################################################################################

def widgetName():    
    """ widgetName() -> str
    Return the name of this widget plugin
    
    """
    return 'VTK Viewer'

def registerWidget(reg, basicModules, basicWidgets):
    """ registerWidget(reg: module_registry,
                       basicModules: python package,
                       basicWidgets: python package) -> None
    Register all widgets in this package to VisTrails module_registry
    
    """
    reg.addModule(VTKCell)
    reg.addInputPort(VTKCell, "Location", basicWidgets.CellLocation)
    reg.addInputPort(VTKCell, "AddRenderer", reg.registry.getDescriptorByName('vtkRenderer').module)
