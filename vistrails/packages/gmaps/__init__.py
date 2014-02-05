"""Maps package for VisTrails.

This package uses the Google Maps API to display information using
Qt's WebKit in the spreadsheet.

"""

# 2014-02-04 -- 0.1.0
#   * Package created (from existing local work from 2013)


from vistrails.core.packagemanager import get_package_manager

from identifiers import *

def package_dependencies():
    pm = get_package_manager()
    deps = ['org.vistrails.vistrails.tabledata']
    if pm.has_package('org.vistrails.vistrails.spreadsheet'):
        return deps + ['org.vistrails.vistrails.spreadsheet']
    else:
        return deps
