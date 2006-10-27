import itk
import modules
from ITK import *
from PixelTypes import *

class Image(ITK):
    def setDimension(self, dim):
        self.dim = dim

    def setPixelType(self, pixeltype):
        self._type = pixeltype

    def getDimension(self):
        return self.dim

    def getPixelType(self):
        # Note:  This is still a PixelType object. 
        return self._type

    def compute(self):
        inIm = self.getInputFromPort("Image")
        if inIm:
            self.setDimension(inIm.getDimension())
            self.setPixelType(inIm.getPixelType())
        else:    
            self.setDimension(self.getInputFromPort("Dimension"))
            self.setPixelType(self.getInputFromPort("Pixel Type"))

        self._image = itk.Image[_type._type, dim]
        self._image.New()

        self.setResult("Image Pixel Type", self._type)
        self.setResult("Image Dimension", self.dim)
        self.setResult("Output Image", self)
