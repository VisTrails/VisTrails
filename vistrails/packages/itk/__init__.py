############################################################################
##
## Copyright (C) 2006-2007 University of Utah. All rights reserved.
##
## This file is part of VisTrails.
##
## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of
## this file.  Please review the following to ensure GNU General Public
## Licensing requirements will be met:
## http://www.opensource.org/licenses/gpl-license.php
##
## If you are unsure which license is appropriate for your use (for
## instance, you are interested in developing a commercial derivative
## of VisTrails), please contact us at vistrails@sci.utah.edu.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################
#  ITK package for VisTrails

version = '0.1'

try:
    import itk
except ImportError:
    raise PackageError("This package requires ITK and WrapITK")

import core.modules
import core.modules.module_registry

from ITK import ITK, PixelType
from PixelTypes import *
from Image import *
from ImageReader import *
from Filters import *
from FeatureExtractionFilters import *
from IntensityFilters import *
from SegmentationFilters import *

def initialize(*args, **keywords):
    reg = core.modules.module_registry
    basic = core.modules.basic_modules

    reg.addModule(ITK)
    reg.addModule(Index2D)
    reg.addInputPort(Index2D, "X Index", (basic.Integer, 'X Index'))
    reg.addInputPort(Index2D, "Y Index", (basic.Integer, 'Y Index'))
    reg.addOutputPort(Index2D, "Index", (Index2D, 'Index'))

    reg.addModule(Index3D)
    reg.addInputPort(Index3D, "X Index", (basic.Integer, 'X Index'))
    reg.addInputPort(Index3D, "Y Index", (basic.Integer, 'Y Index'))
    reg.addInputPort(Index3D, "Z Index", (basic.Integer, 'Z Index'))
    reg.addOutputPort(Index3D, "Index", (Index3D, 'Index'))

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

    reg.addModule(Filter, "Image Filters")
    reg.addModule(FeatureFilter, "Feature Extraction Filters")
    reg.addModule(GradientMagnitudeRecursiveGaussianImageFilter)
    reg.addInputPort(GradientMagnitudeRecursiveGaussianImageFilter, "Input Filter", (Filter, 'Input Filter'))
    reg.addInputPort(GradientMagnitudeRecursiveGaussianImageFilter, "Input Image", (Image, 'Input Image'))
    reg.addInputPort(GradientMagnitudeRecursiveGaussianImageFilter, "Input PixelType", (PixelType, 'Input PixelType'))
    reg.addInputPort(GradientMagnitudeRecursiveGaussianImageFilter, "Output PixelType", (PixelType, 'Output PixelType'))
    reg.addInputPort(GradientMagnitudeRecursiveGaussianImageFilter, "Dimension", (basic.Integer, 'Dimension'))
    reg.addInputPort(GradientMagnitudeRecursiveGaussianImageFilter, "Sigma", (basic.Float, 'Sigma'))
    reg.addOutputPort(GradientMagnitudeRecursiveGaussianImageFilter, "Output Image", (Image, 'Output Image'))
    reg.addOutputPort(GradientMagnitudeRecursiveGaussianImageFilter, "Filter", (Filter, 'Filter'))

    reg.addModule(IntensityFilter, "Image Intensity Filters")
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

    reg.addModule(SegmentationFilter, "Segmentation Filters")
    reg.addModule(IsolatedWatershedImageFilter)
    reg.addInputPort(IsolatedWatershedImageFilter, "Input Image", (Image, 'Input Image'))
    reg.addInputPort(IsolatedWatershedImageFilter, "Input PixelType", (PixelType, 'Input PixelType'))
    reg.addInputPort(IsolatedWatershedImageFilter, "Output PixelType", (PixelType, 'Output PixelType'))
    reg.addInputPort(IsolatedWatershedImageFilter, "Dimension", (basic.Integer, 'Dimension'))
    reg.addInputPort(IsolatedWatershedImageFilter, "Seed1", (Index2D, 'Seed 1 Location'))
    reg.addInputPort(IsolatedWatershedImageFilter, "Threshold", (basic.Float, 'Threshold'))
    reg.addOutputPort(IsolatedWatershedImageFilter, "Output Image", (Image, 'Output Image'))