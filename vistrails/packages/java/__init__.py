"""This package provides automatic wrapping of Java libraries.
"""

from .identifiers import name, identifier, version


def can_handle_identifier(identifier):
    """This package handles packages starting with Java#
    """
    return identifier.startswith("Java#")


def package_requirements():
    from .java_vm import get_java_vm


_force_no_unload_pkg_list = ['vistrails.packages.java.java_vm']