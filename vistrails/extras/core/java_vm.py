import os
import sys
import platform
import core.system
import functools


_java_vm = None

JavaException = None


USING_JYTHON = platform.system() in ['Java', 'JAVA']
USING_WINDOWS = platform.system() in ['Windows', 'Microsoft']

if not USING_JYTHON:
    import jpype


__all__ = ['get_java_vm', 'get_class', 'JavaException', 'build_jarray']


def _find_executable_from_path(filename):
    pathlist = (os.environ['PATH'].split(os.pathsep) +
                [core.system.vistrails_root_directory(), "."])
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


class JythonVM(object):
    def __getattr__(self, name):
        return __import__(name, globals(), locals())


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
            return os.path.realpath(os.path.join(java, '../client/jvm.dll'))

        # Else, look for a Java distribution in standard locations
        for path in ['C:/Program Files/Java',
                     'C:/Program Files (x86)/Java']:
            # First attempt to use the 'jre6' version
            if os.stat(os.path.join(path, 'jre6')):
                return os.path.join(path, 'jre6/bin/client/jvm.dll')
            # Else, any version
            for subdir in os.listdir(path):
                dll = os.path.join(path, subdir, 'bin/client/jvm.dll')
                if os.stat(dll):
                    return dll
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
    classpath = os.environ['classpath'].split(os.pathsep)

    if USING_JYTHON:
        sys.path.extend(classpath)

        # We are using Jython -- we are in a JVM
        # We can access Java classes natively through import
        _java_vm = JythonVM()

        import java.lang
        JavaException = java.lang.Exception
    else:
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
    if USING_JYTHON:
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
    else:
        get_java_vm()
        try:
            return JPypeReflectedClass(jpype.java.lang.Class.forName(
                    fullname,
                    True,
                    jpype.java.lang.ClassLoader.getSystemClassLoader()))
        except JavaException:
            raise ValueError("Class.forName() failed")


def build_jarray(t, seq):
    if USING_JYTHON:
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
    else:
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
