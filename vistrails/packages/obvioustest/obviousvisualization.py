import core.modules.module_registry
from core.modules.vistrails_module import Module, ModuleError
from obvious.data import Data
from obvious.viz import Visualization, VisualizationFactory
from java.lang import System

version = "0.0.1"
name = "ObviousVisualization"
identifier = "com.googlecode.obvious.viz.obviousvisualization"
class ObviousVisualization(Module):
    
    def compute(self):
        data = self.getInputConnector("data")
        params = self.getInputConnector("params")
        generatedparams = self.parseParams(params)
        factory = VisualizationFactory.getInstance()
        visualizationFactoryName = self.getInputConnector("visualizationFactoryName")
        System.setProperty("obvious.VisualizationFactory", visualizationFactoryName)
        visualization = factory.createVisualization(data, None, None, generatedparams)
        self.setResult("visualization", visualization)
        
    def parseParams(self, params):
        return None
    
def initialize(*args, **keywords):
    reg = core.modules.module_registry.registry
    reg.addModule(ObviousVisualization)
    reg.add_input_port(ObviousVisualization, "data",
                       (Data, "obvious network or data"))
    reg.add_input_port(ObviousVisualization, "visualizationFactoryName"
                       (core.modules.basic_modules.String, "name of the visualizationfactory"))
    reg.add_input_port(ObviousVisualization, "params"
                       (core.modules.basic_modules.String, "parameters for the visualization factory"))
    reg.add_output_port(ObviousVisualization, "visualization",
                        (Visualization, "an obvious visualization"))