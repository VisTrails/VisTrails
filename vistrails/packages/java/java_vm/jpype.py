from __future__ import absolute_import

import functools
import jpype
import os
import platform
import sys


_java_vm = None


USING_WINDOWS = platform.system() == 'Windows'


def _find_executable_from_path(filename):
    pathlist = os.environ['PATH'].split(os.pathsep) + ["."]
    for p in pathlist:
        # On Windows, paths may be enclosed in ""
        if USING_WINDOWS:
            if p.startswith('"') and p.endswith('"'):
                p = p[1:-1]
        fullpath = os.path.join(p, filename)
        if os.path.isfile(fullpath):
            return fullpath
        elif USING_WINDOWS and os.path.isfile(fullpath + '.exe'):
            return fullpath + '.exe'
    return None


class JPypeVM(object):
    def __getattr__(self, name):
        try:
            return getattr(jpype, name)
        except AttributeError:
            return jpype.JPackage(name)


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


def _find_java_dll():
    if USING_WINDOWS:
        # First attempt to locate the java executable, and use the DLL of that
        # distribution
        java = _find_executable_from_path('java')
        if java is not None:
            # If the 'java' command comes from a JDK, the DLL is located in a
            # 'jre' subdirectory
            path = os.path.realpath(os.path.join(
                java, '../../jre/bin/client/jvm.dll'))
            if os.path.exists(path):
                return path
            else:
                path = os.path.realpath(os.path.join(
                    java, '../client/jvm.dll'))
                if not os.path.exists(path):
                    path = None

        # Else, look for a Java distribution in standard locations
        if sys.maxint > (2 << 32): # 64-bit Python
            paths = ['C:/Program Files/Java']
        else:
            paths = ['C:/Program Files (x86)/Java', 'C:/Program Files/Java']
        for path in paths:
            # First attempt to use the 'jre7' version
            try:
                if os.stat(os.path.join(path, 'jre7')):
                    return os.path.join(path, 'jre7/bin/client/jvm.dll')
            except OSError:
                pass
            # Else, any version
            for subdir in os.listdir(path):
                dll = os.path.join(path, subdir, 'bin/client/jvm.dll')
                try:
                    if os.stat(dll):
                        return dll
                except OSError:
                    pass
        return None
    else:
        # Assume UNIX
        # Attempt to locate the java executable
        java = _find_executable_from_path('java')
        java = os.path.realpath(java)

        # Attempt to find libjvm.so around here
        java_home = os.path.realpath(os.path.join(java, '../../lib'))
        for dirpath, dirnames, filenames in os.walk(java_home):
            if 'libjvm.so' in filenames:
                return os.path.join(java_home, dirpath, 'libjvm.so')


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
    for d in ['../javalibs', '../libs', '../lib', '../jars', '../jar',
              '../../javalibs', '../../libs', '../../lib', '../../jars',
              '../../jar']:
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

    # Locate the Java DLL
    dll = _find_java_dll()
    print "using Java DLL: %s" % dll

    # Start the JVM
    jpype.startJVM(
            dll,
            '-ea',
            '-Djava.class.path=%s' % os.pathsep.join(classpath))
    print '-Djava.class.path=%s' % os.pathsep.join(classpath)

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
    return jpype.JArray(t)(seq)


def add_on_classpath(path):
    return False # Can't do this on JPype...


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
