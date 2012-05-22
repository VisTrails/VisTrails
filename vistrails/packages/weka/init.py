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
import json
import hashlib

from core import debug
from core.configuration import get_vistrails_configuration
from core.system import default_dot_vistrails


def hashfile(filename, hash=hashlib.md5()):
    block_size = hash.block_size
    with open(filename, 'rb') as f:
        chunk = f.read(block_size)
        while chunk != '':
            hash.update(chunk)
            chunk = f.read(block_size)
    return hash.hexdigest()


def initialize():
    configuration = get_vistrails_configuration()

    try:
        weka_jar = configuration['wekaJar']
    except KeyError:
        weka_jar = 'weka.jar'

    try:
        weka_src = configuration['wekaSrcJar']
    except KeyError:
        weka_src = 'weka-src.jar'

    try:
        weka_dir = os.path.abspath(configuration['wekaDirectory'])
        if not os.path.isdir(weka_dir):
            debug.warning("specified wekaDirectory is not a directory:\n"
                          "%s" % weka_dir)
        weka_jar = os.path.join(weka_dir, weka_jar)
        weka_src = os.path.join(weka_dir, weka_src)
    except KeyError:
        weka_dir = ''

    if not os.path.isfile(weka_jar):
        raise Exception("Couldn't find weka.jar")
    if not os.path.isfile(weka_jar):
        raise Exception("Couldn't find weka-src.jar")

    parseResultFilename = os.path.join(
            default_dot_vistrails(),
            'weka-methods.json')

    # Attempt to load the cached result
    try:
        parseResultFile = file(parseResultFilename)
        parseResult = json.load(parseResultFile)
        parseResultFile.close()
    # If it fails, rebuild everything
    except IOError:
        parseResult = None
    else:
        # Check that we are still using the same Weka library
        if parseResult['weka_md5'] != hashfile(weka_jar):
            parseResult = None

    if parseResult is None:
        import javaparser, javareflect
        parsed_classes = javaparser.parse_jar(weka_src, 'src/main/java')
        parseResult = javareflect.parse_jar(weka_jar, parsed_classes)
        try:
            parseResultFile = file(parseResultFilename, 'w')
            json.dump(parseResult, parseResultFile)
            parseResultFile.close()
        except IOError:
            debug.warning("couldn't write the weka reflection cache file\n"
                          "it will have to be parsed again next time...")

    import module_generator
    module_generator.generate(parseResult)
