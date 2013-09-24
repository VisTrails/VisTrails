# VisTrails package for metro support
# Copyright Carlos Eduardo Scheidegger, 2007
# Get metro at http://vcg.sourceforge.net/

# License: GPLv2 or later

# ChangeLog:

# 2007-03-13  Carlos Scheidegger  <cscheid@juggernaut>
# 	* First release
##############################################################################

import core.modules
import core.modules.module_registry
from core.modules.vistrails_module import Module, ModuleError
import core.bundles
from core.system import list2cmdline
import core.requirements
import os
import re

try:
    from core.configuration import ConfigurationObject
    global configuration
    configuration = ConfigurationObject(executable_path=(None, str))
    old_vistrails = False
except ImportError:
    old_vistrails = True

identifier = 'edu.utah.sci.cscheid.metro'
version = '0.1'
name = 'metro'

################################################################################

def get_path():
    global _metro_path
    if old_vistrails:
        return _metro_path
    if configuration.has('executable_path'):
        p = configuration.executable_path + '/'
    else:
        p = ''
    p += 'metro'
    return p

class Metro(Module):

    def __init__(self):
        Module.__init__(self)
        self.need_error_meshes = False
        self.need_histograms = False

    def is_cacheable(self):
        return self.need_error_meshes and self.need_histograms

    def compute(self):
        self.checkInputPort('mesh1')
        self.checkInputPort('mesh2')
        f1 = self.get_input('mesh1')
        f2 = self.get_input('mesh2')

        make_file = self.interpreter.filePool.create_file

        metro_output = make_file(suffix='.txt')

        values = [get_path(), f1.name, f2.name, '-q']

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

        values.append('>')
        values.append(metro_output.name)
        
        cmdline = list2cmdline(values)

#         cmdline = ('%s ' * len(values)) % tuple(values)
#         cmdline += '> '
#         cmdline += metro_output.name
        print cmdline
        
        result = os.system(cmdline)
        if result != 0:
            raise ModuleError(self, "Execution failed")
        l = [x for x in file(metro_output.name).readlines()
             if x.startswith('Hausdorff')][0]
        regexp = re.compile(r'Hausdorff distance: ([0123456789.]+) \(([0123456789.]+)  wrt bounding box diagonal\)')
        results = regexp.match(l).groups()
        
        if need_error_meshes:
            self.set_output('error_mesh_1', error_mesh_output[0])
            self.set_output('error_mesh_2', error_mesh_output[1])

        if need_histograms:
            self.set_output('error_hist_1', error_hist_output[0])
            self.set_output('error_hist_2', error_hist_output[1])

        self.need_error_meshes = need_error_meshes
        self.need_histograms = need_histograms

        self.set_output('hausdorff_error', float(results[0]))
        self.set_output('normalized_hausdorff_error', float(results[1]))

################################################################################

def initialize(executable_path=None):
    if old_vistrails:
        global _metro_path
        if (core.requirements.executable_file_exists('metro') or
            core.bundles.install({'linux-ubuntu': 'vcg-metro'})):
            _metro_path = 'metro'
        elif executable_path:
            _metro_path = executable_path + '/metro'
            print "Will assume metro is in ",executable_path
        else:
            raise core.requirements.MissingRequirement("VCG's Metro")
    else:
        if (not core.requirements.executable_file_exists('metro') and
            not core.bundles.install({'linux-ubuntu': 'vcg-metro'})):
            raise core.requirements.MissingRequirement("VCG's Metro")
    
    reg = core.modules.module_registry

    reg.add_module(Metro)
    reg.add_input_port(Metro, 'mesh1',
                       core.modules.basic_modules.File)
    reg.add_input_port(Metro, 'mesh2',
                       core.modules.basic_modules.File)

    reg.add_output_port(Metro, 'hausdorff_error',
                        core.modules.basic_modules.Float)
    reg.add_output_port(Metro, 'normalized_hausdorff_error',
                        core.modules.basic_modules.Float)
    reg.add_output_port(Metro, 'error_mesh_1',
                        core.modules.basic_modules.File)
    reg.add_output_port(Metro, 'error_mesh_2',
                        core.modules.basic_modules.File)
    reg.add_output_port(Metro, 'error_hist_1',
                        core.modules.basic_modules.File)
    reg.add_output_port(Metro, 'error_hist_2',
                        core.modules.basic_modules.File)
