################################################################################
# SVG plugin for VisTrails Spreadsheet
################################################################################
from svg import SVGCell, SVGSplitter

################################################################################

def widgetName():
    """ widgetName() -> str
    Return the name of this widget plugin
    
    """
    return 'SVG Widgets'

def registerWidget(reg, basicModules, basicWidgets):    
    """ registerWidget(reg: module_registry,
                       basicModules: python package,
                       basicWidgets: python package) -> None
    Register all widgets in this package to VisTrails module_registry
    
    """
    reg.addModule(SVGCell)
    reg.addInputPort(SVGCell, "Location", basicWidgets.CellLocation)
    reg.addInputPort(SVGCell, "File", basicModules.File)

    reg.addModule(SVGSplitter)
    reg.addInputPort(SVGSplitter, "File", basicModules.File)
