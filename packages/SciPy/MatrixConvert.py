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
from Matrix import Matrix, COOMatrix, SparseMatrix, CSRMatrix
from scipy import sparse
import numpy, scipy

class MatrixConvert(SciPy):

    def compute(self):
        m = self.getInputFromPort("InputMatrix")
        to = self.getInputFromPort("OutputType")

        to = to.upper()
        if to == 'Dense':
            self.matrix = DenseMatrix(m.matrix.todense())
            self.setResult("SparseOutput", self.matrix)
        else:
            self.matrix = SparseMatrix(m.matrix.tocsc())
            self.setResult("SparseOutput", self.matrix)

class vtkDataSetToMatrix(SciPy):
    ''' In some cases, particularly in terms of user-defined VTK Filters, the
        output of the filter is a vtk datatype representing '''
    
    def from_unstructured_grid(self, vtkalgout):
        import vtk
        prod = vtkalgout.vtkInstance.GetProducer()
        prod.Update()
        grid = prod.GetOutput()
        pt_set = grid.GetPoints()
        scalars = grid.GetPointData().GetScalars()

        ''' Points in vtk are always 3D... so we must assume this. '''
        self.matrix_ = SparseMatrix()
        self.matrix_.matrix = sparse.csc_matrix((grid.GetNumberOfPoints(), 3))

        i = 0
        while i < grid.GetNumberOfPoints():
            (x,y,z) = pt_set.GetPoint(i)
            self.matrix_.matrix[i,0] = x
            self.matrix_.matrix[i,1] = y
            self.matrix_.matrix[i,2] = z
            print x, y, z
            i += 1
            
        
    def compute(self):
        if self.hasInputFromPort("vtkUnstructuredGrid"):
            self.from_unstructured_grid(self.getInputFromPort("vtkUnstructuredGrid"))
        else:
            pass

        self.setResult("Output Matrix", self.matrix_)

class PhaseHistogramToVTKPoints(SciPy):

    def form_point_set(self, histo, point_set):
        (slices, numbins) = histo.shape
        phases = numpy.arange(numbins)
        phases = phases * (360. / numbins)
        phases += phases[1] / 2.
        phi_step = phases[0]
        
        for time in xrange(slices):
            z = float(time)
            for bin in xrange(numbins):
                r = histo[time,bin]
                theta = phi_step * (bin+1)
                theta *= (scipy.pi / 180.)
                x = r*scipy.cos(theta)
                y = r*scipy.sin(theta)
                point_set.InsertNextPoint(x, y, z)

            for bin in xrange(numbins):
                curbin = bin
                lastbin = bin-1
                if lastbin < 0:
                    lastbin = numbins-1

                r = (histo[time,bin] -  histo[time,lastbin]) / 2.
                theta = curbin * 360. / numbins
                x = r*scipy.cos(theta)
                y = r*scipy.sin(theta)
                point_set.InsertNextPoint(x, y, z)
                

    def compute(self):
        import vtk
        
        phasors = self.getInputFromPort("FFT Input")
        numbins = self.getInputFromPort("Num Bins")
        phasor_matrix = phasors.matrix.toarray()
        (timeslices,phases) = phasor_matrix.shape

        point_set = vtk.vtkPoints()

        histo = numpy.zeros((timeslices, numbins))

        for time in xrange(timeslices):
            phase_slice = phasor_matrix[time,:]
            reals = phase_slice.real
            imaginary = phase_slice.imag
            phases = scipy.arctan2(imaginary, reals)
            phases = phases * (180. / scipy.pi)
            bins = phases % numbins
            for b in bins:
                histo[time,b] += 1

        self.form_point_set(histo, point_set)

        pointdata = vtk.vtkUnstructuredGrid()
        pointdata.SetPoints(point_set)

        self.surf_filter = vtk.vtkSurfaceReconstructionFilter()

        self.surf_filter.SetInput(0,pointdata)
#        self.surf_filter.Update()
        reg = core.modules.module_registry
        vtk_set = reg.registry.get_descriptor_by_name('edu.utah.sci.vistrails.vtk', 'vtkAlgorithmOutput').module()
        vtk_set.vtkInstance = self.surf_filter.GetOutputPort()

        histo_mat = SparseMatrix()
        histo_mat.matrix = sparse.csc_matrix(histo)

        self.setResult("Num Slices", timeslices)
        self.setResult("Phase Histogram", histo_mat)
        self.setResult("Phase Geometry", vtk_set)
