import contextlib

import vistrails.core.db.io
from vistrails.core.db.locator import UntitledLocator, FileLocator
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

    import vistrails.core.application

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
            self._current_pipeline = Pipeline(self.controller.current_pipeline)
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

    @property
    def changed(self):
        return self.controller.changed

    # TODO : vistrail modification methods


class Pipeline(object):
    """This class represents a single Pipeline.

    It doesn't have a controller.
    """
    def __init__(self, pipeline=None):
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

    @property
    def modules(self):
        pass  # TODO

    def execute(self, *args, **kwargs):
        pass  # TODO : magic

    def __repr__(self):
        return "<%s: %d modules, %d connections>" % (
                self.__class__.__name__,
                len(self.pipeline.modules),
                len(self.pipeline.connections))


class Module(object):
    """Wrapper for a module, which can be in a Pipeline or not yet.
    """
    # TODO


class Package(object):
    """Wrapper for an enabled package.
    """
    # TODO


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


def load_package(identifier):
    """Gets a package by identifier, enabling it if necessary.
    """
    initialize()
    # TODO


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
