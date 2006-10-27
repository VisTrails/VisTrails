#  ITK package for VisTrails

version = '0.1'

try:
    import itk
except ImportError:
    raise PackageError("This package requires ITK and WrapITK")

import modules
import modules.module_registry

from ITK import ITK, PixelType
from PixelTypes import *
from Image import *
from ImageReader import *
from Filters import *

def initialize(*args, **keywords):
    reg = modules.module_registry
    basic = modules.basic_modules

    reg.addModule(ITK)
    reg.addModule(PixelType)

    reg.addModule(PixelTypeFloat)
    reg.addOutputPort(PixelTypeFloat, "Pixel Type", (PixelType, 'Pixel Type'))

    reg.addModule(PixelTypeUnsignedChar)
    reg.addOutputPort(PixelTypeUnsignedChar, "Pixel Type", (PixelType, 'Pixel Type'))

    reg.addModule(Image)
    reg.addInputPort(Image, "Pixel Type", (PixelType, 'Pixel Type'))
    reg.addInputPort(Image, "Dimension", (basic.Integer, 'Dimension'))
    reg.addInputPort(Image, "Image", (Image, 'Image'))
    reg.addOutputPort(Image, "Image Pixel Type", (PixelType, 'Image Pixel Type'))
    reg.addOutputPort(Image, "Image Dimension", (basic.Integer, 'Image Dimension'))
    reg.addOutputPort(Image, "Output Image", (Image, 'Output Image'))

    reg.addModule(ImageReader)
    reg.addInputPort(ImageReader, "Filename", (basic.String, 'Filename'))
    reg.addInputPort(ImageReader, "Pixel Type", (PixelType, 'Pixel Type'))
    reg.addInputPort(ImageReader, "Dimension", (basic.Integer, 'Dimension'))
    reg.addOutputPort(ImageReader, "Image", (Image, 'Image'))
    reg.addOutputPort(ImageReader, "Reader", (ImageReader, 'Reader'))

    reg.addModule(ImageToFile)
    reg.addInputPort(ImageToFile, "Suffix", (basic.String, 'Suffix'))
    reg.addInputPort(ImageToFile, "Pixel Type", (PixelType, 'Pixel Type'))
    reg.addInputPort(ImageToFile, "Dimension", (basic.Integer, 'Dimension'))
    reg.addInputPort(ImageToFile, "Image", (Image, 'Image'))
    reg.addOutputPort(ImageToFile, "File", (basic.File, 'File'))

    reg.addModule(Filter)
    reg.addModule(GradientMagnitudeRecursiveGaussianImageFilter)
    reg.addInputPort(GradientMagnitudeRecursiveGaussianImageFilter, "Input Filter", (Filter, 'Input Filter'))
    reg.addInputPort(GradientMagnitudeRecursiveGaussianImageFilter, "Input Image", (Image, 'Input Image'))
    reg.addInputPort(GradientMagnitudeRecursiveGaussianImageFilter, "Input PixelType", (PixelType, 'Input PixelType'))
    reg.addInputPort(GradientMagnitudeRecursiveGaussianImageFilter, "Output PixelType", (PixelType, 'Output PixelType'))
    reg.addInputPort(GradientMagnitudeRecursiveGaussianImageFilter, "Dimension", (basic.Integer, 'Dimension'))
    reg.addInputPort(GradientMagnitudeRecursiveGaussianImageFilter, "Sigma", (basic.Float, 'Sigma'))
    reg.addOutputPort(GradientMagnitudeRecursiveGaussianImageFilter, "Output Image", (Image, 'Output Image'))
    reg.addOutputPort(GradientMagnitudeRecursiveGaussianImageFilter, "Filter", (Filter, 'Filter'))

    reg.addModule(RescaleIntensityImageFilter)
    reg.addInputPort(RescaleIntensityImageFilter, "Input Filter", (Filter, 'Input Filter'))
    reg.addInputPort(RescaleIntensityImageFilter, "Input Image", (Image, 'Input Image'))
    reg.addInputPort(RescaleIntensityImageFilter, "Input PixelType", (PixelType, 'Input PixelType'))
    reg.addInputPort(RescaleIntensityImageFilter, "Output PixelType", (PixelType, 'Output PixelType'))
    reg.addInputPort(RescaleIntensityImageFilter, "Dimension", (basic.Integer, 'Dimension'))
    reg.addInputPort(RescaleIntensityImageFilter, "Minimum", (basic.Integer, 'Minimum'))
    reg.addInputPort(RescaleIntensityImageFilter, "Maximum", (basic.Integer, 'Maximum'))
    reg.addOutputPort(RescaleIntensityImageFilter, "Output Image", (Image, 'Output Image'))
    reg.addOutputPort(RescaleIntensityImageFilter, "Filter", (Filter, 'Filter'))

