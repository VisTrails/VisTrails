from imageviewer import ImageViewerCell

def widgetName():    
    return 'Image Viewer'

def registerWidget(reg, basicModules, basicWidgets):
    reg.addModule(ImageViewerCell)
    reg.addInputPort(ImageViewerCell, "Location", basicWidgets.CellLocation)
    reg.addInputPort(ImageViewerCell, "File", basicModules.File)    
