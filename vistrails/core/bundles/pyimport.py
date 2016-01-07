###############################################################################
##
## Copyright (C) 2014-2016, New York University.
## Copyright (C) 2011-2014, NYU-Poly.
## Copyright (C) 2006-2011, University of Utah.
## All rights reserved.
## Contact: contact@vistrails.org
##
## This file is part of VisTrails.
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met:
##
##  - Redistributions of source code must retain the above copyright notice,
##    this list of conditions and the following disclaimer.
##  - Redistributions in binary form must reproduce the above copyright
##    notice, this list of conditions and the following disclaimer in the
##    documentation and/or other materials provided with the distribution.
##  - Neither the name of the New York University nor the names of its
##    contributors may be used to endorse or promote products derived from
##    this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
## AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
## THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
## PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
## CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
## OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
## WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
## OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
## ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
###############################################################################

"""module responsible for smartly importing python modules, checking
for necessary installs."""

from __future__ import division

import vistrails.core.bundles.installbundle
from vistrails.core.configuration import get_vistrails_configuration, \
    get_vistrails_persistent_configuration
from vistrails.core import debug

##############################################################################

_previously_failed_pkgs = set()

class PyImportException(ImportError):
    pass

class PyImportBug(PyImportException):
    pass

def _vanilla_import(module_name):
    return __import__(module_name, globals(), locals(), [])

def py_import(module_name, dependency_dictionary, store_in_config=False):
    """Tries to import a python module, installing if necessary.

    If the import doesn't succeed, we guess which system we are running on and
    install the corresponding package from the dictionary. We then run the
    import again.
    If the installation fails, we won't try to install that same module again
    for the session.
    """
    try:
        result = _vanilla_import(module_name)
        return result
    except ImportError:
        if not getattr(get_vistrails_configuration(), 'installBundles'):
            raise

    if module_name in _previously_failed_pkgs:
        raise PyImportException("Import of Python module '%s' failed again, "
                                "not triggering installation" % module_name)
    if store_in_config:
        ignored_packages_list = getattr(get_vistrails_configuration(),
                                        'bundleDeclinedList',
                                        None)
        if ignored_packages_list:
            ignored_packages = set(ignored_packages_list.split(';'))
        else:
            ignored_packages = set()
        if module_name in ignored_packages:
            raise PyImportException("Import of Python module '%s' failed "
                                    "again, installation disabled by "
                                    "configuration" % module_name)
    debug.warning("Import of python module '%s' failed. "
                  "Will try to install bundle." % module_name)

    success = vistrails.core.bundles.installbundle.install(
            dependency_dictionary)

    if store_in_config:
        if bool(success):
            ignored_packages.discard(module_name)
        else:
            ignored_packages.add(module_name)
        setattr(get_vistrails_configuration(),
                'bundleDeclinedList',
                ';'.join(sorted(ignored_packages)))
        setattr(get_vistrails_persistent_configuration(),
                'bundleDeclinedList',
                ';'.join(sorted(ignored_packages)))

    if not success:
        _previously_failed_pkgs.add(module_name)
        raise PyImportException("Installation of Python module '%s' failed." %
                                module_name)
    try:
        result = _vanilla_import(module_name)
        return result
    except ImportError, e:
        _previously_failed_pkgs.add(module_name)
        raise PyImportBug("Installation of package '%s' succeeded, but import "
                          "still fails." % module_name)
