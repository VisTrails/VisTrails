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

import contextlib
from itertools import izip
import subprocess

import vistrails.core.application
import vistrails.core.db.action
import vistrails.core.db.io
from vistrails.core.db.locator import UntitledLocator, FileLocator
from vistrails.core.interpreter.default import get_default_interpreter
from vistrails.core.modules.module_registry import get_module_registry
from vistrails.core.modules.package import Package as _Package
from vistrails.core.modules.sub_module import get_port_spec_info
from vistrails.core.modules.utils import parse_port_spec_string
from vistrails.core.packagemanager import get_package_manager
from vistrails.core.system import get_vistrails_basic_pkg_id
from vistrails.core.utils import DummyView
from vistrails.core.vistrail.controller import VistrailController
from vistrails.core.vistrail.pipeline import Pipeline as _Pipeline
from vistrails.core.vistrail.vistrail import Vistrail as _Vistrail
from vistrails.db.domain import IdScope


__all__ = ['Vistrail', 'Pipeline', 'Module', 'Package',
           'ExecutionResults', 'ExecutionErrors', 'Function',
           'ipython_mode', 'load_vistrail', 'load_pipeline', 'load_package',
           'output_mode', 'run_vistrail',
           'NoSuchVersion', 'NoSuchPackage']


class NoSuchVersion(KeyError):
    """The version number or tag you specified doesn't exist in the vistrail.
    """


class NoSuchPackage(ValueError):
    """Couldn't find a package with the given identifier.
    """


is_initialized = False
_application = None


def initialize():
    """Initializes VisTrails.

    You don't have to call this directly. Initialization will happen when you
    start using the API.
    """
    global is_initialized
    global _application

    if is_initialized:
        return False

    # Creates a core application
    _application = vistrails.core.application.init(
            options_dict={
                'installBundles': False,
                'loadPackages': False,
                'enablePackagesSilently': True},
            args=[])

    is_initialized = True

    return True


def ipython_mode(use_notebook=True):
    """Selects whether the IPython notebook should be used.

    Call ``vistrails.ipython_mode(True)`` to enable IPythonMode for output
    modules, directing supported output to the notebook instead of files.
    """
    if use_notebook:
        try:
            import IPython.core.display
        except ImportError:
            raise ValueError("IPython doesn't seem to be installed!?")

    from vistrails.core.modules.output_modules import IPythonMode
    IPythonMode.notebook_override = use_notebook


class Vistrail(object):
    """This class wraps both Vistrail and VistrailController.

    From it, you can get any pipeline from a tag name or version number.

    It has a concept of "current version", from which you can create new
    versions by performing actions.
    """
    _current_pipeline = None
    _html = None

    def __init__(self, arg=None):
        initialize()
        if arg is None:
            # Copied from VistrailsApplicationInterface#open_vistrail()
            locator = UntitledLocator()
            loaded_objs = vistrails.core.db.io.load_vistrail(locator)
            self.controller = VistrailController(loaded_objs[0], locator,
                                                 *loaded_objs[1:])
        elif isinstance(arg, (_Pipeline, Pipeline)):
            if isinstance(arg, Pipeline):
                pipeline = arg.pipeline
            else:
                pipeline = arg
            # Copied from VistrailsApplicationInterface#open_workflow()
            vistrail = _Vistrail()
            ops = []
            for module in pipeline.module_list:
                ops.append(('add', module))
            for connection in pipeline.connection_list:
                ops.append(('add', connection))
            action = vistrails.core.db.action.create_action(ops)
            vistrail.add_action(action, 0L)
            vistrail.update_id_scope()
            vistrail.change_description("Imported pipeline", 0L)
            self.controller = VistrailController(vistrail, UntitledLocator())
        elif isinstance(arg, VistrailController):
            self.controller = arg
        elif isinstance(arg, basestring):
            raise TypeError("Vistrail was constructed from %r.\n"
                            "Use load_vistrail() to get a Vistrail from a "
                            "file." % type(arg).__name__)
        else:
            raise TypeError("Vistrail was constructed from unexpected "
                            "argument type %r" % type(arg).__name__)

    def get_pipeline(self, version):
        """Returns a pipeline from a version number of tag.

        This does not change the currently selected version in this Vistrail.
        """
        vistrail = self.controller.vistrail
        if isinstance(version, (int, long)):
            if not vistrail.db_has_action_with_id(version):
                raise NoSuchVersion("Vistrail doesn't have a version %r" %
                                    version)
            return Pipeline(vistrail.getPipelineVersionNumber(version))
        elif isinstance(version, basestring):
            if not vistrail.has_tag_str(version):
                raise NoSuchVersion("Vistrail doesn't have a tag %r" % version)
            return Pipeline(vistrail.getPipelineVersionName(version))
        else:
            raise TypeError("get_pipeline() argument must be a string or "
                            "integer, not %r" % type(version).__name__)

    def select_version(self, version):
        """Sets a different version as current.

        The current workflow is accessible via current_workflow; it is the one
        that gets executed when calling execute(), and the version from which
        new versions are created if you perform actions.
        """
        vistrail = self.controller.vistrail
        if isinstance(version, (int, long)):
            if not vistrail.db_has_action_with_id(version):
                raise NoSuchVersion("Vistrail doesn't have a version %r" %
                                    version)
        elif (isinstance(version, basestring)):
            if not vistrail.has_tag_str(version):
                raise NoSuchVersion("Vistrail doesn't have a tag %r" % version)
            version = vistrail.get_tag_str(version).action_id
        else:
            raise TypeError("select_version() argument must be a string "
                            "or integer, not %r" % type(version).__name__)
        self.controller.do_version_switch(version)
        self._current_pipeline = None
        self._html = None

    def select_latest_version(self):
        """Sets the most recent version in the vistrail as current.
        """
        self.controller.do_version_switch(
                self.controller.get_latest_version_in_graph())
        self._current_pipeline = None
        self._html = None

    @property
    def current_pipeline(self):
        if self._current_pipeline is None:
            self._current_pipeline = Pipeline(
                    self.controller.current_pipeline,
                    vistrail=(self, self.current_version))
        return self._current_pipeline

    @property
    def current_version(self):
        return self.controller.current_version

    def set_tag(self, *args):
        """Sets a tag for the current or specified version.
        """
        if len(args) == 1:
            version, (tag,) = self.controller.current_version, args
        elif len(args) == 2:
            version, tag = args
        else:
            raise TypeError("set_tag() takes 1 or 2 arguments (%r given)" %
                            len(args))
        if isinstance(version, (int, long)):
            if not self.controller.vistrail.db_has_action_with_id(version):
                raise NoSuchVersion("Vistrail doesn't have a version %r" %
                                    version)
        elif isinstance(version, basestring):
            if not self.controller.vistrail.has_tag_str(version):
                raise NoSuchVersion("Vistrail doesn't have a tag %r" % version)
        else:
            raise TypeError("set_tag() expects the version to be a string or "
                            "integer, not %r" % type(version).__name__)
        self.controller.vistrail.set_tag(version, tag)

    def tag(self, tag):
        """Sets a tag for the current version.
        """
        self.set_tag(tag)

    def execute(self, *args, **kwargs):
        """Executes the current workflow.
        """
        return self.current_pipeline.execute(*args, **kwargs)

    @property
    def changed(self):
        return self.controller.changed

    # TODO : vistrail modification methods

    def __repr__(self):
        version_nb = self.controller.current_version
        if self.controller.vistrail.has_tag(version_nb):
            version = "%s (tag %s)" % (
                    version_nb,
                    self.controller.vistrail.get_tag(version_nb))
        else:
            version = version_nb
        return "<%s: %s, version %s, %s>" % (
                self.__class__.__name__,
                self.controller.name,
                version,
                ('not changed', 'changed')[self.controller.changed])

    def _repr_html_(self):
        if self._html is None:
            import cgi
            try:
                from cStringIO import StringIO
            except ImportError:
                from StringIO import StringIO

            self._html = ''
            stream = StringIO()
            self.controller.recompute_terse_graph()
            self.controller.save_version_graph(
                    stream,
                    highlight=self.controller.current_version)
            stream.seek(0)
            dot = stream.read()

            try:
                proc = subprocess.Popen(['dot', '-Tsvg'],
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE)
                svg, _ = proc.communicate(dot)
                if proc.wait() == 0:
                    self._html += svg
            except OSError:
                pass
            self._html += '<pre>' + cgi.escape(repr(self)) + '</pre>'
        return self._html


def get_inputoutput_name(module):
    for function in module.functions:
        if function.name == 'name':
            if len(function.params) == 1:
                return function.params[0].strValue
    return None


class Pipeline(object):
    """This class represents a single Pipeline.

    It doesn't have a controller.
    """
    vistrail = None
    version = None
    _inputs = None
    _outputs = None
    _html = None

    def __init__(self, pipeline=None, vistrail=None):
        initialize()
        if pipeline is None:
            self.pipeline = _Pipeline()
        elif isinstance(pipeline, _Pipeline):
            self.pipeline = pipeline
        elif isinstance(pipeline, basestring):
            raise TypeError("Pipeline was constructed from %r.\n"
                            "Use load_pipeline() to get a Pipeline from a "
                            "file." % type(pipeline).__name__)
        else:
            raise TypeError("Pipeline was constructed from unexpected "
                            "argument type %r" % type(pipeline).__name__)
        if vistrail is not None:
            if (isinstance(vistrail, tuple) and len(vistrail) == 2 and
                    isinstance(vistrail[0], Vistrail)):
                self.vistrail, self.version = vistrail
            else:
                raise TypeError("Pipeline got unknown type %r as 'vistrail' "
                                "argument" % type(vistrail).__name__)

    @property
    def modules(self):
        for module in self.pipeline.module_list:
            yield Module(descriptor=module.module_descriptor,
                         module_id=module.id,
                         pipeline=self)

    def execute(self, *args, **kwargs):
        """Execute the pipeline.

        Positional arguments are either input values (created from
        ``module == value``, where `module` is a Module from the pipeline and
        `value` is some value or Function instance) for the pipeline's
        InputPorts, or Module instances (to select sink modules).

        Keyword arguments are also used to set InputPort by looking up inputs
        by name.

        Example::

           input_bound = pipeline.get_input('higher_bound')
           input_url = pipeline.get_input('url')
           sinkmodule = pipeline.get_module(32)
           pipeline.execute(sinkmodule,
                            input_bound == vt.Function(Integer, 10),
                            input_url == 'http://www.vistrails.org/',
                            resolution=15)  # kwarg: only one equal sign
        """
        sinks = set()
        inputs = {}

        reg = get_module_registry()
        InputPort_desc = reg.get_descriptor_by_name(
                get_vistrails_basic_pkg_id(),
                'InputPort')

        # Read args
        for arg in args:
            if isinstance(arg, ModuleValuePair):
                if arg.module.id in inputs:
                    raise ValueError(
                            "Multiple values set for InputPort %r" %
                            get_inputoutput_name(arg.module))
                if not reg.is_descriptor_subclass(arg.module.module_descriptor,
                                                  InputPort_desc):
                    raise ValueError("Module %d is not an InputPort" %
                                     arg.module.id)
                inputs[arg.module.id] = arg.value
            elif isinstance(arg, Module):
                sinks.add(arg.module_id)

        # Read kwargs
        for key, value in kwargs.iteritems():
            key = self.get_input(key)  # Might raise KeyError
            if key.module_id in inputs:
                raise ValueError("Multiple values set for InputPort %r" %
                                 get_inputoutput_name(key.module))
            inputs[key.module_id] = value

        reason = "API pipeline execution"
        sinks = sinks or None

        # Use controller only if no inputs were passed in
        if (not inputs and self.vistrail is not None and
                self.vistrail.current_version == self.version):
            controller = self.vistrail.controller
            results, changed = controller.execute_workflow_list([[
                    controller.locator,  # locator
                    self.version,  # version
                    self.pipeline,  # pipeline
                    DummyView(),  # view
                    None,  # custom_aliases
                    None,  # custom_params
                    reason,  # reason
                    sinks,  # sinks
                    None,  # extra_info
                    ]])
            result, = results
        else:
            pipeline = self.pipeline
            if inputs:
                id_scope = IdScope(1)
                pipeline = pipeline.do_copy(False, id_scope)

                # A hach to get ids from id_scope that we know won't collide:
                # make them negative
                id_scope.getNewId = lambda t, g=id_scope.getNewId: -g(t)

                create_module = \
                        VistrailController.create_module_from_descriptor_static
                create_function = VistrailController.create_function_static
                create_connection = VistrailController.create_connection_static
                # Fills in the ExternalPipe ports
                for module_id, values in inputs.iteritems():
                    module = pipeline.modules[module_id]
                    if not isinstance(values, (list, tuple)):
                        values = [values]

                    # Guess the type of the InputPort
                    _, sigstrings, _, _, _ = get_port_spec_info(pipeline, module)
                    sigstrings = parse_port_spec_string(sigstrings)

                    # Convert whatever we got to a list of strings, for the
                    # pipeline
                    values = [reg.convert_port_val(val, sigstring, None)
                              for val, sigstring in izip(values, sigstrings)]

                    if len(values) == 1:
                        # Create the constant module
                        constant_desc = reg.get_descriptor_by_name(
                                *sigstrings[0])
                        constant_mod = create_module(id_scope, constant_desc)
                        func = create_function(id_scope, constant_mod,
                                               'value', values)
                        constant_mod.add_function(func)
                        pipeline.add_module(constant_mod)

                        # Connect it to the ExternalPipe port
                        conn = create_connection(id_scope,
                                                 constant_mod, 'value',
                                                 module, 'ExternalPipe')
                        pipeline.db_add_connection(conn)
                    else:
                        raise RuntimeError("TODO : create tuple")

            interpreter = get_default_interpreter()
            result = interpreter.execute(pipeline,
                                         reason=reason,
                                         sinks=sinks)

        if result.errors:
            raise ExecutionErrors(self, result)
        else:
            return ExecutionResults(self, result)

    def get_module(self, module_id):
        if isinstance(module_id, (int, long)):  # module id
            module = self.pipeline.modules[module_id]
        elif isinstance(module_id, basestring):  # module name
            def desc(mod):
                if '__desc__' in mod.db_annotations_key_index:
                    return mod.get_annotation_by_key('__desc__').value
                else:
                    return None
            modules = [mod
                       for mod in self.pipeline.modules.itervalues()
                       if desc(mod) == module_id]
            if not modules:
                raise KeyError("No module with description %r" % module_id)
            elif len(modules) > 1:
                raise ValueError("Multiple modules with description %r" %
                                 module_id)
            else:
                module, = modules

        else:
            raise TypeError("get_module() expects a string or integer, not "
                            "%r" % type(module_id).__name__)
        return Module(descriptor=module.module_descriptor,
                      module_id=module.id,
                      pipeline=self)

    def _get_inputs_or_outputs(self, module_name):
        reg = get_module_registry()
        desc = reg.get_descriptor_by_name(
                'org.vistrails.vistrails.basic',
                module_name)
        modules = {}
        for module in self.pipeline.modules.itervalues():
            if module.module_descriptor is desc:
                name = get_inputoutput_name(module)
                if name is not None:
                    modules[name] = module
        return modules

    def get_input(self, name):
        try:
            module = self._get_inputs_or_outputs('InputPort')[name]
        except KeyError:
            raise KeyError("No InputPort module with name %r" % name)
        else:
            return Module(descriptor=module.module_descriptor,
                          module_id=module.id,
                          pipeline=self)

    def get_output(self, name):
        try:
            module = self._get_inputs_or_outputs('OutputPort')[name]
        except KeyError:
            raise KeyError("No OutputPort module with name %r" % name)
        else:
            return Module(descriptor=module.module_descriptor,
                          module_id=module.id,
                          pipeline=self)

    @property
    def inputs(self):
        if self._inputs is None:
            self._inputs = self._get_inputs_or_outputs('InputPort').keys()
        return self._inputs

    @property
    def outputs(self):
        if self._outputs is None:
            self._outputs = self._get_inputs_or_outputs('OutputPort').keys()
        return self._outputs

    def __repr__(self):
        desc = "<%s: %d modules, %d connections" % (
                self.__class__.__name__,
                len(self.pipeline.modules),
                len(self.pipeline.connections))
        inputs = self.inputs
        if inputs:
            desc += "; inputs: %s" % ", ".join(inputs)
        outputs = self.outputs
        if outputs:
            desc += "; outputs: %s" % ", ".join(outputs)
        return desc + ">"

    def _repr_html_(self):
        if self._html is None:
            import cgi
            try:
                from cStringIO import StringIO
            except ImportError:
                from StringIO import StringIO

            self._html = ''

            # http://www.graphviz.org/doc/info/shapes.html
            dot = ['digraph {\n    node [shape=plaintext];']

            # {moduleId: (input_ports, output_ports)}
            modules = dict((mod.id, (set(), set()))
                           for mod in self.pipeline.module_list)
            for conn in self.pipeline.connection_list:
                src, dst = conn.source, conn.destination
                modules[src.moduleId][1].add(src.name)
                modules[dst.moduleId][0].add(dst.name)

            # {moduleId: ({input_port_name: input_num},
            #             {output_port_name: output_num})
            # where input_num and output_num are just some sequences of numbers
            modules = dict((mod_id,
                            (dict((n, i) for i, n in enumerate(mod_ports[0])),
                             dict((n, i) for i, n in enumerate(mod_ports[1]))))
                           for mod_id, mod_ports in modules.iteritems())

            # Write out the modules
            for mod, port_lists in modules.iteritems():
                labels = []
                for port_type, ports in izip(('in', 'out'), port_lists):
                    label = ('<td port="%s%s">%s</td>' % (port_type, port_num, cgi.escape(port_name))
                             for port_name, port_num in ports.iteritems())
                    labels.append(''.join(label))

                label = ['<table border="0" cellborder="0" cellspacing="0">']
                if labels[0]:
                    label += ['<tr><td><table border="0" cellborder="1" cellspacing="0"><tr>', labels[0], '</tr></table></td></tr>']
                mod_obj = self.pipeline.modules[mod]
                if '__desc__' in mod_obj.db_annotations_key_index:
                    name = (mod_obj.get_annotation_by_key('__desc__')
                                 .value.strip())
                else:
                    name = mod_obj.label
                label += ['<tr><td border="1" bgcolor="grey"><b>', cgi.escape(name), '</b></td></tr>']
                if labels[1]:
                    label += ['<tr><td><table border="0" cellborder="1" cellspacing="0"><tr>', labels[1], '</tr></table></td></tr>']
                label += ['</table>']
                dot.append('    module%d [label=<%s>];' % (mod, '\n'.join(label)))
            dot.append('')

            # Write out the connections
            for conn in self.pipeline.connection_list:
                src, dst = conn.source, conn.destination
                dot.append('    module%d:out%d -> module%d:in%d;' % (
                           src.moduleId,
                           modules[src.moduleId][1][src.name],
                           dst.moduleId,
                           modules[dst.moduleId][0][dst.name]))

            dot.append('}')
            try:
                proc = subprocess.Popen(['dot', '-Tsvg'],
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE)
                svg, _ = proc.communicate('\n'.join(dot))
                if proc.wait() == 0:
                    self._html += svg
            except OSError:
                pass
            self._html += '<pre>' + cgi.escape(repr(self)) + '</pre>'
        return self._html


class ModuleClass(type):
    def __new__(cls, descriptor):
        return type.__new__(cls, descriptor.name, (object,), {})

    def __init__(self, descriptor):
        self.descriptor = descriptor

    def __call__(self, *args, **kwargs):
        return Module(self.descriptor, *args, **kwargs)

    def __repr__(self):
        return "<Module class %r from %s>" % (self.descriptor.name,
                                              self.descriptor.identifier)
    __str__ = __repr__
    __unicode__ = __repr__

    def __instancecheck__(self, instance):
        return (isinstance(instance, Module) and
                instance.descriptor == self.descriptor)

    def __subclasscheck__(self, other):
        if not issubclass(other, type):
            raise TypeError
        if not isinstance(other, ModuleClass):
            return False
        reg = get_module_registry()
        return reg.is_descriptor_subclass(self.descriptor, other.descriptor)


class ModuleValuePair(object):
    """Internal object returned by Module == value expressions.
    """
    def __init__(self, module, value):
        self.module = module
        self.value = value

    def __nonzero__(self):
        raise TypeError("Took truth value of ModuleValuePair!")


class Module(object):
    """Wrapper for a module, which can be in a Pipeline or not yet.
    """
    module_id = None
    pipeline = None

    def __init__(self, descriptor, **kwargs):
        self.descriptor = descriptor
        if 'module_id' and 'pipeline' in kwargs:
            self.module_id = kwargs.pop('module_id')
            self.pipeline = kwargs.pop('pipeline')
            if not (isinstance(self.module_id, (int, long)) and
                    isinstance(self.pipeline, Pipeline)):
                raise TypeError
        elif 'module_id' in kwargs or 'pipeline' in kwargs:
            raise TypeError("Module was given an id but no pipeline")

        if kwargs:
            raise TypeError("Module was given unexpected argument: %r" %
                            next(iter(kwargs)))

    @property
    def module(self):
        if self.module_id is None:
            raise ValueError("This module is not part of a pipeline")
        return self.pipeline.pipeline.modules[self.module_id]

    @property
    def module_class(self):
        return ModuleClass(self.descriptor)

    @property
    def name(self):
        if self.module_id is None:
            raise ValueError("This module is not part of a pipeline")
        mod = self.pipeline.pipeline.modules[self.module_id]
        if '__desc__' in mod.db_annotations_key_index:
            return mod.get_annotation_by_key('__desc__').value
        else:
            return None

    def __repr__(self):
        desc = "<Module %r from %s" % (self.descriptor.name,
                                       self.descriptor.identifier)
        if self.module_id is not None:
            desc += ", id %d" % self.module_id
            if self.pipeline is not None:
                mod = self.pipeline.pipeline.modules[self.module_id]
                if '__desc__' in mod.db_annotations_key_index:
                    desc += (", name \"%s\"" %
                             mod.get_annotation_by_key('__desc__').value)
        return desc + ">"

    def __eq__(self, other):
        if isinstance(other, Module):
            if self.module_id is None:
                return other.module_id is None
            else:
                if other.module_id is None:
                    return False
                return (self.module_id == other.module_id and
                        self.pipeline == other.pipeline)
        else:
            return ModuleValuePair(self.module, other)


class ModuleNamespace(object):
    def __init__(self, identifier, namespace=''):
        self.identifier = identifier
        self._namespace = namespace
        self._namespaces = {}

    def __getattr__(self, name):
        if name in self._namespaces:
            return self._namespaces[name]
        else:
            return self[name]

    def __getitem__(self, name):
        name = name.rsplit('|', 1)
        if len(name) == 2:
            if self._namespace:
                namespace = self._namespace + '|' + name[0]
            else:
                namespace = name[0]
            name = name[1]
        else:
            name, = name
            namespace = self._namespace
        reg = get_module_registry()
        descr = reg.get_descriptor_by_name(self.identifier,
                                           name,
                                           namespace)
        return ModuleClass(descr)

    def __repr__(self):
        return "<Namespace %s of package %s>" % (self._namespace,
                                                 self.identifier)


class Package(ModuleNamespace):
    """Wrapper for an enabled package.

    You can get modules from a Package using either the
    ``pkg['namespace|module']`` or ``pkg.namespace.module`` syntax.
    """
    def __init__(self, package):
        if not isinstance(package, _Package):
            raise TypeError("Can't construct a package from "
                            "%r" % type(package).__name__)
        ModuleNamespace.__init__(self, package.identifier)
        self._package = package

        # Builds namespaces
        for mod, namespaces in self._package.descriptors.iterkeys():
            if not namespaces:
                continue
            ns = self
            fullname = None
            for name in namespaces.split('|'):
                if fullname is not None:
                    fullname += '|' + name
                else:
                    fullname = name
                if name not in ns._namespaces:
                    ns_ = ns._namespaces[name] = ModuleNamespace(
                            self.identifier,
                            fullname)
                    ns = ns_
                else:
                    ns = ns._namespaces[name]

    def __repr__(self):
        return "<Package: %s, %d modules>" % (self.identifier,
                                              len(self._package.descriptors))

    def __eq__(self, other):
        return isinstance(other, Package) and self._package is other._package

    def __ne__(self, other):
        return not self == other


class ExecutionErrors(Exception):
    """Errors raised during a pipeline execution.
    """
    def __init__(self, pipeline, resultobj):
        self.pipeline = pipeline
        self._errors = resultobj.errors

    def __str__(self):
        return "Pipeline execution failed: %d error%s:\n%s" % (
                len(self._errors),
                's' if len(self._errors) >= 2 else '',
                '\n'.join('%d: %s' % p for p in self._errors.iteritems()))


class ExecutionResults(object):
    """Contains the results of a pipeline execution.
    """
    def __init__(self, pipeline, resultobj):
        self.pipeline = pipeline
        self._objects = resultobj.objects

    def output_port(self, output):
        """Gets the value passed to an OutputPort module with that name.
        """
        if isinstance(output, basestring):
            outputs = self.pipeline._get_inputs_or_outputs('OutputPort')
            module_id = outputs[output].id
        else:
            raise TypeError("output_port() expects a string, not %r" %
                            type(output).__name__)
        return self._objects[module_id].get_output('ExternalPipe')

    def module_output(self, module):
        """Gets all the output ports of a specified module.
        """
        if not isinstance(module, Module):
            module = self.pipeline.get_module(module)
        return self._objects[module.module_id].outputPorts

    def __repr__(self):
        return "<ExecutionResult: %d modules>" % len(self._objects)


class Function(object):
    """A function, essentially a value with an explicit module type.
    """
    # TODO : Function


def load_vistrail(filename, version=None):
    """Loads a Vistrail from a filename.
    """
    initialize()
    if not isinstance(filename, basestring):
        raise TypeError("load_vistrails() expects a filename, got %r" %
                        type(filename).__name__)

    locator = FileLocator(filename)
    # Copied from VistrailsApplicationInterface#open_vistrail()
    loaded_objs = vistrails.core.db.io.load_vistrail(locator)
    controller = VistrailController(loaded_objs[0], locator,
                                    *loaded_objs[1:])

    vistrail = Vistrail(controller)
    if version is not None:
        vistrail.select_version(version)
    return vistrail


def load_pipeline(filename):
    """Loads a single pipeline from a filename.
    """
    initialize()
    if not isinstance(filename, basestring):
        raise TypeError("load_vistrails() expects a filename, got %r" %
                        type(filename).__name__)

    # Copied from VistrailsApplicationInterface#open_workflow()
    locator = FileLocator(filename)
    pipeline = locator.load(_Pipeline)

    return Pipeline(pipeline)


# TODO : provide a shortcut for basic_modules
def load_package(identifier, autoload=True):
    """Gets a package by identifier, enabling it if necessary.
    """
    initialize()
    pm = get_package_manager()
    pkg = pm.identifier_is_available(identifier)
    if pm.has_package(identifier):
        return Package(pkg)
    elif pkg is None:
        raise NoSuchPackage("Package %r not found" % identifier)

    # Copied from VistrailController#try_to_enable_package()
    dep_graph = pm.build_dependency_graph([identifier])
    deps = pm.get_ordered_dependencies(dep_graph)
    for pkg_id in deps:
        if not do_enable_package(pm, pkg_id):
            raise NoSuchPackage("Package %r not found" % pkg_id)

    return Package(pkg)


# Copied from VistrailController#try_to_enable_package()
def do_enable_package(pm, identifier):
    pkg = pm.identifier_is_available(identifier)
    if pm.has_package(pkg.identifier):
        return True
    if pkg and not pm.has_package(pkg.identifier):
        pm.late_enable_package(pkg.codepath)
        pkg = pm.get_package_by_codepath(pkg.codepath)
        if pkg.identifier != identifier:
            # pkg is probably a parent of the "identifier" package
            # try to load it
            if (hasattr(pkg.module, 'can_handle_identifier') and
                    pkg.module.can_handle_identifier(identifier)):
                pkg.init_module.load_from_identifier(identifier)
        return True
    # identifier may refer to a subpackage
    if (pkg and pkg.identifier != identifier and
            hasattr(pkg.module, 'can_handle_identifier') and
            pkg.module.can_handle_identifier(identifier) and
            hasattr(pkg.init_module, 'load_from_identifier')):
        pkg.init_module.load_from_identifier(identifier)
        return True
    return False


@contextlib.contextmanager
def output_mode(output, mode, **kwargs):
    """Context manager that makes an output use a specific mode.
    """
    # TODO : Output mode selection
    yield


def run_vistrail(filename, version=None, *args, **kwargs):
    """Shortcut for load_vistrail(filename).execute(...)
    """
    return load_vistrail(filename, version).execute(*args, **kwargs)
