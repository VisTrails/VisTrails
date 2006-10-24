import itk
import modules
from ITK import *

class ImageReader(ITK):
    def compute(self):
        dim = self.getInputFromPort("Dimension")
        pt = self.getInputFromPort("Pixel Type")
        fn = self.getInputFromPort("Filename")
        self.reader = itk.ImageFileReader[itk.Image[pt._type, dim]].New()
        self.reader.SetFileName(fn)
        self.reader.Update()
        self.setResult("Image", self.reader.GetOutput())
        self.setResult("Reader", self)

class ImageToFile(ITK):
    def compute(self):
        dim = self.getInputFromPort("Dimension")
        pt = self.getInputFromPort("Pixel Type")._type
        suf = self.getInputFromPort("Suffix")
        im = self.getInputFromPort("Image")
        f = self.createOutputFile(suf)
        writeType = itk.Image[pt, dim]
        writer = itk.ImageFileWriter[writeType].New(im, FileName=f.name)
        writer.Update()
        self.setResult("File", f)

    def createOutputFile(self, s):
        return self.interpreter.filePool.createFile(suffix=s)

