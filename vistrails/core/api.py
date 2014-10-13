import contextlib
import warnings

import vistrails.core.application
import vistrails.core.db.action
import vistrails.core.db.io
from vistrails.core.db.locator import UntitledLocator, FileLocator
from vistrails.core.interpreter.default import get_default_interpreter
from vistrails.core.modules.module_registry import get_module_registry
from vistrails.core.modules.package import Package as _Package
from vistrails.core.packagemanager import get_package_manager
from vistrails.core.utils import DummyView
from vistrails.core.vistrail.controller import VistrailController
from vistrails.core.vistrail.pipeline import Pipeline as _Pipeline
from vistrails.core.vistrail.vistrail import Vistrail as _Vistrail


__all__ = ['Vistrail', 'Pipeline', 'Module', 'Package',
           'ExecutionResults', 'ExecutionErrors', 'Function',
           'load_vistrail', 'load_pipeline', 'load_package',
           'output_mode', 'run_vistrail',
           'NoSuchVersion', 'NoSuchPackage']


class NoSuchVersion(KeyError):
    """The version number or tag you specified doesn't exist in the vistrail.
    """


class NoSuchPackage(ValueError):
    """Couldn't find a package with the given identifier.
    """


is_initialized = False
_application = None


def initialize():
    """Initializes VisTrails.

    You don't have to call this directly. Initialization will happen when you
    start using the API.
    """
    global is_initialized
    global _application

    if is_initialized:
        return False

    # Creates a core application
    _application = vistrails.core.application.init(
            options_dict={
                'installBundles': False,
                'loadPackages': False,
                'enablePackagesSilently': True},
            args=[])

    is_initialized = True

    return True


class Vistrail(object):
    """This class wraps both Vistrail and VistrailController.

    From it, you can get any pipeline from a tag name or version number.

    It has a concept of "current version", from which you can create new
    versions by performing actions.
    """
    _current_pipeline = None

    def __init__(self, arg=None):
        initialize()
        if arg is None:
            # Copied from VistrailsApplicationInterface#open_vistrail()
            locator = UntitledLocator()
            loaded_objs = vistrails.core.db.io.load_vistrail(locator)
            self.controller = VistrailController(*loaded_objs)
        elif isinstance(arg, (_Pipeline, Pipeline)):
            if isinstance(arg, Pipeline):
                pipeline = arg.pipeline
            else:
                pipeline = arg
            # Copied from VistrailsApplicationInterface#open_workflow()
            vistrail = _Vistrail()
            ops = []
            for module in pipeline.module_list:
                ops.append(('add', module))
            for connection in pipeline.connection_list:
                ops.append(('add', connection))
            action = vistrails.core.db.action.create_action(ops)
            vistrail.add_action(action, 0L)
            vistrail.update_id_scope()
            vistrail.change_description("Imported pipeline", 0L)
            self.controller = VistrailController(vistrail, UntitledLocator())
        elif isinstance(arg, VistrailController):
            self.controller = arg
        elif isinstance(arg, basestring):
            raise TypeError("Vistrail was constructed from %r.\n"
                            "Use load_vistrail() to get a Vistrail from a "
                            "file." % type(arg).__name__)
        else:
            raise TypeError("Vistrail was constructed from unexpected "
                            "argument type %r" % type(arg).__name__)

    def get_pipeline(self, version):
        """Returns a pipeline from a version number of tag.

        This does not change the currently selected version in this Vistrail.
        """
        vistrail = self.controller.vistrail
        if isinstance(version, (int, long)):
            if not vistrail.db_has_action_with_id(version):
                raise NoSuchVersion("Vistrail doesn't have a version %r" %
                                    version)
            return Pipeline(vistrail.getPipelineVersionNumber(version))
        elif isinstance(version, basestring):
            if not vistrail.has_tag_str(version):
                raise NoSuchVersion("Vistrail doesn't have a tag %r" % version)
            return Pipeline(vistrail.getPipelineVersionName(version))
        else:
            raise TypeError("get_pipeline() argument must be a string or "
                            "integer, not %r" % type(version).__name__)

    def select_version(self, version):
        """Sets a different version as current.

        The current workflow is accessible via current_workflow; it is the one
        that gets executed when calling execute(), and the version from which
        new versions are created if you perform actions.
        """
        vistrail = self.controller.vistrail
        if isinstance(version, (int, long)):
            if not vistrail.db_has_action_with_id(version):
                raise NoSuchVersion("Vistrail doesn't have a version %r" %
                                    version)
        elif (isinstance(version, basestring)):
            if not vistrail.has_tag_str(version):
                raise NoSuchVersion("Vistrail doesn't have a tag %r" % version)
        else:
            raise TypeError("set_current_pipeline() argument must be a string "
                            "or integer, not %r" % type(version).__name__)
        self.controller.change_selected_version(version)
        self._current_pipeline = None

    def select_latest_version(self):
        """Sets the most recent version in the vistrail as current.
        """
        self.controller.select_latest_version()
        self._current_pipeline = None

    @property
    def current_pipeline(self):
        if self._current_pipeline is None:
            self._current_pipeline = Pipeline(
                    self.controller.current_pipeline,
                    vistrail=(self, self.current_version))
        return self._current_pipeline

    @property
    def current_version(self):
        return self.controller.current_version

    def set_tag(self, *args):
        """Sets a tag for the current or specified version.
        """
        if len(args) == 1:
            version, (tag,) = self.controller.current_version, args
        elif len(args) == 2:
            version, tag = args
        else:
            raise TypeError("set_tag() takes 1 or 2 arguments (%r given)" %
                            len(args))
        if isinstance(version, (int, long)):
            if not self.controller.vistrail.db_has_action_with_id(version):
                raise NoSuchVersion("Vistrail doesn't have a version %r" %
                                    version)
        elif isinstance(version, basestring):
            if not self.controller.vistrail.has_tag_str(version):
                raise NoSuchVersion("Vistrail doesn't have a tag %r" % version)
        else:
            raise TypeError("set_tag() expects the version to be a string or "
                            "integer, not %r" % type(version).__name__)
        self.controller.vistrail.set_tag(version, tag)

    def tag(self, tag):
        """Sets a tag for the current version.
        """
        self.set_tag(tag)

    def execute(self, *args, **kwargs):
        """Executes the current workflow.
        """
        return self.current_pipeline.execute(*args, **kwargs)

    @property
    def changed(self):
        return self.controller.changed

    # TODO : vistrail modification methods

    def __repr__(self):
        version_nb = self.controller.current_version
        if self.controller.vistrail.has_tag(version_nb):
            version = "%s (tag %s)" % (
                    version_nb,
                    self.controller.vistrail.get_tag(version_nb))
        else:
            version = version_nb
        return "<%s: %s, version %s, %s>" % (
                self.__class__.__name__,
                self.controller.name,
                version,
                ('not changed', 'changed')[self.controller.changed])


def get_inputoutput_name(module):
    for function in module.functions:
        if function.name == 'name':
            if len(function.params) == 1:
                return function.params[0].strValue
    return None


class Pipeline(object):
    """This class represents a single Pipeline.

    It doesn't have a controller.
    """
    vistrail = None
    version = None
    _inputs = None
    _outputs = None

    def __init__(self, pipeline=None, vistrail=None):
        initialize()
        if pipeline is None:
            self.pipeline = _Pipeline()
        elif isinstance(pipeline, _Pipeline):
            self.pipeline = pipeline
        elif isinstance(pipeline, basestring):
            raise TypeError("Pipeline was constructed from %r.\n"
                            "Use load_pipeline() to get a Pipeline from a "
                            "file." % type(pipeline).__name__)
        else:
            raise TypeError("Pipeline was constructed from unexpected "
                            "argument type %r" % type(pipeline).__name__)
        if vistrail is not None:
            if (isinstance(vistrail, tuple) and len(vistrail) == 2 and
                    isinstance(vistrail[0], Vistrail)):
                self.vistrail, self.version = vistrail
            else:
                raise TypeError("Pipeline got unknown type %r as 'vistrail' "
                                "argument" % type(vistrail).__name__)

    @property
    def modules(self):
        for module in self.pipeline.module_list:
            yield Module(descriptor=module.module_descriptor,
                         module_id=module.id,
                         pipeline=self)

    def execute(self, *args, **kwargs):
        """Execute the pipeline.

        Positional arguments are either input values (created from
        ``module == value``, where `module` is a Module from the pipeline and
        `value` is some value or Function instance) for the pipeline's
        InputPorts, or Module instances (to select sink modules).

        Keyword arguments are also used to set InputPort by looking up inputs
        by name.

        Example::

           input_bound = pipeline.get_input('higher_bound')
           input_url = pipeline.get_input('url')
           sinkmodule = pipeline.get_module(32)
           pipeline.execute(sinkmodule,
                            input_bound == vt.Function(Integer, 10),
                            input_url == 'http://www.vistrails.org/',
                            resolution=15)  # kwarg: only one equal sign
        """
        sinks = set()
        inputs = {}

        # Read args
        for arg in args:
            if isinstance(arg, ModuleValuePair):
                if arg.module.id in inputs:
                    raise ValueError(
                            "Multiple values set for InputPort %r" %
                            get_inputoutput_name(arg.module))
                inputs[arg.module.id] = arg
            elif isinstance(arg, Module):
                sinks.add(arg.module_id)

        # Read kwargs
        for key, value in kwargs.iteritems():
            key = self.get_input(key)  # Might raise KeyError
            if key.module.id in inputs:
                raise ValueError("Multiple values set for InputPort %r" %
                                 get_inputoutput_name(key.module))
            inputs[key.module.id] = value

        reason = "API pipeline execution"
        sinks = sinks or None

        if (not inputs and self.vistrail is not None and
                self.vistrail.current_version == self.version):
            controller = self.vistrail.controller
            results, changed = controller.execute_workflow_list([[
                    controller.locator,  # locator
                    self.version,  # version
                    self.pipeline,  # pipeline
                    DummyView(),  # view
                    None,  # custom_aliases
                    None,  # custom_params
                    reason,  # reason
                    sinks,  # sinks
                    None,  # extra_info
                    ]])
            result, = results
        else:
            if inputs:
                # TODO : set input
                warnings.warn("execute() does not yet support setting "
                              "input ports")

            interpreter = get_default_interpreter()
            result = interpreter.execute(self.pipeline,
                                         reason=reason,
                                         sinks=sinks)

        if result.errors:
            raise ExecutionErrors(self, result)
        else:
            return ExecutionResults(self, result)

    def get_module(self, module_id):
        if isinstance(module_id, (int, long)):  # module id
            module = self.pipeline.modules[module_id]
        elif isinstance(module_id, basestring):  # module name
            def desc(mod):
                if '__desc__' in mod.db_annotations_key_index:
                    return mod.get_annotation_by_key('__desc__').value
                else:
                    return None
            modules = [mod
                       for mod in self.pipeline.modules.itervalues()
                       if desc(mod) == module_id]
            if not modules:
                raise KeyError("No module with description %r" % module_id)
            elif len(modules) > 1:
                raise ValueError("Multiple modules with description %r" %
                                 module_id)
            else:
                module, = modules
        else:
            raise TypeError("get_module() expects a string or integer, not "
                            "%r" % type(module_id).__name__)
        return Module(descriptor=module.module_descriptor,
                      module_id=module.id,
                      pipeline=self)

    def _get_inputs_or_outputs(self, module_name):
        reg = get_module_registry()
        desc = reg.get_descriptor_by_name(
                'org.vistrails.vistrails.basic',
                module_name)
        modules = {}
        for module in self.pipeline.modules.itervalues():
            if module.module_descriptor is desc:
                name = get_inputoutput_name(module)
                if name is not None:
                    modules[name] = module
        return modules

    def get_input(self, name):
        try:
            module = self._get_inputs_or_outputs('InputPort')[name]
        except KeyError:
            raise KeyError("No InputPort module with name %r" % name)
        else:
            return Module(descriptor=module.module_descriptor,
                          module_id=module.id,
                          pipeline=self)

    def get_output(self, name):
        try:
            module = self._get_inputs_or_outputs('OutputPort')[name]
        except KeyError:
            raise KeyError("No OutputPort module with name %r" % name)
        else:
            return Module(descriptor=module.module_descriptor,
                          module_id=module.id,
                          pipeline=self)

    @property
    def inputs(self):
        if self._inputs is None:
            self._inputs = self._get_inputs_or_outputs('InputPort').keys()
        return self._inputs

    @property
    def outputs(self):
        if self._outputs is None:
            self._outputs = self._get_inputs_or_outputs('OutputPort').keys()
        return self._outputs

    def __repr__(self):
        desc = "<%s: %d modules, %d connections" % (
                self.__class__.__name__,
                len(self.pipeline.modules),
                len(self.pipeline.connections))
        inputs = self.inputs
        if inputs:
            desc += "; inputs: %s" % ", ".join(inputs)
        outputs = self.outputs
        if outputs:
            desc += "; outputs: %s" % ", ".join(outputs)
        return desc + ">"


class ModuleValuePair(object):
    """Internal object returned by Module == value expressions.
    """
    def __init__(self, module, value):
        self.module = module
        self.value = value


class Module(object):
    """Wrapper for a module, which can be in a Pipeline or not yet.
    """
    module_id = None
    pipeline = None

    def __init__(self, descriptor, **kwargs):
        self.descriptor = descriptor
        if 'module_id' and 'pipeline' in kwargs:
            self.module_id = kwargs.pop('module_id')
            self.pipeline = kwargs.pop('pipeline')
            if not (isinstance(self.module_id, (int, long)) and
                    isinstance(self.pipeline, Pipeline)):
                raise TypeError
        elif 'module_id' in kwargs or 'pipeline' in kwargs:
            raise TypeError("Module was given an id but no pipeline")

        if kwargs:
            raise TypeError("Module was given unexpected argument: %r" %
                            next(iter(kwargs)))

    def __repr__(self):
        desc = "<Module %r from %s" % (self.descriptor.name,
                                       self.descriptor.identifier)
        if self.module_id is not None:
            desc += ", id %d" % self.module_id
            if self.pipeline is not None:
                mod = self.pipeline.pipeline.modules[self.module_id]
                if '__desc__' in mod.db_annotations_key_index:
                    desc += (", label \"%s\"" %
                             mod.get_annotation_by_key('__desc__').value)
        return desc + ">"

    def __eq__(self, other):
        if isinstance(other, Module):
            if self.module_id is None:
                return other.module_id is None
            else:
                if other.module_id is None:
                    return False
                return (self.module_id == other.module_id and
                        self.pipeline == other.pipeline)
        else:
            return ModuleValuePair(self.module, other)


class ModuleNamespace(object):
    def __init__(self, identifier, namespace=''):
        self.identifier = identifier
        self._namespace = namespace
        self._namespaces = {}

    def __getattr__(self, name):
        if name in self._namespaces:
            return self._namespaces[name]
        else:
            return self[name]

    def __getitem__(self, name):
        name = name.rsplit('|', 1)
        if len(name) == 2:
            if self._namespace:
                namespace = self._namespace + '|' + name[0]
            else:
                namespace = name[0]
            name = name[1]
        else:
            name, = name
            namespace = self._namespace
        reg = get_module_registry()
        descr = reg.get_descriptor_by_name(self.identifier,
                                           name,
                                           namespace)
        return Module(descriptor=descr)

    def __repr__(self):
        return "<Namespace %s of package %s>" % (self._namespace,
                                                 self.identifier)


class Package(ModuleNamespace):
    """Wrapper for an enabled package.

    You can get modules from a Package using either the
    ``pkg['namespace|module']`` or ``pkg.namespace.module`` syntax.
    """
    def __init__(self, package):
        if not isinstance(package, _Package):
            raise TypeError("Can't construct a package from "
                            "%r" % type(package).__name__)
        ModuleNamespace.__init__(self, package.identifier)
        self._package = package

        # Builds namespaces
        for mod, namespaces in self._package.descriptors.iterkeys():
            if not namespaces:
                continue
            ns = self
            fullname = None
            for name in namespaces.split('|'):
                if fullname is not None:
                    fullname += '|' + name
                else:
                    fullname = name
                if name not in ns._namespaces:
                    ns_ = ns._namespaces[name] = ModuleNamespace(
                            self.identifier,
                            fullname)
                    ns = ns_
                else:
                    ns = ns._namespaces[name]

    def __repr__(self):
        return "<Package: %s, %d modules>" % (self.identifier,
                                              len(self._package.descriptors))

    def __eq__(self, other):
        return isinstance(other, Package) and self._package is other._package

    def __ne__(self, other):
        return not self == other


class ExecutionErrors(Exception):
    """Errors raised during a pipeline execution.
    """
    def __init__(self, pipeline, resultobj):
        self.pipeline = pipeline
        self._errors = resultobj.errors

    def __str__(self):
        return "Pipeline execution failed: %d error%s:\n%s" % (
                len(self._errors),
                's' if len(self._errors) >= 2 else '',
                '\n'.join('%d: %s' % p for p in self._errors.iteritems()))


class ExecutionResults(object):
    """Contains the results of a pipeline execution.
    """
    def __init__(self, pipeline, resultobj):
        self.pipeline = pipeline
        self._objects = resultobj.objects

    def output_port(self, output):
        """Gets the value passed to an OutputPort module with that name.
        """
        if isinstance(output, basestring):
            outputs = self.pipeline._get_inputs_or_outputs('OutputPort')
            module_id = outputs[output].id
        else:
            raise TypeError("output_port() expects a string, not %r" %
                            type(output).__name__)
        return self._objects[module_id].get_output('ExternalPipe')

    def module_output(self, module):
        """Gets all the output ports of a specified module.
        """
        if not isinstance(module, Module):
            module = self.pipeline.get_module(module)
        return self._objects[module.module_id].outputPorts

    def __repr__(self):
        return "<ExecutionResult: %d modules>" % len(self._objects)


class Function(object):
    """A function, essentially a value with an explicit module type.
    """
    # TODO : Function


def load_vistrail(filename, version=None):
    """Loads a Vistrail from a filename.
    """
    initialize()
    if not isinstance(filename, basestring):
        raise TypeError("load_vistrails() expects a filename, got %r" %
                        type(filename).__name__)

    locator = FileLocator(filename)
    # Copied from VistrailsApplicationInterface#open_vistrail()
    loaded_objs = vistrails.core.db.io.load_vistrail(locator)
    controller = VistrailController(loaded_objs[0], locator,
                                    *loaded_objs[1:])

    return Vistrail(controller)


def load_pipeline(filename):
    """Loads a single pipeline from a filename.
    """
    initialize()
    if not isinstance(filename, basestring):
        raise TypeError("load_vistrails() expects a filename, got %r" %
                        type(filename).__name__)

    # Copied from VistrailsApplicationInterface#open_workflow()
    locator = FileLocator(filename)
    pipeline = locator.load(_Pipeline)

    return Pipeline(pipeline)


# TODO : provide a shortcut for basic_modules
def load_package(identifier, autoload=True):
    """Gets a package by identifier, enabling it if necessary.
    """
    initialize()
    pm = get_package_manager()
    pkg = pm.identifier_is_available(identifier)
    if pm.has_package(identifier):
        return Package(pkg)
    elif pkg is None:
        raise NoSuchPackage("Package %r not found" % identifier)

    # Copied from VistrailController#try_to_enable_package()
    dep_graph = pm.build_dependency_graph([identifier])
    deps = pm.get_ordered_dependencies(dep_graph)
    for pkg_id in deps:
        if not do_enable_package(pm, pkg_id):
            raise NoSuchPackage("Package %r not found" % pkg_id)

    return Package(pkg)


# Copied from VistrailController#try_to_enable_package()
def do_enable_package(pm, identifier):
    pkg = pm.identifier_is_available(identifier)
    if pm.has_package(pkg.identifier):
        return True
    if pkg and not pm.has_package(pkg.identifier):
        pm.late_enable_package(pkg.codepath)
        pkg = pm.get_package_by_codepath(pkg.codepath)
        if pkg.identifier != identifier:
            # pkg is probably a parent of the "identifier" package
            # try to load it
            if (hasattr(pkg.module, 'can_handle_identifier') and
                    pkg.module.can_handle_identifier(identifier)):
                pkg.init_module.load_from_identifier(identifier)
        return True
    # identifier may refer to a subpackage
    if (pkg and pkg.identifier != identifier and
            hasattr(pkg.module, 'can_handle_identifier') and
            pkg.module.can_handle_identifier(identifier) and
            hasattr(pkg.init_module, 'load_from_identifier')):
        pkg.init_module.load_from_identifier(identifier)
        return True
    return False


@contextlib.contextmanager
def output_mode(output, mode, **kwargs):
    """Context manager that makes an output use a specific mode.
    """
    # TODO : Output mode selection
    yield


def run_vistrail(filename, version=None, *args, **kwargs):
    """Shortcut for load_vistrail(filename).execute(...)
    """
    return load_vistrail(filename, version).execute(*args, **kwargs)
