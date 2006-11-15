################################################################################
# This file contains the spreadsheet registry:
#   SpreadsheetRegistry
################################################################################

class SpreadsheetRegistry(object):
    """
    SpreadsheetRegistry is the class holding information about cell and sheet
    types. Each sheet name will only have one sheet type associated with it
    
    """
    def __init__(self):
        """ SpreadsheetRegistry() -> SpreadsheetRegistry
        Initialize the registry with no member
        
        """
        self.packages = {}
        self.sheets = {}

    def registerPackage(self, package, name):
        """ registerPackage(package: python package, name: str) -> None
        Register a package containing spreadsheet widgets to the spreadsheet
        
        """
        self.packages[package] = name

    def unregisterPackage(self, package):
        """ unregisterPackage(package: python package) -> None
        Unregister a package out of the spreadsheet
        
        """
        if self.packages.has_key(package):
            del self.packages[package]

    def registerSheet(self, name, sheetType):
        """ registerSheet(name: str, sheetType: type) -> None
        Register a name for a sheet type
        
        """
        self.sheets[name] = sheetType
        
    def unregisterSheet(self, name):
        """ unregisterSheet(name: str) -> None
        Unregister a named sheet type
        
        """
        if self.sheets.has_key(name):
            del self.sheets[name]

    def getSheet(self, name):
        """ getSheet(name: str) -> type
        Return the type of sheet with the corresponding name
        
        """
        if self.sheets.has_key(name):            
            return self.sheets[name]
        else:
            return None

    def getSheetByType(self, type):
        """ getSheetByType(type) -> name
        Return the name of sheet with the corresponding type
        
        """
        for (n,t) in self.sheets.items():
            if t==type:
                return n
        return None
        
spreadsheetRegistry = SpreadsheetRegistry()
