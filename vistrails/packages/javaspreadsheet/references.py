# VisTrails module imports
from vistrails.core.modules.vistrails_module import Module


class SheetReference(Module):
    """A reference to a specific sheet, or to any sheet.
    """
    def __init__(self, name=None):
        super(SheetReference, self).__init__()
        self.name = name

    def compute(self):
        name = self.force_get_input('sheet', None)
        self.set_output('reference', SheetReference(name))


class CellLocation(Module):
    """The position of a cell in any sheet.
    """
    def __init__(self, row=None, column=None):
        super(CellLocation, self).__init__()
        self.row = row
        self.column = column

    def compute(self):
        row = self.force_get_input('row', None)
        column = self.force_get_input('column', None)
        self.set_output('location', CellLocation(row, column))
