############################################################################
##
## Copyright (C) 2006-2009 University of Utah. All rights reserved.
##
## This file is part of VisTrails.
##
## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of
## this file.  Please review the following to ensure GNU General Public
## Licensing requirements will be met:
## http://www.opensource.org/licenses/gpl-license.php
##
## If you are unsure which license is appropriate for your use (for
## instance, you are interested in developing a commercial derivative
## of VisTrails), please contact us at vistrails@sci.utah.edu.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################

"""Module with utilities to inspect bundles, if possible."""

from core.bundles.utils import guess_system, guess_graphical_sudo
import core.bundles.checkbundle # this is on purpose
import os

##############################################################################

def linux_ubuntu_check(package_name):
    import apt_pkg
    apt_pkg.init()
    cache = apt_pkg.GetCache()
    depcache = apt_pkg.GetDepCache(cache)

    def get_single_package(name):
        if type(package) != str:
            raise TypeError("Expected string")
        cache = apt_pkg.GetCache()
        depcache = apt_pkg.GetDepCache(cache)
        records = apt_pkg.GetPkgRecords(cache)
        sourcelist = apt_pkg.GetPkgSourceList()
        pkg = apt.package.Package(cache, depcache, records,
                                  sourcelist, None, cache[sys.argv[1]])
        return pkg

    if type(package_name) == str:
        return get_single_package(package_name).candidateVersion
    elif type(package_name) == list:
        return [get_single_package(name).candidateVersion
                for name in package_name]

def get_version(dependency_dictionary):
    """Tries to determine a bundle version.
    """
    distro = guess_system()
    if not dependency_dictionary.has_key(distro):
        return None
    else:
        callable_ = getattr(core.bundles.checkbundle,
                            distro.replace('-', '_') + '_get_version')
        
        return callable_(dependency_dictionary[distro])
