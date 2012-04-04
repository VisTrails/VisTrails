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
## of VisTrails), please contact us at contact@vistrails.org.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################
import itk
import core.modules

from ITK import *
from Image import Image

class ImageReader(Module):
    my_namespace = "ImageReader"
    def compute(self):
        dim = self.getInputFromPort("Dimension")
        outPixelType = self.getInputFromPort("Pixel Type")
        fn = self.getInputFromPort("Filename")
        self.reader = itk.ImageFileReader[itk.Image[outPixelType._type, dim]].New()
        self.reader.SetFileName(fn)
        self.reader.Update()

        #setup output image
        outIm = Image()
        outIm.setImg(self.reader.GetOutput())
        outIm.setPixelType(outPixelType)
        outIm.setDim(dim)

        self.setResult("Image", outIm)
        self.setResult("Reader", self)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="ImageReader", namespace=cls.my_namespace)
        reg.add_input_port(cls, "Filename", (basic.String, 'Filename'))
        reg.add_input_port(cls, "Pixel Type", (PixelType, 'Pixel Type'))
        reg.add_input_port(cls, "Dimension", (basic.Integer, 'Dimension'))

        reg.add_output_port(cls, "Image", (Image, 'Image'))
        reg.add_output_port(cls, "Reader", (ImageReader, 'Reader'))

class ImageToFile(Module):
    my_namespace = "ImageReader"
    def compute(self):
        im = self.getInputFromPort("Image")
        #check for input PixelType
        if self.hasInputFromPort("Input PixelType"):
            inPixelType = self.getInputFromPort("Input PixelType")._type
        else:
            inPixelType = im.getPixelType()

        #check for dimension
        if self.hasInputFromPort("Dimension"):
            dim = self.getInputFromPort("Dimension")
        else:
            dim = im.getDim()

        suf = self.getInputFromPort("Suffix")
        f = self.createOutputFile(suf)
        writeType = itk.Image[inPixelType._type, dim]
        writer = itk.ImageFileWriter[writeType].New(im.getImg(), FileName=f.name)
        writer.Update()
        self.setResult("File", f)

    def createOutputFile(self, s):
        return self.interpreter.filePool.create_file(suffix=s)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="ImageToFile", namespace=cls.my_namespace)
        reg.add_input_port(cls, "Suffix", (basic.String, 'Suffix'))
        reg.add_input_port(cls, "Pixel Type", (PixelType, 'Pixel Type'),True)
        reg.add_input_port(cls, "Dimension", (basic.Integer, 'Dimension'),True)
        reg.add_input_port(cls, "Image", (Image, 'Image'))

        reg.add_output_port(cls, "File", (basic.File, 'File'))

class GDCMReader(Module):
    my_namespace = "ImageReader"
    def compute(self):
        dir = self.getInputFromPort("Directory")
        dim = self.getInputFromPort("Dimension")
        self.dicomNames_ = itk.GDCMSeriesFileNames.New()

        self.dicomNames_.SetDirectory(dir)
        self.dicomNames_.SetUseSeriesDetails(True)
        self.dicomNames_.SetRecursive(True)
        self.dicomNames_.LoadSequencesOn()

        self.iType_ = itk.Image[itk.US,dim]
        self.reader_ = itk.ImageSeriesReader[self.iType_].New()
        self.reader_.SetFileNames(self.dicomNames_.GetInputFileNames())
        self.io_ = itk.GDCMImageIO.New()
        self.reader_.SetImageIO(self.io_.GetPointer())
        self.reader_.Update()

        #setup output image
        outIm = Image()
        outIm.setImg(self.reader_.GetOutput())
        outIm.setPixelType(itk.US)
        outIm.setDim(dim)

        self.setResult("Image Series", outIm)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="GDCMReader", namespace=cls.my_namespace)
        reg.add_input_port(cls, "Directory", (basic.String, 'Directory'))
        reg.add_input_port(cls, "Dimension", (basic.Integer, 'Dimension'))
        reg.add_output_port(cls, "Image Series", (Image, 'Image Series'))

class DICOMReader(Module):
    my_namespace = "ImageReader"
    def compute(self):
        dir = self.getInputFromPort("Directory")
        dim = self.getInputFromPort("Dimension")
        self.dicomNames_ = itk.DICOMSeriesFileNames.New()

        self.dicomNames_.SetFileNameSortingOrderToSortByImagePositionPatient()
        self.dicomNames_.SetDirectory(dir)

        self.iType_ = itk.Image[itk.US,dim]
        self.reader_ = itk.ImageSeriesReader[self.iType_].New()
        self.reader_.SetFileNames(self.dicomNames_.GetFileNames(False))
        self.reader_.Update()

        #setup output image
        outIm = Image()
        outIm.setImg(self.reader_.GetOutput())
        outIm.setPixelType(itk.US)
        outIm.setDim(dim)

        self.setResult("Image Series", outIm)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, name="DICOMReader", namespace=cls.my_namespace)
        reg.add_input_port(cls, "Directory", (basic.String, 'Directory'))
        reg.add_input_port(cls, "Dimension", (basic.Integer, 'Dimension'))
        reg.add_output_port(cls, "Image Series", (Image, 'Image Series'))

class ITKImageToVTKData(Module):
    my_namespace = "ImageReader"
    def compute(self):
        dim = self.getInputFromPort("Dimension")
        pType = self.getInputFromPort("Input PixelType")
        iType = itk.Image[itk.pType,dim]
        self.vtkExport_ = itk.VTKImageExport[iType].New()
        im = self.getInputFromPort("Input Image")
        self.vtkExport_.SetInput(im)
        self.vtkExport_.Update()
        self.setResult("VTK Output", self.vtkExport_.GetOutput())

        #TODO add register method
