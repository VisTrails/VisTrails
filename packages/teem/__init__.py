"""Teem package for VisTrails.
"""

import core.modules
import core.modules.module_registry
import core.modules.basic_modules
from core.modules.vistrails_module import Module, ModuleError, \
     new_module, IncompleteImplementation

import os
import subprocess

_teemPath = None
_teemLimnTestPath = None
_teemTenTestPath = None

identifier = 'edu.utah.sci.cscheid.teem'
version = '0.1'
name = 'teem'

###############################################################################

class Teem(Module):

    def run_at_path(self, cmdline, path):
        cmdline = path + cmdline
        print cmdline
        result = os.system(cmdline)
        if result != 0:
            raise ModuleError(self, '"%s" failed' % cmdline)

    def run_path(self, *cmds):
        cmdline = " ".join([str(cmd) for cmd in cmds])
        self.run_at_path(cmdline, '')
        
    def run_teem(self, *cmds):
        cmdline = " ".join([str(cmd) for cmd in cmds])
        self.run_at_path(cmdline, _teemPath)

    def run_limn_test(self, *cmds):
        cmdline = " ".join([str(cmd) for cmd in cmds])
        self.run_at_path(cmdline, _teemLimnTestPath)

    def run_ten_test(self, *cmds):
        cmdline = " ".join([str(cmd) for cmd in cmds])
        self.run_at_path(cmdline, _teemTenTestPath)

    def opt_command_line_val(self, option_name, port_name):
        if self.hasInputFromPort(port_name):
            return [option_name, self.getInputFromPort(port_name)]
        else:
            return []

    def opt_command_line_vec(self, option_name, port_name):
        if self.hasInputFromPort(port_name):
            t = self.getInputFromPort(port_name)
            return [option_name] + list(t)
        else:
            return []

    def opt_command_line_file(self, option_name, port_name):
        if self.hasInputFromPort(port_name):
            t = self.getInputFromPort(port_name)
            return [option_name, t.name]
        else:
            return []

    def opt_command_line_noopt(self, option_name, port_name):
        if self.hasInputFromPort(port_name):
            return [option_name]
        else:
            return []

    ##########################################################################
    # Default compute for (hopefully) most classes

    _opt_dict = {'v': opt_command_line_val,
                 'V': opt_command_line_vec,
                 'f': opt_command_line_file,
                 'n': opt_command_line_noopt}

    def process_command_line_input(self):
        cmdline = [self._cmdline_base]
        for (opt_type, port_name, option_name) in self._cmdline_inputs:
            call = self._opt_dict[opt_type]
            cmdline += call(self, option_name=option_name,
                            port_name=port_name)
        return cmdline

    def process_command_line_output(self):
        (port_name, opt_name, format) = self._cmdline_output
        if callable(format):
            format = format(self)
        output_file = self.interpreter.filePool.create_file(suffix='.'+format)
        self.setResult(port_name, output_file)
        return [opt_name, output_file.name]

    def compute(self):
        cmdline_input = self.process_command_line_input()
        cmdline_output = self.process_command_line_output()
        self._cmdline_callable(*(cmdline_input + cmdline_output))

class Emap(Teem):

    def compute(self):
        cmdline = ['emap']
        cmdline += self.opt_command_line_vec(port_name='from',
                                             option_name='-fr')
        cmdline += self.opt_command_line_vec(port_name='ambient',
                                             option_name='-amb')
        cmdline += self.opt_command_line_vec(port_name='up',
                                             option_name='-up')
        cmdline += self.opt_command_line_noopt(port_name='right_hand',
                                               option_name='-rh')
        self.checkInputPort('input_file')
        cmdline += self.opt_command_line_file(port_name='input_file',
                                              option_name='-i')

        output_file = self.interpreter.filePool.create_file(suffix='.nrrd')
        cmdline += ['-o', output_file.name]
        
        self.run_teem(*cmdline)
        
        self.setResult("output_file", output_file)


class Soid(Teem):

    def compute(self):
        cmdline = ['soid']
        cmdline += self.opt_command_line_val(port_name='resolution',
                                                option_name='-res')
        cmdline += self.opt_command_line_val(port_name='radius',
                                                option_name='-r')
        cmdline += self.opt_command_line_vec(port_name='scalings',
                                             option_name='-sc')
        cmdline += self.opt_command_line_noopt(port_name='sphere',
                                               option_name='-sphere')

        if self.hasInputFromPort('AB'):
            cmdline += self.opt_command_line_vec(port_name='AB',
                                                 option_name='-AB')
        elif self.hasInputFromPort('A') and self.hasInputFromPort('B'):
            cmdline += ['-AB',
                        self.getInputFromPort('A'),
                        self.getInputFromPort('B')]

        output_file = self.interpreter.filePool.create_file(suffix='.nrrd')
        cmdline += ['-o', output_file.name]

        self.run_limn_test(*cmdline)
        self.setResult("output_file", output_file)


class OffToEps(Teem):

    def compute(self):
        cmdline = ['off2eps']
        cmdline += self.opt_command_line_vec(port_name='from_point',
                                             option_name='-fr')
        cmdline += self.opt_command_line_vec(port_name='u_range',
                                             option_name='-ur')
        cmdline += self.opt_command_line_vec(port_name='v_range',
                                             option_name='-vr')
        cmdline += self.opt_command_line_vec(port_name='edge_widths',
                                             option_name='-wd')
        cmdline += self.opt_command_line_file(port_name='environment_map',
                                              option_name='-e')
        cmdline += self.opt_command_line_noopt(port_name='orthogonal',
                                               option_name='-or')
        cmdline += self.opt_command_line_noopt(port_name='right_hand',
                                               option_name='-rh')
        cmdline += self.opt_command_line_noopt(port_name='concave',
                                               option_name='-concave')
        cmdline += self.opt_command_line_noopt(port_name='no_background',
                                               option_name='-nobg')
        cmdline += self.opt_command_line_val(port_name='world_to_points_scale',
                                             option_name='-ws')
        

        self.checkInputPort('input_file')
        input_file = self.getInputFromPort('input_file')
        cmdline += ['-i', input_file.name]

        output_file = self.interpreter.filePool.create_file(suffix='.eps')
        cmdline += ['-o', output_file.name]

        self.run_limn_test(*cmdline)
        self.setResult("output_file", output_file)


class EpsToPpm(Teem):

    def compute(self):
        cmdline = ['eps2ppm']
        self.checkInputPort('input_file')
        self.checkInputPort('resolution')
        cmdline += [self.getInputFromPort('input_file').name]
        cmdline += [self.getInputFromPort('resolution')]
        cmdline += ['>']
        output_file = self.interpreter.filePool.create_file(suffix='.ppm')
        cmdline += [output_file.name]
        self.run_path(*cmdline)
        self.setResult("output_file", output_file)


class Unu(Teem):

    def do_output(self):
        if self.hasInputFromPort('format'):
            suffix = '.'+self.getInputFromPort('format')
        else:
            suffix = '.nrrd'
        output_file = self.interpreter.filePool.create_file(suffix=suffix)
        return (['-o', output_file.name], output_file)

    def do_input(self):
        self.checkInputPort('input_file')
        return ['-i', self.getInputFromPort('input_file').name]

class UnuSave(Unu):
    def compute(self):
	cmdline = ['unu save']
	cmdline += self.do_input()
	(ocmd, output_file) = self.do_output()
	self.setResult("output_file", output_file)
	self.setResult("output_name", output_file.name)
	cmdline += ocmd
	cmdline += self.opt_command_line_val(port_name='output_format', option_name='-f')
	self.run_teem(*cmdline)

class UnuProject(Unu):

    def compute(self):
        cmdline = ['unu project']
        cmdline += self.do_input()
        (ocmd, output_file) = self.do_output()
        self.setResult("output_file", output_file)
        cmdline += ocmd
        cmdline += self.opt_command_line_val(port_name='axis',
                                             option_name='-a')
        cmdline += self.opt_command_line_val(port_name='measure',
                                             option_name='-m')
        self.run_teem(*cmdline)


class UnuResample(Unu):

    def compute(self):
        cmdline = ['unu resample']
        cmdline += self.do_input()
        (ocmd, output_file) = self.do_output()
        cmdline += ocmd
        self.setResult("output_file", output_file)
        cmdline += self.opt_command_line_val(port_name='sampling_spec',
                                             option_name='-s')
        cmdline += self.opt_command_line_val(port_name='kernel',
                                             option_name='-k')
        self.run_teem(*cmdline)


class UnuJoin(Unu):

    def do_input(self):
        self.checkInputPort('input_list')
        return ['-i'] + [x.name
                         for x in self.getInputFromPort('input_list')]

    def compute(self):
        cmdline = ['unu join']
        cmdline += self.do_input()
        cmdline += self.opt_command_line_val(port_name='axis',
                                             option_name='-a')
        (ocmd, output_file) = self.do_output()
        cmdline += ocmd
        self.setResult("output_file", output_file)
        self.run_teem(*cmdline)


class Unu1op(Unu):

    def do_input(self):
        r = []
        if self.hasInputFromPort('in1_file'):
            r += ['-i', self.getInputFromPort('in1_file').name]
        return r

    def is_cacheable(self):
        return not self.getInputFromPort('op') in ['rand', 'nrand']

    def compute(self):
        allowed_ops = ['-', 'r', 'sin',
                       'cos', 'tan', 'asin', 'acos', 'atan',
                       'exp', 'log', 'log10', 'log1p', 'log2', 'sqrt'
                       'cbrt', 'ceil', 'floor', 'erf', 'rup',
                       'abs', 'sgn', 'exists', 'rand', 'nrand',
                       'if', '0', '1']
        self.checkInputPort('op')
        if not self.getInputFromPort('op') in allowed_ops:
            raise ModuleError(self, ("Operation %s is not allowed." % 
                                     self.getInputFromPort('op')))
        cmdline = ['unu 1op']
        cmdline += [self.getInputFromPort('op')]
        cmdline += self.do_input()
        (ocmd, output_file) = self.do_output()
        cmdline += ocmd
        self.setResult('output_file', output_file)
        self.run_teem(*cmdline)


class Unu2op(Unu):

    def do_input(self):
        r = []
        if self.hasInputFromPort('in1_file'):
            r += [self.getInputFromPort('in1_file').name]
        elif self.hasInputFromPort('in1_value'):
            r += [self.getInputFromPort('in1_value')]
        else:
            raise ModuleError(self, "Needs either in1_file or in1_value")
        if self.hasInputFromPort('in2_file'):
            r += [self.getInputFromPort('in2_file').name]
        elif self.hasInputFromPort('in2_value'):
            r += [self.getInputFromPort('in2_value')]
        else:
            raise ModuleError(self, "Needs either in2_file or in2_value")
        return r

    def compute(self):
        allowed_ops = ['+', '-', 'x', '/',
                       '^', 'spow', '%', 'fmod', 'atan2',
                       'min', 'max', 'lt', 'lte', 'gt', 'gte'
                       'eq', 'neq', 'comp', 'if', 'exists']
        self.checkInputPort('op')
        if not self.getInputFromPort('op') in allowed_ops:
            raise ModuleError(self, ("Operation %s is not allowed." % 
                                     self.getInputFromPort('op')))
        cmdline = ['unu 2op']
        cmdline += [self.getInputFromPort('op')]
        cmdline += self.do_input()
        (ocmd, output_file) = self.do_output()
        cmdline += ocmd
        self.setResult('output_file', output_file)
        self.run_teem(*cmdline)


class Unu3op(Unu):

    def do_input(self):
        r = []
        if self.hasInputFromPort('in1_file'):
            r += [self.getInputFromPort('in1_file').name]
        elif self.hasInputFromPort('in1_value'):
            r += [self.getInputFromPort('in1_value')]
        else:
            raise ModuleError(self, "Needs either in1_file or in1_value")
        if self.hasInputFromPort('in2_file'):
            r += [self.getInputFromPort('in2_file').name]
        elif self.hasInputFromPort('in2_value'):
            r += [self.getInputFromPort('in2_value')]
        else:
            raise ModuleError(self, "Needs either in2_file or in2_value")
        if self.hasInputFromPort('in3_file'):
            r += [self.getInputFromPort('in3_file').name]
        elif self.hasInputFromPort('in3_value'):
            r += [self.getInputFromPort('in3_value')]
        else:
            raise ModuleError(self, "Needs either in3_file or in3_value")
        return r

    def compute(self):
        allowed_ops = ['+', 'x',
                       'min', 'max',
                       'clamp', 'ifelse',
                       'lerp', 'exists',
                       'in_op', 'in_cl']
        self.checkInputPort('op')
        if not self.getInputFromPort('op') in allowed_ops:
            raise ModuleError(self, ("Operation %s is not allowed." % 
                                     self.getInputFromPort('op')))
        cmdline = ['unu 3op']
        cmdline += [self.getInputFromPort('op')]
        cmdline += self.do_input()
        (ocmd, output_file) = self.do_output()
        cmdline += ocmd
        self.setResult('output_file', output_file)
        self.run_teem(*cmdline)

class Teem_TT(Teem):
    _cmdline_base = 'tt'
    _cmdline_inputs = [('v', 'num_samples', '-n'),
                       ('V', 'location', '-p'),
                       ('v', 'max_ca', '-ca'),
                       ('n', 'right_triangle', '-r'),
                       ('n', 'whole', '-w'),
                       ('v', 'westin_metric', '-v'),
                       ('v', 'hack', '-hack')]
    _cmdline_output = ('output_file', '-o', '.nrrd')
    _cmdline_callable = Teem.run_ten_test


class Tend_norm(Teem):
    _cmdline_base = 'tend norm'
    _cmdline_inputs = [('V', 'weights', '-w'),
                       ('v', 'amount', '-a'),
                       ('v', 'target', '-t'),
                       ('f', 'input_file', '-i')]
    _cmdline_output = ('output_file', '-o', 'nrrd')
    _cmdline_callable = Teem.run_teem

class Tend_glyph(Teem):
    _cmdline_base = 'tend glyph'
    _cmdline_inputs = [('v', 'sat', '-sat'),
                       ('f', 'emap', '-emap'),
                       ('f', 'input_file', '-i'),
                       ('V', 'from_point', '-fr'),
                       ('V', 'up', '-up'),
                       ('v', 'psc', '-psc'),
                       ('V', 'u_range', '-ur'),
                       ('V', 'v_range', '-vr'),
                       ('n', 'orthogonal', '-or'),
                       ('v', 'atr', '-atr'),
                       ('n', 'no_background', '-nobg'),
                       ('n', 'right_hand', '-rh'),
                       ('v', 'glyph_shape', '-g'),
                       ('v', 'glyph_size', '-gsc'),
                       ('v', 'glyph_resolution', '-gr'),
                       ('V', 'widths', '-wd')]
    _cmdline_output = ('output_file', '-o', 'eps')
    _cmdline_callable = Teem.run_teem
 
###############################################################################

def initialize(path=None, limnTestPath=None, tenTestPath=None,
               *args, **keywords):
    global _teemPath
    if not path:
        print "path not specified or incorrect: Will assume teem is on path"
        _teemPath = ""
    else:
        print "will use teem from ", path
        _teemPath = path + '/'

    global _teemLimnTestPath
    if not limnTestPath:
        print "limnTestPath not specified or incorrect: Will not install",
        print "limnTest modules"
        _teemLimnTestPath = ""
    else:
        print "will use limnTest tools from ", limnTestPath
        _teemLimnTestPath = limnTestPath + '/'

    global _teemTenTestPath
    if not tenTestPath:
        print "tenTestPath not specified or incorrect: Will not install",
        print "tenTestPath modules"
        _teemTenTestPath = ""
    else:
        print "will use tenTest tools from ", tenTestPath
        _teemTenTestPath = tenTestPath + '/'

    reg = core.modules.module_registry
    basic = core.modules.basic_modules
    reg.add_module(Teem)
    reg.add_module(Unu)
    reg.add_input_port(Unu, "format",
                     (basic.String, 'file format for output'))
    reg.add_output_port(Unu, "output_file",
                      (basic.File, 'the output file'))
    
    reg.add_module(Emap)
    reg.add_input_port(Emap, "right_hand", [])
    reg.add_input_port(Emap, "input_file",
                     (basic.File, 'the lights input file'))
    reg.add_input_port(Emap, "from", [(basic.Float, 'x'),
                                    (basic.Float, 'y'),
                                    (basic.Float, 'z')])
    reg.add_input_port(Emap, "ambient", [(basic.Float, 'x'),
                                       (basic.Float, 'y'),
                                       (basic.Float, 'z')])
    reg.add_input_port(Emap, "up", [(basic.Float, 'x'),
                                  (basic.Float, 'y'),
                                  (basic.Float, 'z')])
    reg.add_output_port(Emap, "output_file",
                      (basic.File, 'the resulting nrrd'))

    reg.add_module(Soid)
    reg.add_input_port(Soid, "resolution",
                     (basic.Float, 'The ellipsoid resolution'))
    reg.add_input_port(Soid, "radius", (basic.Float, 'The radius'))
    reg.add_input_port(Soid, "sphere", [])
    reg.add_input_port(Soid, "scalings", [(basic.Float, 'x scaling'),
                                        (basic.Float, 'y scaling'),
                                        (basic.Float, 'z scaling')])
    reg.add_input_port(Soid, "AB", [(basic.Float, 'A exponent'),
                                  (basic.Float, 'B exponent')])
    reg.add_input_port(Soid, "A", (basic.Float, 'A exponent'))
    reg.add_input_port(Soid, "B", (basic.Float, 'B exponent'))
    reg.add_output_port(Soid, "output_file",
                      (basic.File, 'the resulting OFF file'))

    reg.add_module(OffToEps)
    reg.add_input_port(OffToEps, "right_hand", [])
    reg.add_input_port(OffToEps, "input_file",
                     (basic.File, 'the input OFF file'))
    reg.add_input_port(OffToEps, "environment_map",
                     (basic.File, 'the nrrd storing the environment map'))
    reg.add_input_port(OffToEps, "from_point", [(basic.Float, '')] * 3)
    reg.add_input_port(OffToEps, "u_range", [(basic.Float, '')] * 2)
    reg.add_input_port(OffToEps, "v_range", [(basic.Float, '')] * 2)
    reg.add_input_port(OffToEps, "edge_widths", [(basic.Float, '')] * 5)
    reg.add_input_port(OffToEps, "orthogonal", [])
    reg.add_input_port(OffToEps, "no_background", [])
    reg.add_input_port(OffToEps, "concave", [])
    reg.add_input_port(OffToEps, "world_to_points_scale", (basic.Float, ''))
    reg.add_output_port(OffToEps, "output_file", (basic.File, ''))

    reg.add_module(EpsToPpm)
    reg.add_input_port(EpsToPpm, "input_file", (basic.File, 'the input EPS'))
    reg.add_input_port(EpsToPpm, "resolution",
                     (basic.Float, 'the resolution to rasterize the EPS'))
    reg.add_output_port(EpsToPpm, "output_file",
                      (basic.File, 'the resulting PPM file'))

    reg.add_module(UnuSave)
    reg.add_input_port(UnuSave, "input_file", (basic.File, 'Input File'))
    reg.add_input_port(UnuSave, "output_format", (basic.String, 'Output Format'))
    reg.add_output_port(UnuSave, "output_name", (basic.String, 'Output Filename'))

    reg.add_module(UnuProject)
    reg.add_input_port(UnuProject, "input_file", (basic.File, 'the input file'))
    reg.add_input_port(UnuProject, "measure",
                     (basic.String, 'the measure to use'))
    reg.add_input_port(UnuProject, "axis",
                     (basic.Integer, 'the axis to project'))

    reg.add_module(UnuResample)
    reg.add_input_port(UnuResample, "input_file", (basic.File, 'the input file'))
    reg.add_input_port(UnuResample, "sampling_spec", (basic.String, 'the sampling spec'))
    reg.add_input_port(UnuResample, "kernel", (basic.String, 'the resampling kernel'))

    reg.add_module(UnuJoin)
    reg.add_input_port(UnuJoin, "input_list", (basic.List, 'list of input files'))
    reg.add_input_port(UnuJoin, "axis", (basic.Integer, 'the axis to join'))

    reg.add_module(Unu1op)
    reg.add_input_port(Unu1op, "in1_file", (basic.File, 'input file 1'))
    reg.add_input_port(Unu1op, "op", (basic.String, 'the operation'))

    reg.add_module(Unu2op)
    reg.add_input_port(Unu2op, "in1_file", (basic.File, 'input file 1'))
    reg.add_input_port(Unu2op, "in1_value", (basic.String, 'input value 1'))
    reg.add_input_port(Unu2op, "in2_file", (basic.File, 'input file 2'))
    reg.add_input_port(Unu2op, "in2_value", (basic.String, 'input value 2'))
    reg.add_input_port(Unu2op, "op", (basic.String, 'the operation'))

    reg.add_module(Unu3op)
    reg.add_input_port(Unu3op, "in1_file", (basic.File, 'input file 1'))
    reg.add_input_port(Unu3op, "in1_value", (basic.String, 'input value 1'))
    reg.add_input_port(Unu3op, "in2_file", (basic.File, 'input file 2'))
    reg.add_input_port(Unu3op, "in2_value", (basic.String, 'input value 2'))
    reg.add_input_port(Unu3op, "in3_file", (basic.File, 'input file 3'))
    reg.add_input_port(Unu3op, "in3_value", (basic.String, 'input value 3'))
    reg.add_input_port(Unu3op, "op", (basic.String, 'the operation'))


    reg.add_module(Teem_TT)
    reg.add_input_port(Teem_TT, "num_samples", (basic.String, 'number of samples'))
    reg.add_input_port(Teem_TT, "location", [(basic.Float, 'u'),
                                           (basic.Float, 'v'),
                                           (basic.Float, 'w')])
    reg.add_input_port(Teem_TT, "max_ca", (basic.Float, 'max CA'))
    reg.add_input_port(Teem_TT, "westin_metric", (basic.Float, 'Metric to use'))
    reg.add_input_port(Teem_TT, "hack", (basic.Float, '"this is a hack"'))
    reg.add_input_port(Teem_TT, "right_triangle", [])
    reg.add_input_port(Teem_TT, "whole", [])
    reg.add_output_port(Teem_TT, "output_file", (basic.File, "the output file"))

    reg.add_module(Tend_norm)
    reg.add_input_port(Tend_norm, "weights", [(basic.Float, 'w0'),
                                            (basic.Float, 'w1'),
                                            (basic.Float, 'w2')])
    reg.add_input_port(Tend_norm, "amount", (basic.Float,
                                           "amount of normalization"))
    reg.add_input_port(Tend_norm, "target", (basic.Float,
                                           "target size post normalization"))
    reg.add_input_port(Tend_norm, "input_file", (basic.File,
                                               "input DT volume"))
    reg.add_output_port(Tend_norm, "output_file", (basic.File,
                                                 "output file"))

    reg.add_module(Tend_glyph)
    reg.add_input_port(Tend_glyph, "sat", (basic.Float, "max saturation"))
    reg.add_input_port(Tend_glyph, "from_point", [(basic.Float, '')] * 3)
    reg.add_input_port(Tend_glyph, "up", [(basic.Float, '')] * 3)
    reg.add_input_port(Tend_glyph, "psc", [(basic.Float, 'ps scale')])
    reg.add_input_port(Tend_glyph, "u_range", [(basic.Float, '')] * 2)
    reg.add_input_port(Tend_glyph, "v_range", [(basic.Float, '')] * 2)
    reg.add_input_port(Tend_glyph, "orthogonal", [])
    reg.add_input_port(Tend_glyph, "atr", [(basic.Float,
                                          'anisotropy threshold')])
    reg.add_input_port(Tend_glyph, "emap", [(basic.File,
                                           'environment map nrrd')])
    reg.add_input_port(Tend_glyph, "input_file", [(basic.File,
                                                 'the input file')])
    reg.add_input_port(Tend_glyph, "no_background", [])
    reg.add_input_port(Tend_glyph, "glyph_shape", [(basic.String,
                                                  'glyph shape')])
    reg.add_input_port(Tend_glyph, "glyph_size",
                     [(basic.Float, 'glyph size in world space')])
    reg.add_input_port(Tend_glyph, "glyph_resolution",
                     [(basic.Integer, 'glyph resolution of polygonization')])
    reg.add_input_port(Tend_glyph, "widths", [(basic.Float, '')] * 3)
    reg.add_input_port(Tend_glyph, "right_hand", [])
    reg.add_output_port(Tend_glyph, "output_file",
                      [(basic.File, 'output EPS file')])

