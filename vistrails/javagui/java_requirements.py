import os
import re
import sys

from core import debug
from core.requirements import MissingRequirement
from extras.core.java_vm import get_java_vm


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


_PATTERN_TO_RE = re.compile(r'\{([A-Za-z_-]+)\}')

_libs_path = None


def check_java_requirement(
        lib_folders,
        jar_name_pattern, jar_name_defaults,
        imports):
    global _libs_path

    # This will import the JARs in the CLASSPATH environment variable
    get_java_vm()

    if not isinstance(imports, (tuple, list)):
        raise ValueError

    # Try it now -- maybe the package is already accessible
    status, error = _try_import(imports)
    if status is True:
        return

    # If the package was missing, we try to locate a JAR

    jar_name_re = re.compile(
            _PATTERN_TO_RE.sub(r'(.+)', jar_name_pattern.replace('.', r'\.')))
    jar_name_vars = _PATTERN_TO_RE.findall(jar_name_pattern)

    # Locate the directory where the JARs are
    if _libs_path is None:
        for d in ['../javalibs', '../libs', '../lib', '../jars', '../jar',
                  '../../javalibs', '../../libs', '../../lib', '../../jars',
                  '../../jar']:
            if os.path.isdir(d):
                _libs_path = d
                break
        if _libs_path is None:
            raise MissingRequirement("Couldn't locate the JAR directory")
        debug.log("Using Java library path: %s" % _libs_path)

    if lib_folders is None:
        lib_folders = ['']
    else:
        lib_folders.extend('')
    # For each folder the JAR could be in
    match = None
    score = 0
    for d in lib_folders:
        path = os.path.join(_libs_path, d)
        if os.path.isdir(path):
            # Ok, in this dir, we want to locate the jar file
            # We have the generic pattern of the filename we expect and the
            # default values of each variable, but we will accept other values
            # for those variables as well (with a lower score)
            for name in os.listdir(path):
                if not os.path.isfile(os.path.join(path, name)):
                    continue

                m = jar_name_re.match(name)
                if m is not None:
                    s = 0
                    for i, n in enumerate(jar_name_vars):
                        default = jar_name_defaults[n]
                        if ((isinstance(default, basestring) and
                                m.group(i+1) == default) or
                                (m.group(i+1) in default)):
                            s += 1
                    if s > score:
                        score = s
                        match =  os.path.join(path, name)

    if match is None:
        # We didn't find a suitable JAR -- still fails
        raise MissingRequirement(error)
    else:
        sys.path.append(match)

        # Try to import again
        status, error = _try_import(imports)

        if not status:
            sys.path.remove(match)
            raise MissingRequirement(error)
        else:
            debug.log("Added %s to the PYTHON PATH")
