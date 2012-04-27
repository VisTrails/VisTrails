# VisTrails module imports
from core.modules.vistrails_module import Module


class SheetReference(Module):
    """A reference to a specific sheet, or to any sheet.
    """
    def __init__(self, name=None):
        super(SheetReference, self).__init__()
        self.name = name

    def compute(self):
        name = self.forceGetInputFromPort('sheet', None)
        self.setResult('reference', SheetReference(name))


class CellLocation(Module):
    """The position of a cell in any sheet.
    """
    def __init__(self, row=None, column=None):
        super(CellLocation, self).__init__()
        self.row = row
        self.column = column

    def compute(self):
        row = self.forceGetInputFromPort('row', None)
        column = self.forceGetInputFromPort('column', None)
        self.setResult('location', CellLocation(row, column))
