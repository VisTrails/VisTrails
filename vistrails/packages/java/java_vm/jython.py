from __future__ import absolute_import

import os
import sys

from vistrails.core.system import vistrails_root_directory


_java_vm = None


class JythonVM(object):
    def __getattr__(self, name):
        return __import__(name, globals(), locals())


def get_java_vm():
    """Returns a Java VM, creating it if necessary.
    """
    global _java_vm
    global JavaException

    if _java_vm is not None:
        return _java_vm

    # Build the classpath parameter

    # CLASSPATH environment variable
    try:
        classpath = os.environ['classpath']
    except KeyError:
        classpath = []
    else:
        classpath = classpath.split(os.pathsep)

    # Application library directory
    vt_root = vistrails_root_directory()
    for d in ['../javalibs', '../libs', '../lib', '../jars', '../jar',
              '../../javalibs', '../../libs', '../../lib', '../../jars',
              '../../jar']:
        d = os.path.join(vt_root, d)
        if os.path.isdir(d):
            for root, dirs, files in os.walk(d):
                for f in files:
                    if f[-4:].lower() == '.jar':
                        classpath.append(os.path.join(root, f))
                # Don't visit subdirectories beginning with a dot
                i = 0
                while i < len(dirs):
                    if dirs[i][0] == '.':
                        del dirs[i]
                    else:
                        i += 1

    sys.path.extend(classpath)

    # We are using Jython -- we are in a JVM
    # We can access Java classes natively through import
    _java_vm = JythonVM()

    import java.lang
    JavaException = java.lang.Exception

    return _java_vm


def get_class(fullname):
    pos = fullname.rfind('.')
    if pos == -1:
        raise ValueError("get_class() on a class without package")
    name = fullname[pos+1:]
    package = fullname[:pos]
    try:
        return getattr(__import__(package, globals(), locals(), name), name)
    except ImportError:
        raise ValueError("get_class() didn't find the requested package")
    except AttributeError:
        raise ValueError("get_class() didn't find the requested class")


def build_jarray(t, seq):
    import jarray
    if t == 'boolean':
        t = 'Z'
    elif t == 'byte':
        t = 'B'
    elif t == 'char':
        t = 'C'
    elif t == 'double':
        t = 'D'
    elif t == 'float':
        t = 'F'
    elif t == 'int':
        t = 'I'
    elif t == 'long':
        t = 'J'
    return jarray.array(seq, t)


def add_on_classpath(path):
    if isinstance(path, basestring):
        if not path in sys.path:
            sys.path.append(path)
    elif isinstance(path, (tuple, list, set)):
        for p in path:
            if not p in sys.path:
                sys.path.append(p)
    return True


def implement(interface_name):
    def actual_decorator(klass):
        # Get the interface from its name
        interface = get_class(interface_name)
        # We'll replace this class with a subclass
        subclass = type(
            klass.__name__ + '_Proxy',
            (klass, interface),
            dict())
        return subclass
    return actual_decorator
