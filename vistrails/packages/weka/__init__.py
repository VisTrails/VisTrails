"""Weka is a collection of machine learning algorithms for data mining tasks.

It is a Java library that is automatically wrapper as VisTrails modules through
limited parsing of the JARs.
"""

from core.configuration import ConfigurationObject

name = 'Weka'
identifier = "edu.utah.sci.vistrails.weka"
version = "0.1.0"
configuration = ConfigurationObject(
        wekaDirectory='',
        wekaJar='weka.jar',
        wekaSrcJar='weka-src.jar')

def package_requirements():
    from core.requirements import require_python_module
    require_python_module('json')
