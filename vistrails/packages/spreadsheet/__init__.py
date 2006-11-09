from core.modules.vistrails_module import Module
from spreadsheet_registry import spreadsheetRegistry
from spreadsheet_window import SpreadsheetWindow
import core.modules
import core.modules.basic_modules
import core.modules.module_registry
import core.system

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
    widgetDir = core.system.visTrailsRootDirectory()+'/'+string.replace(__name__, '.', '/')+'/widgets/'
    candidates = os.listdir(widgetDir)
    for folder in candidates:
        if os.path.isdir(widgetDir+folder) and folder!='.svn':
            addWidget(__name__+'.widgets.'+folder,
                      core.modules.module_registry,
                      core.modules.basic_modules,
                      basicWidgets)

def initialize(*args, **keywords):

    print 'Loading Spreadsheet widgets...'
    basicWidgets = addWidget('packages.spreadsheet.basic_widgets',
                             core.modules.module_registry,
                             core.modules.basic_modules,
                             None)
    importWidgetModules(basicWidgets)
    global spreadsheetWindow
    spreadsheetWindow = SpreadsheetWindow()
    spreadsheetWindow.configShow()
