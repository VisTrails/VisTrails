import itk
import modules
from ITK import *

class GradientMagnitudeRecursiveGaussianImageFilter(Filter):
    def setSigma(self, sigma):
        self.sigma_ = sigma;
        
    def compute(self):
        inFilter = self.forceGetInputFromPort("Input Filter")
        im = self.getInputFromPort("Input Image")
        inType = self.getInputFromPort("Input PixelType")._type
        outType = self.getInputFromPort("Output PixelType")._type
        dim = self.getInputFromPort("Dimension")
        self.setSigma(self.getInputFromPort("Sigma"))
        inType = itk.Image[inType, dim]
        outType= itk.Image[outType, dim]

        self.filter_ = itk.GradientMagnitudeRecursiveGaussianImageFilter[inType, outType].New(im)
        self.filter_.SetSigma(self.sigma_)
        
        self.filter_.Update()

        self.setResult("Output Image", self.filter_.GetOutput())
        self.setResult("Filter", self)

class RescaleIntensityImageFilter(Filter):
    def compute(self):
        inFilter = self.forceGetInputFromPort("Input Filter")
        im = self.getInputFromPort("Input Image")
        inType = self.getInputFromPort("Input PixelType")._type
        outType = self.getInputFromPort("Output PixelType")._type
        dim = self.getInputFromPort("Dimension")
        minimum = self.getInputFromPort("Minimum")
        maximum = self.getInputFromPort("Maximum")
        inType = itk.Image[inType, dim]
        outType= itk.Image[outType, dim]

        self.filter_ = itk.RescaleIntensityImageFilter[inType, outType].New(im)
        self.filter_.SetOutputMaximum(maximum)
        self.filter_.SetOutputMinimum(minimum)
        
        self.filter_.Update()

        self.setResult("Output Image", self.filter_.GetOutput())
        self.setResult("Filter", self)
        
