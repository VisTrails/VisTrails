import core.modules
import core.modules.module_registry
from core.modules.vistrails_module import Module, ModuleError
import core.bundles
import core.requirements
import os
import re

from core.configuration import ConfigurationObject

configuration = ConfigurationObject(executable_path=(None, str))

identifier = 'edu.utah.sci.cscheid.poissonrecon'
version = '0.1'
name = 'Poisson Surface Reconstruction'

##############################################################################

class PoissonRecon(Module):

    def __init__(self):
        Module.__init__(self)

    def compute(self):
        self.checkInputPort('pts')
        f1 = self.getInputFromPort('mesh1')

        make_file = self.interpreter.filePool.create_file

        metro_output = make_file(suffix='.ply')

        values = ['', f1.name, f2.name, '-q']

        need_error_meshes = False
        if (self.outputPorts.has_key('error_mesh_1') or
            self.outputPorts.has_key('error_mesh_2')):
            need_error_meshes = True
            error_mesh_output = (make_file(suffix='.ply'),
                                 make_file(suffix='.ply'))
            values.append('-c')
            values.append(error_mesh_output[0].name)
            values.append(error_mesh_output[1].name)

        need_histograms = False
        if (self.outputPorts.has_key('error_hist_1') or
            self.outputPorts.has_key('error_hist_2')):
            need_histograms = True
            error_hist_output = (make_file(suffix='.csv'),
                                 make_file(suffix='.csv'))
            values.append('-h')
            values.append(error_hist_output[0].name)
            values.append(error_hist_output[1].name)

        print values
        print ('%s ' * len(values))
        cmdline = ('%s ' * len(values)) % tuple(values)
        cmdline += '> '
        cmdline += metro_output.name
        print cmdline
        
        result = os.system(cmdline)
        if result != 0:
            raise ModuleError(self, "Execution failed")
        l = [x for x in file(metro_output.name).readlines()
             if x.startswith('Hausdorff')][0]
        regexp = re.compile(r'Hausdorff distance: ([0123456789.]+) \(([0123456789.]+)  wrt bounding box diagonal\)')
        results = regexp.match(l).groups()
        
        if need_error_meshes:
            self.setResult('error_mesh_1', error_mesh_output[0])
            self.setResult('error_mesh_2', error_mesh_output[1])

        if need_histograms:
            self.setResult('error_hist_1', error_hist_output[0])
            self.setResult('error_hist_2', error_hist_output[1])

        self.need_error_meshes = need_error_meshes
        self.need_histograms = need_histograms

        self.setResult('hausdorff_error', float(results[0]))
        self.setResult('normalized_hausdorff_error', float(results[1]))

##############################################################################

def initialize():
    if not core.requirements.executable_file_exists('PoissonRecon'):
        raise core.requirements.MissingRequirement("PoissonRecon")
    
    reg = core.modules.module_registry

    reg.add_module(PoissonRecon)
    reg.add_input_port(PoissonRecon, 'pts',
                       core.modules.basic_modules.File)
    reg.add_input_port(PoissonRecon, 'binary',
                       core.modules.basic_modules.Boolean)
    reg.add_input_port(PoissonRecon, 'depth',
                       core.modules.basic_modules.Integer)

    reg.add_output_port(PoissonRecon, 'output',
                        core.modules.basic_modules.File)

