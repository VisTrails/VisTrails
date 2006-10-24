from svg import SVGCell, SVGSplitter

def widgetName():
    return 'SVG Widgets'

def registerWidget(reg, basicModules, basicWidgets):    
    reg.addModule(SVGCell)
    reg.addInputPort(SVGCell, "Location", basicWidgets.CellLocation)
    reg.addInputPort(SVGCell, "File", basicModules.File)

    reg.addModule(SVGSplitter)
    reg.addInputPort(SVGSplitter, "File", basicModules.File)
