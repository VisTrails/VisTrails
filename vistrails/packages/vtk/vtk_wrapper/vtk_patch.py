# This is a vistrails python wrapper patch file
# Each patch is a function with a body containing predefined placeholder variables
# The argument list declares which placeholder variables are used
# The patch is used by extracting the function body and replacing the variable placeholders

# This file contains the patches for vtk used by vistrails

# This builds the scalar tree
def guarded_SimpleScalarTree(self, original):
    original
    self.BuildTree()

# The behavior for vtkWriter subclasses is to call Write()
# If the user sets a name, we will create a file with that name
# If not, we will create a temporary file using _tempfile
def guarded_Writer(self, output):
    output = self.GetFileName()
    if not output:
        output = self._tempfile(suffix='.vtk')
        self.SetFileName(output)
    self.Write()

# Set magic tempfile
# This is used to create temporary files in the "guarded_" patches
def _set_tempfile(self, input):
    self._tempfile = input

# This checks for the presence of file in VTK readers
# Skips the check if it's a vtkImageReader or vtkPLOT3DReader, because
# it has other ways of specifying files, like SetFilePrefix for
# multiple files
def guarded_SetFileName(self, original):
    import os
    if not os.path.isfile(self.GetFileName()):
        raise Exception('File does not exist')
    original

def SetRenderWindow(self, input):
    import vtk
    window = vtk.vtkRenderWindow()
    w = 512
    h = 512
    window.OffScreenRenderingOn()
    window.SetSize(w, h)
    window.AddRenderer(input)
    window.Render()
    self.SetRenderWindow(window)

def TransferFunction(self, input):
    input.set_on_vtk_volume_property(self)

def PointData(self, input):
    self.GetPointData().ShallowCopy(input)

def CellData(self, input):
    self.GetCellData().ShallowCopy(input)

def PointIds(self, input):
    self.GetPointIds().SetNumberOfIds(input.GetNumberOfIds())
    for i in xrange(input.GetNumberOfIds()):
        self.GetPointIds().SetId(i, input.GetId(i))

def CopyImportVoidPointer(self, input):
    self.CopyImportVoidPointer(input, len(input))

def GetFirstBlock(self, output):
    output = self.GetOutput().GetBlock(0)

# Set magic callback
# Patches Update method with progress callback
def _set_callback(self, input):
    import types
    old_Update = self.Update
    def update_with_callback(self):
        is_aborted = [False]
        cbId = None
        def ProgressEvent(obj, event):
            try:
                input(obj.GetProgress())
            except Exception, e:
                if e.__name__ == 'AbortExecution':
                    obj.SetAbortExecute(True)
                    self.RemoveObserver(cbId)
                    is_aborted[0] = True
                else:
                    raise
        cbId = self.AddObserver('ProgressEvent', ProgressEvent)
        old_Update()
        self.RemoveObserver(cbId)
    self.Update = types.MethodType(update_with_callback, self)

# Non-C locales may have problem reading VTK files
# We temporary sets the locale to C in the VTK file readers
# Set initialize
def _initialize(self):
    import locale
    self._previous_locale = locale.setlocale(locale.LC_ALL)
    locale.setlocale(locale.LC_ALL, 'C')

# Set cleanup
def _cleanup(self):
    import locale
    locale.setlocale(locale.LC_ALL, self._previous_locale)

# from fix_classes
def SetLookupTable(self, original):
    self.UserControlledLookupTableOn()
    original

#basic:Color translation
def basic_Color_input(input, output):
    output = input.tuple

def basic_Color_output(input, output):
    from vistrails.core.utils import InstanceObject
    output = InstanceObject(tuple=input)

#basic:File translation
def basic_File_input(input, output):
    output = input.name

def basic_File_output(input, output):
    from vistrails.core.modules.basic_modules import PathObject
    output = PathObject(input)

# DEPRECATION
# Adds .vtkInstance attribute so that old script code still work
def vtkInstanceDeprecation(self):
    self.vtkInstance = self
