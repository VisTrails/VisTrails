from java.io import File, FileInputStream, IOException
from java.util.zip import ZipInputStream
from java.lang import Class
from java.lang import Exception as JavaException
from java.net import URLClassLoader

import sys

from core import debug


# Iterates on the .class files in a JAR
class JarIterator(object):
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
            e.printStackTrace() # FIXME : This is a Java method
        return None

    def __init__(self, f):
        if isinstance(f, str):
            f = File(f)
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


def format_type(t):
    if not Class.isArray(t):
        return Class.getName(t)
    else:
        return format_type(Class.getComponentType(t)) + '[]'


def analyse_class(c):
    from sys import stdout
    methods = c.getMethods()
    for m in methods:
        stdout.write("  %s %s(" % (format_type(m.getReturnType()), m.getName()))
        params = m.getParameterTypes()
        first = True
        i = 0
        for p in params:
            i += 1
            if first:
                first = False
            else:
                stdout.write(", ")
            stdout.write(format_type(p))
        stdout.write(")\n")


IGNORED_CLASSES = set([
        'weka.gui.MacArffOpenFilesHandler'])


def parse_jar(filename, parsed_sources):
    # Because the path used by the java ClassLoader and the Python path are
    # separate, we cannot just add the JAR to the path here
    # We will use another ClassLoader so we can access the classes through
    # Class.forName()
    #url = File('jar:file://%s!/' % filename).toURI().toURL()
    url = File(filename).toURI().toURL()
    classLoader = URLClassLoader([url])

    iterator = JarIterator(filename)
    ok, err = 0, 0
    for classname in iterator:
        if classname in IGNORED_CLASSES:
            continue
        try:
            c = classLoader.loadClass(classname)
            print classname
            analyse_class(c)
            ok += 1
        except JavaException, e:
            print e
            err += 1

    debug.warning("ok: %d, err: %d" % (ok, err))


if __name__ == '__main__':
    debug.DebugPrint.getInstance().set_message_level(debug.DebugPrint.Log)

    parse_jar('C:\\Program Files (x86)\\Weka-3-6\\weka.jar', set())
