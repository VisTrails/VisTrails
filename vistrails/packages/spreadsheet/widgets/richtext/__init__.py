################################################################################
# RichText plugin for VisTrails Spreadsheet
################################################################################
from richtext import RichTextCell

################################################################################

def widgetName():
    """ widgetName() -> str
    Return the name of this widget plugin
    
    """
    return 'HTML Viewer'

def registerWidget(reg, basicModules, basicWidgets):    
    """ registerWidget(reg: module_registry,
                       basicModules: python package,
                       basicWidgets: python package) -> None
    Register all widgets in this package to VisTrails module_registry
    
    """
    reg.addModule(RichTextCell)
    reg.addInputPort(RichTextCell, "Location", basicWidgets.CellLocation)
    reg.addInputPort(RichTextCell, "File", basicModules.File)
