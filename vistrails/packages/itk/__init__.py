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
identifier = 'edu.utah.sci.vistrails.itk'
name = 'ITK'

import core.bundles.utils
import core.requirements

# Ugly, but Carlos doesnt know any better
if core.bundles.utils.guess_system() == 'linux-ubuntu':
    import sys
    sys.path.append('/usr/local/lib/VisTrailsITK')

try:
    from core.bundles import py_import
    itk = py_import('itk', {'linux-ubuntu': 'vistrails-itk'})
except ImportError:
    raise core.requirements.MissingRequirement("ITK and WrapITK")

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
from SelectionFilters import *
from SmoothingFilters import *

def initialize(*args, **keywords):
    reg = core.modules.module_registry
    basic = core.modules.basic_modules

    reg.add_module(ITK)
    reg.add_module(Index2D)
    reg.add_input_port(Index2D, "X Index", (basic.Integer, 'X Index'))
    reg.add_input_port(Index2D, "Y Index", (basic.Integer, 'Y Index'))
    reg.add_output_port(Index2D, "Index", (Index2D, 'Index'))

    reg.add_module(Index3D)
    reg.add_input_port(Index3D, "X Index", (basic.Integer, 'X Index'))
    reg.add_input_port(Index3D, "Y Index", (basic.Integer, 'Y Index'))
    reg.add_input_port(Index3D, "Z Index", (basic.Integer, 'Z Index'))
    reg.add_output_port(Index3D, "Index", (Index3D, 'Index'))

    reg.add_module(Size)
    reg.add_input_port(Size, "Dimension", (basic.Integer, 'Dimension'))
    reg.add_input_port(Size, "Element 1", (basic.Integer, 'Element 1'))
    reg.add_input_port(Size, "Element 2", (basic.Integer, 'Element 2'))
    reg.add_input_port(Size, "Element 3", (basic.Integer, 'Element 3'))
    reg.add_output_port(Size, "Size", (Size, 'Size'))

    reg.add_module(Region)
    reg.add_input_port(Region, "Dimension", (basic.Integer, 'Dimension'))
    reg.add_input_port(Region, "Size", (Size, 'Size'))
    reg.add_input_port(Region, "Input 2D Index", (Index2D, 'Input 2D Index'))
    reg.add_input_port(Region, "Input 3D Index", (Index3D, 'Input 3D Index'), True)
    reg.add_output_port(Region, "Region", (Region, 'Region'))

    reg.add_module(PixelType)

    reg.add_module(PixelTypeFloat)
    reg.add_output_port(PixelTypeFloat, "Pixel Type", (PixelType, 'Pixel Type'))

    reg.add_module(PixelTypeUnsignedChar)
    reg.add_output_port(PixelTypeUnsignedChar, "Pixel Type", (PixelType, 'Pixel Type'))

    reg.add_module(PixelTypeUnsignedShort)
    reg.add_output_port(PixelTypeUnsignedShort, "Pixel Type", (PixelType, 'Pixel Type'))

    reg.add_module(PixelTypeRGB)
    reg.add_output_port(PixelTypeRGB, "Pixel Type", (PixelType, 'Pixel Type'))

    reg.add_module(Image)
    reg.add_input_port(Image, "Pixel Type", (PixelType, 'Pixel Type'))
    reg.add_input_port(Image, "Dimension", (basic.Integer, 'Dimension'))
    reg.add_input_port(Image, "Image", (Image, 'Image'))
    reg.add_output_port(Image, "Image Pixel Type", (PixelType, 'Image Pixel Type'))
    reg.add_output_port(Image, "Image Dimension", (basic.Integer, 'Image Dimension'))
    reg.add_output_port(Image, "Output Image", (Image, 'Output Image'))

    reg.add_module(ImageReader)
    reg.add_input_port(ImageReader, "Filename", (basic.String, 'Filename'))
    reg.add_input_port(ImageReader, "Pixel Type", (PixelType, 'Pixel Type'))
    reg.add_input_port(ImageReader, "Dimension", (basic.Integer, 'Dimension'))
    reg.add_output_port(ImageReader, "Image", (Image, 'Image'))
    reg.add_output_port(ImageReader, "Reader", (ImageReader, 'Reader'))

    reg.add_module(DICOMReader)
    reg.add_input_port(DICOMReader, "Directory", (basic.String, 'Directory'))
    reg.add_input_port(DICOMReader, "Dimension", (basic.Integer, 'Dimension'))
    reg.add_output_port(DICOMReader, "Image Series", (Image, 'Image Series'))

    reg.add_module(GDCMReader)
    reg.add_input_port(GDCMReader, "Directory", (basic.String, 'Directory'))
    reg.add_input_port(GDCMReader, "Dimension", (basic.Integer, 'Dimension'))
    reg.add_output_port(GDCMReader, "Image Series", (Image, 'Image Series'))

    reg.add_module(ImageToFile)
    reg.add_input_port(ImageToFile, "Suffix", (basic.String, 'Suffix'))
    reg.add_input_port(ImageToFile, "Pixel Type", (PixelType, 'Pixel Type'))
    reg.add_input_port(ImageToFile, "Dimension", (basic.Integer, 'Dimension'))
    reg.add_input_port(ImageToFile, "Image", (Image, 'Image'))
    reg.add_output_port(ImageToFile, "File", (basic.File, 'File'))

    reg.add_module(Filter, "Image Filters")
    reg.add_module(FeatureFilter, "Feature Extraction Filters")
    reg.add_module(GradientMagnitudeRecursiveGaussianImageFilter)
    reg.add_input_port(GradientMagnitudeRecursiveGaussianImageFilter, "Input Filter", (Filter, 'Input Filter'))
    reg.add_input_port(GradientMagnitudeRecursiveGaussianImageFilter, "Input Image", (Image, 'Input Image'))
    reg.add_input_port(GradientMagnitudeRecursiveGaussianImageFilter, "Input PixelType", (PixelType, 'Input PixelType'))
    reg.add_input_port(GradientMagnitudeRecursiveGaussianImageFilter, "Output PixelType", (PixelType, 'Output PixelType'))
    reg.add_input_port(GradientMagnitudeRecursiveGaussianImageFilter, "Dimension", (basic.Integer, 'Dimension'))
    reg.add_input_port(GradientMagnitudeRecursiveGaussianImageFilter, "Sigma", (basic.Float, 'Sigma'))
    reg.add_output_port(GradientMagnitudeRecursiveGaussianImageFilter, "Output Image", (Image, 'Output Image'))
    reg.add_output_port(GradientMagnitudeRecursiveGaussianImageFilter, "Filter", (Filter, 'Filter'), True)
    reg.add_output_port(GradientMagnitudeRecursiveGaussianImageFilter, "Output PixelType", (PixelType, 'Output PixelType'))

    reg.add_module(IntensityFilter, "Image Intensity Filters")
    reg.add_module(RescaleIntensityImageFilter)
    reg.add_input_port(RescaleIntensityImageFilter, "Input Filter", (Filter, 'Input Filter'), True)
    reg.add_input_port(RescaleIntensityImageFilter, "Input Image", (Image, 'Input Image'))
    reg.add_input_port(RescaleIntensityImageFilter, "Input PixelType", (PixelType, 'Input PixelType'))
    reg.add_input_port(RescaleIntensityImageFilter, "Output PixelType", (PixelType, 'Output PixelType'))
    reg.add_input_port(RescaleIntensityImageFilter, "Dimension", (basic.Integer, 'Dimension'))
    reg.add_input_port(RescaleIntensityImageFilter, "Minimum", (basic.Integer, 'Minimum'))
    reg.add_input_port(RescaleIntensityImageFilter, "Maximum", (basic.Integer, 'Maximum'))
    reg.add_output_port(RescaleIntensityImageFilter, "Output Image", (Image, 'Output Image'))
    reg.add_output_port(RescaleIntensityImageFilter, "Filter", (Filter, 'Filter'), True)
    reg.add_output_port(RescaleIntensityImageFilter, "Output PixelType", (PixelType, 'Output PixelType'))

    reg.add_module(SigmoidImageFilter)
    reg.add_input_port(SigmoidImageFilter, "Input Filter", (Filter, 'Input Filter'), True)
    reg.add_input_port(SigmoidImageFilter, "Input Image", (Image, 'Input Image'))
    reg.add_input_port(SigmoidImageFilter, "Input PixelType", (PixelType, 'Input PixelType'))
    reg.add_input_port(SigmoidImageFilter, "Output PixelType", (PixelType, 'Output PixelType'), True)
    reg.add_input_port(SigmoidImageFilter, "Dimension", (basic.Integer, 'Dimension'))
    reg.add_input_port(SigmoidImageFilter, "Minimum", (basic.Integer, 'Minimum'), True)
    reg.add_input_port(SigmoidImageFilter, "Maximum", (basic.Integer, 'Maximum'), True)
    reg.add_input_port(SigmoidImageFilter, "Alpha", (basic.Float, 'Alpha'), True)
    reg.add_input_port(SigmoidImageFilter, "Beta", (basic.Float, 'Beta'), True)
    
    reg.add_output_port(SigmoidImageFilter, "Output Image", (Image, 'Output Image'))
    reg.add_output_port(SigmoidImageFilter, "Filter", (Filter, 'Output Filter'))
    reg.add_output_port(SigmoidImageFilter, "Output PixelType", (PixelType, 'Output PixelType'))
    reg.add_output_port(SigmoidImageFilter, "Output Dimension", (basic.Integer, 'Output Dimension'))

    reg.add_module(ThresholdImageFilter)
    reg.add_input_port(ThresholdImageFilter, "Input Image", (Image, 'Input Image'))
    reg.add_input_port(ThresholdImageFilter, "Dimension", (basic.Integer, 'Dimension'))
    reg.add_input_port(ThresholdImageFilter, "Input PixelType", (PixelType, 'Input PixelType'))
    reg.add_input_port(ThresholdImageFilter, "Upper Value", (basic.Integer, 'Upper Value'))
    reg.add_input_port(ThresholdImageFilter, "Lower Value", (basic.Integer, 'Lower Value'))

    reg.add_output_port(ThresholdImageFilter, "Output Image", (Image, 'Output Image'))
    reg.add_output_port(ThresholdImageFilter, "Output Dimension", (basic.Integer, 'Output Dimension'))
    reg.add_output_port(ThresholdImageFilter, "Output PixelType", (PixelType, 'Output PixelType'))

    reg.add_module(SegmentationFilter, "Segmentation Filters")
    reg.add_module(IsolatedWatershedImageFilter)
    reg.add_input_port(IsolatedWatershedImageFilter, "Input Image", (Image, 'Input Image'))
    reg.add_input_port(IsolatedWatershedImageFilter, "Input PixelType", (PixelType, 'Input PixelType'))
    reg.add_input_port(IsolatedWatershedImageFilter, "Dimension", (basic.Integer, 'Dimension'))
    reg.add_input_port(IsolatedWatershedImageFilter, "Seed1", (Index2D, 'Seed 1 Location'))

    reg.add_input_port(IsolatedWatershedImageFilter, "Output PixelType", (PixelType, 'Output PixelType'), True)
    reg.add_input_port(IsolatedWatershedImageFilter, "Threshold", (basic.Float, 'Threshold'), True)
    reg.add_input_port(IsolatedWatershedImageFilter, "Seed2", (Index2D, 'Seed 2 Location'), True)
    reg.add_input_port(IsolatedWatershedImageFilter, "ReplaceValue1", (basic.Float, 'Replacement Value 1'), True);
    reg.add_input_port(IsolatedWatershedImageFilter, "ReplaceValue2", (basic.Float, 'Replacement Value 2'), True);

    reg.add_output_port(IsolatedWatershedImageFilter, "Output Image", (Image, 'Output Image'))
    reg.add_output_port(IsolatedWatershedImageFilter, "Output PixelType", (PixelType, 'Output PixelType'))

    reg.add_module(ConnectedThresholdImageFilter)
    reg.add_input_port(ConnectedThresholdImageFilter, "Input Image", (Image, 'Input Image'))
    reg.add_input_port(ConnectedThresholdImageFilter, "Input PixelType", (PixelType, 'Input PixelType'))
    reg.add_input_port(ConnectedThresholdImageFilter, "Dimension", (basic.Integer, 'Dimension'))
    reg.add_input_port(ConnectedThresholdImageFilter, "Seed2D", (Index2D, 'Seed Point'))
    reg.add_input_port(ConnectedThresholdImageFilter, "Seed3D", (Index3D, 'Seed Point'))
    reg.add_input_port(ConnectedThresholdImageFilter, "Replace Value", (basic.Float, 'Replacement Value'))
    reg.add_input_port(ConnectedThresholdImageFilter, "Upper Value", (basic.Float, 'Upper Threshold Value'))
    reg.add_input_port(ConnectedThresholdImageFilter, "Lower Value", (basic.Float, 'Lower Threshold Value'))

    reg.add_output_port(ConnectedThresholdImageFilter, "Output Image", (Image, 'Output Image'))
    reg.add_output_port(ConnectedThresholdImageFilter, "Output Dimension", (basic.Integer, 'Output Dimension'))
    reg.add_output_port(ConnectedThresholdImageFilter, "Output PixelType", (PixelType, 'Output PixelType'))

    reg.add_module(ConfidenceConnectedImageFilter)
    reg.add_input_port(ConfidenceConnectedImageFilter, "Input Image", (Image, 'Input Image'))
    reg.add_input_port(ConfidenceConnectedImageFilter, "Input PixelType", (PixelType, 'Input PixelType'))
    reg.add_input_port(ConfidenceConnectedImageFilter, "Dimension", (basic.Integer, 'Dimension'))
    reg.add_input_port(ConfidenceConnectedImageFilter, "Seed2D", (Index2D, 'Seed Point'))
    reg.add_input_port(ConfidenceConnectedImageFilter, "Seed3D", (Index3D, 'Seed Point'))
    reg.add_input_port(ConfidenceConnectedImageFilter, "Replace Value", (basic.Float, 'Replacement Value'))
    reg.add_input_port(ConfidenceConnectedImageFilter, "Multiplier", (basic.Float, 'Multiplier'))

    reg.add_output_port(ConfidenceConnectedImageFilter, "Output Image", (Image, 'Output Image'))
    reg.add_output_port(ConfidenceConnectedImageFilter, "Output Dimension", (basic.Integer, 'Output Dimension'))
    reg.add_output_port(ConfidenceConnectedImageFilter, "Output PixelType", (PixelType, 'Output PixelType'))


    reg.add_module(SelectionFilter, "Image Selection Filters")
    reg.add_module(CastImageFilter)
    reg.add_input_port(CastImageFilter, "Input Image", (Image, 'Input Image'))
    reg.add_input_port(CastImageFilter, "Dimension", (basic.Integer, 'Dimension'))
    reg.add_input_port(CastImageFilter, "Input PixelType", (PixelType, 'Input PixelType'))
    reg.add_input_port(CastImageFilter, "Output PixelType", (PixelType, 'Output PixelType'))
    reg.add_output_port(CastImageFilter, "Output Image", (Image, 'Output Image'))
    reg.add_output_port(CastImageFilter, "Output PixelType", (PixelType, 'Output PixelType'))
    reg.add_output_port(CastImageFilter, "Dimension", (basic.Integer, 'Dimension'))

    reg.add_module(RegionOfInterestImageFilter, "RegionOfInterestFilter")
    reg.add_input_port(RegionOfInterestImageFilter, "Input Dimension", (basic.Integer, 'Input Dimension'))
    reg.add_input_port(RegionOfInterestImageFilter, "Output Dimension", (basic.Integer, 'Output Dimension'))
    reg.add_input_port(RegionOfInterestImageFilter, "Input PixelType", (PixelType, 'Input PixelType'))
    reg.add_input_port(RegionOfInterestImageFilter, "Output PixelType", (PixelType, 'Output PixelType'), True)
    reg.add_input_port(RegionOfInterestImageFilter, "Input 2D Index", (Index2D, 'Input 2D Index'))
    reg.add_input_port(RegionOfInterestImageFilter, "Input 3D Index", (Index3D, 'Input 3D Index'), True)
    reg.add_input_port(RegionOfInterestImageFilter, "Region Size", (Size, 'Region Size'))
    reg.add_input_port(RegionOfInterestImageFilter, "Input Image", (Image, 'Input Image'))
    reg.add_input_port(RegionOfInterestImageFilter, "Input Region", (Region, 'Input Region'), True)
    reg.add_output_port(RegionOfInterestImageFilter, "Output Image", (Image, 'Output Image'))
    reg.add_output_port(RegionOfInterestImageFilter, "Output PixelType", (PixelType, 'Output PixelType'))
    reg.add_output_port(RegionOfInterestImageFilter, "Filter", (Filter, 'Filter'))
    reg.add_output_port(RegionOfInterestImageFilter, "Output Dimension", (basic.Integer, 'Output Dimension'))

    reg.add_module(ExtractImageFilter)
    reg.add_input_port(ExtractImageFilter, "Input Volume", (Image, 'Input Image'))
    reg.add_input_port(ExtractImageFilter, "Input Dimension", (basic.Integer, 'Input Dimension'))
    reg.add_input_port(ExtractImageFilter, "Output Dimension", (basic.Integer, 'Output Dimension'))
    reg.add_input_port(ExtractImageFilter, "Input PixelType", (PixelType, 'Input PixelType'))
    reg.add_input_port(ExtractImageFilter, "Extraction Region", (Region, 'Extraction Region'))
    reg.add_output_port(ExtractImageFilter, "Output Image", (Image, 'Output Image'))
    reg.add_output_port(ExtractImageFilter, "Output PixelType", (PixelType, 'Output PixelType'))
    reg.add_output_port(ExtractImageFilter, "Dimension", (basic.Integer, 'Dimension'))

    reg.add_module(SmoothingFilter, "Image Smoothing Filters")
    reg.add_module(CurvatureAnisotropicDiffusionFilter)
    reg.add_input_port(CurvatureAnisotropicDiffusionFilter, "Input Image", (Image, 'Input Image'))
    reg.add_input_port(CurvatureAnisotropicDiffusionFilter, "Input Dimension", (basic.Integer, 'Input Dimension'))
    reg.add_input_port(CurvatureAnisotropicDiffusionFilter, "Input PixelType", (PixelType, 'Input PixelType'))
    reg.add_input_port(CurvatureAnisotropicDiffusionFilter, "Output PixelType", (PixelType, 'Output PixelType'), True)
    reg.add_input_port(CurvatureAnisotropicDiffusionFilter, "Iterations", (basic.Integer, 'Iterations'), True)
    reg.add_input_port(CurvatureAnisotropicDiffusionFilter, "TimeStep", (basic.Float, 'TimeStep'), True)
    reg.add_input_port(CurvatureAnisotropicDiffusionFilter, "Conductance", (basic.Float, 'Conductance'), True)
    reg.add_output_port(CurvatureAnisotropicDiffusionFilter, "Output Image", (Image, 'Output Image'))
    reg.add_output_port(CurvatureAnisotropicDiffusionFilter, "Output PixelType", (PixelType, 'Output PixelType'))
    reg.add_output_port(CurvatureAnisotropicDiffusionFilter, "Output Dimension", (basic.Integer, 'Output Dimension'))
    reg.add_output_port(CurvatureAnisotropicDiffusionFilter, "Filter", (Filter, 'Filter'), True)

    reg.add_module(RecursiveGaussianImageFilter)
    reg.add_input_port(RecursiveGaussianImageFilter, "Input Image", (Image, 'Input Image'))
    reg.add_input_port(RecursiveGaussianImageFilter, "Input Dimension", (basic.Integer, 'Input Dimension'))
    reg.add_input_port(RecursiveGaussianImageFilter, "Input PixelType", (PixelType, 'Input PixelType'))
    reg.add_input_port(RecursiveGaussianImageFilter, "Sigma", (basic.Float, 'Sigma'))

    reg.add_output_port(RecursiveGaussianImageFilter, "Output Image", (Image, 'Output Image'))
    reg.add_output_port(RecursiveGaussianImageFilter, "Output Dimension", (basic.Integer, 'Output Dimension'))
    reg.add_output_port(RecursiveGaussianImageFilter, "Output PixelType", (PixelType, 'Output PixelType'))

    reg.add_module(CurvatureFlowImageFilter)
    reg.add_input_port(CurvatureFlowImageFilter, "Input Image", (Image, 'Input Image'))
    reg.add_input_port(CurvatureFlowImageFilter, "Input Dimension", (basic.Integer, 'Input Dimension'))
    reg.add_input_port(CurvatureFlowImageFilter, "Input PixelType", (PixelType, 'Input PixelType'))
    reg.add_input_port(CurvatureFlowImageFilter, "TimeStep", (basic.Float, 'TimeStep'), True)
    reg.add_input_port(CurvatureFlowImageFilter, "Iterations", (basic.Integer, 'Iterations'), True)
    reg.add_output_port(CurvatureFlowImageFilter, "Output Image", (Image, 'Output Image'))
    reg.add_output_port(CurvatureFlowImageFilter, "Output Dimension", (basic.Integer, 'Output Dimension'))
    reg.add_output_port(CurvatureFlowImageFilter, "Output PixelType", (PixelType, 'Output PixelType'))
