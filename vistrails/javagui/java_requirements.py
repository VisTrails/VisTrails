from extras.core.java_vm import get_java_vm
from core.requirements import MissingRequirement


def _try_import(imports):
    """Try to import the given symbols from the package.

    This is used to test if the current system path has been correctly set.
    """
    if isinstance(imports[0], basestring):
        if len(imports) != 2:
            raise ValueError
        imports = [imports]
    for package, name_list in imports:
        if not isinstance(package, basestring):
            raise ValueError
        elif not isinstance(name_list, (tuple, list)):
            raise ValueError
        try:
            p = __import__(package, globals(), locals(), name_list, 0)
        except ImportError:
            return False, "Couldn't import package '%s'" % package
        for name in name_list:
            try:
                getattr(p, name)
            except AttributeError:
                return (False, "Package '%s' didn't provide symbol "
                        "'%s'" % (package, name))

    return True, None


def check_java_requirement(
        imports):
    # This will import the JARs
    get_java_vm()

    if not isinstance(imports, (tuple, list)):
        raise ValueError

    # Try it now -- maybe the package is already accessible
    status, error = _try_import(imports)
    if status is True:
        return
    raise MissingRequirement(error)
