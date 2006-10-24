import modules
import modules.basic_modules
import modules.module_registry
from modules.vistrails_module import Module
from spreadsheet_window import SpreadsheetWindow
from spreadsheet_registry import spreadsheetRegistry

def importReturnLast(name):
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod

def addWidget(packageName, reg, basicModules, basicWidgets):
    try:
        widget = importReturnLast(packageName)
        if hasattr(widget, 'widgetName'):
            widgetName = widget.widgetName()
        else:
            widgetName = packageName
        widget.registerWidget(reg, basicModules, basicWidgets)
        spreadsheetRegistry.registerPackage(widget, packageName)
        print '  ==> Successfully import <%s>' % widgetName
    except:
        widget = None
    return widget

def importWidgetModules(basicWidgets):
    import os, string
    import system
    widgetDir = system.visTrailsRootDirectory()+'/'+string.replace(__name__, '.', '/')+'/widgets/'
    candidates = os.listdir(widgetDir)
    for folder in candidates:
        if os.path.isdir(widgetDir+folder) and folder!='CVS':
            addWidget('packages.spreadsheet.widgets.'+folder,
                      modules.module_registry,
                      modules.basic_modules,
                      basicWidgets)

def initialize(*args, **keywords):

    print 'Loading Spreadsheet widgets...'
    basicWidgets = addWidget('packages.spreadsheet.basic_widgets',
                             modules.module_registry,
                             modules.basic_modules,
                             None)
    importWidgetModules(basicWidgets)
    global spreadsheetWindow
    spreadsheetWindow = SpreadsheetWindow()
    spreadsheetWindow.configShow()
