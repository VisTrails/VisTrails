'''
Module: RunParc
This module wraps the Python PARC module for use as a widget 
in the VisTrails SAHM package

Date: 11/5/2010
'''
from core.modules.vistrails_module import Module, ModuleError
from core.modules.basic_modules import File, Directory, new_constant, Constant
from core.system import list2cmdline, execute_cmdline
import init

#FixMe import map_ports and path_value from the init module doesn't work
#from init import map_ports, path_value
import itertools
import os

def map_ports(module, port_map):
    args = {}
    for port, (flag, access, required) in port_map.iteritems():
        if required or module.hasInputFromPort(port):
            value = module.getInputFromPort(port)
            if access is not None:
                value = access(value)
            args[flag] = value
    return args

def path_value(value):
    return value.name



class PARC(Module):
    '''
    This class provides a widget to run the PARC module which 
    provides functionality to sync raster layer properties
    with a template dataset
    '''
    _input_ports = [('predictor', "(gov.usgs.sahm:Predictor:DataInput)"),
                                ('PredictorList', '(gov.usgs.sahm:PredictorList:DataInput)'),
                                ('templateLayer', '(gov.usgs.sahm:Predictor:DataInput)'),
                                ('outputDir', '(edu.utah.sci.vistrails.basic:Directory)'),
                                ('resampleMethod', '(edu.utah.sci.vistrails.basic:String)'),
                                ('method', '(edu.utah.sci.vistrails.basic:String)')]
    
    _output_ports = [('outputDir', '(edu.utah.sci.vistrails.basic:Directory)')]
    
    def compute(self):
        port_map = {'method': ('-m',  None, False),
                    'resampleMethod': ('-r', None, False),
                    'outputDir': ('-o', path_value, True)}
        args = map_ports(self, port_map)

        print args, type(args)
        arg_items = []
        for k,v in args.items():
            arg_items.append(k)
            arg_items.append(v)
        print arg_items
        for item in arg_items:
            print item
        
        predictor_list = self.forceGetInputFromPort('PredictorList', [])
        predictor_list.extend(self.forceGetInputListFromPort('predictor'))

        predictors = []
        for predictor in predictor_list:
            predictors.append(os.path.join(predictor.name))

        #FixMe replace path here with relative path configuration.sahm_path
        #PARC_py = os.path.join(configuration.sahm_path,"python", "PARC.py")
        PARC_py = r"I:\Vistrails\Central_VisTrailsInstall_debug\VisTrails\vistrails\packages\sahm\SAHM\python\PARC.py"
        cmd = ([PARC_py] + arg_items + [self.getInputFromPort('templateLayer').name]
               + predictors)
        print cmd
        print "cmd type = ", type(cmd)
        for item in cmd:
            print item, type(item)
            
        cmdline = list2cmdline(cmd)
        print cmdline
        
        result = os.system(cmdline)
        if result != 0:
            raise ModuleError(self, "Execution failed")


