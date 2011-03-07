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

#from PARC import PARC as PARC_
#import PARC

import itertools
import os

from utils import map_ports, path_value, create_file_module, create_dir_module
from utils import create_dir_module, mktempfile, mktempdir

print ("*"*60 + "\n")*2 + ("*"*60)
print ("*"*60 + "\n")*2 + ("*"*60)
print ("*"*60 + "\n")*2 + ("*"*60)
import packages.sahm.pySAHM as P2
print "RunParc", dir(P2)

#class PARC(Module):
#    '''
#    This class provides a widget to run the PARC module which
#    provides functionality to sync raster layer properties
#    with a template dataset
#    '''
#    configuration = []
#    _input_ports = [('predictor', "(gov.usgs.sahm:Predictor:DataInput)"),
#                                ('PredictorList', '(gov.usgs.sahm:PredictorList:DataInput)'),
#                                ('templateLayer', '(gov.usgs.sahm:TemplateLayer:DataInput)'),
#                                ('resampleMethod', '(edu.utah.sci.vistrails.basic:String)'),
#                                ('aggregationMethod', '(edu.utah.sci.vistrails.basic:String)')]
#
#    _output_ports = [('PredictorLayersDir', '(edu.utah.sci.vistrails.basic:Directory)')]
#
#    def compute(self):
#        port_map = {'method': ('-m',  None, False),
#                    'resampleMethod': ('-r', None, False)}
#        args = map_ports(self, port_map)
#
#        output_dname = mktempdir(prefix='parc')
#        args['-o'] = output_dname
#
#        print args, type(args)
#        arg_items = []
#        for k,v in args.items():
#            arg_items.append(k)
#            arg_items.append(v)
#
#        for item in arg_items:
#            print item
#
#        predictor_list = self.forceGetInputFromPort('PredictorList', [])
#        predictor_list.extend(self.forceGetInputListFromPort('predictor'))
#
#        predictors = []
#        for predictor in predictor_list:
#            predictors.append(os.path.join(predictor.name))
#
#        args = (arg_items + [self.getInputFromPort('templateLayer').name]
#               + predictors)
#        ourPARCer = PARC_.PARC()
#        ourPARCer.main(args)
#
##        #FixMe replace path here with relative path configuration.sahm_path
##        #PARC_py = os.path.join(configuration.sahm_path,"python", "PARC.py")
##
##        from init import configuration
##        PARC_py = configuration.sahm_path + r"/python/PARC.py"
##
##        cmd = ([PARC_py] + arg_items + [self.getInputFromPort('templateLayer').name]
##               + predictors)
##        print cmd
##        print "cmd type = ", type(cmd)
##        for item in cmd:
##            print item, type(item)
##
##        cmdline = list2cmdline(cmd)
##        print cmdline
##
##        result = os.system(cmdline)
##        if result != 0:
##            raise ModuleError(self, "Execution failed")
##
##        output_dir = create_dir_module(args["-o"])
#        self.setResult('PredictorLayersDir', output_dname)

#if __name__ == "__main__":

#    parc = PARC()
#    parc.aggMethod = "Max"
#    parc.resMethod = "Near"
#    parc.verbose = True
#
#    print "about to Parc"
#    #print self.forceGetInputFromPort('templateLayer').name, predictors, self.forceGetInputFromPort('outputDir').name
#    parc.parcFiles(r"I:\VisTrails\WorkingFiles\TrialData\gsenm_400m_eucl_dist_streams.tif", ["I:\\Maxent_Daymet_WGS84\\UnitedStates\\tiff2\\Bio2.tif"], r"I:\VisTrails\WorkingFiles\TrialData\trialOutput2")
