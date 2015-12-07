#!/usr/bin/env python
###############################################################################
##
## Copyright (C) 2014-2015, New York University.
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
""" Methods for handling changes in specs

compute_diff - generate and print diff between 2 specs
apply_diff - apply diff changes to a spec
"""

from __future__ import division

from xml.etree import ElementTree as ET
from specs import SpecList


def edit_distance(s1, s2):
    """ Calculates string edit distance
    """
    m=len(s1)+1
    n=len(s2)+1

    tbl = {}
    for i in range(m): tbl[i,0]=i
    for j in range(n): tbl[0,j]=j
    for i in range(1, m):
        for j in range(1, n):
            cost = 0 if s1[i-1] == s2[j-1] else 1
            tbl[i,j] = min(tbl[i, j-1]+1, tbl[i-1, j]+1, tbl[i-1, j-1]+cost)

    return tbl[i,j]


def string_similarity(s1, s2):
    """ Normalized for length so that partial matches are scored higher

    """
    if s1 == s2:
        return max(len(s1), len(s2))
    score = 1 - float(edit_distance(s1, s2)) / max(len(s1), len(s2))
    #print s1, s2, score
    return score


def all_specs(input_port_spec):
    """ Return all alternate specs
    """
    return [input_port_spec] + input_port_spec.alternate_specs


def module_similarity(s1, s2):
    """ default module similarity function
        adds name and port similarity
    """
    # string_similarity can actually be used on any list
    s1_port_specs = sorted([s.name for spec in s1.input_port_specs
                     for s in all_specs(spec)])
    s2_port_specs = sorted([s.name for spec in s2.input_port_specs
                     for s in all_specs(spec)])
    input_port_score = 1 + string_similarity(s1_port_specs, s2_port_specs)

    s1_port_specs = [s.name for s in s1.output_port_specs]
    s2_port_specs = [s.name for s in s2.output_port_specs]
    output_port_score = 1 + string_similarity(s1_port_specs, s2_port_specs)

    name_score = 1 + string_similarity(s1.name.lower(), s2.name.lower())

    return name_score + input_port_score + output_port_score


def port_similarity(p1, p2):
    """ default port similarity function
        checks name similarity for ports of same type
        if names don't match it is still a possible match
    """
    if p1.port_type != p2.port_type:
        return 0
    score = 1 + string_similarity(p1.name.lower(), p2.name.lower())
    #print p1.name, p2.name, score
    return score


def compute_ps_diff(root, in_ps_list, out_ps_list, code_ref, qualifier,
                    port=None, show_docstring=True):
    if qualifier == "alternate":
        if port is None:
            raise ValueError("Must specify port with alternate")
        out_port_specs = dict((ps.name, ps) for ps in out_ps_list)
        in_port_specs = dict((ps.name, ps) for ps in in_ps_list)
    else:
        out_port_specs = dict((ps.arg, ps) for ps in out_ps_list)
        in_port_specs = dict((ps.arg, ps) for ps in in_ps_list)

    out_port_specs_set = set(out_port_specs.iterkeys())
    in_port_specs_set = set(in_port_specs.iterkeys())

    for arg in in_port_specs_set - out_port_specs_set:
        if show_docstring or arg != 'docstring':
            print "--- %s.%s.%s" % (code_ref, qualifier, arg)
        elt = ET.Element("deletePortSpec")
        elt.set("code_ref", code_ref)
        if qualifier == "alternate":
            elt.set("port", port)
            elt.set("altName", arg)
        else:
            elt.set("port", arg)
        elt.set("type", qualifier)
        root.append(elt)

    for arg, out_ps in out_port_specs.iteritems():
        if arg not in in_port_specs:
            if show_docstring or arg != 'docstring':
                print "+++ %s.%s.%s %s" % (code_ref, qualifier, arg,
                                           ET.tostring(out_ps.to_xml()))
            elt = ET.Element("addPortSpec")
            elt.set("code_ref", code_ref)
            if qualifier == "alternate":
                elt.set("port", port)
                elt.set("altName", arg)
                out_ps.xml_name = 'alternateSpec'
            else:
                elt.set("port", arg)
            elt.set("type", qualifier)
            subelt = ET.Element("value")
            subelt.append(out_ps.to_xml())
            elt.append(subelt)
            root.append(elt)
            continue

        in_ps = in_port_specs[arg]

        for attr in out_ps.attrs:
            in_val = getattr(in_ps, attr) 
            out_val = getattr(out_ps, attr)
            if in_val != out_val:
                if show_docstring or attr != 'docstring':
                    print ("CCC %s.%s.%s.%s (%s -> %s)" %
                           (code_ref, qualifier, arg, attr, in_val, out_val))
                elt = ET.Element("changePortSpec")
                elt.set("code_ref", code_ref)
                if qualifier == "alternate":
                    elt.set("port", port)
                    elt.set("altName", arg)
                else:
                    elt.set("port", arg)
                elt.set("type", qualifier)
                elt.set("attr", attr)
                subelt = ET.Element("value")
                subelt.text = out_ps.get_raw(attr)  # serializes value
                elt.append(subelt)
                root.append(elt)
        # only do this for input right now
        if qualifier == "input":
            compute_ps_diff(root, in_ps.alternate_specs, out_ps.alternate_specs,
                            code_ref, "alternate", arg, show_docstring=show_docstring)


def compute_diff(module_spec, in_fname, out_fname, diff_fname=None, show_docstring=True):
    in_specs = SpecList.read_from_xml(in_fname, module_spec)
    out_specs = SpecList.read_from_xml(out_fname, module_spec)

    in_refs = dict((spec.code_ref, spec) for spec in in_specs.module_specs)
    out_refs = dict((spec.code_ref, spec) for spec in out_specs.module_specs)
    
    in_refs_set = set(in_refs.iterkeys())
    out_refs_set = set(out_refs.iterkeys())

    root = ET.Element("diff")

    for ref in in_refs_set - out_refs_set:
        print "--- %s" % ref
        elt = ET.Element("deleteModule")
        elt.set("code_ref", ref)
        root.append(elt)

    for code_ref, out_spec in out_refs.iteritems():
        # need to check port specs, which removed, which added
        if code_ref not in in_refs:
            print "+++ %s %s" % (ref, ET.tostring(out_spec.to_xml()))
            elt = ET.Element("addModule")
            elt.set("code_ref", ref)
            subelt = ET.Element("value")
            subelt.append(out_spec.to_xml())
            elt.append(subelt)
            root.append(elt)
            continue

        in_spec = in_refs[code_ref]

        for attr in module_spec.attrs:
            in_val = getattr(in_spec, attr)
            out_val = getattr(out_spec, attr)
            if in_val != out_val:
                if show_docstring or attr != 'docstring':
                    print "CCC %s.%s %s" % (out_spec.code_ref, attr, out_val)
                elt = ET.Element("changeModule")
                elt.set("code_ref", out_spec.code_ref)
                elt.set("attr", attr)
                subelt = ET.Element("value")
                subelt.text = out_spec.get_raw(attr)  # serializes value
                elt.append(subelt)
                root.append(elt)

        compute_ps_diff(root, in_spec.input_port_specs, out_spec.input_port_specs,
                        code_ref, "input", show_docstring=show_docstring)
        compute_ps_diff(root, in_spec.output_port_specs, 
                        out_spec.output_port_specs,
                        code_ref, "output",
                        show_docstring=show_docstring)

    tree = ET.ElementTree(root)

    def indent(elem, level=0):
        i = "\n" + level*"  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                indent(elem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
    indent(tree.getroot())

    if diff_fname:
        tree.write(diff_fname)


def apply_diff(module_spec, in_fname, diff_fname, out_fname):
    in_specs = SpecList.read_from_xml(in_fname, module_spec)
    
    in_refs = dict((spec.code_ref, spec)
                   for spec in in_specs.module_specs)
    in_ips_refs = dict(((spec.code_ref, ps.arg), ps)
                       for spec in in_specs.module_specs 
                       for ps in spec.input_port_specs)
    in_ops_refs = dict(((spec.code_ref, ps.arg), ps)
                       for spec in in_specs.module_specs
                       for ps in spec.output_port_specs)
    in_alt_refs = dict(((spec.code_ref, ps.arg, alt_ps.name), alt_ps)
                       for spec in in_specs.module_specs
                       for ps in spec.input_port_specs
                       for alt_ps in ps.alternate_specs)

    tree = ET.parse(diff_fname)
    for elt in tree.getroot():
        code_ref = elt.get("code_ref")
        m_spec = in_refs[code_ref]
        port = elt.get("port", None)
        if port:
            port_type = elt.get("type")
            if port_type == "alternate":
                alt_name = elt.get("altName")
        if elt.tag.startswith('delete'):
            if port:
                if port_type == "input":
                    port_spec = in_ips_refs[(code_ref, port)]
                    print "deleting", (code_ref, port)
                    m_spec.input_port_specs.remove(port_spec)
                elif port_type == 'output':
                    port_spec = in_ops_refs[(code_ref, port)]
                    m_spec.output_port_specs.remove(port_spec)
                elif port_type == 'alternate':
                    ps = in_ips_refs[(code_ref, port)][1]
                    alt_spec = in_alt_refs[(code_ref, port, alt_name)]
                    ps.alternate_specs.remove(alt_spec)
                else:
                    raise ValueError('Cannot access list of type "%s"' %
                                     port_type)
            else:
                in_specs.module_specs.remove(m_spec)
        elif elt.tag.startswith('add'):
            for child in elt.getchildren():
                if child.tag == 'value':
                    for subchild in child.getchildren():
                        value = subchild
            if port:
                if port_type == "input":
                    m_spec.input_port_specs.append(
                        module_spec.InputSpecType.from_xml(value))
                elif port_type == "output":
                    m_spec.output_port_specs.append(
                        module_spec.OutputSpecType.from_xml(value))
                elif port_type == "alternate":
                    ps = in_ips_refs[(code_ref, port)]
                    ps.alternate_specs.append(
                        module_spec.InputSpecType.from_xml(value))
                else:
                    raise ValueError('Cannot access list of type "%s"' %
                                     port_type)
            else:
                in_specs.module_specs.append(module_spec.from_xml(value))
        elif elt.tag.startswith('change'):
            attr = elt.get("attr")
            for child in elt.getchildren():
                if child.tag == 'value':
                    value = child.text
            if port:
                # KLUDGE to fix change from output_type to port_type
                if attr == "output_type":
                    attr = "port_type"
                if port_type == "input":
                    port_spec = in_ips_refs[(code_ref, port)]
                    port_spec.set_raw(attr, value)
                elif port_type == "output":
                    port_spec = in_ops_refs[(code_ref, port)]
                    port_spec.set_raw(attr, value)
                elif port_type == "alternate":
                    port_spec = in_alt_refs[(code_ref, port, alt_name)]
                    port_spec.set_raw(attr, value)
            else:
                m_spec.set_raw(attr, value)

    in_specs.write_to_xml(out_fname)


def compute_upgrade(module_spec, in_fname, out_fname,
                    module_similarity_func=None, port_similarity_func=None):
    """ Computes module upgrade path suggestions

    Parameters
    ----------
    module_similarity_func : function(m1, m2)
        compares 2 module specifications
    port_similarity_func : function(p1, p2)
        compares 2 port specifications and returns similarity as:
        >0 possible match score
        0 no match
    """
    if module_similarity_func is None:
        module_similarity_func = module_similarity
    if port_similarity_func is None:
        port_similarity_func = port_similarity
    in_specs = SpecList.read_from_xml(in_fname, module_spec)
    out_specs = SpecList.read_from_xml(out_fname, module_spec)

    in_refs = dict((spec.module_name, spec) for spec in in_specs.module_specs)
    out_refs = dict((spec.module_name, spec) for spec in out_specs.module_specs)

    in_refs_set = set(in_refs.iterkeys())
    out_refs_set = set(out_refs.iterkeys())

    deleted_modules = in_refs_set - out_refs_set
    added_modules = out_refs_set - in_refs_set

    old_module_map = {}

    def best_match(score_list):
        # best score must be >0 and alone
        if (len(score_list) == 0 or score_list[-1][0] <= 0 or
           (len(score_list) > 1 and score_list[-2][0] == score_list[-1][0])):
            return None
        else:
            return sorted(score_list)[-1][1]
        old_module_map[best_match] = ref

    for ref in deleted_modules:
        # Suggest module to upgrade to by calculating similarity scores
        # FIXME: we could use something more intelligent here
        score_list = sorted([(module_similarity_func(in_refs[ref],
                                                     out_refs[a]), a)
                             for a in added_modules])
        print "%s --> %s" % (ref, best_match(score_list))

    for code_ref, out_spec in out_refs.iteritems():
        # need to check port specs, which removed, which added
        if code_ref in in_refs:
            in_spec = in_refs[code_ref]
        elif code_ref in old_module_map:
            in_spec = in_refs[old_module_map[code_ref]]
        else:
            # No old module found
            continue

        # Compute input mappings
        old_params = dict([(spec.name, spec)
                           for port_spec in in_spec.input_port_specs
                           for spec in all_specs(port_spec)])
        new_params = dict([(spec.name, spec)
                           for port_spec in out_spec.input_port_specs
                           for spec in all_specs(port_spec)])
        deleted_params = set(old_params) - set(new_params)
        added_params = set(new_params) - set(old_params)

        for ref in deleted_params:
            ref_spec = old_params[ref]
            # Suggest param upgrade by calculating most similar port
            score_list = sorted([(port_similarity_func(old_params[ref],
                                                       new_params[a]), a)
                                 for a in added_params])
            print "%s.%s.%s --> %s" % (code_ref, 'input', ref,
                                       best_match(score_list))

        # Compute output mappings
        old_params = dict([(spec.name, spec)
                           for spec in in_spec.output_port_specs])
        new_params = dict([(spec.name, spec)
                           for spec in out_spec.output_port_specs])

        deleted_params = set(old_params) - set(new_params)
        added_params = set(new_params) - set(old_params)

        for ref in deleted_params:
            # Suggest param to upgrade to by calculating similarity scores
            score_list = sorted([(port_similarity_func(old_params[ref],
                                                       new_params[a]), a)
                                 for a in added_params])
            print "%s.%s.%s --> %s" % (code_ref, 'output', ref,
                                       best_match(score_list))


#########################################################################
# Script commands for diff'ing function and class specs
# This needs to be re-implemented when using subclasses

def usage():
    print "Usage: %s %s [apply[f|c] raw diff xml|compute[f|c] raw xml diff|upgrade[f|c] spec1 spec2|show[f|c] spec1 spec2)]" % (sys.executable, sys.argv[0])


if __name__ == '__main__':
    import sys
    from vistrails.core.wrapper.specs import FunctionSpec, ClassSpec
    if len(sys.argv) < 2:
        usage()
    elif sys.argv[1] == "applyf":
        apply_diff(FunctionSpec, sys.argv[2], sys.argv[3], sys.argv[4])
    elif sys.argv[1] == "applyc":
        apply_diff(ClassSpec, sys.argv[2], sys.argv[3], sys.argv[4])
    elif sys.argv[1] == "computef":
        compute_diff(FunctionSpec, sys.argv[2], sys.argv[3], sys.argv[4])
    elif sys.argv[1] == "computec":
        compute_diff(ClassSpec, sys.argv[2], sys.argv[3], sys.argv[4])
    elif sys.argv[1] == "upgradef":
        compute_upgrade(FunctionSpec, sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "upgradec":
        compute_upgrade(ClassSpec, sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "showf":
        compute_diff(FunctionSpec, sys.argv[2], sys.argv[3], show_docstring=False)
    elif sys.argv[1] == "showc":
        compute_diff(ClassSpec, sys.argv[2], sys.argv[3], show_docstring=False)
    else:
        usage()

# example
# PYTHONPATH=/home/tommy/git/vistrails python diff.py computef ~/.vistrails/numpy-1_10_1-spec-0_1_0-functions.xml ~/.vistrails/numpy-1_10_1-spec-0_1_0-functions.xml function-diff.xml