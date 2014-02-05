"""Table data package for VisTrails.

This package contains data extraction and manipulation facilities. It wraps
numpy and csv and allows the use of several file types from VisTrails, with
extraction and conversion routines.

"""

# ChangeLog:
# 2014-02-03 -- 0.1.4
#   * Merges some tabdata functionality (improve CSV)
# 2014-01-14 -- 0.1.3
#   * Adds writer modules
# 2013-12-09 -- 0.1.2
#   * No longer use 'self' ports to output tables
# 2013-10-04 -- 0.1.1
#   * Moves reading modules out of specific namespaces
#     (read|csv|CSVFile -> read|CSVFile)
# 2013-05-16 -- 0.1.0
#   * Package created (for DAT project)

from vistrails.core.packagemanager import get_package_manager

from .identifiers import *


def package_dependencies():
    pm = get_package_manager()
    if pm.has_package('org.vistrails.vistrails.spreadsheet'):
        return ['org.vistrails.vistrails.spreadsheet']
    else:
        return []


def package_requirements():
    from vistrails.core.requirements import require_python_module
    require_python_module('csv')
