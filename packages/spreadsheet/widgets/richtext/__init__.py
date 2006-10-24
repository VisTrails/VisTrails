from richtext import RichTextCell

def widgetName():
    return 'HTML Viewer'

def registerWidget(reg, basicModules, basicWidgets):    
    reg.addModule(RichTextCell)
    reg.addInputPort(RichTextCell, "Location", basicWidgets.CellLocation)
    reg.addInputPort(RichTextCell, "File", basicModules.File)
