import cdms2
import cdms2.error

from PyQt4 import QtCore, QtGui

import axesWidgets

from dat.packages import Plot, DataPort, Variable, FileVariableLoader, \
    translate, derive_varname
from dat.vistrails_interface import ConstantPort


__all__ = ['_plots', '_variable_loaders']


_ = translate('packages.uvcdat_cdms')

# Builds a DAT variable from a data file
variable_type = 'gov.llnl.uvcdat.cdms:CDMSVariable'


def build_variable(filename, varname, axes_kwargs):
    var = Variable(type=variable_type)
    # We use the high-level interface to build the variable pipeline
    varmod = var.add_module(variable_type)
    varmod.add_function('file', 'basic:File', filename)
    varmod.add_function('name', 'basic:String', varname)

    def get_kwargs_str(kwargs_dict):
        kwargs_str = ""
        for k, v in kwargs_dict.iteritems():
            if k == 'order':
                o = kwargs_dict[k]
                skip = True
                for i in range(len(o)):
                    if int(o[i])!=i:
                        skip = False
                        break
                if skip:
                    continue
            kwargs_str += "%s=%s," % (k, repr(v))
        return kwargs_str
    varmod.add_function('axes', 'basic:String', get_kwargs_str(axes_kwargs))

    # We select the 'self' output port of the CDMSVariable module as the port
    # that will be connected to plots when this variable is used
    var.select_output_port(varmod, 'self')
    return var


########################################
# Defines plots
#

_plots = []

for plot_type in ('Boxfill', 'Isofill', 'Isoline', 'Meshfill',
                  'Scatter', 'Taylordiagram', 'Vector',
                  'XvsY', 'Xyvsy', 'Yxvsx',
                  '3D_Scalar', '3D_Dual_Scalar', '3D_Vector'):
    pipeline = ('python_lists', [
            ('InputPort', 'org.vistrails.vistrails.basic', [
                ('name', [('String', 'variable')]),
                ('spec', [('String', 'gov.llnl.uvcdat.cdms:CDMSVariable')]),
            ]),
            ('InputPort', 'org.vistrails.vistrails.basic', [
                ('name', [('String', 'graphics method')]),
                ('spec', [('String', 'basic:String')]),
                ('Default', [('String', 'default')]),
            ]),
            ('CDMS' + plot_type, 'gov.llnl.uvcdat.cdms', []),
            ('CDMSCell', 'gov.llnl.uvcdat.cdms', []),
        ], [
            (0, 'InternalPipe', 2, 'variable'),
            (1, 'InternalPipe', 2, 'graphicsMethodName'),
            (2, 'self', 3, 'plot'),
        ])
    _plots.append(Plot(plot_type, pipeline=pipeline, ports=[
        DataPort(name='variable',
                 type='gov.llnl.uvcdat.cdms:CDMSVariable'),
        ConstantPort(name='graphics method',
                     type='basic:String')]))


########################################
# Defines a variable loader
#

class CDMSLoader(FileVariableLoader):
    """Loads a VTK dataset.
    """
    @classmethod
    def can_load(cls, filename):
        try:
            cdms2.open(filename)
        except cdms2.error.CDMSError:
            return False
        return True

    def __init__(self, filename):
        FileVariableLoader.__init__(self)
        self.filename = filename

        f = cdms2.open(filename)

        self._name_field = QtGui.QComboBox()
        for name in sorted(f.variables):
            self._name_field.addItem(name)
        self.connect(self._name_field,
                     QtCore.SIGNAL('currentIndexChanged(const QString&)'),
                     self._var_changed)

        layout = QtGui.QFormLayout()
        layout.addRow(_("Variable &name:"), self._name_field)

        # dimensions
        self.dims=QtGui.QFrame()
        self.dimsLayout=QtGui.QVBoxLayout()
        self.dims.setLayout( self.dimsLayout )
        layout.addRow(_("&Dimensions:"), self.dims)
        # Axes
        axisList = axesWidgets.QAxisList(f, self._name_field.currentText(), self)
        axisList.setupVariableAxes()
        self.axisListHolder = axisList
        self.fillDimensionsWidget(axisList)

        self._var_changed(self._name_field.currentText())

        self.setLayout(layout)

    def _var_changed(self, varname):
        self._varname = derive_varname(self.filename, remove_ext=True,
                                       remove_path=True, prefix="cdms_",
                                       suffix='_%s' % varname.decode('utf-8'))
        self.default_variable_name_changed(self._varname)

        # Axes
        f = cdms2.open(self.filename)
        axisList = axesWidgets.QAxisList(f, varname, self)
        axisList.setupVariableAxes()
        self.axisListHolder = axisList
        self.fillDimensionsWidget(axisList)

    def load(self):
        varname = self._name_field.currentText().encode('utf-8')
        return build_variable(self.filename, varname, self.generateKwArgs())

    def get_default_variable_name(self):
        return self._varname

    def clearDimensionsWidget(self):
        if not self.axisListHolder is None:
            self.axisListHolder.destroy()
        it = self.dimsLayout.takeAt(0)
        if it: 
            it.widget().deleteLater()
    ##             it.widget().destroy()
#            self.dimsLayout.removeItem(it)
            del(it)

    def fillDimensionsWidget(self,axisList):
        self.clearDimensionsWidget()
        self.axisListHolder = axisList
        self.dimsLayout.insertWidget(0,axisList)
        #self.updateVarInfo(axisList)
        self.dims.update()
        #self.update()

    def generateKwArgs(self, axisList=None):
        """ Generate and return the variable axes keyword arguments """
        if axisList is None:
            axisList = self.dimsLayout.itemAt(0).widget()

        kwargs = {}
        for axisWidget in axisList.getAxisWidgets():
            if not axisWidget.isHidden():
                kwargs[axisWidget.axis.id] = axisWidget.getCurrentValues()

        # Generate additional args
        #kwargs['squeeze'] = 0
        kwargs['order'] = axisList.getAxesOrderString()
        return kwargs

_variable_loaders = {
    CDMSLoader: _("CDAT data"),
}
