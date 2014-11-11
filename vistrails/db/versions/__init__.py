###############################################################################
##
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
##  - Neither the name of the University of Utah nor the names of its 
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
from itertools import izip
import os

from vistrails.core.system import vistrails_root_directory
from vistrails.db import VistrailsDBException

currentVersion = '1.0.4'

def getVersionDAO(version=None):
    if version is None:
        version = currentVersion
    persistence_dir = 'vistrails.db.versions.' + get_version_name(version) + \
        '.persistence'
    try:
        persistence = __import__(persistence_dir, {}, {}, [''])
    except ImportError as e:
        if str(e).startswith('No module named v'):
            # assume version is not available
            msg = "Cannot find DAO for version '%s'" % version
            raise VistrailsDBException(msg)
        # assume other error
        import traceback
        raise VistrailsDBException(traceback.format_exc())
    return persistence.DAOList()

def translate_object(obj, method_name, version=None, target_version=None):
    if version is None:
        version = obj.version
    if target_version is None:
        target_version = currentVersion

    version_map = {
        '0.3.0': '0.3.1',
        '0.3.1': '0.6.0',
        '0.5.0': '0.6.0',
        '0.6.0': '0.7.0',
        '0.7.0': '0.8.0',
        '0.8.0': '0.8.1',
        '0.8.1': '0.9.0',
        '0.9.0': '0.9.1',
        '0.9.1': '0.9.3',
        '0.9.2': '0.9.3',
        '0.9.3': '0.9.4',
        '0.9.4': '0.9.5',
        '0.9.5': '1.0.0',
        '1.0.0': '1.0.1',
        '1.0.1': '1.0.2',
        '1.0.2': '1.0.3',
        '1.0.3': '1.0.4',
        }

    rev_version_map = {
        '1.0.4': '1.0.3',
        '1.0.3': '1.0.2',
        '1.0.2': '1.0.1',
        '1.0.1': '1.0.0',
        '1.0.0': '0.9.5',
        '0.9.5': '0.9.4',
        '0.9.4': '0.9.3',
        }

    def get_translate_module(map, start_version, end_version):
        translate_dir = 'vistrails.db.versions.' + \
            get_version_name(end_version) + '.translate.' + \
            get_version_name(start_version)
        return __import__(translate_dir, {}, {}, [''])

    path = []
    old_tuple = version.split('.')
    new_tuple = target_version.split('.')
    map = version_map
    for i, j in izip(old_tuple, new_tuple):
        if i < j:
            # forward
            break
        elif i > j:
            # reverse
            map = rev_version_map
            break

    # don't get stuck in an infinite loop
    count = 0
    while version != target_version:
        if count > len(map):
            break
        next_version = map[version]
        try:
            translate_module = get_translate_module(map, version, next_version)
        except Exception, e:
            import traceback
            raise VistrailsDBException("Cannot translate version: "
                                       "error loading translation version %s method '%s': %s" % \
                                           (version, method_name, traceback.format_exc()))
        if not hasattr(translate_module, method_name):
            raise VistrailsDBException("Cannot translate version: "
                                       "version %s missing method '%s'" % \
                                           (version, method_name))
        obj = getattr(translate_module, method_name)(obj)
        version = next_version
        count += 1

    if version != target_version:
        msg = "An error occurred when translating,"
        msg += "only able to translate to version '%s'" % version
        raise VistrailsDBException(msg)

    return obj

def translate_vistrail(vistrail, version=None, target_version=None):
    return translate_object(vistrail, 'translateVistrail', version, 
                            target_version)

def translate_workflow(workflow, version=None, target_version=None):
    return translate_object(workflow, 'translateWorkflow', version, 
                            target_version)

def translate_log(log, version=None, target_version=None):
    return translate_object(log, 'translateLog', version, target_version)

def translate_registry(registry, version=None, target_version=None):
    return translate_object(registry, 'translateRegistry', version, 
                            target_version)

def translate_startup(startup, version=None, target_version=None):
    return translate_object(startup, 'translateStartup', version,
                            target_version)

def get_version_name(version_no):
    return 'v' + version_no.replace('.', '_')

def getVersionSchemaDir(version=None):
    if version is None:
        version = currentVersion
    versionName = get_version_name(version)
    schemaDir = os.path.join(vistrails_root_directory(), 'db', 'versions', 
                             versionName, 'schemas', 'sql')
    return schemaDir
