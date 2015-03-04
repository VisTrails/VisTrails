""" Convert VTK classes into functions using spec in vtk.xml"""
import locale
import os
import re
import tempfile
import types
import warnings

import vtk

from . import fix_classes
from .wrapper import VTKInstanceWrapper
from .generate.specs import SpecList, ClassSpec

################################################################################

# filter some deprecation warnings coming from the fact that vtk calls
# range() with float parameters

warnings.filterwarnings("ignore",
                        message="integer argument expected, got float")

#### METHOD PATCHING CODE ####

def patch_methods(base_module, cls):
    """class_dict(base_module, cls: vtkClass) -> dict
    Returns the class dictionary for the module represented by base_module and
    with base class base_module"""

    instance_dict = {}
    def update_dict(name, callable_):
        if instance_dict.has_key(name):
            instance_dict[name] = callable_(types.MethodType(instance_dict[name], base_module))
        elif hasattr(base_module, name):
            instance_dict[name] = callable_(getattr(base_module, name))
        else:
            instance_dict[name] = callable_(None)

    def compute_UpdateAlgorithm(oldUpdate):
        def call_UpdateAlgorithm(self):
            if self._callback is None:
                oldUpdate()
                return
            is_aborted = [False]
            cbId = None
            def ProgressEvent(obj, event):
                try:
                    self._callback(obj.GetProgress())
                except Exception, e:
                    if e.__name__ == 'AbortExecution':
                        obj.SetAbortExecute(True)
                        self.RemoveObserver(cbId)
                        is_aborted[0] = True
                    else:
                        raise
            cbId = self.AddObserver('ProgressEvent', ProgressEvent)
            oldUpdate()
            if not is_aborted[0]:
                self.RemoveObserver(cbId)
        return call_UpdateAlgorithm
    if issubclass(cls, vtk.vtkAlgorithm):
        update_dict('Update', compute_UpdateAlgorithm)

    def guarded_SimpleScalarTree_wrap_compute(old_compute):
        # This builds the scalar tree
        def compute(self):
            old_compute(self)
            self.vtkInstance.BuildTree()
        return compute
    if issubclass(cls, vtk.vtkScalarTree):
        update_dict('Update', guarded_SimpleScalarTree_wrap_compute)

    def guarded_Writer_wrap_compute(self):
        # The behavior for vtkWriter subclasses is to call Write()
        # If the user sets a name, we will create a file with that name
        # If not, we will create a temporary file using _tempfile
        fn = self.vtkInstance.GetFileName()
        if not fn:
            fn = self._tempfile(suffix='.vtk')
            self.vtkInstance.SetFileName(fn)
        self.vtkInstance.Write()
        return fn
    if issubclass(cls, vtk.vtkWriter):
        instance_dict['file'] = guarded_Writer_wrap_compute

    def guarded_SetFileName(old_compute):
        # This builds the scalar tree
        def check_SetFileName(self):
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
            if not any(issubclass(cls, x) for x in skip):
                filename = self.vtkInstance.GetFileName()
                if not os.path.isfile(filename):
                    raise Exception('File does not exist')
            old_compute()
        return check_SetFileName
    if hasattr(cls, 'SetFileName') and \
       cls.__name__.endswith('Reader') and \
       not cls.__name__.endswith('TiffReader'):
        update_dict('Update', guarded_SetFileName)

    def call_SetRenderWindow(self, cellObj):
        if cellObj.cellWidget:
            self.vtkInstance.SetRenderWindow(cellObj.cellWidget.mRenWin)
    if hasattr(cls, 'SetRenderWindow'):
        instance_dict['VTKCell'] = call_SetRenderWindow

    def call_TransferFunction(self, tf):
        tf.set_on_vtk_volume_property(self.vtkInstance)
    if issubclass(cls, vtk.vtkVolumeProperty):
        instance_dict['SetTransferFunction'] = call_TransferFunction

    def call_PointData(self, pd):
        self.vtkInstance.GetPointData().ShallowCopy(pd.vtkInstance)
    def call_CellData(self, cd):
        self.vtkInstance.GetCellData().ShallowCopy(cd.vtkInstance)
    if issubclass(cls, vtk.vtkDataSet):
        instance_dict['PointData'] = call_PointData
        instance_dict['CellData'] = call_CellData

    def call_PointIds(self, point_ids):
        self.vtkInstance.GetPointIds().SetNumberOfIds(point_ids.GetNumberOfIds())
        for i in xrange(point_ids.GetNumberOfIds()):
            self.vtkInstance.GetPointIds().SetId(i, point_ids.vtkInstance.GetId(i))
    if issubclass(cls, vtk.vtkCell):
        instance_dict['PointIds'] = call_PointIds

    def call_CopyImportVoidPointer(self, pointer):
        self.CopyImportVoidPointer(pointer, len(pointer))
        return call_CopyImportVoidPointer
    if issubclass(cls, vtk.vtkImageImport):
        instance_dict['CopyImportString'] = call_CopyImportVoidPointer

    for name, method in instance_dict.iteritems():
        setattr(base_module, name, types.MethodType(method, base_module))

#### END METHOD PATCHING CODE ####


class vtkObjectInfo(object):
    """ Each instance represents a VTK class

    """
    def __init__(self, spec, parent=None):
        self.parent = parent
        self.spec = spec
        self.vtkClass = getattr(vtk, spec.code_ref)
        # use fixed classes
        if hasattr(fix_classes, self.vtkClass.__name__ + '_fixed'):
            self.vtkClass = getattr(fix_classes, self.vtkClass.__name__ + '_fixed')

class VTKInstancePatcher(object):
    """ This is used in place of the vtk instance because it may not be
        safe to set attributes directly on the vtk object.

    """
    def __init__(self, info_obj):
        # fixes reading data files on non-C locales
        self._previous_locale = locale.setlocale(locale.LC_ALL)
        locale.setlocale(locale.LC_ALL, 'C')

        self._info_obj = info_obj
        self._callback = None
        self._tempfile = tempfile.mkstemp
        self.vtkInstance = info_obj.vtkClass()
        patch_methods(self, info_obj.vtkClass)

    def _cleanup(self):
        locale.setlocale(locale.LC_ALL, self._previous_locale)

    def __getattr__(self, name):
        # redirect calls to vtkInstance
        def call_wrapper(*args):
            args = list(args)
            for i in xrange(len(args)):
                if hasattr(args[i], 'vtkInstance'):
                    # Unwrap VTK objects
                    args[i] = args[i].vtkInstance
            args = tuple(args)

            #print "CALLING", name, [a.__class__.__name__ for a in args]
            result = getattr(self.vtkInstance, name)(*args)
            #print "GOT", result.__class__.__name__

            if isinstance(result, vtk.vtkObjectBase):
                # Wrap VTK objects
                result = VTKInstanceWrapper(result)
            return result
        return call_wrapper

    def _set_callback(self, callback):
        self._callback = callback

    def _set_tempfile(self, tempfile):
        self._tempfile = tempfile
        
    def Update(self):
        if hasattr(self.vtkInstance, 'Update'):
            self.vtkInstance.Update()

# keep track of created modules for use as subclasses
infoObjs = {}


def gen_instance_factory(spec):
    """Create an instance factory from a vtk class specification

    """
    infoObj = vtkObjectInfo(spec, infoObjs.get(spec.superklass, None))
    infoObjs[spec.module_name] = infoObj
    def instanceFactory():
        return VTKInstancePatcher(infoObj)
    return instanceFactory


def initialize(spec_name=None):
    """ Generate class wrappers and add them to current module namespace
        Also adds spec so it can be referenced by module wrapper

    """
    if spec_name is None:
        # The spec can be placed in the same folder if used as a standalone package
        spec_name = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'vtk.xml')
        if not os.path.exists(spec_name):
            return
    specs = SpecList.read_from_xml(spec_name, ClassSpec)
    globals()['specs'] = specs
    for spec in specs.module_specs:
        globals()[spec.module_name] = gen_instance_factory(spec)


# Initialize if possible
initialize()
