#test from marian
import csv
from datetime import datetime
import glob
import itertools
import os
import shutil
import sys
import subprocess
import traceback

from core.modules.vistrails_module import Module, ModuleError, ModuleConnector
from core.modules.basic_modules import File, Directory, Path, new_constant, Constant
from packages.spreadsheet.basic_widgets import SpreadsheetCell, CellLocation
from packages.spreadsheet.spreadsheet_cell import QCellWidget, QCellToolBar
#from packages.persistence.init import PersistentPath, PersistentFile, PersistentDir

from core.modules.basic_modules import List
from core.modules.basic_modules import String

from PyQt4 import QtCore, QtGui

from widgets import get_predictor_widget, get_predictor_config
from enum_widget import build_enum_widget

from SelectPredictorsLayers import SelectListDialog

import utils
#import our python SAHM Processing files
import packages.sahm.pySAHM.FieldDataQuery as FDQ
import packages.sahm.pySAHM.MDSBuilder as MDSB
import packages.sahm.pySAHM.PARC as parc
import packages.sahm.pySAHM.RasterFormatConverter as RFC
import packages.sahm.pySAHM.MaxentRunner as MaxentRunner
from SahmOutputViewer import SAHMModelOutputViewerCell
from SahmSpatialOutputViewer import SAHMSpatialOutputViewerCell 

from utils import writetolog
from pySAHM.utilities import TrappedError

from SahmSpatialOutputViewer import setQGIS

identifier = 'gov.usgs.sahm' 

def menu_items():
    """ Add a menu item which allows users to specify their session directory
    """
    def change_session_folder():
        global session_dir
        
        path = str(QtGui.QFileDialog.getExistingDirectory(None,
                                        'Browse to new session folder -'))
        session_dir = path
        utils.setrootdir(path)
        
        writetolog("*" * 79 + "\n" + "*" * 79)
        writetolog(" output directory:   " + session_dir)
        writetolog("*" * 79 + "\n" + "*" * 79)
    
    lst = []
    lst.append(("Change session folder", change_session_folder))
    return(lst)




def expand_ports(port_list):
    new_port_list = []
    for port in port_list:
        port_spec = port[1]
        if type(port_spec) == str: # or unicode...
            if port_spec.startswith('('):
                port_spec = port_spec[1:]
            if port_spec.endswith(')'):
                port_spec = port_spec[:-1]
            new_spec_list = []
            for spec in port_spec.split(','):
                spec = spec.strip()
                parts = spec.split(':', 1)
#                print 'parts:', parts
                namespace = None
                if len(parts) > 1:
                    mod_parts = parts[1].rsplit('|', 1)
                    if len(mod_parts) > 1:
                        namespace, module_name = mod_parts
                    else:
                        module_name = parts[1]
                    if len(parts[0].split('.')) == 1:
                        id_str = 'edu.utah.sci.vistrails.' + parts[0]
                    else:
                        id_str = parts[0]
                else:
                    mod_parts = spec.rsplit('|', 1)
                    if len(mod_parts) > 1:
                        namespace, module_name = mod_parts
                    else:
                        module_name = spec
                    id_str = identifier
                if namespace:
                    new_spec_list.append(id_str + ':' + module_name + ':' + \
                                             namespace)
                else:
                    new_spec_list.append(id_str + ':' + module_name)
            port_spec = '(' + ','.join(new_spec_list) + ')'
        new_port_list.append((port[0], port_spec) + port[2:])
#    print new_port_list
    return new_port_list

class FieldData(Path): 
    '''
    Field Data

    The FieldData module allows a user to add presence/absence points or count data recorded across a
    landscape for the phenomenon being modeled (e.g., plant sightings, evidence of animal presence, etc.).
    The input data for this module must be in the form of a .csv file that follows one of two formats: 

    Format 1
    A .csv file with the following column headings, in order: "X," "Y," and "responseBinary".
    In this case, the "X" field should be populated with the horizontal (longitudinal) positional
    data for a sample point. The "Y" field should be populated with the vertical (latitudinal) data
    for a sample point. These values must be in the same coordinate system/units as the template
    layer used in the workflow. The column "responseBinary" should be populated with either a '0'
    (indicating absence at the point) or a '1' (indicating presence at the point).

    Format 2
    A .csv file with the following column headings, in order: "X," "Y," and "responseCount".
    In this case, the "X" field should be populated with the horizontal (longitudinal) positional
    data for a sample point. The "Y" field should be populated with the vertical (latitudinal) data
    for a sample point. These values must be in the same coordinate system/units as the template
    layer used in the workflow. The column "responseCount" should be populated with either a '-9999'
    (indicating that the point is a background point) or a numerical value (either '0' or a positive integer)
    indicating the number of incidences of the phenomenon recorded at that point.
    '''   
#    _input_ports = [('csvFile', '(edu.utah.sci.vistrails.basic:File)')]
    _output_ports = [('value', '(gov.usgs.sahm:FieldData:DataInput)'),
                     ('value_as_string', '(edu.utah.sci.vistrails.basic:String)', True)]
    
    
    
class AggregationMethod(String):
    '''
    This module is a required class for other modules and scripts within the
    SAHM package. It is not intended for direct use or incorporation into
    the VisTrails workflow by the user.
    '''
    _input_ports = [('value', '(gov.usgs.sahm:AggregationMethod:Other)')]
    _output_ports = [('value_as_string', '(edu.utah.sci.vistrails.basic:String)', True)]
    _widget_class = build_enum_widget('AggregationMethod', 
                                      ['Mean', 'Max', 'Min', 'Majority', 'None'])

    @staticmethod
    def get_widget_class():
        return AggregationMethod._widget_class

class ResampleMethod(String):
    '''
    This module is a required class for other modules and scripts within the
    SAHM package. It is not intended for direct use or incorporation into
    the VisTrails workflow by the user.
    '''
    _input_ports = [('value', '(gov.usgs.sahm:ResampleMethod:Other)')]
    _output_ports = [('value_as_string', '(edu.utah.sci.vistrails.basic:String)', True)]
    _widget_class = build_enum_widget('ResampleMethod', 
                                      ['NearestNeighbor', 'Bilinear', 'Cubic', 'CubicSpline', 'Lanczos'])

    @staticmethod
    def get_widget_class():
        return ResampleMethod._widget_class

class Predictor(Constant):
    '''
    Predictor
    
    The Predictor module allows a user to select a single raster layer for consideration in the
    modeled analysis. Four parameters must be specified by the user:
    
    1. Aggregation Method: The aggregation method to be used in the event that the raster layer
    must be up-scaled to match the template layer (e.g., generalizing a 10 m input layer to a
    100 m output layer). Care should be taken to ensure that the aggregation method that
    best preserves the integrity of the data is used.
    
    2. Resample Method: The resample method employed to interpolate new cell values when
    transforming the raster layer to the coordinate space or cell size of the template layer,
    if necessary. 
    
    3. Categorical (Boolean): Checking this box indicates that the data contained in the raster
    layer is categorical (e.g. landcover categories). Leaving this box unchecked indicates that
    the data contained in the raster is continuous (e.g., a DEM layer). This distinction is important
    in determining an appropriate resampling method.
    
    4. File Path: The location of the raster predictor file, which a user can specify by navigating to the
    file's location on their file system. When a user is selecting an ESRI grid raster, the user should navigate
    to the 'hdr.adf' file contained within the grid folder.

    '''
    _input_ports = [('categorical', '(edu.utah.sci.vistrails.basic:Boolean)'),
                    ('ResampleMethod', '(gov.usgs.sahm:ResampleMethod:Other)', {'defaults':str(['Bilinear'])}),
                    ('AggregationMethod', '(gov.usgs.sahm:AggregationMethod:Other)', {'defaults':str(['Mean'])}),
                    ('file', '(edu.utah.sci.vistrails.basic:Path)')]
    _output_ports = [('value', '(gov.usgs.sahm:Predictor:DataInput)'),
                     ('value_as_string', '(edu.utah.sci.vistrails.basic:String)', True)]

    def compute(self):
        if (self.hasInputFromPort("ResampleMethod")):
            resampleMethod = self.getInputFromPort("ResampleMethod")
            if resampleMethod.lower() not in ['nearestneighbor', 'bilinear', 'cubic', 'cubicspline', 'lanczos']:
                raise ModuleError(self, 
                                  "Resample Method not one of 'nearestneighbor', 'bilinear', 'cubic', 'cubicspline', or 'lanczos'")
        else:
            resampleMethod = 'Bilinear'
        
        if (self.hasInputFromPort("AggregationMethod")):
            aggregationMethod = self.getInputFromPort("AggregationMethod")
            if self.getInputFromPort("AggregationMethod").lower() not in ['mean', 'max', 'min', 'majority', 'none']:
                raise ModuleError(self, "No Aggregation Method specified")
        else:
            aggregationMethod = "Mean"
        
        if (self.hasInputFromPort("categorical")):
            if self.getInputFromPort("categorical") == True:
                categorical = '1'
            else:
                categorical = '0'
        else:
            categorical = '0'
        
        if (self.hasInputFromPort("file")):
            inFile = utils.getRasterName(self.getInputFromPort("file").name)
        else:
            raise ModuleError(self, "No input file specified")
        self.setResult('value', (inFile, categorical, resampleMethod, aggregationMethod))
   
class PredictorList(Constant):
    '''
    This module is a required class for other modules and scripts within the
    SAHM package. It is not intended for direct use or incorporation into
    the VisTrails workflow by the user.
    '''
    _input_ports = expand_ports([('value', 'Other|PredictorList'),
                                 ('addPredictor', 'DataInput|Predictor')])
    _output_ports = expand_ports([('value', 'Other|PredictorList')])
    
    @staticmethod
    def translate_to_string(v):
        return str(v)

    @staticmethod
    def translate_to_python(v):
        v_list = eval(v)
        return v_list

    @staticmethod
    def validate(x):
        return type(x) == list

    def compute(self):
        p_list = self.forceGetInputListFromPort("addPredictor")
        v = self.forceGetInputFromPort("value", [])
        
        b = self.validate(v)
        if not b:
            raise ModuleError(self, "Internal Error: Constant failed validation")
        if len(v) > 0 and type(v[0]) == tuple:
            f_list = [utils.create_file_module(v_elt[1]) for v_elt in v]
        else:
            f_list = v
        p_list += f_list
        #self.setResult("value", p_list)
        self.setResult("value", v)     

class PredictorListFile(Module):
    '''
    Predictor List File

    The PredictorListFile module allows a user to load a .csv file containing a list
    of rasters for consideration in the modeled analysis. The .csv file should contain
    a header row and four columns containing the following information, in order, for
    each raster input. 
    
    Column 1: The full file path to the input raster layer.
    
    Column 2: A binary value indicating whether the input layer is categorical or not.
    A value of "0" indicates that an input raster is non-categorical data (continuous),
    while a value of "1" indicates that an input raster is categorical data.
    
    Column 3: The resampling method employed to interpolate new cell values when
    transforming the raster layer to the coordinate space or cell size of the template
    layer, if necessary. The resampling type should be specified using one of the following
    values: "nearestneighbor," "bilinear," "cubic," or "lanczos."
    
    Column 4: The aggregation method to be used in the event that the raster layer
    must be up-scaled to match the template layer (e.g., generalizing a 10 m input layer to a
    100 m output layer). Care should be taken to ensure that the aggregation method that
    best preserves the integrity of the data is used. The aggregation should be specified
    using one of the following values: "Min," "Mean," "Max," "Majority," or "None."

    In formatting the list of predictor files, the titles assigned to each of the columns
    are unimportant as the module retrieves the information based on the order of the
    values in the .csv file (the ordering of the information and the permissible values
    in the file however, are strictly enforced). The module also anticipates a header row
    and will ignore the first row in the .csv file.

    '''
    _input_ports = expand_ports([('csvFileList', '(edu.utah.sci.vistrails.basic:File)'),
                                 ('addPredictor', 'DataInput|Predictor')])
    _output_ports = expand_ports([('RastersWithPARCInfoCSV', '(gov.usgs.sahm:RastersWithPARCInfoCSV:Other)')])

    #copies the input predictor list csv to our working directory
    #and appends any additionally added predictors

    @staticmethod
    def translate_to_string(v):
        return str(v)

    @staticmethod
    def translate_to_python(v):
        v_list = eval(v)
        return v_list

    @staticmethod
    def validate(x):
        return type(x) == list

    def compute(self):
        if not (self.hasInputFromPort("csvFileList") or
                self.hasInputFromPort("addPredictor")):
            raise ModuleError(self, "No inputs or CSV file provided")

        output_fname = utils.mknextfile(prefix='PredictorList_', suffix='.csv')
        if (self.hasInputFromPort("csvFileList") and 
            os.path.exists(self.getInputFromPort("csvFileList").name)):
            shutil.copy(self.getInputFromPort("csvFileList").name, 
                output_fname)
            csv_writer = csv.writer(open(output_fname, 'ab'))
        else:
            #create an empty file to start with.
            csv_writer = csv.writer(open(output_fname, 'wb'))
            csv_writer.writerow(["file", "Resampling", "Aggregation"])
        
        if self.hasInputFromPort("addPredictor"):
            p_list = self.forceGetInputListFromPort("addPredictor")
            for p in p_list:
                if p.hasInputFromPort('resampleMethod'):
                    resMethod = p.getInputFromPort('resampleMethod')
                else:
                    resMethod = "NearestNeighbor"
                if p.hasInputFromPort('aggregationMethod'):
                    aggMethod = p.getInputFromPort('aggregationMethod')
                else:
                    aggMethod = "Mean"  
                csv_writer.writerow([os.path.normpath(p.name), resMethod, aggMethod])

        del csv_writer
        
        output_file = utils.create_file_module(output_fname)
        self.setResult('RastersWithPARCInfoCSV', output_file)
        
class TemplateLayer(Path):
    '''
    Template Layer

    The TemplateLayer is a raster data layer with a defined coordinate system, a known cell size,
    and an extent that defines the study area. This raster layer serves as the template for all
    the other inputs in the analysis. All additional raster layers used in the analysis will be
    resampled and reprojected as needed to match the template, snapped to the template, and
    clipped to have an extent that matches the template. Users should ensure that any additional
    layers considered in the analysis have coverage within the extent of the template layer.

    The TemplateLayer is a required input for the PARC module.

    '''
#    _input_ports = [('FilePath', '(edu.utah.sci.vistrails.basic:File)')]
    _output_ports = [('value', '(gov.usgs.sahm:TemplateLayer:DataInput)'),
                     ('value_as_string', '(edu.utah.sci.vistrails.basic:String)', True)]
#    def compute(self):
#        output_file = create_file_module(self.forceGetInputFromPort('FilePath', []))
#        self.setResult('value', output_file)

#class SingleInputPredictor(Predictor):
#    pass
#
#class SpatialDef(Module):
#    _output_ports = [('spatialDef', '(gov.usgs.sahm:SpatialDef:DataInput)')]

class MergedDataSet(File):
    '''
    This module is a required class for other modules and scripts within the
    SAHM package. It is not intended for direct use or incorporation into
    the VisTrails workflow by the user.
    '''
    _input_ports = expand_ports([('mdsFile', '(edu.utah.sci.vistrails.basic:File)')])
    _output_ports = expand_ports([('value', '(gov.usgs.sahm:MergedDataSet:Other)')])
    
    pass
    
class RastersWithPARCInfoCSV(File):
    '''
    This module is a required class for other modules and scripts within the
    SAHM package. It is not intended for direct use or incorporation into
    the VisTrails workflow by the user.
    '''
    _input_ports = expand_ports([('mdsFile', '(edu.utah.sci.vistrails.basic:File)')])
    _output_ports = expand_ports([('value', '(gov.usgs.sahm:MergedDataSet:Other)')])
    
    pass
#    def compute(self, is_input=None):
#        PersistentPath.compute(self, is_input, 'blob')

class ApplyModel(Module):
    '''
    Apply Model

    The ApplyModel module allows the user to apply a model developed using a
    particular package within the workflow and generate output probability and binary
    maps. The process of creating an output probability map and binary map based on
    a particular model can be time-consuming, depending on the input data. By
    existing as a stand-alone process in the workflow, the ApplyModel module allows
    a user to investigate the performance metrics for a particular model (such as
    the ROC curve or the AUC) before dedicating the processing time needed to generate
    the output maps. In most cases, a user will "fine tune" a model by exploring the
    performance metrics of different model iterations before applying the model and
    generating the actual maps as a final step.
    
    The ApplyModel module also provides the user with the option of projecting the results
    of a model developed from one set of environmental predictors onto a new modeled space
    containing that same set of environmental predictors but representing data captured at
    a different temporal or spatial location. For example, a user could generate a model
    predicting habitat suitability using recorded presence points and certain environmental
    predictors such as elevation, landcover, and proximity to water in one geographic
    location. Based on the training from this information, the modeled results could be
    generated for (or "projected to") a new location based on the range of values seen in
    elevation, landcover, and proximity to water in the second geographic area. Similarly,
    modeling predicted results through time is also possible. A model trained using field
    data and a set of predictor layers representative of one time period could be projected
    onto the same geographical area using a new set of layers corresponding to the same
    predictors but representing data from a different time period (e.g., different climate
    data).

    The ApplyModel module accepts two inputs from the user:

    1. Model Workspace: The model workspace field accepts as an input a modeling
    package element (complete with all required parameters) from upstream in the workflow.
    The inputs and specifications provided in the dialogue fields of the model will be applied
    and used to generate the output maps. A user should populate the model workspace field by
    connecting a model element to the appropriate input port of the ApplyModel module in the
    visual display of the model workflow.
    
    2. Projection Target: The projection target is an optional parameter that allows a user to
    apply a model to a particular geographic area and or set of predictors (other than those
    used to train the model) and create output maps within the spatial extent of the projection
    target layers. This input field should be populated by connecting either the output of the
    ProjectionLayers module or a separate MDSBuilder element to the appropriate input port of
    the ApplyModel module.
    
    '''
    
    _input_ports = [('projectionTarget', '(gov.usgs.sahm:MergedDataSet:Other)'),
                    ('modelWorkspace', '(edu.utah.sci.vistrails.basic:File)'),
                    ('makeBinMap', '(edu.utah.sci.vistrails.basic:Boolean)'),
                    ('makeProbabilityMap', '(edu.utah.sci.vistrails.basic:Boolean)'),]
    _output_ports = [('BinaryMap', '(edu.utah.sci.vistrails.basic:File)'), 
                     ('ProbabilityMap', '(edu.utah.sci.vistrails.basic:File)')]
    
    
    
    def compute(self):
        
        workspace = self.forceGetInputFromPort('modelWorkspace').name
        output_dname = utils.mknextdir(prefix='AppliedModel_')
        if self.hasInputFromPort('projectionTarget'):
            mdsFile = self.forceGetInputFromPort('projectionTarget').name
            args = "ws=" + '"' + workspace + '"' + " c=" + '"' + mdsFile + '"' + " o=" + '"' + output_dname + '"'
        else:
            args = "ws=" + '"' + workspace + '"' + " o=" + '"' + output_dname + '"'
        
        if self.hasInputFromPort('makeBinMap'):
            makeBinMap = self.forceGetInputFromPort('makeBinMap')
            args += ' mbt=' + str(makeBinMap).upper()
        else:
            args += ' mbt=TRUE'
            
        if self.hasInputFromPort('makeProbabilityMap'):
            makeProbabilityMap = self.forceGetInputFromPort('makeProbabilityMap')
            args += ' mpt=' + str(makeProbabilityMap).upper()
        else:
             args += ' mpt=TRUE'
                
        
        utils.runRScript('PredictModel.r', args, self)
        
        input_fname = os.path.join(output_dname, "prob_map.tif")
        output_fname = os.path.join(output_dname, 'prob_map.jpeg')
        if os.path.exists(input_fname):
            utils.tif_to_color_jpeg(input_fname, output_fname, color_breaks_csv)
            output_file1 = utils.create_file_module(output_fname)
            self.setResult('ProbabilityMap', output_file1)
        else:
            msg = "Expected output from ApplyModel was not found."
            msg += "\nThis likely indicates problems with the inputs to the R module."
            writetolog(msg, False, True)
            raise ModuleError(self, msg)
        
        if  os.path.exists(os.path.join(output_dname, "bin_map.tif")):
            outFileName = os.path.join(output_dname, "bin_map.tif")
            output_file2 = utils.create_file_module(outFileName)
            self.setResult('BinaryMap', output_file2)
        
class Model(Module):
    '''
    This module is a required class for other modules and scripts within the
    SAHM package. It is not intended for direct use or incorporation into
    the VisTrails workflow by the user.
    '''
    _input_ports = [('mdsFile', '(gov.usgs.sahm:MergedDataSet:Other)'),
                    ('makeBinMap', '(edu.utah.sci.vistrails.basic:Boolean)', {'defaults':str(['True']), 'optional':False}),
                    ('makeProbabilityMap', '(edu.utah.sci.vistrails.basic:Boolean)', {'defaults':str(['True']), 'optional':False}),
                    ('makeMESMap', '(edu.utah.sci.vistrails.basic:Boolean)', {'defaults':str(['False']), 'optional':False}),
                    ('ThresholdOptimizationMethod', '(edu.utah.sci.vistrails.basic:Integer)', {'defaults':str(['2']), 'optional':False})
                    ]
    _output_ports = [('modelWorkspace', '(edu.utah.sci.vistrails.basic:File)'), 
                     ('BinaryMap', '(edu.utah.sci.vistrails.basic:File)'), 
                     ('ProbabilityMap', '(edu.utah.sci.vistrails.basic:File)'),
                     ('AUC_plot', '(edu.utah.sci.vistrails.basic:File)'),
                     ('ResponseCurves', '(edu.utah.sci.vistrails.basic:File)'),
                     ('Text_Output', '(edu.utah.sci.vistrails.basic:File)')]

    def compute(self):
        global color_breaks_csv
        
        ModelOutput = {"FIT_BRT_pluggable.r":"brt",
                       "FIT_GLM_pluggable.r":"glm",
                       "FIT_RF_pluggable.r":"rf",
                       "FIT_MARS_pluggable.r":"mars"}
        ModelAbbrev = ModelOutput[self.name]
        
        output_dname = utils.mknextdir(prefix=ModelAbbrev + 'output_')
        argsDict = utils.map_ports(self, self.port_map)
        mdsFile = self.forceGetInputFromPort('mdsFile').name
        
        args = ''
        for k, v in argsDict.iteritems():
            if k == 'c':
                args += ' ' + '='.join([str(k),'"' + str(v) + '"'])
            else:
                args += ' ' + '='.join([str(k),str(v)])
        args += " o=" + '"' + output_dname + '"'
        args += " rc=" + utils.MDSresponseCol(mdsFile)
#        if self.hasInputFromPort('makeBinMap'):
#            makeBinMap = self.forceGetInputFromPort('makeBinMap')
#            args += ' mbt=' + str(makeBinMap).upper()
#        else:
#            makeBinMap = True
#            args += ' mbt=TRUE'
#            
#        if self.hasInputFromPort('makeProbabilityMap'):
#            makeProbabilityMap = self.forceGetInputFromPort('makeProbabilityMap')
#            args += ' mpt=' + str(makeProbabilityMap).upper()
#        else:
#            makeProbabilityMap = True
#            args += ' mpt=TRUE'  
#        
#        if self.hasInputFromPort('seed'):
#            args += ' seed=' + str(self.forceGetInputFromPort('seed'))
#        
#        if self.hasInputFromPort('someParam'):
#            x = self.forceGetInputFromPort('someParam')
#            if x > 1:
#                msg = "Expected output from " + ModelAbbrev + " was not found."
#                msg += "\nThis likely indicates problems with the inputs to the R module."
#                writetolog(msg, False, True)
#            args += " abr=" + x
                
        utils.runRScript(self.name, args, self)
#        utils.runRScript('FIT_BRT_pluggableErrorMessage.r', args, self)
        
        input_fname = os.path.join(output_dname, ModelAbbrev + "_prob_map.tif")
        output_fname = os.path.join(output_dname, ModelAbbrev + "_prob_map.jpeg")
        if os.path.exists(input_fname):
#            utils.tif_to_color_jpeg(input_fname, output_fname, color_breaks_csv)
#            output_file4 = utils.create_file_module(output_fname)
            self.setResult('ProbabilityMap', input_fname)
        elif (argsDict.has_key('mpt') and argsDict['mpt'] == True) or \
            not argsDict.has_key('mpt'):
            msg = "Expected output from " + ModelAbbrev + " was not found."
            msg += "\nThis might indicate problems with the inputs to the R module."
            msg += "\nCheck the console output for additional R warnings "
            writetolog(msg, False, True)
            raise ModuleError(self, msg)
        
        if (argsDict.has_key('mbt') and argsDict['mbt'] == True) or \
            not argsDict.has_key('mbt'):
            outFileName = os.path.join(output_dname, ModelAbbrev + "_bin_map.tif")
            output_file1 = utils.create_file_module(outFileName)
            self.setResult('BinaryMap', output_file1)
        
        outFileName = os.path.join(output_dname, ModelAbbrev + "_output.txt")
        output_file2 = utils.create_file_module(outFileName)
        self.setResult('Text_Output', output_file2)
        
        outFileName = os.path.join(output_dname, ModelAbbrev + "_auc_plot.jpg")
#        print "out auc: ", outFileName
        output_file3 = utils.create_file_module(outFileName)
        self.setResult('AUC_plot', output_file3)
        
        outFileName = os.path.join(output_dname, ModelAbbrev + "_response_curves.pdf")
        output_file5 = utils.create_file_module(outFileName)
        self.setResult('ResponseCurves', output_file5)
        
        outFileName = os.path.join(output_dname, "modelWorkspace")
#        print "out auc: ", outFileName
        output_file6 = utils.create_file_module(outFileName)
        self.setResult('modelWorkspace', output_file6)
        
        writetolog("Finished " + ModelAbbrev   +  " builder\n", True, True) 
        
class GLM(Model):
    _input_ports = list(Model._input_ports)
    _input_ports.extend([('ModelFamily', '(edu.utah.sci.vistrails.basic:String)', {'defaults':str(['binomial']), 'optional':True}),
                         ('SimplificationMethod', '(edu.utah.sci.vistrails.basic:String)', {'defaults':str(['AIC']), 'optional':True}),
                         ]) 
    def __init__(self):
        global models_path
        Model.__init__(self) 
        self.name = 'FIT_GLM_pluggable.r'
        self.port_map = {'mdsFile':('c', None, True),#These ports are for all Models
                         'makeProbabilityMap':('mpt', utils.R_boolean, False),
                         'makeBinMap':('mbt', utils.R_boolean, False),
                         'makeMESMap':('mes', utils.R_boolean, False),
                         'ThresholdOptimizationMethod':('om', None, False),
                         'ModelFamily':('mf', None, False), #This is a GLM specific port
                         'SimplificationMethod':('sm', None, False) #This is a GLM specific port
                         }

class RandomForest(Model):
    _input_ports = list(Model._input_ports)
    _input_ports.extend([('MTRY', '(edu.utah.sci.vistrails.basic:Integer)', {'defaults':str(['1']), 'optional':True}),
                         ]) 
    def __init__(self):
        global models_path
        Model.__init__(self)
        self.name = 'FIT_RF_pluggable.r'
        self.port_map = {'mdsFile':('c', None, True),#These ports are for all Models
                         'makeProbabilityMap':('mpt', utils.R_boolean, False),
                         'makeBinMap':('mbt', utils.R_boolean, False),
                         'makeMESMap':('mes', utils.R_boolean, False), 
                         'ThresholdOptimizationMethod':('om', None, False),
                         'MTRY': ('mtry', None, False) #This is a Random Forest specific port
                         }

class MARS(Model):
    _input_ports = list(Model._input_ports)
    _input_ports.extend([('MarsDegree', '(edu.utah.sci.vistrails.basic:Integer)', {'defaults':str(['1']), 'optional':True}),
                          ('MarsPenalty', '(edu.utah.sci.vistrails.basic:Integer)', {'defaults':str(['2']), 'optional':True}),
                          ])
    def __init__(self):
        global models_path        
        Model.__init__(self)
        self.name = 'FIT_MARS_pluggable.r'
        self.port_map = {'mdsFile':('c', None, True),#These ports are for all Models
                         'makeProbabilityMap':('mpt', utils.R_boolean, False),
                         'makeBinMap':('mbt', utils.R_boolean, False),
                         'makeMESMap':('mes', utils.R_boolean, False), 
                         'ThresholdOptimizationMethod':('om', None, False),
                         'MarsDegree':('deg', None, False), #This is a MARS specific port
                         'MarsPenalty':('pen', None, False), #This is a MARS specific port
                         }

class BoostedRegressionTree(Model):
    _input_ports = list(Model._input_ports)
    _input_ports.extend([('Seed', '(edu.utah.sci.vistrails.basic:Integer)', True),
                              ('TreeComplexity', '(edu.utah.sci.vistrails.basic:Integer)', True),
                              ('NumberOfTrees', '(edu.utah.sci.vistrails.basic:Integer)', {'defaults':str(['10000']), 'optional':True}),
                              ('BagFraction', '(edu.utah.sci.vistrails.basic:Float)', {'defaults':str(['0.5']), 'optional':True}),
                              ('NumberOfFolds', '(edu.utah.sci.vistrails.basic:Integer)', {'defaults':str(['3']), 'optional':True}),
                              ('Alpha', '(edu.utah.sci.vistrails.basic:Float)', {'defaults':str(['1']), 'optional':True}),
                              ('PrevalenceStratify', '(edu.utah.sci.vistrails.basic:Boolean)', {'defaults':str(['True']), 'optional':True}),
                              ('ToleranceMethod', '(edu.utah.sci.vistrails.basic:String)', {'defaults':str(['auto']), 'optional':True}),
                              ('Tolerance', '(edu.utah.sci.vistrails.basic:Float)', {'defaults':str(['0.001']), 'optional':True})
                              ])
    def __init__(self):
        global models_path
        Model.__init__(self)
        self.name = 'FIT_BRT_pluggable.r'
        self.port_map = {'mdsFile':('c', None, True),#These ports are for all Models
                         'makeProbabilityMap':('mpt', utils.R_boolean, False),
                         'makeBinMap':('mbt', utils.R_boolean, False),
                         'makeMESMap':('mes', utils.R_boolean, False), 
                         'ThresholdOptimizationMethod':('om', None, False),
                         'Seed':('seed', None, False), #This is a BRT specific port
                         'TreeComplexity':('tc', None, False), #This is a BRT specific port
                         'NumberOfTrees':('nf', None, False), #This is a BRT specific port
                         'BagFraction':('bf', None, False), #This is a BRT specific port
                         'NumberOfFolds':('nf', None, False), #This is a BRT specific port
                         'Alpha':('alp', None, False), #This is a BRT specific port
                         'PrevalenceStratify':('ps', None, False), #This is a BRT specific port
                         'ToleranceMethod':('tolm', None, False), #This is a BRT specific port
                         'Tolerance':('tol', None, False) #This is a BRT specific port
                         }
   
class MDSBuilder(Module):
    '''
    MDS Builder

    The Merged Data Set (MDS) Builder module is a utility that extracts the values of each predictor
    layer to the point locations included in the field data set. The module produces a .csv file that
    contains the x and y locations of the sample points and a column indicating whether each point
    represents a presence recording, an absence recording, a presence count, or a background point.
    Following these first three columns, each environmental predictor layer is appended as a column
    with row entries representing the value present in the raster layer at each field sample point.
    There are a total of three header rows in the output .csv of the MDSBuilder. The first row contains
    the columns "x," "y," "ResponseBinary" or "ResponseCount," and the names of each of the raster
    predictor files that were passed to the MDS Builder. The second row contains a binary value
    indicating whether the column should be included when the model is finally applied; these values
    are later modified during the Covariate Correlation and Selection process that takes place downstream
    in the workflow. The final header row contains the full path on the file system to each of the raster
    predictor files.

    The MDSBuilder accepts four inputs from the user:

    1. Rasters with PARC Info .csv File: The raster layers listed in this file will have their values
    extracted to the points in the field data .csv file. This parameter should be supplied by connecting
    the output of a PARC module within the workflow to the MDSBuilder module. (In order to properly
    extract the values of each predictor layer to the field data points, all the layers must have matching
    coordinate systems and cell sizes; outputs from the PARC module will have had the prerequisite processing).
    
    2. Background Point Count: This is an optional value that applies only to workflows that employ the
    Maxent modeling package. The dialogue box provides the option of specifying a number of background points
    to be randomly scattered throughout the study area (the extent of the template layer) to capture a more
    complete sample of the range of values present for each predictor layer. These points will be added to
    the field data .csv file with a value of "-999" denoting them as background points.
    
    3. Background Probability Surface: This is an optional parameter that applies only to workflows that
    employ the Maxent modeling package. In some analyses, it may be appropriate to spatially limit background
    points to a particular subset of the study area (e.g., islands within a study area polygon, particular
    regions within a study area polygon, or a region determined by the known bias present in the field data).
    Specifying a background probability surface raster allows a user to control where random points will be
    scattered within the extent of the study area. The raster layer specified by a user should have the same
    projection and extent as the template layer and contain values ranging from 0 to 100. These values represent
    the probability that a randomly generated point will be retained should it fall within a particular cell.
    That is, randomly generated points will not be generated in any part of the probability grid with a value
    of "0" while all points falling in an area with a value of "100" will be retained. A point falling in an
    area with a value of "50" will be kept as a background point 50% of the time.
    
    4. Field Data: The field data input corresponds to a .csv file containing presence/absence points or count
    data recorded across a landscape for the phenomenon being modeled (e.g., plant sightings, evidence of
    animal presence, etc.). This input file must be in a particular format, and in most cases, a user should
    populate this field by connecting a FieldData element to the MDSBuilder in the visual display within VisTrails.
    Please see the documention for the FieldData module for more details.

    '''

#    _input_ports = expand_ports([('RastersWithPARCInfoCSV', '(gov.usgs.sahm:RastersWithPARCInfoCSV:Other)'),
#                                 ('fieldData', '(gov.usgs.sahm:FieldData:DataInput)'),
#                                 ('backgroundPointCount', '(edu.utah.sci.vistrails.basic:Integer)'),
#                                 ('backgroundProbSurf', '(edu.utah.sci.vistrails.basic:File)')]
#                                 )
#    _input_ports = expand_ports([('RastersWithPARCInfoCSV', '(edu.utah.sci.vistrails.persistence:PersistentFile)'),
#                                 ('fieldData', '(gov.usgs.sahm:FieldData:DataInput)'),
#                                 ('backgroundPointCount', '(edu.utah.sci.vistrails.basic:Integer)'),
#                                 ('backgroundProbSurf', '(edu.utah.sci.vistrails.basic:File)')]
#                                 )
    _input_ports = expand_ports([('RastersWithPARCInfoCSV', '(edu.utah.sci.vistrails.basic:File)'),
                                 ('fieldData', '(gov.usgs.sahm:FieldData:DataInput)'),
                                 ('backgroundPointCount', '(edu.utah.sci.vistrails.basic:Integer)'),
                                 ('backgroundProbSurf', '(edu.utah.sci.vistrails.basic:File)')]
                                 )
    
    _output_ports = expand_ports([('mdsFile', '(gov.usgs.sahm:MergedDataSet:Other)')])

    def compute(self):
        port_map = {'fieldData': ('fieldData', None, True),
                    'backgroundPointCount': ('pointcount', None, False),
                    'backgroundProbSurf': ('probsurf', None, False),}
        
        MDSParams = utils.map_ports(self, port_map)            
        MDSParams['outputMDS'] = utils.mknextfile(prefix='MergedDataset_', suffix='.csv')
        
        #allow multiple CSV of inputs to be provided.  
        #if more than one then combine into a single CSV before sending to MDSBuilder
        inputs_csvs = self.forceGetInputListFromPort('RastersWithPARCInfoCSV')
        if len(inputs_csvs) == 0:
            raise ModuleError(self, "Must supply at least one 'RastersWithPARCInfoCSV'/nThis is the output from the PARC module")
        if len(inputs_csvs) > 1:
            inputs_csv = utils.mknextfile(prefix='CombinedPARCFiles_', suffix='.csv')
            inputs_names = [f.name for f in inputs_csvs]
            utils.merge_inputs_csvs(inputs_names, inputs_csv)
        else:
            inputs_csv = inputs_csvs[0].name
        MDSParams['inputsCSV'] = inputs_csv
        
        #inputsCSV = utils.path_port(self, 'RastersWithPARCInfoCSV')
        
        ourMDSBuilder = MDSB.MDSBuilder()
        utils.PySAHM_instance_params(ourMDSBuilder, MDSParams)

        writetolog("    inputsCSV=" + ourMDSBuilder.inputsCSV, False, False)
        writetolog("    fieldData=" + ourMDSBuilder.fieldData, False, False)
        writetolog("    outputMDS=" + ourMDSBuilder.outputMDS, False, False)
        
        try:
            ourMDSBuilder.run()
        except TrappedError as e:
            raise ModuleError(self, e.message)
        except:
            utils.informative_untrapped_error(self, "MDSBuilder")

        output_file = utils.create_file_module(ourMDSBuilder.outputMDS)
        
        self.setResult('mdsFile', output_file)

class FieldDataAggregateAndWeight(Module):
    '''
    Documentation to be updated when module finalized.
    '''
    _input_ports = expand_ports([('templateLayer', '(gov.usgs.sahm:TemplateLayer:DataInput)'),
                                 ('fieldData', '(gov.usgs.sahm:FieldData:DataInput)'),
                                 ('aggregateRows', 'basic:Boolean'),
                                 ('aggregateRowsByYear', 'basic:Boolean')])
    _output_ports = expand_ports([('fieldData', '(gov.usgs.sahm:FieldData:DataInput)')])
    
    def compute(self):
        writetolog("\nRunning FieldDataQuery", True)
        port_map = {'templateLayer': ('template', None, True),
            'fieldData': ('csv', None, True),
            'aggregateRowsByYear': ('aggRows', None, False),
            'addKDE': ('addKDE', None, False),}
        
        KDEParams = utils.map_ports(self, port_map)
        output_fname = utils.mknextfile(prefix='FDQ_', suffix='.csv')
        writetolog("    output_fname=" + output_fname, True, False)
        KDEParams['output'] = output_fname
        
        output_fname = utils.mknextfile(prefix='FDQ_', suffix='.csv')
        writetolog("    output_fname=" + output_fname, True, False)
        
        ourFDQ = FDQ.FieldDataQuery()
        utils.PySAHM_instance_params(ourFDQ, KDEParams)
            
        ourFDQ.processCSV()
        
        output_file = utils.create_file_module(output_fname)
        writetolog("Finished running FieldDataQuery", True)
        self.setResult('fieldData', output_file)

class PARC(Module):
    '''
    PARC

    The Projection, Aggregation, Resampling, and Clipping (PARC) module is a powerful
    utility that automates the preparation steps required for using raster layers in
    most geospatial modeling packages. In order to successfully consider multiple
    environmental predictors in raster format, each layer must have coincident cells
    (pixels) of the same size, have the same coordinate system (and projection, if
    applicable), and the same geographic extent. The PARC module ensures that all of
    these conditions are met for the input layers by transforming and or reprojecting
    each raster to match the coordinate system of the template layer. This process
    usually involves aggregation (necessary when an input raster layer must be up-scaled
    to match the template layer-- e.g., generalizing a 10 m input layer to a 100 m output
    layer), and or resampling (necessary for interpolating new cell values when transforming
    the raster layer to the coordinate space or cell size of the template layer). Lastly,
    each raster predictor layer is clipped to match the extent of the template layer.

    The settings used during these processing steps follow a particular set of decision rules
    designed to preserve the integrity of data as much as possible. However, it is important
    for a user to understand how these processing steps may modify the data inputs. For
    additional information about the PARC module, please see the extended help and
    documentation for the SAHM package. 

    The PARC module accepts four kinds of inputs: 

    1. Predictor List: A user should not have to populate this field. This field is populated
    when a selection is made from the pre-loaded .csv file of raster predictor layer inputs
    (specified during the SAHM install) and connected to the PARC module in the visual display. 
    
    2. .csv File List: The .csv file list corresponds to the Predictor List File element and
    allows a user to load a .csv file containing a list of rasters for consideration in the
    modeled analysis. For additional information, please see the documentation for the Predictor
    List File element.
    
    3. Predictor:  The predictor input allows a user to select a single raster predictor layer
    to be considered in the analysis. It is recommended that a user add this input as a separate
    element in the visual display (and then link it to the PARC module) so that the aggregation
    and resampling settings can be established. The PARC module can accept multiple predictor
    elements. For additional information, please see the documentation for the Predictor element.
    
    4. Template Layer: The template layer is a raster data layer with a defined coordinate system,
    a known cell size, and an extent that defines the study area. This raster layer serves as the
    template for all the other inputs in the analysis. All additional raster layers used in the
    analysis will be resampled and reprojected as needed to match the template, snapped to the
    template, and clipped to have an extent that matches the template. Users should ensure that
    any additional layers considered in the analysis have coverage within the extent of the
    template layer. The template layer is a required input for the PARC module.

    '''

    #configuration = []
    _input_ports = [('predictor', "(gov.usgs.sahm:Predictor:DataInput)"),
                                ('PredictorList', '(gov.usgs.sahm:PredictorList:Other)'),
                                ('RastersWithPARCInfoCSV', '(gov.usgs.sahm:RastersWithPARCInfoCSV:Other)'),
                                ('templateLayer', '(gov.usgs.sahm:TemplateLayer:DataInput)'),
                                ('multipleCores', '(edu.utah.sci.vistrails.basic:Boolean)', {'defaults':str(['True']), 'optional':True})]

#    _output_ports = [('RastersWithPARCInfoCSV', '(gov.usgs.sahm:RastersWithPARCInfoCSV:Other)')]
#    _output_ports = [('RastersWithPARCInfoCSV', '(edu.utah.sci.vistrails.persistence:PersistentFile)')]
    _output_ports = [('RastersWithPARCInfoCSV', '(edu.utah.sci.vistrails.basic:File)')]
    
    def compute(self):
        #writetolog("\nRunning PARC", True)
        
        ourPARC = parc.PARC()
        output_dname = utils.mknextdir(prefix='PARC_')
        
        if configuration.verbose:
            ourPARC.verbose = True
        ourPARC.logger = utils.getLogger()
        
        ourPARC.out_dir = output_dname

        if self.hasInputFromPort("multipleCores"):
             if self.getInputFromPort("multipleCores"):
                ourPARC.multicores = "True"

        workingCSV = utils.mknextfile(prefix='tmpFilesToPARC_', suffix='.csv')
        outputCSV = utils.mknextfile(prefix='PARCOutput_', suffix='.csv')

        #append additional inputs to the existing CSV if one was supplied
        #otherwise start a new CSV
        if self.hasInputFromPort("RastersWithPARCInfoCSV"):
            inputCSV = self.forceGetInputFromPort("RastersWithPARCInfoCSV").name
            shutil.copy(inputCSV, workingCSV)
            f = open(workingCSV, "ab")
            csvWriter = csv.writer(f)
        else:
            f = open(workingCSV, "wb")
            csvWriter = csv.writer(f)
            csvWriter.writerow(["FilePath", "Categorical", "Resampling", "Aggregation"])
        
        if self.hasInputFromPort("PredictorList"):
            predictor_lists = self.forceGetInputListFromPort('PredictorList')
            for predictor_list in predictor_lists:
                for predictor in predictor_list:
                    csvWriter.writerow(list(predictor))
        
        if self.hasInputFromPort("predictor"):
            predictor_list = self.forceGetInputListFromPort('predictor')
            for predictor in predictor_list:
                csvWriter.writerow(list(predictor))
        f.close()
        del csvWriter
        ourPARC.inputs_CSV = workingCSV
        ourPARC.template = self.forceGetInputFromPort('templateLayer').name
        writetolog('    template layer = ' + self.forceGetInputFromPort('templateLayer').name)
        writetolog("    output_dname=" + output_dname, False, False)
        writetolog("    workingCSV=" + workingCSV, False, False)
        try:
            ourPARC.parcFiles()
        except TrappedError as e:
            writetolog(e.message)
            raise ModuleError(self, e.message)
        except:
            utils.informative_untrapped_error(self, "PARC")        
        
        #delete our temp working file
        os.remove(workingCSV)
        
        predictorsDir = utils.create_dir_module(output_dname)
        outputCSV = os.path.join(output_dname, "PARC_Files.csv")
        output_file = utils.create_file_module(outputCSV)
        
        
        writetolog("Finished running PARC", True)
        self.setResult('RastersWithPARCInfoCSV', output_file)
        

class RasterFormatConverter(Module):
    '''
    Raster Format Converter

    The RasterFormatConverter module allows a user to easily convert .tif raster layers
    into a different raster format for use and display in other software packages. The
    module accepts as an input either a list of rasters in a Merged Dataset File (MDS)
    or the location of a directory containing multiple raster files. All outputs will be
    sent to a folder named "ConvertedRasters" (followed by an underscore and a number
    corresponding to the run sequence of the module) within the user's current VisTrail
    session folder.

    Three parameters can be specified by the user:

    1. Format: The format corresponds to the desired raster output format. The following
    output file formats are supported: Arc/Info ASCII Grid, ESRI BIL, ERDAS Imagine, and JPEG.
    
    To specify the desired output, users should enter the values shown below.
    For an ASCII (.asc) output, enter: "asc"
    For an ESRI BIL output, enter: "bil"
    For an Erdas Imagine (.img) output, enter: "img"
    For a JPEG (.jpg) output, enter: "jpg"
    
    If no value is entered by the user, the module will default to an ASCII (.asc) output
    format.

    2. Input Directory: The input directory allows a user to point to an entire folder as
    an input to the RasterFormatConverter. The contents of the specified folder will be
    checked for raster files and all the raster files contained within the directory will
    be converted to the format specified in the "Format" dialogue box. The module will
    identify and convert files of the following raster types: .bil, .img, .tif, .jpg, and .asc. 

    3. Input Merged Dataset (MDS): The input merged dataset allows a user to specify a .csv
    file created in the VisTrails workflow (containing a list of .tif raster files) as an
    input to the raster converter. All of the files listed in the MDS will be converted to
    the raster format specified in the "Format" dialogue box.

    '''

    #configuration = []
    _input_ports = [("inputMDS", "(gov.usgs.sahm:MergedDataSet:Other)"),
                    ('inputDir', '(edu.utah.sci.vistrails.basic:Directory)'),
                    ('format', '(edu.utah.sci.vistrails.basic:String)'),
                    ('multipleCores', '(edu.utah.sci.vistrails.basic:Boolean)', {'defaults':str(['True']), 'optional':True})]

    _output_ports = [('outputDir', '(edu.utah.sci.vistrails.basic:Directory)')]

    def compute(self):
        writetolog("\nRunning TiffConverter", True)
        ourRFC = RFC.FormatConverter()
        if self.hasInputFromPort('inputMDS'):
            ourRFC.MDSFile = self.forceGetInputFromPort('inputMDS').name
        elif self.hasInputFromPort('inputDir'):
            ourRFC.inputDir = self.forceGetInputFromPort('inputDir').name
            
        if self.hasInputFromPort('format'):
            format = self.forceGetInputFromPort('format')
            if format == '':
                format = 'asc'
            ourRFC.format = format
             
        if self.hasInputFromPort("multipleCores"):
             if self.getInputFromPort("multipleCores"):
                ourRFC.multicores = "True"
        
        ourRFC.outputDir = utils.mknextdir(prefix='ConvertedRasters_')
        if configuration.verbose:
            ourRFC.verbose = True
        ourRFC.logger = utils.getLogger()
        writetolog("    output directory = " + ourRFC.outputDir, False, False)
        
        try:
            ourRFC.run()
        except TrappedError as e:
            raise ModuleError(self, e.message)
        except:
            utils.informative_untrapped_error(self, "RasterFormatConverter") 
        
        
        outputDir = utils.create_dir_module(ourRFC.outputDir)
        self.setResult('outputDir', outputDir)
        writetolog("\nFinished running TiffConverter", True)
        
class TestTrainingSplit(Module):
    '''
    Test Training Split

    The TestTrainingSplit module provides the opportunity to establish specific settings
    for how field data will be used in the modeling process. Three parameters can be set
    by the user:

    1. Ratio of Presence/Absence Points:
    This field is populated with a number corresponding to the desired proportion of
    presence and absence points to be used in the analysis. If populated, this entry should
    be a number greater than zero. (A value of '1' will result in an equal number of both
    presence and absence points being used, a value of '2' indicates that twice as many
    presence points will be used, a value of 0.5 indicates that twice as many absence points
    will be used, etc.). All field data points with a value equal to or greater than 1 are
    interpreted as presence points. Although the original field data is unmodified, this
    option will reduce the sample size as the merged dataset containing sample points will
    have points deleted from it to achieve the specified ratio. A warning will be generated
    if more than 50% of either the presence or absence points will be deleted based on the
    ratio specified by the user. Background points are ignored by this module (they are read
    in and written out, but not assigned to either the test or training split).

    When left empty, this field will default to 'null' and the model will use the existing
    presence/absence ratio present in the field data.

    2. Input Merged Data Set (MDS): 
    This is the input data set consisting of locational data for each sample point, the
    values of each predictor variable at those points, and if established, a field denoting
    the weight that will be assigned to each point in modeling. This input is usually provided
    by the upstream steps that precede the Test Training Split module. Any value entered here
    (e.g., specifying another existing MDS on the file system) will override the input
    specified by a model connection in the visual display.

    3. Training Proportion:
    This is the proportion of the sample points that will be used to train the model, relative
    to the total number of points. Entered values should be greater than 0 but less than 1.
    For example, a value of '0.9' will result in 90% of the sample points being used to train
    the model, with 10% of the sample being held out to test the model's performance. Choosing
    an appropriate training proportion can depend on various factors, such as the total number
    of sample points available.

    '''

    _input_ports = [("inputMDS", "(gov.usgs.sahm:MergedDataSet:Other)"),
                    ('trainingProportion', '(edu.utah.sci.vistrails.basic:Float)', 
                        {'defaults':str(['0.7'])}),
                    ('RatioPresAbs', '(edu.utah.sci.vistrails.basic:Float)')]
    _output_ports = [("outputMDS", "(gov.usgs.sahm:MergedDataSet:Other)")]
    
    def compute(self):
        if self.hasInputFromPort('trainingProportion'):
            print 'real input'
        writetolog("\nGenerating Test Training split ", True)
        inputMDS = utils.dir_path_value(self.forceGetInputFromPort('inputMDS', []))
        outputMDS = utils.mknextfile(prefix='TestTrainingSplit_', suffix='.csv')

        global models_path
        
        args = "i=" + '"' + inputMDS + '"' + " o=" + '"' + outputMDS + '"'
        args += " rc=" + utils.MDSresponseCol(inputMDS) 
        if (self.hasInputFromPort("trainingProportion")):
            try:
                trainingProportion = float(self.getInputFromPort("trainingProportion"))
                if trainingProportion <= 0 or trainingProportion > 1:
                    raise ModuleError(self, "Train Proportion (trainProp) must be a number between 0 and 1 excluding 0")
                args += " p=" + str(trainingProportion)
            except:
                raise ModuleError(self, "Train Proportion (trainProp) must be a number between 0 and 1 excluding 0")
        if (self.hasInputFromPort("RatioPresAbs")):
            try:
                RatioPresAbs = float(self.getInputFromPort("RatioPresAbs"))
                if RatioPresAbs <= 0:
                    raise ModuleError(self, "The ratio of presence to absence (RatioPresAbs) must be a number greater than 0") 
                args += " m=" + str(trainingProportion) 
            except:
                raise ModuleError(self, "The ratio of presence to absence (RatioPresAbs) must be a number greater than 0") 
        
        utils.runRScript("TestTrainSplit.r", args, self)

        output = os.path.join(outputMDS)
        if os.path.exists(output):
            output_file = utils.create_file_module(output)
            writetolog("Finished Test Training split ", True)
        else:
            msg = "Problem encountered generating Test Training split.  Expected output file not found."
            writetolog(msg, False)
            raise ModuleError(self, msg)
        self.setResult("outputMDS", output_file)
        
class CovariateCorrelationAndSelection(Module):
    '''
    Covariate Correlation And Selection

    The CovariateCorrelationAndSelection view provides a breakpoint in the modeling workflow
    for the user to assess how well each variable explains the distribution of the sampled
    data points and to remove any variables that may exhibit high correlation with others. 

    The display shows the 10 most correlated variables of those selected. These variables
    are displayed on the diagonal and their respective graphical display and correlation with
    other variables can be found by locating the row/column intersection between each (above
    and below the diagonal). The column heading over each variable displays the number of
    other variables with which the environmental predictor is correlated. The user defined
    "Threshold" option allows a user to specify the degree of correlation required between
    two variables for them to be counted in this tally.

    A user is provided with the opportunity to select a new set of the environmental predictor
    variables and "Update" the Covariate Correlation screen to investigate the relationships
    among the new variables selected. The options are provided to include or exclude the
    presence/count points, the absence points (when applicable), and the background points in
    this correlation test. Variables with a high degree of correlation with other variables
    should generally be unchecked in their respective radio buttons, and will be excluded from
    subsequent analysis steps in the model workflow.

    Multiple iterations can be run at this screen, allowing the user to investigate the
    relationships among the environmental predictor variables and choose the most appropriate
    set to be used in the subsequent modeling. When the desired set of variables has been chosen,
    the "OK" button is selected and processing will resume in the VisTrails workflow.

    '''
    kwargs = {}
    kwargs['defaults'] = str(['initial'])
    _input_ports = [("inputMDS", "(gov.usgs.sahm:MergedDataSet:Other)"),
                    ('selectionName', '(edu.utah.sci.vistrails.basic:String)', kwargs),
                    ('ShowGUI', '(edu.utah.sci.vistrails.basic:Boolean)')]
    _output_ports = [("outputMDS", "(gov.usgs.sahm:MergedDataSet:Other)")]

    def compute(self):
        writetolog("\nOpening Select Predictors Layers widget", True)
        inputMDS = utils.dir_path_value(self.forceGetInputFromPort('inputMDS'))
        selectionName = self.forceGetInputFromPort('selectionName', 'initial')
#        outputMDS = utils.mknextfile(prefix='SelectPredictorsLayers_' + selectionName + "_", suffix='.csv')
#        displayJPEG = utils.mknextfile(prefix='PredictorCorrelation_' + selectionName + "_", suffix='.jpg')
        global session_dir
        outputMDS = os.path.join(session_dir, "CovariateCorrelationOutputMDS_" + selectionName + ".csv")
        displayJPEG = os.path.join(session_dir, "CovariateCorrelationDisplay.jpg")
        writetolog("    inputMDS = " + inputMDS, False, False)
        writetolog("    displayJPEG = " + displayJPEG, False, False)
        writetolog("    outputMDS = " + outputMDS, False, False)
        
        if os.path.exists(outputMDS):
            utils.applyMDS_selection(outputMDS, inputMDS)
            os.remove(outputMDS)
        
        self.callDisplayMDS(inputMDS, outputMDS, displayJPEG)

        output_file = utils.create_file_module(outputMDS)
        writetolog("Finished Select Predictors Layers widget", True)
        self.setResult("outputMDS", output_file)

    def callDisplayMDS(self, inputMDS, outputMDS, displayJPEG):
        dialog = SelectListDialog(inputMDS, outputMDS, displayJPEG, configuration.r_path)
        #dialog.setWindowFlags(QtCore.Qt.WindowMaximizeButtonHint)
#        print " ... finished with dialog "  
        retVal = dialog.exec_()
        #outputPredictorList = dialog.outputList
        if retVal == 1:
            raise ModuleError(self, "Cancel or Close selected (not OK) workflow halted.")


class ProjectionLayers(Module):
    '''
    Projection Layers

    Note: as of June 2011, this module offers some functionality that is only available
    to users running the SAHM package within the USGS Fort Collins Science Center (FORT).

    The ProjectionLayers module provides the option to prepare a separate set of predictor
    layers so that the results of a model developed from one set of environmental predictors
    can be projected onto a new modeled space. This second set of environmental predictors
    (corresponding to the "projection target") most often contains the same environmental
    predictors but represents data captured at a different temporal or spatial location. For
    example, a user could generate a model predicting habitat suitability using recorded
    presence points and certain environmental predictors such as elevation, landcover, and
    proximity to water in one geographic location. Based on the training from this information,
    the modeled results could be generated for (or "projected to") a new location based on the
    range of values seen in elevation, landcover, and proximity to water in the second geographic
    area. Similarly, modeling predicted results through time is also possible. A model trained
    using field data and a set of predictor layers representative of one time period could be
    projected onto the same geographical area using a new set of predictor layers corresponding
    to the same predictors but representing data from a different time period (e.g., different
    climate data). 

    The output of this module is subsequently used as the projection target in the ApplyModel module.

    (As part of the process of preparing the layers for modeling, the ProjectionLayers module runs
    the PARC module internally on the inputs. Outputs from the ProjectionLayers module will possess
    matching coordinate systems, cell sizes, and extents and do not need to be run through PARC
    before being used downstream in the workflow.)

    Six parameters can be set by the user:

    1. Directory Crosswalk CSV: This is a .csv file containing two columns designating
    the layers that should be swapped out in the projected model. The first column
    contains a list of the full paths to the predictor layers used to develop the original
    model that will be replaced in the projection process. The second column contains the
    full paths to the new predictor layers that will substitute the respective layers used
    in the original model. Each original layer in the first column should be paired with
    its replacement in the second column (e.g., Column 1 = C:\ModelLayers\Precipitation1980.tif,
    Column 2 = C:\ModelLayers\Precipitation2000.tif). In the case of any file used to develop
    the first model that is not expressly listed in the Directory Crosswalk CSV with a
    replacement, the original file will be used in the new model projection. The module
    anticipates a header row in this .csv file (thus, the first row of data will be ignored).
    
    2. File List CSV: This is a .csv file containing the list of predictor files used to
    develop the first model. Effectively, this file will be updated based on the information
    provided in the directory crosswalk .csv and used as the input to the training process
    for the projected model. The output of the PARC module from the first model iteration
    should be used as the input to this parameter.
    
    3. Model (available only to users at the FORT): This parameter allows VisTrail users
    running the SAHM package on site at the USGS Science Center in Fort Collins (FORT) to
    specify one of three models to use for the projected model run ("CCCMA," "CSIRO,"
    or "hadcm3").
    
    4. Scenario (available only to users at the FORT): This parameter allows VisTrail
    users running the SAHM package on site at the USGS Science Center in Fort Collins 
    FORT) to specify one of two scenarios for the projected model run ("A2a" or "B2b"). 
    
    5. Template: This parameter allows a user to specify the new template layer to be used
    in the projected model run. The template layer is a raster data layer with a defined
    coordinate system, a known cell size, and an extent that defines the (new) study area.
    This raster layer serves as the template for all the other inputs in the analysis. All
    additional raster layers used in the analysis will be resampled and reprojected as
    needed to match the template, snapped to the template, and clipped to have an extent
    that matches the template. Users should ensure that all the layers used for the projected
    analysis have coverage within the extent of the template layer.
    
    6. Year (available only to users at the FORT): This parameter allows VisTrail users
    running the SAHM package on site at the USGS Science Center in Fort Collins (FORT)
    to specify one of three years to use for the projected model run ("2020," "2050," or "2080").

    '''
    _input_ports = [('RastersWithPARCInfoCSV', '(gov.usgs.sahm:RastersWithPARCInfoCSV:Other)'),
                    ('templateLayer', '(gov.usgs.sahm:TemplateLayer:DataInput)'),
                    ('model', '(edu.utah.sci.vistrails.basic:String)'),
                    ('scenario', '(edu.utah.sci.vistrails.basic:String)'),
                    ('year', '(edu.utah.sci.vistrails.basic:String)'),
                    ('directoryCrosswalkCSV', '(edu.utah.sci.vistrails.basic:File)')
                    ]
    _output_ports = [("MDS", "(gov.usgs.sahm:MergedDataSet:Other)")]

    def compute(self):
        models = ['CCCMA', 'CSIRO', 'hadcm3']
        scenarioss = ['A2a', 'B2b']
        years = ['2020', '2050', '2080']
        
        writetolog("\nRunning make Projection Layers", True)
        
        inputCSV = self.forceGetInputFromPort('RastersWithPARCInfoCSV').name
    
        if self.hasInputFromPort('templateLayer'):
            template = self.forceGetInputFromPort('templateLayer').name
        else:
            template = '' #we'll get a template below
            
        fromto = []
        climargs = {}
        
        for input in ['model', 'scenario', 'year']:
            if self.hasInputFromPort(input):
                climargs[input] = self.forceGetInputFromPort(input)
        if climargs <> {} and climargs.keys() <> ['model', 'scenario', 'year']:
            #they did not add in one of each, Not going to fly
            raise ModuleError(self, "All of model, scenario, and year must be supplied if any are used.")
        elif climargs <> {} and climargs.keys <> ['model', 'scenario', 'year']:
            #they specified a alt climate scenario add this to our list to search for
            fromto.append([r'K:\GIS_LIBRARY\Climate\WorldClim\BioclimaticVariables\bio_30s_esri\bio',
                           os.path.join('I:\WorldClim_Future_Climate\RenamedBILs', 
                                        climargs['model'], climargs['scenario'], climargs['year'])])
        
        if self.hasInputFromPort('directoryCrosswalkCSV'):
            crosswalkCSV = csv.reader(open(self.forceGetInputFromPort('directoryCrosswalkCSV'), 'r'))
            header = crosswalkCSV
            for row in crosswalkCSV:
                fromto.append(row[0], row[1])
            del crosswalkCSV    
            
        #write out the outputs to an empty MDS file (just the header is needed to PARC the outputs)
            
        
        inCSV = csv.reader(open(inputCSV, 'r'))
        inCSV.next() #skip header
        workingCSV = utils.mknextfile(prefix='tmpFilesToPARC_', suffix='.csv')
        tmpCSV = csv.writer(open(workingCSV, 'wb'))
        tmpCSV.writerow(["FilePath", "Categorical", "Resampling", "Aggregation"])
        outHeader1 = ['x', 'y', 'response']
        outHeader2 = ['', '', '']
        outHeader3 = ['', '', '']
        
        output_dname = utils.mknextdir(prefix='ProjectionLayers_')
        
        for row in inCSV:
            if template == '':
                template = row[0]
            fileShortName = utils.getShortName(row[0])
            if row[1] == 1:
                outHeader1.append(fileShortName + '_categorical')
            else:
                outHeader1.append(fileShortName)
            outHeader2.append('1')
            outHeader3.append(os.path.join(output_dname, fileShortName + '.tif'))

            origFile = row[4]
            newOrigFile = origFile
            for lookup in fromto:
               if lookup[0] in origFile:
                   newOrigFile = origFile.replace(lookup[0], lookup[1])
            tmpCSV.writerow([newOrigFile,] + row[1:4])
        del tmpCSV
        
        #PARC the files here
        ourPARC = parc.PARC()
        
        
        if configuration.verbose:
            ourPARC.verbose = True
        writetolog("    output_dname=" + output_dname, False, False)
        ourPARC.outDir = output_dname
        ourPARC.inputsCSV = workingCSV
        ourPARC.template = template

        try:
            ourPARC.parcFiles()
        except TrappedError as e:
            raise ModuleError(self, e.message)
        except :
            utils.informative_untrapped_error(self, "PARC")
        
        #loop through our workingCSV and format it into an MDS header
        
        #outputMDS = utils.mknextfile(prefix='ProjectionLayersMDS_', suffix = '.csv')
        outputMDS = os.path.join(output_dname, 'ProjectionLayersMDS.csv')
        outCSV = csv.writer(open(outputMDS, 'wb'))
        outCSV.writerow(outHeader1)
        outCSV.writerow(outHeader2)
        outCSV.writerow(outHeader3)
        
        output_file = utils.create_file_module(outputMDS)
        self.setResult("MDS", output_file)
        writetolog("Finished Select Projection Layers widget", True)

#class ClimateModel(String):
#    _input_ports = [('value', '(gov.usgs.sahm:ClimateModel:Other)')]
#    _output_ports = [('value_as_string', '(edu.utah.sci.vistrails.basic:String)', True)]
#    _widget_class = build_enum_widget('ClimateModel', 
#                                      ['CCCMA', 'CSIRO', 'hadcm3'])
#
#    @staticmethod
#    def get_widget_class():
#        return ClimateModel._widget_class
#
#class ClimateScenario(String):
#    _input_ports = [('value', '(gov.usgs.sahm:ClimateScenario:Other)')]
#    _output_ports = [('value_as_string', '(edu.utah.sci.vistrails.basic:String)', True)]
#    _widget_class = build_enum_widget('ClimateScenario', 
#                                      ['A2a', 'B2b'])
#
#    @staticmethod
#    def get_widget_class():
#        return ClimateScenario._widget_class
#
#class ClimateYear(String):
#    _input_ports = [('value', '(gov.usgs.sahm:ClimateYear:Other)')]
#    _output_ports = [('value_as_string', '(edu.utah.sci.vistrails.basic:String)', True)]
#    _widget_class = build_enum_widget('ClimateYear', 
#                                      ['2020', '2050', '2080'])
#
#    @staticmethod
#    def get_widget_class():
#        return ClimateYear._widget_class

class MAXENT(Module):

    _output_ports = [("lambdas", "(edu.utah.sci.vistrails.basic:File)"),
                     ("report", "(edu.utah.sci.vistrails.basic:File)"),
                     ("roc", "(edu.utah.sci.vistrails.basic:File)")]

    def compute(self):
        global maxent_path

        ourMaxent = MaxentRunner.MAXENTRunner()
        ourMaxent.outputDir = utils.mknextdir(prefix='maxentFiles_')
        
        ourMaxent.inputMDS = self.forceGetInputFromPort('inputMDS').name
        
        ourMaxent.maxentpath = maxent_path
        
        MaxentArgsCSV = utils.mknextfile(prefix='MaxentArgs', suffix='.csv')
        argWriter = csv.writer(open(MaxentArgsCSV, 'wb'))
        argWriter.writerow(['parameter','value'])
        for port in self._input_ports:
            #print port
            if port[0] <> 'inputMDS' and port[0] <> 'projectionlayers':
                if self.hasInputFromPort(port[0]):
                    port_val = self.getInputFromPort(port[0])
                    if port[1] == "(edu.utah.sci.vistrails.basic:Boolean)":
                        port_val = str(port_val).lower()
                    elif (port[1] == "(edu.utah.sci.vistrails.basic:Path)" or \
                        port[1] == "(edu.utah.sci.vistrails.basic:File)"):
                        port_val = port_val.name
                    argWriter.writerow([port[0], port_val])
                else:
                    #print "   has no input "
                    kwargs = port[2]
                    #print kwargs
                    try:
                        if port[1] == "(edu.utah.sci.vistrails.basic:Boolean)":
                            default = kwargs['defaults'][2:-2].lower()
                        else:
                            default = kwargs['defaults'][2:-2]
                        #args[port[0]] = default
                        argWriter.writerow([port[0], default])
                    except KeyError:
                        pass
        if self.hasInputFromPort('projectionlayers'):
            value = self.forceGetInputListFromPort('projectionlayers')
            projlayers = ','.join([path.name for path in value])
            argWriter.writerow(['projectionlayers', projlayers])
            
        del argWriter
        ourMaxent.argsCSV = MaxentArgsCSV
        ourMaxent.logger = utils.getLogger()
        try:
            ourMaxent.run()
        except TrappedError as e:
            raise ModuleError(self, e.message)  
        except:
            utils.informative_untrapped_error(self, "Maxent")
        
         #set outputs
        lambdasfile = os.path.join(ourMaxent.outputDir, ourMaxent.args["species_name"] + ".lambdas")
        output_file = utils.create_file_module(lambdasfile)
        self.setResult("lambdas", output_file)
        
        
        rocfile = os.path.join(ourMaxent.outputDir, 'plots', ourMaxent.args["species_name"] + "_roc.png")
        output_file = utils.create_file_module(rocfile)
        self.setResult("roc", output_file)

        htmlfile = os.path.join(ourMaxent.outputDir, ourMaxent.args["species_name"] + ".html")
        print htmlfile
        output_file = utils.create_file_module(htmlfile)
        self.setResult("report", output_file)

        writetolog("Finished Maxent widget", True)
        
def load_max_ent_params():    
    maxent_fname = os.path.join(os.path.dirname(__file__), 'maxent.csv')
    csv_reader = csv.reader(open(maxent_fname, 'rU'))
    # pass on header
    csv_reader.next()
    input_ports = []
    
    input_ports.append(('inputMDS', '(gov.usgs.sahm:MergedDataSet:Other)'))
    
    docs = {}
    basic_pkg = 'edu.utah.sci.vistrails.basic'
    p_type_map = {'file/directory': 'Path',
                  'double': 'Float'}
    for row in csv_reader:
        [name, flag, p_type, default, doc, notes] = row
        name = name.strip()
        p_type = p_type.strip()
        if p_type in p_type_map:
            p_type = p_type_map[str(p_type)]
        else:
            p_type = str(p_type).capitalize()
        kwargs = {}
        default = default.strip()
        if default:
            if p_type == 'Boolean':
                default = default.capitalize()
            kwargs['defaults'] = str([default])
        if p_type == 'Boolean':
            kwargs['optional'] = True
        input_ports.append((name, '(' + basic_pkg + ':' + p_type + ')', kwargs))
        # FIXME set documentation
        #print 'port:', (name, '(' + basic_pkg + ':' + p_type + ')', kwargs)
        docs[name] = doc


    #print 'MAXENT:', input_ports
    MAXENT._input_ports = input_ports
    MAXENT._port_docs = docs

    def provide_input_port_documentation(cls, port_name):
        return cls._port_docs[port_name]
    MAXENT.provide_input_port_documentation = \
        classmethod(provide_input_port_documentation)


#class ModelOutputCell(SpreadsheetCell):
#    _input_ports = [("row", "(edu.utah.sci.vistrails.basic:Integer)"),
#                    ("column", "(edu.utah.sci.vistrails.basic:Integer)"),
#                    ('ProbabilityMap', '(edu.utah.sci.vistrails.basic:File)')]
#    
#    def __init__(self):
#        SpreadsheetCell.__init__(self)
#        self.cellWidget = None
#
#    def compute(self):
#        renderView = self.forceGetInputFromPort('SetRenderView')
#        if renderView==None:
#            raise ModuleError(self, 'A vtkRenderView input is required.')
#        self.cellWidget = self.displayAndWait(QVTKViewWidget, (renderView,))

#class SAHMViewWidget(QCellWidget):
#    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
#        QCellWidget.__init__(self, parent, f | QtCore.Qt.MSWindowsOwnDC)
#        

#class RasterLayer(Module):
#    _input_ports = [('file', '(edu.utah.sci.vistrails.basic:File)'), 
#                    ('name', '(edu.utah.sci.vistrails.basic:String)')]
#    _output_ports = [('self', '(gov.usgs.sahm:RasterLayer:DataInput)')]
#
#    def __init__(self):
#        Module.__init__(self)
#        self.qgis_obj = None
#
#    def compute(self):
#        fname = self.getInputFromPort('file').name
#        if self.hasInputFromPort('name'):
#            name = self.getInputFromPort('name')
#        else:
#            name = os.path.splitext(os.path.basename(fname))[0]
#        self.qgis_obj = qgis.core.QgsRasterLayer(fname, name)
#        self.setResult('self', self)
#
#class VectorLayer(Module):
#    _input_ports = [('file', '(edu.utah.sci.vistrails.basic:File)'), 
#                    ('name', '(edu.utah.sci.vistrails.basic:String)')]
#    _output_ports = [('self', '(gov.usgs.sahm:VectorLayer:DataInput)')]
#
#    def __init__(self):
#        Module.__init__(self)
#        self.qgis_obj = None
#
#    def compute(self):
#        fname = self.getInputFromPort('file').name
#        if self.hasInputFromPort('name'):
#            name = self.getInputFromPort('name')
#        else:
#            name = os.path.splitext(os.path.basename(fname))[0]
#        self.qgis_obj = qgis.core.QgsVectorLayer(fname, name, "ogr")
#        self.setResult('self', self)



def initialize():    
    global maxent_path, color_breaks_csv
    global session_dir
    utils.config = configuration
       
    r_path = os.path.abspath(configuration.r_path)
    maxent_path = os.path.abspath(configuration.maxent_path)
    
    
    #I was previously setting the following environmental variables and path additions 
    #so that each user wouldn't have to do this on their individual machines.  
    #I was running into problems with imports occuring before this initialize routine so 
    #I moved the setting of these to an external .net application that sets these before 
    #starting up VisTrails.py.
    
    #This should also make this package easier to port to other systems as this stuff would
    #only work on a windows instance.
    #the current dependencies are:
    #an installation of GDAL and Proj.4
    # this includes the GDAL_DATA and PROJ_LIB directories as environmental variables
    #GDAL bindings for python in the python path.
    #QGIS built for the version of Python, QT, PyQt, and SIP used by VisTrails.
    #  This one was a painful bear on Windows.
    #All of the DLLs required by the above QGIS build must be on the path.
    #In my case these were in a folder in the OSGeoW installation that QGIS was built 
    #off of.
    #And finally QGIS bindings for python in the python path.
    
     
    import qgis.core
    import qgis.gui
    globals()["qgis"] = qgis
    setQGIS(qgis)
    
    qgis_prefix = os.path.join(configuration.qgis_path, "qgis1.7.0")
    qgis.core.QgsApplication.setPrefixPath(qgis_prefix, True)
    qgis.core.QgsApplication.initQgis() 
    
    
    session_dir = utils.createrootdir(configuration.output_dir)
    utils.createLogger(session_dir, configuration.output_dir)
    #log_file = Utilities.createsessionlog(session_dir, configuration.verbose)
    
    color_breaks_csv = os.path.abspath(os.path.join(os.path.dirname(__file__),  "ColorBreaks.csv"))
    
    load_max_ent_params()
    
    global layers_csv_fname
    
    writetolog("*" * 79)
    writetolog("Initializing:", True, True)
    writetolog("  Locations of dependencies")
#    writetolog("   Layers CSV = " + os.path.join(os.path.dirname(__file__), 'layers.csv'))
    writetolog("   Layers CSV = " + layers_csv_fname)
    writetolog("   R path = " + r_path)
    writetolog("   GDAL folder = " + os.path.abspath(configuration.gdal_path))
    writetolog("        Must contain subfolders proj, gdal-data, GDAL")
    writetolog("   Maxent folder = " + maxent_path)
    writetolog("   QGIS folder = " + os.path.abspath(configuration.qgis_path))
    writetolog("        Must contain subfolders qgis1.7.0, OSGeo4W")
    writetolog("    ")
    writetolog("*" * 79)
    
    writetolog("*" * 79)
    writetolog(" output directory:   " + session_dir)
    writetolog("*" * 79)
    writetolog("*" * 79)
    
def finalize():
    pass
    #utils.cleantemps()#No longer used  

def generate_namespaces(modules):
    module_list = []
    for namespace, m_list in modules.iteritems():
        for module in m_list:
            m_dict = {'namespace': namespace}
            if type(module) == tuple:
                m_dict.update(module[1])
                module_list.append((module[0], m_dict))
                #print 'm_dict:', m_dict
            else:
                module_list.append((module, m_dict))
    return module_list

def build_available_trees():
    trees = {}
    global layers_csv_fname
    layers_csv_fname = os.path.join(os.path.dirname(__file__), 'layers.csv')
    csv_reader = csv.reader(open(layers_csv_fname, 'rU'))
    csv_reader.next()
    first_file = csv_reader.next()[0]
    
    #if the first file in the layers file does not exist assume that none
    #of them do and use the exampledata version
    if not os.path.exists(first_file):
        print (("!" * 30) + " WARNING " + ("!" * 30) + "\n")*3
        print "The first grid in your layers CSV could not be found."
        print "Defaulting to the example data csv."
        print "fix/set paths in file " + layers_csv_fname + " to enable this functionality."
        print "See documentation for more information on setting up the layers.csv\n"
        print (("!" * 30) + " WARNING " + ("!" * 30) + "\n")*3
        layers_csv_fname = os.path.join(os.path.dirname(__file__), 'layers.exampledata.csv')
    
    csv_reader = csv.reader(open(layers_csv_fname, 'rU'))
    # pass on header
    csv_reader.next()
    for row in csv_reader:
        if row[2] not in trees:
            trees[row[2]] = {}
        available_dict = trees[row[2]]
#        if 'Daymet' not in available_dict:
#            available_dict['Daymet'] = []
#        available_dict['Daymet'].append((row[0], row[1], row[3]))            
        if row[3] not in available_dict:
            available_dict[row[3]] = []
        available_dict[row[3]].append((row[0], row[1], row[4]))
       
    return trees

def build_predictor_modules():
    available_trees = build_available_trees()
    modules = []
    for name, tree in available_trees.iteritems():
        name_arr = name.strip().split()
        class_base = ''.join(n.capitalize() for n in name_arr)
        widget_class = get_predictor_widget(class_base, tree)
        config_class = get_predictor_config(class_base, tree)
        class_name = class_base + "Predictors"
        def get_widget_method(w_class):
            @staticmethod
            def get_widget_class():
                return w_class
            return get_widget_class
        module = type(class_name, (PredictorList,),
                      {'get_widget_class': get_widget_method(widget_class),
                       '_input_ports': \
                           [('value',
                             '(gov.usgs.sahm:%s:DataInput)' % class_name, True)]})
        
        modules.append((module, {'configureWidgetType': config_class}))
        for module in modules:
            module[0]._output_ports.append(('value_as_string', '(edu.utah.sci.vistrails.basic:String)', True))
            
    return modules


 

_modules = generate_namespaces({'DataInput': [
                                              Predictor,
                                              PredictorListFile,
                                              FieldData,
                                              TemplateLayer] + \
                                              build_predictor_modules(),
                                'Tools': [FieldDataAggregateAndWeight,
                                          MDSBuilder,
                                          PARC,
                                          RasterFormatConverter,
                                          ProjectionLayers,
                                          TestTrainingSplit,
                                          CovariateCorrelationAndSelection,
                                          ApplyModel],                                          
                                'Models': [GLM,
                                           RandomForest,
                                           MARS,
                                           MAXENT,
                                           BoostedRegressionTree],
                                'Other':  [(Model, {'abstract': True}),
                                           (ResampleMethod, {'abstract': True}),
                                           (AggregationMethod, {'abstract': True}),
                                           (PredictorList, {'abstract': True}),
                                           (MergedDataSet, {'abstract': True}),
                                           (RastersWithPARCInfoCSV, {'abstract': True})],
                                'Output': [SAHMModelOutputViewerCell,
                                          SAHMSpatialOutputViewerCell,
                                          ]
#                                           ClimateModel,
#                                           ClimateScenario,
#                                           ClimateYear

                                })