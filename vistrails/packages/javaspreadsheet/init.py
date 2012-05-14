# VisTrails module imports
from core.modules.vistrails_module import Module
from core.modules.module_registry import get_module_registry
from core.modules import basic_modules

from component import Component
from spreadsheet import Spreadsheet
from references import SheetReference, CellLocation

from javax.swing import JFrame, JPanel, BoxLayout


# Create a Spreadsheet object where we will store everything
spreadsheet = Spreadsheet()


# Module that allocates a cell to display a Swing component
class AssignCell(Module):
    """Module that allocates a cell to display a Swing component.

    You can also pass in a sheet reference if you want to use a specific sheet,
    and a location in that spreadsheet. If you don't, a cell will be selected
    automatically.
    """
    def compute(self):
        sheetref = self.forceGetInputFromPort('sheet', SheetReference())
        location = self.forceGetInputFromPort('location', CellLocation())
        widgets = self.getInputListFromPort('widget')

        sheet = spreadsheet.getSheet(sheetref)
        cell = sheet.getCell(location)
        cell.removeAll()
        for widget in widgets:
            cell.add(widget)

        spreadsheet.setVisible(True)

        self.setResult('cell', cell)


class Frame(Module):
    """Simple module building a JFrame.

    This module displays a Swing component in a JFrame of its own. It
    doesn't use the spreadsheet.
    """
    def compute(self):
        widgets = self.getInputListFromPort('widget')
        frame = JFrame()
        top = JPanel()
        top.setLayout(BoxLayout(top, BoxLayout.PAGE_AXIS))
        frame.setContentPane(top)
        for widget in widgets:
            top.add(widget)
        frame.pack()
        frame.setVisible(True)


def initialize(*args, **keywords):
    reg = get_module_registry()

    # Modules

    reg.add_module(Component)
    reg.add_input_port(
            Component, 'text',
            (basic_modules.String, "text to be displayed on the component"))
    reg.add_output_port(
            Component, 'component',
            (Component, "a test component"))

    reg.add_module(SheetReference)
    reg.add_input_port(
            SheetReference, 'sheet',
            (basic_modules.String, "name of the sheet to be addressed"))
    reg.add_output_port(
            SheetReference, 'reference',
            (SheetReference, "reference to a sheet"))

    reg.add_module(CellLocation)
    reg.add_input_port(
            CellLocation, 'row',
            (basic_modules.Integer, "row number, >= 0"))
    reg.add_input_port(
            CellLocation, 'column',
            (basic_modules.Integer, "column number, >= 0"))
    reg.add_output_port(
            CellLocation, 'location',
            (CellLocation, "reference to a cell location on a sheet"))

    reg.add_module(AssignCell)
    reg.add_input_port(
            AssignCell, 'sheet',
            (SheetReference, "reference to the sheet to be used"))
    reg.add_input_port(
            AssignCell, 'location',
            (CellLocation, "reference to the cell location to be used"))
    reg.add_input_port(
            AssignCell, 'widget',
            (Component, "the swing component to be placed in the cell"))
    reg.add_output_port(
            AssignCell, 'cell',
            (Component, "the cell component"))

    reg.add_module(Frame)
    reg.add_input_port(
            Frame, 'widget',
            (Component, "the swing component to be placed in the frame"))
