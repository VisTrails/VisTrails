from core import system
from core.modules.module_registry import registry
from packages.spreadsheet.basic_widgets import SpreadsheetCell, CellLocation

class Render(SpreadsheetCell):
  def compute(self): 
      pass

def registerRender():
    registry.add_module(Render, abstract=True)
