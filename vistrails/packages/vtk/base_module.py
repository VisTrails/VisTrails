###############################################################################
##
## Copyright (C) 2011-2014, NYU-Poly.
## Copyright (C) 2006-2011, University of Utah. 
## All rights reserved.
## Contact: contact@vistrails.org
##
## This file is part of VisTrails.
##
## "Redistribution and use in source and binary forms, with or without 
## modification, are permitted provided that the following conditions are met:
##
##  - Redistributions of source code must retain the above copyright notice, 
##    this list of conditions and the following disclaimer.
##  - Redistributions in binary form must reproduce the above copyright 
##    notice, this list of conditions and the following disclaimer in the 
##    documentation and/or other materials provided with the distribution.
##  - Neither the name of the University of Utah nor the names of its 
##    contributors may be used to endorse or promote products derived from 
##    this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
## AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
## THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR 
## PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR 
## CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; 
## OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
## WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR 
## OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF 
## ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
###############################################################################
################################################################################
# This describes basic modules used by other VTK module
################################################################################
from itertools import izip
import vtk

from vistrails.core import debug
from vistrails.core.interpreter.base import AbortExecution
from vistrails.core.configuration import ConfigField
from vistrails.core.modules.config import ModuleSettings
from vistrails.core.modules.module_registry import registry
from vistrails.core.modules.output_modules import OutputModule, ImageFileMode, \
    ImageFileModeConfig
from vistrails.core.modules.vistrails_module import Module, ModuleError
import vistrails.core.system
from .identifiers import identifier as vtk_pkg_identifier
from .wrapper import VTKInstanceWrapper

################################################################################

class vtkBaseModule(Module):
    """
    vtkBaseModule is the base class for all VTK modules in VisTrails, it acts
    as a wrapper to direct all input/output ports to appropriate VTK function
    calls
    
    """

    def __init__(self):
        """ vtkBaseModule() -> vtkBaseModule
        Instantiate an empty VTK Module with real VTK instance
        
        """
        Module.__init__(self)
        self.vtkInstance = None

    def is_cacheable(self):
        # VTK objects are by default cacheable only if they're subclasses
        # of vtkAlgorithm
        return (issubclass(self.vtkClass, vtk.vtkAlgorithm)
                and (not issubclass(self.vtkClass, vtk.vtkAbstractMapper)))

    def call_input_function(self, function, params):
        """self.call_input_function(function, params) -> None
        Calls the input function on the vtkInstance, or a special
        input function if one exists in the class."""
        if hasattr(self, '_special_input_function_' + function):
            attr = getattr(self, '_special_input_function_' + function)
        else:
            try:
                attr = getattr(self.vtkInstance, function)
            except AttributeError:
                # Compensates for overload by exploiting the fact that
                # no VTK method has underscores.
                f = function.find('_')
                if f != -1:
                    function = function[:f]
                attr = getattr(self.vtkInstance, function)

        from init import get_method_signature, prune_signatures

        doc = ''
        try:
            # doc = self.provide_output_port_documentation(function)
            doc = self.get_doc(function)
        except Exception:
            doc = ''

        setterSig = []
        if doc != '': setterSig = get_method_signature(None, doc, function)

        if len(setterSig) > 1:
            prune_signatures(self, function, setterSig)

        pp = []
        for j in xrange(len(setterSig)):
            setter = list(setterSig[j][1]) if setterSig[j][1] != None else None
            aux = []
            if setter != None and len(setter) == len(params) and pp == []:
                for i in xrange(len(setter)):
                    if setter[i].find('[') != -1:
                        del aux[:]
                        aux.append(params[i])
                    elif setter[i].find(']') != -1:
                        aux.append(params[i])
                        pp.append(aux)
                    else:
                        if len(aux) > 0:
                            aux.append(params[i])
                        else:
                            pp.append(params[i])
        if pp != []:
            params = pp 
            attr(*params)
        else: 
            attr(*params)
        # print "Called ",attr,function,params

    @classmethod
    def get_doc(cls, port_name):
        f = port_name.find('_')
        if f != -1:
            name = port_name[:f]
        else:
            name = port_name
        return getattr(cls.vtkClass, name).__doc__

    # @classmethod
    # def provide_input_port_documentation(cls, port_name):
    #     return cls.get_doc(port_name)

    # @classmethod
    # def provide_output_port_documentation(cls, port_name):
    #     return cls.get_doc(port_name)

    def compute(self):
        """ compute() -> None
        Actually perform real VTK task by directing all input/output ports
        to VTK function calls
        
        """

        def call_it(function, p):
            # Translate between VisTrails objects and VTK objects
            if p is None:
                # None indicates a call with no parameters
                params = []
            elif isinstance(p, tuple):
                # A tuple indicates a call with many parameters
                params = list(p)
            else:
                # Otherwise, it's a single parameter
                params = [p]

            # Unwraps VTK objects
            for i in xrange(len(params)):
                if hasattr(params[i], 'vtkInstance'):
                    params[i] = params[i].vtkInstance
            try:
                self.call_input_function(function, params)
            except Exception, e:
                raise ModuleError(
                        self,
                        "VTK Exception: %s" % debug.format_exception(e))

        # Always re-create vtkInstance module, no caching here
        if self.vtkInstance:
            del self.vtkInstance
        self.vtkInstance = self.vtkClass()

        # We need to call method ports before anything else, and in
        # the right order.

        # FIXME: This does not belong here, it belongs in the main class
        # No time for that now
        methods = self.is_method.values()
        methods.sort()
        for value in methods:
            (_, port) = value
            conn = self.is_method.inverse[value]
            p = conn()
            call_it(port, p)

        # Make sure all input ports are called correctly
        for (function, connector_list) in self.inputPorts.iteritems():
            paramList = self.force_get_input_list(function)
            if function[:18]=='SetInputConnection':
                paramList = zip([int(function[18:])]*len(paramList),
                                 paramList)
                function = 'SetInputConnection'
            if function=='AddInputConnection':
                desc = registry.get_descriptor_by_name(
                    vtk_pkg_identifier,
                    'vtkAlgorithmOutput')
                for i in xrange(len(paramList)):
                    paramList[i] = (0, paramList[i])
            for p,connector in izip(paramList, connector_list):
                # Don't call method
                if connector in self.is_method:
                    continue
                call_it(function, p)
                
        #In the case of a vtkRenderer, 
        # we need to call the methods after the
        #input ports are set.
        if isinstance(self.vtkInstance, vtk.vtkRenderer):
            for value in methods:
                (_, port) = value
                conn = self.is_method.inverse[value]
                p = conn()
                call_it(port, p)

        # Call update if appropriate
        if hasattr(self.vtkInstance, 'Update'):
            is_aborted = False
            isAlgorithm = issubclass(self.vtkClass, vtk.vtkAlgorithm)
            cbId = None
            if isAlgorithm:
                def ProgressEvent(obj, event):
                    try:
                        self.logging.update_progress(self, obj.GetProgress())
                    except AbortExecution:
                        obj.SetAbortExecute(True)
                        self.vtkInstance.RemoveObserver(cbId)
                        is_aborted = True
                cbId = self.vtkInstance.AddObserver('ProgressEvent', ProgressEvent)
            self.vtkInstance.Update()
            if isAlgorithm and not is_aborted:
                self.vtkInstance.RemoveObserver(cbId)

        mid = self.moduleInfo['moduleId']

        # Then update the output ports also with appropriate function calls
        for function in self.outputPorts.keys():
            if function[:13]=='GetOutputPort':
                i = int(function[13:])
                vtkOutput = self.vtkInstance.GetOutputPort(i)
                self.set_output(function, VTKInstanceWrapper(vtkOutput, mid))
            elif hasattr(self.vtkInstance, function):
                retValues = getattr(self.vtkInstance, function)()
                if issubclass(retValues.__class__, vtk.vtkObject):
                    self.set_output(function, VTKInstanceWrapper(retValues, mid))
                elif isinstance(retValues, (tuple, list)):
                    result = list(retValues)
                    for i in xrange(len(result)):
                        if issubclass(result[i].__class__, vtk.vtkObject):
                            result[i] = VTKInstanceWrapper(result[i], mid)
                    self.set_output(function, type(retValues)(result))
                else:
                    self.set_output(function, retValues)
        self.set_output('Instance', VTKInstanceWrapper(self.vtkInstance, mid))

class vtkRendererToFile(ImageFileMode):
    config_cls = ImageFileModeConfig
    formats = ['png', 'jpg', 'tif', 'pnm']

    @classmethod
    def can_compute(cls):
        return True

    def compute_output(self, output_module, configuration):
        format_map = {'png': vtk.vtkPNGWriter,
                      'jpg': vtk.vtkJPEGWriter,
                      'tif': vtk.vtkTIFFWriter,
                      'pnm': vtk.vtkPNMWriter}
        r = output_module.get_input("value").vtkInstance
        w = configuration["width"]
        h = configuration["height"]
        img_format = self.get_format(configuration)
        if img_format not in format_map:
            raise ModuleError(output_module, 
                              'Cannot output in format "%s"' % img_format)
        fname = self.get_filename(configuration, suffix='.%s' % img_format)

        window = vtk.vtkRenderWindow()
        window.OffScreenRenderingOn()
        window.SetSize(w, h)

        # FIXME think this may be fixed in VTK6 so we don't have this
        # dependency...
        widget = None
        if vistrails.core.system.systemType=='Darwin':
            from PyQt4 import QtCore, QtGui
            widget = QtGui.QWidget(None, QtCore.Qt.FramelessWindowHint)
            widget.resize(w, h)
            widget.show()
            window.SetWindowInfo(str(int(widget.winId())))

        window.AddRenderer(r)
        window.Render()
        win2image = vtk.vtkWindowToImageFilter()
        win2image.SetInput(window)
        win2image.Update()
        writer = format_map[img_format]()
        writer.SetInput(win2image.GetOutput())
        writer.SetFileName(fname)
        writer.Write()
        window.Finalize()
        if widget!=None:
            widget.close()

class vtkRendererOutput(OutputModule):
    # DAK: no render view here, use a separate module for this...
    _settings = ModuleSettings(configure_widget="vistrails.gui.modules.output_configuration:OutputModuleConfigurationWidget")
    _input_ports = [('value', 'vtkRenderer')]
                    # DK: these ports can be enabled, I think, just
                    # have to be laoded without the spreadsheet being
                    # enabled
                    # ('interactionHandler', 'vtkInteractionHandler'), 
                    # ('interactorStyle', 'vtkInteractorStyle'), 
                    # ('picker', 'vtkAbstractPicker')]
    _output_modes = [vtkRendererToFile]
