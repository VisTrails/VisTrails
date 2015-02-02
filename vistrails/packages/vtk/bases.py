from itertools import izip

from vistrails.core.modules.vistrails_module import Module, ModuleError
from vistrails.core.interpreter.base import AbortExecution
from vistrails.core import debug

class vtkObjectBase(Module):
    @staticmethod
    def get_set_method_info(port_name):
        return None

    @staticmethod
    def get_get_method_info(port_name):
        return None

    def call_set_method(self, vtk_obj, port_name, params):
        print "CALLING SET", port_name, params
        info = self.get_set_method_info(port_name)
        if info is None:
            raise ModuleError(self, 
                              'Internal error: cannot find '
                              'port "%s"' % port_name)
        method_name, shape, other_params, translator = info

        if isinstance(params, tuple):
            params = list(params)
        elif not isinstance(params, list):
            params = [params]
        if translator is not None:
            params = [translator(p) for p in params]
        method = getattr(vtk_obj, method_name)
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
        try:
            print "  calling", method_name, other_params + params
            method(*(other_params + params))
        except Exception, e:
            raise ModuleError(self,
                              "VTK Exception: %s" % debug.format_exception(e))

    def call_get_method(self, vtk_obj, port_name):
        print "CALLING GET", port_name
        info = self.get_get_method_info(port_name)
        if info is None:
            raise ModuleError(self, 
                              'Internal error: cannot find '
                              'port "%s"' % port_name)
        method_name, other_params = info
        method = getattr(vtk_obj, method_name)
        try:
            print "  calling", method_name, other_params
            output = method(*other_params)            
            self.set_output(port_name, output)
        except Exception, e:
            raise ModuleError(self,
                              "VTK Exception: %s" % debug.format_exception(e))

    def do_method_calls(self, vtk_obj):
        for value in sorted(self.is_method.itervalues()):
            (_, port_name) = value
            # FIXME can we make this an iteritems thing with itemgetter(1)?
            connector = self.is_method.inverse[value]
            self.call_set_method(vtk_obj, port_name, connector())

    def do_connected_calls(self, vtk_obj):
        for (port_name, connector_list) in self.inputPorts.iteritems():
            params = self.get_input_list(port_name)
            for p, connector in izip(params, connector_list):
                # Don't call method if method, this is separate
                if connector in self.is_method:
                    continue
                self.call_set_method(vtk_obj, port_name, params)

    def do_algorithm_update(self, vtk_obj):
        is_aborted = False
        cbId = None
        def ProgressEvent(obj, event):
            try:
                self.logging.update_progress(self, obj.GetProgress())
            except AbortExecution:
                obj.SetAbortExecute(True)
                vtk_obj.RemoveObserver(cbId)
                is_aborted = True
        cbId = vtk_obj.AddObserver('ProgressEvent', ProgressEvent)
        vtk_obj.Update()
        if not is_aborted:
            vtk_obj.RemoveObserver(cbId)
        
    def do_output_calls(self, vtk_obj):
        for port_name in self.outputPorts:
            if port_name == 'self':
                self.set_output('self', vtk_obj)
            else:
                self.call_get_method(vtk_obj, port_name)

    def do_compute(self, vtk_obj, is_algorithm):
        self.do_method_calls(vtk_obj)
        self.do_connected_calls(vtk_obj)
        if is_algorithm:
            self.do_algorithm_update(vtk_obj)
        elif hasattr(vtk_obj, 'Update'):
            vtk_obj.Update()
        self.do_output_calls(vtk_obj)

_modules = [vtkObjectBase,]
