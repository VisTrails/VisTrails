from __future__ import absolute_import

import functools
import jpype
import os

from vistrails.core.system import vistrails_root_directory

from .locate_dll import find_java_dll


_java_vm = None

classpath_additions = []


class JPypeVM(object):
    def __init__(self):
        self.__unbox = {
                self.java.lang.Boolean: lambda b: b.booleanValue(),
                self.java.lang.Byte: lambda i: i.intValue(),
                self.java.lang.Character: unicode,
                self.java.lang.Double: lambda d: d.doubleValue(),
                self.java.lang.Float: lambda f: f.floatValue(),
                self.java.lang.Integer: lambda i: i.intValue(),
                self.java.lang.Long: lambda i: i.intValue(),
                self.java.lang.Short: lambda i: i.intValue(),
                self.java.lang.String: unicode}

    def __getattr__(self, name):
        try:
            return getattr(jpype, name)
        except AttributeError:
            return jpype.JPackage(name)

    def unbox(self, obj):
        try:
            f = self.__unbox[type(obj)]
        except KeyError:
            return obj
        else:
            return f(obj)


class JPypeReflectedClass(object):
    def __init__(self, jpype_class):
        self._class = jpype_class

    def __getattr__(self, name):
        try:
            return getattr(self._class, name)
        except AttributeError:
            return functools.partial(
                    getattr(jpype.reflect, name),
                    self._class)


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

    classpath.extend(classpath_additions)

    # Locate the Java DLL
    dll = find_java_dll()
    print "using Java DLL: %s" % dll
    print '-Djava.class.path=%s' % os.pathsep.join(classpath)

    # Start the JVM
    jpype.startJVM(
            dll,
            '-ea',
            '-Djava.class.path=%s' % os.pathsep.join(classpath))

    _java_vm = JPypeVM()

    JavaException = jpype.JavaException

    return _java_vm


def get_class(fullname):
    get_java_vm()
    try:
        return JPypeReflectedClass(jpype.java.lang.Class.forName(
                fullname,
                True,
                jpype.java.lang.ClassLoader.getSystemClassLoader()))
    except JavaException:
        raise ValueError("Class.forName() failed")


def build_jarray(t, seq):
    if t == 'boolean':
        t = jpype.JBoolean
    elif t == 'byte':
        t = jpype.JByte
    elif t == 'char':
        t = jpype.JChar
    elif t == 'double':
        t = jpype.JDouble
    elif t == 'float':
        t = jpype.JFloat
    elif t == 'int':
        t = jpype.JInt
    elif t == 'long':
        t = jpype.JLong
    elif t == 'object':
        t = 'java.lang.Object'
    else:
        raise ValueError
    return jpype.JArray(t)(seq)


def add_to_classpath(path):
    if _java_vm is not None:
        return False # Can't do this on JPype...
    else:
        classpath_additions.append(path)
        return True


def implement(interface_name):
    def actual_decorator(klass):
        # We replace the class with a constructor method
        def constructor(*args, **kwargs):
            # Build the instance
            inst = klass(*args, **kwargs)
            # Make a JProxy
            return jpype.JProxy(interface_name, inst=inst)
        return constructor
    return actual_decorator


# Reflection


def isArray(javaclass):
    return javaclass.__javaclass__.isArray()


def getName(javaclass):
    return javaclass.__javaclass__.getName()


def getComponentType(javaclass):
    return javaclass.__javaclass__.getComponentType()
