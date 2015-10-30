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


def compute_ps_diff(root, in_ps_list, out_ps_list, code_ref, qualifier,
                    port=None):
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
        print "- %s.%s.%s" % (code_ref, qualifier, arg)
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
            print "out_ps:", out_ps
            print "+ %s.%s.%s %s" % (code_ref, qualifier, arg, 
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
                print "C %s.%s.%s.%s %s" % (code_ref, qualifier, arg, attr, 
                                            out_val)
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
                            code_ref, "alternate", arg)


def compute_diff(module_spec, in_fname, out_fname, diff_fname):
    in_specs = SpecList.read_from_xml(in_fname, module_spec)
    out_specs = SpecList.read_from_xml(out_fname, module_spec)

    in_refs = dict((spec.code_ref, spec) for spec in in_specs.module_specs)
    out_refs = dict((spec.code_ref, spec) for spec in out_specs.module_specs)
    
    in_refs_set = set(in_refs.iterkeys())
    out_refs_set = set(out_refs.iterkeys())

    root = ET.Element("diff")

    for ref in in_refs_set - out_refs_set:
        print "- %s" % ref
        elt = ET.Element("deleteModule")
        elt.set("code_ref", ref)
        root.append(elt)

    for code_ref, out_spec in out_refs.iteritems():
        # need to check port specs, which removed, which added
        if code_ref not in in_refs:
            print "+ %s %s" % (ref, ET.tostring(out_spec.to_xml()))
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
                print "C %s.%s %s" % (out_spec.code_ref, attr, out_val)
                elt = ET.Element("changeModule")
                elt.set("code_ref", out_spec.code_ref)
                elt.set("attr", attr)
                subelt = ET.Element("value")
                subelt.text = out_spec.get_raw(attr)  # serializes value
                elt.append(subelt)
                root.append(elt)

        compute_ps_diff(root, in_spec.input_port_specs, out_spec.input_port_specs,
                        code_ref, "input")
        compute_ps_diff(root, in_spec.output_port_specs, 
                        out_spec.output_port_specs,
                        code_ref, "output")

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
