import warnings
class VTKInstanceWrapper(object):
    def __init__(self, instance):
        self.vtkInstance = instance

    # For future use: warns when .vtkInstance is used
    # If this is enabled, replace mentions of self.vtkInstance with
    # self.__dict__['vtkInstance'] in this class
    #@property
    #def vtkInstance(self):
    #    warnings.warn(
    #            "Dereferencing VTK object with '.vtkInstance' is not needed "
    #            "anymore, call method directly",
    #            DeprecationWarning,
    #            stacklevel=2)
    #    return self.__dict__['vtkInstance']

    def __getattr__(self, name):
        return getattr(self.vtkInstance, name)
