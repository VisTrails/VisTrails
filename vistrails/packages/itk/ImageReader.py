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

