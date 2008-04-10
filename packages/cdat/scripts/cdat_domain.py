#!/usr/bin/env python
############################################################################
##
## Copyright (C) 2006-2008 University of Utah. All rights reserved.
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
def convert_to_vt_type(t):
    vt_type_dict = {'str':'core.modules.basic_modules.String',
                    'float': 'core.modules.basic_modules.Float',
                    'int':'core.modules.basic_modules.Integer',
                    'bool':'core.modules.basic_modules.Boolean',
                    'numpy.ndarray':'reg.get_module_by_name("edu.utah.sci.vistrails.numpyscipy", "Numpy Array", namespace="numpy|array")',
                    #'cdms2.tvariable.TransientVariable': 'TransientVariable'
                    }
    if vt_type_dict.has_key(t):
        return vt_type_dict[t]
    else:
        print "Type %s not found!" % t
        return None

class CDATModule:
    def __init__(self, author=None, language=None, type=None, url=None,
                 codepath=None, version=None, actions=None):
        self._author = author
        self._language = language
        self._type = type
        self._url = url
        self._codepath = codepath
        self._version = version
        self._actions = actions
        (self._namespace, self._name) = self.split(codepath)
        self._extra_modules = []
        self._extra_vistrails_modules = {}

    def split(self,codepath):
        dot = codepath.rfind('.')
        name = codepath[dot+1:]
        data = codepath[:dot]
        namespace = data.replace('.','|')
        return (namespace,name)

    def write_extra_module_definition(self, lines, name):
        lines.append("%s = new_module(Module,'%s')\n"%(name,name))

    def write_extra_module_definitions(self, lines):
        lines.append("vt_type_dict = {}\n")
        lines.append("def get_late_type(type):\n")
        lines.append("    return vt_type_dict[type]\n\n")

        for t in self._extra_modules:
            namespace,name = self.split(t)
            lines.append("%s = new_module(Module,'%s')\n"%(name,name))
            lines.append("vt_type_dict['%s'] = %s\n"%(t,name))
            self._extra_vistrails_modules[name] = namespace
        lines.append("\n\n")


    def register_extra_vistrails_modules(self,lines, ident=''):
        for (name,namespace) in self._extra_vistrails_modules.iteritems():
            lines.append(ident + "    reg.add_module(%s,namespace='%s')\n"%(name,
                                                                      namespace))

    def register_extra_vistrails_module(self, lines, name, ident=''):
        lines.append(ident + "    reg.add_module(%s,namespace='%s')\n"%(name,
                                                                        self._namespace))

    def write_module_definitions(self, lines):
        for a in self._actions:
            a.write_module_definition(lines)

    def register_vistrails_modules(self, lines):
        for a in self._actions:
            a.register_itself(lines,self._namespace)
            for t in a._output_types:
                if t not in self._extra_modules:
                    self._extra_modules.append(t)

    def add_extra_input_port_to_all_modules(self, lines, port_name, port_type,
                                            doc, optional = False):
        lines.append("\n    #extra input ports not available in the xml file\n")
        for a in self._actions:
            a.register_extra_input_port(port_name, port_type, lines, doc,
                                        optional)

    def add_extra_output_port_to_all_modules(self, lines, port_name, port_type,
                                            doc, optional = False):
        lines.append("\n    #extra output ports not available in the xml file\n")
        for a in self._actions:
            a.register_extra_output_port(port_name, port_type, lines, doc,
                                         optional)
class CDATAction:
    def __init__(self, name=None, type=None, options=None, inputs=None,
                 outputs=None, doc=None):
        self._name = name
        self._type = type
        self._options = options
        self._inputs = inputs
        self._outputs = outputs
        self._doc = doc
        self._output_types = []

    def write_module_definition(self, lines, ident=''):
        def write_compute_method(self,lines, ident):
            lines.append(ident + "def compute(self):\n")
            lines.append(ident + "    if self.hasInputFromPort('canvas'):\n")
            lines.append(ident + "        canvas = self.getInputFromPort('canvas')\n")
            lines.append(ident + "    else:\n")
            lines.append(ident + "        canvas = vcs.init()\n")
            for inp in self._inputs:
                lines.append(ident + "    %s = None\n"%inp._name)
                for inst in inp._valid_instances:
                    if inp._valid_instances.index(inst) == 0:
                        lines.append(ident + "    if self.hasInputFromPort('%s'):\n" % inst)
                        lines.append(ident + "        %s = self.getInputFromPort('%s')\n" % (inp._name, inst))
                    else:
                        lines.append(ident + "    elif self.hasInputFromPort('%s'):\n" % inst)
                        lines.append(ident + "        %s = self.getInputFromPort('%s')\n" % (inp._name, inst))
                if inp._required:
                    lines.append("\n"+ ident +"    # %s is a required port\n" % inp._name)
                    lines.append(ident + "    if %s == None:\n" % inp._name)
                    lines.append(ident + "        raise ModuleError(self, \"'%s' is a mandatory port\")\n" % inp._name)

            lines.append("\n"+ident +"    # build up the keyword arguments from the optional inputs.\n")
            lines.append(ident +"    kwargs = {}\n")

            for opt in self._options:
                for inst in opt._valid_instances:
                    if opt._valid_instances.index(inst) == 0:
                        lines.append(ident +"    if self.hasInputFromPort('%s'):\n" % inst)
                        lines.append(ident +"        kwargs['%s'] = self.getInputFromPort('%s')\n" % (opt._name, inst))
                    else:
                        lines.append(ident +"    elif self.hasInputFromPort('%s'):\n" % inst)
                        lines.append(ident +"        kwargs['%s'] = self.getInputFromPort('%s')\n" % (opt._name, inst))
            s_input = ''
            for inp in self._inputs:
                s_input += "%s, "% inp._name
            lines.append(ident + "    res = canvas.%s(%s**kwargs)\n"%(self._name,s_input))
            lines.append(ident + "    self.setResult('%s',res)\n"%(self._outputs[0]._name))
            lines.append(ident + "    self.setResult('canvas',canvas)\n")
            lines.append("\n")
        lines.append(ident + "class %s(Module):\n" % self._name)
        lines.append(ident + '    """%s\n'%self._doc)
        lines.append(ident + '    """\n')
        write_compute_method(self,lines,ident="    ")

    def register_itself(self,lines, namespace):
        lines.append("\n    #Module %s\n" % self._name)
        lines.append("    reg.add_module(%s,namespace='%s')\n" % (self._name,namespace))
        for inp in self._inputs:
            inp.write_input_ports(self._name, lines)
        for opt in self._options:
            opt.write_input_ports(self._name, lines, True, force=False)
        for out in self._outputs:
            out.write_output_ports(self._name, lines, force=True)
            if out._instance[0] not in self._output_types:
                self._output_types.append(out._instance[0])

    def register_extra_input_port(self, port_name, port_type, lines, doc,
                                  optional=False):
        self._write_port('input', port_name, port_type, lines, doc, optional)

    def register_extra_output_port(self, port_name, port_type, lines, doc,
                                  optional=False):
        self._write_port('output', port_name, port_type, lines, doc, optional)

    #private methods
    def _write_port(self, io_type, port_name, port_type,
                    lines, doc, optional=False):
        lines.append("    reg.add_%s_port(%s, '%s', \n" % (io_type,
                                                           self._name,
                                                           port_name))
        lines.append("                       ")
        lines.append("(%s,\n" % port_type)
        lines.append("                        ")
        if not optional:
            lines.append("\"%s\"))\n" % doc)
        else:
            lines.append("\"%s\"), True)\n" % doc)

class CDATItem:
    def __init__(self, tag=None, doc=None, instance=None, required=False):
        self._name = tag
        self._doc = doc
        self._instance = [i.strip(" \t\n") for i in instance.split('/')]
        self._valid_instances = []
        if required == None:
            self._required = False
        else:
            self._required = required

    def write_input_ports(self, module_name, lines, optional=False, force=False):
        self._write_ports('input',module_name, lines, optional, force)

    def write_output_ports(self, module_name, lines, optional=False, force=False):
        self._write_ports('output',module_name, lines, optional, force)

    def _write_ports(self, port_type, module_name, lines, optional=False,
                     force=False):
        if len(self._instance) == 1:
            type = convert_to_vt_type(self._instance[0])
            if force and type == None:
                type = "get_late_type('%s')"%self._instance[0]
            if type != None:
                self._valid_instances.append(self._name)
                lines.append("    reg.add_%s_port(%s, '%s', \n" % (port_type,
                                                                   module_name,
                                                                   self._name))
                lines.append("                       ")
                lines.append("(%s,\n" % type)
                lines.append("                        ")
                if not optional:
                    lines.append("\"%s\"))\n" % self._doc)
                else:
                    lines.append("\"%s\"), True)\n" % self._doc)
        else:
            count = 0
            for i in xrange(len(self._instance)):
                type = convert_to_vt_type(self._instance[i])
                if force and type == None:
                    type = "get_late_type('%s')"%self._instance[i]
                if type != None:
                    name = "%s_%s"%(self._name,count)
                    self._valid_instances.append(name)
                    count += 1
                    lines.append("    reg.add_input_port(%s, '%s', \n" % (module_name,
                                                                          name))
                    lines.append("                       ")
                    lines.append("(%s,\n" % type)
                    lines.append("                        ")
                    if not optional:
                        lines.append("\"%s\"))\n" % self._doc)
                    else:
                        lines.append("\"%s\"), True)\n" % self._doc)

class CDATOption(CDATItem):
    def __init__(self, tag=None, default=None, doc=None, instance=None):
        CDATItem.__init__(self, tag, doc, instance, False)
        self._default = default

class CDATPort(CDATItem):
    def __init__(self, tag=None, doc=None, instance=None, position=None, required=False):
        CDATItem.__init__(self, tag, doc, instance, required)
        self._position = position