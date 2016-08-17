<%text>###############################################################################
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
</%text>
"""generated automatically by generate.py"""

import copy
from itertools import izip

% for obj in objs:
class ${obj.getClassName()}Test(object):
    @staticmethod
    def deep_eq_test(obj1, obj2, test_obj, alternate_tests={}):
        test_obj.assertEqual(obj1.__class__, obj2.__class__)
        if obj1 is None:
            return
        % for field in obj.getPythonFields():
        alternate_key = (obj1.__class__.__name__, '${field.getFieldName()}')
        if alternate_key in alternate_tests:
            # None means pass the test, else we should have a function
            if alternate_tests[alternate_key] is not None:
                alternate_tests[alternate_key](obj1, obj2, test_obj, alternate_tests)
        else:
            % if field.isReference():
            % if field.isPlural():
            test_obj.assertEqual(len(obj1.${field.getFieldName()}),
                             len(obj2.${field.getFieldName()}))
            % if field.getReferencedObject().getKey() is not None:
            for child1, child2 in izip(sorted(obj1.${field.getFieldName()}, key=lambda x: x.${field.getReferencedObject().getKey().getFieldName()}),
                                   sorted(obj2.${field.getFieldName()}, key=lambda x: x.${field.getReferencedObject().getKey().getFieldName()})):
            % else:
            for child1, child2 in izip(obj1.${field.getFieldName()},
                                   obj2.${field.getFieldName()}):
            % endif
                % if field.isChoice():
                <% cond = 'if' %> \\
                % for prop in field.properties:
                ${cond} child1.vtType == \
                    '${prop.getReferencedObject().getRegularName()}':
                    ${prop.getReferencedObject().getClassName()}Test. \!
                    deep_eq_test(child1, child2, test_obj, alternate_tests)
                <% cond = 'elif' %> \\
                % endfor
                % else:
                ${field.getReferencedObject().getClassName()}Test. \!
                deep_eq_test(child1, child2, test_obj, alternate_tests)
                % endif
            % else:
            % if field.isChoice():
            child1 = obj1.${field.getFieldName()}
            child2 = obj2.${field.getFieldName()}
            <% cond = 'if' %> \\
            % for prop in field.properties:
            ${cond} child1.vtType == \
                '${prop.getReferencedObject().getRegularName()}':
                ${prop.getReferencedObject().getClassName()}Test. \!
                deep_eq_test(child1, child2, test_obj, alternate_tests)
            <% cond = 'elif' %> \\
            % endfor
            % else:
            ${field.getReferencedObject().getClassName()}Test. \!
            deep_eq_test(obj1.${field.getFieldName()}, obj2.${field.getFieldName()}, test_obj, alternate_tests)
            % endif
            % endif
            % else:
            % if field.getType() == 'float':
            test_obj.assertAlmostEqual(obj1.${field.getFieldName()},
                                       obj2.${field.getFieldName()})
            % else:
            test_obj.assertEqual(obj1.${field.getFieldName()},
                                   obj2.${field.getFieldName()})
            % endif
            % endif
        % endfor

% endfor
