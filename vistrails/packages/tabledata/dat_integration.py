import sys

from PyQt4 import QtCore, QtGui

from vistrails.core.modules.basic_modules import Boolean, File, Float, \
    Integer, List, String

from dat.packages import Variable, FileVariableLoader, VariableOperation, \
    OperationArgument, translate, derive_varname

from read.read_csv import CSVFile, ExtractColumn
from read.read_numpy import NumPyArray


__all__ = ['_variable_loaders', '_variable_operations']


_ = translate('packages.tabledata')


# Builds a DAT variable from a data file
def build_file_variable(filename, dtype, shape=None):
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

def build_csv_variable(filename, delimiter, header_present, column, numeric):
    var = Variable(type=List)

    csvfile = var.add_module(CSVFile)
    csvfile.add_function('file', File, filename)
    if delimiter is not None:
        csvfile.add_function('delimiter', String, delimiter)
    csvfile.add_function('header_present', Boolean, header_present)

    extract = var.add_module(ExtractColumn)
    csvfile.connect_outputport_to('value', extract, 'csv')
    if isinstance(column, (int, long)):
        extract.add_function('column_index', Integer, column)
    else:
        extract.add_function('column_name', String, column)
    extract.add_function('numeric', Boolean, numeric)

    var.select_output_port(extract, 'value')
    return var


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
        return build_file_variable(
                self.filename,
                BinaryArrayLoader.FORMATS[
                        self._format_field.currentIndex()][1],
                shape)

    def get_default_variable_name(self):
        return self._varname


# Loads from a NPY array
def npy_load(self, filename):
    return build_file_variable(filename, 'npy')
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
        self._column_names = None
        self._selected_column = None
        self._varname = derive_varname("csv_data")

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
        range_layout.addStretch()
        range_layout.addWidget(QtGui.QLabel('-'))
        range_layout.addStretch()
        range_layout.addWidget(self._range2)
        options.addRow(_("Range of rows to load:"), range_layout)

        self._table = QtGui.QTableWidget()
        self._table.setSelectionBehavior(QtGui.QTableWidget.SelectColumns)
        self._table.setSelectionMode(QtGui.QTableWidget.SingleSelection)
        self.connect(self._table, QtCore.SIGNAL('itemSelectionChanged()'),
                     self._selection_changed)
        layout.addWidget(self._table)

        self.setLayout(layout)

        self.read_file()

    def read_file(self):
        column_count, self._column_names, self._delimiter = CSVFile.read_file(
                self._filename,
                self._delimiter,
                self._header_present)
        self._delimiter_input.setText(self._delimiter)
        self._table.setColumnCount(column_count)
        self._table.setRowCount(3)
        if self._column_names is not None:
            for col, name in enumerate(self._column_names):
                item = QtGui.QTableWidgetItem(name)
                font = item.font()
                font.setBold(True)
                item.setFont(font)
                self._table.setItem(0, col, item)
        with open(self._filename, 'rb') as fp:
            if self._header_present:
                fp.readline()
            for row in xrange(1 if self._column_names is not None else 0, 3):
                line = fp.readline()
                line = line.split(self._delimiter)
                for col in xrange(min(column_count, len(line))):
                    item = QtGui.QTableWidgetItem(line[col])
                    self._table.setItem(row, col, item)

        self._table.clearSelection()

    def _selection_changed(self):
        selected = self._table.selectedRanges()
        if selected:
            selected = selected[0]
            self._selected_column = selected.leftColumn()
            if self._column_names is not None:
                column = derive_varname(
                        self._column_names[self._selected_column])
            else:
                column = "col%d" % self._selected_column
            self._varname = derive_varname(self._filename, remove_ext=True,
                                           remove_path=True,
                                           suffix='_%s' % column)
            self.default_variable_name_changed(self._varname)
        else:
            self.default_variable_name_changed('csv_data')
            self._selected_column = None

    def load(self):
        if self._selected_column is None:
            QtGui.QMessageBox.warning(
                    self,
                    _("Error"),
                    _("You must select a column to load"))
            return
        if self._header_present:
            column = self._column_names[self._selected_column]
        else:
            column = self._selected_column
        return build_csv_variable(
                self._filename,
                self._delimiter,
                self._header_present,
                column,
                self._numeric_checkbox.isChecked())

    def get_default_variable_name(self):
        return self._varname


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
