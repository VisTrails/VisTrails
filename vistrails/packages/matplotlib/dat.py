from __future__ import absolute_import # 'import dat' is not ambiguous

from PyQt4 import QtCore, QtGui

from vistrails.core.modules.basic_modules import Color, File, List, String, \
    Integer, Float

from dat.packages import Plot, DataPort, ConstantPort, Variable, \
    FileVariableLoader, VariableOperation, OperationArgument, \
    translate, derive_varname

from .numpy import NumPyArray, CSVFile
import sys


__all__ = ['_plots', '_variable_loaders', '_variable_operations']


_ = translate('packages.matplotlib')

# Builds a DAT variable from a data file
def build_variable(filename, dtype, shape=None):
    var = Variable(type=List)
    # We use the high-level interface to build the variable pipeline
    mod = var.add_module(NumPyArray)
    mod.add_function('file', File, filename)
    mod.add_function('datatype', String, dtype)
    if shape is not None:
        mod.add_function('shape', List, repr(shape))
    # We select the 'value' output port of the NumPyArray module as the
    # port that will be connected to plots when this variable is used
    var.select_output_port(mod, 'value')
    return var

########################################
# Defines plots from subworkflow files
#
_plots = [
    Plot(name="Matplotlib bar diagram",
         subworkflow='{package_dir}/dat-plots/bar.xml',
         description=_("Build a bar diagram out of two lists"),
         ports=[
             DataPort(name='left', type=List, optional=True),
             DataPort(name='height', type=List),
             ConstantPort(name='title', type=String, optional=True),
             ConstantPort(name='alpha', type=Float, optional=True),
             ConstantPort(name='facecolor', type=Color, optional=True),
             ConstantPort(name='edgecolor', type=Color, optional=True)]),
    Plot(name="Matplotlib box plot",
         subworkflow='{package_dir}/dat-plots/boxplot.xml',
         description=_("Build a box diagram out of a list of values"),
         ports=[
             DataPort(name='values', type=List),
             ConstantPort(name='title', type=String, optional=True),
             ConstantPort(name='edgecolor', type=Color, optional=True)]),
    Plot(name="Matplotlib histogram",
         subworkflow='{package_dir}/dat-plots/hist.xml',
         description=_("Build a histogram out of a list"),
         ports=[
             DataPort(name='x', type=List),
             ConstantPort(name='title', type=String, optional=True),
             ConstantPort(name='bins', type=Integer, optional=True),
             ConstantPort(name='alpha', type=Float, optional=True),
             ConstantPort(name='facecolor', type=Color, optional=True),
             ConstantPort(name='edgecolor', type=Color, optional=True)]),
    Plot(name="Matplotlib image",
         subworkflow='{package_dir}/dat-plots/imshow.xml',
         description=_("Shows a 2D MxN or MxNx3 matrix as an image"),
         ports=[
             DataPort(name='matrix', type=List),
             ConstantPort(name='title', type=String, optional=True)]),
    Plot(name="Matplotlib line plot",
         subworkflow='{package_dir}/dat-plots/line.xml',
         description=_("Build a plot out of two lists"),
         ports=[
             DataPort(name='x', type=List, optional=True),
             DataPort(name='y', type=List),
             ConstantPort(name='title', type=String, optional=True),
             ConstantPort(name='marker', type=String, optional=True),
             ConstantPort(name='markercolor', type=Color, optional=True),
             ConstantPort(name='edgecolor', type=Color, optional=True)]),
    Plot(name="Matplotlib pie diagram",
         subworkflow='{package_dir}/dat-plots/pie.xml',
         description=_("Build a pie diagram out of a list of values"),
         ports=[
             DataPort(name='x', type=List),
             ConstantPort(name='title', type=String, optional=True)]),
    Plot(name="Matplotlib polar plot",
         subworkflow='{package_dir}/dat-plots/polar.xml',
         description=_("Build a plot out of two lists"),
         ports=[
             DataPort(name='r', type=List),
             DataPort(name='theta', type=List),
             ConstantPort(name='title', type=String, optional=True),
             ConstantPort(name='marker', type=String, optional=True),
             ConstantPort(name='markercolor', type=Color, optional=True),
             ConstantPort(name='edgecolor', type=Color, optional=True)]),
]

########################################
# Defines variable loaders
#

# Loads from a raw binary file
class BinaryArrayLoader(FileVariableLoader):
    """Loads a NumPy array using numpy:fromfile().
    """
    FORMATS = [
            ("%s (%s)" % (_("byte"), 'numpy.int8'),
             'int8'),
            ("%s (%s)" % (_("unsigned byte"), 'numpy.uint8'),
             'uint8'),
            ("%s (%s)" % (_("short"), 'numpy.int16'),
             'int16'),
            ("%s (%s)" % (_("unsigned short"), 'numpy.uint16'),
             'uint16'),
            ("%s (%s)" % (_("32-bit integer"), 'numpy.int32'),
             'int32'),
            ("%s (%s)" % (_("32-bit unsigned integer"), 'numpy.uint32'),
             'uint32'),
            ("%s (%s)" % (_("64-bit integer"), 'numpy.int64'),
             'int64'),
            ("%s (%s)" % (_("64-bit unsigned integer"), 'numpy.uint64'),
             'uint64'),

            ("%s (%s)" % (_("32-bit floating number"), 'numpy.float32'),
             'float32'),
            ("%s (%s)" % (_("64-bit floating number"), 'numpy.float64'),
             'float64'),
            ("%s (%s)" % (_("128-bit floating number"), 'numpy.float128'),
             'float128'),

            ("%s (%s)" % (_("64-bit complex number"), 'numpy.complex64'),
             'complex64'),
            ("%s (%s)" % (_("128-bit complex number"), 'numpy.complex128'),
             'complex128'),
            ("%s (%s)" % (_("256-bit complex number"), 'numpy.complex256'),
             'complex128'),
    ]

    @classmethod
    def can_load(cls, filename):
        return (filename.lower().endswith('.dat') or
                filename.lower().endswith('.ima'))

    def __init__(self, filename):
        FileVariableLoader.__init__(self)
        self.filename = filename
        self._varname = derive_varname(filename, remove_ext=True,
                                       remove_path=True, prefix="nparray_")

        layout = QtGui.QFormLayout()

        self._format_field = QtGui.QComboBox()
        for label, dtype in BinaryArrayLoader.FORMATS:
            self._format_field.addItem(label)
        layout.addRow(_("Data &format:"), self._format_field)

        self._shape = QtGui.QLineEdit()
        layout.addRow(_("&Shape:"), self._shape)
        shape_label = QtGui.QLabel(_("Comma-separated list of dimensions"))
        label_font = shape_label.font()
        label_font.setItalic(True)
        shape_label.setFont(label_font)
        layout.addRow('', shape_label)

        self.setLayout(layout)

    def load(self):
        shape = str(self._shape.text())
        if not shape:
            shape = None
        else:
            shape = [int(d.strip()) for d in shape.split(',')]
        return build_variable(
                self.filename,
                BinaryArrayLoader.FORMATS[
                        self._format_field.currentIndex()][1],
                shape)

    def get_default_variable_name(self):
        return self._varname

# Loads from a NPY array
def npy_load(self, filename):
    return build_variable(filename, 'npy')
def npy_get_varname(filename):
    return derive_varname(filename, remove_ext=True,
                          remove_path=True, prefix="nparray_")
NPYArrayLoader = FileVariableLoader.simple(
        extension='.npy',
        load=npy_load,
        get_varname=npy_get_varname)

# Loads from a CSV file
class CSVLoader(FileVariableLoader):
    @classmethod
    def can_load(cls, filename):
        return filename.lower().endswith('.csv')

    def __init__(self, filename):
        FileVariableLoader.__init__(self)
        self._filename = filename

        # Defaults
        self._delimiter = None
        self._header_present = True

        layout = QtGui.QVBoxLayout()
        options = QtGui.QFormLayout()

        # header_present
        self._header_present_checkbox = QtGui.QCheckBox()
        self._header_present_checkbox.setChecked(True)
        def header_present_cb(state):
            self._header_present = state == QtCore.Qt.Checked
            self.read_file()
        self.connect(
                self._header_present_checkbox,
                QtCore.SIGNAL('stateChanged(int)'),
                header_present_cb)
        options.addRow(_("First line has the column names"),
                       self._header_present_checkbox)

        # delimiter, will be initialized on the first call to read_file
        self._delimiter_input = QtGui.QLineEdit()
        self._delimiter_input.setMaxLength(1)
        self._delimiter_input.setSizePolicy(
                QtGui.QSizePolicy.Fixed,
                self._delimiter_input.sizePolicy().verticalPolicy())
        def delimiter_cb(text):
            self._delimiter = str(text)
            self.read_file()
        self.connect(
                self._delimiter_input,
                QtCore.SIGNAL('textChanged(QString)'),
                delimiter_cb)
        options.addRow(_("Column separator:"), self._delimiter_input)

        # numeric, checked by default
        self._numeric_checkbox = QtGui.QCheckBox()
        self._numeric_checkbox.setChecked(True)
        options.addRow(_("load as Numpy array:"), self._numeric_checkbox)

        layout.addLayout(options)

        # Range selector
        self._range1 = QtGui.QSpinBox()
        self._range1.setRange(0, sys.maxint)
        self._range2 = QtGui.QSpinBox()
        self._range2.setRange(0, sys.maxint)
        self._range2.setSpecialValueText(_("end"))
        range_layout = QtGui.QHBoxLayout()
        range_layout.addWidget(self._range1)
        range_layout.addWidget(QtGui.QLabel('-'))
        range_layout.addWidget(self._range2)
        options.addRow(_("Range of rows to load:"), range_layout)

        self._table = QtGui.QTableWidget()
        layout.addWidget(self._table)

        self.setLayout(layout)

        self.read_file()

    def read_file(self):
        column_count, column_names, self._delimiter = CSVFile.read_file(
                self._filename,
                self._delimiter,
                self._header_present)
        self._delimiter_input.setText(self._delimiter)
        self._table.setColumnCount(column_count)
        self._table.setRowCount(3)
        if column_names is not None:
            for col, name in enumerate(column_names):
                item = QtGui.QTableWidgetItem(name)
                font = item.font()
                font.setBold(True)
                item.setFont(font)
                self._table.setItem(0, col, item)
        with open(self._filename, 'rb') as fp:
            if self._header_present:
                fp.readline()
            for row in xrange(1 if column_names is not None else 0, 3):
                line = fp.readline()
                line = line.split(self._delimiter)
                for col in xrange(min(column_count, len(line))):
                    item = QtGui.QTableWidgetItem(line[col])
                    self._table.setItem(row, col, item)

_variable_loaders = {
        BinaryArrayLoader: _("Numpy plain binary array"),
        NPYArrayLoader: _("Numpy .NPY format"),
        CSVLoader: _("CSV table")
}

########################################
# Defines variable operations
#
_variable_operations = [
    VariableOperation(
        '*',
        subworkflow='{package_dir}/dat-operations/scale_array.xml',
        args=[
            OperationArgument('array', List),
            OperationArgument('num', Float),
        ],
        return_type=List,
        symmetric=True),
]
