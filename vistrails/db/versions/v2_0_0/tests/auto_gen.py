###############################################################################
##
# Copyright (C) 2014-2016, New York University.
# Copyright (C) 2011-2014, NYU-Poly.
# Copyright (C) 2006-2011, University of Utah.
# All rights reserved.
# Contact: contact@vistrails.org
##
# This file is part of VisTrails.
##
# "Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
##
# - Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
# - Neither the name of the New York University nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
##
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
###############################################################################

"""generated automatically by generate.py"""

import copy
from itertools import izip


class DBOpmWasGeneratedByTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_effect')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            DBOpmArtifactIdEffectTest.deep_eq_test(
                obj1.db_effect, obj2.db_effect, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_role')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            DBOpmRoleTest.deep_eq_test(
                obj1.db_role, obj2.db_role, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_cause')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            DBOpmProcessIdCauseTest.deep_eq_test(
                obj1.db_cause, obj2.db_cause, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_accounts')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_accounts),
                                 len(obj2.db_accounts))
            for child1, child2 in izip(obj1.db_accounts,
                                       obj2.db_accounts):
                DBOpmAccountIdTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_opm_times')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_opm_times),
                                 len(obj2.db_opm_times))
            for child1, child2 in izip(obj1.db_opm_times,
                                       obj2.db_opm_times):
                DBOpmTimeTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)


class DBConfigKeyTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_name')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_name,
                                 obj2.db_name)
        alternate_key = (obj1.__class__.__name__, 'db_value')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            child1 = obj1.db_value
            child2 = obj2.db_value
            if child1.vtType == 'config_str':
                DBConfigStrTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
            elif child1.vtType == 'config_int':
                DBConfigIntTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
            elif child1.vtType == 'config_float':
                DBConfigFloatTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
            elif child1.vtType == 'config_bool':
                DBConfigBoolTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
            elif child1.vtType == 'configuration':
                DBConfigurationTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)


class DBMashupAliasTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_id,
                                 obj2.db_id)
        alternate_key = (obj1.__class__.__name__, 'db_name')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_name,
                                 obj2.db_name)
        alternate_key = (obj1.__class__.__name__, 'db_component')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            DBMashupComponentTest.deep_eq_test(
                obj1.db_component, obj2.db_component, test_obj, alternate_tests)


class DBGroupTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_id,
                                 obj2.db_id)
        alternate_key = (obj1.__class__.__name__, 'db_workflow')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            DBWorkflowTest.deep_eq_test(
                obj1.db_workflow, obj2.db_workflow, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_cache')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_cache,
                                 obj2.db_cache)
        alternate_key = (obj1.__class__.__name__, 'db_name')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_name,
                                 obj2.db_name)
        alternate_key = (obj1.__class__.__name__, 'db_namespace')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_namespace,
                                 obj2.db_namespace)
        alternate_key = (obj1.__class__.__name__, 'db_package')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_package,
                                 obj2.db_package)
        alternate_key = (obj1.__class__.__name__, 'db_version')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_version,
                                 obj2.db_version)
        alternate_key = (obj1.__class__.__name__, 'db_location')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            DBLocationTest.deep_eq_test(
                obj1.db_location, obj2.db_location, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_functions')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_functions),
                                 len(obj2.db_functions))
            for child1, child2 in izip(sorted(obj1.db_functions, key=lambda x: x.db_id),
                                       sorted(obj2.db_functions, key=lambda x: x.db_id)):
                DBFunctionTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_annotations')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_annotations),
                                 len(obj2.db_annotations))
            for child1, child2 in izip(sorted(obj1.db_annotations, key=lambda x: x.db_id),
                                       sorted(obj2.db_annotations, key=lambda x: x.db_id)):
                DBAnnotationTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_controlParameters')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_controlParameters),
                                 len(obj2.db_controlParameters))
            for child1, child2 in izip(sorted(obj1.db_controlParameters, key=lambda x: x.db_id),
                                       sorted(obj2.db_controlParameters, key=lambda x: x.db_id)):
                DBControlParameterTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)


class DBOpmWasControlledByTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_effect')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            DBOpmProcessIdEffectTest.deep_eq_test(
                obj1.db_effect, obj2.db_effect, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_role')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            DBOpmRoleTest.deep_eq_test(
                obj1.db_role, obj2.db_role, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_cause')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            DBOpmAgentIdTest.deep_eq_test(
                obj1.db_cause, obj2.db_cause, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_accounts')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_accounts),
                                 len(obj2.db_accounts))
            for child1, child2 in izip(obj1.db_accounts,
                                       obj2.db_accounts):
                DBOpmAccountIdTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_starts')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_starts),
                                 len(obj2.db_starts))
            for child1, child2 in izip(obj1.db_starts,
                                       obj2.db_starts):
                DBOpmTimeTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_ends')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_ends),
                                 len(obj2.db_ends))
            for child1, child2 in izip(obj1.db_ends,
                                       obj2.db_ends):
                DBOpmTimeTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)


class DBAddTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_id,
                                 obj2.db_id)
        alternate_key = (obj1.__class__.__name__, 'db_what')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_what,
                                 obj2.db_what)
        alternate_key = (obj1.__class__.__name__, 'db_objectId')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_objectId,
                                 obj2.db_objectId)
        alternate_key = (obj1.__class__.__name__, 'db_parentObjId')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_parentObjId,
                                 obj2.db_parentObjId)
        alternate_key = (obj1.__class__.__name__, 'db_parentObjType')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_parentObjType,
                                 obj2.db_parentObjType)
        alternate_key = (obj1.__class__.__name__, 'db_data')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            child1 = obj1.db_data
            child2 = obj2.db_data
            if child1.vtType == 'module':
                DBModuleTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
            elif child1.vtType == 'location':
                DBLocationTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
            elif child1.vtType == 'annotation':
                DBAnnotationTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
            elif child1.vtType == 'controlParameter':
                DBControlParameterTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
            elif child1.vtType == 'function':
                DBFunctionTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
            elif child1.vtType == 'connection':
                DBConnectionTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
            elif child1.vtType == 'port':
                DBPortTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
            elif child1.vtType == 'parameter':
                DBParameterTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
            elif child1.vtType == 'portSpec':
                DBPortSpecTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
            elif child1.vtType == 'abstraction':
                DBAbstractionTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
            elif child1.vtType == 'group':
                DBGroupTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
            elif child1.vtType == 'other':
                DBOtherTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
            elif child1.vtType == 'plugin_data':
                DBPluginDataTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)


class DBProvGenerationTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_prov_entity')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            DBRefProvEntityTest.deep_eq_test(
                obj1.db_prov_entity, obj2.db_prov_entity, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_prov_activity')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            DBRefProvActivityTest.deep_eq_test(
                obj1.db_prov_activity, obj2.db_prov_activity, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_prov_role')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_prov_role,
                                 obj2.db_prov_role)


class DBOpmUsedTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_effect')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            DBOpmProcessIdEffectTest.deep_eq_test(
                obj1.db_effect, obj2.db_effect, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_role')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            DBOpmRoleTest.deep_eq_test(
                obj1.db_role, obj2.db_role, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_cause')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            DBOpmArtifactIdCauseTest.deep_eq_test(
                obj1.db_cause, obj2.db_cause, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_accounts')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_accounts),
                                 len(obj2.db_accounts))
            for child1, child2 in izip(obj1.db_accounts,
                                       obj2.db_accounts):
                DBOpmAccountIdTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_opm_times')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_opm_times),
                                 len(obj2.db_opm_times))
            for child1, child2 in izip(obj1.db_opm_times,
                                       obj2.db_opm_times):
                DBOpmTimeTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)


class DBOpmArtifactIdCauseTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_id,
                                 obj2.db_id)


class DBRefProvEntityTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_prov_ref')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_prov_ref,
                                 obj2.db_prov_ref)


class DBVtConnectionTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_id,
                                 obj2.db_id)
        alternate_key = (obj1.__class__.__name__, 'db_vt_source')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_vt_source,
                                 obj2.db_vt_source)
        alternate_key = (obj1.__class__.__name__, 'db_vt_dest')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_vt_dest,
                                 obj2.db_vt_dest)
        alternate_key = (obj1.__class__.__name__, 'db_vt_source_port')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_vt_source_port,
                                 obj2.db_vt_source_port)
        alternate_key = (obj1.__class__.__name__, 'db_vt_dest_port')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_vt_dest_port,
                                 obj2.db_vt_dest_port)
        alternate_key = (obj1.__class__.__name__, 'db_vt_source_signature')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_vt_source_signature,
                                 obj2.db_vt_source_signature)
        alternate_key = (obj1.__class__.__name__, 'db_vt_dest_signature')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_vt_dest_signature,
                                 obj2.db_vt_dest_signature)


class DBOpmAccountTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_id,
                                 obj2.db_id)
        alternate_key = (obj1.__class__.__name__, 'db_value')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_value,
                                 obj2.db_value)


class DBGroupExecTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_id,
                                 obj2.db_id)
        alternate_key = (obj1.__class__.__name__, 'db_ts_start')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_ts_start,
                                 obj2.db_ts_start)
        alternate_key = (obj1.__class__.__name__, 'db_ts_end')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_ts_end,
                                 obj2.db_ts_end)
        alternate_key = (obj1.__class__.__name__, 'db_cached')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_cached,
                                 obj2.db_cached)
        alternate_key = (obj1.__class__.__name__, 'db_module_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_module_id,
                                 obj2.db_module_id)
        alternate_key = (obj1.__class__.__name__, 'db_group_name')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_group_name,
                                 obj2.db_group_name)
        alternate_key = (obj1.__class__.__name__, 'db_group_type')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_group_type,
                                 obj2.db_group_type)
        alternate_key = (obj1.__class__.__name__, 'db_completed')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_completed,
                                 obj2.db_completed)
        alternate_key = (obj1.__class__.__name__, 'db_error')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_error,
                                 obj2.db_error)
        alternate_key = (obj1.__class__.__name__, 'db_machine_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_machine_id,
                                 obj2.db_machine_id)
        alternate_key = (obj1.__class__.__name__, 'db_annotations')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_annotations),
                                 len(obj2.db_annotations))
            for child1, child2 in izip(sorted(obj1.db_annotations, key=lambda x: x.db_id),
                                       sorted(obj2.db_annotations, key=lambda x: x.db_id)):
                DBAnnotationTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_item_execs')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_item_execs),
                                 len(obj2.db_item_execs))
            for child1, child2 in izip(sorted(obj1.db_item_execs, key=lambda x: x.db_id),
                                       sorted(obj2.db_item_execs, key=lambda x: x.db_id)):
                if child1.vtType == 'module_exec':
                    DBModuleExecTest.deep_eq_test(
                        child1, child2, test_obj, alternate_tests)
                elif child1.vtType == 'group_exec':
                    DBGroupExecTest.deep_eq_test(
                        child1, child2, test_obj, alternate_tests)
                elif child1.vtType == 'loop_exec':
                    DBLoopExecTest.deep_eq_test(
                        child1, child2, test_obj, alternate_tests)


class DBOpmAgentIdTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_id,
                                 obj2.db_id)


class DBParameterTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_id,
                                 obj2.db_id)
        alternate_key = (obj1.__class__.__name__, 'db_pos')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_pos,
                                 obj2.db_pos)
        alternate_key = (obj1.__class__.__name__, 'db_name')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_name,
                                 obj2.db_name)
        alternate_key = (obj1.__class__.__name__, 'db_type')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_type,
                                 obj2.db_type)
        alternate_key = (obj1.__class__.__name__, 'db_val')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_val,
                                 obj2.db_val)
        alternate_key = (obj1.__class__.__name__, 'db_alias')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_alias,
                                 obj2.db_alias)


class DBVistrailTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_id,
                                 obj2.db_id)
        alternate_key = (obj1.__class__.__name__, 'db_entity_type')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_entity_type,
                                 obj2.db_entity_type)
        alternate_key = (obj1.__class__.__name__, 'db_version')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_version,
                                 obj2.db_version)
        alternate_key = (obj1.__class__.__name__, 'db_name')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_name,
                                 obj2.db_name)
        alternate_key = (obj1.__class__.__name__, 'db_last_modified')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_last_modified,
                                 obj2.db_last_modified)
        alternate_key = (obj1.__class__.__name__, 'db_actions')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_actions),
                                 len(obj2.db_actions))
            for child1, child2 in izip(sorted(obj1.db_actions, key=lambda x: x.db_id),
                                       sorted(obj2.db_actions, key=lambda x: x.db_id)):
                DBActionTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_annotations')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_annotations),
                                 len(obj2.db_annotations))
            for child1, child2 in izip(sorted(obj1.db_annotations, key=lambda x: x.db_id),
                                       sorted(obj2.db_annotations, key=lambda x: x.db_id)):
                DBAnnotationTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_controlParameters')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_controlParameters),
                                 len(obj2.db_controlParameters))
            for child1, child2 in izip(sorted(obj1.db_controlParameters, key=lambda x: x.db_id),
                                       sorted(obj2.db_controlParameters, key=lambda x: x.db_id)):
                DBControlParameterTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_vistrailVariables')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_vistrailVariables),
                                 len(obj2.db_vistrailVariables))
            for child1, child2 in izip(sorted(obj1.db_vistrailVariables, key=lambda x: x.db_uuid),
                                       sorted(obj2.db_vistrailVariables, key=lambda x: x.db_uuid)):
                DBVistrailVariableTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_parameter_explorations')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_parameter_explorations),
                                 len(obj2.db_parameter_explorations))
            for child1, child2 in izip(sorted(obj1.db_parameter_explorations, key=lambda x: x.db_id),
                                       sorted(obj2.db_parameter_explorations, key=lambda x: x.db_id)):
                DBParameterExplorationTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_actionAnnotations')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_actionAnnotations),
                                 len(obj2.db_actionAnnotations))
            for child1, child2 in izip(sorted(obj1.db_actionAnnotations, key=lambda x: x.db_id),
                                       sorted(obj2.db_actionAnnotations, key=lambda x: x.db_id)):
                DBActionAnnotationTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)


class DBOpmArtifactValueTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_value')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            child1 = obj1.db_value
            child2 = obj2.db_value
            if child1.vtType == 'portSpec':
                DBPortSpecTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
            elif child1.vtType == 'function':
                DBFunctionTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)


class DBConfigStrTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_value')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_value,
                                 obj2.db_value)


class DBStartupTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_version')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_version,
                                 obj2.db_version)
        alternate_key = (obj1.__class__.__name__, 'db_configuration')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            DBConfigurationTest.deep_eq_test(
                obj1.db_configuration, obj2.db_configuration, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_enabled_packages')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            DBEnabledPackagesTest.deep_eq_test(
                obj1.db_enabled_packages, obj2.db_enabled_packages, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_disabled_packages')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            DBDisabledPackagesTest.deep_eq_test(
                obj1.db_disabled_packages, obj2.db_disabled_packages, test_obj, alternate_tests)


class DBModuleTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_id,
                                 obj2.db_id)
        alternate_key = (obj1.__class__.__name__, 'db_cache')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_cache,
                                 obj2.db_cache)
        alternate_key = (obj1.__class__.__name__, 'db_name')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_name,
                                 obj2.db_name)
        alternate_key = (obj1.__class__.__name__, 'db_namespace')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_namespace,
                                 obj2.db_namespace)
        alternate_key = (obj1.__class__.__name__, 'db_package')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_package,
                                 obj2.db_package)
        alternate_key = (obj1.__class__.__name__, 'db_version')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_version,
                                 obj2.db_version)
        alternate_key = (obj1.__class__.__name__, 'db_location')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            DBLocationTest.deep_eq_test(
                obj1.db_location, obj2.db_location, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_functions')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_functions),
                                 len(obj2.db_functions))
            for child1, child2 in izip(sorted(obj1.db_functions, key=lambda x: x.db_id),
                                       sorted(obj2.db_functions, key=lambda x: x.db_id)):
                DBFunctionTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_annotations')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_annotations),
                                 len(obj2.db_annotations))
            for child1, child2 in izip(sorted(obj1.db_annotations, key=lambda x: x.db_id),
                                       sorted(obj2.db_annotations, key=lambda x: x.db_id)):
                DBAnnotationTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_controlParameters')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_controlParameters),
                                 len(obj2.db_controlParameters))
            for child1, child2 in izip(sorted(obj1.db_controlParameters, key=lambda x: x.db_id),
                                       sorted(obj2.db_controlParameters, key=lambda x: x.db_id)):
                DBControlParameterTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_portSpecs')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_portSpecs),
                                 len(obj2.db_portSpecs))
            for child1, child2 in izip(sorted(obj1.db_portSpecs, key=lambda x: x.db_id),
                                       sorted(obj2.db_portSpecs, key=lambda x: x.db_id)):
                DBPortSpecTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)


class DBPortTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_id,
                                 obj2.db_id)
        alternate_key = (obj1.__class__.__name__, 'db_type')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_type,
                                 obj2.db_type)
        alternate_key = (obj1.__class__.__name__, 'db_moduleId')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_moduleId,
                                 obj2.db_moduleId)
        alternate_key = (obj1.__class__.__name__, 'db_moduleName')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_moduleName,
                                 obj2.db_moduleName)
        alternate_key = (obj1.__class__.__name__, 'db_name')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_name,
                                 obj2.db_name)
        alternate_key = (obj1.__class__.__name__, 'db_signature')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_signature,
                                 obj2.db_signature)


class DBOpmAgentsTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_agents')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_agents),
                                 len(obj2.db_agents))
            for child1, child2 in izip(sorted(obj1.db_agents, key=lambda x: x.db_id),
                                       sorted(obj2.db_agents, key=lambda x: x.db_id)):
                DBOpmAgentTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)


class DBOpmDependenciesTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_dependencys')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_dependencys),
                                 len(obj2.db_dependencys))
            for child1, child2 in izip(obj1.db_dependencys,
                                       obj2.db_dependencys):
                if child1.vtType == 'opm_used':
                    DBOpmUsedTest.deep_eq_test(
                        child1, child2, test_obj, alternate_tests)
                elif child1.vtType == 'opm_was_generated_by':
                    DBOpmWasGeneratedByTest.deep_eq_test(
                        child1, child2, test_obj, alternate_tests)
                elif child1.vtType == 'opm_was_triggered_by':
                    DBOpmWasTriggeredByTest.deep_eq_test(
                        child1, child2, test_obj, alternate_tests)
                elif child1.vtType == 'opm_was_derived_from':
                    DBOpmWasDerivedFromTest.deep_eq_test(
                        child1, child2, test_obj, alternate_tests)
                elif child1.vtType == 'opm_was_controlled_by':
                    DBOpmWasControlledByTest.deep_eq_test(
                        child1, child2, test_obj, alternate_tests)


class DBPEFunctionTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_id,
                                 obj2.db_id)
        alternate_key = (obj1.__class__.__name__, 'db_module_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_module_id,
                                 obj2.db_module_id)
        alternate_key = (obj1.__class__.__name__, 'db_port_name')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_port_name,
                                 obj2.db_port_name)
        alternate_key = (obj1.__class__.__name__, 'db_is_alias')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_is_alias,
                                 obj2.db_is_alias)
        alternate_key = (obj1.__class__.__name__, 'db_parameters')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_parameters),
                                 len(obj2.db_parameters))
            for child1, child2 in izip(sorted(obj1.db_parameters, key=lambda x: x.db_id),
                                       sorted(obj2.db_parameters, key=lambda x: x.db_id)):
                DBPEParameterTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)


class DBWorkflowTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_id,
                                 obj2.db_id)
        alternate_key = (obj1.__class__.__name__, 'db_entity_type')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_entity_type,
                                 obj2.db_entity_type)
        alternate_key = (obj1.__class__.__name__, 'db_name')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_name,
                                 obj2.db_name)
        alternate_key = (obj1.__class__.__name__, 'db_version')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_version,
                                 obj2.db_version)
        alternate_key = (obj1.__class__.__name__, 'db_last_modified')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_last_modified,
                                 obj2.db_last_modified)
        alternate_key = (obj1.__class__.__name__, 'db_modules')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_modules),
                                 len(obj2.db_modules))
            for child1, child2 in izip(sorted(obj1.db_modules, key=lambda x: x.db_id),
                                       sorted(obj2.db_modules, key=lambda x: x.db_id)):
                if child1.vtType == 'module':
                    DBModuleTest.deep_eq_test(
                        child1, child2, test_obj, alternate_tests)
                elif child1.vtType == 'abstraction':
                    DBAbstractionTest.deep_eq_test(
                        child1, child2, test_obj, alternate_tests)
                elif child1.vtType == 'group':
                    DBGroupTest.deep_eq_test(
                        child1, child2, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_connections')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_connections),
                                 len(obj2.db_connections))
            for child1, child2 in izip(sorted(obj1.db_connections, key=lambda x: x.db_id),
                                       sorted(obj2.db_connections, key=lambda x: x.db_id)):
                DBConnectionTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_annotations')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_annotations),
                                 len(obj2.db_annotations))
            for child1, child2 in izip(sorted(obj1.db_annotations, key=lambda x: x.db_id),
                                       sorted(obj2.db_annotations, key=lambda x: x.db_id)):
                DBAnnotationTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_plugin_datas')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_plugin_datas),
                                 len(obj2.db_plugin_datas))
            for child1, child2 in izip(sorted(obj1.db_plugin_datas, key=lambda x: x.db_id),
                                       sorted(obj2.db_plugin_datas, key=lambda x: x.db_id)):
                DBPluginDataTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_others')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_others),
                                 len(obj2.db_others))
            for child1, child2 in izip(sorted(obj1.db_others, key=lambda x: x.db_id),
                                       sorted(obj2.db_others, key=lambda x: x.db_id)):
                DBOtherTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_vistrail_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_vistrail_id,
                                 obj2.db_vistrail_id)


class DBMashupActionTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_id,
                                 obj2.db_id)
        alternate_key = (obj1.__class__.__name__, 'db_prevId')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_prevId,
                                 obj2.db_prevId)
        alternate_key = (obj1.__class__.__name__, 'db_date')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_date,
                                 obj2.db_date)
        alternate_key = (obj1.__class__.__name__, 'db_user')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_user,
                                 obj2.db_user)
        alternate_key = (obj1.__class__.__name__, 'db_mashup')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            DBMashupTest.deep_eq_test(
                obj1.db_mashup, obj2.db_mashup, test_obj, alternate_tests)


class DBConfigurationTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_config_keys')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_config_keys),
                                 len(obj2.db_config_keys))
            for child1, child2 in izip(sorted(obj1.db_config_keys, key=lambda x: x.db_name),
                                       sorted(obj2.db_config_keys, key=lambda x: x.db_name)):
                DBConfigKeyTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)


class DBChangeTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_id,
                                 obj2.db_id)
        alternate_key = (obj1.__class__.__name__, 'db_what')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_what,
                                 obj2.db_what)
        alternate_key = (obj1.__class__.__name__, 'db_oldObjId')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_oldObjId,
                                 obj2.db_oldObjId)
        alternate_key = (obj1.__class__.__name__, 'db_newObjId')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_newObjId,
                                 obj2.db_newObjId)
        alternate_key = (obj1.__class__.__name__, 'db_parentObjId')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_parentObjId,
                                 obj2.db_parentObjId)
        alternate_key = (obj1.__class__.__name__, 'db_parentObjType')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_parentObjType,
                                 obj2.db_parentObjType)
        alternate_key = (obj1.__class__.__name__, 'db_data')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            child1 = obj1.db_data
            child2 = obj2.db_data
            if child1.vtType == 'module':
                DBModuleTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
            elif child1.vtType == 'location':
                DBLocationTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
            elif child1.vtType == 'annotation':
                DBAnnotationTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
            elif child1.vtType == 'controlParameter':
                DBControlParameterTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
            elif child1.vtType == 'function':
                DBFunctionTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
            elif child1.vtType == 'connection':
                DBConnectionTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
            elif child1.vtType == 'port':
                DBPortTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
            elif child1.vtType == 'parameter':
                DBParameterTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
            elif child1.vtType == 'portSpec':
                DBPortSpecTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
            elif child1.vtType == 'abstraction':
                DBAbstractionTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
            elif child1.vtType == 'group':
                DBGroupTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
            elif child1.vtType == 'other':
                DBOtherTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
            elif child1.vtType == 'plugin_data':
                DBPluginDataTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)


class DBPackageTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_id,
                                 obj2.db_id)
        alternate_key = (obj1.__class__.__name__, 'db_name')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_name,
                                 obj2.db_name)
        alternate_key = (obj1.__class__.__name__, 'db_identifier')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_identifier,
                                 obj2.db_identifier)
        alternate_key = (obj1.__class__.__name__, 'db_codepath')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_codepath,
                                 obj2.db_codepath)
        alternate_key = (obj1.__class__.__name__, 'db_load_configuration')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_load_configuration,
                                 obj2.db_load_configuration)
        alternate_key = (obj1.__class__.__name__, 'db_version')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_version,
                                 obj2.db_version)
        alternate_key = (obj1.__class__.__name__, 'db_description')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_description,
                                 obj2.db_description)
        alternate_key = (obj1.__class__.__name__, 'db_module_descriptors')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_module_descriptors),
                                 len(obj2.db_module_descriptors))
            for child1, child2 in izip(sorted(obj1.db_module_descriptors, key=lambda x: x.db_id),
                                       sorted(obj2.db_module_descriptors, key=lambda x: x.db_id)):
                DBModuleDescriptorTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)


class DBLoopExecTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_id,
                                 obj2.db_id)
        alternate_key = (obj1.__class__.__name__, 'db_ts_start')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_ts_start,
                                 obj2.db_ts_start)
        alternate_key = (obj1.__class__.__name__, 'db_ts_end')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_ts_end,
                                 obj2.db_ts_end)
        alternate_key = (obj1.__class__.__name__, 'db_loop_iterations')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_loop_iterations),
                                 len(obj2.db_loop_iterations))
            for child1, child2 in izip(sorted(obj1.db_loop_iterations, key=lambda x: x.db_id),
                                       sorted(obj2.db_loop_iterations, key=lambda x: x.db_id)):
                DBLoopIterationTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)


class DBConnectionTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_id,
                                 obj2.db_id)
        alternate_key = (obj1.__class__.__name__, 'db_ports')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_ports),
                                 len(obj2.db_ports))
            for child1, child2 in izip(sorted(obj1.db_ports, key=lambda x: x.db_id),
                                       sorted(obj2.db_ports, key=lambda x: x.db_id)):
                DBPortTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)


class DBConfigBoolTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_value')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_value,
                                 obj2.db_value)


class DBActionTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_id,
                                 obj2.db_id)
        alternate_key = (obj1.__class__.__name__, 'db_prevId')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_prevId,
                                 obj2.db_prevId)
        alternate_key = (obj1.__class__.__name__, 'db_date')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_date,
                                 obj2.db_date)
        alternate_key = (obj1.__class__.__name__, 'db_session')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_session,
                                 obj2.db_session)
        alternate_key = (obj1.__class__.__name__, 'db_user')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_user,
                                 obj2.db_user)
        alternate_key = (obj1.__class__.__name__, 'db_annotations')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_annotations),
                                 len(obj2.db_annotations))
            for child1, child2 in izip(sorted(obj1.db_annotations, key=lambda x: x.db_id),
                                       sorted(obj2.db_annotations, key=lambda x: x.db_id)):
                DBAnnotationTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_operations')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_operations),
                                 len(obj2.db_operations))
            for child1, child2 in izip(sorted(obj1.db_operations, key=lambda x: x.db_id),
                                       sorted(obj2.db_operations, key=lambda x: x.db_id)):
                if child1.vtType == 'add':
                    DBAddTest.deep_eq_test(
                        child1, child2, test_obj, alternate_tests)
                elif child1.vtType == 'delete':
                    DBDeleteTest.deep_eq_test(
                        child1, child2, test_obj, alternate_tests)
                elif child1.vtType == 'change':
                    DBChangeTest.deep_eq_test(
                        child1, child2, test_obj, alternate_tests)


class DBStartupPackageTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_name')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_name,
                                 obj2.db_name)
        alternate_key = (obj1.__class__.__name__, 'db_configuration')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            DBConfigurationTest.deep_eq_test(
                obj1.db_configuration, obj2.db_configuration, test_obj, alternate_tests)


class DBConfigIntTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_value')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_value,
                                 obj2.db_value)


class DBOpmProcessIdEffectTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_id,
                                 obj2.db_id)


class DBRefProvPlanTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_prov_ref')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_prov_ref,
                                 obj2.db_prov_ref)


class DBOpmAccountsTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_accounts')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_accounts),
                                 len(obj2.db_accounts))
            for child1, child2 in izip(sorted(obj1.db_accounts, key=lambda x: x.db_id),
                                       sorted(obj2.db_accounts, key=lambda x: x.db_id)):
                DBOpmAccountTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_opm_overlapss')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_opm_overlapss),
                                 len(obj2.db_opm_overlapss))
            for child1, child2 in izip(obj1.db_opm_overlapss,
                                       obj2.db_opm_overlapss):
                DBOpmOverlapsTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)


class DBRefProvAgentTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_prov_ref')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_prov_ref,
                                 obj2.db_prov_ref)


class DBPortSpecTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_id,
                                 obj2.db_id)
        alternate_key = (obj1.__class__.__name__, 'db_name')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_name,
                                 obj2.db_name)
        alternate_key = (obj1.__class__.__name__, 'db_type')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_type,
                                 obj2.db_type)
        alternate_key = (obj1.__class__.__name__, 'db_optional')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_optional,
                                 obj2.db_optional)
        alternate_key = (obj1.__class__.__name__, 'db_depth')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_depth,
                                 obj2.db_depth)
        alternate_key = (obj1.__class__.__name__, 'db_sort_key')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_sort_key,
                                 obj2.db_sort_key)
        alternate_key = (obj1.__class__.__name__, 'db_portSpecItems')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_portSpecItems),
                                 len(obj2.db_portSpecItems))
            for child1, child2 in izip(sorted(obj1.db_portSpecItems, key=lambda x: x.db_id),
                                       sorted(obj2.db_portSpecItems, key=lambda x: x.db_id)):
                DBPortSpecItemTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_min_conns')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_min_conns,
                                 obj2.db_min_conns)
        alternate_key = (obj1.__class__.__name__, 'db_max_conns')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_max_conns,
                                 obj2.db_max_conns)


class DBEnabledPackagesTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_packages')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_packages),
                                 len(obj2.db_packages))
            for child1, child2 in izip(obj1.db_packages,
                                       obj2.db_packages):
                DBStartupPackageTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)


class DBOpmArtifactTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_id,
                                 obj2.db_id)
        alternate_key = (obj1.__class__.__name__, 'db_value')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            DBOpmArtifactValueTest.deep_eq_test(
                obj1.db_value, obj2.db_value, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_accounts')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_accounts),
                                 len(obj2.db_accounts))
            for child1, child2 in izip(obj1.db_accounts,
                                       obj2.db_accounts):
                DBOpmAccountIdTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)


class DBLogTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_id,
                                 obj2.db_id)
        alternate_key = (obj1.__class__.__name__, 'db_entity_type')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_entity_type,
                                 obj2.db_entity_type)
        alternate_key = (obj1.__class__.__name__, 'db_version')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_version,
                                 obj2.db_version)
        alternate_key = (obj1.__class__.__name__, 'db_name')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_name,
                                 obj2.db_name)
        alternate_key = (obj1.__class__.__name__, 'db_last_modified')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_last_modified,
                                 obj2.db_last_modified)
        alternate_key = (obj1.__class__.__name__, 'db_workflow_execs')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_workflow_execs),
                                 len(obj2.db_workflow_execs))
            for child1, child2 in izip(sorted(obj1.db_workflow_execs, key=lambda x: x.db_id),
                                       sorted(obj2.db_workflow_execs, key=lambda x: x.db_id)):
                DBWorkflowExecTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_vistrail_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_vistrail_id,
                                 obj2.db_vistrail_id)


class DBLoopIterationTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_id,
                                 obj2.db_id)
        alternate_key = (obj1.__class__.__name__, 'db_ts_start')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_ts_start,
                                 obj2.db_ts_start)
        alternate_key = (obj1.__class__.__name__, 'db_ts_end')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_ts_end,
                                 obj2.db_ts_end)
        alternate_key = (obj1.__class__.__name__, 'db_iteration')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_iteration,
                                 obj2.db_iteration)
        alternate_key = (obj1.__class__.__name__, 'db_completed')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_completed,
                                 obj2.db_completed)
        alternate_key = (obj1.__class__.__name__, 'db_error')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_error,
                                 obj2.db_error)
        alternate_key = (obj1.__class__.__name__, 'db_item_execs')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_item_execs),
                                 len(obj2.db_item_execs))
            for child1, child2 in izip(sorted(obj1.db_item_execs, key=lambda x: x.db_id),
                                       sorted(obj2.db_item_execs, key=lambda x: x.db_id)):
                if child1.vtType == 'module_exec':
                    DBModuleExecTest.deep_eq_test(
                        child1, child2, test_obj, alternate_tests)
                elif child1.vtType == 'group_exec':
                    DBGroupExecTest.deep_eq_test(
                        child1, child2, test_obj, alternate_tests)
                elif child1.vtType == 'loop_exec':
                    DBLoopExecTest.deep_eq_test(
                        child1, child2, test_obj, alternate_tests)


class DBOpmProcessIdCauseTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_id,
                                 obj2.db_id)


class DBOpmArtifactsTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_artifacts')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_artifacts),
                                 len(obj2.db_artifacts))
            for child1, child2 in izip(sorted(obj1.db_artifacts, key=lambda x: x.db_id),
                                       sorted(obj2.db_artifacts, key=lambda x: x.db_id)):
                DBOpmArtifactTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)


class DBPEParameterTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_id,
                                 obj2.db_id)
        alternate_key = (obj1.__class__.__name__, 'db_pos')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_pos,
                                 obj2.db_pos)
        alternate_key = (obj1.__class__.__name__, 'db_interpolator')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_interpolator,
                                 obj2.db_interpolator)
        alternate_key = (obj1.__class__.__name__, 'db_value')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_value,
                                 obj2.db_value)
        alternate_key = (obj1.__class__.__name__, 'db_dimension')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_dimension,
                                 obj2.db_dimension)


class DBWorkflowExecTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_id,
                                 obj2.db_id)
        alternate_key = (obj1.__class__.__name__, 'db_user')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_user,
                                 obj2.db_user)
        alternate_key = (obj1.__class__.__name__, 'db_ip')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_ip,
                                 obj2.db_ip)
        alternate_key = (obj1.__class__.__name__, 'db_session')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_session,
                                 obj2.db_session)
        alternate_key = (obj1.__class__.__name__, 'db_vt_version')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_vt_version,
                                 obj2.db_vt_version)
        alternate_key = (obj1.__class__.__name__, 'db_ts_start')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_ts_start,
                                 obj2.db_ts_start)
        alternate_key = (obj1.__class__.__name__, 'db_ts_end')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_ts_end,
                                 obj2.db_ts_end)
        alternate_key = (obj1.__class__.__name__, 'db_parent_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_parent_id,
                                 obj2.db_parent_id)
        alternate_key = (obj1.__class__.__name__, 'db_parent_type')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_parent_type,
                                 obj2.db_parent_type)
        alternate_key = (obj1.__class__.__name__, 'db_parent_version')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_parent_version,
                                 obj2.db_parent_version)
        alternate_key = (obj1.__class__.__name__, 'db_completed')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_completed,
                                 obj2.db_completed)
        alternate_key = (obj1.__class__.__name__, 'db_name')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_name,
                                 obj2.db_name)
        alternate_key = (obj1.__class__.__name__, 'db_annotations')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_annotations),
                                 len(obj2.db_annotations))
            for child1, child2 in izip(sorted(obj1.db_annotations, key=lambda x: x.db_id),
                                       sorted(obj2.db_annotations, key=lambda x: x.db_id)):
                DBAnnotationTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_machines')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_machines),
                                 len(obj2.db_machines))
            for child1, child2 in izip(sorted(obj1.db_machines, key=lambda x: x.db_id),
                                       sorted(obj2.db_machines, key=lambda x: x.db_id)):
                DBMachineTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_item_execs')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_item_execs),
                                 len(obj2.db_item_execs))
            for child1, child2 in izip(sorted(obj1.db_item_execs, key=lambda x: x.db_id),
                                       sorted(obj2.db_item_execs, key=lambda x: x.db_id)):
                if child1.vtType == 'module_exec':
                    DBModuleExecTest.deep_eq_test(
                        child1, child2, test_obj, alternate_tests)
                elif child1.vtType == 'group_exec':
                    DBGroupExecTest.deep_eq_test(
                        child1, child2, test_obj, alternate_tests)
                elif child1.vtType == 'loop_exec':
                    DBLoopExecTest.deep_eq_test(
                        child1, child2, test_obj, alternate_tests)


class DBLocationTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_id,
                                 obj2.db_id)
        alternate_key = (obj1.__class__.__name__, 'db_x')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertAlmostEqual(obj1.db_x,
                                       obj2.db_x)
        alternate_key = (obj1.__class__.__name__, 'db_y')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertAlmostEqual(obj1.db_y,
                                       obj2.db_y)


class DBFunctionTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_id,
                                 obj2.db_id)
        alternate_key = (obj1.__class__.__name__, 'db_pos')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_pos,
                                 obj2.db_pos)
        alternate_key = (obj1.__class__.__name__, 'db_name')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_name,
                                 obj2.db_name)
        alternate_key = (obj1.__class__.__name__, 'db_parameters')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_parameters),
                                 len(obj2.db_parameters))
            for child1, child2 in izip(sorted(obj1.db_parameters, key=lambda x: x.db_id),
                                       sorted(obj2.db_parameters, key=lambda x: x.db_id)):
                DBParameterTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)


class DBActionAnnotationTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_id,
                                 obj2.db_id)
        alternate_key = (obj1.__class__.__name__, 'db_key')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_key,
                                 obj2.db_key)
        alternate_key = (obj1.__class__.__name__, 'db_value')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_value,
                                 obj2.db_value)
        alternate_key = (obj1.__class__.__name__, 'db_action_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_action_id,
                                 obj2.db_action_id)
        alternate_key = (obj1.__class__.__name__, 'db_date')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_date,
                                 obj2.db_date)
        alternate_key = (obj1.__class__.__name__, 'db_user')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_user,
                                 obj2.db_user)


class DBProvActivityTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_id,
                                 obj2.db_id)
        alternate_key = (obj1.__class__.__name__, 'db_startTime')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_startTime,
                                 obj2.db_startTime)
        alternate_key = (obj1.__class__.__name__, 'db_endTime')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_endTime,
                                 obj2.db_endTime)
        alternate_key = (obj1.__class__.__name__, 'db_vt_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_vt_id,
                                 obj2.db_vt_id)
        alternate_key = (obj1.__class__.__name__, 'db_vt_type')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_vt_type,
                                 obj2.db_vt_type)
        alternate_key = (obj1.__class__.__name__, 'db_vt_cached')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_vt_cached,
                                 obj2.db_vt_cached)
        alternate_key = (obj1.__class__.__name__, 'db_vt_completed')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_vt_completed,
                                 obj2.db_vt_completed)
        alternate_key = (obj1.__class__.__name__, 'db_vt_machine_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_vt_machine_id,
                                 obj2.db_vt_machine_id)
        alternate_key = (obj1.__class__.__name__, 'db_vt_error')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_vt_error,
                                 obj2.db_vt_error)
        alternate_key = (obj1.__class__.__name__, 'db_is_part_of')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            DBIsPartOfTest.deep_eq_test(
                obj1.db_is_part_of, obj2.db_is_part_of, test_obj, alternate_tests)


class DBProvUsageTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_prov_activity')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            DBRefProvActivityTest.deep_eq_test(
                obj1.db_prov_activity, obj2.db_prov_activity, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_prov_entity')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            DBRefProvEntityTest.deep_eq_test(
                obj1.db_prov_entity, obj2.db_prov_entity, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_prov_role')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_prov_role,
                                 obj2.db_prov_role)


class DBOpmArtifactIdEffectTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_id,
                                 obj2.db_id)


class DBOpmGraphTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_accounts')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            DBOpmAccountsTest.deep_eq_test(
                obj1.db_accounts, obj2.db_accounts, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_processes')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            DBOpmProcessesTest.deep_eq_test(
                obj1.db_processes, obj2.db_processes, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_artifacts')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            DBOpmArtifactsTest.deep_eq_test(
                obj1.db_artifacts, obj2.db_artifacts, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_agents')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            DBOpmAgentsTest.deep_eq_test(
                obj1.db_agents, obj2.db_agents, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_dependencies')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            DBOpmDependenciesTest.deep_eq_test(
                obj1.db_dependencies, obj2.db_dependencies, test_obj, alternate_tests)


class DBIsPartOfTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_prov_ref')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_prov_ref,
                                 obj2.db_prov_ref)


class DBOpmWasDerivedFromTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_effect')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            DBOpmArtifactIdEffectTest.deep_eq_test(
                obj1.db_effect, obj2.db_effect, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_role')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            DBOpmRoleTest.deep_eq_test(
                obj1.db_role, obj2.db_role, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_cause')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            DBOpmArtifactIdCauseTest.deep_eq_test(
                obj1.db_cause, obj2.db_cause, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_accounts')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_accounts),
                                 len(obj2.db_accounts))
            for child1, child2 in izip(obj1.db_accounts,
                                       obj2.db_accounts):
                DBOpmAccountIdTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_opm_times')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_opm_times),
                                 len(obj2.db_opm_times))
            for child1, child2 in izip(obj1.db_opm_times,
                                       obj2.db_opm_times):
                DBOpmTimeTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)


class DBControlParameterTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_id,
                                 obj2.db_id)
        alternate_key = (obj1.__class__.__name__, 'db_name')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_name,
                                 obj2.db_name)
        alternate_key = (obj1.__class__.__name__, 'db_value')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_value,
                                 obj2.db_value)


class DBPluginDataTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_id,
                                 obj2.db_id)
        alternate_key = (obj1.__class__.__name__, 'db_data')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_data,
                                 obj2.db_data)


class DBDeleteTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_id,
                                 obj2.db_id)
        alternate_key = (obj1.__class__.__name__, 'db_what')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_what,
                                 obj2.db_what)
        alternate_key = (obj1.__class__.__name__, 'db_objectId')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_objectId,
                                 obj2.db_objectId)
        alternate_key = (obj1.__class__.__name__, 'db_parentObjId')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_parentObjId,
                                 obj2.db_parentObjId)
        alternate_key = (obj1.__class__.__name__, 'db_parentObjType')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_parentObjType,
                                 obj2.db_parentObjType)


class DBVistrailVariableTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_name')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_name,
                                 obj2.db_name)
        alternate_key = (obj1.__class__.__name__, 'db_uuid')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_uuid,
                                 obj2.db_uuid)
        alternate_key = (obj1.__class__.__name__, 'db_package')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_package,
                                 obj2.db_package)
        alternate_key = (obj1.__class__.__name__, 'db_module')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_module,
                                 obj2.db_module)
        alternate_key = (obj1.__class__.__name__, 'db_namespace')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_namespace,
                                 obj2.db_namespace)
        alternate_key = (obj1.__class__.__name__, 'db_value')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_value,
                                 obj2.db_value)


class DBOpmOverlapsTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_opm_account_ids')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_opm_account_ids),
                                 len(obj2.db_opm_account_ids))
            for child1, child2 in izip(obj1.db_opm_account_ids,
                                       obj2.db_opm_account_ids):
                DBOpmAccountIdTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)


class DBOpmWasTriggeredByTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_effect')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            DBOpmProcessIdEffectTest.deep_eq_test(
                obj1.db_effect, obj2.db_effect, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_role')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            DBOpmRoleTest.deep_eq_test(
                obj1.db_role, obj2.db_role, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_cause')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            DBOpmProcessIdCauseTest.deep_eq_test(
                obj1.db_cause, obj2.db_cause, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_accounts')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_accounts),
                                 len(obj2.db_accounts))
            for child1, child2 in izip(obj1.db_accounts,
                                       obj2.db_accounts):
                DBOpmAccountIdTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_opm_times')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_opm_times),
                                 len(obj2.db_opm_times))
            for child1, child2 in izip(obj1.db_opm_times,
                                       obj2.db_opm_times):
                DBOpmTimeTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)


class DBModuleDescriptorTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_id,
                                 obj2.db_id)
        alternate_key = (obj1.__class__.__name__, 'db_name')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_name,
                                 obj2.db_name)
        alternate_key = (obj1.__class__.__name__, 'db_package')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_package,
                                 obj2.db_package)
        alternate_key = (obj1.__class__.__name__, 'db_namespace')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_namespace,
                                 obj2.db_namespace)
        alternate_key = (obj1.__class__.__name__, 'db_package_version')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_package_version,
                                 obj2.db_package_version)
        alternate_key = (obj1.__class__.__name__, 'db_version')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_version,
                                 obj2.db_version)
        alternate_key = (obj1.__class__.__name__, 'db_base_descriptor_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_base_descriptor_id,
                                 obj2.db_base_descriptor_id)
        alternate_key = (obj1.__class__.__name__, 'db_portSpecs')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_portSpecs),
                                 len(obj2.db_portSpecs))
            for child1, child2 in izip(sorted(obj1.db_portSpecs, key=lambda x: x.db_id),
                                       sorted(obj2.db_portSpecs, key=lambda x: x.db_id)):
                DBPortSpecTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)


class DBOpmRoleTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_value')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_value,
                                 obj2.db_value)


class DBProvDocumentTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_prov_entitys')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_prov_entitys),
                                 len(obj2.db_prov_entitys))
            for child1, child2 in izip(sorted(obj1.db_prov_entitys, key=lambda x: x.db_id),
                                       sorted(obj2.db_prov_entitys, key=lambda x: x.db_id)):
                DBProvEntityTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_prov_activitys')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_prov_activitys),
                                 len(obj2.db_prov_activitys))
            for child1, child2 in izip(sorted(obj1.db_prov_activitys, key=lambda x: x.db_id),
                                       sorted(obj2.db_prov_activitys, key=lambda x: x.db_id)):
                DBProvActivityTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_prov_agents')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_prov_agents),
                                 len(obj2.db_prov_agents))
            for child1, child2 in izip(sorted(obj1.db_prov_agents, key=lambda x: x.db_id),
                                       sorted(obj2.db_prov_agents, key=lambda x: x.db_id)):
                DBProvAgentTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_vt_connections')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_vt_connections),
                                 len(obj2.db_vt_connections))
            for child1, child2 in izip(sorted(obj1.db_vt_connections, key=lambda x: x.db_id),
                                       sorted(obj2.db_vt_connections, key=lambda x: x.db_id)):
                DBVtConnectionTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_prov_usages')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_prov_usages),
                                 len(obj2.db_prov_usages))
            for child1, child2 in izip(obj1.db_prov_usages,
                                       obj2.db_prov_usages):
                DBProvUsageTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_prov_generations')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_prov_generations),
                                 len(obj2.db_prov_generations))
            for child1, child2 in izip(obj1.db_prov_generations,
                                       obj2.db_prov_generations):
                DBProvGenerationTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_prov_associations')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_prov_associations),
                                 len(obj2.db_prov_associations))
            for child1, child2 in izip(obj1.db_prov_associations,
                                       obj2.db_prov_associations):
                DBProvAssociationTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)


class DBOpmProcessesTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_processs')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_processs),
                                 len(obj2.db_processs))
            for child1, child2 in izip(sorted(obj1.db_processs, key=lambda x: x.db_id),
                                       sorted(obj2.db_processs, key=lambda x: x.db_id)):
                DBOpmProcessTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)


class DBOpmAccountIdTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_id,
                                 obj2.db_id)


class DBPortSpecItemTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_id,
                                 obj2.db_id)
        alternate_key = (obj1.__class__.__name__, 'db_pos')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_pos,
                                 obj2.db_pos)
        alternate_key = (obj1.__class__.__name__, 'db_module')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_module,
                                 obj2.db_module)
        alternate_key = (obj1.__class__.__name__, 'db_package')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_package,
                                 obj2.db_package)
        alternate_key = (obj1.__class__.__name__, 'db_namespace')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_namespace,
                                 obj2.db_namespace)
        alternate_key = (obj1.__class__.__name__, 'db_label')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_label,
                                 obj2.db_label)
        alternate_key = (obj1.__class__.__name__, 'db_default')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_default,
                                 obj2.db_default)
        alternate_key = (obj1.__class__.__name__, 'db_values')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_values,
                                 obj2.db_values)
        alternate_key = (obj1.__class__.__name__, 'db_entry_type')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_entry_type,
                                 obj2.db_entry_type)


class DBMashupComponentTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_id,
                                 obj2.db_id)
        alternate_key = (obj1.__class__.__name__, 'db_vtid')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_vtid,
                                 obj2.db_vtid)
        alternate_key = (obj1.__class__.__name__, 'db_vttype')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_vttype,
                                 obj2.db_vttype)
        alternate_key = (obj1.__class__.__name__, 'db_vtparent_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_vtparent_id,
                                 obj2.db_vtparent_id)
        alternate_key = (obj1.__class__.__name__, 'db_vtparent_type')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_vtparent_type,
                                 obj2.db_vtparent_type)
        alternate_key = (obj1.__class__.__name__, 'db_vtpos')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_vtpos,
                                 obj2.db_vtpos)
        alternate_key = (obj1.__class__.__name__, 'db_vtmid')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_vtmid,
                                 obj2.db_vtmid)
        alternate_key = (obj1.__class__.__name__, 'db_pos')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_pos,
                                 obj2.db_pos)
        alternate_key = (obj1.__class__.__name__, 'db_type')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_type,
                                 obj2.db_type)
        alternate_key = (obj1.__class__.__name__, 'db_val')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_val,
                                 obj2.db_val)
        alternate_key = (obj1.__class__.__name__, 'db_minVal')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_minVal,
                                 obj2.db_minVal)
        alternate_key = (obj1.__class__.__name__, 'db_maxVal')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_maxVal,
                                 obj2.db_maxVal)
        alternate_key = (obj1.__class__.__name__, 'db_stepSize')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_stepSize,
                                 obj2.db_stepSize)
        alternate_key = (obj1.__class__.__name__, 'db_strvaluelist')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_strvaluelist,
                                 obj2.db_strvaluelist)
        alternate_key = (obj1.__class__.__name__, 'db_widget')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_widget,
                                 obj2.db_widget)
        alternate_key = (obj1.__class__.__name__, 'db_seq')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_seq,
                                 obj2.db_seq)
        alternate_key = (obj1.__class__.__name__, 'db_parent')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_parent,
                                 obj2.db_parent)


class DBMashupTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_id,
                                 obj2.db_id)
        alternate_key = (obj1.__class__.__name__, 'db_name')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_name,
                                 obj2.db_name)
        alternate_key = (obj1.__class__.__name__, 'db_version')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_version,
                                 obj2.db_version)
        alternate_key = (obj1.__class__.__name__, 'db_aliases')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_aliases),
                                 len(obj2.db_aliases))
            for child1, child2 in izip(sorted(obj1.db_aliases, key=lambda x: x.db_id),
                                       sorted(obj2.db_aliases, key=lambda x: x.db_id)):
                DBMashupAliasTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_type')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_type,
                                 obj2.db_type)
        alternate_key = (obj1.__class__.__name__, 'db_vtid')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_vtid,
                                 obj2.db_vtid)
        alternate_key = (obj1.__class__.__name__, 'db_layout')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_layout,
                                 obj2.db_layout)
        alternate_key = (obj1.__class__.__name__, 'db_geometry')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_geometry,
                                 obj2.db_geometry)
        alternate_key = (obj1.__class__.__name__, 'db_has_seq')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_has_seq,
                                 obj2.db_has_seq)


class DBMachineTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_id,
                                 obj2.db_id)
        alternate_key = (obj1.__class__.__name__, 'db_name')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_name,
                                 obj2.db_name)
        alternate_key = (obj1.__class__.__name__, 'db_os')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_os,
                                 obj2.db_os)
        alternate_key = (obj1.__class__.__name__, 'db_architecture')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_architecture,
                                 obj2.db_architecture)
        alternate_key = (obj1.__class__.__name__, 'db_processor')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_processor,
                                 obj2.db_processor)
        alternate_key = (obj1.__class__.__name__, 'db_ram')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_ram,
                                 obj2.db_ram)


class DBConfigFloatTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_value')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertAlmostEqual(obj1.db_value,
                                       obj2.db_value)


class DBOtherTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_id,
                                 obj2.db_id)
        alternate_key = (obj1.__class__.__name__, 'db_key')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_key,
                                 obj2.db_key)
        alternate_key = (obj1.__class__.__name__, 'db_value')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_value,
                                 obj2.db_value)


class DBRefProvActivityTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_prov_ref')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_prov_ref,
                                 obj2.db_prov_ref)


class DBAbstractionTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_id,
                                 obj2.db_id)
        alternate_key = (obj1.__class__.__name__, 'db_cache')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_cache,
                                 obj2.db_cache)
        alternate_key = (obj1.__class__.__name__, 'db_name')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_name,
                                 obj2.db_name)
        alternate_key = (obj1.__class__.__name__, 'db_namespace')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_namespace,
                                 obj2.db_namespace)
        alternate_key = (obj1.__class__.__name__, 'db_package')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_package,
                                 obj2.db_package)
        alternate_key = (obj1.__class__.__name__, 'db_version')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_version,
                                 obj2.db_version)
        alternate_key = (obj1.__class__.__name__, 'db_internal_version')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_internal_version,
                                 obj2.db_internal_version)
        alternate_key = (obj1.__class__.__name__, 'db_location')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            DBLocationTest.deep_eq_test(
                obj1.db_location, obj2.db_location, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_functions')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_functions),
                                 len(obj2.db_functions))
            for child1, child2 in izip(sorted(obj1.db_functions, key=lambda x: x.db_id),
                                       sorted(obj2.db_functions, key=lambda x: x.db_id)):
                DBFunctionTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_annotations')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_annotations),
                                 len(obj2.db_annotations))
            for child1, child2 in izip(sorted(obj1.db_annotations, key=lambda x: x.db_id),
                                       sorted(obj2.db_annotations, key=lambda x: x.db_id)):
                DBAnnotationTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_controlParameters')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_controlParameters),
                                 len(obj2.db_controlParameters))
            for child1, child2 in izip(sorted(obj1.db_controlParameters, key=lambda x: x.db_id),
                                       sorted(obj2.db_controlParameters, key=lambda x: x.db_id)):
                DBControlParameterTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)


class DBProvAgentTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_id,
                                 obj2.db_id)
        alternate_key = (obj1.__class__.__name__, 'db_vt_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_vt_id,
                                 obj2.db_vt_id)
        alternate_key = (obj1.__class__.__name__, 'db_prov_type')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_prov_type,
                                 obj2.db_prov_type)
        alternate_key = (obj1.__class__.__name__, 'db_prov_label')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_prov_label,
                                 obj2.db_prov_label)
        alternate_key = (obj1.__class__.__name__, 'db_vt_machine_os')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_vt_machine_os,
                                 obj2.db_vt_machine_os)
        alternate_key = (obj1.__class__.__name__, 'db_vt_machine_architecture')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_vt_machine_architecture,
                                 obj2.db_vt_machine_architecture)
        alternate_key = (obj1.__class__.__name__, 'db_vt_machine_processor')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_vt_machine_processor,
                                 obj2.db_vt_machine_processor)
        alternate_key = (obj1.__class__.__name__, 'db_vt_machine_ram')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_vt_machine_ram,
                                 obj2.db_vt_machine_ram)


class DBMashuptrailTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_id,
                                 obj2.db_id)
        alternate_key = (obj1.__class__.__name__, 'db_name')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_name,
                                 obj2.db_name)
        alternate_key = (obj1.__class__.__name__, 'db_version')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_version,
                                 obj2.db_version)
        alternate_key = (obj1.__class__.__name__, 'db_vtVersion')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_vtVersion,
                                 obj2.db_vtVersion)
        alternate_key = (obj1.__class__.__name__, 'db_last_modified')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_last_modified,
                                 obj2.db_last_modified)
        alternate_key = (obj1.__class__.__name__, 'db_actions')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_actions),
                                 len(obj2.db_actions))
            for child1, child2 in izip(sorted(obj1.db_actions, key=lambda x: x.db_id),
                                       sorted(obj2.db_actions, key=lambda x: x.db_id)):
                DBMashupActionTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_annotations')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_annotations),
                                 len(obj2.db_annotations))
            for child1, child2 in izip(sorted(obj1.db_annotations, key=lambda x: x.db_id),
                                       sorted(obj2.db_annotations, key=lambda x: x.db_id)):
                DBAnnotationTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_actionAnnotations')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_actionAnnotations),
                                 len(obj2.db_actionAnnotations))
            for child1, child2 in izip(sorted(obj1.db_actionAnnotations, key=lambda x: x.db_id),
                                       sorted(obj2.db_actionAnnotations, key=lambda x: x.db_id)):
                DBMashupActionAnnotationTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)


class DBRegistryTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_id,
                                 obj2.db_id)
        alternate_key = (obj1.__class__.__name__, 'db_entity_type')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_entity_type,
                                 obj2.db_entity_type)
        alternate_key = (obj1.__class__.__name__, 'db_version')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_version,
                                 obj2.db_version)
        alternate_key = (obj1.__class__.__name__, 'db_root_descriptor_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_root_descriptor_id,
                                 obj2.db_root_descriptor_id)
        alternate_key = (obj1.__class__.__name__, 'db_name')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_name,
                                 obj2.db_name)
        alternate_key = (obj1.__class__.__name__, 'db_last_modified')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_last_modified,
                                 obj2.db_last_modified)
        alternate_key = (obj1.__class__.__name__, 'db_packages')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_packages),
                                 len(obj2.db_packages))
            for child1, child2 in izip(sorted(obj1.db_packages, key=lambda x: x.db_id),
                                       sorted(obj2.db_packages, key=lambda x: x.db_id)):
                DBPackageTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)


class DBOpmAgentTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_id,
                                 obj2.db_id)
        alternate_key = (obj1.__class__.__name__, 'db_value')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_value,
                                 obj2.db_value)
        alternate_key = (obj1.__class__.__name__, 'db_accounts')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_accounts),
                                 len(obj2.db_accounts))
            for child1, child2 in izip(obj1.db_accounts,
                                       obj2.db_accounts):
                DBOpmAccountIdTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)


class DBProvEntityTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_id,
                                 obj2.db_id)
        alternate_key = (obj1.__class__.__name__, 'db_prov_type')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_prov_type,
                                 obj2.db_prov_type)
        alternate_key = (obj1.__class__.__name__, 'db_prov_label')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_prov_label,
                                 obj2.db_prov_label)
        alternate_key = (obj1.__class__.__name__, 'db_prov_value')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_prov_value,
                                 obj2.db_prov_value)
        alternate_key = (obj1.__class__.__name__, 'db_vt_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_vt_id,
                                 obj2.db_vt_id)
        alternate_key = (obj1.__class__.__name__, 'db_vt_type')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_vt_type,
                                 obj2.db_vt_type)
        alternate_key = (obj1.__class__.__name__, 'db_vt_desc')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_vt_desc,
                                 obj2.db_vt_desc)
        alternate_key = (obj1.__class__.__name__, 'db_vt_package')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_vt_package,
                                 obj2.db_vt_package)
        alternate_key = (obj1.__class__.__name__, 'db_vt_version')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_vt_version,
                                 obj2.db_vt_version)
        alternate_key = (obj1.__class__.__name__, 'db_vt_cache')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_vt_cache,
                                 obj2.db_vt_cache)
        alternate_key = (obj1.__class__.__name__, 'db_vt_location_x')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_vt_location_x,
                                 obj2.db_vt_location_x)
        alternate_key = (obj1.__class__.__name__, 'db_vt_location_y')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_vt_location_y,
                                 obj2.db_vt_location_y)
        alternate_key = (obj1.__class__.__name__, 'db_is_part_of')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            DBIsPartOfTest.deep_eq_test(
                obj1.db_is_part_of, obj2.db_is_part_of, test_obj, alternate_tests)


class DBAnnotationTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_id,
                                 obj2.db_id)
        alternate_key = (obj1.__class__.__name__, 'db_key')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_key,
                                 obj2.db_key)
        alternate_key = (obj1.__class__.__name__, 'db_value')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_value,
                                 obj2.db_value)


class DBOpmTimeTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_no_later_than')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_no_later_than,
                                 obj2.db_no_later_than)
        alternate_key = (obj1.__class__.__name__, 'db_no_earlier_than')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_no_earlier_than,
                                 obj2.db_no_earlier_than)
        alternate_key = (obj1.__class__.__name__, 'db_clock_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_clock_id,
                                 obj2.db_clock_id)


class DBParameterExplorationTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_id,
                                 obj2.db_id)
        alternate_key = (obj1.__class__.__name__, 'db_action_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_action_id,
                                 obj2.db_action_id)
        alternate_key = (obj1.__class__.__name__, 'db_name')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_name,
                                 obj2.db_name)
        alternate_key = (obj1.__class__.__name__, 'db_date')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_date,
                                 obj2.db_date)
        alternate_key = (obj1.__class__.__name__, 'db_user')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_user,
                                 obj2.db_user)
        alternate_key = (obj1.__class__.__name__, 'db_dims')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_dims,
                                 obj2.db_dims)
        alternate_key = (obj1.__class__.__name__, 'db_layout')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_layout,
                                 obj2.db_layout)
        alternate_key = (obj1.__class__.__name__, 'db_functions')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_functions),
                                 len(obj2.db_functions))
            for child1, child2 in izip(sorted(obj1.db_functions, key=lambda x: x.db_id),
                                       sorted(obj2.db_functions, key=lambda x: x.db_id)):
                DBPEFunctionTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)


class DBMashupActionAnnotationTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_id,
                                 obj2.db_id)
        alternate_key = (obj1.__class__.__name__, 'db_key')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_key,
                                 obj2.db_key)
        alternate_key = (obj1.__class__.__name__, 'db_value')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_value,
                                 obj2.db_value)
        alternate_key = (obj1.__class__.__name__, 'db_action_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_action_id,
                                 obj2.db_action_id)
        alternate_key = (obj1.__class__.__name__, 'db_date')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_date,
                                 obj2.db_date)
        alternate_key = (obj1.__class__.__name__, 'db_user')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_user,
                                 obj2.db_user)


class DBOpmProcessTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_id,
                                 obj2.db_id)
        alternate_key = (obj1.__class__.__name__, 'db_value')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            DBOpmProcessValueTest.deep_eq_test(
                obj1.db_value, obj2.db_value, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_accounts')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_accounts),
                                 len(obj2.db_accounts))
            for child1, child2 in izip(obj1.db_accounts,
                                       obj2.db_accounts):
                DBOpmAccountIdTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)


class DBDisabledPackagesTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_packages')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_packages),
                                 len(obj2.db_packages))
            for child1, child2 in izip(obj1.db_packages,
                                       obj2.db_packages):
                DBStartupPackageTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)


class DBModuleExecTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_id,
                                 obj2.db_id)
        alternate_key = (obj1.__class__.__name__, 'db_ts_start')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_ts_start,
                                 obj2.db_ts_start)
        alternate_key = (obj1.__class__.__name__, 'db_ts_end')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_ts_end,
                                 obj2.db_ts_end)
        alternate_key = (obj1.__class__.__name__, 'db_cached')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_cached,
                                 obj2.db_cached)
        alternate_key = (obj1.__class__.__name__, 'db_module_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_module_id,
                                 obj2.db_module_id)
        alternate_key = (obj1.__class__.__name__, 'db_module_name')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_module_name,
                                 obj2.db_module_name)
        alternate_key = (obj1.__class__.__name__, 'db_completed')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_completed,
                                 obj2.db_completed)
        alternate_key = (obj1.__class__.__name__, 'db_error')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_error,
                                 obj2.db_error)
        alternate_key = (obj1.__class__.__name__, 'db_machine_id')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_machine_id,
                                 obj2.db_machine_id)
        alternate_key = (obj1.__class__.__name__, 'db_annotations')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_annotations),
                                 len(obj2.db_annotations))
            for child1, child2 in izip(sorted(obj1.db_annotations, key=lambda x: x.db_id),
                                       sorted(obj2.db_annotations, key=lambda x: x.db_id)):
                DBAnnotationTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_loop_execs')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(len(obj1.db_loop_execs),
                                 len(obj2.db_loop_execs))
            for child1, child2 in izip(sorted(obj1.db_loop_execs, key=lambda x: x.db_id),
                                       sorted(obj2.db_loop_execs, key=lambda x: x.db_id)):
                DBLoopExecTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)


class DBProvAssociationTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_prov_activity')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            DBRefProvActivityTest.deep_eq_test(
                obj1.db_prov_activity, obj2.db_prov_activity, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_prov_agent')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            DBRefProvAgentTest.deep_eq_test(
                obj1.db_prov_agent, obj2.db_prov_agent, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_prov_plan')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            DBRefProvPlanTest.deep_eq_test(
                obj1.db_prov_plan, obj2.db_prov_plan, test_obj, alternate_tests)
        alternate_key = (obj1.__class__.__name__, 'db_prov_role')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            test_obj.assertEqual(obj1.db_prov_role,
                                 obj2.db_prov_role)


class DBOpmProcessValueTest(object):

    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        alternate_key = (obj1.__class__.__name__, 'db_value')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](
                    obj1, obj2, test_obj, alternate_tests)
        else:
            child1 = obj1.db_value
            child2 = obj2.db_value
            if child1.vtType == 'module_exec':
                DBModuleExecTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
            elif child1.vtType == 'group_exec':
                DBGroupExecTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
            elif child1.vtType == 'loop_exec':
                DBLoopExecTest.deep_eq_test(
                    child1, child2, test_obj, alternate_tests)
