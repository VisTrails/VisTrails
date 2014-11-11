import ast
import copy
import os
import sys
import unittest

from vistrails.core.configuration import ConfigurationObject, ConfigField, ConfigPath, ConfigURL, get_vistrails_persistent_configuration, get_vistrails_temp_configuration
from vistrails.core.modules.vistrails_module import Module, NotCacheable, ModuleError
from vistrails.core.modules.config import IPort, OPort, ModuleSettings
import vistrails.core.system

class OutputMode(object):
    mode_type = None
    priority = -1

    @classmethod
    def can_compute(cls):
        return False

    def compute_output(self, output_module, configuration=None):
        raise NotImplementedError("Subclass of OutputMode should implement "
                                  "this")

# Ideally, these are globally and locally configurable so that we use
# global settings if nothing is set locally (e.g. output directory)
class OutputModeConfig(dict):
    mode_type = None
    _fields = []
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        for k, v in self.iteritems():
            if not self.has_field(k):
                raise ValueError('Field "%s" is not declared for class "%s"' %
                                 (k, self.__class__.__name__))

    @classmethod
    def ensure_field_dict(cls):
        if '_field_dict' not in cls.__dict__:
            if '_fields' in cls.__dict__:
                cls._field_dict = dict((f.name, f) for f in cls._fields)
            else:
                cls._field_dict = {}

    @classmethod
    def has_field(cls, k):
        cls_list = [cls]
        while len(cls_list) > 0:
            c = cls_list.pop(0)
            if issubclass(c, OutputModeConfig):
                c.ensure_field_dict()
                if k in c._field_dict:
                    return True
                cls_list.extend(c.__bases__)
        return False
            
    @classmethod
    def get_field(cls, k):
        cls_list = [cls]
        while len(cls_list) > 0:
            c = cls_list.pop(0)
            if issubclass(c, OutputModeConfig):
                c.ensure_field_dict()
                if k in c._field_dict:
                    return c._field_dict[k]
                cls_list.extend(c.__bases__)
        return None

    @classmethod
    def get_all_fields(cls):
        field_dicts = []
        cls_list = [cls]
        while len(cls_list) > 0:
            c = cls_list.pop(0)
            if issubclass(c, OutputModeConfig):
                c.ensure_field_dict()
                field_dicts.append(c._field_dict)
                cls_list.extend(c.__bases__)
        field_dict = {}
        for fd in reversed(field_dicts):
            field_dict.update(fd)
        fields = field_dict.values()
        fields.sort()
        return fields

    @classmethod
    def get_default(cls, k):
        f = cls.get_field(k)
        if f is not None:
            return f.default_val
        return None

    @classmethod
    def has_from_config(cls, config, k):
        if hasattr(cls, 'mode_type'):
            mode_type = cls.mode_type
            if config.has(mode_type):
                subconfig = getattr(config, mode_type)
                if subconfig.has(k):
                    return True
        return False

    @classmethod
    def get_from_config(cls, config, k):
        if hasattr(cls, 'mode_type'):
            mode_type = cls.mode_type
            if config.has(mode_type):
                subconfig = getattr(config, mode_type)
                if subconfig.has(k):
                    return getattr(subconfig, k)
        return None

    @classmethod
    def has_override(cls, k):
        config = get_vistrails_temp_configuration().outputSettings
        return cls.has_from_config(config, k)

    @classmethod
    def get_override(cls, k):
        config = get_vistrails_temp_configuration().outputSettings
        str_val = cls.get_from_config(config, k)
        return cls.get_field(k).from_string(str_val)

    @classmethod
    def has_global_setting(cls, k):
        config = get_vistrails_persistent_configuration().outputDefaultSettings
        return cls.has_from_config(config, k)

    @classmethod
    def get_global_setting(cls, k):
        config = get_vistrails_persistent_configuration().outputDefaultSettings
        return cls.get_from_config(config, k)

    @classmethod
    def has_config_setting(cls, k):
        return cls.has_override(k) or cls.has_global_setting(k)

    def __setitem__(self, k, v):
        if not self.has_field(k):
            raise ValueError('Setting "%s" is not declared for class "%s"' %
                             (k, self.__class__.__name__))
        dict.__setitem__(self, k, v)

    def __getitem__(self, k):
        if self.has_override(k):
            return self.get_override(k)
        try:
            return dict.__getitem__(self, k)
        except KeyError, e:
            if self.has_global_setting(k):
                return self.get_global_setting(k)
            else:
                if self.has_field(k):
                    return self.get_default(k)
            raise e

    def __hasitem__(self, k):
        return (self.has_field(k) or dict.__hasitem__(self, k) or 
                self.has_override(k) or self.has_global_setting(k))

class OutputModule(NotCacheable, Module):
    _input_ports = [IPort('value', "Variant"),
                    IPort('mode_type', "String"),
                    IPort('configuration', "Dictionary")]
    _settings = ModuleSettings(abstract=True)

    # configuration is a dictionary of dictionaries where root-level
    # keys are mode_types and the inner dictionaries are
    # workflow-specific settings

    # want to have mode inheritance here...

    @classmethod
    def ensure_mode_dict(cls):
        if '_output_modes_dict' not in cls.__dict__:
            if '_output_modes' in cls.__dict__:
                cls._output_modes_dict = \
                                dict((mcls.mode_type, (mcls, mcls.priority))
                                     for mcls in cls._output_modes)
            else:
                cls._output_modes_dict = {}
            
    @classmethod
    def register_output_mode(cls, mode_cls, priority=None):
        if mode_cls.mode_type is None:
            raise ValueError("mode_cls.mode_type must not be None")
        if priority is None:
            priority = mode_cls.priority
        cls.ensure_mode_dict()
        if '_output_modes' not in cls.__dict__:
            cls._output_modes = []
        cls._output_modes.append(mode_cls)
        cls._output_modes_dict[mode_cls.mode_type] = (mode_cls, priority)

    @classmethod
    def set_mode_priority(cls, mode_type, priority):
        cls.ensure_mode_dict()

        if mode_type not in cls._output_modes_dict:
            raise ValueError('mode_type "%s" is not set for this module' % 
                             mode_type)
        cls._output_modes_dict[mode_type][1] = priority

    @classmethod
    def get_mode_class(cls, mode_type):
        cls_list = [cls]
        while len(cls_list) > 0:
            c = cls_list.pop(0)
            if issubclass(c, OutputModule):
                c.ensure_mode_dict()
                if mode_type in c._output_modes_dict:
                    return c._output_modes_dict[mode_type][0]
                cls_list.extend(c.__bases__)
        return None

    @classmethod
    def get_sorted_mode_list(cls):
        cls_list = [cls]
        idx = 0
        while idx < len(cls_list):
            for c in cls_list[idx].__bases__:
                if issubclass(c, OutputModule):
                    c.ensure_mode_dict()
                    cls_list.append(c)
            idx += 1

        mode_dict = {}
        for c in reversed(cls_list):
            mode_dict.update(c._output_modes_dict)
        mode_list = [c for c, _ in reversed(sorted(mode_dict.itervalues(), 
                                                   key=lambda x: x[1]))]
        return mode_list

    @classmethod
    def get_mode_tree(cls):
        cls_list = [cls]
        idx = 0
        while idx < len(cls_list):
            for c in cls_list[idx].__bases__:
                if issubclass(c, OutputModule):
                    c.ensure_mode_dict()
                    cls_list.append(c)
            idx += 1

        mode_tree = {}
        for c in reversed(cls_list):
            c.ensure_mode_dict()

    def get_mode_config(self, mode_cls):
        mode_config_cls = mode_cls.config_cls
        mode_config_dict = {}
        configuration = self.force_get_input('configuration')
        if configuration is not None:
            # want to search through all mode classes in case we have
            # base class settings that should trump
            cls_list = [mode_config_cls]
            mode_config_cls_list = []
            while len(cls_list) > 0:
                c = cls_list.pop(0)
                if issubclass(c, OutputModeConfig):
                    mode_config_cls_list.append(c)
                    cls_list.extend(c.__bases__)
            mode_config_cls_list.reverse()

            for mode_config_cls in mode_config_cls_list:
                for k, v in configuration.iteritems():
                    if k == mode_config_cls.mode_type:
                        mode_config_dict.update(v)
        mode_config = mode_config_cls(mode_config_dict)
        return mode_config

    def compute(self):
        mode_cls = None
        self.ensure_mode_dict()
        if self.has_input("mode_type"):
            # use user-specified mode_type
            mode_type = self.get_input("mode_type")
            mode_cls = self.get_mode_class(mode_type)
            if mode_cls is None:
                raise ModuleError(self, 'Cannot output in mode "%s" because '
                                  'that mode has not been defined' % mode_type)
        else:
            # FIXME should have user-setable priorities!

            # determine mode_type based on registered modes by priority,
            # checking if each is possible
            for mcls in self.get_sorted_mode_list():
                if mcls.can_compute():
                    mode_cls = mcls
                    break

        if mode_cls is None:
            raise ModuleError(self, "No output mode is valid, output cannot "
                              "be generated")

        mode_config = self.get_mode_config(mode_cls)
        mode = mode_cls()
        self.annotate({"output_mode": mode.mode_type})
        mode.compute_output(self, mode_config)
                
class StdoutModeConfig(OutputModeConfig):
    mode_type = "stdout"
    _fields = []

class StdoutMode(OutputMode):
    mode_type = "stdout"
    priority = 2
    config_cls = StdoutModeConfig

    @classmethod
    def can_compute(cls):
        return True

class FileModeConfig(OutputModeConfig):
    mode_type = "file"
    _fields = [ConfigField('file', None, ConfigPath),
               ConfigField('basename', None, str),
               ConfigField('prefix', None, str),
               ConfigField('suffix', None, str),
               ConfigField('dir', None, ConfigPath),
               ConfigField('series', False, bool),
               ConfigField('overwrite', True, bool),
               ConfigField('seriesPadding', 3, int),
               ConfigField('seriesStart', 0, int),
               ConfigField('format', None, str)]

class FileMode(OutputMode):
    mode_type = "file"
    priority = 1
    config_cls = FileModeConfig
    formats = []
    
    # need to reset this after each execution!
    series_next = 0

    @classmethod
    def can_compute(cls):
        return True

    @classmethod
    def get_formats(cls):
        formats = []
        cls_list = [cls]
        while len(cls_list) > 0:
            c = cls_list.pop(0)
            if issubclass(c, FileMode):
                if 'formats' in c.__dict__:
                    return c.formats
                cls_list.extend(c.__bases__)
        return []

    def get_format(self, configuration=None):
        format_map = {'png': 'png',
                      'jpeg': 'jpg',
                      'jpg': 'jpg',
                      'tif': 'tif',
                      'tiff': 'tif'}
        if configuration is not None and 'format' in configuration:
            conf_format = configuration['format']
            if conf_format.lower() in format_map:
                return format_map[conf_format.lower()]
            return conf_format

        # default is the first listed if it exists
        format_list = self.get_formats()
        if len(format_list) > 0:
            return format_list[0]
        return None

    def get_series_num(self):
        retval = FileMode.series_next 
        FileMode.series_next += 1
        return retval
        
    # FIXME should add format into this computation
    def get_filename(self, configuration, full_path=None, filename=None,
                     dirname=None, basename=None, prefix=None, suffix=None,
                     overwrite=True, series=False, series_padding=3):
        # if prefix/suffix/series are overridden, want to use them
        # instead of name...
        if full_path is None:
            # use file if overridden or none of the file params are
            # overridden and the file is not None

            overwrite = configuration['overwrite']
            if (configuration.has_override('file') or
                (not (configuration.has_override('basename') or
                      configuration.has_override('prefix') or
                      configuration.has_override('suffix') or
                      configuration.has_override('dir') or
                      configuration.has_override('series') or
                      configuration.has_override('seriesPadding') or
                      configuration.has_override('seriesStart')) and
                 'file' in configuration and
                 configuration['file'] is not None)):
                full_path = configuration['file']
            else:
                if configuration['basename'] is not None:
                    basename = configuration['basename']
                if configuration['prefix'] is not None:
                    prefix = configuration['prefix']
                if configuration['suffix'] is not None:
                    suffix = configuration['suffix']
                if configuration['dir'] is not None:
                    dirname = configuration['dir']
                if configuration['series'] is not None:
                    series = configuration['series']
                if configuration['seriesPadding'] is not None:
                    series_padding = configuration['seriesPadding']

        if full_path is None:                
            # should any of these necessitate series=True?
            if basename is None:
                basename = 'vt_out'
            if prefix is None:
                prefix = ''
            if suffix is None:
                suffix = ''
            if dirname is None:
                # FIXME should unify with VisTrails output
                # directory global!  should check for abspath (if
                # not, use relative to global output directory)
                dirname = ''

            # seriesPadding and series have defaults so no
            # need to default them

            if not overwrite and series:
                # need to find first open slot
                full_path = None
                while full_path is None or os.path.exists(full_path):
                    series_str = (("%%0%dd" % series_padding) % 
                                  self.get_series_num())
                    full_path = os.path.join(dirname, "%s%s%s%s" % 
                                             (prefix, basename, 
                                              series_str, suffix))
            else:
                if series:
                    series_str = (("%%0%dd" % series_padding) % 
                                  self.get_series_num())
                else:
                    series_str = ""
                full_path = os.path.join(dirname, "%s%s%s%s" % 
                                         (prefix, basename, series_str, 
                                          suffix))
            if not overwrite and os.path.exists(full_path):
                raise IOError('File "%s" exists and overwrite is False' % full_path)

        return full_path
        
class FileToFileMode(FileMode):
    def compute_output(self, output_module, configuration=None):
        old_fname = output_module.get_input('value').name
        full_path = self.get_filename(configuration)
        # we know we are in overwrite mode because it would have been
        # flagged otherwise
        if os.path.exists(full_path):
            try:
                os.remove(full_path)
            except OSError, e:
                raise ModuleError(output_module, 
                                  ('Could not delete existing '
                                   'path "%s"' % full_path))
        try:
            vistrails.core.system.link_or_copy(old_fname, full_path)
        except OSError, e:
            msg = "Could not create file '%s': %s" % (full_path, e)
            raise ModuleError(output_module, msg)

class FileToStdoutMode(StdoutMode):
    def compute_output(self, output_module, configuration=None):
        fname = output_module.get_input('value').name
        with open(fname, 'r') as f:
            for line in f:
                sys.stdout.write(line)

class GenericToStdoutMode(StdoutMode):
    def compute_output(self, output_module, configuration=None):
        value = output_module.get_input('value')
        print >>sys.stdout, value

class GenericToFileMode(FileMode):
    def compute_output(self, output_module, configuration=None):
        value = output_module.get_input('value')
        filename = self.get_filename(configuration)
        with open(filename, 'w') as f:
            print >>f, value

class GenericOutput(OutputModule):
    _settings = ModuleSettings(configure_widget="vistrails.gui.modules.output_configuration:OutputModuleConfigurationWidget")
    _output_modes = [GenericToStdoutMode, GenericToFileMode]

class FileOutput(OutputModule):
    _settings = ModuleSettings(configure_widget="vistrails.gui.modules.output_configuration:OutputModuleConfigurationWidget")
    # should set file as a higher priority here...
    _input_ports = [('value', 'File')]
    _output_modes = [FileToStdoutMode, FileToFileMode]

class ImageFileModeConfig(FileModeConfig):
    mode_type = "imageFile"
    _fields = [ConfigField('width', 800, int),
               ConfigField('height', 600, int)]

class ImageFileMode(FileMode):
    config_cls = ImageFileModeConfig
    mode_type = "imageFile"

class RichTextOutput(OutputModule):
    _settings = ModuleSettings(configure_widget="vistrails.gui.modules.output_configuration:OutputModuleConfigurationWidget")
    # need specific spreadsheet richtext mode here
    pass

_modules = [OutputModule, GenericOutput, FileOutput]

# need to put WebOutput, ImageOutput, RichTextOutput, SVGOutput, etc. elsewhere

class TestOutputModeConfig(unittest.TestCase):
    def test_fields(self):
        class AlteredFileModeConfig(FileModeConfig):
            _fields = [ConfigField("newattr", 3, int)]
            
        self.assertTrue(AlteredFileModeConfig.has_field("overwrite"))
        self.assertTrue(AlteredFileModeConfig.has_field("newattr"))

    def test_config(self):
        config_obj = ConfigurationObject(file=ConfigurationObject(seriesStart=5))
        self.assertTrue(FileModeConfig.has_from_config(config_obj, 
                                                       "seriesStart"))
        self.assertEqual(FileModeConfig.get_from_config(config_obj, 
                                                        "seriesStart"), 5)
        
    def test_subclass_config(self):
        class AlteredFileModeConfig(FileModeConfig):
            mode_type = "file"
            _fields = [ConfigField("newattr", 3, int)]
        config_obj = ConfigurationObject(file=ConfigurationObject(seriesStart=5))
        self.assertEqual(AlteredFileModeConfig.get_from_config(config_obj, 
                                                        "seriesStart"), 5)

    def test_get_item(self):
        config = FileModeConfig()
        self.assertEqual(config["seriesStart"], 0)        

    def test_get_default(self):
        self.assertEqual(FileModeConfig.get_default("seriesStart"), 0)

if __name__ == '__main__':
    import vistrails.core.application
    app = vistrails.core.application.init()
    unittest.main()
