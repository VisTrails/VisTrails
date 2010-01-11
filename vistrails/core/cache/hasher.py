############################################################################
##
## Copyright (C) 2006-2010 University of Utah. All rights reserved.
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
"""Hasher class for vistrail items."""

from core.cache.utils import hash_list

try:
    import hashlib
    sha_hash = hashlib.sha1
except ImportError:
    import sha
    sha_hash = sha.new

##############################################################################

class Hasher(object):

    @staticmethod
    def parameter_signature(p, constant_hasher_map={}):
        k = (p.identifier, p.type, p.namespace)
        custom_hasher = constant_hasher_map.get(k, None)
        if custom_hasher:
            return custom_hasher(p)
        else:
            hasher = sha_hash()
            u = hasher.update
            u(p.type)
            u(p.identifier)
            u(p.namespace or "")
            u(p.strValue)
            u(p.name)
            u(p.evaluatedStrValue)
            return hasher.digest()

    @staticmethod
    def function_signature(function, constant_hasher_map={}):
        hasher = sha_hash()
        u = hasher.update
        u(function.name)
        u(function.returnType)
        u(hash_list(function.params,
                    Hasher.parameter_signature,
                    constant_hasher_map))
        return hasher.digest()

    @staticmethod
    def connection_signature(c):
        hasher = sha_hash()
        u = hasher.update
        u(c.source.name)
        u(c.destination.name)
        return hasher.digest()

    @staticmethod
    def connection_subpipeline_signature(c, source_sig, dest_sig):
        """Returns the signature for the connection, including source
and dest subpipelines"""
        hasher = sha_hash()
        u = hasher.update
        u(Hasher.connection_signature(c))
        u(source_sig)
        u(dest_sig)
        return hasher.digest()

    @staticmethod
    def module_signature(obj, constant_hasher_map={}):
        hasher = sha_hash()
        u = hasher.update
        u(obj.module_descriptor.name)
        u(obj.module_descriptor.package)
        u(obj.module_descriptor.namespace or '')
        u(obj.module_descriptor.package_version or '')
        u(obj.module_descriptor.version or '')
        u(hash_list(obj.functions, Hasher.function_signature, constant_hasher_map))
        return hasher.digest()

    @staticmethod
    def subpipeline_signature(module_sig, upstream_sigs):
        """Returns the signature for a subpipeline, given the
signatures for the upstream pipelines and connections.

        WARNING: For efficiency, upstream_sigs is mutated!
        """
        hasher = sha_hash()
        hasher.update(module_sig)
        upstream_sigs.sort()
        for pipeline_connection_sig in upstream_sigs:
            hasher.update(pipeline_connection_sig)
        return hasher.digest()

    @staticmethod
    def compound_signature(sig_list):
        """compound_signature(list of signatures) -> sha digest
        returns the signature of the compound object formed by the list
        of signatures, assuming the list order is irrelevant"""
        hasher = sha_hash()
        for h in sorted(sig_list):
            hasher.update(h)
        return hasher.digest()
