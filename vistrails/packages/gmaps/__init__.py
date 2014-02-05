"""Maps package for VisTrails.

This package uses the Google Maps API to display information using
Qt's WebKit in the spreadsheet.

"""

# 2014-02-04 -- 0.1.0
#   * Package created (from existing local work from 2013)


from identifiers import *


def package_dependencies():
    return ['org.vistrails.vistrails.tabledata',
            'org.vistrails.vistrails.spreadsheet']
