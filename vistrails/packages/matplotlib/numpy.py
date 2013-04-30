from __future__ import absolute_import # 'import numpy' is not ambiguous

import csv
from itertools import izip
import numpy

from vistrails.core.modules.vistrails_module import Module, ModuleError


class NumPyArray(Module):
    """
    A Numpy Array, that can be loaded from a file.

    Declared as returning a List, but returns a Numpy array instead!
    """
    _input_ports = [
            ('file', '(org.vistrails.vistrails.basic:File)'),
            ('datatype', '(org.vistrails.vistrails.basic:String)'),
            ('shape', '(org.vistrails.vistrails.basic:List)')]
    _output_ports = [
            ('value', '(org.vistrails.vistrails.basic:List)')]

    NPY_FMT = object()

    FORMAT_MAP = dict(
               npy = NPY_FMT,

              int8 = numpy.int8,
             uint8 = numpy.uint8,
             int16 = numpy.int16,
            uint16 = numpy.uint16,
             int32 = numpy.int32,
            uint32 = numpy.uint32,
             int64 = numpy.int64,
            uint64 = numpy.uint64,

           float32 = numpy.float32,
           float64 = numpy.float64,

         complex64 = numpy.complex64,
        complex128 = numpy.complex128,
    )

    def compute(self):
        filename = self.getInputFromPort('file').name
        if self.hasInputFromPort('datatype'):
            dtype = NumPyArray.FORMAT_MAP[self.getInputFromPort('datatype')]
        else:
            if filename[-4].lower() == '.npy':
                dtype = self.NPY_FMT
            else:
                dtype = numpy.float32
        if dtype is self.NPY_FMT:
            # Numpy's ".NPY" format
            # Written with: numpy.save('xxx.npy', array)
            array = numpy.load(filename)
        else:
            # Numpy's plain binary format
            # Written with: array.tofile('xxx.dat')
            array = numpy.fromfile(filename, dtype)
        if self.hasInputFromPort('shape'):
            array.shape = tuple(self.getInputFromPort('shape'))
        self.setResult('value', array)


class CSVFile(Module):
    _input_ports = [
            ('file', '(org.vistrails.vistrails.basic:File)'),
            ('delimiter', '(org.vistrails.vistrails.basic:String)',
             {'optional': True}),
            ('header_present', '(org.vistrails.vistrails.basic:Boolean)',
             {'optional': True, 'defaults': "['True']"})]
    _output_ports = [
            ('column_count', '(org.vistrails.vistrails.basic:Integer)'),
            ('column_names', '(org.vistrails.vistrails.basic:List)'),
            ('value', '(org.vistrails.vistrails.matplotlib:CSVFile)')]

    _STANDARD_DELIMITERS = [';', ',', '\t', '|']

    def compute(self):
        csv_file = self.getInputFromPort('file').name
        self.header_present = self.getInputFromPort('header_present',
                                               allowDefault=True)
        if self.hasInputFromPort('delimiter'):
            self.delimiter = self.getInputFromPort('delimiter')
        else:
            self.delimiter = None

        self.filename = csv_file

        if self.header_present or self.delimiter is None:
            try:
                with open(csv_file, 'rb') as fp:
                    first_line = fp.readline()
                counts = [first_line.count(d)
                          for d in self._STANDARD_DELIMITERS]
                self.delimiter, count = max(
                        izip(self._STANDARD_DELIMITERS, counts),
                        key=lambda (delim, count): count)
                if count == 0:
                    raise ModuleError(self, "Couldn't guess the field delimiter")

                self.column_count = count - 1
                self.setResult('column_count', self.column_count)

                if self.header_present:
                    self.column_names = [
                            name.strip()
                            for name in first_line.split(self.delimiter)]
                    self.setResult('column_names', self.column_names)
            except IOError:
                raise ModuleError(self, "File does not exist")

        self.setResult('value', self)


class ExtractColumn(Module):
    _input_ports = [
            ('csv', CSVFile),
            ('column_name', '(org.vistrails.vistrails.basic:String)',
             {'optional': True}),
            ('column_index', '(org.vistrails.vistrails.basic:Integer)',
             {'optional': True}),
            ('numeric', '(org.vistrails.vistrails.basic:Boolean)',
             {'optional': True, 'defaults': "['True']"})]
    _output_ports = [
            ('value', '(org.vistrails.vistrails.basic:List)')]

    def compute(self):
        csv_file = self.getInputFromPort('csv')
        if self.hasInputFromPort('column_index'):
            column_index = self.getInputFromPort('column_index')
        if self.hasInputFromPort('column_name'):
            name = self.getInputFromPort('column_name')
            if isinstance(name, unicode):
                name = name.encode('utf-8')
            try:
                index = csv_file.column_names.index(name)
            except ValueError:
                try:
                    name = name.strip()
                    index = csv_file.column_names.index(name)
                except:
                    raise ModuleError(self, "Column name was not found")
            if self.hasInputFromPort('column_index'):
                if column_index != index:
                    raise ModuleError(self,
                                      "Both column_name and column_index were "
                                      "specified, and they don't agree")
        elif self.hasInputFromPort('column_index'):
            index = column_index
        else:
            raise ModuleError(self,
                              "You must set one of column_name or "
                              "column_index")

        if self.getInputFromPort('numeric', allowDefault=True):
            result = numpy.loadtxt(
                    csv_file.filename,
                    dtype=numpy.float32,
                    delimiter=csv_file.delimiter,
                    skiprows=1 if csv_file.header_present else 0,
                    usecols=[index])
        else:
            with open(csv_file.filename, 'rb') as fp:
                if csv_file.header_present:
                    fp.readline()
                reader = csv.reader(
                        fp,
                        delimiter=csv_file.delimiter)
                result = [row[index] for row in reader]

        self.setResult('value', result)


_modules = [NumPyArray, CSVFile, ExtractColumn]
