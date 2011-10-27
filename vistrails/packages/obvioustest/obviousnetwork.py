import core.modules.module_registry
from core.modules.vistrails_module import Module, ModuleError
from obvious.data import Network, DataFactory
from obvious.impl import SchemaImpl
from obviousx.io.impl import GraphMLImport
from java.lang import System

version = "0.0.1"
name = "ObviousNetwork"
identifier = "com.googlecode.obvious.data.obviousnetwork"

class ObviousNetwork(Module):
    
    def compute(self):
        nodeSchema = SchemaImpl()
        edgeSchema = SchemaImpl()
        file = self.getInputConnector("file")
        dataFactoryName = self.getInputConnector("dataFactoryName")
        try:
            System.setProperty("obvious.DataFactory", dataFactoryName)
            factory = DataFactory.getInstance()
            network = factory.createGraph(nodeSchema, edgeSchema)
        except:
            raise ModuleError(self, "unrecognized datafactory " + dataFactoryName)
        graphmlimport = GraphMLImport(file, network, "source", "target", "nodeId")
        filledNetwork = graphmlimport.loadGraph()
        self.setResult("network", filledNetwork)
    
def initialize(*args, **keywords):
    reg = core.modules.module_registry.registry
    reg.addModule(ObviousNetwork)
    reg.add_input_port(ObviousNetwork, "file",
                       (core.modules.basic_modules.File, "a graphml file describing graph content"))
    reg.add_input_port(ObviousNetwork, "dataFactoryName"
                       (core.modules.basic_modules.String, "name of the datafactory"))
    reg.add_output_port(ObviousNetwork, "network",
                        (Network, "an Obvious network"))
