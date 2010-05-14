from datetime import datetime
import glob
import itertools
import os
import shutil
import tempfile

from core.modules.vistrails_module import Module, ModuleError, ModuleConnector
from core.modules.basic_modules import File, Directory, new_constant
from core.system import list2cmdline, execute_cmdline

from widgets import ClimatePredictorListConfig

identifier = 'gov.usgs.sahm'
_temp_files = []
_temp_dirs = []

def mktempfile(*args, **kwargs):
    global _temp_files
    (fd, fname) = tempfile.mkstemp(*args, **kwargs)
    os.close(fd)
    _temp_files.append(fname)
    return fname

def mktempdir(*args, **kwargs):
    global _temp_dirs
    dname = tempfile.mkdtemp(*args, **kwargs)
    _temp_dirs.append(dname)
    return dname

def run_cmd_line_jar(jar_name, args):
    arg_items = list(itertools.chain(*args.items()))
    output = []
    jar_name = os.path.join(sahm_path, jar_name)
    cmdline = ['java', '-jar', jar_name] + arg_items
    print 'running', cmdline
    res = execute_cmdline(['java', '-jar', jar_name] + arg_items, output)
    return res, output
     
def path_value(value):
    return value.name

def map_ports(module, port_map):
    args = {}
    for port, (flag, access, required) in port_map.iteritems():
        if required or module.hasInputFromPort(port):
            value = module.getInputFromPort(port)
            if access is not None:
                value = access(value)
            args[flag] = value
    return args

def create_file_module(fname, f=None):
    if f is None:
        f = File()
    f.name = fname
    f.upToDate = True
    return f

def create_dir_module(dname, d=None):
    if d is None:
        d = Directory()
    d.name = dname
    d.upToDate = True
    return d

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
                print 'parts:', parts
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
    print new_port_list
    return new_port_list

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

class MDSBuilder(Module):
    _input_ports = expand_ports([('fieldData', 'basic:File'),
                                 ('minValue', 'basic:Float'),
                                 ('addPredictor', 'DataInput|Predictor'),
                                 ('predictorList', 'DataInput|PredictorList'),
                                 ('sessionDir', 'basic:Directory')])
    _output_ports = expand_ports([('mdsFile', 'basic:File')])

    def compute(self):
        port_map = {'fieldData': ('-f', path_value, False),
                    'minValue': ('-m', None, False),
                    'sessionDir': ('-s', path_value, False)}
        args = map_ports(self, port_map)

        predictor_list = self.forceGetInputFromPort('predictorList', [])
        predictor_list.extend(self.getInputListFromPort('addPredictor'))

        predictors_dir = mktempdir(prefix='sahm_layers')
        for predictor in predictor_list:
            shutil.copy(predictor.name, predictors_dir)

        output_fname = mktempfile(prefix='sahm', suffix='.mds')
        args['-o'] = output_fname
        args['-i'] = predictors_dir

        res, output = run_cmd_line_jar('MdsBuilder.jar', args)
        if res != 0:
            raise ModuleError(self, ''.join(output))

        output_file = create_file_module(output_fname)
        self.setResult('mdsFile', output_file)

class FieldDataQuery(Module):
    _input_ports = expand_ports([('siteConfig', 'basic:File'),
                                 ('fieldData', 'basic:File'),
                                 ('siteName', 'basic:String'),
                                 ('sessionDir', 'basic:Directory'),
                                 ('aggregateRows', 'basic:Boolean'),
                                 ('aggregateRowsByYear', 'basic:Boolean')])
    _output_ports = expand_ports([('outputDir', 'basic:Directory')])

    def compute(self):
        port_map = {'siteConfig': ('-c', path_value, True),
                    'fieldData': ('-f', path_value, False),
                    'siteName': ('-n', None, True),
                    'sessionDir': ('-s', session_dir, False),
                    'aggregateRows': ('-p', None, False),
                    'aggregateRowsByYear': ('-y', None, False),
                    }
        args = map_ports(self, port_map)

        output_dname = mktempdir(prefix='sahm')
        args['-o'] = output_dname

        res, output = run_cmd_line_jar('FieldDataQuery.jar', args)
        if res != 0:
            raise ModuleError(self, ''.join(output))
        
        output_dir = create_dir_module(output_dname)
        self.setResult('outputDir', output_dir)

class ModelBuilder(Module):
    _input_ports = expand_ports([('mdsFile', 'basic:File'),
                                 ('addModel', 'Models|Model'),
                                 ('addPredictor', 'DataInput|Predictor'),
                                 ('predictorList', 'DataInput|PredictorList'),
                                 ('sessionDir', 'basic:Directory')])
    _output_ports = expand_ports([('outputFile', 'basic:File'),
                                  ('ancillaryDir', 'basic:Directory')])

    def compute(self):
        port_map = {'mdsFile': ('-f', path_value, True),
                    'sessionDir': ('-s', path_value, False),
                    }
        args = map_ports(self, port_map)
        
        models = self.getInputListFromPort('addModel')
        predictor_list = self.forceGetInputFromPort('predictorList', [])
        predictor_list.extend(self.getInputListFromPort('addPredictor'))

        ancillary_dname = mktempdir(prefix='sahm_ancillary')

        models_dir = mktempdir(prefix='sahm_models')
        for model in models:
            print model
            shutil.copy(model.name, models_dir)
        predictors_dir = mktempdir(prefix='sahm_layers')
        for predictor in predictor_list:
            shutil.copy(predictor.name, predictors_dir)

        output_fname = mktempfile(prefix='sahm', suffix='.xml')
        args['-a'] = ancillary_dname
        args['-o'] = output_fname
        args['-m'] = models_dir
        args['-i'] = predictors_dir

        res, output = run_cmd_line_jar('ModelBuilder.jar', args)
        if res != 0:
            raise ModuleError(self, ''.join(output))

        output_file = create_file_module(output_fname)
        self.setResult('outputFile', output_file)

        ancillary_dir = create_dir_module(ancillary_dname)
        self.setResult('ancillaryDir', ancillary_dir)

class MapBuilder(Module):
    _input_ports = expand_ports([('ancillaryDir', 'basic:Directory'),
                                 ('xmlFile', 'basic:File'),
                                 ('sessionDir', 'basic:Directory')])
    _output_ports = expand_ports([('tiffImage', 'basic:File'),
                                  ('jpgImage', 'basic:File'),
                                  ('ancillaryDir', 'basic:Directory')])
    
    def compute(self):
        port_map = {'xmlFile': ('-f', path_value, True),
                    'ancillaryDir': ('-a', path_value, True),
                    'sessionDir': ('-s', path_value, False),
                    }
        self.setResult('ancillaryDir', self.getInputFromPort('ancillaryDir'))

        args = map_ports(self, port_map)
        
        tif_fname = mktempfile(prefix='sahm', suffix='.tif')
        args['-t'] = tif_fname
        jpg_fname = mktempfile(prefix='sahm', suffix='.jpg')
        args['-j'] = jpg_fname

        res, output = run_cmd_line_jar('MapBuilder.jar', args)
        if res != 0:
            raise ModuleError(self, ''.join(output))

        tif_file = create_file_module(tif_fname)
        self.setResult('tiffImage', tif_file)

        jpg_file = create_file_module(jpg_fname)
        self.setResult('jpgImage', jpg_file)

class ReportBuilder(Module):
    _input_ports = expand_ports([('fieldData', 'basic:File'),
                                 ('jpgFile', 'basic:File'),
                                 ('mdsFile', 'basic:File'),
                                 ('tifFile', 'basic:File'),
                                 ('xmlFile', 'basic:File'),
                                 ('sessionDir', 'basic:Directory')])
    _output_ports = expand_ports([('htmlFile', 'basic:File')])

    def compute(self):
        port_map = {'fieldData': ('-f', path_value, True),
                    'jpgFile': ('-j', path_value, True),
                    'mdsFile': ('-m', path_value, True),
                    'tifFile': ('-t', path_value, True),
                    'xmlFile': ('-x', path_value, True),
                    'sessionDir': ('-s', path_value, False)}
        args = map_ports(self, port_map)
        
        output_fname = mktempfile(prefix='sahm', suffix='.html')
        args['-o'] = output_fname

        res, output = run_cmd_line_jar('RptBuilder.jar', args)
        if res != 0:
            raise ModuleError(self, ''.join(output))

        output_file = create_file_module(output_fname)
        self.setResult('htmlFile', output_file)

from core.modules.basic_modules import List

PredictorList = new_constant("PredictorList",
                             List.translate_to_python,
                             [], staticmethod(lambda x: type(x) == list), 
                             ClimatePredictorListConfig,
                             base_class=List)

class ClimatePredictors(Module):
    _input_ports = [('selected_list', 
                     '(gov.usgs.sahm:PredictorList:DataInput)')]

def initialize():
    global sahm_path, models_path
    sahm_path = configuration.sahm_path
    models_path = configuration.models_path

def finalize():
    global _temp_files, _temp_dirs
    for file in _temp_files:
        os.remove(file)
    for dir in _temp_dirs:
        shutil.rmtree(dir)

_modules = {'DataInput': [Predictor, 
                          PredictorList,
                          RemoteSensingPredictor,
                          ClimatePredictor,
                          StaticPredictor,
                          ClimatePredictors,
                          SpatialDef],
            'Tools': [Resampler, 
                      FieldDataQuery,
                      MDSBuilder,
                      ModelBuilder,
                      MapBuilder],
            'Models': [Model,
                       GLM,
                       RandomForest,
                       MARS,
                       MAXENT,
                       BoostedRegressionTree],
            'Reporting': [ReportBuilder],
            }
