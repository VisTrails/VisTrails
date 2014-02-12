from vistrails.core import debug
from vistrails.core.modules.vistrails_module import Module

from . import java_vm
from .java_vm import get_java_vm, get_class


_JAVA_VM = get_java_vm()

Class = get_class('java.lang.Class')


class JavaBaseModule(Module):
    """Base Module from which all Java modules inherit.
    """


def format_type(t):
    if not java_vm.isArray(t):
        return java_vm.getName(t)
    else:
        return format_type(java_vm.getComponentType(t)) + '[]'


def format_type_list(l):
    return map(format_type, l)


class GetterModuleMixin(object):
    """The mixin implementing the logic for the *_get Module.

    Uses the _getters attribute.
    """
    def __init__(self):
        super(GetterModuleMixin, self).__init__()
        # Load the class
        # We do it now so that we don't load unused classes when building the
        # modules
        self._class = get_class(self._classname)

    def compute(self):
        # Get the object fron the input port
        this = self.get_input('this')

        # Call the getters
        for getter in self._getters:
            called = False
            for method in self._class.getMethods():
                if method.getName() == getter:
                    output = method.invoke(this, [])
                    called = True
                    break
            if called:
                self.set_output(getter, output)
            else:
                debug.warning("didn't find requested getter method\n"
                              "class=%s, method=%s" % (
                              self._classname, getter))


class ConstructorModuleMixin(object):
    """The mixin implementing the logic for the *_N Module.

    Uses the _getters, _setters and _ctor_params attributes.
    """
    def __init__(self):
        super(ConstructorModuleMixin, self).__init__()
        # Load the class
        # We do it now so that we don't load unused classes when building the
        # modules
        self._class = get_class(self._classname)
        # Find the correct constructor
        expected_parameters = [param.type for param in self._ctor_params]
        ctors = self._class.getConstructors()
        self._ctor = None
        for c in ctors:
            params = format_type_list(list(c.getParameterTypes()))
            if params == expected_parameters:
                self._ctor = c
                break
        if self._ctor is None:
            debug.critical("Couldn't load the Java class %s" %
                           self._classname)

    def compute(self):
        # Get the constructor parameters from the input ports
        params = []
        for param in self._ctor_params:
            params.append(self.get_input('ctor_%s' % param.name))

        # Call the constructor
        this = self._ctor.newInstance(params)

        # Call the setters
        for setter in self._setters:
            if self.has_input(setter):
                value = self.get_input(setter)
                called = False
                for method in self._class.getMethods():
                    if method.getName() == setter:
                        method.invoke(this, [value])
                        called = True
                        break
                if not called:
                    debug.warning("didn't find requested setter method\n"
                                  "class=%s, method=%s" % (
                                  self._classname, setter))

        # Call the getters
        for getter in self._getters:
            called = False
            for method in self._class.getMethods():
                if method.getName() == getter:
                    output = method.invoke(this, [])
                    called = True
                    break
            if called:
                self.set_output(getter, output)
            else:
                debug.warning("didn't find requested getter method\n"
                              "class=%s, method=%s" % (
                              self._classname, getter))

        self.set_output('this', this)


class StaticModuleMixin(object):
    """The mixin implementating the logic for static method modules.

    Uses the _classname and _params attributes.
    """
    def __init__(self):
        super(StaticModuleMixin, self).__init__()
        # Load the class
        # We do it now so that we don't load unused classes when building the
        # modules
        self._class = get_class(self._classname)
        # Find the correct static method
        expected_parameters = [param.type for param in self._params]
        methods = self._class.getDeclaredMethods()
        self._method = None
        for m in methods:
            params = format_type_list(list(m.getParameterTypes()))
            if params == expected_parameters:
                self._method = m
                break
        if self._method is None:
            debug.critical("Couldn't load the Java class %s" % self._classname)

    def compute(self):
        # Get the method parameters from the input ports
        params = []
        for param in self._params:
            params.append(self.get_input(param.name))

        # Call the method
        result = self._method.invoke(None, params)
        result = _JAVA_VM.unbox(result)

        self.set_output('Result', result)
