from PyQt4 import QtCore, QtGui
from packages.spreadsheet.spreadsheet_controller import spreadsheetController
from packages.spreadsheet.spreadsheet_event import DisplayCellEvent
from cdat_cell import QCDATWidget
import cdms2
import core.modules.module_registry
import core.modules.vistrails_module
from logging import debug, warn
from core.vistrail.connection import Connection
from core.vistrail.port import Port

def setup_open_call(filename, variable, plotType):
    """ hack to see if the `api' module works better."""
    import api

    cdat_id = "edu.utah.sci.vistrails.cdat"

#    api.get_current_vistrail()
    filename=QtCore.QString('/local/dev/vt/cdat/Packages/dat/clt.nc')
    variable=QtCore.QString('clt')

    hvo_cdat = "edu.utah.sci.vistrails.hvo.cdat"
    # Create all our modules.
    m_open = api.add_module(0,400, cdat_id, 'open', "cdms2")
    m_call = api.add_module(10,300, cdat_id, '__call__', "cdms2|dataset")
    m_quickplot = api.add_module(0,200, hvo_cdat, 'quickplot', 'cdat')

    reg = api.get_module_registry()

    debug("giving fn of: %s" % filename)
    api.get_current_controller().update_function(m_open,'uri', [filename])
    api.get_current_controller().update_function(m_quickplot,'plot',
                                                 [plotType])
    api.get_current_controller().update_function(m_call,'id',
                                                 [variable])

    # get all the ports so we can ...
    open_out = reg.get_port_spec(cdat_id, 'open', 'cdms2', 'dataset', 'output')
    call_in = reg.get_port_spec(cdat_id, '__call__', 'cdms2|dataset',
                                'cdmsfile', 'input')
    call_out = reg.get_port_spec(cdat_id, '__call__', 'cdms2|dataset',
                                 'variable', 'output')

    quickplot_in_var = reg.get_port_spec(hvo_cdat, 'quickplot', 'cdat',
                                         'variable', 'input')
    quickplot_in_ds = reg.get_port_spec(hvo_cdat, 'quickplot', 'cdat',
                                        'dataset', 'input')
    quickplot_in_cvs = reg.get_port_spec(hvo_cdat, 'quickplot', 'cdat',
                                         'plot', 'input')

    # ... connect them!
    cnxns = (
        (m_open,open_out, m_call,call_in),
        (m_call,call_out, m_quickplot,quickplot_in_ds),
    )
#        (m_isoline,isoline_cvs_out, m_quickplot,quickplot_in_cvs)
#        (m_isofill,isofill_out, m_isoline,isoline_in2)
#        (m_call,call_out, m_quickplot,quickplot_in_ds),
    [api.add_connection(c[0].id,c[1], c[2].id,c[3]) for c in cnxns]

    api.switch_to_pipeline_view()

class QCDATWindow(QtGui.QWidget):

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setWindowTitle('CDAT')
        gridLayout = QtGui.QGridLayout(self)
        self.setLayout(gridLayout)

        label = QtGui.QLabel('File Name')
        gridLayout.addWidget(label, 0, 0)

        self.fileNameEdit = QtGui.QLineEdit()
        gridLayout.addWidget(self.fileNameEdit, 0, 1)

        self.selectFileButton = QtGui.QToolButton()
        self.selectFileButton.setText('. . .')
        gridLayout.addWidget(self.selectFileButton, 0, 2)

        label = QtGui.QLabel('Variable')
        gridLayout.addWidget(label, 1, 0)

        self.variableCombo = QtGui.QComboBox()
        gridLayout.addWidget(self.variableCombo, 1, 1)

        label = QtGui.QLabel('Plot Type')
        gridLayout.addWidget(label, 2, 0)

        self.plotTypeCombo = QtGui.QComboBox()
        self.plotTypeCombo.addItems(QtCore.QStringList(['Boxfill', 'Isofill', 'Isoline']))
        gridLayout.addWidget(self.plotTypeCombo, 2, 1)
        
        self.sendButton = QtGui.QPushButton('Send To Spreadsheet')
        gridLayout.addWidget(self.sendButton, 3, 0, 1, 3)

        self.connect(self.selectFileButton, QtCore.SIGNAL('clicked()'), self.selectFile)
        self.connect(self.fileNameEdit, QtCore.SIGNAL('editingFinished()'), self.updateVariableList)
        self.connect(self.sendButton, QtCore.SIGNAL('clicked()'), self.sendToSpreadsheet)

    def selectFile(self):
        open_fn = QtGui.QFileDialog.getOpenFileName
        fileName = open_fn(self, 'Select CDAT data file', '.',
                           "CDAT data (*.cdms *.ctl *.dic *.hdf *.nc *.xml)")

        if not fileName.isNull():
            self.fileNameEdit.setText(fileName)
            self.updateVariableList()


    def getCurrentFileName(self):
        return str(self.fileNameEdit.text())
        
    def getCurrentVariable(self):
        return str(self.variableCombo.currentText())
        
    def getCurrentPlotType(self):
        return str(self.plotTypeCombo.currentText())
        
    def sendToSpreadsheet(self):
        import api
        api.get_current_controller().change_selected_version(0)
        reg = core.modules.module_registry.get_module_registry()
        setup_open_call(self.getCurrentFileName(), self.getCurrentVariable(), self.getCurrentPlotType())
        api.get_current_controller().execute_current_workflow()

    def updateVariableList(self):
        fn = self.getCurrentFileName()
        if QtCore.QFile(fn).exists():
            data = cdms2.open(fn)
            self.variableCombo.clear()
            self.variableCombo.addItems(QtCore.QStringList(data.listvariables()))        
