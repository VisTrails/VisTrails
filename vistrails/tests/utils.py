import contextlib


def execute(modules, connections=[]):
    """Build a pipeline and execute it.

    This is useful to simply build a pipeline in a test case, and run it. When
    doing that, intercept_result() can be used to check the results of each
    module.

    modules is a list of module tuples describing the modules to be created,
    with the following format:
        [('ModuleName', 'package.identifier', [
            # Functions
            ('port_name', [
                # Function parameters
                ('Signature', 'value-as-string'),
            ]),
        ])]

    connections is a list of tuples describing the connections to make, with
    the following format:
        [
            (source_module_index, 'source_port_name',
             dest_module_index, 'dest_module_name'),
         ]

    The function returns the 'errors' dict it gets from the interpreter, so you
    should use a construct like self.assertFalse(execute(...)) if the execution
    is not supposed to fail.


    For example, this creates (and runs) an Integer module with its value set
    to 44, connected to a PythonCalc module, connected to a StandardOutput:

    self.assertFalse(execute([
            ('Float', 'org.vistrails.vistrails.basic', [
                ('value', [('Float', '44.0')]),
            ]),
            ('PythonCalc', 'edu.utah.sci.vistrails.pythoncalc', [
                ('value2', [('Float', '2.0')]),
                ('op', [('String', '-')]),
            ]),
            ('StandardOutput', 'org.vistrails.vistrails.basic', []),
        ],
        [
            (0, 'value', 1, 'value1'),
            (1, 'value', 2, 'value'),
        ]))
    """
    from vistrails.core.db.locator import XMLFileLocator
    from vistrails.core.interpreter.default import get_default_interpreter
    from vistrails.core.packagemanager import get_package_manager
    from vistrails.core.utils import DummyView
    from vistrails.core.vistrail.connection import Connection
    from vistrails.core.vistrail.module import Module
    from vistrails.core.vistrail.module_function import ModuleFunction
    from vistrails.core.vistrail.module_param import ModuleParam
    from vistrails.core.vistrail.pipeline import Pipeline
    from vistrails.core.vistrail.port import Port

    pm = get_package_manager()

    pipeline = Pipeline()
    module_list = []
    for name, identifier, functions in modules:
        function_list = []
        pkg = pm.get_package_by_identifier(identifier)
        for func_name, params in functions:
            param_list = []
            for param_type, param_val in params:
                param_list.append(ModuleParam(type=param_type,
                                              val=param_val))
            function_list.append(ModuleFunction(name=func_name,
                                                parameters=param_list))
        module = Module(name=name,
                        package=identifier,
                        version=pkg.version,
                        id=len(module_list),
                        functions=function_list)
        pipeline.add_module(module)
        module_list.append(module)

    for i, (sid, sport, did, dport) in enumerate(connections):
        s_sig = module_list[sid].get_port_spec(sport, 'output').sigstring
        d_sig = module_list[did].get_port_spec(dport, 'input').sigstring
        pipeline.add_connection(Connection(
                id=i,
                ports=[
                    Port(id=i*2,
                         type='source',
                         moduleId=module_list[sid].id,
                         name=sport,
                         signature=s_sig),
                    Port(id=i*2+1,
                         type='destination',
                         moduleId=module_list[did].id,
                         name=dport,
                         signature=d_sig),
                ]))

    interpreter = get_default_interpreter()
    result = interpreter.execute(
            pipeline,
            locator=XMLFileLocator('foo.xml'),
            current_version=1,
            view=DummyView())
    return result.errors


@contextlib.contextmanager
def intercept_result(module, output_name):
    """This temporarily hooks a module to intercept its results.

    It is used as a context manager, for instance:
    class MyModule(Module):
        def compute(self):
            self.setResult('res', 42)
        ...
    with intercept_result(MyModule, 'res') as results:
        self.assertFalse(execute(...))
    self.assertEqual(results, [42])
    """
    old_setResult = module.setResult
    results = []
    def new_setResult(self, name, value):
        if name == output_name:
            results.append(value)
        old_setResult(self, name, value)
    module.setResult = new_setResult
    try:
        yield results
    finally:
        module.setResult = old_setResult
