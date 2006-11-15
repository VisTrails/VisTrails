################################################################################
# ImageViewer plugin for VisTrails Spreadsheet
################################################################################
from imageviewer import ImageViewerCell

################################################################################

def widgetName():
    """ widgetName() -> str
    Return the name of this widget plugin
    
    """
    return 'Image Viewer'

def registerWidget(reg, basicModules, basicWidgets):
    """ registerWidget(reg: module_registry,
                       basicModules: python package,
                       basicWidgets: python package) -> None
    Register all widgets in this package to VisTrails module_registry
    
    """
    reg.addModule(ImageViewerCell)
    reg.addInputPort(ImageViewerCell, "Location", basicWidgets.CellLocation)
    reg.addInputPort(ImageViewerCell, "File", basicModules.File)    
