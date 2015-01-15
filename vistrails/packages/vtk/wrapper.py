#import warnings


from __future__ import division

class VTKInstanceWrapper(object):
    def __init__(self, instance, module_id):
        self.vtkInstance = instance
        self.vt_module_id = module_id

    # For future use: warns when .vtkInstance is used
    #@property
    #def vtkInstance(self):
    #    warnings.warn(
    #            "Dereferencing VTK object with '.vtkInstance' is not needed "
    #            "anymore, call method directly",
    #            DeprecationWarning,
    #            stacklevel=2)
    #    return self.__vtkInstance

    def __getattr__(self, name):
        return getattr(self.vtkInstance, name)
