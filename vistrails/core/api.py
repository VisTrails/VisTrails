import contextlib

import vistrails.core.db.io
from vistrails.core.db.locator import UntitledLocator, FileLocator
from vistrails.core.vistrail.controller import VistrailController
from vistrails.core.vistrail.pipeline import Pipeline as _Pipeline
from vistrails.core.vistrail.vistrail import Vistrail as _Vistrail


__all__ = ['Vistrail', 'Pipeline', 'Module', 'Package',
           'Results', 'Function',
           'load_vistrail', 'load_pipeline', 'output_mode', 'run_vistrail']


is_initialized = False
_application = None


def initialize():
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

    return True


class Vistrail(object):
    """This class wraps both Vistrail and VistrailController.
    """
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


class Module(object):
    """Wrapper for a module, which can be in a Pipeline or not yet.
    """


class Package(object):
    """Wrapper for an enabled package.
    """


class Results(object):
    """Contains the results of a pipeline execution.
    """


class Function(object):
    """A function, essentially a value with an explicit module type.
    """


def load_vistrail(filename, version=None):
    """Loads a Vistrail from a filename.
    """
    if not isinstance(filename, basestring):
        raise TypeError("load_vistrails() expects a filename, got %r" %
                        type(filename).__name__)
    locator = FileLocator(filename)

    loaded_objs = vistrails.core.db.io.load_vistrail(locator)
    controller = VistrailController(*loaded_objs)

    return Vistrail(controller)


def load_pipeline(filename):
    """Loads a single pipeline from a filename.
    """
    if not isinstance(filename, basestring):
        raise TypeError("load_vistrails() expects a filename, got %r" %
                        type(filename).__name__)

    # Copied from VistrailsApplicationInterface#open_workflow()
    locator = FileLocator(filename)
    pipeline = locator.load(_Pipeline)

    return Pipeline(pipeline)


@contextlib.contextmanager
def output_mode(output, mode, **kwargs):
    """Context manager that makes an output use a specific mode.
    """
    yield


def run_vistrail(filename, version=None):
    """Shortcut for load_vistrail(filename).execute(...)
    """
