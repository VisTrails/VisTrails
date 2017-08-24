""" Allows Pandas DataFrame to be passed around through Input and Output ports.
And does various operations with DataFrames.
Made by Matt Dirks (skylogic.ca)."""

from __future__ import division, print_function
from vistrails.core.packagemanager import get_package_manager
from .identifiers import *

__author__ = "Matthew Dirks"
__email__ = "matt@skylogic.ca"

def package_dependencies():
    # pm = get_package_manager()
    # spreadsheet_identifier = 'org.vistrails.vistrails.spreadsheet'
    # if pm.has_package(spreadsheet_identifier):
    #     return [spreadsheet_identifier]
    # else: # pragma: no cover
    return ['org.vistrails.vistrails.tabledata', 'org.vistrails.vistrails.sql']


def package_requirements():
    from vistrails.core.requirements import require_python_module
    # require_python_module('csv')
    require_python_module('sqlalchemy', {
            'pip': 'SQLAlchemy',
            'linux-debian': 'python-sqlalchemy',
            'linux-ubuntu': 'python-sqlalchemy',
            'linux-fedora': 'python-sqlalchemy'})
