import csv
from datetime import datetime
import glob
import itertools
import os
import shutil
import sys
import subprocess

from core.modules.vistrails_module import Module, ModuleError, ModuleConnector
from core.modules.basic_modules import File, Directory, new_constant, Constant
from core.modules.basic_modules import List
from core.system import list2cmdline, execute_cmdline


from widgets import get_predictor_widget, get_predictor_config
#from RunPARC import PARC
from SelectPredictorsLayers import SelectPredictorsLayers
from utils import map_ports, path_value, create_file_module, createrootdir 
from utils import create_dir_module, mktempfile, mktempdir, cleantemps
from utils import dir_path_value, collapse_dictionary, tif_to_color_jpeg

#import our python SAHM Processing files
import packages.sahm.pySAHM.FieldDataQuery as FDQ
import packages.sahm.pySAHM.MDSBuilder as MDSB
import packages.sahm.pySAHM.PARC as parc

identifier = 'gov.usgs.sahm'

def run_cmd_line_jar(jar_name, args):
    arg_items = list(itertools.chain(*args.items()))
    output = []
    jar_name = os.path.join(sahm_path, jar_name)
    cmdline = ['java', '-jar', jar_name] + arg_items
    print 'running', cmdline
    res = execute_cmdline(['java', '-jar', jar_name] + arg_items, output)
    return res, output

def run_cmd_line_py(jar_name, args):
    arg_items = list(itertools.chain(*args.items()))
    output = []
    jar_name = os.path.join(sahm_path, jar_name)
    cmdline = ['java', '-jar', jar_name] + arg_items
    print 'running', cmdline
    res = execute_cmdline(['java', '-jar', jar_name] + arg_items, output)
    return res, output

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

class TemplateLayer(File):
    # _input_ports = [('csvFile', '(edu.utah.sci.vistrails.basic:File)')]
    _output_ports = [('value', '(gov.usgs.sahm:TemplateLayer:DataInput)'),
                     ('value_as_string', '(edu.utah.sci.vistrails.basic:String)', True)]
    pass

class SingleInputPredictor(Predictor):
    pass

class SpatialDef(Module):
    _output_ports = [('spatialDef', '(gov.usgs.sahm:SpatialDef:DataInput)')]

class MergedDataSet(File):
    _input_ports = expand_ports([('mdsFile', '(edu.utah.sci.vistrails.basic:File)')])
    _output_ports = expand_ports([('value', '(gov.usgs.sahm:MergedDataSet:DataInput)')])
    
    True
    

class Model2(Module):
    _input_ports = [('mdsFile', '(gov.usgs.sahm:MergedDataSet:DataInput)')]
    _output_ports = [('BinaryMap', '(edu.utah.sci.vistrails.basic:File)'), 
                     ('ProbabilityMap', '(edu.utah.sci.vistrails.basic:File)'),
                     ('AUC_plot', '(edu.utah.sci.vistrails.basic:File)'),
                     ('ResponseCurves', '(edu.utah.sci.vistrails.basic:File)'),
                     ('Text_Output', '(edu.utah.sci.vistrails.basic:File)')]

    def compute(self):
        mdsFile = dir_path_value(self.forceGetInputFromPort('mdsFile', []))
        print "mdsFile: ", mdsFile
        print "sys.path[0]", sys.path[0]
        print "sys.argv[0]", sys.argv[0]
        
        global r_path
        print r_path
        
        r_path = r_path + ""
        program = r_path + r"\i386\Rterm.exe" #-q prevents program from running
        Script = r"I:\VisTrails\Central_VisTrailsInstall_debug\vistrails\packages\sahm\pySAHM\Resources\R_Modules\FIT_BRT_pluggable.r"
        output_dname = mktempdir(prefix='output_')
        
        args = "c=" + mdsFile + " o=" + output_dname + " rc=ResponseBinary"
        
        command = program + " --vanilla -f " + Script + " --args " + args
        print command
        p = subprocess.Popen(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

        # Second, use communicate to run the command; communicate() returns a
        #   tuple (stdoutdata, stderrdata)
        print "starting R Processing"

        ret = p.communicate()
        if ret[1]:
            print ret[1]
        del(ret)
        
        
        input_fname = os.path.join(output_dname,"brt_1_prob_map.tif")
        output_fname = mktempfile(prefix='brt_1_prob_map_', suffix='.jpeg')
        tif_to_color_jpeg(input_fname, output_fname)
        
        
        outFileName = os.path.join(output_dname,"brt_1_bin_map.tif")
        output_file1 = create_file_module(outFileName)
        self.setResult('BinaryMap', output_file1)
        
        outFileName = os.path.join(output_dname,"brt_1_output.txt")
        output_file2 = create_file_module(outFileName)
        self.setResult('Text_Output', output_file2)
        
        outFileName = os.path.join(output_dname,"brt_1_auc_plot.jpg")
        print "out auc: ", outFileName
        output_file3 = create_file_module(outFileName)
        self.setResult('AUC_plot', output_file3)
        
        outFileName = output_fname
        print "brt_1_prob_map.tif: ", outFileName
        output_file4 = create_file_module(outFileName)
        self.setResult('ProbabilityMap', output_file4)
        
        outFileName = os.path.join(output_dname,"brt_1_response_curves.pdf")
        output_file5 = create_file_module(outFileName)
        self.setResult('ResponseCurves', output_file5)
        
        
        print "\nfinished BRT builder\n"
        




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

    _input_ports = expand_ports([('PredictorsDir', 'basic:Directory'),
                                 ('fieldData', '(gov.usgs.sahm:FieldData:DataInput)'),
                                 ('minValue', 'basic:Float')]
                                 )
    _output_ports = expand_ports([('mdsFile', '(gov.usgs.sahm:MergedDataSet:DataInput)')])

    def compute(self):
        port_map = {'fieldData': ('-f', dir_path_value, True),
                    'PredictorsDir': ('-d', path_value, True),
                    'minValue': ('-m', None, False)}
         
        args = map_ports(self, port_map)

        output_fname = mktempfile(prefix='sahm', suffix='.mds')
        args['-o'] = output_fname

        print args
        
        cmd_args = collapse_dictionary(args)
        print cmd_args

        MDSB.run(cmd_args)

        output_file = create_file_module(output_fname)
        
        print "\nfinished running MDS builder\n"
        
        self.setResult('mdsFile', output_file)

class FieldDataQuery(Module):
    _input_ports = expand_ports([('templateLayer', '(gov.usgs.sahm:TemplateLayer:DataInput)'),
                                 ('fieldData', '(gov.usgs.sahm:FieldData:DataInput)'),
                                 ('aggregateRows', 'basic:Boolean'),
                                 ('aggregateRowsByYear', 'basic:Boolean')])
    _output_ports = expand_ports([('fieldData', '(gov.usgs.sahm:FieldData:DataInput)')])
    
    def compute(self):
        port_map = {'fieldData': ('-f', dir_path_value, True),
            'templateLayer': ('-t', dir_path_value, True),
            'aggregateRows': ('-p', None, False),
            'aggregateRowsByYear': ('-y', None, False),
            }
        args = map_ports(self, port_map)

        output_fname = mktempfile(prefix='FDQ_', suffix='.csv')
        print output_fname
        args['-o'] = output_fname
        
        try:
            if args['-p'] == True:
                args['-p'] = ''
            if args['-p'] == False:
                del args['-p']
            if args['-y'] == True:
                args['-y'] = ''
            if args['-y'] == False:
                del args['-y']
        except:
            pass
        
        cmd_args = collapse_dictionary(args)
      

        FDQ.run(cmd_args)
#        
        output_file = create_file_module(args['-o'])
        print "\nfinished running Field Data Query\n"
        self.setResult('fieldData', output_file)

class PARC(Module):
    '''
    This class provides a widget to run the PARC module which
    provides functionality to sync raster layer properties
    with a template dataset
    '''
    configuration = []
    _input_ports = [('predictor', "(gov.usgs.sahm:Predictor:DataInput)"),
                                ('PredictorList', '(gov.usgs.sahm:PredictorList:DataInput)'),
                                ('templateLayer', '(gov.usgs.sahm:TemplateLayer:DataInput)'),
                                ('resampleMethod', '(edu.utah.sci.vistrails.basic:String)'),
                                ('aggregationMethod', '(edu.utah.sci.vistrails.basic:String)')]

    _output_ports = [('PredictorLayersDir', '(edu.utah.sci.vistrails.basic:Directory)')]

    def compute(self):
        port_map = {'aggregationMethod': ('-m',  None, False),
                    'resampleMethod': ('-r', None, False)}
        args = map_ports(self, port_map)

        output_dname = mktempdir(prefix='parc')
        args['-o'] = output_dname

        arg_items = collapse_dictionary(args)

        predictor_list = self.forceGetInputFromPort('PredictorList', [])
        predictor_list.extend(self.forceGetInputListFromPort('predictor'))

        predictors = []
        for predictor in predictor_list:
            predictors.append(os.path.join(predictor.name))

        args = (arg_items + [self.getInputFromPort('templateLayer').name]
               + predictors)
        
        ourPARCer = parc.PARC()
        ourPARCer.main(args)
        print output_dname
        predictorsDir = create_dir_module(output_dname)
        print "\nfinished running PARC\n"
        self.setResult('PredictorLayersDir', predictorsDir)

#class FieldDataQuery(Module):
#    _input_ports = expand_ports([('siteConfig', 'basic:File'),
#                                 ('fieldData', 'basic:File'),
#                                 ('siteName', 'basic:String'),
#                                 ('sessionDir', 'basic:Directory'),
#                                 ('aggregateRows', 'basic:Boolean'),
#                                 ('aggregateRowsByYear', 'basic:Boolean')])
#    _output_ports = expand_ports([('outputDir', 'basic:Directory')])
#
#    def compute(self):
#        port_map = {'siteConfig': ('-c', path_value, True),
#                    'fieldData': ('-f', path_value, False),
#                    'siteName': ('-n', None, True),
#                    'sessionDir': ('-s', path_value, False),
#                    'aggregateRows': ('-p', None, False),
#                    'aggregateRowsByYear': ('-y', None, False),
#                    }
#        
#        args = map_ports(self, port_map)
#        
#        try:
#            if args['-p'] == True:
#                args['-p'] = ''
#            if args['-p'] == False:
#                del args['-p']
#        except:
#            pass
#        
#        output_dname = mktempdir(prefix='sahm')
#        args['-o'] = output_dname
#
#        for k,v in args:
#            print "%s=%s" % (k, v)
#        print args
#        
#        res, output = run_cmd_line_jar('FieldDataQuery.jar', args)
#        if res != 0:
#            raise ModuleError(self, ''.join(output))
#        
#        output_dir = create_dir_module(output_dname)
#        self.setResult('outputDir', output_dir)

class ModelBuilder(Module):
    _input_ports = expand_ports([('mdsFile', 'basic:File'),
                                 ('addModel', 'Models|Model'),
                                 ('PredictorLayersDir', 'basic:Directory'),
                                 ('sessionDir', 'basic:Directory')])
    _output_ports = expand_ports([('outputFile', 'basic:File'),
                                  ('ancillaryDir', 'basic:Directory')])

    def compute(self):
        port_map = {'mdsFile': ('-f', path_value, True),
                    'sessionDir': ('-s', path_value, False),
                    'PredictorLayersDir': ('-i', path_value, False)
                    }
        args = map_ports(self, port_map)
        
        models = self.getInputListFromPort('addModel')
        predictor_list = self.forceGetInputFromPort('predictorList', [])
        predictor_list.extend(self.forceGetInputListFromPort('addPredictor'))

        ancillary_dname = mktempdir(prefix='sahm_ancillary')

        models_dir = mktempdir(prefix='sahm_models')
        for model in models:
            print model
            shutil.copy(model.name, models_dir)
            print "%%% NAME %%%", model.__class__.__name__
            if model.__class__.__name__ == 'MAXENT':
                # create file named RunMaxEnt.args and copy parameters there
                args_fname = os.path.join(models_dir, "RunMaxEnt.args")
                args_f = None
                for port in model._input_ports:
                    print 'checking port:', port[0], port
                    if model.hasInputFromPort(port[0]):
                        port_val = model.getInputFromPort(port[0])
                        if port[1] == "(edu.utah.sci.vistrails.basic:Boolean)":
                            port_val = str(port_val)
                            port_val = port_val[0].lower() + port_val[1:]
                        if args_f is None:
                            args_f = open(args_fname, 'w')
                        print "%s=%s" % (port[0], port_val)
                        print >>args_f, "%s=%s" % (port[0], port_val),
                if args_f is not None:
                    args_f.close()
                    
                # FIXME, use parameters from MAXENT
                # for port in model.input_ports:
                #    port + model.getInputFromPort(port)
                pass
            
#        predictors_dir = mktempdir(prefix='sahm_layers')
#        for predictor in predictor_list:
#            shutil.copy(predictor.name, predictors_dir)

        

        output_fname = mktempfile(prefix='sahm', suffix='.xml')
        args['-a'] = ancillary_dname
        args['-o'] = output_fname
        args['-m'] = models_dir
        #args['-i'] = predictors_dir

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




# FIXME: OK on trunk, changed for current release
#
# PredictorList = new_constant("PredictorList",
#                              List.translate_to_python,
#                              [], staticmethod(lambda x: type(x) == list), 
#                              ClimatePredictorListConfig,
#                              base_class=List)

class PredictorList(Constant):
    _input_ports = expand_ports([('value', 'DataInput|PredictorList'),
                                 ('addPredictor', 'DataInput|Predictor')])
    _output_ports = expand_ports([('value', 'DataInput|PredictorList')])
    
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
            f_list = [create_file_module(v_elt[1]) for v_elt in v]
        else:
            f_list = v
        p_list += f_list
        self.setResult("value", p_list)

def load_max_ent_params():    
    maxent_fname = os.path.join(os.path.dirname(__file__), 'maxent.csv')
    csv_reader = csv.reader(open(maxent_fname, 'rU'))
    # pass on header
    csv_reader.next()
    input_ports = []
    docs = {}
    basic_pkg = 'edu.utah.sci.vistrails.basic'
    p_type_map = {'file/directory': 'Path',
                  'double': 'Float'}
    for row in csv_reader:
        [name, flag, p_type, default, doc] = row
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
        print 'port:', (name, '(' + basic_pkg + ':' + p_type + ')', kwargs)
        docs[name] = doc

    print 'MAXENT:', input_ports
    MAXENT._input_ports = input_ports
    MAXENT._port_docs = docs

    def provide_input_port_documentation(cls, port_name):
        return cls._port_docs[port_name]
    MAXENT.provide_input_port_documentation = \
        classmethod(provide_input_port_documentation)

def initialize():
    global sahm_path, models_path, r_path
    sahm_path = configuration.sahm_path
    models_path = configuration.models_path
    r_path = configuration.r_path
    createrootdir()
    #RunParc.configuration = configuration
    load_max_ent_params()
    
def finalize():
    cleantemps()
    

# FIXME: no need for generate_namespaces on trunk, this is built in to the
#        registry

def generate_namespaces(modules):
    module_list = []
    for namespace, m_list in modules.iteritems():
        for module in m_list:
            m_dict = {'namespace': namespace}
            if type(module) == tuple:
                m_dict.update(module[1])
                module_list.append((module[0], m_dict))
                print 'm_dict:', m_dict
            else:
                module_list.append((module, m_dict))
    return module_list

def build_available_trees():
    trees = {}

    layers_fname = os.path.join(os.path.dirname(__file__), 'layers.csv')
    csv_reader = csv.reader(open(layers_fname, 'rU'))
    # pass on header
    csv_reader.next()
    for row in csv_reader:
        if row[2] not in trees:
            trees[row[2]] = {}
        available_dict = trees[row[2]]
        if 'Daymet' not in available_dict:
            available_dict['Daymet'] = []
        available_dict['Daymet'].append((row[0], row[1], row[3]))            
        # if row[1] not in available_dict:
        #     available_dict[row[1]] = []
        # available_dict[row[1]].append((row[3], row[2]))    
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
                             '(gov.usgs.sahm:%s:DataInput)' % class_name)]})
        modules.append((module, {'configureWidgetType': config_class}))
    return modules

_modules = generate_namespaces({'DataInput': [Predictor, 
                                              PredictorList,
                                              FieldData,
                                              TemplateLayer,
                                              SingleInputPredictor,
                                              MergedDataSet] + \
                                    build_predictor_modules(),
                                'Tools': [FieldDataQuery,
                                          ModelBuilder,
                                          MapBuilder,
                                          MDSBuilder,
                                          PARC,
                                          SelectPredictorsLayers],
                                'Models': [Model,
                                           Model2,
                                           GLM,
                                           RandomForest,
                                           MARS,
                                           MAXENT,
                                           BoostedRegressionTree],
                                'Reporting': [ReportBuilder],
                                })
