###############################################################################
##
## Copyright (C) 2014-2016, New York University.
## Copyright (C) 2011-2014, NYU-Poly.
## Copyright (C) 2006-2011, University of Utah.
## All rights reserved.
## Contact: contact@vistrails.org
##
## This file is part of VisTrails.
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met:
##
##  - Redistributions of source code must retain the above copyright notice,
##    this list of conditions and the following disclaimer.
##  - Redistributions in binary form must reproduce the above copyright
##    notice, this list of conditions and the following disclaimer in the
##    documentation and/or other materials provided with the distribution.
##  - Neither the name of the New York University nor the names of its
##    contributors may be used to endorse or promote products derived from
##    this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
## AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
## THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
## PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
## CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
## OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
## WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
## OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
## ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
###############################################################################
"""basic_modules defines basic VisTrails Modules that are used in most
pipelines."""
from __future__ import division

import vistrails.core.cache.hasher
from vistrails.core.debug import format_exception
from vistrails.core.modules.module_registry import get_module_registry
from vistrails.core.modules.vistrails_module import Module, new_module, \
    Converter, NotCacheable, ModuleError
from vistrails.core.modules.config import ConstantWidgetConfig, \
    QueryWidgetConfig, ParamExpWidgetConfig, ModuleSettings, IPort, OPort, \
    CIPort
import vistrails.core.system
from vistrails.core.utils import InstanceObject
from vistrails.core import debug

from abc import ABCMeta
from ast import literal_eval
from itertools import izip
import mimetypes
import os
import pickle
import re
import shutil
import zipfile
import urllib

try:
    import hashlib
    sha_hash = hashlib.sha1
except ImportError:
    import sha
    sha_hash = sha.new

###############################################################################

version = '2.1.1'
name = 'Basic Modules'
identifier = 'org.vistrails.vistrails.basic'
old_identifiers = ['edu.utah.sci.vistrails.basic']

constant_config_path = "vistrails.gui.modules.constant_configuration"
query_config_path = "vistrails.gui.modules.query_configuration"
paramexp_config_path = "vistrails.gui.modules.paramexplore"

def get_port_name(port):
    if hasattr(port, 'name'):
        return port.name
    else:
        return port[0]

class meta_add_value_ports(type):
    def __new__(cls, name, bases, dct):
        """This metaclass adds the 'value' input and output ports.
        """
        mod = type.__new__(cls, name, bases, dct)

        if '_input_ports' in mod.__dict__:
            input_ports = mod._input_ports
            if not any(get_port_name(port_info) == 'value'
                       for port_info in input_ports):
                mod._input_ports = [('value', mod)]
                mod._input_ports.extend(input_ports)
        else:
            mod._input_ports = [('value', mod)]

        if '_output_ports' in mod.__dict__:
            output_ports = mod._output_ports
            if not any(get_port_name(port_info) == 'value'
                       for port_info in output_ports):
                mod._output_ports = [('value', mod)]
                mod._output_ports.extend(output_ports)
        else:
            mod._output_ports = [('value', mod)]

        return mod

class Constant(Module):
    """Base class for all Modules that represent a constant value of
    some type.
    
    When implementing your own constant, You have to adhere to the
    following interface:

    Implement the following methods:
    
       translate_to_python(x): Given a string, translate_to_python
       must return a python value that will be the value seen by the
       execution modules.

       For example, translate_to_python called on a float parameter
       with value '3.15' will return float('3.15').
       
       translate_to_string(): Return a string representation of the
       current constant, which will eventually be passed to
       translate_to_python.

       validate(v): return True if given python value is a plausible
       value for the constant. It should be implemented such that
       validate(translate_to_python(x)) == True for all valid x

    A constant must also expose its default value, through the field
    default_value.

    There are fields you are not allowed to use in your constant classes.
    These are: 'id', 'interpreter', 'logging' and 'change_parameter'

    You can also define the constant's own GUI widget.
    See core/modules/constant_configuration.py for details.
    
    """
    _settings = ModuleSettings(abstract=True)
    _output_ports = [OPort("value_as_string", "String")]

    __metaclass__ = meta_add_value_ports

    def compute(self):
        """Constant.compute() only checks validity (and presence) of
        input value."""
        v = self.get_input("value")
        b = self.validate(v)
        if not b:
            raise ModuleError(self, "Internal Error: Constant failed validation")
        self.set_output("value", v)
        self.set_output("value_as_string", self.translate_to_string(v))

    def setValue(self, v):
        self.set_output("value", self.translate_to_python(v))
        self.upToDate = True

    @staticmethod
    def translate_to_string(v):
        return str(v)

    @staticmethod
    def get_widget_class():
        # return StandardConstantWidget
        return None

    @staticmethod
    def query_compute(value_a, value_b, query_method):
        if query_method == '==' or query_method is None:
            return (value_a == value_b)
        elif query_method == '!=':
            return (value_a != value_b)
        return False

def new_constant(name, py_conversion=None, default_value=None, validation=None,
                 widget_type=None,
                 str_conversion=None, base_class=Constant,
                 compute=None, query_compute=None):
    """new_constant(name: str, 
                    py_conversion: callable,
                    default_value: python_type,
                    validation: callable,
                    widget_type: (path, name) tuple or QWidget type,
                    str_conversion: callable,
                    base_class: class,
                    compute: callable,
                    query_compute: static callable) -> Module

    new_constant dynamically creates a new Module derived from
    Constant with given py_conversion and str_conversion functions, a
    corresponding python type and a widget type. py_conversion is a
    python callable that takes a string and returns a python value of
    the type that the class should hold. str_conversion does the reverse.

    This is the quickest way to create new Constant Modules."""

    d = {}

    if py_conversion is not None:
        d["translate_to_python"] = py_conversion
    elif base_class == Constant:
        raise ValueError("Must specify translate_to_python for constant")
    if validation is not None:
        d["validate"] = validation
    elif base_class == Constant:
        raise ValueError("Must specify validation for constant")
    if default_value is not None:
        d["default_value"] = default_value

    if str_conversion is not None:
        d['translate_to_string'] = str_conversion
    if compute is not None:
        d['compute'] = compute
    if query_compute is not None:
        d['query_compute'] = query_compute
    if widget_type is not None:
        @staticmethod
        def get_widget_class():
            return widget_type
        d['get_widget_class'] = get_widget_class            

    m = new_module(base_class, name, d)
    m._input_ports = [('value', m)]
    m._output_ports = [('value', m)]
    return m

class Boolean(Constant):
    _settings = ModuleSettings(
            constant_widget='%s:BooleanWidget' % constant_config_path)
    default_value = False

    @staticmethod
    def translate_to_python(x):
        s = x.upper()
        if s == 'TRUE':
            return True
        if s == 'FALSE':
            return False
        raise ValueError('Boolean from String in VisTrails should be either '
                         '"true" or "false", got "%s" instead' % x)

    @staticmethod
    def validate(x):
        return isinstance(x, bool)

class Float(Constant):
    _settings = ModuleSettings(constant_widgets=[
        QueryWidgetConfig('%s:NumericQueryWidget' % query_config_path),
        ParamExpWidgetConfig('%s:FloatExploreWidget' % paramexp_config_path)])
    default_value = 0.0

    @staticmethod
    def translate_to_python(x):
        return float(x)

    @staticmethod
    def validate(x):
        return isinstance(x, (int, long, float))

    @staticmethod
    def query_compute(value_a, value_b, query_method):
        value_a = float(value_a)
        value_b = float(value_b)
        if query_method == '==' or query_method is None:
            return (value_a == value_b)
        elif query_method == '<':
            return (value_a < value_b)
        elif query_method == '>':
            return (value_a > value_b)
        elif query_method == '<=':
            return (value_a <= value_b)
        elif query_method == '>=':
            return (value_a >= value_b)

class Integer(Float):
    _settings = ModuleSettings(constant_widgets=[
        QueryWidgetConfig('%s:NumericQueryWidget' % query_config_path),
        ParamExpWidgetConfig('%s:IntegerExploreWidget' % paramexp_config_path)])
    default_value = 0

    @staticmethod
    def translate_to_python(x):
        if x.startswith('0x'):
            return int(x, 16)
        else:
            return int(x)

    @staticmethod
    def validate(x):
        return isinstance(x, (int, long))

class String(Constant):
    _settings = ModuleSettings(
            configure_widget="vistrails.gui.modules.string_configure:TextConfigurationWidget",
            constant_widgets=[
                 ConstantWidgetConfig('%s:MultiLineStringWidget' % constant_config_path,
                                      widget_type='multiline'),
                 QueryWidgetConfig('%s:StringQueryWidget' % query_config_path)])
    _output_ports = [OPort("value_as_string", "String", optional=True)]
    default_value = ""

    @staticmethod
    def translate_to_python(x):
        assert isinstance(x, (str, unicode))
        return str(x)

    @staticmethod
    def validate(x):
        return isinstance(x, str)

    @staticmethod
    def query_compute(value_a, value_b, query_method):
        if query_method == '*[]*' or query_method is None:
            return (value_b in value_a)
        elif query_method == '==':
            return (value_a == value_b)
        elif query_method == '=~':
            try:
                m = re.match(value_b, value_a)
                if m is not None:
                    return (m.end() ==len(value_a))
            except re.error:
                pass
        return False

##############################################################################

# Rich display for IPython
try:
    from IPython import display
except ImportError:
    display = None

class PathObject(object):
    def __init__(self, name):
        self.name = name
        self._ipython_repr = None

    def __repr__(self):
        return "PathObject(%r)" % self.name
    __str__ = __repr__

    def __getattr__(self, name):
        if name.startswith('_repr_') and name.endswith('_'):
            if self._ipython_repr is None:
                filetype, encoding = mimetypes.guess_type(self.name)
                if filetype and filetype.startswith('image/'):
                    self._ipython_repr = display.Image(filename=self.name)
                else:
                    self._ipython_repr = False
            if self._ipython_repr is not False:
                return getattr(self._ipython_repr, name)
        raise AttributeError

class Path(Constant):
    _settings = ModuleSettings(constant_widget=("%s:PathChooserWidget" % \
                                                constant_config_path))
    _input_ports = [IPort("value", "Path"),
                    IPort("name", "String", optional=True)]
    _output_ports = [OPort("value", "Path")]

    @staticmethod
    def translate_to_python(x):
        return PathObject(x)

    @staticmethod
    def translate_to_string(x):
        return str(x.name)

    @staticmethod
    def validate(v):
        return isinstance(v, PathObject)

    def get_name(self):
        n = None
        if self.has_input("value"):
            n = self.get_input("value").name
        if n is None:
            self.check_input("name")
            n = self.get_input("name")
        return n

    def set_results(self, n):
        self.set_output("value", PathObject(n))
        self.set_output("value_as_string", n)

    def compute(self):
        n = self.get_name()
        self.set_results(n)

Path.default_value = PathObject('')

def path_parameter_hasher(p):
    def get_mtime(path):
        t = int(os.path.getmtime(path))
        if os.path.isdir(path):
            for subpath in os.listdir(path):
                subpath = os.path.join(path, subpath)
                if os.path.isdir(subpath):
                    t = max(t, get_mtime(subpath))
        return t

    h = vistrails.core.cache.hasher.Hasher.parameter_signature(p)
    try:
        # FIXME: This will break with aliases - I don't really care that much
        t = get_mtime(p.strValue)
    except OSError:
        return h
    hasher = sha_hash()
    hasher.update(h)
    hasher.update(str(t))
    return hasher.digest()

class File(Path):
    """File is a VisTrails Module that represents a file stored on a
    file system local to the machine where VisTrails is running."""

    _settings = ModuleSettings(constant_signature=path_parameter_hasher,
                               constant_widget=("%s:FileChooserWidget" % \
                                                constant_config_path))
    _input_ports = [IPort("value", "File"),
                    IPort("create_file", "Boolean", optional=True)]
    _output_ports = [OPort("value", "File"),
                     OPort("local_filename", "String", optional=True)]

    def compute(self):
        n = self.get_name()
        if (self.has_input("create_file") and self.get_input("create_file")):
            vistrails.core.system.touch(n)
        if not os.path.isfile(n):
            raise ModuleError(self, 'File %r does not exist' % n)
        self.set_results(n)
        self.set_output("local_filename", n)

class Directory(Path):

    _settings = ModuleSettings(constant_signature=path_parameter_hasher,
                               constant_widget=("%s:DirectoryChooserWidget" % \
                                                constant_config_path))
    _input_ports = [IPort("value", "Directory"),
                    IPort("create_directory", "Boolean", optional=True)]
    _output_ports = [OPort("value", "Directory"),
                     OPort("itemList", "List")]

    def compute(self):
        n = self.get_name()
        if (self.has_input("create_directory") and 
                self.get_input("create_directory")):
            try:
                vistrails.core.system.mkdir(n)
            except Exception, e:
                raise ModuleError(self, 'mkdir: %s' % format_exception(e))
        if not os.path.isdir(n):
            raise ModuleError(self, 'Directory "%s" does not exist' % n)
        self.set_results(n)

        dir_list = os.listdir(n)
        output_list = []
        for item in dir_list:
            full_path = os.path.join(n, item)
            output_list.append(PathObject(full_path))
        self.set_output('itemList', output_list)

##############################################################################

class OutputPath(Path):
    _settings = ModuleSettings(constant_widget=("%s:OutputPathChooserWidget" % \
                                                constant_config_path))
    _input_ports = [IPort("value", "OutputPath")]
    _output_ports = [OPort("value", "OutputPath")]

    def get_name(self):
        n = None
        if self.has_input("value"):
            n = self.get_input("value").name
        if n is None:
            self.check_input("name")
            n = self.get_input("name")
        return n

    def set_results(self, n):
        self.set_output("value", PathObject(n))
        self.set_output("value_as_string", n)

    def compute(self):
        n = self.get_name()
        self.set_results(n)

class FileSink(NotCacheable, Module):
    """FileSink takes a file and writes it to a user-specified
    location in the file system.  The file is stored at location
    specified by the outputPath.  The overwrite flag allows users to
    specify whether an existing path should be overwritten."""

    _input_ports = [IPort("file", File),
                    IPort("outputPath", OutputPath),
                    IPort("overwrite", Boolean, optional=True, 
                          default=True),
                    IPort("publishFile", Boolean, optional=True)]
    
    def compute(self):
        input_file = self.get_input("file")
        output_path = self.get_input("outputPath")
        full_path = output_path.name

        if os.path.isfile(full_path):
            if self.get_input('overwrite'):
                try:
                    os.remove(full_path)
                except OSError, e:
                    msg = ('Could not delete existing path "%s" '
                           '(overwrite on)' % full_path)
                    raise ModuleError(self, msg)
            else:
                raise ModuleError(self,
                                  "Could not copy file to '%s': file already "
                                  "exists")

        try:
            vistrails.core.system.link_or_copy(input_file.name, full_path)
        except OSError, e:
            msg = "Could not create file '%s': %s" % (full_path, e)
            raise ModuleError(self, msg)

        if (self.has_input("publishFile") and
            self.get_input("publishFile") or 
            not self.has_input("publishFile")):
            if self.moduleInfo.has_key('extra_info'):
                if self.moduleInfo['extra_info'].has_key('pathDumpCells'):
                    folder = self.moduleInfo['extra_info']['pathDumpCells']
                    base_fname = os.path.basename(full_path)
                    (base_fname, file_extension) = os.path.splitext(base_fname)
                    base_fname = os.path.join(folder, base_fname)
                    # make a unique filename
                    filename = base_fname + file_extension
                    counter = 2
                    while os.path.exists(filename):
                        filename = base_fname + "_%d%s" % (counter,
                                                           file_extension)
                        counter += 1
                    try:
                        vistrails.core.system.link_or_copy(input_file.name, filename)
                    except OSError, e:
                        msg = "Could not publish file '%s' \n   on  '%s':" % (
                                full_path, filename)
                        # I am not sure whether we should raise an error
                        # I will just print a warning for now (Emanuele)
                        debug.warning("%s" % msg, e)

class DirectorySink(NotCacheable, Module):
    """DirectorySink takes a directory and writes it to a
    user-specified location in the file system.  The directory is
    stored at location specified by the outputPath.  The overwrite
    flag allows users to specify whether an existing path should be
    overwritten."""

    _input_ports = [IPort("dir", Directory),
                    IPort("outputPath", OutputPath),
                    IPort("overwrite", Boolean, optional=True, default="True")]

    def compute(self):
        input_dir = self.get_input("dir")
        output_path = self.get_input("outputPath")
        full_path = output_path.name

        if os.path.exists(full_path):
            if self.get_input("overwrite"):
                try:
                    if os.path.isfile(full_path):
                        os.remove(full_path)
                    else:
                        shutil.rmtree(full_path)
                except OSError, e:
                    msg = ('Could not delete existing path "%s" '
                           '(overwrite on)' % full_path)
                    raise ModuleError(
                            self,
                            '%s\n%s' % (msg, format_exception(e)))
            else:
                msg = ('Could not write to existing path "%s" '
                       '(overwrite off)' % full_path)
                raise ModuleError(self, msg)
            
        try:
            shutil.copytree(input_dir.name, full_path)
        except OSError, e:
            msg = 'Could not copy path from "%s" to "%s"' % \
                (input_dir.name, full_path)
            raise ModuleError(self, '%s\n%s' % (msg, format_exception(e)))

##############################################################################

class WriteFile(Converter):
    """Writes a String to a temporary File.
    """
    _input_ports = [IPort('in_value', String),
                    IPort('suffix', String, optional=True, default=""),
                    IPort('encoding', String, optional=True)]
    _output_ports = [OPort('out_value', File)]

    def compute(self):
        contents = self.get_input('in_value')
        suffix = self.force_get_input('suffix', '')
        result = self.interpreter.filePool.create_file(suffix=suffix)
        if self.has_input('encoding'):
            contents = contents.decode('utf-8') # VisTrails uses UTF-8
                                                # internally (I hope)
            contents = contents.encode(self.get_input('encoding'))
        with open(result.name, 'wb') as fp:
            fp.write(contents)
        self.set_output('out_value', result)

class ReadFile(Converter):
    """Reads a File to a String.
    """
    _input_ports = [IPort('in_value', File),
                    IPort('encoding', String, optional=True)]
    _output_ports = [OPort('out_value', String)]

    def compute(self):
        filename = self.get_input('in_value').name
        with open(filename, 'rb') as fp:
            contents = fp.read()
        if self.has_input('encoding'):
            contents = contents.decode(self.get_input('encoding'))
            contents = contents.encode('utf-8') # VisTrails uses UTF-8
                                                # internally (for now)
        self.set_output('out_value', contents)

##############################################################################

class Color(Constant):
    # We set the value of a color object to be an InstanceObject that
    # contains a tuple because a tuple would be interpreted as a
    # type(tuple) which messes with the interpreter

    _settings = ModuleSettings(constant_widgets=[
        '%s:ColorWidget' % constant_config_path, 
        ConstantWidgetConfig('%s:ColorEnumWidget' % \
                             constant_config_path, 
                             widget_type='enum'),
        QueryWidgetConfig('%s:ColorQueryWidget' % \
                          query_config_path),
        ParamExpWidgetConfig('%s:RGBExploreWidget' % \
                             paramexp_config_path,
                             widget_type='rgb'),
        ParamExpWidgetConfig('%s:HSVExploreWidget' % \
                             paramexp_config_path,
                             widget_type='hsv')])
    _input_ports = [IPort("value", "Color")]
    _output_ports = [OPort("value", "Color")]

    default_value = InstanceObject(tuple=(1,1,1))

    @staticmethod
    def translate_to_python(x):
        return InstanceObject(
            tuple=tuple([float(a) for a in x.split(',')]))

    @staticmethod
    def translate_to_string(v):
        return ','.join('%f' % c for c in v.tuple)

    @staticmethod
    def validate(x):
        return isinstance(x, InstanceObject) and hasattr(x, 'tuple')

    @staticmethod
    def to_string(r, g, b):
        return "%s,%s,%s" % (r,g,b)        

    @staticmethod
    def query_compute(value_a, value_b, query_method):
        # SOURCE: http://www.easyrgb.com/index.php?X=MATH
        def rgb_to_xyz(r, g, b):
            # r,g,b \in [0,1]

            if r > 0.04045: 
                r = ( ( r + 0.055 ) / 1.055 ) ** 2.4
            else:
                r = r / 12.92
            if g > 0.04045:
                g = ( ( g + 0.055 ) / 1.055 ) ** 2.4
            else:
                g = g / 12.92
            if b > 0.04045: 
                b = ( ( b + 0.055 ) / 1.055 ) ** 2.4
            else:
                b = b / 12.92

            r *= 100
            g *= 100
            b *= 100

            # Observer. = 2 deg, Illuminant = D65
            x = r * 0.4124 + g * 0.3576 + b * 0.1805
            y = r * 0.2126 + g * 0.7152 + b * 0.0722
            z = r * 0.0193 + g * 0.1192 + b * 0.9505
            return (x,y,z)

        def xyz_to_cielab(x,y,z):
            # Observer= 2 deg, Illuminant= D65
            ref_x, ref_y, ref_z = (95.047, 100.000, 108.883)
            x /= ref_x
            y /= ref_y
            z /= ref_z

            if x > 0.008856:
                x = x ** ( 1/3.0 )
            else:                    
                x = ( 7.787 * x ) + ( 16 / 116.0 )
            if y > 0.008856:
                y = y ** ( 1/3.0 )
            else:
                y = ( 7.787 * y ) + ( 16 / 116.0 )
            if z > 0.008856: 
                z = z ** ( 1/3.0 )
            else:
                z = ( 7.787 * z ) + ( 16 / 116.0 )

            L = ( 116 * y ) - 16
            a = 500 * ( x - y )
            b = 200 * ( y - z )
            return (L, a, b)

        def rgb_to_cielab(r,g,b):
            return xyz_to_cielab(*rgb_to_xyz(r,g,b))
        
        value_a_rgb = (float(a) for a in value_a.split(','))
        value_b_rgb = (float(b) for b in value_b.split(','))
        value_a_lab = rgb_to_cielab(*value_a_rgb)
        value_b_lab = rgb_to_cielab(*value_b_rgb)
        
        # cie76 difference
        diff = sum((v_1 - v_2) ** 2 
                   for v_1, v_2 in izip(value_a_lab, value_b_lab)) ** (0.5)

        # print "CIE 76 DIFFERENCE:", diff
        if query_method is None:
            query_method = '2.3'
        return diff < float(query_method)

##############################################################################

class StandardOutput(NotCacheable, Module):
    """StandardOutput is a VisTrails Module that simply prints the
    value connected on its port to standard output. It is intended
    mostly as a debugging device."""

    _input_ports = [IPort("value", 'Variant')]

    def compute(self):
        v = self.get_input("value")
        if isinstance(v, PathObject):
            try:
                fp = open(v.name, 'rb')
            except IOError:
                print v
            else:
                try:
                    CHUNKSIZE = 2048
                    chunk = fp.read(CHUNKSIZE)
                    if chunk:
                        sys.stdout.write(chunk)
                        while len(chunk) == CHUNKSIZE:
                            chunk = fp.read(CHUNKSIZE)
                            if chunk:
                                sys.stdout.write(chunk)
                        sys.stdout.write('\n')
                finally:
                    fp.close()
        else:
            print v

##############################################################################

# Tuple will be reasonably magic right now. We'll integrate it better
# with vistrails later.
# TODO: Check Tuple class, test, integrate.
class Tuple(Module):
    """Tuple represents a tuple of values. Tuple might not be well
    integrated with the rest of VisTrails, so don't use it unless
    you know what you're doing."""

    _settings = ModuleSettings(configure_widget=
        "vistrails.gui.modules.tuple_configuration:TupleConfigurationWidget")

    def __init__(self):
        Module.__init__(self)
        self.input_ports_order = []
        self.values = tuple()

    def transfer_attrs(self, module):
        Module.transfer_attrs(self, module)
        self.input_ports_order = [p.name for p in module.input_port_specs]

    def compute(self):
        values = tuple([self.get_input(p)
                        for p in self.input_ports_order])
        self.values = values
        self.set_output("value", values)

class Untuple(Module):
    """Untuple takes a tuple and returns the individual values.  It
    reverses the actions of Tuple.

    """

    _settings = ModuleSettings(configure_widget=
        "vistrails.gui.modules.tuple_configuration:UntupleConfigurationWidget")

    def __init__(self):
        Module.__init__(self)
        self.output_ports_order = []

    def transfer_attrs(self, module):
        Module.transfer_attrs(self, module)
        self.output_ports_order = [p.name for p in module.output_port_specs]
        # output_ports are reversed for display purposes...
        self.output_ports_order.reverse()

    def compute(self):
        if self.has_input("tuple"):
            tuple = self.get_input("tuple")
            values = tuple.values
        else:
            values = self.get_input("value")
        for p, value in izip(self.output_ports_order, values):
            self.set_output(p, value)

##############################################################################

class ConcatenateString(Module):
    """ConcatenateString takes many strings as input and produces the
    concatenation as output. Useful for constructing filenames, for
    example.

    This class will probably be replaced with a better API in the
    future."""

    fieldCount = 4
    _input_ports = [IPort("str%d" % i, "String")
                    for i in xrange(1, 1 + fieldCount)]
    _output_ports = [OPort("value", "String")]

    def compute(self):
        result = "".join(self.force_get_input('str%d' % i, '')
                         for i in xrange(1, 1 + self.fieldCount))
        self.set_output('value', result)

##############################################################################

class Not(Module):
    """Not inverts a Boolean.
    """
    _input_ports = [IPort('input', 'Boolean')]
    _output_ports = [OPort('value', 'Boolean')]

    def compute(self):
        value = self.get_input('input')
        self.set_output('value', not value)

##############################################################################

# List

# If numpy is available, we consider numpy arrays to be lists as well
class ListType(object):
    __metaclass__ = ABCMeta

ListType.register(list)
try:
    import numpy
except ImportError:
    numpy = None
else:
    ListType.register(numpy.ndarray)

class List(Constant):
    _settings = ModuleSettings(configure_widget=
        "vistrails.gui.modules.list_configuration:ListConfigurationWidget")
    _input_ports = [IPort("value", "List"),
                    IPort("head", "Variant", depth=1),
                    IPort("tail", "List")]
    _output_ports = [OPort("value", "List")]

    default_value = []

    def __init__(self):
        Constant.__init__(self)
        self.input_ports_order = []

    def transfer_attrs(self, module):
        Module.transfer_attrs(self, module)
        self.input_ports_order = [p.name for p in module.input_port_specs]

    @staticmethod
    def validate(x):
        return isinstance(x, ListType)

    @staticmethod
    def translate_to_python(v):
        return literal_eval(v)

    @staticmethod
    def translate_to_string(v, dims=None):
        if dims is None:
            if numpy is not None and isinstance(v, numpy.ndarray):
                dims = v.ndim
            else:
                dims = 1
        if dims == 1:
            return '[%s]' % ', '.join(repr(c)
                                      for c in v)
        else:
            return '[%s]' % ', '.join(List.translate_to_string(c, dims-1)
                                      for c in v)

    def compute(self):
        head, middle, items, tail = [], [], [], []
        got_value = False

        if self.has_input('value'):
            # run the regular compute here
            Constant.compute(self)
            middle = self.outputPorts['value']
            got_value = True
        if self.has_input('head'):
            head = self.get_input('head')
            got_value = True
        if self.input_ports_order:
            items = [self.get_input(p)
                     for p in self.input_ports_order]
            got_value = True
        if self.has_input('tail'):
            tail = self.get_input('tail')
            got_value = True

        if not got_value:
            self.get_input('value')
        self.set_output('value', head + middle + items + tail)

##############################################################################
# Dictionary

class Dictionary(Constant):
    default_value = {}
    _input_ports = [CIPort("addPair", "Module, Module"),
                    IPort("addPairs", "List")]

    @staticmethod
    def translate_to_python(v):
        return literal_eval(v)

    @staticmethod
    def validate(x):
        return isinstance(x, dict)

    def compute(self):
        d = {}
        if self.has_input('value'):
            Constant.compute(self)
            d.update(self.outputPorts['value'])
        if self.has_input('addPair'):
            pairs_list = self.get_input_list('addPair')
            d.update(pairs_list)
        if self.has_input('addPairs'):
            d.update(self.get_input('addPairs'))

        self.set_output("value", d)

##############################################################################

# TODO: Null should be a subclass of Constant?
class Null(Module):
    """Null is the class of None values."""
    _settings = ModuleSettings(hide_descriptor=True)

    def compute(self):
        self.set_output("value", None)

##############################################################################

class Unpickle(Module):
    """Unpickles a string.
    """
    _settings = ModuleSettings(hide_descriptor=True)
    _input_ports = [IPort('input', 'String')]
    _output_ports = [OPort('result', 'Variant')]

    def compute(self):
        value = self.get_input('input')
        self.set_output('result', pickle.loads(value))

##############################################################################

class CodeRunnerMixin(object):
    def __init__(self):
        self.output_ports_order = []
        super(CodeRunnerMixin, self).__init__()

    def transfer_attrs(self, module):
        Module.transfer_attrs(self, module)
        self.output_ports_order = [p.name for p in module.output_port_specs]
        # output_ports are reversed for display purposes...
        self.output_ports_order.reverse()

    def run_code(self, code_str,
                 use_input=False,
                 use_output=False):
        """run_code runs a piece of code as a VisTrails module.
        use_input and use_output control whether to use the inputport
        and output port dictionary as local variables inside the
        execution."""
        import vistrails.core.packagemanager
        def fail(msg):
            raise ModuleError(self, msg)
        def cache_this():
            self.is_cacheable = lambda *args, **kwargs: True
        locals_ = locals()
        if use_input:
            for k in self.inputPorts:
                locals_[k] = self.get_input(k)
        if use_output:
            for output_portname in self.output_ports_order:
                if output_portname not in self.inputPorts:
                    locals_[output_portname] = None
        _m = vistrails.core.packagemanager.get_package_manager()
        reg = get_module_registry()
        locals_.update({'fail': fail,
                        'package_manager': _m,
                        'cache_this': cache_this,
                        'registry': reg,
                        'self': self})
        if 'source' in locals_:
            del locals_['source']
        # Python 2.6 needs code to end with newline
        exec code_str + '\n' in locals_, locals_
        if use_output:
            for k in self.output_ports_order:
                if locals_.get(k) is not None:
                    self.set_output(k, locals_[k])

##############################################################################

class PythonSource(CodeRunnerMixin, NotCacheable, Module):
    """PythonSource is a Module that executes an arbitrary piece of
    Python code.

    It is especially useful for one-off pieces of 'glue' in a
    pipeline.

    If you want a PythonSource execution to fail, call
    fail(error_message).

    If you want a PythonSource execution to be cached, call
    cache_this().
    """
    _settings = ModuleSettings(
        configure_widget=("vistrails.gui.modules.python_source_configure:"
                             "PythonSourceConfigurationWidget"))
    _input_ports = [IPort('source', 'String', optional=True, default="")]
    _output_pors = [OPort('self', 'Module')]

    def compute(self):
        s = urllib.unquote(str(self.get_input('source')))
        self.run_code(s, use_input=True, use_output=True)

##############################################################################

def zip_extract_file(archive, filename_in_archive, output_filename):
    z = zipfile.ZipFile(archive)
    try:
        fileinfo = z.getinfo(filename_in_archive) # Might raise KeyError
        output_dirname, output_filename = os.path.split(output_filename)
        fileinfo.filename = output_filename
        z.extract(fileinfo, output_dirname)
    finally:
        z.close()


def zip_extract_all_files(archive, output_path):
    z = zipfile.ZipFile(archive)
    try:
        z.extractall(output_path)
    finally:
        z.close()


class Unzip(Module):
    """Unzip extracts a file from a ZIP archive."""
    _input_ports = [IPort('archive_file', 'File'),
                    IPort('filename_in_archive', 'String')]
    _output_ports = [OPort('file', 'File')]

    def compute(self):
        self.check_input("archive_file")
        self.check_input("filename_in_archive")
        filename_in_archive = self.get_input("filename_in_archive")
        archive_file = self.get_input("archive_file")
        if not os.path.isfile(archive_file.name):
            raise ModuleError(self, "archive file does not exist")
        suffix = self.interpreter.filePool.guess_suffix(filename_in_archive)
        output = self.interpreter.filePool.create_file(suffix=suffix)
        zip_extract_file(archive_file.name,
                         filename_in_archive,
                         output.name)
        self.set_output("file", output)


class UnzipDirectory(Module):
    """UnzipDirectory extracts every file from a ZIP archive."""
    _input_ports = [IPort('archive_file', 'File')]
    _output_ports = [OPort('directory', 'Directory')]

    def compute(self):
        self.check_input("archive_file")
        archive_file = self.get_input("archive_file")
        if not os.path.isfile(archive_file.name):
            raise ModuleError(self, "archive file does not exist")
        output = self.interpreter.filePool.create_directory()
        zip_extract_all_files(archive_file.name,
                              output.name)
        self.set_output("directory", output)

##############################################################################

class Round(Converter):
    """Turns a Float into an Integer.
    """
    _settings = ModuleSettings(hide_descriptor=True)
    _input_ports = [IPort('in_value', 'Float'),
                    IPort('floor', 'Boolean', optional=True, default="True")]
    _output_ports = [OPort('out_value', 'Integer')]

    def compute(self):
        fl = self.get_input('in_value')
        floor = self.get_input('floor')
        if floor:
            integ = int(fl)         # just strip the decimals
        else:
            integ = int(fl + 0.5)   # nearest
        self.set_output('out_value', integ)


class TupleToList(Converter):
    """Turns a Tuple into a List.
    """
    _settings = ModuleSettings(hide_descriptor=True)
    _input_ports = [IPort('in_value', 'Variant')]
    _output_ports = [OPort('out_value', 'List')]
    
    @classmethod
    def can_convert(cls, sub_descs, super_descs):
        if len(sub_descs) <= 1:
            return False
        reg = get_module_registry()
        return super_descs == [reg.get_descriptor(List)]

    def compute(self):
        tu = self.get_input('in_value')
        if not isinstance(tu, tuple):
            raise ModuleError(self, "Input is not a tuple")
        self.set_output('out_value', list(tu))

##############################################################################
    
class Variant(Module):
    """
    Variant is tracked internally for outputing a variant type on
    output port. For input port, Module type should be used
    
    """
    _settings = ModuleSettings(abstract=True)

##############################################################################

class Generator(object):
    """
    Used to keep track of list iteration, it will execute a module once for
    each input in the list/generator.
    """
    _settings = ModuleSettings(abstract=True)

    generators = []
    def __init__(self, size=None, module=None, generator=None, port=None,
                 accumulated=False):
        self.module = module
        self.generator = generator
        self.port = port
        self.size = size
        self.accumulated = accumulated
        if generator and module not in Generator.generators:
            # add to global list of generators
            # they will be topologically ordered
            module.generator = generator
            Generator.generators.append(module)
            
    def next(self):
        """ return next value - the generator """
        value = self.module.get_output(self.port)
        if isinstance(value, Generator):
            value = value.all()
        return value
    
    def all(self):
        """ exhausts next() for Streams
        
        """
        items = []
        item = self.next()
        while item is not None:
            items.append(item)
            item = self.next()
        return items

    @staticmethod
    def stream():
        """ executes all generators until inputs are exhausted
            this makes sure branching and multiple sinks are executed correctly

        """
        result = True
        if not Generator.generators:
            return
        while result is not None:
            for g in Generator.generators:
                result = g.next()
        Generator.generators = []

##############################################################################

class Assert(Module):
    """
    Assert is a simple module that conditionally stops the execution.
    """
    _input_ports = [IPort('condition', 'Boolean')]

    def compute(self):
        condition = self.get_input('condition')
        if not condition:
            raise ModuleError(self, "Assert: condition is False",
                              abort=True)


class AssertEqual(Module):
    """
    AssertEqual works like Assert but compares two values.

    It is provided for convenience.
    """

    _input_ports = [IPort('value1', 'Variant'),
                    IPort('value2', 'Variant')]

    def compute(self):
        values = (self.get_input('value1'),
                  self.get_input('value2'))
        if values[0] != values[1]:
            reprs = tuple(repr(v) for v in values)
            reprs = tuple('%s...' % v[:17] if len(v) > 20 else v
                          for v in reprs)
            raise ModuleError(self, "AssertEqual: values are different: "
                                    "%r, %r" % reprs,
                              abort=True)

##############################################################################

class StringFormat(Module):
    """
    Builds a string from objects using Python's str.format().
    """
    _settings = ModuleSettings(configure_widget=
        'vistrails.gui.modules.stringformat_configuration:'
            'StringFormatConfigurationWidget')
    _input_ports = [IPort('format', String)]
    _output_ports = [OPort('value', String)]

    @staticmethod
    def list_placeholders(fmt):
        placeholders = set()
        nb = 0
        i = 0
        n = len(fmt)
        while i < n:
            if fmt[i] == '{':
                i += 1
                if fmt[i] == '{': # KeyError:
                    i += 1
                    continue
                e = fmt.index('}', i) # KeyError
                f = e
                for c in (':', '!', '[', '.'):
                    c = fmt.find(c, i)
                    if c != -1:
                        f = min(f, c)
                if i == f:
                    nb += 1
                else:
                    arg = fmt[i:f]
                    try:
                        arg = int(arg)
                    except ValueError:
                        placeholders.add(arg)
                    else:
                        nb = max(nb, arg + 1)
                i = e
            i += 1
        return nb, placeholders

    def compute(self):
        fmt = self.get_input('format')
        args, kwargs = StringFormat.list_placeholders(fmt)
        f_args = [self.get_input('_%d' % n)
                  for n in xrange(args)]
        f_kwargs = dict((n, self.get_input(n))
                        for n in kwargs)
        self.set_output('value', fmt.format(*f_args, **f_kwargs))

##############################################################################

def init_constant(m):
    reg = get_module_registry()

    reg.add_module(m)
    reg.add_input_port(m, "value", m)
    reg.add_output_port(m, "value", m)

_modules = [Module, Converter, Constant, Boolean, Float, Integer, String, List,
            Path, File, Directory, OutputPath,
            FileSink, DirectorySink, WriteFile, ReadFile, StandardOutput,
            Tuple, Untuple, ConcatenateString, Not, Dictionary, Null, Variant,
            Unpickle, PythonSource, Unzip, UnzipDirectory, Color,
            Round, TupleToList, Assert, AssertEqual, StringFormat]

def initialize(*args, **kwargs):
    # initialize the sub_module modules, too
    import vistrails.core.modules.sub_module
    import vistrails.core.modules.output_modules
    _modules.extend(vistrails.core.modules.sub_module._modules)
    _modules.extend(vistrails.core.modules.output_modules._modules)


def handle_module_upgrade_request(controller, module_id, pipeline):
    from vistrails.core.upgradeworkflow import UpgradeWorkflowHandler
    reg = get_module_registry()

    def outputName_remap(old_conn, new_module):
        ops = []
        old_src_module = pipeline.modules[old_conn.source.moduleId]
        op_desc = reg.get_descriptor(OutputPath)
        new_x = (old_src_module.location.x + new_module.location.x) / 2.0
        new_y = (old_src_module.location.y + new_module.location.y) / 2.0
        op_module = \
            controller.create_module_from_descriptor(op_desc, new_x, new_y)
        ops.append(('add', op_module))
        create_new_connection = UpgradeWorkflowHandler.create_new_connection
        new_conn_1 = create_new_connection(controller,
                                           old_src_module,
                                           old_conn.source,
                                           op_module,
                                           "name")
        ops.append(('add', new_conn_1))
        new_conn_2 = create_new_connection(controller,
                                           op_module,
                                           "value",
                                           new_module,
                                           "outputPath")
        ops.append(('add', new_conn_2))
        return ops

    module_remap = {'FileSink':
    [(None, '1.6', None,
                          {'dst_port_remap':
                               {'overrideFile': 'overwrite',
                                'outputName': outputName_remap},
                           'function_remap':
                               {'overrideFile': 'overwrite',
                                'outputName': 'outputPath'}})],
                    'GetItemsFromDirectory':
                        [(None, '1.6', 'Directory',
                          {'dst_port_remap':
                               {'dir': 'value'},
                           'src_port_remap':
                               {'itemlist': 'itemList'},
                           })],
                    'InputPort':
                        [(None, '1.6', None,
                          {'dst_port_remap': {'old_name': None}})],
                    'OutputPort':
                        [(None, '1.6', None,
                          {'dst_port_remap': {'old_name': None}})],
                    'PythonSource':
                        [(None, '1.6', None, {})],
                    'Tuple':
                        [(None, '2.1.1', None, {})],
                    'StandardOutput':
                        [(None, '2.1.1', None, {})],
                    'List':
                        [(None, '2.1.1', None, {})],
                    'AssertEqual':
                        [(None, '2.1.1', None, {})],
                    'Converter':
                        [(None, '2.1.1', None, {})],
                    }

    return UpgradeWorkflowHandler.remap_module(controller, module_id, pipeline,
                                               module_remap)

###############################################################################

class NewConstant(Constant):
    """
    A new Constant module to be used inside the FoldWithModule module.
    """
    def setValue(self, v):
        self.set_output("value", v)
        self.upToDate = True

def create_constant(value):
    """
    Creates a NewConstant module, to be used for the ModuleConnector.
    """
    constant = NewConstant()
    constant.setValue(value)
    return constant

def get_module(value, signature=None):
    """
    Creates a module for value, in order to do the type checking.
    """
    if isinstance(value, Constant):
        return type(value)
    elif isinstance(value, bool):
        return Boolean
    elif isinstance(value, str):
        return String
    elif isinstance(value, int):
        return Integer
    elif isinstance(value, float):
        return Float
    if isinstance(value, list):
        return List
    elif isinstance(value, tuple):
        # Variant supports signatures of any length
        if signature is None or \
           (len(signature) == 1 and signature[0][0] == Variant):
            return (Variant,)*len(value)
        v_modules = ()
        for element in xrange(len(value)):
            v_modules += (get_module(value[element], signature[element]),)
        if None in v_modules: # Identification failed
            return None
        return v_modules
    else: # pragma: no cover
        debug.warning("Could not identify the type of the list element.")
        debug.warning("Type checking is not going to be done inside "
                      "iterated module.")
        return None

###############################################################################

import sys
import unittest

class TestConcatenateString(unittest.TestCase):
    @staticmethod
    def concatenate(**kwargs):
        from vistrails.tests.utils import execute, intercept_result
        with intercept_result(ConcatenateString, 'value') as results:
            errors = execute([
                    ('ConcatenateString', 'org.vistrails.vistrails.basic', [
                        (name, [('String', value)])
                        for name, value in kwargs.iteritems()
                    ]),
                ])
            if errors:
                return None
        return results

    def test_concatenate(self):
        """Concatenates strings"""
        self.assertEqual(self.concatenate(
                str1="hello ", str2="world"),
                ["hello world"])
        self.assertEqual(self.concatenate(
                str3="hello world"),
                ["hello world"])
        self.assertEqual(self.concatenate(
                str2="hello ", str4="world"),
                ["hello world"])
        self.assertEqual(self.concatenate(
                str1="hello", str3=" ", str4="world"),
                ["hello world"])

    def test_empty(self):
        """Runs ConcatenateString with no input"""
        self.assertEqual(self.concatenate(), [""])


class TestNot(unittest.TestCase):
    def run_pipeline(self, functions):
        from vistrails.tests.utils import execute, intercept_result
        with intercept_result(Not, 'value') as results:
            errors = execute([
                    ('Not', 'org.vistrails.vistrails.basic',
                     functions),
                ])
        return errors, results

    def test_true(self):
        errors, results = self.run_pipeline([
                ('input', [('Boolean', 'True')])])
        self.assertFalse(errors)
        self.assertEqual(len(results), 1)
        self.assertIs(results[0], False)

    def test_false(self):
        errors, results = self.run_pipeline([
                ('input', [('Boolean', 'False')])])
        self.assertFalse(errors)
        self.assertEqual(len(results), 1)
        self.assertIs(results[0], True)

    def test_notset(self):
        errors, results = self.run_pipeline([])
        self.assertTrue(errors)


class TestList(unittest.TestCase):
    @staticmethod
    def build_list(value=None, head=None, tail=None):
        from vistrails.tests.utils import execute, intercept_result
        with intercept_result(List, 'value') as results:
            functions = []
            def add(n, v, t):
                if v is not None:
                    for e in v:
                        functions.append(
                                (n, [(t, e)])
                            )
            add('value', value, 'List')
            add('head', head, 'String')
            add('tail', tail, 'List')

            errors = execute([
                    ('List', 'org.vistrails.vistrails.basic', functions),
                ])
            if errors:
                return None
        # List is a Constant, so the interpreter will set the result 'value'
        # from the 'value' input port automatically
        # Ignore these first results
        return results[-1]

    def test_simple(self):
        """Tests the default ports of the List module"""
        self.assertEqual(self.build_list(
                value=['["a", "b", "c"]']),
                ["a", "b", "c"])
        self.assertEqual(self.build_list(
                head=["d"],
                value=['["a", "b", "c"]']),
                ["d", "a", "b", "c"])
        self.assertEqual(self.build_list(
                head=["d"],
                value=['["a", "b", "c"]'],
                tail=['["e", "f"]']),
                ["d", "a", "b", "c", "e", "f"])
        self.assertEqual(self.build_list(
                value=['[]'],
                tail=['[]']),
                [])

    def test_multiple(self):
        """Tests setting multiple values on a port"""
        # Multiple values on 'head'
        self.assertEqual(self.build_list(
                head=["a", "b"]),
                ["a", "b"])
        self.assertEqual(self.build_list(
                head=["a", "b"],
                value=['["c", "d"]']),
                ["a", "b", "c", "d"])

        # Multiple values on 'value'
        res = self.build_list(value=['["a", "b"]', '["c", "d"]'])
        # Connections of List type are merged
        self.assertEqual(res, ["a", "b", "c", "d"])

    def test_items(self):
        """Tests the multiple 'itemN' ports"""
        from vistrails.tests.utils import execute, intercept_result
        def list_with_items(nb_items, **kwargs):
            with intercept_result(List, 'value') as results:
                errors = execute([
                        ('List', 'org.vistrails.vistrails.basic', [
                            (k, [('String', v)])
                            for k, v in kwargs.iteritems()
                        ]),
                    ],
                    add_port_specs=[
                        (0, 'input', 'item%d' % i,
                         '(org.vistrails.vistrails.basic:Module)')
                        for i in xrange(nb_items)
                    ])
                if errors:
                    return None
            return results[-1]

        self.assertEqual(
                list_with_items(2, head="one", item0="two", item1="three"),
                ["one", "two", "three"])

        # All 'itemN' ports have to be set
        self.assertIsNone(
                list_with_items(3, head="one", item0="two", item2="three"))


class TestPythonSource(unittest.TestCase):
    def test_simple(self):
        """A simple PythonSource returning a string"""
        import urllib2
        from vistrails.tests.utils import execute, intercept_result
        source = 'customout = "nb is %d" % customin'
        source = urllib2.quote(source)
        with intercept_result(PythonSource, 'customout') as results:
            self.assertFalse(execute([
                    ('PythonSource', 'org.vistrails.vistrails.basic', [
                        ('source', [('String', source)]),
                        ('customin', [('Integer', '42')])
                    ]),
                    ('String', 'org.vistrails.vistrails.basic', []),
                ],
                [
                    (0, 'customout', 1, 'value'),
                ],
                add_port_specs=[
                    (0, 'input', 'customin',
                     'org.vistrails.vistrails.basic:Integer'),
                    (0, 'output', 'customout',
                     'org.vistrails.vistrails.basic:String'),
                ]))
        self.assertEqual(results[-1], "nb is 42")


class TestNumericConversions(unittest.TestCase):
    def test_full(self):
        from vistrails.tests.utils import execute, intercept_result
        with intercept_result(Round, 'out_value') as results:
            self.assertFalse(execute([
                    ('Integer', 'org.vistrails.vistrails.basic', [
                        ('value', [('Integer', '5')])
                    ]),
                    ('Float', 'org.vistrails.vistrails.basic', []),
                    ('PythonCalc', 'org.vistrails.vistrails.pythoncalc', [
                        ('value2', [('Float', '2.7')]),
                        ('op', [('String', '+')]),
                    ]),
                    ('Round', 'org.vistrails.vistrails.basic', [
                        ('floor', [('Boolean', 'True')]),
                    ]),
                ],
                [
                    (0, 'value', 1, 'value'),
                    (1, 'value', 2, 'value1'),
                    (2, 'value', 3, 'in_value'),
                ]))
        self.assertEqual(results, [7])


class TestUnzip(unittest.TestCase):
    def test_unzip_file(self):
        from vistrails.tests.utils import execute, intercept_result
        from vistrails.core.system import vistrails_root_directory
        zipfile = os.path.join(vistrails_root_directory(),
                               'tests', 'resources',
                               'test_archive.zip')
        with intercept_result(Unzip, 'file') as outfiles:
            self.assertFalse(execute([
                    ('Unzip', 'org.vistrails.vistrails.basic', [
                        ('archive_file', [('File', zipfile)]),
                        ('filename_in_archive', [('String', 'file1.txt')]),
                    ]),
                ]))
        self.assertEqual(len(outfiles), 1)
        with open(outfiles[0].name, 'rb') as outfile:
            self.assertEqual(outfile.read(), "some random\ncontent")

    def test_unzip_all(self):
        from vistrails.tests.utils import execute, intercept_result
        from vistrails.core.system import vistrails_root_directory
        zipfile = os.path.join(vistrails_root_directory(),
                               'tests', 'resources',
                               'test_archive.zip')
        with intercept_result(UnzipDirectory, 'directory') as outdir:
            self.assertFalse(execute([
                    ('UnzipDirectory', 'org.vistrails.vistrails.basic', [
                        ('archive_file', [('File', zipfile)]),
                    ]),
                ]))
        self.assertEqual(len(outdir), 1)

        self.assertEqual(
                [(d, f) for p, d, f in os.walk(outdir[0].name)],
                [(['subdir'], ['file1.txt']),
                 ([], ['file2.txt'])])


from vistrails.core.configuration import get_vistrails_configuration

class TestTypechecking(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        conf = get_vistrails_configuration()
        cls.error_all = conf.showConnectionErrors
        cls.error_variant = conf.showVariantErrors

    @classmethod
    def tearDownClass(cls):
        conf = get_vistrails_configuration()
        conf.showConnectionErrors = cls.error_all
        conf.showVariantErrors = cls.error_variant

    @staticmethod
    def set_settings(error_all, error_variant):
        conf = get_vistrails_configuration()
        conf.showConnectionErrors = error_all
        conf.showVariantErrors = error_variant

    def run_test_pipeline(self, result, expected_results, *args, **kwargs):
        from vistrails.tests.utils import execute, intercept_result
        for error_all, error_variant, expected in expected_results:
            self.set_settings(error_all, error_variant)
            with intercept_result(*result) as results:
                error = execute(*args, **kwargs)
            if not expected:
                self.assertTrue(error)
            else:
                self.assertFalse(error)
                self.assertEqual(results, expected)

    def test_basic(self):
        import urllib2
        # Base case: no typing error
        # This should succeed in every case
        self.run_test_pipeline(
            (PythonSource, 'r'),
            [(False, False, ["test"]),
             (True, True, ["test"])],
            [
                ('PythonSource', 'org.vistrails.vistrails.basic', [
                    ('source', [('String', urllib2.quote('o = "test"'))]),
                ]),
                ('PythonSource', 'org.vistrails.vistrails.basic', [
                    ('source', [('String', urllib2.quote('r = i'))])
                ]),
            ],
            [
                (0, 'o', 1, 'i'),
            ],
            add_port_specs=[
                (0, 'output', 'o',
                 'org.vistrails.vistrails.basic:String'),
                (1, 'input', 'i',
                 'org.vistrails.vistrails.basic:String'),
                (1, 'output', 'r',
                 'org.vistrails.vistrails.basic:String')
            ])

    def test_fake(self):
        import urllib2
        # A module is lying, declaring a String but returning an int
        # This should fail with showConnectionErrors=True (not the
        # default)
        self.run_test_pipeline(
            (PythonSource, 'r'),
            [(False, False, [42]),
             (False, True, [42]),
             (True, True, False)],
            [
                ('PythonSource', 'org.vistrails.vistrails.basic', [
                    ('source', [('String', urllib2.quote('o = 42'))]),
                ]),
                ('PythonSource', 'org.vistrails.vistrails.basic', [
                    ('source', [('String', urllib2.quote('r = i'))])
                ]),
            ],
            [
                (0, 'o', 1, 'i'),
            ],
            add_port_specs=[
                (0, 'output', 'o',
                 'org.vistrails.vistrails.basic:String'),
                (1, 'input', 'i',
                 'org.vistrails.vistrails.basic:String'),
                (1, 'output', 'r',
                 'org.vistrails.vistrails.basic:String')
            ])

    def test_inputport(self):
        import urllib2
        # This test uses an InputPort module, whose output port should not be
        # considered a Variant port (although it is)
        self.run_test_pipeline(
            (PythonSource, 'r'),
            [(False, False, [42]),
             (False, True, [42]),
             (True, True, [42])],
            [
                ('InputPort', 'org.vistrails.vistrails.basic', [
                    ('ExternalPipe', [('Integer', '42')]),
                ]),
                ('PythonSource', 'org.vistrails.vistrails.basic', [
                    ('source', [('String', urllib2.quote('r = i'))])
                ]),
            ],
            [
                (0, 'InternalPipe', 1, 'i'),
            ],
            add_port_specs=[
                (1, 'input', 'i',
                 'org.vistrails.vistrails.basic:String'),
                (1, 'output', 'r',
                 'org.vistrails.vistrails.basic:String'),
            ])


class TestStringFormat(unittest.TestCase):
    def test_list_placeholders(self):
        fmt = 'a {} b}} {c!s} {{d e}} {}f'
        self.assertEqual(StringFormat.list_placeholders(fmt),
                         (2, set(['c'])))

    def run_format(self, fmt, expected, **kwargs):
        from vistrails.tests.utils import execute, intercept_result
        functions = [('format', [('String', fmt)])]
        functions.extend((n, [(t, v)])
                         for n, (t, v) in kwargs.iteritems())
        with intercept_result(StringFormat, 'value') as results:
            self.assertFalse(execute([
                    ('StringFormat', 'org.vistrails.vistrails.basic',
                     functions),
                ],
                add_port_specs=[
                    (0, 'input', n, t)
                    for n, (t, v) in kwargs.iteritems()
                ]))
        self.assertEqual(results, [expected])

    def test_format(self):
        self.run_format('{{ {a} }} b {c!s}', '{ 42 } b 12',
                        a=('Integer', '42'),
                        c=('Integer', '12'))

    # Python 2.6 doesn't support {}
    @unittest.skipIf(sys.version_info < (2, 7), "No {} support on 2.6")
    def test_format_27(self):
        self.run_format('{} {}', 'a b',
                        _0=('String', 'a'), _1=('String', 'b'))
        self.run_format('{{ {a} {} {b!s}', '{ 42 b 12',
                        a=('Integer', '42'), _0=('String', 'b'),
                        b=('Integer', '12'))
        self.run_format('{} {} {!r}{ponc} {:.2f}', "hello dear 'world'! 1.33",
                        _0=('String', 'hello'), _1=('String', 'dear'),
                        _2=('String', 'world'), _3=('Float', '1.333333333'),
                        ponc=('String', '!'))


class TestConstantMetaclass(unittest.TestCase):
    def test_meta(self):
        """Tests the __metaclass__ for Constant.
        """
        mod1_in = [('value', 'basic:String'), IPort('other', 'basic:Float')]
        mod1_out = [('someport', 'basic:Integer')]
        class Mod1(Constant):
            _input_ports = mod1_in
            _output_ports = mod1_out
        self.assertEqual(Mod1._input_ports, mod1_in)
        self.assertEqual(Mod1._output_ports, [('value', Mod1)] + mod1_out)

        mod2_in = [('another', 'basic:String')]
        class Mod2(Mod1):
            _input_ports = mod2_in
        self.assertEqual(Mod2._input_ports, [('value', Mod2)] + mod2_in)
        self.assertEqual(Mod2._output_ports, [('value', Mod2)])

        class Mod3(Mod1):
            _output_ports = []
        self.assertEqual(Mod3._input_ports, [('value', Mod3)])
        self.assertEqual(Mod3._output_ports, [('value', Mod3)])
