import cdms2
import cdms2.error

from PyQt4 import QtCore, QtGui

from dat.packages import Plot, DataPort, \
    Variable, FileVariableLoader, VariableOperation, OperationArgument, \
    translate, derive_varname


__all__ = ['_plots', '_variable_loaders']


_ = translate('packages.uvcdat_cdms')

# Builds a DAT variable from a data file
variable_type = 'gov.llnl.uvcdat.cdms:CDMSVariable'

def build_variable(filename, varname):
    var = Variable(type=variable_type)
    # We use the high-level interface to build the variable pipeline
    varmod = var.add_module(variable_type)
    varmod.add_function('file', 'basic:File', filename)
    varmod.add_function('name', 'basic:String', varname)
    # We select the 'self' output port of the CDMSVariable module as the port
    # that will be connected to plots when this variable is used
    var.select_output_port(varmod, 'self')
    return var

########################################
# Defines a plot from a subworkflow file
#
_plots = [
    Plot(name="3D_Scalar",
         subworkflow='{package_dir}/dat-plots/CDMS3D_Scalar.xml',
         description=_("3D_Scalar/default plot"),
         ports=[DataPort(name='variable', type=variable_type,
                         multiple_values=True)])
]

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
        names = sorted(f.variables)

        self._name_field = QtGui.QComboBox()
        for name in sorted(f.variables):
            self._name_field.addItem(name)
        self.connect(self._name_field,
                     QtCore.SIGNAL('currentIndexChanged(const QString&)'),
                     self._var_changed)
        self._var_changed(self._name_field.currentText())

        layout = QtGui.QFormLayout()
        layout.addRow(_("Variable &name:"), self._name_field)
        self.setLayout(layout)

    def _var_changed(self, varname):
        self._varname = derive_varname(self.filename, remove_ext=True,
                                       remove_path=True, prefix="cdms_",
                                       suffix='_%s' % varname.decode('utf-8'))
        self.default_variable_name_changed(self._varname)

    def load(self):
        varname = self._name_field.currentText().encode('utf-8')
        return build_variable(self.filename, varname)

    def get_default_variable_name(self):
        return self._varname

_variable_loaders = {
    CDMSLoader: _("CDAT data"),
}
