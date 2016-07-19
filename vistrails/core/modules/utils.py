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
from __future__ import division

from vistrails.core.system import _defaultPkgPrefix, \
    get_vistrails_basic_pkg_id, get_module_registry

def load_cls(cls_item, prefix=None):
    path = None
    if isinstance(cls_item, basestring):
        (path, cls_name) = cls_item.split(':')[:2]
    elif isinstance(cls_item, tuple):
        (path, cls_name) = cls_item
    if path is not None:
        try:
            module = __import__(path, globals(), locals(), [cls_name])
        except ImportError:
            if prefix is None:
                raise
            path = '.'.join([prefix, path])
            module = __import__(path, globals(), locals(), [cls_name])
        return getattr(module, cls_name)
    return cls_item

def create_descriptor_string(package, name, namespace=None,
                             use_package=True):
    package_str = ""
    namespace_str = ""
    if use_package:
        package_str = "%s:" % package
    if namespace:
        namespace_str = "%s|" % namespace
    return "%s%s%s" % (package_str, namespace_str, name)

def parse_descriptor_string(d_string, cur_package=None):
    """parse_descriptor_string will expand names of modules using
    information about the current package and allowing shortcuts
    for any bundled vistrails packages (e.g. "basic" for
    "org.vistrails.vistrails.basic").  It also allows a nicer
    format for namespace/module specification (namespace comes
    fist unlike port specifications where it is after the module
    name...

    Examples:
      "persistence:PersistentInputFile", None -> 
          ("org.vistrails.vistrails.persistence", PersistentInputFile", "")
      "basic:String", None ->
          ("org.vistrails.vistrails.basic", "String", "")
      "NamespaceA|NamespaceB|Module", "org.example.my" ->
          ("org.example.my", "Module", "NamespaceA|NamespaceB")
    """

    package = ''
    qual_name = ''
    name = ''
    namespace = None
    parts = d_string.strip().split(':', 1)
    if len(parts) > 1:
        qual_name = parts[1]
        if '.' in parts[0]:
            package = parts[0]
        else:
            package = '%s.%s' % (_defaultPkgPrefix, parts[0])
    else:
        qual_name = d_string
        if cur_package is None:
            reg = get_module_registry()
            if reg._current_package is not None:
                package = reg._current_package.identifier
            else:
                package = get_vistrails_basic_pkg_id()
        else:
            package = cur_package
    qual_parts = qual_name.rsplit('|', 1)
    if len(qual_parts) > 1:
        namespace, name = qual_parts
    else:
        name = qual_name
    return (package, name, namespace)

def parse_port_spec_item_string(spec, cur_package=None):
    spec = spec.strip()
    spec_arr = spec.split(':', 2)
    if len(spec_arr) > 2:
        # switch format of spec to more natural
        # <package>:<namespace>|<name> for descriptor parsing
        spec = '%s:%s|%s' % (spec_arr[0], spec_arr[2], spec_arr[1])
    return parse_descriptor_string(spec, cur_package)

def create_port_spec_item_string(package, name, namespace=None, 
                                 old_style=False):
    if old_style:
        if namespace:
            namespace = ':' + namespace
        return '%s:%s%s' % (package, name, namespace)
    else:
        return create_descriptor_string(package, name, namespace)

def parse_port_spec_string(p_string, cur_package=None):
    port_spec = p_string.strip()
    if port_spec.startswith('('):
        port_spec = port_spec[1:]
    if port_spec.endswith(')'):
        port_spec = port_spec[:-1]
    if port_spec.strip() == '':
        return []

    specs_list = []
    for spec in port_spec.split(','):
        specs_list.append(parse_port_spec_item_string(spec, 
                                                      cur_package))
    return specs_list


def create_port_spec_string(specs_list, old_style=False):
    spec_items = []
    for specs in specs_list:
        if len(specs) == 3:
            pkg, name, ns = specs
        elif len(specs) == 2:
            pkg, name = specs
            ns = None
        else:
            raise TypeError("create_port_spec_string() got spec tuple "
                            "with %d elements" % len(specs))
        spec_items.append(create_port_spec_item_string(pkg, name, ns,
                                                       old_style))
    return '(%s)' % ','.join(spec_items)

def expand_port_spec_string(p_string, cur_package=None, 
                            old_style=False):
    specs_list = parse_port_spec_string(p_string, cur_package)
    return create_port_spec_string(specs_list, old_style)


def make_modules_dict(*dcts, **kwargs):
    """Makes a dictionary suitable to be exposed as the '_modules' of a package.

    This combines dictionaries hierarchically to make a global dict from other
    "sub-dicts", allowing to structure a package with subpackages.

    For example, you could have:
        a/aa.py:
            _modules = {'aa': [Some, Module]}
        a/__init__.py:
            from .aa import _modules as aa_modules
            from .ab import _modules as bb_modules
            _modules = make_modules_dict(aa_modules, bb_modules, namespace='a')
        b.py:
            _modules = {'b': [Other, Modules]}
        init.py:
            from .a import _modules as a_modules
            from .b import _modules as b_modules
            _modules = make_modules_dict(a_modules, b_modules)

    The resulting module hierarchy will be:
        a.aa.Some, a.aa.Module
        b.Other, b.Modules
    """
    namespace = kwargs.pop('namespace', '')
    if kwargs:
        raise TypeError("make_modules_dict got unexpected keyword arguments")
    if namespace:
        build_namespace = lambda n: '%s|%s' % (namespace, n)
    else:
        build_namespace = lambda n: n

    dct = dict()
    for d in dcts:
        if not isinstance(d, dict):
            d = {'': d}

        for subname, sublist in d.iteritems():
            if subname:
                name = build_namespace(subname)
            else:
                name = namespace
            dct.setdefault(name, []).extend(sublist)

    return dct


###############################################################################

import unittest


class UnorderedList(object):
    def __init__(self, *elems):
        self._set = set(elems)

    def __eq__(self, other):
        return set(other) == self._set

    def __str__(self):
        return 'ul(%s)' % ', '.join(repr(e) for e in self._set)

    def __repr__(self):
        return str(self)


class TestModulesDict(unittest.TestCase):
    def test_modulesdict(self):
        ul = UnorderedList
        pkg_a_aa = {'aa': [1, 2], 'aa|n': [3]}
        pkg_a_ab = {'ab': [4, 5]}
        pkg_a = make_modules_dict(pkg_a_aa, pkg_a_ab, [12, 13], namespace='a')
        self.assertEqual(set(pkg_a.keys()),
                         set(['a', 'a|aa', 'a|aa|n', 'a|ab']))
        pkg_b = {'b': [6, 7]}
        glob = [10, 11]
        more = {'a|aa': [8, 9]}
        pkg = make_modules_dict(pkg_a, pkg_b, glob, more)
        self.assertEqual(
                pkg,
                {
                    '': ul(10, 11),
                    'a': ul(12, 13),
                    'a|aa': ul(1, 2, 8, 9),
                    'a|aa|n': ul(3),
                    'a|ab': ul(4, 5),
                    'b': ul(6, 7)})
