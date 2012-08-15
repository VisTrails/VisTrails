import os
import sys
import platform
import functools


_java_vm = None

JavaException = None


USING_JYTHON = platform.system() in ['Java', 'JAVA']
USING_WINDOWS = platform.system() in ['Windows', 'Microsoft']

if not USING_JYTHON:
    import jpype


__all__ = ['get_java_vm', 'get_class', 'build_jarray', 'implement_interface',
           'JavaException', 'USING_JYTHON']


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
            # If the 'java' command comes from a JDK, the DLL is located in a
            # 'jre' subdirectory
            path = os.path.realpath(os.path.join(
                java, '../../jre/bin/client/jvm.dll'))
            if os.path.exists(path):
                return path
            else:
                return os.path.realpath(os.path.join(
                    java, '../client/jvm.dll'))

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

    # CLASSPATH environment variable
    classpath = os.environ['classpath'].split(os.pathsep)

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


if USING_JYTHON:
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
else:
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


import unittest

class TestInterfaceCallback(unittest.TestCase):
    def setUp(self):
        self._vm = get_java_vm()

    def test_callback_class(self):
        class InterfImpl(object):
            def __init__(self, testcase):
                self.testcase = testcase

            def callback(self, number, name):
                self.testcase.assertEqual(number, 42)
                self.testcase.assertEqual(name, u"answer")
                self.testcase.assertTrue(isinstance(name, (unicode, str)))
        # No class decorator in 2.5 syntax
        InterfImpl = implement('tests.jproxy.CallbackInterface')(InterfImpl)

        proxy = InterfImpl(self)
        self._vm.tests.jproxy.CallbackUser.use(proxy)


class TestInterfaceBean(unittest.TestCase):
    def setUp(self):
        self._vm = get_java_vm()

    def test_bean_class(self):
        class BeanImpl(object):
            def getNumber(self):
                return 42
            def getName(self):
                return "answer"
        # No class decorator in 2.5 syntax
        BeanImpl = implement('tests.jproxy.BeanInterface')(BeanImpl)
        proxy = BeanImpl()
        self._vm.tests.jproxy.BeanUser.use(proxy)

if __name__ == '__main__':
    unittest.main()
