from core.modules.vistrails_module import Module
from core.modules.module_registry import get_module_registry


class WekaBaseModule(Module):
    def compute(self):
        # TODO
        pass


class ModuleCreator(object):
    """Walk over the parseResult structure and emit the Module's in order.

    A recursive method _create_module_rec() is used to make sure parent modules
    are created and added to the registry before children.
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
        self._created_modules = set()
        self._module_registry = get_module_registry()
        self._used_methods = 0
        self._ignored_methods = 0

    def _create_module_rec(self, c):
        if c['fullname'] in self._creating_modules:
            raise ModuleCreator.CyclicInheritance
        self._creating_modules.add(c['fullname'])

        # Create the parent module first
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
            self._create_module_rec(parent)

        # FIXME : short module names
        name = c['fullname'].replace('.', '_')

        # Create the module
        mod = type(name, (parent,), dict())
        self._module_registry.add_module(mod)
        self._created_modules.add(c['fullname'])

        # List of ports to create from the methods
        setters = set()
        getters = set()
        for m in c['methods']:
            # Setters
            if (m['name'].startswith('set') and
                    len(m['params']) == 1):
                setters.add(m['name'])
                self._used_methods += 1
            # Getters
            elif (m['name'].startswith('get') and
                    len(m['params']) == 0):
                getters.add(m['name'])
                self._used_methods += 1
            else:
                self._ignored_methods += 1
        mod._setters = setters
        mod._getters = getters

    def create_module(self, c):
        if c['fullname'] not in self._created_modules:
            # Keep track of modules being created to detect cycles
            self._creating_modules = set()

        self._create_module_rec(c)

    def create_all_modules(self):
        for c in self._parseResult.itervalues():
            self.create_module(c)


def generate(parseResult):
    """Generates the VisTrails Module's from the parseResult structure.

    This method will be called at each startup with either a freshly parsed
    object or the cache file.
    """
    reg = get_module_registry()
    reg.add_module(WekaBaseModule)

    creator = ModuleCreator(parseResult)
    creator.create_all_modules()
