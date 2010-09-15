import core.modules.module_registry
from core.modules.vistrails_module import Module, ModuleError
from PyQt4 import QtCore, QtGui
import api


class QCDATPVWindow(QtGui.QWidget):
    MODELLIST = ['bccr_bcm2_0','cccma_cgcm3_1','cccma_cgcm3_1_t63','cnrm_cm3',
                 'csiro_mk3_0','csiro_mk3_5','gfdl_cm2_0','gfdl_cm2_1','giss_aom',
                 'giss_model_e_h','giss_model_e_r','iap_fgoals1_0_g','ingv_echam4',
                 'inmcm3_0','ipsl_cm4','miroc3_2_hires','miroc3_2_medres','mpi_echam5',
                 'mri_cgcm2_3_2a','ncar_ccsm3_0','ncar_pcm1','ukmo_hadcm3','ukmo_hadgem1']

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setWindowTitle('ParaView CDAT Example')
        gridLayout = QtGui.QGridLayout()
        self.setLayout(gridLayout)
        
        gridLayout.addWidget(QtGui.QLabel('Model 1'), 0, 0)
        gridLayout.addWidget(QtGui.QLabel('Model 2'), 1, 0)
        gridLayout.addWidget(QtGui.QLabel('Year Begin'), 2, 0)
        gridLayout.addWidget(QtGui.QLabel('Year End'), 3, 0)

        self.model1Combo = QtGui.QComboBox()
        self.model2Combo = QtGui.QComboBox()
        self.model1Combo.addItems(QCDATPVWindow.MODELLIST)
        self.model2Combo.addItems(QCDATPVWindow.MODELLIST)
        gridLayout.addWidget(self.model1Combo, 0, 1)  
        gridLayout.addWidget(self.model2Combo, 1, 1)
        self.model1Combo.setCurrentIndex(QCDATPVWindow.MODELLIST.index('ncar_ccsm3_0'))
        self.model2Combo.setCurrentIndex(QCDATPVWindow.MODELLIST.index('mpi_echam5'))
     
        numberValidator = QtGui.QIntValidator(self)
        self.yearBeginEdit = QtGui.QLineEdit('0')
        self.yearEndEdit = QtGui.QLineEdit('0')
        self.yearBeginEdit.setValidator(numberValidator)
        self.yearBeginEdit.setValidator(numberValidator)
        gridLayout.addWidget(self.yearBeginEdit, 2, 1)
        gridLayout.addWidget(self.yearEndEdit, 3, 1)
        self.yearBeginEdit.setText('1979')
        self.yearEndEdit.setText('1980')
        
        self.runButton = QtGui.QPushButton('Run')
        gridLayout.addWidget(self.runButton, 4, 0)
        self.connect(self.runButton, QtCore.SIGNAL('clicked()'), self.runPipeline)

    def runPipeline(self):
        api.open_vistrail_from_file('/Users/hvo/src/vistrails/packages/ParaView/pvcdat.vt')
        api.select_version('Ex8')
        controller = api.get_current_controller()
        aliases = {}
        aliases['model1'] = str(self.model1Combo.currentText())
        aliases['model2'] = str(self.model2Combo.currentText())
        aliases['fromYear'] = str(self.yearBeginEdit.text())
        aliases['toYear'] = str(self.yearEndEdit.text())
        controller.execute_current_workflow(custom_aliases=aliases)

    def createModule(self):
        """ createModule() -> None
        Collect parameters, values and operator, and create a
        PythonCalc module to the current pipeline using the API
        provided in vistrails.api.

        """
        pythoncalc = "edu.utah.sci.vistrails.pythoncalc"
        module = api.add_module(0, 0, pythoncalc, 'PythonCalc', '')
        api.get_current_controller().update_function(module, 'value1',
                                                     [str(self.value1Edit.text())])
        api.get_current_controller().update_function(module, 'value2',
                                                     [str(self.value2Edit.text())])
        api.get_current_controller().update_function(module, 'op',
                                                     [str(self.opCombo.currentText())])
        api.switch_to_pipeline_view()
