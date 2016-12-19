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
"""Hasher class for vistrail items."""
from __future__ import division

import unittest
from vistrails.core.cache.utils import hash_list

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
    def control_param_signature(control_param, constant_hasher_map={}):
        hasher = sha_hash()
        u = hasher.update
        u(control_param.name)
        u(control_param.value)
        return hasher.digest()

    @staticmethod
    def connection_signature(c):
        hasher = sha_hash()
        u = hasher.update
        u(c.source.name)
        u(c.destination.name)
        return hasher.digest()

    @staticmethod
    def port_spec_signature(ps, constant_hasher_map={}):
        hasher = sha_hash()
        u = hasher.update
        u(ps.type)
        u(ps.name)
        u(ps.sigstring)
        u('%d' % ps.depth)
        return hasher.digest()

    @staticmethod
    def connection_subpipeline_signature(c, source_sig, dest_sig):
        """Returns the signature for the connection, including source and dest
        subpipelines

        """
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
        u(hash_list(obj.functions, Hasher.function_signature,
                    constant_hasher_map))
        u(hash_list(obj.control_parameters, Hasher.control_param_signature,
                    constant_hasher_map))
        u(hash_list(obj.port_spec_list, Hasher.port_spec_signature,
                    constant_hasher_map))
        return hasher.digest()

    @staticmethod
    def subpipeline_signature(module_sig, upstream_sigs):
        """Returns the signature for a subpipeline, given the signatures for
        the upstream pipelines and connections.

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
        """compound_signature(list of signatures) -> sha digest returns the
        signature of the compound object formed by the list of
        signatures, assuming the list order is irrelevant

        """
        hasher = sha_hash()
        for h in sorted(sig_list):
            hasher.update(h)
        return hasher.digest()


##############################################################################
# Unit tests


class TestCacheHash(unittest.TestCase):
    def test_outputportspec_cache(self):
        """
        Test that signature hash includes port specs

        If it is not included, a module with different port spec may
        be used in the cache, leading to an exception.
        """
        from vistrails import api
        from vistrails.core.vistrail.port_spec import PortSpec
        api.new_vistrail()
        c = api.get_current_controller()
        ps = api.add_module(0, 0, 'org.vistrails.vistrails.basic', 'PythonSource', '')
        api.change_parameter(ps.id, 'source', ['a = b = 1\ncache_this()'])
        so = api.add_module(0, 0, 'org.vistrails.vistrails.basic', 'Integer', '')

        api.add_port_spec(ps.id, PortSpec(name='a', type='output', sigstring='org.vistrails.vistrails.basic:Integer'))
        api.add_connection(ps.id, 'a', so.id, 'value')
        # adds ps to cache
        self.assertEqual(c.execute_current_workflow()[0][0].errors, {})

        api.add_port_spec(ps.id, PortSpec(name='b', type='output', sigstring='org.vistrails.vistrails.basic:Integer'))
        api.add_connection(ps.id, 'b', so.id, 'value')
        # will fail if outputportspec is not hashed and cache is reused
        self.assertEqual(c.execute_current_workflow()[0][0].errors, {})
