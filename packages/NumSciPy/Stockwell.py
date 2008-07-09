import core.modules
import core.modules.module_registry
from core.modules.vistrails_module import Module, ModuleError
from Matrix import *
from Array import *
from DSP import DSPModule
import scipy
import numpy
import smt
import st

class StockwellTransform(DSPModule, Module):
    def compute(self):
        signals = self.getInputFromPort("Signals").get_array()
        lof = self.getInputFromPort("Low Freq")
        hif = self.getInputFromPort("Hi Freq")
        if len(signals.shape) == 1:
            signals.shape = (1, signals.shape[0])

        outl = []
        for i in xrange(signals.shape[0]):
            sig_ar = signals[i]
            x = st.st(sig_ar, lof, hif)
            outl.append(x)

        out_ar = numpy.array(outl).squeeze()
        out = NDArray()
        out.set_array(out_ar)
        self.setResult("Output", out)
        
    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Signals", (NDArray, "Input Signals"))
        reg.add_input_port(cls, "Low Freq", (basic.Float, "Low Frequency"))
        reg.add_input_port(cls, "Hi Freq", (basic.Float, "High Frequency"))
        reg.add_output_port(cls, "Output", (NDArray, "Output TFR"))

class MultiTaperStockwellTransform(DSPModule, Module):
    def compute(self):
        signals = self.getInputFromPort("Signals").get_array()
        sr = self.getInputFromPort("Sample Rate")
        lof = self.getInputFromPort("Low Freq")
        hif = self.getInputFromPort("Hi Freq")

        if len(signals.shape) == 1:
            signals.shape = (1, signals.shape[0])

        if self.hasInputFromPort("Bandwidth"):
            self.k = smt.calcK(self.getInputFromPort("Bandwidth"),signals.shape[1], sr)
        else:
            self.k = self.getInputFromPort("K")

        outl = []
        for i in xrange(signals.shape[0]):
            sig_ar = signals[i]
            x = smt.mtst(self.k, smt.calc_tapers(self.k, signals.shape[1]), sig_ar, lof, hif)
            outl.append(x)

        out_ar = numpy.array(outl).squeeze()
        out = NDArray()
        out.set_array(out_ar)
        self.setResult("Output", out)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.my_namespace)
        reg.add_input_port(cls, "Signals", (NDArray, 'Input Signal Array'))
        reg.add_input_port(cls, "Sample Rate", (basic.Integer, 'Sample Rate'))
        reg.add_input_port(cls, "K", (basic.Float, "K"))
        reg.add_input_port(cls, "Bandwidth", (basic.Float, "Bandwidth"))
        reg.add_input_port(cls, "Low Freq", (basic.Float, "Low Frequency"))
        reg.add_input_port(cls, "Hi Freq", (basic.Float, "High Frequency"))
        reg.add_output_port(cls, "Output", (NDArray, "Output TFR"))

