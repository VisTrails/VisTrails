import itertools

import core.application
from core.db.locator import FileLocator
import core.db.io
from core.modules.module_registry import get_module_registry
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
            constant_desc = \
                reg.get_descriptor_by_name("edu.utah.sci.vistrails.basic",  \
                                                "Constant")
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

            args = None
            # FIXME want this to be any iterable
            if type(value) == tuple:
                args = value
            else:
                args = (value,)
            self._update_func(port_spec, *args)
        else:
            raise AttributeError("type object '%s' has no "
                                 "attribute '%s'" % \
                                     (self.__class__.__name__,
                                      attr_name))                

    def __getattr__(self, attr_name):
        def create_port(port_spec):
            return Port(self, port_spec)
        try:
            return self.__dict__[attr_name]
        except KeyError:
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
                raise Exception("cannot update an output port spec")

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
            reg = core.modules.module_registry.get_module_registry()
            tuple_desc = \
                reg.get_descriptor_by_name('edu.utah.sci.vistrails.basic',
                                           'Tuple', '')

            d = {'_module_desc': tuple_desc,
                 '_package': self._package,}
            tuple = type('module', (Module,), d)()

            output_port_spec = PortSpec(id=-1,
                                        name='value',
                                        type='output',
                                        sigstring=port_spec.sigstring)
            vt_api.add_port_spec(tuple._module.id, output_port_spec)
            self._update_func(port_spec, *[tuple.value()])
            assert len(port_spec.descriptors()) == len(args)
            for i, descriptor in enumerate(port_spec.descriptors()):
                arg_name = 'arg%d' % i
                sigstring = "(" + descriptor.sigstring + ")"
                tuple_port_spec = PortSpec(id=-1,
                                           name=arg_name,
                                           type='input',
                                           sigstring=sigstring)
                vt_api.add_port_spec(tuple._module.id, tuple_port_spec)
                tuple._process_attr_value(arg_name, args[i])
                
                
            # create tuple object
            pass
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
                        raise Exception("cannot update an input "
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
        try:
            return self.__dict__[attr_name]
        except KeyError:
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

    def __init__(self, app=None):
        if app is None:
            app = core.application.get_vistrails_application()
        self._packages = None
        self._controller = app.get_controller()
        self._old_log = None

    def add_module(self, identifier, name, namespace='', internal_version=-1):
        module = self._controller.add_module(identifier, name, namespace, 
                                             internal_version=internal_version)
        return Module.create_module(module)

    def add_module_from_descriptor(self, desc):
        module = self._controller.add_module_from_descriptor(desc)
        return Module.create_module(module)

    def add_connection(self, module_a, port_a, module_b, port_b):
        conn = self._controller.add_connection(module_a._module.id, port_a,
                                               module_b._module.id, port_b)

    def add_port_spec(self, module, port_spec):
        self._controller.add_port_spec(module._module.id,
                                       (port_spec.type, port_spec.name,
                                        port_spec.sigstring))

    def change_parameter(self, module, function_name, param_list):
        self._controller.update_function(module._module, function_name,
                                         param_list)

    def execute(self, custom_aliases=None, custom_params=None,
                 extra_info=None, reason='API Pipeline Execution'):
        self._controller.execute_current_workflow(custom_aliases, custom_params,
                                                  extra_info, reason)

    def get_packages(self):
        if self._packages is None:
            self._packages = {}
            reg = get_module_registry()
            for package in reg.package_list:
                pkg = Package(package.identifier, package.version)
                self._packages[package.identifier] = pkg
        return self._packages
        
    def list_packages(self):
        for package in self.get_packages():
            print package

    def get_package(self, identifier):
        packages = self.get_packages()
        return packages[identifier]
            
    def list_modules(self):
        for identifier, package in sorted(self.get_packages().iteritems()):
            print identifier
            for module in package.get_modules():
                print ' --', module

    def _convert_version(self, version):
        if type(version) == type(""):
            try:
                version = \
                    self._controller.vistrail.get_version_number(version)
            except:
                raise Exception('Cannot locate version "%s"' % version)
        return version

    def tag_version(self, tag, version=None):
        if version is None:
            version = self._controller.current_version
        else:
            version = self._convert_version(version)
        self._controller.vistrail.set_tag(version, tag)

    def save_vistrail(self, fname, version=None):
        locator = FileLocator(fname)
        self._controller.write_vistrail(locator, version)

    def load_vistrail(self, fname):
        self._old_logs = None
        locator = FileLocator(fname)
        (vistrail, abstraction_files, thumbnail_files, mashups) = \
            core.db.io.load_vistrail(locator, False)
        self._controller.set_vistrail(vistrail, locator, abstraction_files,
                                      thumbnail_files, mashups)
        self._controller.select_latest_version()
        
    def select_version(self, version):
        self._controller.change_selected_version(self._convert_version(version))

    def close_vistrail(self):
        self._controller.close_vistrail(self._controller.get_locator())

    def get_current_workflow(self):
        return self._controller.current_pipeline

    def get_all_executions(self):
        wf_execs = []
        if (self._old_log is None and
            hasattr(self._controller.vistrail, 'db_log_filename') and
            self._controller.vistrail.db_log_filename is not None):
            self._old_log = \
                core.db.io.open_log(self._controller.vistrail.db_log_filename, True)
        if self._old_log is not None:
            wf_execs.extend(self._old_log.workflow_execs)
        wf_execs.extend(self._controller.log.workflow_execs)
        return wf_execs

