from core import debug

from javareflect import format_type


def format_type_list(l):
    return map(format_type, l)


class GetterModuleMixin(object):
    """The mixin implementing the logic for the *_get Module.

    Uses the _getters attribute.
    """
    def compute(self):
        # TODO
        pass


class ConstructorModuleMixin(object):
    """The mixin implementing the logic for the *_N Module.

    Uses the _getters, _setters and _ctor_params attributes.
    """
    def __init__(self):
        super(ConstructorModuleMixin, self).__init__()
        # Load the class
        # When do it now so that we don't load unused classes when building the
        # modules
        self._class = self._classloader.loadClass(self._classname)
        # Find the correct constructor
        expected_parameters = [t for t, n in self._ctor_params]
        ctors = self._class.getConstructors()
        self._ctor = None
        for c in ctors:
            params = format_type_list(list(c.getParameterTypes()))
            if params == expected_parameters:
                self._ctor = c
                break
        if self._ctor is None:
            debug.critical("Couldn't load the Java class %s" % self._classname)

    def compute(self):
        # Get the constructor parameters from the input ports
        params = []
        for t, n in self._ctor_params:
            params.append(self.getInputFromPort('ctor_%s' % n))

        # Call the constructor
        this = self._ctor.newInstance(params)

        self.setResult('this', this)
