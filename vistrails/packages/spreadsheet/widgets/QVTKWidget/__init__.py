from QVTKWidget import VTKCell

def widgetName():    
    return 'VTK Viewer'

def registerWidget(reg, basicModules, basicWidgets):
    reg.addModule(VTKCell)
    reg.addInputPort(VTKCell, "Location", basicWidgets.CellLocation)
    reg.addInputPort(VTKCell, "AddRenderer", reg.registry.getDescriptorByName('vtkRenderer').module)
