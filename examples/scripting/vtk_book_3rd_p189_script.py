import sys
sys.path.append('/Users/benbu/src/vistrails/vistrails/')

import vistrails.core.application
import vistrails.core.db.action
import vistrails.core.db.locator
import vistrails.core.modules.module_registry


#init vistrails
vt_app = vistrails.core.application.init()
controller = vt_app.get_controller()
registry = vistrails.core.modules.module_registry.get_module_registry()

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
    action = vistrails.core.db.action.create_action(item_ops + ops)
    controller.add_new_action(action)
    version = controller.perform_action(action)
    controller.change_selected_version(version)

def layoutAndAdd(module, connections):
    print 'adding %s' % module.name
    if not isinstance(connections, list):
        connections = [connections]
    ops = controller.layout_modules_ops(preserve_order=True, no_gaps=False,
                                        new_modules=[module],
                                        new_connections=connections)
    addToPipeline([module] + connections, ops)

#========================== package prefixes ===================================
httppkg = 'edu.utah.sci.vistrails.http'
vtkpkg = 'edu.utah.sci.vistrails.vtk'

#============================ start script =====================================

renderer = newModule(vtkpkg, 'vtkRenderer')
addToPipeline([renderer])

#this is missing when running from script??
# cell = newModule(vtkpkg, 'VTKCell')
# cell = newModule(vtkpkg, 'vtkCell')
# renderer_cell = newConnection(renderer, 'self',
#                               cell, 'AddRenderer')
# layoutAndAdd(cell, renderer_cell)

qcActor = newModule(vtkpkg, 'vtkActor')
qcActor_renderer = newConnection(qcActor, 'self',
                                 renderer, 'AddActor')
layoutAndAdd(qcActor, qcActor_renderer)

oActor = newModule(vtkpkg, 'vtkActor')
oActor_renderer = newConnection(oActor, 'self',
                                renderer, 'AddActor')
layoutAndAdd(oActor, oActor_renderer)

qcMapper = newModule(vtkpkg, 'vtkPolyDataMapper')
qcMapper_actor = newConnection(qcMapper, 'self',
                               qcActor, 'SetMapper')
layoutAndAdd(qcMapper, qcMapper_actor)

oProp = newModule(vtkpkg, 'vtkProperty')
setPortValue(oProp, 'SetColor', (0,0,0))
oProp_actor = newConnection(oProp, 'self',
                            oActor, 'SetProperty')
layoutAndAdd(oProp, oProp_actor)

oMapper = newModule(vtkpkg, 'vtkPolyDataMapper')
oMapper_actor = newConnection(oMapper, 'self',
                              oActor, 'SetMapper')
layoutAndAdd(oMapper, oMapper_actor)

qContour = newModule(vtkpkg, 'vtkContourFilter')
setPortValue(qContour, 'GenerateValues', (5,0,1.2))
qContour_mapper = newConnection(qContour, 'GetOutputPort0',
                                qcMapper, 'SetInputConnection0')
layoutAndAdd(qContour, qContour_mapper)

sample = newModule(vtkpkg, 'vtkSampleFunction')
setPortValue(sample, 'SetSampleDimensions', (50,50,50))
sample_qContour = newConnection(sample, 'GetOutputPort0',
                                qContour, 'SetInputConnection0')
layoutAndAdd(sample, sample_qContour)

outline = newModule(vtkpkg, 'vtkOutlineFilter')
outline_mapper = newConnection(outline, 'GetOutputPort0',
                               oMapper, 'SetInputConnection0')
sample_outline = newConnection(sample, 'GetOutputPort0',
                               outline, 'SetInputConnection0')
layoutAndAdd(outline, [outline_mapper, sample_outline])

quad = newModule(vtkpkg, 'vtkQuadric')
setPortValue(quad, 'SetCoefficients', (0.5,1,0.2,0,0.1,0,0,0.2,0,0))
quad_sample = newConnection(quad, 'self',
                            sample, 'SetImplicitFunction')
layoutAndAdd(quad, quad_sample)

#write to file
locator = vistrails.core.db.locator.FileLocator('p189_gaps_preserve_order.vt')
controller.write_vistrail(locator)
