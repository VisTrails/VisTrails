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

from collections import namedtuple as _namedtuple, Mapping
from itertools import izip

_docs = {}

def get_field_name(v):
    if isinstance(v[0], tuple):
        return v[0][0]
    return v[0]

def namedtuple(typename, fields):
    field_names = [f[0][0] if isinstance(f[0], tuple) else f[0]
                   for f in fields]
    default_values = []
    default_found = False
    field_types = []
    docstrings = []

    new_fields = []
    for f in fields:
        field_name = get_field_name(f)
        field_key = (typename, field_name)
        field_type = None
        docstring = None
        default_value = None
        if field_key in _docs:
            (field_type, docstring) = _docs[field_key]
        else:
            if len(f) > 1 and f[1]:
                field_type = f[1]
            if len(f) > 2 and f[2]:
                docstring = f[2]

        if isinstance(f[0], tuple):
            default_found = True
            default_value = f[0][1]
            default_values.append(default_value)
        elif default_found:
            raise Exception('Field "%s" must have default value since the '
                            'preceding field does.' % f[0])
        if field_type:
            field_types.append("(%s)" % field_type)
        else:
            field_types.append("")
        if docstring:
            docstrings.append("\n        %s\n" % docstring)
        else:
            docstrings.append("")

        new_fields.append(((field_name, default_value), field_type, docstring))
    
    fields = new_fields

    T = _namedtuple(typename, field_names)
    args = []
    if len(default_values) > 0:
        T.__new__.__defaults__ = tuple(default_values)
        args.extend("%s=%s" % (field_name, '"%s"' % default_val \
                               if isinstance(default_val, basestring) \
                               else default_val) \
                    for (field_name, default_val) in \
                    izip(reversed(field_names), reversed(default_values)))
        args.reverse()
        args = field_names[:len(field_names)-len(default_values)] + args
    else:
        args = field_names
    
    init_docstring = ""
    for (field_name, field_type, docstring) in \
        izip(field_names, field_types, docstrings):
        init_docstring += "    .. py:attribute:: %s %s\n%s\n" % \
                          (field_name, field_type, docstring)

    init_template = "def __init__(self, %s): pass" % ', '.join(args)
    d = {}
    exec init_template in d
    T.__init__ = d['__init__']
    T.__init__.im_func.__doc__ = init_docstring
    T._vistrails_fields = fields

    return T
    

def subnamedtuple(typename, cls, new_fields=[], override_fields=[]):
    override_dict = dict((get_field_name(f), f) for f in override_fields)
    fields = []
    for f in cls._vistrails_fields:
        field_name = get_field_name(f)
        if field_name in override_dict:
            fields.append(override_dict[field_name])
        else:
            fields.append(f)
    fields.extend(new_fields)

    return namedtuple(typename, fields)
    
_documentation = \
"""
   ConstantWidgetConfig.widget: QWidget | String

      The widget to be used either as the class itself or a string of
      the form ``<py_module>:<class>``
      (e.g. "vistrails.gui.modules.constant_configuration:BooleanWidget")

   ConstantWidgetConfig.widget_type: String

      A developer-available type that links a widget to a port entry_type

   ConstantWidgetConfig.widget_use: String

      Intended to differentiate widgets for different purposes in
      VisTrails.  Currently uses the values None, "query", and
      "paramexp" to define widget uses in parameter, query, and
      parameter exploration configurations, repsectively.

   QueryWidgetConfig.widget_use: String

      Like :py:attr:`ConstantWidgetConfig.widget_use`, just defaulted
      to "query"

   ParamExpWidgetConfig.widget_use: String

      Like :py:attr:`ConstantWidgetConfig.widget_use`, just defaulted
      to "paramexp"

   ModuleSettings.name: String

      An optional string that will identify the module (defaults to
      the module class's ``__name__``).

   ModuleSettings.configure_widget: QWidget | PathString

      An optional module configuration widget that is provided so that
      users can configure the module (e.g. PythonSource uses a widget
      to display a code editor more suited for writing code).

   ModuleSettings.constant_widget: ConstantWidgetConfig | QWidget | PathString

      If not None, the registry will use the specified widget(s) or
      import path string(s) of the form "<module>:<class>" to import
      the widget.  A tuple allows a user to specify the widget_type
      (e.g. "default", "enum", etc.)  as the second item and the
      widget_use (e.g. "default", "query", "paramexp").  If the plural
      form is used, we expect a list, the singular form is used for a
      single item.

   ModuleSettings.constant_widgets: List(constant_widget)

      See :py:attr:`ModuleSettings.constant_widget`

   ModuleSettings.signature: Callable

      If not None, then the cache uses this callable as the function
      to generate the signature for the module in the cache. The
      function should take three parameters: the pipeline (of type
      vistrails.core.vistrail.Pipeline), the module (of type
      vistrails.core.vistrail.Module), and a dict that stores
      parameter hashers. This dict is supposed to be passed to
      vistrails/core/cache/hasher.py:Hasher, in case that needs to be
      called.

   ModuleSettings.constant_signature: Callable

      If not None, the cache uses this callable as the function used
      to generate the signature for parameters of the associated
      module's type.  This function should take a single argument (of
      type vistrials.core.vistrail.module_param.ModuleParam) and
      returns a SHA hash.

   ModuleSettings.color: (Float, Float, Float)

      In the GUI, the module will be colored according to the
      specified RGB tuple where each value is a float in [0,1.0].

   ModuleSettings.fringe: List((Float, Float))

      If not None, generates custom lateral fringes for the module
      boxes.  module_fringe must be a list of pairs of floats.  The
      first point must be (0.0, 0.0), and the last must be (0.0,
      1.0). This will be used to generate custom lateral fringes for
      module boxes. All x values must be positive, and all y values
      must be between 0.0 and 1.0. Alternatively, the user can set
      :py:attr:`ModuleSettings.left_fringe` and
      :py:attr:`ModuleSettings.right_fringe` to set two different
      fringes.

   ModuleSettings.left_fringe: List((Float, Float))

      See :py:attr:`ModuleSettings.fringe`.

   ModuleSettings.right_fringe: List((Float, Float))

      See :py:attr:`ModuleSettings.fringe`.

   ModuleSettings.abstract: Boolean

      If True, means the module only serves as a base class for other
      modules.  It will not appear in the module palette but may be
      used as a input or output port type.

   ModuleSettings.package: String

      If not None, then we use this package instead of the current
      one.  This is only intended to be used with local per-module
      module registries (in other words: if you don't know what a
      local per-module registry is, you can ignore this option).

   ModuleSettings.namespace: String

      If not None, then we associate a namespace with the module. A
      namespace is essentially appended to the package identifier so
      that multiple modules inside the same package can share the same
      name.  Namespaces may be nested using the "|" separator.  For
      example, "Tools|Mathematical" specified the Mathematical
      namespace inside of the Tools namespace.

   ModuleSettings.version: String

      The module version.  This is usually used with subworkflows
      where the underlying module may have different versions.  Not
      recommended for general use at this time.

   ModuleSettings.package_version: String

      The current package version for the module.  As with
      :py:attr:`ModuleSettings.package`, you shuold not use this
      unless you know what you are doing as VisTrails will
      automatically fill in this information for any normal package.

   ModuleSettings.hide_namespace: Boolean

      If True, the module palette will not display the namespace for
      the module.  Used for subworkflows, otherwise it may be
      confusing for users.

   ModuleSettings.hide_descriptor: Boolean

      If True, the module palette will not display that module in its
      list (similar to abstract, but can be used when the module is
      not truly abstract).

   ModuleSettings.is_root: Boolean

      Internal use only.  This is used to designate the base Module
      class and should not be used by any other module.

   ModuleSettings.ghost_package: String

      If not None, then the 'ghost_identifier' is set on the
      descriptor, which will cause the module to be displayed under
      that package in the module palette, rather than the package
      specified by the package argument (or current package).

   ModuleSettings.ghost_package_version: String

      If not None, then the attribute 'ghost_package_version' is set
      on the descriptor.  Currently this value is unused, but
      eventually if multiple packages with the same identifier but
      different package versions are loaded simultaneously, this will
      allow overriding the package_version to clean up the module
      palette.

   ModuleSettings.ghost_namespace: String

      If not None, the descriptor will be displayed under the
      specified namespace instead of the 'namespace' attribute of the
      descriptor.

   Port.name: String

      The name of the of the port

   Port.signature: String

      The signature of the of the port (e.g. "basic:Float")

   Port.optional: Boolean

      Whether the port should be visible by default (defaults to True)

   Port.sort_key: Integer

      An integer value that indicates where, relative to other ports,
      this port should appear visually

   Port.docstring: String

      Documentation for the port

   Port.shape: "triangle" | "diamond" | "circle" | [(Float,Float)]

      The shape of the port.  If triangle, appending an angle (in
      degrees) rotates the triangle.  If a list of (x,y) tuples,
      specifies points of a polygon in the [0,1] x [0,1] region

   Port.min_conns: Integer

      The minimum number of values required for the port

   Port.max_conns: Integer

      The maximum number of values allowed for the port

   Port.depth: Integer

      The list depth of the port. Default is 0 (no list)
      
   InputPort.label: String

      A label to be shown with a port

   InputPort.default:

      The default value for a constant-typed port

   InputPort.values: List

      A list of enumerated values that a
      :py:class:`.ConstantWidgetConfig` uses to configure the widget.
      For example, the "enum" widget uses the entries to present an
      exclusive list of choices.

   InputPort.entry_type: String

      The type of the configuration widget that should be used with
      this port. Developers may use custom widgets on a port-by-port
      basis by adding widgets with different
      :py:attr:`ConstantWidgetConfig.widget_type` values and defining
      the port\'s entry_type to match.

   CompoundInputPort.labels: List(String)

      A list of :py:attr:`InputPort.label`

   CompoundInputPort.defaults: List

      A list of :py:attr:`InputPort.default`

   CompoundInputPort.values: List(List)

      A list of :py:attr:`InputPort.values`

   CompoundInputPort.entry_types: List(String)

      A list of :py:attr:`InputPort.entry_type`

   CompoundInputPort.items: List(InputPortItem)

      Either use this field and break individual
      labels/defaults/values/entry_types into
      :py:class:`.InputPortItem` components or use the other four
      fields.

   CompoundInputPort.signature: String

      The signature of the port (e.g. "basic:Integer, basic:Float").
      Note that for compound ports, this may be instead included on a
      per-component basis in :py:attr:`InputPortItem.signature`.

   CompoundOutputPort.items: List(OutputPortItem)

      Either use this field and break individual signatures into
      :py:class:`.OutputPortItem` components or use the signature
      field.

   CompoundOutputPort.signature: String

      The signature of the port (e.g. "basic:Integer, basic:Float").
      Note that for compound ports, this may be instead included on a
      per-component basis in :py:attr:`OutputPortItem.signature`.

   PortItem.signature: String

      See :py:attr:`InputPort.signature`

   InputPortItem.label: String

      See :py:attr:`InputPort.label`

   InputPortItem.default:

      See :py:attr:`InputPort.default`

   InputPortItem.values: List

      See :py:attr:`InputPort.values`

   InputPortItem.entry_type: String

      See :py:attr:`InputPort.entry_type`

"""

def parse_documentation():
    global _docs

    line_iter = iter(_documentation.splitlines())
    line_iter.next()
    for line in line_iter:
        field, field_type = line.strip().split(':', 1)
        (cls_name, field_name) = field.split('.')
        doc_lines = []
        line = line_iter.next()
        while True:
            line = line_iter.next()
            if not line.strip():
                break
            doc_lines.append(line.strip())
        _docs[(cls_name, field_name)] = (field_type, ' '.join(doc_lines))

parse_documentation()

ConstantWidgetConfig = \
    namedtuple('ConstantWidgetConfig', 
               [('widget',),
                (('widget_type', None),),
                (('widget_use', None),)])
QueryWidgetConfig = subnamedtuple('QueryWidgetConfig', ConstantWidgetConfig, 
    override_fields=[(('widget_use', 'query'),)])
ParamExpWidgetConfig = subnamedtuple('ParamExpWidgetConfig', 
    ConstantWidgetConfig,
    override_fields=[(('widget_use', 'paramexp'),)])

ModuleSettings = namedtuple('ModuleSettings',
                          [(('name', None),),
                           (('configure_widget', None),),
                           (('constant_widget', None),),
                           (('constant_widgets', None),),
                           (('signature', None),),
                           (('constant_signature', None),),
                           (('color', None),),
                           (('fringe', None),),
                           (('left_fringe', None),),
                           (('right_fringe', None),),
                           (('abstract', False),),
                           (('package', None),),
                           (('namespace', None),),
                           (('version', None),),
                           (('package_version', None),),
                           (('hide_namespace', False),),
                           (('hide_descriptor', False),),
                           (('is_root', False),),
                           (('ghost_package', None),),
                           (('ghost_package_version', None),),
                           (('ghost_namespace', None),),])

Port = namedtuple('Port', 
                     [("name",),
                      ("signature",),
                      (("optional", False),),
                      (("sort_key", -1),),
                      (("docstring", None),),
                      (("shape", None),),
                      (("min_conns", 0),),
                      (("max_conns", -1),),
                      (("depth", 0),),
                      ])

InputPort = subnamedtuple('InputPort', Port,
                          [(('label', None),),
                           (('default', None),),
                           (('values', None),),
                           (('entry_type', None),)])
OutputPort = subnamedtuple('OutputPort', Port)

CompoundPort = subnamedtuple('CompoundPort', Port,
                             [(('items', None),)],
                             [(('signature', None),)])
CompoundInputPort = subnamedtuple('CompoundInputPort', CompoundPort,
                                  [(('labels', None),), 
                                   (('defaults', None),),
                                   (('values', None),),
                                   (('entry_types', None),)])
CompoundOutputPort = subnamedtuple('CompoundOutputPort', CompoundPort)

PortItem = namedtuple('PortItem', [('signature', None)])
InputPortItem = subnamedtuple('InputPortItem', PortItem,
                              [(('label', None),),
                               (('default', None),),
                               (('values', None),),
                               (('entry_type', None),)])
OutputPortItem = subnamedtuple('OutputPortItem', PortItem)

DeprecatedInputPort = \
                      namedtuple('DeprecatedInputPort',
                                 [("name", "String",),
                                  ("signature", "String",),
                                  (("optional", True),),
                                  (("sort_key", -1),),
                                  (('labels', None),), 
                                  (('defaults', None),),
                                  (('values', None),),
                                  (('entry_types', None),),
                                  (("docstring", None),),
                                  (("shape", None),),
                                  (("min_conns", 0),),
                                  (("max_conns", -1),),
                              ])

IPort = InputPort
OPort = OutputPort
CIPort = CompoundInputPort
COPort = CompoundOutputPort
IPItem = InputPortItem
OPItem = OutputPortItem
