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
import core.modules
import core.modules.module_registry
from core.modules.vistrails_module import Module, ModuleError
from SciPy import SciPy
from Matrix import *
from MatlabReader import MatlabReader
from MatrixInfo import MatrixInfo
from MatrixConvert import *
from MatrixOperations import *
from DSP import *
from Filters import *
import core.modules.basic_modules

version = '0.9.0'
name = 'SciPy'
identifier = 'edu.utah.sci.vistrails.scipy'

##############################################################################

from scipy import sparse

def initialize(*args, **keywords):
    reg = core.modules.module_registry.get_module_registry()
    basic = core.modules.basic_modules

    reg.add_module(SciPy)
    reg.add_module(Matrix)
    reg.add_module(MatrixOperation)
    reg.add_module(DSP)
    reg.add_module(DSPFilters, name="DSP Window Filters")

    reg.add_module(SparseMatrix)
    reg.add_input_port(SparseMatrix, "size", (basic.Integer, 'Matrix Size'))
    reg.add_output_port(SparseMatrix, "output", (SparseMatrix, 'Output Matrix'))

    reg.add_module(HanningWindow)
    reg.add_input_port(HanningWindow, "Window Size", (basic.Integer, 'Window Size'))
    reg.add_output_port(HanningWindow, "Window", (SparseMatrix, 'Window'))

    reg.add_module(TriangularWindow)
    reg.add_input_port(TriangularWindow, "Window Size", (basic.Integer, 'Window Size'))
    reg.add_output_port(TriangularWindow, "Window", (SparseMatrix, 'Window'))

    reg.add_module(BlackmanWindow)
    reg.add_input_port(BlackmanWindow, "Window Size", (basic.Integer, 'Window Size'))
    reg.add_output_port(BlackmanWindow, "Window", (SparseMatrix, 'Window'))

    reg.add_module(BlackmanHarrisWindow)
    reg.add_input_port(BlackmanHarrisWindow, "Window Size", (basic.Integer, 'Window Size'))
    reg.add_output_port(BlackmanHarrisWindow, "Window", (SparseMatrix, 'Window'))

    reg.add_module(ParzenWindow)
    reg.add_input_port(ParzenWindow, "Window Size", (basic.Integer, 'Window Size'))
    reg.add_output_port(ParzenWindow, "Window", (SparseMatrix, 'Window'))

    reg.add_module(HammingWindow)
    reg.add_input_port(HammingWindow, "Window Size", (basic.Integer, 'Window Size'))
    reg.add_output_port(HammingWindow, "Window", (SparseMatrix, 'Window'))

    reg.add_module(KaiserWindow)
    reg.add_input_port(KaiserWindow, "Window Size", (basic.Integer, 'Window Size'))
    reg.add_input_port(KaiserWindow, "Beta", (basic.Float, 'Beta'))
    reg.add_output_port(KaiserWindow, "Window", (SparseMatrix, 'Window'))

    reg.add_module(BartlettHannWindow)
    reg.add_input_port(BartlettHannWindow, "Window Size", (basic.Integer, 'Window Size'))
    reg.add_output_port(BartlettHannWindow, "Window", (SparseMatrix, 'Window'))

    reg.add_module(GaussianWindow)
    reg.add_input_port(GaussianWindow, "Window Size", (basic.Integer, 'Window Size'))
    reg.add_input_port(GaussianWindow, "Sigma", (basic.Integer, 'Sigma (Std. Deviation)'))
    reg.add_output_port(GaussianWindow, "Window", (SparseMatrix, 'Window'))

    reg.add_module(BoxcarWindow)
    reg.add_input_port(BoxcarWindow, "Window Size", (basic.Integer, 'Window Size'))
    reg.add_output_port(BoxcarWindow, "Window", (SparseMatrix, 'Window'))

    reg.add_module(BohmanWindow)
    reg.add_input_port(BohmanWindow, "Window Size", (basic.Integer, 'Window Size'))
    reg.add_output_port(BohmanWindow, "Window", (SparseMatrix, 'Window'))

    reg.add_module(BartlettWindow)
    reg.add_input_port(BartlettWindow, "Window Size", (basic.Integer, 'Window Size'))
    reg.add_output_port(BartlettWindow, "Window", (SparseMatrix, 'Window'))

    reg.add_module(NuttallBlackmanHarrisWindow)
    reg.add_input_port(NuttallBlackmanHarrisWindow, "Window Size", (basic.Integer, 'Window Size'))
    reg.add_output_port(NuttallBlackmanHarrisWindow, "Window", (SparseMatrix, 'Window'))

    reg.add_module(PrintMatrix)
    reg.add_input_port(PrintMatrix, "InputMatrix", (Matrix, 'Matrix'))
    reg.add_output_port(PrintMatrix, "Output", (basic.String, 'Output String'))

    reg.add_module(MatrixConvert)
    reg.add_input_port(MatrixConvert, "InputMatrix", (Matrix, 'Matrix'))
    reg.add_input_port(MatrixConvert, "OutputType", (basic.String, 'Output Type'))
    reg.add_output_port(MatrixConvert, "SparseOutput", (SparseMatrix, 'Output Sparse Matrix'))
#    reg.add_output_port(MatrixConvert, "COOOutput", (COOMatrix, 'Output COO Matrix'))
#    reg.add_output_port(MatrixConvert, "CSCOutput", (CSCMatrix, 'Output CSC Matrix'))

    reg.add_module(MatlabReader)
    reg.add_input_port(MatlabReader, "Filename", (basic.String, 'Filename'))
    reg.add_output_port(MatlabReader, "sparseoutput", (SparseMatrix, 'Output Sparse Matrix'))
    reg.add_input_port(MatlabReader, "File", (basic.File, 'File'))
    
    reg.add_module(MatrixInfo)
    reg.add_input_port(MatrixInfo, "InputMatrix", (Matrix, 'Matrix'))
    reg.add_output_port(MatrixInfo, "output", (basic.String, 'Output String'))

    reg.add_module(GetReals)
    reg.add_input_port(GetReals, "InputMatrix", (SparseMatrix, 'Input Matrix'))
    reg.add_output_port(GetReals, "OutputMatrix", (SparseMatrix, 'Result'))

    reg.add_module(GetImaginaries)
    reg.add_input_port(GetImaginaries, "InputMatrix", (SparseMatrix, 'Input Matrix'))
    reg.add_output_port(GetImaginaries, "OutputMatrix", (SparseMatrix, 'Result'))

    reg.add_module(Conjugate)
    reg.add_input_port(Conjugate, "InputMatrix", (SparseMatrix, 'Input Matrix'))
    reg.add_output_port(Conjugate, "OutputMatrix", (SparseMatrix, 'Result'))

    reg.add_module(GetRow)
    reg.add_input_port(GetRow, "InputMatrix", (Matrix, 'Input Matrix'))
    reg.add_input_port(GetRow, "RowIndex", (basic.Integer, 'Row Index'))
    reg.add_output_port(GetRow, "OutputMatrix", (SparseMatrix, 'Result'))

    reg.add_module(GetCol)
    reg.add_input_port(GetCol, "InputMatrix", (Matrix, 'Input Matrix'))
    reg.add_input_port(GetCol, "ColIndex", (basic.Integer, 'Col Index'))
    reg.add_output_port(GetCol, "OutputMatrix", (SparseMatrix, 'Result'))

    reg.add_module(GetColumnRange)
    reg.add_input_port(GetColumnRange, "InputMatrix", (SparseMatrix, 'Input Matrix'))
    reg.add_input_port(GetColumnRange, "StartIndex", (basic.Integer, 'Start Index'))
    reg.add_input_port(GetColumnRange, "EndIndex", (basic.Integer, 'End Index'))
    reg.add_output_port(GetColumnRange, "Output", (SparseMatrix, 'Result'))
    
    reg.add_module(ScalarMultiply)
    reg.add_input_port(ScalarMultiply, "InputMatrix", (Matrix, 'Input Matrix'))
    reg.add_input_port(ScalarMultiply, "Scalar", (basic.Float, 'Scalar'))
    reg.add_output_port(ScalarMultiply, "OutputMatrix", (SparseMatrix, 'Result'))

    reg.add_module(Transpose)
    reg.add_input_port(Transpose, "InputMatrix", (Matrix, 'Input Matrix'))
    reg.add_output_port(Transpose, "OutputMatrix", (Matrix, 'Output Matrix'))

    reg.add_module(MatrixMultiply)
    reg.add_input_port(MatrixMultiply, "InputMatrix1", (Matrix, 'Input Matrix 1'))
    reg.add_input_port(MatrixMultiply, "InputMatrix2", (Matrix, 'Input Matrix 2'))
    reg.add_output_port(MatrixMultiply, "OutputMatrix", (Matrix, 'Output Matrix'))

    reg.add_module(ElementMultiply)
    reg.add_input_port(ElementMultiply, "InputMatrix1", (Matrix, 'Input Matrix 1'))
    reg.add_input_port(ElementMultiply, "InputMatrix2", (Matrix, 'Input Matrix 2'))
    reg.add_output_port(ElementMultiply, "OutputMatrix", (SparseMatrix, 'Output Matrix'))

    reg.add_module(ATan2)
    reg.add_input_port(ATan2, "InputMatrix", (SparseMatrix, 'Complex Matrix'))
    reg.add_input_port(ATan2, "RealMatrix", (SparseMatrix, 'Real Matrix'), True)
    reg.add_input_port(ATan2, "ImaginaryMatrix", (SparseMatrix, 'Imaginary Matrix'), True)
    reg.add_output_port(ATan2, "Output", (SparseMatrix, 'Output Matrix'))

    reg.add_module(FFT)
    reg.add_input_port(FFT, "Signals", (Matrix, 'Input Signal Matrix'))
    reg.add_input_port(FFT, "FFT Samples", (basic.Integer, 'FFT Samples'))
    reg.add_output_port(FFT, "FFT Output", (SparseMatrix, 'FFT Output'))

    reg.add_module(FFT2)
    reg.add_input_port(FFT2, "Signals", (Matrix, 'Input Signal Matrix'))
    reg.add_output_port(FFT2, "FFT Output", (SparseMatrix, 'FFT Output'))

    reg.add_module(WindowedFourierTransform)
    reg.add_input_port(WindowedFourierTransform, "Signal", (Matrix, 'Input Signal'))
    reg.add_input_port(WindowedFourierTransform, "Sampling Rate", (basic.Integer, 'Sampling Rate'))
    reg.add_input_port(WindowedFourierTransform, "Window Size", (basic.Integer, 'Window Size'), True)
    reg.add_input_port(WindowedFourierTransform, "Stride", (basic.Integer, 'Window Stride'), True)
    reg.add_output_port(WindowedFourierTransform, "FFT Output", (SparseMatrix, 'FFT Output'))

    reg.add_module(ShortTimeFourierTransform)
    reg.add_input_port(ShortTimeFourierTransform, "Signal", (Matrix, 'Input Signal'))
    reg.add_input_port(ShortTimeFourierTransform, "Sampling Rate", (basic.Integer, 'Sampling Rate'))
    reg.add_input_port(ShortTimeFourierTransform, "Stride", (basic.Integer, 'Window Stride'))
    reg.add_input_port(ShortTimeFourierTransform, "Window", (Matrix, 'Window Function'), True)
    reg.add_input_port(ShortTimeFourierTransform, "WindowSize", (basic.Integer, 'Window Size'))
    reg.add_output_port(ShortTimeFourierTransform, "FFT Output", (SparseMatrix, 'FFT Output'))
    reg.add_output_port(ShortTimeFourierTransform, "Signal Output", (SparseMatrix, 'Signal Output'), True)
    
    reg.add_module(vtkDataSetToMatrix)
    reg.add_input_port(vtkDataSetToMatrix, "vtkUnstructuredGrid", (reg.get_descriptor_by_name('edu.utah.sci.vistrails.vtk', 'vtkAlgorithmOutput').module, 'Input Unstructured Grid'))
    reg.add_output_port(vtkDataSetToMatrix, "Output Matrix", (SparseMatrix, 'Output Matrix'))

    reg.add_module(PhaseHistogramToVTKPoints)
    reg.add_input_port(PhaseHistogramToVTKPoints, "FFT Input", (SparseMatrix, 'FFT Input'))
    reg.add_input_port(PhaseHistogramToVTKPoints, "Num Bins", (basic.Integer, 'Number of Phase Bins'))
    reg.add_output_port(PhaseHistogramToVTKPoints, "Num Slices", (basic.Integer, 'Number of Histogram Timeslices'), True)
    reg.add_output_port(PhaseHistogramToVTKPoints, "Phase Histogram", (SparseMatrix, 'Phase Histogram'), True)
    reg.add_output_port(PhaseHistogramToVTKPoints, "Phase Geometry", (reg.get_descriptor_by_name('edu.utah.sci.vistrails.vtk', 'vtkAlgorithmOutput').module, 'Phase Geometry Connection'))

def package_dependencies():
    import core.packagemanager
    manager = core.packagemanager.get_package_manager()
    if manager.has_package('edu.utah.sci.vistrails.vtk'):
        return ['edu.utah.sci.vistrails.vtk']
    else:
        return []
