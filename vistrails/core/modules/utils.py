###############################################################################
##
## Copyright (C) 2011-2013, NYU-Poly.
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
import vistrails.core
from vistrails.core.system import get_vistrails_default_pkg_prefix

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
            package = '%s.%s' % (get_vistrails_default_pkg_prefix(), parts[0])
    else:
        qual_name = d_string
        if cur_package is None:
            from vistrails.core.modules.module_registry import get_module_registry
            reg = get_module_registry()
            if reg._current_package is not None:
                package = reg._current_package.identifier
            else:
                import vistrails.core.modules.basic_modules
                basic_pkg = vistrails.core.modules.basic_modules.identifier
                package = basic_pkg
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
    return '(' + ','.join(create_port_spec_item_string(
            *(specs + ((None, old_style) if len(specs) < 3 else (old_style,))))
                          for specs in specs_list) + ')'

def expand_port_spec_string(p_string, cur_package=None, 
                            old_style=False):
    specs_list = parse_port_spec_string(p_string, cur_package)
    return create_port_spec_string(specs_list, old_style)
