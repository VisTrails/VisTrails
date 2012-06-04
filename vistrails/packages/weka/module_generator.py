from core.modules.vistrails_module import Module
from core.modules.module_registry import get_module_registry

from core.modules.basic_modules import Boolean, Float, Integer, String


class WekaBaseModule(Module):
    """Base Module from which all Weka modules inherit.
    """


class GetterModuleMixin(object):
    """The mixin implementing the logic for the *_get Module.

    Uses the _getters attribute.
    """
    def compute(self):
        # TODO
        pass


class ConstructorModuleMixin(object):
    """The mixin implemting the logic for the *_N Module.

    Uses the _getters, _setters and _ctor_params attributes.
    """
    def compute(self):
        # TODO
        pass


_type_to_module = {
        'int': Integer, 'long': Integer, 'Integer': Integer, 'Long': Integer,
        'float': Float, 'double': Float, 'Float': Float, 'Double': Float,
        'boolean': Boolean, 'Boolean': Boolean,
        'java.lang.String': String}


class ModuleCreator(object):
    """Walk over the parseResult structure and emit the Module's in order.

    Here, the objective is to create all the Module's associated with each
    Java class.
    The structure is as follow:
      - An abstract module is created for the class, which represents this
          datatype. It also has all the getters (converted into output ports),
          and inherits from the abstract module associated with the parent
          class, or WekaBaseModule.
      - A concrete module used to call getters. It inherits from the abstract
          module, so it has the getter ports, and has a single input port
          'this'.
          The module name is appended '_get'.
      - For each constructor, a concrete module is created. It inherits from
          the abstract module, so it has all the getter ports, and has an input
          port for each constructor parameter. It also has the setters.
          An output port 'this' returns the object constructed with the
          parameters and after the setters have been called.
          The module name is appended an underscore and a number.
      - For each static method, a concrete module is created. It inherits
          from the WekaBaseModule directly, not from the abstract module.
          The module name is appended an underscore and the method name.

    _create_module is used to create all the abstract modules, creating the
    parent first if it exists.
    Then, _populate_modules is used to add the getter ports to the abstract
    modules and to create the concrete modules.
    This is done in two steps because the modules might be referenced as a
    datatype by a port on another module.
    """
    class CyclicInheritance(Exception):
        """We found a cycle in the inheritance graph.

        Weird. Java would complain.
        """
        pass

    class MissingParent(Exception):
        """Some class inherits from a class we don't know about.
        """
        # FIXME : shouldn't we just ignore that dependency and add the module
        # as a top-level module?
        pass

    def __init__(self, parseResult):
        self._parseResult = parseResult
        self._created_modules = dict()
        self._module_registry = get_module_registry()
        self._used_methods = 0
        self._ignored_methods = 0

    def _get_type_module(self, typename):
        """Return the VisTrails module that represents the given typename.
        """
        try:
            # If this is one of the Java classes, we can return the abstract
            # module associated with it
            if typename.startswith('weka.'):
                return self._created_modules[typename]
            # Else we look it up in our map of standard types
            return _type_to_module[typename]
        except KeyError:
            pass

        return WekaBaseModule # Well, we have to return something...

    def _create_module(self, c):
        if c['fullname'] in self._created_modules:
            # Already created
            return

        if c['fullname'] in self._creating_modules:
            # Already being created! We stumbled on the same module while
            # following the 'extends' relations! This is bad!
            raise ModuleCreator.CyclicInheritance
        self._creating_modules.add(c['fullname'])

        # Process the parent class first
        parent = WekaBaseModule
        if (c['extends'] is not None and
                c['extends'] not in self._created_modules):
            try:
                parent = self._parseResult[c['extends']]
            except KeyError:
                raise ModuleCreator.MissingParent(
                        "%s extends %s but it couldn't be found" % (
                                c['fullname'],
                                c['extends']))
            self._create_module(parent)
            parent = self._created_modules[c['extends']]

        name = c['fullname'].replace('.', '_')

        # Create the abstract module
        mod = type(name, (parent,), dict())
        self._module_registry.add_module(mod, abstract=True)
        self._created_modules[c['fullname']] = mod

    def _populate_modules(self, c):
        mod = self._created_modules[c['fullname']]
        name = mod.__name__

        # We identify the input ports for the setters, and the output ports for
        # the getters
        # Note that we only add the getters as ports of the Module!
        setters = dict()
        getters = set()
        for m in c['methods']:
            # Setters
            if (m['name'].startswith('set') and
                    len(m['params']) == 1):
                setters[m['name']] = (
                        self._get_type_module(m['params'][0][0]),
                        m['params'][0][1])
                self._used_methods += 1
            # Getters
            elif (m['name'].startswith('get') and
                    len(m['params']) == 0):
                getters.add(m['name'])
                self._module_registry.add_output_port(
                        mod, m['name'],
                        (
                                self._get_type_module(m['returnType']),
                                m['returnType']))
                self._used_methods += 1
            else:
                self._ignored_methods += 1
        mod._setters = set(setters.keys())
        mod._getters = getters

        # Create the getter module
        if getters:
            cname = '%s_get' % name
            cmod = type(cname, (GetterModuleMixin, mod), dict())
            self._module_registry.add_module(cmod)
            self._module_registry.add_input_port(
                    cmod, 'this',
                    (mod, 'the object to call getters on'))

        # Now, we need to create a new concrete module for each constructor
        if not c['abstract']:
            i = 0
            for m in c['constructors']:
                i += 1
                cname = '%s_%d' % (name, i)
                cmod = type(
                        cname,
                        (ConstructorModuleMixin, mod),
                        dict(_ctor_params=len(m['params'])))
                self._module_registry.add_module(cmod)
                # Constructor parameters
                for t, n in m['params']:
                    self._module_registry.add_input_port(
                            cmod, ("ctor_%s" % n),
                            (
                                    self._get_type_module(t),
                                    t))
                # Setters
                for sname, (t, n) in setters.iteritems():
                    self._module_registry.add_input_port(
                            cmod, sname,
                            (t, n))
                # The 'this' output port, that returns the created object
                self._module_registry.add_output_port(
                        cmod, 'this',
                        (mod, 'the created object'))

        # TODO : static methods

    def create_all_modules(self):
        # Create the abstract modules
        for c in self._parseResult.itervalues():
            # This field is used to detect cycles in the dependency graph
            self._creating_modules = set()

            self._create_module(c)

        # Add the input/output ports and create the concrete modules
        for c in self._parseResult.itervalues():
            self._populate_modules(c)


def generate(parseResult):
    """Generates the VisTrails Module's from the parseResult structure.

    This method will be called at each startup with either a freshly parsed
    object or the cache file.
    """
    reg = get_module_registry()
    reg.add_module(WekaBaseModule, abstract=True)

    creator = ModuleCreator(parseResult)
    creator.create_all_modules()
