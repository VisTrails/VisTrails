import contextlib


__all__ = ['Vistrail', 'Pipeline', 'Module', 'Package',
           'Results', 'Function',
           'load_vistrail', 'output_mode', 'run_vistrail']


is_initialized = False


def initialize():
    if is_initialized:
        return False

    import vistrails.core.application

    # Creates a core application
    vistrails.core.application.init(
            options_dict={
                'installBundles': False,
                'loadPackages': False,
                'enablePackagesSilently': True},
            args=[])

    return True


class Vistrail(object):
    """This class wraps both Vistrail and VistrailController.
    """
    def __init__(self, controller=None):
        initialize()


class Pipeline(object):
    """This class represents a single Pipeline.

    It doesn't have a controller.
    """
    def __init__(self, pipeline=None):
        initialize()


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


@contextlib.contextmanager
def output_mode(output, mode, **kwargs):
    """Context manager that makes an output use a specific mode.
    """
    yield


def run_vistrail(filename, version=None):
    """Shortcut for load_vistrail(filename).execute(...)
    """
