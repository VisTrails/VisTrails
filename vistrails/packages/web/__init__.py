from vistrails.core.configuration import ConfigurationObject

from identifiers import *


configuration = ConfigurationObject(server_port=13254)


def package_dependencies():
    return ['org.vistrails.vistrails.spreadsheet']
