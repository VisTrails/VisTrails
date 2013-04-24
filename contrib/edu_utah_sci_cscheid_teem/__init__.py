"""Teem package for VisTrails.
"""

##############################################################################
# Changes
#
# 20081002: Added UnuSlice

import core.modules
import core.modules.module_registry
import core.modules.basic_modules as basic
from core.modules.vistrails_module import Module, ModuleError, \
     new_module, IncompleteImplementation

import os
import subprocess

_teemPath = None
_teemLimnTestPath = None
_teemTenTestPath = None

identifier = 'edu.utah.sci.cscheid.teem'
version = '0.2'
name = 'teem'

###############################################################################

FileType = [(basic.File, '')]
FloatType = [(basic.Float, '')]
IntegerType = [(basic.Integer, '')]
StringType = [(basic.String, '')]
Vec3Type = [(basic.Float, 'x'),
            (basic.Float, 'y'),
            (basic.Float, 'z')]

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

    _input_ports = [('right_hand', []),
                    ('input_file', [(basic.File, 'the lights input file')]),
                    ('from', Vec3Type),
                    ('ambient', Vec3Type),
                    ('up', Vec3Type)]
    _output_ports = [('output_file', [(basic.File, 'the resulting nrrd')])]

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

    _input_ports = [('resolution', [(basic.Float, 'The ellipsoid resolution')]),
                    ('radius', [(basic.Float, 'The radius')]),
                    ('sphere', []),
                    ('scalings', Vec3Type),
                    ('AB', [(basic.Float, 'A exponent'),
                            (basic.Float, 'B exponent')]),
                    ('A', [(basic.Float, 'A exponent')]),
                    ('B', [(basic.Float, 'B exponent')]),
                    ]
    _output_ports = [('output_file', [(basic.File, 'the resulting OFF file')])]


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


    _input_ports = [
        ("right_hand", []),
        ("input_file", [(basic.File, 'the input OFF file')]),
        ("environment_map", [(basic.File, 'the nrrd storing the environment map')]),
        ("from_point", [(basic.Float, '')] * 3),
        ("u_range", [(basic.Float, '')] * 2),
        ("v_range", [(basic.Float, '')] * 2),
        ("edge_widths", [(basic.Float, '')] * 5),
        ("orthogonal", []),
        ("no_background", []),
        ("concave", []),
        ("world_to_points_scale", [(basic.Float, '')]),
        ]

    _output_ports = [
        ("output_file", [(basic.File, '')]),
        ]

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

    _input_ports = [
        ("input_file", [(basic.File, 'the input EPS')]),
        ("resolution", [(basic.Float, 'the resolution to rasterize the EPS')]),
        ]

    _output_ports = [
        ("output_file", [(basic.File, 'the resulting PPM file')]),
        ]
    
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

    _input_ports = [
        ("format", [(basic.String, 'file format for output')]),
        ]
    _output_ports = [
        ("output_file", [(basic.File, 'the output file')]),
        ]

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
        
    _input_ports = [
        ("input_file", [(basic.File, 'Input File')]),
        ("output_format", [(basic.String, 'Output Format')]),
        ]
    _output_ports = [
        ("output_name", [(basic.String, 'Output Filename')]),
        ]

class UnuSwap(Unu):

    def compute(self):
        cmdline = ['unu swap']
        cmdline += self.do_input()
        (ocmd, output_file) = self.do_output()
        self.setResult("output_file", output_file)
        v1, v2 = self.getInputFromPort('axes')
        cmdline += ['-a', str(v1), str(v2)]
        cmdline += ocmd
        self.run_teem(*cmdline)

    _input_ports = [
        ("input_file", [(basic.File, 'Input File')]),
        ("axes", [(basic.Integer, '')]*2),
        ]

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

    _input_ports = [
        ("input_file", [(basic.File, 'the input file')]),
        ("measure", [(basic.String, 'the measure to use')]),
        ("axis", (basic.Integer, 'the axis to project')),
        ]

class UnuMinmax(Teem):

    def do_input(self):
        self.checkInputPort('input_file')
        return [self.getInputFromPort('input_file').name]

    def compute(self):
        cmdline = ['unu minmax']
        cmdline += self.do_input()
        if self.hasInputFromPort('blind8'):
            cmdline += '-blind8 true'
        output_file = self.interpreter.filePool.create_file()
        # FIXME use popen*
        cmdline += ['>%s'%output_file.name]
        self.run_teem(*cmdline)
        f = file(output_file.name)
        try:
            mn = float(f.readline().split()[-1])
            mx = float(f.readline().split()[-1])
        except:
            raise ModuleError(self, 'Could not read result')
        self.setResult('range', (mn, mx))

    _input_ports = [('input_file', [(basic.File, 'the input file')]),
                    ('blind8', [])]
    _output_ports = [('range', [(basic.Float,'')] * 2)]

class UnuReshape(Unu):

    def compute(self):
        cmdline = ['unu reshape']
        cmdline += self.do_input()
        cmdline += self.opt_command_line_val(port_name='axes',
                                             option_name='-s')
        (ocmd, output_file) = self.do_output()
        self.setResult("output_file", output_file)
        cmdline += ocmd
        self.run_teem(*cmdline)

    _input_ports = [
        ("input_file", [(basic.File, 'the input file')]),
        ("axes", [(basic.String, 'axes to split')]),
        ]
    

class UnuResample(Unu):

    def compute(self):
        cmdline = ['unu resample']
        cmdline += self.do_input()
        (ocmd, output_file) = self.do_output()
        cmdline += ocmd
        self.setResult("output_file", output_file)
        cmdline += self.opt_command_line_val(port_name='sampling_spec',
                                             option_name='-s')
        cmdline += self.opt_command_line_val(port_name='centering',
                                             option_name='-c')
        cmdline += self.opt_command_line_val(port_name='kernel',
                                             option_name='-k')
        self.run_teem(*cmdline)

    _input_ports = [
        ("input_file", [(basic.File, 'the input file')]),
        ("sampling_spec", [(basic.String, 'the sampling spec')]),
        ("centering", [(basic.String, 'centering (node/cell)')]),
        ("kernel", [(basic.String, 'the resampling kernel')]),
        ]

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

    _input_ports = [
        ("input_list", [(basic.List, 'list of input files')]),
        ("axis", [(basic.Integer, 'the axis to join')]),
        ]
    
class UnuQuantize(Unu):

    def do_input(self):
        current = Unu.do_input(self)
        self.checkInputPort('bits')
        return current + ['-b', self.getInputFromPort('bits')]

    def compute(self):
        cmdline = ['unu quantize']
        cmdline += self.do_input()
        cmdline += self.opt_command_line_val(port_name='min',
                                             option_name='-min')
        cmdline += self.opt_command_line_val(port_name='max',
                                             option_name='-max')
        (ocmd, output_file) = self.do_output()
        cmdline += ocmd
        self.setResult("output_file", output_file)
        self.run_teem(*cmdline)

    _input_ports = [
        ("input_file", [(basic.File, 'the input file')]),
        ('bits', [(basic.Integer, 'bits to quantize down to')]),
        ('min', [(basic.Float, 'min value')]),
        ('max', [(basic.Float, 'max value')]),
        ]
    
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

    _input_ports = [
        ("in1_file", [(basic.File, 'input file 1')]),
        ("op", [(basic.String, 'the operation')]),
        ]

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
                       '^', 'pow', 'spow', '%', 'fmod', 'atan2',
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

    _input_ports = [
        ("in1_file", [(basic.File, 'input file 1')]),
        ("in1_value", [(basic.String, 'input value 1')]),
        ("in2_file", [(basic.File, 'input file 2')]),
        ("in2_value", [(basic.String, 'input value 2')]),
        ("op", [(basic.String, 'the operation')]),
        ]


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

    _input_ports = [
        ("in1_file", [(basic.File, 'input file 1')]),
        ("in1_value", [(basic.String, 'input value 1')]),
        ("in2_file", [(basic.File, 'input file 2')]),
        ("in2_value", [(basic.String, 'input value 2')]),
        ("in3_file", [(basic.File, 'input file 3')]),
        ("in3_value", [(basic.String, 'input value 3')]),
        ("op", [(basic.String, 'the operation')]),
    ]
    
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

    _input_ports = [
        ("num_samples", [(basic.String, 'number of samples')]),
        ("location", Vec3Type),
        ("max_ca", [(basic.Float, 'max CA')]),
        ("westin_metric", [(basic.Float, 'Metric to use')]),
        ("hack", [(basic.Float, '"this is a hack"')]),
        ("right_triangle", []),
        ("whole", []),
        ]
    _output_ports = [
        ("output_file", [(basic.File, "the output file")]),
        ]

class Tend_norm(Teem):
    _cmdline_base = 'tend norm'
    _cmdline_inputs = [('V', 'weights', '-w'),
                       ('v', 'amount', '-a'),
                       ('v', 'target', '-t'),
                       ('f', 'input_file', '-i')]
    _cmdline_output = ('output_file', '-o', 'nrrd')
    _cmdline_callable = Teem.run_teem

    _input_ports = [
        ("weights", Vec3Type),
        ("amount", [(basic.Float, "amount of normalization")]),
        ("target", [(basic.Float, "target size post normalization")]),
        ("input_file", [(basic.File, "input DT volume")]),
        ]

    _output_ports = [
        ("output_file", [(basic.File, "output file")]),
        ]

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

    _input_ports = [
        ("sat", [(basic.Float, "max saturation")]),
        ("from_point", [(basic.Float, '')] * 3),
        ("up", [(basic.Float, '')] * 3),
        ("psc", [(basic.Float, 'ps scale')]),
        ("u_range", [(basic.Float, '')] * 2),
        ("v_range", [(basic.Float, '')] * 2),
        ("orthogonal", []),
        ("atr", [(basic.Float, 'anisotropy threshold')]),
        ("emap", [(basic.File, 'environment map nrrd')]),
        ("input_file", [(basic.File, 'the input file')]),
        ("no_background", []),
        ("glyph_shape", [(basic.String, 'glyph shape')]),
        ("glyph_size", [(basic.Float, 'glyph size in world space')]),
        ("glyph_resolution", [(basic.Integer, 'glyph resolution of polygonization')]),
        ("widths", [(basic.Float, '')] * 3),
        ("right_hand", []),
    ]
    _output_ports = [
        ("output_file", [(basic.File, 'output EPS file')])
        ]

class UnuSlice(Unu):

    def do_input(self):
        r = []
        self.checkInputPort('in_file')
        self.checkInputPort('axis')
        self.checkInputPort('position')
        r += ['-i', self.getInputFromPort('in_file').name]
        r += ['-a', str(self.getInputFromPort('axis'))]
        r += ['-p', str(self.getInputFromPort('position'))]
        return r

    def compute(self):
        cmdline = ['unu slice']
        cmdline += self.do_input()
        (ocmd, output_file) = self.do_output()
        cmdline += ocmd
        self.setResult('output_file', output_file)
        self.run_teem(*cmdline)

    _input_ports = [
        ('in_file', basic.File),
        ('axis', basic.Integer),
        ('position', basic.Integer),
        ]

    
###############################################################################

class TeemScaledTransferFunction(Teem):
    _input_ports = [('range', [(basic.Float, '')] * 2),
                    ('steps', [basic.Integer])]
    _output_ports = [('nrrd', [(basic.File, 'the output TF')])]

    def compute(self):
        ramp = self.interpreter.filePool.create_file(suffix='.txt')
        tf_vals = self.interpreter.filePool.create_file(suffix='.txt')
        output = self.interpreter.filePool.create_file(suffix='.nrrd')
        steps = self.getInputFromPort('steps')
        rng = self.getInputFromPort('range')
        self.run_teem('echo "0 1"',
                      '| unu reshape -s 1 2',
                      '| unu resample -s = %d -k tent -c node' % steps,
                      '| unu save -f text -o %s' % ramp.name)
        tf_file = file(tf_vals.name, 'w')
        tf = self.getInputFromPort('transfer_function')
        for (scalar, op, (r, g, b)) in tf._pts:
            tf_file.write('%f %f %f %f %f\n' % (scalar, r, g, b, op))
#             tf_file.write('%f %f\n' % (scalar, op))
        tf_file.close()
        self.run_teem('cat %s' % tf_vals.name,
                      '| unu reshape -s 5 %d' % len(tf._pts),
                      '| unu imap -i %s -r -m -' % ramp.name,
                      '| unu reshape -s 4 %d' % steps,
                      '| unu axinfo -a 0 -l "RGBA"',
                      '| unu axinfo -a 1 -l "gage(scalar:v)" -mm %f %f -o %s' % (rng[0],
                                                                                 rng[1],
                                                                                 output.name))
        self.setResult('nrrd', output)

##############################################################################

class Miter(Teem):

    _input_ports = [
        # Input data
        ('input_file', FileType),
        ('transfer_function', FileType),
        # Camera
        ('from_point', Vec3Type),
        ('at_point', Vec3Type),
        ('up_vec', Vec3Type),
        ('right_handed', []),
        ('relative_to_at_point', []),
        ('near_dist', FloatType),
        ('far_dist', FloatType),
        ('image_plane_dist', FloatType),
        ('urange', FloatType * 2),
        ('vrange', FloatType * 2),
        ('image_size', IntegerType * 2),
        # Lighting
        ('light_pos', Vec3Type),
        ('ambient_light', FloatType * 3),
        ('phong_components', FloatType * 3),
        ('shininess', FloatType),
        ('value_kernel', StringType),
        ('d_kernel', StringType),
        ('dd_kernel', StringType),
        ('step_size', FloatType),
        ('ref_step_size', FloatType),
        ('thread_count', IntegerType),
        ('opacity_termination', FloatType),
        ]

    _output_ports = [('output_file', FileType)]
    
    def compute(self):
        cmdline = ['miter']
        self.checkInputPort('input_file')
        self.checkInputPort('transfer_function')
        cmdline += self.opt_command_line_file('-i', 'input_file')
        f = self.interpreter.filePool.create_file(suffix='.nrrd')
        cmdline += ['-o', f.name]
        cmdline += self.opt_command_line_vec('-fr', 'from_point')
        cmdline += self.opt_command_line_vec('-at', 'at_point')
        cmdline += self.opt_command_line_vec('-up', 'up_vec')
        cmdline += self.opt_command_line_noopt('-rh', 'right_handed')
        cmdline += self.opt_command_line_noopt('-ar', 'relative_to_at_point')
        cmdline += self.opt_command_line_val('-dn', 'near_dist')
        cmdline += self.opt_command_line_val('-di', 'image_plane_dist')
        cmdline += self.opt_command_line_val('-df', 'far_dist')
        cmdline += self.opt_command_line_vec('-ur', 'urange')
        cmdline += self.opt_command_line_vec('-vr', 'vrange')
        cmdline += self.opt_command_line_vec('-is', 'image_size')
        cmdline += self.opt_command_line_vec('-ld', 'light_pos')
        cmdline += self.opt_command_line_vec('-am', 'ambient_light')
        cmdline += self.opt_command_line_vec('-ads', 'phong_components')
        cmdline += self.opt_command_line_val('-sp', 'shininess')
        cmdline += self.opt_command_line_val('-k00', 'value_kernel')
        cmdline += self.opt_command_line_val('-k11', 'd_kernel')
        cmdline += self.opt_command_line_val('-k22', 'dd_kernel')
        cmdline += self.opt_command_line_val('-step', 'step_size')
        cmdline += self.opt_command_line_val('-ref', 'ref_step_size')
        cmdline += self.opt_command_line_val('-nt', 'thread_count')
        cmdline += self.opt_command_line_val('-n1', 'opacity_termination')
        cmdline += self.opt_command_line_file('-txf', 'transfer_function')
        self.setResult('output_file', f) 
        self.run_teem(*cmdline)
        
###############################################################################

class OverRGB(Teem):

    _input_ports = [
        ('input_file', FileType),
        ('contrast', FloatType),
        ('component_fixed_point', FloatType),
        ('gamma', FloatType),
        ('background', Vec3Type),
        ('background_image', FileType),]

    _output_ports = [
        ('output_image', FileType),
        ]

    def compute(self):
        cmdline = ['overrgb']
        self.checkInputPort('input_file')
        cmdline += self.opt_command_line_file('-i', 'input_file')
        f = self.interpreter.filePool.create_file(suffix='.png')
        cmdline += ['-o', f.name]
        self.setResult('output_image', f)
        cmdline += self.opt_command_line_val('-c', 'contrast')
        cmdline += self.opt_command_line_val('-cfp', 'component_fixed_point')
        cmdline += self.opt_command_line_val('-g', 'gamma')
        cmdline += self.opt_command_line_vec('-b', 'background')
        cmdline += self.opt_command_line_file('-bi', 'background_image')
        self.run_teem(*cmdline)
        
###############################################################################

_modules = [Teem, Emap, Soid, Miter, OverRGB,
            OffToEps,
            EpsToPpm,
            Unu,
            UnuMinmax,
            UnuSave,
            UnuSwap,
            UnuProject,
            UnuReshape,
            UnuResample,
            UnuJoin,
            UnuQuantize,
            Unu1op,
            Unu2op,
            Unu3op,
            UnuSlice,
            Teem_TT,
            Tend_norm,
            Tend_glyph]

##############################################################################

def package_dependencies():
    import core.packagemanager
    manager = core.packagemanager.get_package_manager()
    if manager.has_package('edu.utah.sci.vistrails.vtk'):
        return ['edu.utah.sci.vistrails.vtk']
    else:
        return []

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

    reg = core.modules.module_registry.registry

    # Register the TF widget interaction modules if they're available
    if reg.has_module('edu.utah.sci.vistrails.vtk',
                      'TransferFunction'):
        # Update the auto-add _modules list
        _modules.append(TeemScaledTransferFunction)
        TF = reg.get_descriptor_by_name('edu.utah.sci.vistrails.vtk',
                                        'TransferFunction').module
        # Update the input ports for TeemScaledTransferFunction now that we
        # know TF is present
        TeemScaledTransferFunction._input_ports.append(('transfer_function', [(TF,
                                                                               "the transfer function")]))
