import itk
import modules
from ITK import *

class PixelTypeFloat(PixelType):
    def compute(self):
        self._type = itk.F
        self.setResult("Pixel Type", self)

class PixelTypeUnsignedChar(PixelType):
    def compute(self):
        self._type = itk.UC
        self.setResult("Pixel Type", self)
