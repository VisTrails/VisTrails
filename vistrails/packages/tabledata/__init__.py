"""Table data package for VisTrails.

This package contains data extraction and manipulation facilities. It wraps
numpy and csv and allows the use of several file types from VisTrails, with
extraction and conversion routines.

"""

from identifiers import *

def package_requirements():
    import vistrails.core.requirements
    if not vistrails.core.requirements.python_module_exists('numpy'):
        raise vistrails.core.requirements.MissingRequirement('numpy')
    if not vistrails.core.requirements.python_module_exists('csv'):
        raise vistrails.core.requirements.MissingRequirement('csv')
