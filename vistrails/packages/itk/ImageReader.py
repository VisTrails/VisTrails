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
import itk
import core.modules
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
        return self.interpreter.filePool.create_file(suffix=s)

class GDCMReader(ITK):
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

	self.setResult("Image Series", self.reader_.GetOutput())

class DICOMReader(ITK):
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

	self.setResult("Image Series", self.reader_.GetOutput())
	

class ITKImageToVTKData(ITK):
    def compute(self):
	dim = self.getInputFromPort("Dimension")
	pType = self.getInputFromPort("Input PixelType")
	iType = itk.Image[itk.pType,dim]
	self.vtkExport_ = itk.VTKImageExport[iType].New()
	im = self.getInputFromPort("Input Image")
	self.vtkExport_.SetInput(im)
	self.vtkExport_.Update()
	self.setResult("VTK Output", self.vtkExport_.GetOutput())