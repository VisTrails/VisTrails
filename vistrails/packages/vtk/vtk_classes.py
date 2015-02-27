""" Convert VTK classes into functions using spec in vtk.xml"""
import locale
import os
import re
import warnings

import vtk

from . import fix_classes
from .wrapper import VTKInstanceWrapper

from .generate.specs import SpecList, VTKModuleSpec

################################################################################

# filter some deprecation warnings coming from the fact that vtk calls
# range() with float parameters

warnings.filterwarnings("ignore",
                        message="integer argument expected, got float")


#### METHOD PATCHING CODE ####

file_name_pattern = re.compile('.*FileName$')
set_file_name_pattern = re.compile('Set.*FileName$')

def patch_methods(base_module, cls):
    """class_dict(base_module, cls: vtkClass) -> dict
    Returns the class dictionary for the module represented by base_module and
    with base class base_module"""

    instance_dict = {}
    def update_dict(name, callable_):
        if instance_dict.has_key(name):
            instance_dict[name] = callable_(instance_dict[name])
        elif hasattr(base_module, name):
            instance_dict[name] = callable_(getattr(base_module, name))
        else:
            instance_dict[name] = callable_(None)

    def compute_VTKCell(old_compute):
        if old_compute is not None:
            return old_compute
        def call_SetRenderWindow(self, vtkInstance, cellObj):
            if cellObj.cellWidget:
                vtkInstance.SetRenderWindow(cellObj.cellWidget.mRenWin)
        return call_SetRenderWindow
    
    def compute_TransferFunction(old_compute):
        if old_compute is not None:
            return old_compute
        def call_TransferFunction(self, vtkInstance, tf):
            tf.set_on_vtk_volume_property(vtkInstance)
        return call_TransferFunction

    def compute_PointData(old_compute):
        if old_compute is not None:
            return old_compute
        def call_PointData(self, vtkInstance, pd):
            vtkInstance.GetPointData().ShallowCopy(pd)
        return call_PointData

    def compute_CellData(old_compute):
        if old_compute is not None:
            return old_compute
        def call_CellData(self, vtkInstance, cd):
            vtkInstance.GetCellData().ShallowCopy(cd)
        return call_CellData

    def compute_PointIds(old_compute):
        if old_compute is not None:
            return old_compute
        def call_PointIds(self, vtkInstance, point_ids):
            vtkInstance.GetPointIds().SetNumberOfIds(point_ids.GetNumberOfIds())
            for i in xrange(point_ids.GetNumberOfIds()):
                vtkInstance.GetPointIds().SetId(i, point_ids.GetId(i))
        return call_PointIds

    def compute_CopyImportString(old_compute):
        if old_compute is not None:
            return old_compute
        def call_CopyImportVoidPointer(self, vtkInstance, pointer):
            vtkInstance.CopyImportVoidPointer(pointer, len(pointer))
        return call_CopyImportVoidPointer

    if hasattr(cls, 'SetRenderWindow'):
        update_dict('_special_input_function_VTKCell',
                    compute_VTKCell)
    if issubclass(cls, vtk.vtkVolumeProperty):
        update_dict('_special_input_function_SetTransferFunction',
                    compute_TransferFunction)
    if issubclass(cls, vtk.vtkDataSet):
        update_dict('_special_input_function_PointData',
                    compute_PointData)
        update_dict('_special_input_function_CellData',
                    compute_CellData)
    if issubclass(cls, vtk.vtkCell):
        update_dict('_special_input_function_PointIds',
                    compute_PointIds)
    if issubclass(cls, vtk.vtkImageImport):
        update_dict('_special_input_function_CopyImportString',
                    compute_CopyImportString)

    for name, method in instance_dict.iteritems():
        setattr(base_module, name, method)

#### END METHOD PATCHING CODE ####


class vtkObjectInfo(object):
    """ Class that can expose a VTK class as a function

    """
    def __init__(self, spec, parent=None):
        self.parent = parent
        self.spec = spec
        self.vtkClass = getattr(vtk, spec.code_ref)
        # use fixed classes
        if hasattr(fix_classes, self.vtkClass.__name__ + '_fixed'):
            self.vtkClass = getattr(fix_classes, self.vtkClass.__name__ + '_fixed')
        self.set_method_table = {}
        for ps in spec.input_port_specs:
            self.set_method_table[ps.arg] = (ps.method_name, ps.get_port_shape(),
                                         ps.get_other_params())
        self.get_method_table = {}
        for ps in spec.output_port_specs:
            self.get_method_table[ps.arg] = (ps.method_name, ps.get_other_params())

        # patch vtk methods
        patch_methods(self, self.vtkClass)

    # cache input specs lookups
    cached_input_port_specs = None
    def get_input_port_specs(self):
        """ Get inputs from parents as well, but skip duplicates
        """
        if self.cached_input_port_specs is not None:
            return self.cached_input_port_specs
        specs = self.spec.input_port_specs
        ports = [spec.arg for spec in specs]
        if self.parent:
            for spec in reversed(self.parent.get_input_port_specs()):
                if spec.arg not in ports:
                    specs.insert(0, spec)
        self.cached_input_port_specs = specs
        return specs

    # cache output specs lookups
    cached_output_port_specs = None
    def get_output_port_specs(self):
        if self.cached_output_port_specs is not None:
            return self.cached_output_port_specs
        specs = self.spec.output_port_specs
        ports = [spec.arg for spec in specs]
        if self.parent:
            for spec in reversed(self.parent.get_output_port_specs()):
                if spec.arg not in ports:
                    specs.insert(0, spec)
        self.cached_output_port_specs = specs
        return specs

    def get_set_method_info(self, port_name):
        if port_name in self.set_method_table:
            return self.set_method_table[port_name]
        return self.parent.get_set_method_info(port_name) if self.parent else None

    def get_get_method_info(self, port_name):
        if port_name in self.get_method_table:
            return self.get_method_table[port_name]
        return self.parent.get_get_method_info(port_name) if self.parent else None

    def call_set_method(self, vtk_obj, port, params):
        info = self.get_set_method_info(port.arg)
        if info is None:
            raise Exception('Internal error: cannot find '
                            'port "%s"' % port.arg)
        method_name, shape, other_params = info

        if isinstance(params, tuple):
            params = list(params)
        elif not isinstance(params, list):
            params = [params]
        if port.port_type == 'basic:Boolean':
            if not params[0]:
                if method_name.endswith('On'):
                    # This is a toggle method
                    method_name = method_name[:-2] + 'Off'
                else:
                    # Skip False 0-parameter method
                    return
            params = []
        elif port.entry_types and 'enum' in port.entry_types:
            # handle enums
            # Append enum name to function name and delete params
            method_name += params[0]
            params = []
        if shape is not None:
            def reshape_params(p, s):
                out = []
                for elt in s:
                    if isinstance(elt, list):
                        out.append(reshape_params(p, elt))
                    else:
                        for i in xrange(elt):
                            out.append(p.pop(0))
                return out
            params = reshape_params(params, shape)
        # Unwraps VTK objects
        for i in xrange(len(params)):
            if hasattr(params[i], 'vtkInstance'):
                params[i] = params[i].vtkInstance
        try:
            if hasattr(self, '_special_input_function_' + method_name):
                method = getattr(self, '_special_input_function_' +
                                 method_name)
                method(self, vtk_obj, *(other_params + params))
            else:
                method = getattr(vtk_obj, method_name)
                method(*(other_params + params))
        except Exception, e:
            raise

    def call_set_methods(self, vtk_obj, inputs):
        input_specs = self.get_input_port_specs()
        methods = [input for input in input_specs if not input.show_port]
        connections = [input for input in input_specs if input.show_port]

        # Compute methods from visible ports last
        #In the case of a vtkRenderer,
        # we need to call the methods after the
        #input ports are set.
        if isinstance(vtk_obj, vtk.vtkRenderer):
            ports = connections + methods
        else:
            ports = methods + connections
        for port in ports:
            if port.arg in inputs:
                params = inputs[port.arg]
                # Call method once for each item in depth1 lists
                if port.depth == 0:
                    params = [params]
                for ps in params:
                    self.call_set_method(vtk_obj, port, ps)

    def call_get_method(self, vtk_obj, port_name):
        info = self.get_get_method_info(port_name)
        if info is None:
            raise Exception('Internal error: cannot find '
                            'port "%s"' % port_name)
        method_name, other_params = info
        method = getattr(vtk_obj, method_name)
        try:
            return method(*other_params)
        except Exception, e:
            raise

    def do_algorithm_update(self, vtk_obj, callback=None):
        if callback is None:
            vtk_obj.Update()
            return
        is_aborted = [False]
        cbId = None
        def ProgressEvent(obj, event):
            try:
                callback(obj.GetProgress())
            except Exception, e:
                if e.__name__ == 'AbortExecution':
                    obj.SetAbortExecute(True)
                    vtk_obj.RemoveObserver(cbId)
                    is_aborted[0] = True
                else:
                    raise
        cbId = vtk_obj.AddObserver('ProgressEvent', ProgressEvent)
        vtk_obj.Update()
        if not is_aborted[0]:
            vtk_obj.RemoveObserver(cbId)

    #### COMPUTE PATCHING CODE ####

    def patch_inputs(self, vtk_obj, kwargs):
        if hasattr(self.vtkClass, 'SetFileName') and \
           self.vtkClass.__name__.endswith('Reader') and \
           not self.vtkClass.__name__.endswith('TiffReader'):
            # This checks for the presence of file in VTK readers
            # Skips the check if it's a vtkImageReader or vtkPLOT3DReader, because
            # it has other ways of specifying files, like SetFilePrefix for
            # multiple files
            skip = [vtk.vtkBYUReader,
                    vtk.vtkImageReader,
                    vtk.vtkDICOMImageReader,
                    vtk.vtkTIFFReader]
            # vtkPLOT3DReader does not exist from version 6.0.0
            v = vtk.vtkVersion()
            version = [v.GetVTKMajorVersion(),
                       v.GetVTKMinorVersion(),
                       v.GetVTKBuildVersion()]
            if version < [6, 0, 0]:
                skip.append(vtk.vtkPLOT3DReader)
            if not any(issubclass(self.vtkClass, x) for x in skip):
                if 'FileName' in kwargs:
                    name = kwargs['FileName']
                else:
                    raise Exception('Missing filename')
                if not os.path.isfile(name):
                    raise Exception('File does not exist')

    def patch_outputs(self, vtk_obj, inputs, outputs):
        if issubclass(self.vtkClass, vtk.vtkWriter):
            # The behavior for vtkWriter subclasses is to call Write()
            # If the user sets a name, we will create a file with that name
            # If not, we will create a temporary file from the file pool
            fn = vtk_obj.GetFileName()
            if not fn:
                fn = inputs['_tempfile'](suffix='.vtk')
                vtk_obj.SetFileName(fn)
            vtk_obj.Write()
            outputs['file'] = fn
        elif issubclass(self.vtkClass, vtk.vtkScalarTree):
            vtk_obj.BuildTree()

    #### END COMPUTE PATCHING CODE ####

    # compute does not mutate class instance.
    # compute is treated as a function, having no state.
    def compute(self, **inputs):
        # fixes reading data files on non-C locales
        previous_locale = locale.setlocale(locale.LC_ALL)
        locale.setlocale(locale.LC_ALL, 'C')
        vtk_obj = self.vtkClass()

        self.patch_inputs(vtk_obj, inputs)

        self.call_set_methods(vtk_obj, inputs)
        if self.spec.is_algorithm:
            self.do_algorithm_update(vtk_obj, inputs.get('_callback'))
        elif hasattr(vtk_obj, 'Update'):
            vtk_obj.Update()

        outputs = {}
        output_names = [out_spec.arg for out_spec in self.get_output_port_specs()]
        for out_name in output_names:
            result = None
            if out_name == 'Instance':
                result = VTKInstanceWrapper(vtk_obj) # For old PythonSources using .vtkInstance
            elif not self.spec.outputs or out_name in inputs['_outputs']:
                # port is connected
                result = self.call_get_method(vtk_obj, out_name)
                if isinstance(result, vtk.vtkObject):
                    result = VTKInstanceWrapper(result)
            outputs[out_name] = result

        self.patch_outputs(vtk_obj, inputs, outputs)

        # return values based on output_type
        if self.spec.output_type is None:
            return outputs.values()[0]
        locale.setlocale(locale.LC_ALL, previous_locale)
        if self.spec.output_type == 'list':
            return [outputs.get(name, None) for name in output_names]
        else:
            return outputs


# keep track of created modules for use as subclasses
infoObjs = {}

def gen_function(spec):
    """Create a function from a vtk class specification

    """
    infoObj = vtkObjectInfo(spec, infoObjs.get(spec.superklass, None))
    compute = infoObj.compute
    compute.__func__.__name__ = spec.module_name
    infoObjs[spec.module_name] = infoObj
    return compute


def initialize(spec_name=None):
    """ Generate vtk functions and add them to current module namespace
        Also adds spec so it can be referenced by module wrapper
    """
    if spec_name is None:
        # The spec can be placed in the same folder if used as a standalone package
        spec_name = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'vtk.xml')
        if not os.path.exists(spec_name):
            return
    specs = SpecList.read_from_xml(spec_name, VTKModuleSpec)
    globals()['specs'] = specs
    for spec in specs.module_specs:
        globals()[spec.module_name] = gen_function(spec)
# Try to initialize
initialize()
