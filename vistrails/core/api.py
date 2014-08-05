import contextlib

import vistrails.core.application
import vistrails.core.db.io
from vistrails.core.db.locator import UntitledLocator, FileLocator
from vistrails.core.modules.module_registry import get_module_registry
from vistrails.core.modules.package import Package as _Package
from vistrails.core.packagemanager import get_package_manager
from vistrails.core.vistrail.controller import VistrailController
from vistrails.core.vistrail.pipeline import Pipeline as _Pipeline
from vistrails.core.vistrail.vistrail import Vistrail as _Vistrail


__all__ = ['Vistrail', 'Pipeline', 'Module', 'Package',
           'Results', 'Function',
           'load_vistrail', 'load_pipeline', 'load_package',
           'output_mode', 'run_vistrail',
           'NoSuchVersion']


class NoSuchVersion(ValueError):
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
        elif isinstance(arg, Pipeline):
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
            self._current_pipeline = Pipeline(self.controller.current_pipeline,
                                              vistrail=self)
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

    def get_module(self, module_id):
        # TODO : module ids are global to a vistrail, so, we should be able to
        # get modules that are not part of the current pipeline as well
        return self.current_pipeline.get_module(module_id)

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


class Pipeline(object):
    """This class represents a single Pipeline.

    It doesn't have a controller.
    """
    vistrail = None

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
            if isinstance(vistrail, Vistrail):
                self.vistrail = vistrail
            else:
                raise TypeError("Pipeline got unknown type %r as 'vistrail' "
                                "argument" % type(vistrail).__name__)

    @property
    def modules(self):
        pass  # TODO

    def execute(self, *args, **kwargs):
        pass  # TODO : magic

    def get_module(self, module_id):
        if isinstance(module_id, (int, long)):  # module id
            module = self.pipeline.modules[module_id]
            return Module(descriptor=module.module_descriptor,
                          module_id=module_id,
                          pipeline=self)
        elif isinstance(module_id, basestring):  # module name
            pass  # TODO
        else:
            raise TypeError("get_module() expects a string or integer, not "
                            "%r" % type(module_id).__name__)

    def __repr__(self):
        # TODO : should show InputPort and OutputPort modules' names
        return "<%s: %d modules, %d connections>" % (
                self.__class__.__name__,
                len(self.pipeline.modules),
                len(self.pipeline.connections))


class Module(object):
    """Wrapper for a module, which can be in a Pipeline or not yet.
    """
    module_id = None
    pipeline = None
    vistrail = None

    def __init__(self, descriptor, **kwargs):
        self.descriptor = descriptor
        if 'module_id' in kwargs:
            if 'pipeline' in kwargs and 'vistrail' in kwargs:
                raise TypeError("Please pass either pipeline or vistrail "
                                "arguments")
            self.module_id = kwargs['module_id']
            if 'pipeline' in kwargs:
                pipeline = kwargs['pipeline']
                if pipeline.vistrail is not None:
                    self.vistrail = pipeline.vistrail
                else:
                    self.pipeline = pipeline
            elif 'vistrail' in kwargs:
                self.vistrail = kwargs['vistrail']
            else:
                raise TypeError("Module was given an id but no pipeline or "
                                "vistrail")
        else:
            if kwargs:
                raise TypeError("Module was given unexpected argument: %r" %
                                next(iter(kwargs)))

    def __repr__(self):
        # TODO : Should show module's name. Also, package identifier?
        if self.module_id is None:
            return "<Module %r>" % self.descriptor.name
        elif self.vistrail is not None:
            return "<Module %r, id %d in %r>" % (self.descriptor.name,
                                                 self.module_id,
                                                 self.vistrail.controller.name)
        else:  # self.pipeline is not None
            return "<Module %r, id %d>" % (self.descriptor.name,
                                                 self.module_id)


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


class Results(object):
    """Contains the results of a pipeline execution.
    """
    # TODO


class Function(object):
    """A function, essentially a value with an explicit module type.
    """
    # TODO


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
        pass  # TODO
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
    # TODO
    yield


def run_vistrail(filename, version=None, *args, **kwargs):
    """Shortcut for load_vistrail(filename).execute(...)
    """
    return load_vistrail(filename, version).execute(*args, **kwargs)
