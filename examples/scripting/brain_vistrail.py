import sys
sys.path.append('/Users/benbu/src/vistrails/vistrails/vistrails')

import core.application
import core.db.action
import core.db.locator
import core.modules.module_registry


#init vistrails
vt_app = core.application.init()
controller = vt_app.get_controller()
registry = core.modules.module_registry.get_module_registry()

#========================== convenience methods ================================
def newModule(package_name, module_name):
    descriptor = registry.get_descriptor_by_name(package_name, module_name)
    return controller.create_module_from_descriptor(descriptor)

def newConnection(source, source_port, target, target_port):
    c = controller.create_connection(source, source_port, target, target_port)
    return c

def setPortValue(module, port_name, value):
    function = controller.create_function(module, port_name, [str(value)])
    module.add_function(function)
    return

def addToPipeline(items, ops=[]):
    item_ops = [('add',item) for item in items]
    action = core.db.action.create_action(item_ops + ops)
    controller.add_new_action(action)
    version = controller.perform_action(action)
    controller.change_selected_version(version)

def layoutAndAdd(module, connection):
    ops = controller.layout_modules_ops(preserve_order=True,
                                        new_modules=[module],
                                        new_connections=[connection])
    addToPipeline([module, connection], ops)

#========================== package prefixes ===================================
httppkg = 'edu.utah.sci.vistrails.http'
vtkpkg = 'edu.utah.sci.vistrails.vtk'

#============================ start script =====================================

#start with http file module
httpFA = newModule(httppkg, 'HTTPFile')
url = 'http://www.vistrails.org/download/download.php?type=DATA&id=gktbhFA.vtk'
setPortValue(httpFA, 'url', url)

#add to pipeline
addToPipeline([httpFA])

#create data set reader module for the gktbhFA.vtk file
dataFA = newModule(vtkpkg, 'vtkDataSetReader')

#connect modules
http_dataFA = newConnection(httpFA, 'file', dataFA, 'SetFile')

#layout new modules before adding
layoutAndAdd(dataFA, http_dataFA)

#add contour filter
contour = newModule(vtkpkg, 'vtkContourFilter')
setPortValue(contour, 'SetValue', (0,0.6))
dataFA_contour = newConnection(dataFA, 'GetOutputPort0',
                               contour, 'SetInputConnection0')
layoutAndAdd(contour, dataFA_contour)

#add normals, stripper, and probe filter
normals = newModule(vtkpkg, 'vtkPolyDataNormals') #GetOutputPort0
setPortValue(normals, 'SetFeatureAngle', 60.0)
contour_normals = newConnection(contour, 'GetOutputPort0', 
                                normals, 'SetInputConnection0')
layoutAndAdd(normals, contour_normals)

stripper = newModule(vtkpkg, 'vtkStripper') #GetOutputPort0
normals_stripper = newConnection(normals, 'GetOutputPort0',
                                 stripper, 'SetInputConnection0')
layoutAndAdd(stripper, normals_stripper)

probe = newModule(vtkpkg, 'vtkProbeFilter') #same
stripper_probe = newConnection(stripper, 'GetOutputPort0',
                               probe, 'SetInputConnection0')
layoutAndAdd(probe, stripper_probe)

#build other branch in reverse
colors = newModule(vtkpkg, 'vtkImageMapToColors')
setPortValue(colors, 'SetOutputFormatToRGBA', True)
colors_probe = newConnection(colors, 'GetOutputPort0',
                             probe, 'SetInputConnection1')
layoutAndAdd(colors, colors_probe)

lookup = newModule(vtkpkg, 'vtkLookupTable')
setPortValue(lookup, 'SetHueRange', (0.0,0.8))
setPortValue(lookup, 'SetSaturationRange', (0.3,0.7))

#write to file
locator = core.db.locator.FileLocator('brain_script2.vt')
controller.write_vistrail(locator)
