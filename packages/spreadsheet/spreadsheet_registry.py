################################################################################
################################################################################
### SpreadsheetRegistry: information lookup for the whole spreadsheet
class SpreadsheetRegistry(object):

    ### Initialize the registry
    def __init__(self):
        self.packages = {}
        self.sheets = {}

    ### Register a package containing widgets to the spreadsheet
    def registerPackage(self, package, name):
        self.packages[package] = name

    ### Unregister a package containing widgets of the spreadsheet
    def unregisterPackage(self, package):
        if self.packages.has_key(package):
            del self.packages[package]

    ### Register sheet type for each name
    def registerSheet(self, name, sheetType):
        self.sheets[name] = sheetType
        
    ### Unregister sheet type for each name
    def unregisterSheet(self, name):
        if self.sheets.has_key(name):
            del self.sheets[name]

    ### Return the type of sheet for the corresponding name
    def getSheet(self, name):
        if self.sheets.has_key(name):            
            return self.sheets[name]
        else:
            return None

    ### Return the name of sheet for the corresponding type
    def getSheetByType(self, type):
        for (n,t) in self.sheets.items():
            if t==type:
                return n
        return None
        
spreadsheetRegistry = SpreadsheetRegistry()
