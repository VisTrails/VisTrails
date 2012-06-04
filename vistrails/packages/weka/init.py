"""Entry point for the Weka module.

The goal here is to automagically create the VisTrails module from the Weka
distribution.
The 'javareflect' module uses the Java language's reflection capabilities to
discover the classes and build a hierarchy of modules.
Because the parameter names are not included in class files, we use the
'javaparser' module to process the source JAR and discover the parameter names.
Finally, the module_generator emits the VisTrails modules.

Because this process is slow, the hierarchy of classes is cached in JSON format
in the dot_vistrails directory so that we don't have to do everything at each
startup, as Weka is a pretty big library.
"""

from __future__ import with_statement

import os
import pickle
import hashlib

from core import debug
from core import configuration
from core.system import default_dot_vistrails


class WekaConfigurationError(Exception):
    pass


def hashfile(filename, hash=hashlib.md5()):
    """Computes the hash of a file, given its path.

    Opens the file in binary mode and wraps the appropriate calls to
    hash.update(). hash defaults to MD5.
    """
    block_size = hash.block_size
    with open(filename, 'rb') as f:
        chunk = f.read(block_size)
        while chunk != '':
            hash.update(chunk)
            chunk = f.read(block_size)
    return hash.hexdigest()


def initialize():
    """Entry point for this module.

    This function create the VisTrails Module's from the JARs. It attempts to
    load the package configuration from a cache file, or regenerates it by
    parsing the source JAR (for method parameter names) and the class JAR.

    Related configuration options:
      'wekaDirectory': where to find the JARs
      'wekaJar': the class JAR (default: weka.jar). May be relative to
          'wekaDirectory'
      'wekaSrcJar': the source JAR (default: weka-src.jar). May be relative to
          'wekaDirectory'
    """
    weka_jar = getattr(configuration, 'wekaJar', 'weka.jar')
    weka_src = getattr(configuration, 'wekaSrcJar', 'weka-src.jar')

    try:
        #weka_dir = os.path.abspath(getattr(configuration, 'wekaDirectory', ''))
        weka_dir = 'C:\\Program Files (x86)\\Weka-3-6' # DEBUG
        if not os.path.isdir(weka_dir):
            debug.warning("specified wekaDirectory is not a directory:\n"
                          "%s" % weka_dir)
        weka_jar = os.path.join(weka_dir, weka_jar)
        weka_src = os.path.join(weka_dir, weka_src)
    except KeyError:
        weka_dir = ''

    if not os.path.isfile(weka_jar):
        raise WekaConfigurationError("Couldn't find weka.jar")

    parseResultFilename = os.path.join(
            default_dot_vistrails(),
            'weka-methods.pickle')

    # Attempt to load the cached result
    try:
        parseResultFile = open(parseResultFilename, 'rb')
        parseResult = pickle.load(parseResultFile)
        parseResultFile.close()
    # If it fails, rebuild everything
    except IOError:
        parseResult = None
    else:
        # Check that we are still using the same Weka library
        pass
        # TODO : store the hash somewhere
        #if parseResult['weka_md5'] != hashfile(weka_jar):
        #    parseResult = None

    if parseResult is None:
        debug.warning("couldn't find the Weka interface cache file\n"
                      "Parsing the Weka JARs now - could take a few minutes")
        import javaparser, javareflect
        if os.path.isfile(weka_src):
            parsed_classes = javaparser.parse_jar(weka_src, 'src/main/java')
        else:
            parsed_classes = None
        parseResult = javareflect.parse_jar(weka_jar, parsed_classes)
        try:
            parseResultFile = open(parseResultFilename, 'wb')
            pickle.dump(parseResult, parseResultFile, pickle.HIGHEST_PROTOCOL)
            parseResultFile.close()
        except IOError:
            debug.warning("couldn't write the weka reflection cache file\n"
                          "it will have to be parsed again next time...")

    import module_generator
    module_generator.generate(parseResult, weka_jar)


if __name__ == '__main__':
    initialize()
