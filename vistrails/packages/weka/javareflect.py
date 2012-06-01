from java.io import File, FileInputStream, IOException
from java.util.zip import ZipInputStream
from java.lang import Class
from java.lang import Exception as JavaException
from java.net import URLClassLoader
from java.lang.reflect import Method, Modifier, Constructor

from itertools import izip

from core import debug

import javaparser


# Note that ClassName.methodName(object) is used throughout this file instead
# of object.methodName() for the classes Class, Method and Constructor, as
# there seems to be a bug in Jython


class JarIterator(object):
    """Iterates on the .class files in a JAR.

    Nested classes (SomeClass$InnerClass) are ignored.
    """
    def _findNextClass(self):
        try:
            entry = self._zip.getNextEntry()
            while entry is not None:
                name = entry.getName()
                if name.endswith('.class'):
                    name = name[0:len(name) - 6].replace('/', '.')
                    if '$' not in name:
                        return name
                entry = self._zip.getNextEntry()
        except IOException, e:
            e.printStackTrace() # Note : This is a Java method
        return None

    def __init__(self, filename):
        if not isinstance(filename, str):
            raise TypeError('filename must be a string')
        f = File(filename)
        self._zip = ZipInputStream(FileInputStream(f))
        self._nextEntry = self._findNextClass()

    def next(self):
        if self._nextEntry is None:
            raise StopIteration
        name = self._nextEntry
        self._nextEntry = self._findNextClass()
        return name

    def __iter__(self):
        return self


class JavaAnalyzer(object):
    """Analyzes Java classes into the parseResult structure.
    """
    def __init__(self, sources=None):
        self._sources = sources
        self.classes = {}

    @staticmethod
    def _format_type(t):
        if not Class.isArray(t):
            return Class.getName(t)
        else:
            return JavaAnalyzer._format_type(Class.getComponentType(t)) + '[]'

    def process(self, c):
        status = 'ok'

        # We're not interested in interfaces
        if Class.isInterface(c):
            return 'skipped (interface)'

        # Get the class info that was retrieved from the sources
        sourceClass = None
        if self._sources:
            try:
                sourceClass = self._sources[Class.getName(c)]

                if sourceClass['template']:
                    # We can't handle that just yet
                    return 'skipped (template)'
            except KeyError:
                pass

        # TODO : Nested classes are currently ignored

        # Find the superclass
        superclass = Class.getName(Class.getSuperclass(c))
        if not superclass.startswith('weka.'):
            superclass = None

        readClass = {
                'fullname': Class.getName(c),
                'extends': superclass,
                'abstract': Modifier.isAbstract(Class.getModifiers(c))}

        # Read the methods
        readMethods = []

        for m in Class.getDeclaredMethods(c):
            if Method.getName(m) == 'getClass':
                continue

            mods = Method.getModifiers(m)
            if (Modifier.isAbstract(mods) or
                    Modifier.isStatic(mods) or
                    not Modifier.isPublic(mods)):
                continue
            readParams = []
            params = Method.getParameterTypes(m)

            # Find the parameter names from the parsed source
            sourceParams = None
            if sourceClass:
                for sourceMethod in sourceClass['methods']:
                    if (sourceMethod['name'] == Method.getName(m) and
                            len(sourceMethod['params']) ==
                            len(Method.getParameterTypes(m))):
                        sourceParams = sourceMethod['params']
                        break
            if sourceParams is None:
                status = "parameter names not available"
                sourceParams = ['arg%d' % i for i in xrange(len(params))]

            for p, n in izip(params, sourceParams):
                readParams.append((JavaAnalyzer._format_type(p), n))
            readMethods.append({
                    'name': Method.getName(m),
                    'returnType': JavaAnalyzer._format_type(
                            Method.getReturnType(m)),
                    'params': readParams})
        readClass['methods'] = readMethods

        # Read the constructors
        readConstructors = []

        for m in Class.getConstructors(c):
            mods = Constructor.getModifiers(m)
            if not Modifier.isPublic(mods):
                continue
            readParams = []
            params = Constructor.getParameterTypes(m)

            # Find the parameter names from the parsed source
            sourceParams = None
            if sourceClass:
                cname = javaparser.shortname(Constructor.getName(m))
                for sourceMethod in sourceClass['methods']:
                    if (sourceMethod['name'] == cname and
                            len(sourceMethod['params']) ==
                            len(Constructor.getParameterTypes(m))):
                        sourceParams = sourceMethod['params']
                        break
            if sourceParams is None:
                status = "parameter names not available"
                sourceParams = ['arg%d' % i for i in xrange(len(params))]

            for p, n in izip(params, sourceParams):
                readParams.append((JavaAnalyzer._format_type(p), n))
            readConstructors.append({
                    'params': readParams})
        readClass['constructors'] = readConstructors

        self.classes[readClass['fullname']] = readClass

        return status


IGNORED_CLASSES = set([
        'weka.gui.MacArffOpenFilesHandler'])


def parse_jar(filename, parsed_sources=None):
    """Parse all the .class files in a JAR into the parseResult structure.

    The parseResult will be cached on disk. It is used to emit the VisTrails
    Module's through module_generator:generate().

    If the parsed sources are available, they will be used to provide the name
    of the method parameters, as they are not included in the compiled class
    files.
    """
    # Because the path used by the java ClassLoader and the Python path are
    # separate, we cannot just add the JAR to the path here
    # We will use another ClassLoader so we can access the classes through
    # Class.forName()
    #url = File('jar:file://%s!/' % filename).toURI().toURL()
    url = File(filename).toURI().toURL()
    classLoader = URLClassLoader([url])

    analyzer = JavaAnalyzer(parsed_sources)

    iterator = JarIterator(filename)
    status = {'ok': 0}
    for classname in iterator:
        if classname in IGNORED_CLASSES:
            continue
        try:
            c = classLoader.loadClass(classname)
            ret = analyzer.process(c)
        except JavaException, e:
            ret = 'exception'
        try:
            status[ret] += 1
        except KeyError:
            status[ret] = 1

    msg = "analyzing weka.jar through java reflection:\n"
    for ret, nb in status.iteritems():
        msg += "  %4d %s\n" % (nb, ret)
    debug.warning(msg)

    return analyzer.classes


if __name__ == '__main__':
    debug.DebugPrint.getInstance().set_message_level(debug.DebugPrint.Log)

    from pprint import pprint
    pprint(parse_jar('C:\\Program Files (x86)\\Weka-3-6\\weka.jar', dict()))
