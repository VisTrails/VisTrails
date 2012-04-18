from core.modules.vistrails_module import Module, ModuleError
# from obvious.data import DataFactory
# from obvious.impl import SchemaImpl
# from obviousx.io.impl import GraphMLImport
# from java.lang import System

class ObviousNetwork(Module):
    def compute(self):
        # nodeSchema = SchemaImpl()
        # edgeSchema = SchemaImpl()
        # file = self.getInputConnector('file')
        # dataFactoryName = self.getInputConnector('dataFactoryName')
        # try:
        #     System.setProperty('obvious.DataFactory', dataFactoryName)
        #     factory = DataFactory.getInstance()
        #     network = factory.createGraph(nodeSchema, edgeSchema)
        # except:
        #     raise ModuleError(self, "unrecognized datafactory %s" % dataFactoryName)
        # graphmlimport = GraphMLImport(file, network, 'source', 'target', 'nodeId')
        # filledNetwork = graphmlimport.loadGraph()
        # self.setResult('network', filledNetwork)
        self.setResult('network', '!!network!!')
