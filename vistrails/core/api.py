import itertools

import vistrails.core.application
from vistrails.core.db.locator import FileLocator
import vistrails.core.db.io
from vistrails.core import debug
from vistrails.core.modules.basic_modules import identifier as basic_pkg
from vistrails.core.modules.module_registry import get_module_registry
from vistrails.core.modules.utils import create_port_spec_string
from vistrails.core.packagemanager import get_package_manager
from vistrails.core.vistrail.pipeline import Pipeline
from vistrails.core.vistrail.port_spec import PortSpec
from vistrails.core.vistrail.vistrail import Vistrail

# from core.modules.package import Package as _Package
# from core.vistrail.module import Module as _Module

_api = None

def get_api():
    if _api is None:
        set_api(VisTrailsAPI())
    return _api

def set_api(api):
    global _api
    _api = api

class Port(object):
    def __init__(self, module, port_spec):
        # print 'calling vistrails_port.__init__'
        self._vistrails_module = module
        self._port_spec = port_spec

    def __call__(self, *args, **kwargs):
        if len(args) + len(kwargs) > 0:
            self._vistrails_module._update_func(self._port_spec,
                                                *args, **kwargs)
            return None
        return self

class Module(object):
    def __init__(self, module, *args, **kwargs):
        self._module = module
        self._module_desc = self._module.module_descriptor
        self._package = None # don't think we need this now
        self.__call__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        reg = get_module_registry()
        if len(args) > 0:
            constant_desc = reg.get_descriptor_by_name(basic_pkg, "Constant")
            if reg.is_descriptor_subclass(self._module_desc, constant_desc):
                kwargs['value'] = args[0]
            
        for attr_name, value in kwargs.iteritems():
            self._process_attr_value(attr_name, value)
        return self

    @staticmethod
    def create_module(module, *args, **kwargs):
        m = Module(module)
        return m

    def _process_attr_value(self, attr_name, value):
        if self._module.has_port_spec(attr_name, 'input'):
            port_spec = self._module.get_port_spec(attr_name, 'input')

            # FIXME want this to be any iterable
            if isinstance(value, tuple):
                self._update_func(port_spec, *value)
            else:
                self._update_func(port_spec, value)
        else:
            raise AttributeError("type object '%s' has no "
                                 "attribute '%s'" % \
                                     (self.__class__.__name__,
                                      attr_name))                

    def __getattr__(self, attr_name):
        def create_port(port_spec):
            return Port(self, port_spec)

        if self._module.has_port_spec(attr_name, 'output'):
            port_spec = \
                self._module.get_port_spec(attr_name, 'output')
            return create_port(port_spec)
        elif self._module.has_port_spec(attr_name, 'input'):
            port_spec = \
                self._module.get_port_spec(attr_name, 'input')
            return create_port(port_spec)
        else:
            raise AttributeError("type object '%s' has no "
                                 "attribute '%s'" % \
                                     (self.__class__.__name__, 
                                      attr_name))

    def __setattr__(self, attr_name, value):
        if attr_name.startswith('_'):
            self.__dict__[attr_name] = value
        else:
            self._process_attr_value(attr_name, value)

    def _update_func(self, port_spec, *args, **kwargs):
        # print 'running _update_func', port_spec.name
        # print args
        vt_api = get_api()

        if port_spec.type != 'input':
            if self._module.has_port_spec(port_spec.name, 'input'):
                port_spec = \
                    self._module.get_port_spec(port_spec.name, 'input')
            else:
                raise TypeError("cannot update an output port spec")

        # FIXME deal with kwargs
        num_ports = 0
        num_params = 0
        for value in args:
            # print 'processing', type(value), value
            if isinstance(value, Port):
                # make connection to specified output port
                # print 'updating port'
                num_ports += 1
            elif isinstance(value, Module):
                # make connection to 'self' output port of value
                # print 'updating module'
                num_ports += 1
            else:
                # print 'update literal', type(value), value
                num_params += 1
        if num_ports > 1 or (num_ports == 1 and num_params > 0):
            reg = get_module_registry()
            tuple_desc = reg.get_descriptor_by_name(basic_pkg, 'Tuple')
            tuple_module = vt_api.add_module_from_descriptor(tuple_desc)
            output_port_spec = PortSpec(id=-1,
                                        name='value',
                                        type='output',
                                        sigstring=port_spec.sigstring)
            vt_api.add_port_spec(tuple_module, output_port_spec)
            self._update_func(port_spec, tuple_module.value())
            assert len(port_spec.descriptors()) == len(args)
            for i, descriptor in enumerate(port_spec.descriptors()):
                arg_name = 'arg%d' % i
                sigstring = create_port_spec_string([descriptor.spec_tuple])
                tuple_port_spec = PortSpec(id=-1,
                                           name=arg_name,
                                           type='input',
                                           sigstring=sigstring)
                vt_api.add_port_spec(tuple_module, tuple_port_spec)
                tuple_module._process_attr_value(arg_name, args[i])
                
        elif num_ports == 1:
            other = args[0]
            if isinstance(other, Port):
                if other._port_spec.type != 'output':
                    other_module = other._vistrails_module._module
                    if other_module.has_port_spec(port_spec.name, 
                                                   'output'):
                        other_port_spec = \
                            other_module.get_port_spec(port_spec.name, 
                                                        'output')
                    else:
                        raise TypeError("cannot update an input "
                                        "port spec")
                else:
                    other_port_spec = other._port_spec

                vt_api.add_connection(other._vistrails_module,
                                      other_port_spec,
                                      self, 
                                      port_spec)
            elif isinstance(other, Module):
                other_port_spec = \
                    other._module.get_port_spec('self', 'output')
                vt_api.add_connection(other, 
                                      other_port_spec,
                                      self,
                                      port_spec)
        else:
            vt_api.change_parameter(self,
                                    port_spec.name,
                                    [str(x) for x in args])

class Package(object):
    def __init__(self, identifier, version=''):
        self._package = None
        # namespace_dict : {namespace : (namespace_dict, modules)}
        self._namespaces = ({}, [])
        reg = get_module_registry()
        self._package = reg.get_package_by_name(identifier, version)
        for desc in self._package.descriptor_list:
            if desc.namespace:
                namespaces = desc.namespace.split('|')
            else:
                namespaces = []
            cur_namespace = self._namespaces[0]
            cur_modules = self._namespaces[1]
            for namespace in namespaces:
                if namespace not in cur_namespace:
                    cur_namespace[namespace] = ({}, [])
                cur_modules = cur_namespace[namespace][1]
                cur_namespace = cur_namespace[namespace][0]
            cur_modules.append(desc)

        iteritems = [self._namespaces]
        for (namespaces, modules) in iteritems:
            modules.sort(key=lambda d: d.name)
            iteritems = itertools.chain(iteritems, namespaces.itervalues())

    def __getattr__(self, attr_name):
        reg = get_module_registry()
        d = reg.get_descriptor_by_name(self._package.identifier,
                                       attr_name, '', 
                                       self._package.version)
        vt_api = get_api()
        module = vt_api.add_module_from_descriptor(d)
        return module
 
    def get_modules(self, namespace=None):
        modules = []
        if namespace == '':
            modules = [d.name for d in self._namespaces[1]]
        else:
            if namespace is None:
                namespace = ''
                modules = [d.name for d in self._namespaces[1]]
                namespaces = sorted(self._namespaces[0].iteritems())
            else:
                namespace_dict = self._namespaces[0]
                descs = self._namespaces[1]
                for ns in namespace.split('|'):
                    (namespace_dict, descs) = namespace_dict[ns]
                namespaces = [(namespace, (namespace_dict, descs))]
            
            for (ns, (child_namespaces, descs)) in namespaces:
                modules.extend(ns + '|' + d.name for d in descs)
                namespaces = \
                    itertools.chain([(ns + '|' + c[0], c[1]) 
                                     for c in child_namespaces.iteritems()],
                                    namespaces)
        return modules

    def list_modules(self, namespace=None):
        for module in self.get_modules(namespace):
            print module

class VisTrailsAPI(object):

    # !!! Do not pass controller or app unless you know what you are doing !!!
    def __init__(self, controller=None, app=None):
        self._controller = controller
        self._app = app
        self._packages = None
        self._old_log = None

    def _get_app(self):
        if self._app is not None:
            return self._app
        return vistrails.core.application.get_vistrails_application()
    app = property(_get_app)

    # !!! Do not call set_app unless you know what you are doing !!!
    def set_app(self, app):
        self._app = app

    def _get_controller(self):
        if self._controller is not None:
            return self._controller
        controller = self.app.get_controller()
        if controller is None:
            raise ValueError("You must have a vistrail open before calling "
                             "this API method.")
        return controller
    controller = property(_get_controller)

    # !!! Do not call set_controller unless you know what you are doing !!!
    def set_controller(self, controller=None):
        self._controller = controller

    def add_module(self, identifier, name, namespace='', internal_version=-1):
        m = self.controller.add_module(identifier, name, namespace, 
                                       internal_version=internal_version)
        # have to go back since there is a copy when the action is performed
        module = self.controller.current_pipeline.modules[m.id]
        return Module.create_module(module)

    def add_module_from_descriptor(self, desc):
        m = self.controller.add_module_from_descriptor(desc)
        # have to go back since there is a copy when the action is performed
        module = self.controller.current_pipeline.modules[m.id]
        return Module.create_module(module)

    def add_connection(self, module_a, port_a, module_b, port_b):
        conn = self.controller.add_connection(module_a._module.id, port_a,
                                               module_b._module.id, port_b)

    def add_port_spec(self, module, port_spec):
        self.controller.add_module_port(module._module.id,
                                         (port_spec.type, port_spec.name,
                                          port_spec.sigstring))

    def add_and_connect_module(self,
                               identifier,
                               name,
                               port,
                               module_b,
                               port_b,
                               is_source=False,
                               auto_layout=True,
                               **kwargs):
        """Adds a module and connects in single action. Returns new module.

        identifier - package identifier for new module
        name - name of new module
        module_b - existing module to connect new module to
        port - port on new module to connect
        port_b - port on existing module to connect
        is_source - whether or not new module is source of connection
        auto_layout - layout pipeline
        **kwargs - additional arguments to create module
        """

        module = self.controller.create_module(identifier, name, **kwargs)

        if is_source:
            source, source_port = module, port
            target, target_port = module_b._module, port_b
        else:
            target, target_port = module, port
            source, source_port = module_b._module, port_b

        create_conn = self.controller.create_connection
        conn = create_conn(source, source_port, target, target_port)

        if auto_layout:
            layout = self.controller.layout_modules_ops
            layout_ops = layout([], True, [module], [conn], None, True)
        else:
            layout_ops = []

        ops = [('add', module), ('add', conn)] + layout_ops
        action = vistrails.core.db.action.create_action(ops)
        self.controller.add_new_action(action)
        version = self.controller.perform_action(action)
        self.controller.change_selected_version(version)

        # have to go back since there is a copy when the action is performed
        m = self.controller.current_pipeline.modules[module.id]
        return Module.create_module(m)

    def change_parameter(self, module, function_name, param_list):
        self.controller.update_function(module._module, function_name,
                                         param_list)

    def execute(self, custom_aliases=None, custom_params=None,
                 extra_info=None, reason='API Pipeline Execution'):
        return self.controller.execute_current_workflow(custom_aliases, custom_params,
                                                        extra_info, reason)

    def get_packages(self):
        if self._packages is None:
            self._packages = {}
            self._old_package_ids = {}
            reg = get_module_registry()
            for package in reg.package_list:
                pkg = Package(package.identifier, package.version)
                self._packages[package.identifier] = pkg
                for old_name in package.old_identifiers:
                    self._old_package_ids[old_name] = pkg
        return self._packages

    def list_packages(self):
        for package in self.get_packages():
            print package

    def get_package(self, identifier):
        packages = self.get_packages()
        if identifier not in packages and identifier in self._old_package_ids:
            return self._old_package_ids[identifier]
        else:
            return packages[identifier]

    def load_package(self, identifier, codepath):
        packages = self.get_packages()
        if identifier not in packages:
            pm = get_package_manager()
            pm.late_enable_package(codepath)
            self._packages = None
        return self.get_package(identifier)
            
    def list_modules(self):
        for identifier, package in sorted(self.get_packages().iteritems()):
            print identifier
            for module in package.get_modules():
                print ' --', module

    def _convert_version(self, version):
        if isinstance(version, basestring):
            try:
                version = \
                    self.controller.vistrail.get_version_number(version)
            except Exception, e:
                debug.unexpected_exception(e)
                raise ValueError('Cannot locate version "%s"' % version)
        return version

    def tag_version(self, tag, version=None):
        if version is None:
            version = self.controller.current_version
        else:
            version = self._convert_version(version)
        self.controller.vistrail.set_tag(version, tag)

    def save_vistrail(self, locator_str):
        return self.app.save_vistrail(locator_str)

    def new_vistrail(self):
        return bool(self.app.new_vistrail())

    def load_vistrail(self, locator_str):
        return bool(self.app.open_vistrail(locator_str))
    open_vistrail = load_vistrail

    def load_workflow(self, locator_str):
        self.app.open_workflow(locator_str)
    open_workflow = load_workflow

    def select_version(self, version):
        self.app.select_version(version)

    def close_vistrail(self):
        self.app.close_vistrail()

    def get_current_workflow(self):
        return self.controller.current_pipeline

    def get_all_executions(self):
        wf_execs = []
        if (self._old_log is None and
            hasattr(self.controller.vistrail, 'db_log_filename') and
            self.controller.vistrail.db_log_filename is not None):
            self._old_log = \
                vistrails.core.db.io.open_log(self.controller.vistrail.db_log_filename, True)
        if self._old_log is not None:
            wf_execs.extend(self._old_log.workflow_execs)
        wf_execs.extend(self.controller.log.workflow_execs)
        return wf_execs

import os
import tempfile
import unittest

class TestAPI(unittest.TestCase):
    if not hasattr(unittest.TestCase, 'assertIsInstance'):
        def assertIsInstance(self, obj, cls, msg=None):
            assert(isinstance(obj, cls))
    
    @classmethod
    def setUpClass(cls):
        get_api().new_vistrail()

    @classmethod
    def tearDownClass(cls):
        get_api().close_vistrail()

    def setUp(self):
        get_api().controller.change_selected_version(0)

    def get_basic_package(self):
        basic = get_api().get_package(basic_pkg)
        self.assertIsInstance(basic, Package)
        return basic

    def create_modules(self,basic):
        s1 = basic.String("abc")
        self.assertIsInstance(s1, Module)
        s2 = basic.String("def")
        self.assertIsInstance(s2, Module)
        return s1, s2
        
    def test_api(self):
        self.get_basic_package()

    def test_add_modules(self):
        basic = self.get_basic_package()
        s1, s2 = self.create_modules(basic)

        # assert there exist two String modules
        self.assertEqual(len(get_api().controller.current_pipeline.modules), 2)
        for m in get_api().controller.current_pipeline.modules.itervalues():
            self.assertEqual(m.package, basic_pkg)
            self.assertEqual(m.name, "String")

    def check_connections(self):
        conns = []
        modules = get_api().controller.current_pipeline.modules
        for c in get_api().controller.current_pipeline.connections.itervalues():
            conns.append((modules[c.sourceId].name, c.source.name,
                          modules[c.destinationId].name, c.destination.name))
        conns.sort()
        self.assertEqual(conns,
                         [('String', 'value', 'ConcatenateString', 'str1'),
                          ('String', 'value', 'ConcatenateString', 'str2')])

    def test_add_connections_by_assignment(self):
        basic = self.get_basic_package()
        s1, s2 = self.create_modules(basic)
        c = basic.ConcatenateString()
        c.str1 = s1.value
        c.str2 = s2.value
        self.check_connections()

    def test_add_connections_by_call(self):
        basic = self.get_basic_package()
        s1, s2 = self.create_modules(basic)
        c = basic.ConcatenateString()
        c.str1(s1.value)
        c.str2(s2.value)
        self.check_connections()

    def test_add_connections_by_constructor(self):
        basic = self.get_basic_package()
        s1, s2 = self.create_modules(basic)
        c = basic.ConcatenateString(str1=s1.value, str2=s2.value)
        self.check_connections()

    def check_parameters(self):
        params = []
        for m in get_api().controller.current_pipeline.modules.itervalues():
            for f in m.functions:
                params.append((m.name, f.name, f.params[0].strValue))
        params.sort()
        self.assertEqual(params,
                         [('String', 'value', 'abc'),
                          ('String', 'value', 'def')])
            
    def test_add_parameters_by_assignment(self):
        basic = self.get_basic_package()
        s1, s2 = self.create_modules(basic)
        s1.value = "abc"
        s2.value = "def"
        self.check_parameters()

    def test_add_parameters_by_call(self):
        basic = self.get_basic_package()
        s1, s2 = self.create_modules(basic)
        s1.value("abc")
        s2.value("def")
        self.check_parameters()

    def test_add_parameters_by_constructor(self):
        basic = self.get_basic_package()
        s1 = basic.String("abc")
        s2 = basic.String("def")
        self.check_parameters()

    def test_write_and_read_vistrail(self):
        self.assertTrue(get_api().new_vistrail())
        basic = self.get_basic_package()
        s1, s2 = self.create_modules(basic)
        fdesc, fname = tempfile.mkstemp(prefix='vt_test_write_read_',
                                 suffix='.vt')
        os.close(fdesc)
        try:
            self.assertTrue(get_api().save_vistrail(fname))
            self.assertTrue(os.path.exists(fname))
            get_api().close_vistrail()
            self.assertTrue(get_api().open_vistrail(fname))
            self.assertEqual(get_api().controller.current_version, 4)
            get_api().close_vistrail()
        finally:
            os.remove(fname)

if __name__ == '__main__':
    vistrails.core.application.init()
    unittest.main()
