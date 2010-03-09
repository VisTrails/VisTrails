from datetime import datetime
import glob
import itertools
import os
import shutil
import tempfile

from core.modules.vistrails_module import Module, ModuleError, ModuleConnector
from core.modules.basic_modules import File, Directory
from core.system import list2cmdline, execute_cmdline

def run_cmd_line_jar(jar_name, args):
    arg_items = list(itertools.chain(*args.items()))
    output = []
    jar_name = os.path.join(sahm_path, jar_name)
    cmdline = ['java', '-jar', jar_name] + arg_items
    print 'running', cmdline
    res = execute_cmdline(['java', '-jar', jar_name] + arg_items, output)
    return res, output
     
def create_file_module(fname, f=None):
    if f is None:
        f = File()
    f.name = fname
    f.upToDate = True
    return f
                
# class WorkingDir(Module):
#     def __init__(self):
#         self.field_data = None
#         self.layers_dir = None
#         self.models_dir = None
#         self.report_file = None
#         self.jpg_file = None
#         self.tif_file = None
#         self.model_images = None
#         self.model_output = None
#         self.dir = None

#     def get_field_data(self):
#         if self.field_data is not None:
#             return self.field_data
#         res = glob.glob(os.path.join(self.name, '*.csv'))
#         if len(res) > 0:
#             self.field_data = res[0]
#             return res[0]
#         return None

#     def get_layers_dir(self):
#         if self.layers_dir is not None:
#             return self.layers_dir
#         layer_dir = os.path.join(self.dir, 'layers')
#         if os.path.exists(layer_dir):
#             self.layer_dir = layer_dir
#         else:
#             self.layer_dir = os.mkdir(layer_dir)
#         return self.layer_dir

#     def get_models_dir(self):
#         if self.model_dir is not None:
#             return self.model_dir
#         model_dir = os.path.join(self.dir, 'models')
#         if os.path.exists(model_dir):
#             self.model_dir = model_dir
#         else:
#             self.model_dir = os.mkdir(model_dir)
#         return self.model_dir

#     def get_report_file(self):
#         if self.report_file is None:
#             fname = os.path.splitext(self.get_field_data())[0] + '.html'
#             if os.path.exists(fname):
#                 self.report_file = fname
#         return self.report_file

#     def get_model_output(self):
#         if self.model_output is None:
#             fname = os.path.splitext(self.get_field_data())[0] + '.xml'
#             if os.path.exists(fname):
#                 self.model_output = fname
#         return self.model_output

#     def get_jpg_file(self):
#         if self.jpg_file is None:
#             fname = os.path.splitext(self.get_field_data())[0] + '.jpg'
#             if os.path.exists(fname):
#                 self.jpg_file = fname
#         return self.jpg_file

#     def get_tif_file(self):
#         if self.tif_file is None:
#             fname = os.path.splitext(self.get_field_data())[0] + '.tif'
#             if os.path.exists(fname):
#                 self.tif_file = fname
#         return self.tif_file

#     def get_model_images(self):
#         if self.model_images is not None:
#             return self.model_images
#         output_dir = os.path.join(self.dir, 'ancillaryOutput')
#         if os.path.exists(output_dir):
#             res = glob.glob(os.path.join(output_dir, '*.jpg'))
#             res += glob.glob(os.path.join(output_dir, '*.tif'))
#             self.model_images = res
#         return self.model_images

#     def compute(self):
#         if self.hasInputFromPort('dir'):
#             self.dir = self.getInputFromPort('dir').name

#         # find the csv file
#         if self.hasInputFromPort('fieldData'):
#             field_data = self.getInputFromPort('fieldData')
#             shutil.copy(field_data, self.dir)
#             self.field_data = os.path.join(self.dir, 
#                                            os.path.basename(field_data))
#         if self.hasInputFromPort('addLayer'):
#             all_layers = self.getInputListFromPort('addLayer')
#             for layer in all_layers:
#                 shutil.copy(layer.name, self.get_layers_dir())
#         if self.hasInputFromPort('addModel'):
#             all_models = self.getInputListFromPort('addModel')
#             for model in all_models:
#                 shutil.copy(model.name, self.get_models_dir())

#         # self is already set by Module.__init__

#     _input_ports = [('dir', '(edu.utah.sci.vistrails.basic:Directory)'),
#                     ('fieldData', '(edu.utah.sci.vistrails.basic:File)'), 
#                     ('addLayer', '(edu.utah.sci.vistrails.basic:File)'), 
#                     ('addModel', '(edu.utah.sci.vistrails.basic:File)')]
#     _output_ports = [('self', '(edu.utah.sci.vistrails.sahm:WorkingDir)')]

# class CreateWorkingDir(Module):
#     def compute(self):
#         root_dir = self.getInputFromPort('rootDir')
#         field_data = self.forceGetInputFromPort('fieldData')
#         layers = self.forceGetInputListFromPort('addLayer')
#         models = self.forceGetInputListFromPort('addModel')

#         root_dir_name = root_dir.name
#         now = datetime.today()
#         wd_dir = os.path.join(root_dir_name, 'WD-%d-%d-%d-%d-%d-%d' %
#                               (now.year, now.month, now.day, now.hour, 
#                                now.minute, now.second))
#         if os.path.exists(wd_dir):
#             if not os.path.isdir(wd_dir):
#                 raise ModuleError('Cannot create working directory "%s".'
#                                   'File exists' %  wd_dir)
#             else:
#                 if not os.path.exists(os.path.join(wd_dir, 'ancillaryOutput')):
#                     os.mkdir(os.path.join(wd_dir, 'ancillaryOutput'))
#                 layers_dir = os.path.join(wd_dir, 'layers')
#                 if not os.path.exists(layers_dir):
#                     os.mkdir(layers_dir)
#                     os.mkdir(os.path.join(layers_dir, 'categorical'))
#                 models_dir = os.path.join(wd_dir, 'models')
#                 if not os.path.exists(models_dir):
#                     os.mkdir(models_dir)
#         else:
#             os.mkdir(wd_dir)
#             os.mkdir(os.path.join(wd_dir, 'ancillaryOutput'))
#             layers_dir = os.path.join(wd_dir, 'layers')
#             os.mkdir(layers_dir)
#             os.mkdir(os.path.join(layers_dir, 'categorical'))
#             models_dir = os.path.join(wd_dir, 'models')
#             os.mkdir(models_dir)

#         wd = WorkingDir()
#         wd.layers_dir = layers_dir
#         wd.models_dir = models_dir
#         wd.dir = wd_dir
#         shutil.copy(field_data.name, wd_dir)
#         wd.field_data = os.path.join(wd_dir, os.path.basename(field_data.name))
#         for layer in layers:
#             shutil.copy(layer.name, layers_dir)
#         for model in models:
#             shutil.copy(model.name, models_dir)

#         self.setResult('workingDir', wd)

#         # recreate this to do this ourselves
#         # make the directory behind the scenes?
#         # allow user to output?
#         # res = run_cmd_line_jar('CreateWorkingDir.jar')

#         # if res[0] != 0:
#         #     raise ModuleError(self, output)
    
#     _input_ports = [('rootDir', '(edu.utah.sci.vistrails.basic:Directory)'),
#                     ('fieldData', '(edu.utah.sci.vistrails.basic:File)'), 
#                     ('addLayer', '(edu.utah.sci.vistrails.basic:File)'), 
#                     ('addModel', '(edu.utah.sci.vistrails.basic:File)')]
#     _output_ports = [('workingDir', \
#                          '(edu.utah.sci.vistrails.sahm:WorkingDir)')]

# class MdsBuilder(Module):
#     def compute(self):
#         working_dir = self.getInputFromPort('workingDir')
#         args = {'-f': working_dir.get_field_data(),
#                 '-i': working_dir.get_layers_dir(),
#                 '-o': working_dir.dir}
#         res, output = run_cmd_line_jar('MdsBuilder.jar', args)
#         if res != 0:
#             raise ModuleError(self, ''.join(output))
#         self.setResult('workingDir', working_dir)

#     _input_ports = [('workingDir', \
#                          '(edu.utah.sci.vistrails.sahm:WorkingDir)')]
#     _output_ports = [('workingDir', \
#                          '(edu.utah.sci.vistrails.sahm:WorkingDir)')]

# class ModelBuilder(Module):
#     def compute(self):
#         working_dir = self.getInputFromPort('workingDir')
#         args = {'-i': working_dir.dir,
#                 '-o': working_dir.dir}
#         res, output = run_cmd_line_jar('ModelBuilder.jar', args)
#         if res != 0:
#             raise ModuleError(self, ''.join(output))
#         self.setResult('workingDir', working_dir)
#         image_files = []
#         for image in working_dir.get_model_images():
#             image_files.append(File.translate_to_python(image))
#         self.setResult('modelImages', image_files)

#     _input_ports = [('workingDir', \
#                          '(edu.utah.sci.vistrails.sahm:WorkingDir)')]
#     _output_ports = [('workingDir', \
#                          '(edu.utah.sci.vistrails.sahm:WorkingDir)'),
#                      ('modelImages',
#                       '(edu.utah.sci.vistrails.control_flow:ListOfElements)')]

# class MapBuilder(Module):
#     def compute(self):
#         working_dir = self.getInputFromPort('workingDir')
#         args = {'-f': working_dir.get_model_output(),
#                 '-o': working_dir.dir}
#         res, output = run_cmd_line_jar('MapBuilder.jar', args)
#         if res != 0:
#             raise ModuleError(self, ''.join(output))
#         self.setResult('workingDir', working_dir)
#         jpg_file = File.translate_to_python(working_dir.get_jpg_file())
#         self.setResult('jpgFile', jpg_file)
#         tif_file = File.translate_to_python(working_dir.get_tif_file())
#         self.setResult('tifFile', tif_file)

#     _input_ports = [('workingDir', \
#                          '(edu.utah.sci.vistrails.sahm:WorkingDir)')]
#     _output_ports = [('workingDir', \
#                          '(edu.utah.sci.vistrails.sahm:WorkingDir)'),
#                      ('jpgFile', '(edu.utah.sci.vistrails.basic:File)'),
#                      ('tifFile', '(edu.utah.sci.vistrails.basic:File)')]

# class RptBuilder(Module):
#     def compute(self):
#         working_dir = self.getInputFromPort('workingDir')
#         args = {'-f': working_dir.get_model_output()}
#         res, output = run_cmd_line_jar('RptBuilder.jar', args)
#         if res != 0:
#             raise ModuleError(self, ''.join(output))
#         self.setResult('workingDir', working_dir)
#         report_file = File.translate_to_python(working_dir.get_report_file())
#         self.setResult('reportFile', report_file)

#     _input_ports = [('workingDir', \
#                          '(edu.utah.sci.vistrails.sahm:WorkingDir)')]
#     _output_ports = [('workingDir', \
#                          '(edu.utah.sci.vistrails.sahm:WorkingDir)'),
#                       ('reportFile', '(edu.utah.sci.vistrails.basic:File)')]

class FieldData(File):
    # _input_ports = [('csvFile', '(edu.utah.sci.vistrails.basic:File)')]
    _output_ports = [('value', '(gov.usgs.sahm:FieldData:DataInput)'),
                     ('value_as_string', 
                      '(edu.utah.sci.vistrails.basic:String)', True)]

class Predictor(File):
    _input_ports = [('categorical', '(edu.utah.sci.vistrails.basic:Boolean)')]
    _output_ports = [('value', '(gov.usgs.sahm:Predictor:DataInput)'),
                     ('value_as_string', 
                      '(edu.utah.sci.vistrails.basic:String)', True)]
    
# class CategoricalPredictor(Module):
#     pass

# class NonCategoricalPredictor(Module):
#     pass

class RemoteSensingPredictor(Predictor):
    pass

class ClimatePredictor(Predictor):
    pass

class StaticPredictor(Predictor):
    pass

class SpatialDef(Module):
    _output_ports = [('spatialDef', '(gov.usgs.sahm:SpatialDef:DataInput)')]

class MergedDataSet(File):
    pass

class MDSBuilder(Module):
    _input_ports = [('fieldData', '(gov.usgs.sahm:FieldData:DataInput)'),
                    ('predictor', '(gov.usgs.sahm:Predictor:DataInput)')]
    _output_ports = [('dataset', '(gov.usgs.sahm:MergedDataSet:DataInput)')]

    def compute(self):
        field_data = self.getInputFromPort('fieldData')
        predictors = self.getInputListFromPort('predictor')
        predictor_dir = tempfile.mkdtemp(prefix='sahm')
        os.mkdir(os.path.join(predictor_dir, 'categorical'))
        for predictor in predictors:
            shutil.copy(predictor.name, predictor_dir)
        output_dir = tempfile.mkdtemp(prefix='sahm')
        args = {'-f': field_data.name,
                '-i': predictor_dir,
                '-o': output_dir}
        res, output = run_cmd_line_jar('MdsBuilder.jar', args)
        if res != 0:
            raise ModuleError(self, ''.join(output))
        
        dataset = create_file_module(os.path.join(output_dir, 
                                                  os.listdir(output_dir)[0]),
                                     MergedDataSet())
#         dataset = MergedDataSet.translate_to_python(
#             os.path.join(output_dir, os.listdir(output_dir)[0]))
        self.setResult('dataset', dataset)

class FieldDataQuery(Module):
    _input_ports = [('dataset', '(gov.usgs.sahm:MergedDataSet:DataInput)'),
                    ('spatial_def', '(gov.usgs.sahm:SpatialDef:DataInput)')]
    _output_ports = [('dataset', '(gov.usgs.sahm:MergedDataSet:DataInput)')]

class Resampler(Module):
    _input_ports = [('predictor', '(gov.usgs.sahm:Predictor:DataInput)'),
                    ('spatialDef', '(gov.usgs.sahm:SpatialDef:DataInput)')]
    _output_ports = [('predictor', '(gov.usgs.sahm:Predictor:DataInput)')]

class Model(File):
    _input_ports = [('value', '(edu.utah.sci.vistrails.basic:File)', True)]
    _output_ports = [('value', '(gov.usgs.sahm:Model:Models)'),
                     ('value_as_string', 
                      '(edu.utah.sci.vistrails.basic:String)', True)]
    
    def compute(self):
        self.upToDate = True
        self.setResult('value', self)
#         self.set_input_port('value', 
#                             ModuleConnector(create_file_module(self.name), 'value'))
#         File.compute(self)

        
class GLM(Model):
    def __init__(self):
        global models_path
        Model.__init__(self)
        self.name = os.path.join(models_path, 'FIT_GLM_pluggable.r')

class RandomForest(Model):
    def __init__(self):
        global models_path
        Model.__init__(self)
        self.name = os.path.join(models_path, 'FIT_RF_pluggable.r')

class MARS(Model):
    def __init__(self):
        global models_path
        Model.__init__(self)
        self.name = os.path.join(models_path, 'FIT_MARS_pluggable.r')

class MAXENT(Model):
    def __init__(self):
        global models_path
        Model.__init__(self)
        self.name = os.path.join(models_path, 'RunMaxEnt.jar')

class BoostedRegressionTree(Model):
    def __init__(self):
        global models_path
        Model.__init__(self)
        self.name = os.path.join(models_path, 'FIT_BRT_pluggable.r')

class ModelBuilder(Module):
    _input_ports = [('model', '(gov.usgs.sahm:Model:Models)'),
                    ('dataset', '(gov.usgs.sahm:MergedDataSet:DataInput)'),
                    ('predictor', '(gov.usgs.sahm:Predictor:DataInput)')]
    _output_ports = [('modelRunOutput', '(edu.utah.sci.vistrails.basic:File)')]
    
    def compute(self):
        models = self.getInputListFromPort('model')
        dataset = self.getInputFromPort('dataset')
        predictors = self.getInputListFromPort('predictor')
        working_dir = tempfile.mkdtemp(prefix='sahm')
        shutil.copy(dataset.name, working_dir)
        models_dir = os.path.join(working_dir, 'models')
        os.mkdir(models_dir)
        for model in models:
            print model
            shutil.copy(model.name, models_dir)
        predictors_dir = os.path.join(working_dir, 'layers')
        os.mkdir(predictors_dir)
        for predictor in predictors:
            shutil.copy(predictor.name, predictors_dir)
        ancillary_output_dir = os.path.join(working_dir, 'ancillaryOutput')
        os.mkdir(ancillary_output_dir)
        args = {'-i': working_dir,
                '-o': working_dir}
        res, output = run_cmd_line_jar('ModelBuilder.jar', args)
        if res != 0:
            raise ModuleError(self, ''.join(output))
        
        run_output = None
        for file in os.listdir(working_dir):
            if file.endswith('xml'):
                run_output = file
        print 'modelRunOutput', os.path.join(working_dir, run_output)
#         modelRunOutput = File.translate_to_python(os.path.join(working_dir, 
#                                                                run_output))
#         modelRunOutput.set_input_port('value', ModuleConnector(modelRunOutput,
#                                                                'value'))
        modelRunOutput = create_file_module(os.path.join(working_dir, 
                                                         run_output))
        self.setResult('modelRunOutput', modelRunOutput)

#         image_files = []
#         for image in working_dir.get_model_images():
#             image_files.append(File.translate_to_python(image))
#         self.setResult('modelImages', image_files)

class MapBuilder(Module):
    _input_ports = [('modelRunOutput', '(edu.utah.sci.vistrails.basic:File)')]
    _output_ports = [('tiffImage', '(edu.utah.sci.vistrails.basic:File)')]

    def compute(self):
        model_output = self.getInputFromPort('modelRunOutput')
        output_dir = tempfile.mkdtemp(prefix='sahm')
        args = {'-f': model_output.name,
                '-o': output_dir}
        res, output = run_cmd_line_jar('MapBuilder.jar', args)
        if res != 0:
            raise ModuleError(self, ''.join(output))
        tiff_file = None
        for file in os.listdir(output_dir):
            if file.endswith('tif'):
                tiff_file = file
        print 'tiffImage', os.path.join(output_dir, tiff_file)
#         tiffImage = File.translate_to_python(os.path.join(output_dir, 
#                                                           tiff_file))
#         tiffImage.set_input_port('value', ModuleConnector(tiffImage, 'value'))
        tiffImage = create_file_module(os.path.join(output_dir, tiff_file))
        self.setResult('tiffImage', tiffImage)
        print 'done'
#         self.setResult('workingDir', working_dir)
#         jpg_file = File.translate_to_python(working_dir.get_jpg_file())
#         self.setResult('jpgFile', jpg_file)
#         tif_file = File.translate_to_python(working_dir.get_tif_file())
#         self.setResult('tifFile', tif_file)

class ReportBuilder(Module):
    _input_ports = [('modelRunOutput', '(edu.utah.sci.vistrails.basic:File)'),
                    ('tiffImage', '(edu.utah.sci.vistrails.basic:File)'),
                    ('dataset', '(edu.utah.sci.vistrails.basic:File)')]
    _output_ports = [('htmlFile', '(edu.utah.sci.vistrails.basic:File)')]

    def compute(self):
        print "running ReportBuilder"
        model_output = self.getInputFromPort('modelRunOutput')
        print "modelRunOuptut done"
        tiff_image = self.getInputFromPort('tiffImage')
        print "tiff_image done"
        dataset = self.getInputFromPort('dataset')
        print "dataset done"
        report_dir = tempfile.mkdtemp(prefix='sahm')
        shutil.copy(model_output.name, report_dir)
        base_fname = os.path.splitext(model_output.name)[0]
        tiff_fname = os.path.join(report_dir, base_fname + '.tif')
        shutil.copy(tiff_image.name, tiff_fname)
        dataset_fname = os.path.join(report_dir, base_fname + '.mds')
        shutil.copy(dataset.name, dataset_fname)
        args = {'-f': os.path.join(report_dir, model_output.name)}
        res, output = run_cmd_line_jar('RptBuilder.jar', args)
        if res != 0:
            raise ModuleError(self, ''.join(output))
        html_file = None
        for file in os.listdir(os.path.dirname(model_output.name)):
            if file.endswith('html'):
                html_file = file
        print 'html_file', os.path.join(os.path.dirname(model_output.name),  html_file)
#         self.setResult('htmlFile', 
#                        File.translate_to_python(os.path.join(os.path.dirname(model_output.name),  html_file)))
        htmlFile = create_file_module(os.path.join(
                os.path.dirname(model_output.name), html_file))
        self.setResult('htmlFile', htmlFile)

# def package_dependencies():
#     return ['edu.utah.sci.vistrails.control_flow']

def initialize():
    global sahm_path, models_path
    sahm_path = configuration.sahm_path
    models_path = configuration.models_path

_modules = [(FieldData, {'namespace': 'DataInput'}),
            (Predictor, {'namespace': 'DataInput'}),
            (RemoteSensingPredictor, {'namespace': 'DataInput'}),
            (ClimatePredictor, {'namespace': 'DataInput'}),
            (StaticPredictor, {'namespace': 'DataInput'}),
            (SpatialDef, {'namespace': 'DataInput'}),
            (MergedDataSet, {'namespace': 'DataInput'}),
            (Resampler, {'namespace': 'Tools'}),
            (FieldDataQuery, {'namespace': 'Tools'}),
            (MDSBuilder, {'namespace': 'Tools'}),
            (ModelBuilder, {'namespace': 'Tools'}),
            (MapBuilder, {'namespace': 'Tools'}),
            (Model, {'namespace': 'Models'}),
            (GLM, {'namespace': 'Models'}),
            (RandomForest, {'namespace': 'Models'}),
            (MARS, {'namespace': 'Models'}),
            (MAXENT, {'namespace': 'Models'}),
            (BoostedRegressionTree, {'namespace': 'Models'}),
            (ReportBuilder, {'namespace': 'Reporting'}),
             ]
 
# _modules = [WorkingDir, 
#             CreateWorkingDir,
#             MdsBuilder,
#             ModelBuilder,
#             MapBuilder,
#             RptBuilder,
#             (FieldData, {'namespace': 'DataInput'})
#             (
# ]
# _subworkflows = ['QuickMap.xml']
