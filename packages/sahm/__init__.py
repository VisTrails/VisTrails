from datetime import datetime
import glob
import itertools
import os
import shutil

from core.configuration import ConfigurationObject
from core.modules.vistrails_module import Module, ModuleError
from core.modules.basic_modules import File, Directory
from core.system import list2cmdline, execute_cmdline

name = "SAHM"
identifier = "edu.utah.sci.vistrails.sahm"
version = '0.0.1'

sahm_path = None
configuration = \
    ConfigurationObject(sahm_path='/vistrails/local_packages/sahm/SAHM')

def run_cmd_line_jar(jar_name, args):
    arg_items = list(itertools.chain(*args.items()))
    output = []
    jar_name = os.path.join(sahm_path, jar_name)
    cmdline = ['java', '-jar', jar_name] + arg_items
    print 'running', cmdline
    res = execute_cmdline(['java', '-jar', jar_name] + arg_items, output)
    return res, output
                     
class WorkingDir(Module):
    def __init__(self):
        self.field_data = None
        self.layers_dir = None
        self.models_dir = None
        self.report_file = None
        self.jpg_file = None
        self.tif_file = None
        self.model_images = None
        self.model_output = None
        self.dir = None

    def get_field_data(self):
        if self.field_data is not None:
            return self.field_data
        res = glob.glob(os.path.join(self.name, '*.csv'))
        if len(res) > 0:
            self.field_data = res[0]
            return res[0]
        return None

    def get_layers_dir(self):
        if self.layers_dir is not None:
            return self.layers_dir
        layer_dir = os.path.join(self.dir, 'layers')
        if os.path.exists(layer_dir):
            self.layer_dir = layer_dir
        else:
            self.layer_dir = os.mkdir(layer_dir)
        return self.layer_dir

    def get_models_dir(self):
        if self.model_dir is not None:
            return self.model_dir
        model_dir = os.path.join(self.dir, 'models')
        if os.path.exists(model_dir):
            self.model_dir = model_dir
        else:
            self.model_dir = os.mkdir(model_dir)
        return self.model_dir

    def get_report_file(self):
        if self.report_file is None:
            fname = os.path.splitext(self.get_field_data())[0] + '.html'
            if os.path.exists(fname):
                self.report_file = fname
        return self.report_file

    def get_model_output(self):
        if self.model_output is None:
            fname = os.path.splitext(self.get_field_data())[0] + '.xml'
            if os.path.exists(fname):
                self.model_output = fname
        return self.model_output

    def get_jpg_file(self):
        if self.jpg_file is None:
            fname = os.path.splitext(self.get_field_data())[0] + '.jpg'
            if os.path.exists(fname):
                self.jpg_file = fname
        return self.jpg_file

    def get_tif_file(self):
        if self.tif_file is None:
            fname = os.path.splitext(self.get_field_data())[0] + '.tif'
            if os.path.exists(fname):
                self.tif_file = fname
        return self.tif_file

    def get_model_images(self):
        if self.model_images is not None:
            return self.model_images
        output_dir = os.path.join(self.dir, 'ancillaryOutput')
        if os.path.exists(output_dir):
            res = glob.glob(os.path.join(output_dir, '*.jpg'))
            res += glob.glob(os.path.join(output_dir, '*.tif'))
            self.model_images = res
        return self.model_images

    def compute(self):
        if self.hasInputFromPort('dir'):
            self.dir = self.getInputFromPort('dir').name

        # find the csv file
        if self.hasInputFromPort('fieldData'):
            field_data = self.getInputFromPort('fieldData')
            shutil.copy(field_data, self.dir)
            self.field_data = os.path.join(self.dir, 
                                           os.path.basename(field_data))
        if self.hasInputFromPort('addLayer'):
            all_layers = self.getInputListFromPort('addLayer')
            for layer in all_layers:
                shutil.copy(layer.name, self.get_layers_dir())
        if self.hasInputFromPort('addModel'):
            all_models = self.getInputListFromPort('addModel')
            for model in all_models:
                shutil.copy(model.name, self.get_models_dir())

        # self is already set by Module.__init__

    _input_ports = [('dir', '(edu.utah.sci.vistrails.basic:Directory)'),
                    ('fieldData', '(edu.utah.sci.vistrails.basic:File)'), 
                    ('addLayer', '(edu.utah.sci.vistrails.basic:File)'), 
                    ('addModel', '(edu.utah.sci.vistrails.basic:File)')]
    _output_ports = [('self', '(edu.utah.sci.vistrails.sahm:WorkingDir)')]

class CreateWorkingDir(Module):
    def compute(self):
        root_dir = self.getInputFromPort('rootDir')
        field_data = self.forceGetInputFromPort('fieldData')
        layers = self.forceGetInputListFromPort('addLayer')
        models = self.forceGetInputListFromPort('addModel')

        root_dir_name = root_dir.name
        now = datetime.today()
        wd_dir = os.path.join(root_dir_name, 'WD-%d-%d-%d-%d-%d-%d' %
                              (now.year, now.month, now.day, now.hour, 
                               now.minute, now.second))
        if os.path.exists(wd_dir):
            if not os.path.isdir(wd_dir):
                raise ModuleError('Cannot create working directory "%s".'
                                  'File exists' %  wd_dir)
            else:
                if not os.path.exists(os.path.join(wd_dir, 'ancillaryOutput')):
                    os.mkdir(os.path.join(wd_dir, 'ancillaryOutput'))
                layers_dir = os.path.join(wd_dir, 'layers')
                if not os.path.exists(layers_dir):
                    os.mkdir(layers_dir)
                    os.mkdir(os.path.join(layers_dir, 'categorical'))
                models_dir = os.path.join(wd_dir, 'models')
                if not os.path.exists(models_dir):
                    os.mkdir(models_dir)
        else:
            os.mkdir(wd_dir)
            os.mkdir(os.path.join(wd_dir, 'ancillaryOutput'))
            layers_dir = os.path.join(wd_dir, 'layers')
            os.mkdir(layers_dir)
            os.mkdir(os.path.join(layers_dir, 'categorical'))
            models_dir = os.path.join(wd_dir, 'models')
            os.mkdir(models_dir)

        wd = WorkingDir()
        wd.layers_dir = layers_dir
        wd.models_dir = models_dir
        wd.dir = wd_dir
        shutil.copy(field_data.name, wd_dir)
        wd.field_data = os.path.join(wd_dir, os.path.basename(field_data.name))
        for layer in layers:
            shutil.copy(layer.name, layers_dir)
        for model in models:
            shutil.copy(model.name, models_dir)

        self.setResult('workingDir', wd)

        # recreate this to do this ourselves
        # make the directory behind the scenes?
        # allow user to output?
        # res = run_cmd_line_jar('CreateWorkingDir.jar')

        # if res[0] != 0:
        #     raise ModuleError(self, output)
    
    _input_ports = [('rootDir', '(edu.utah.sci.vistrails.basic:Directory)'),
                    ('fieldData', '(edu.utah.sci.vistrails.basic:File)'), 
                    ('addLayer', '(edu.utah.sci.vistrails.basic:File)'), 
                    ('addModel', '(edu.utah.sci.vistrails.basic:File)')]
    _output_ports = [('workingDir', \
                         '(edu.utah.sci.vistrails.sahm:WorkingDir)')]

class MdsBuilder(Module):
    def compute(self):
        working_dir = self.getInputFromPort('workingDir')
        args = {'-f': working_dir.get_field_data(),
                '-i': working_dir.get_layers_dir(),
                '-o': working_dir.dir}
        res, output = run_cmd_line_jar('MdsBuilder.jar', args)
        if res != 0:
            raise ModuleError(self, ''.join(output))
        self.setResult('workingDir', working_dir)

    _input_ports = [('workingDir', \
                         '(edu.utah.sci.vistrails.sahm:WorkingDir)')]
    _output_ports = [('workingDir', \
                         '(edu.utah.sci.vistrails.sahm:WorkingDir)')]

class ModelBuilder(Module):
    def compute(self):
        working_dir = self.getInputFromPort('workingDir')
        args = {'-i': working_dir.dir,
                '-o': working_dir.dir}
        res, output = run_cmd_line_jar('ModelBuilder.jar', args)
        if res != 0:
            raise ModuleError(self, ''.join(output))
        self.setResult('workingDir', working_dir)
        image_files = []
        for image in working_dir.get_model_images():
            image_files.append(File.translate_to_python(image))
        self.setResult('modelImages', image_files)

    _input_ports = [('workingDir', \
                         '(edu.utah.sci.vistrails.sahm:WorkingDir)')]
    _output_ports = [('workingDir', \
                         '(edu.utah.sci.vistrails.sahm:WorkingDir)'),
                     ('modelImages',
                      '(edu.utah.sci.vistrails.control_flow:ListOfElements)')]

class MapBuilder(Module):
    def compute(self):
        working_dir = self.getInputFromPort('workingDir')
        args = {'-f': working_dir.get_model_output(),
                '-o': working_dir.dir}
        res, output = run_cmd_line_jar('MapBuilder.jar', args)
        if res != 0:
            raise ModuleError(self, ''.join(output))
        self.setResult('workingDir', working_dir)
        jpg_file = File.translate_to_python(working_dir.get_jpg_file())
        self.setResult('jpgFile', jpg_file)
        tif_file = File.translate_to_python(working_dir.get_tif_file())
        self.setResult('tifFile', tif_file)

    _input_ports = [('workingDir', \
                         '(edu.utah.sci.vistrails.sahm:WorkingDir)')]
    _output_ports = [('workingDir', \
                         '(edu.utah.sci.vistrails.sahm:WorkingDir)'),
                     ('jpgFile', '(edu.utah.sci.vistrails.basic:File)'),
                     ('tifFile', '(edu.utah.sci.vistrails.basic:File)')]

class RptBuilder(Module):
    def compute(self):
        working_dir = self.getInputFromPort('workingDir')
        args = {'-f': working_dir.get_model_output()}
        res, output = run_cmd_line_jar('RptBuilder.jar', args)
        if res != 0:
            raise ModuleError(self, ''.join(output))
        self.setResult('workingDir', working_dir)
        report_file = File.translate_to_python(working_dir.get_report_file())
        self.setResult('reportFile', report_file)

    _input_ports = [('workingDir', \
                         '(edu.utah.sci.vistrails.sahm:WorkingDir)')]
    _output_ports = [('workingDir', \
                         '(edu.utah.sci.vistrails.sahm:WorkingDir)'),
                      ('reportFile', '(edu.utah.sci.vistrails.basic:File)')]

def package_dependencies():
    return ['edu.utah.sci.vistrails.control_flow']

def initialize():
    global sahm_path
    sahm_path = configuration.sahm_path
    
_modules = [WorkingDir, 
            CreateWorkingDir,
            MdsBuilder,
            ModelBuilder,
            MapBuilder,
            RptBuilder]
_subworkflows = ['QuickMap.xml']
