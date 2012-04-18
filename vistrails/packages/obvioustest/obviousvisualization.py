from core.modules.vistrails_module import Module
# from obvious.data import Data
# from obvious.viz import VisualizationFactory
# from java.lang import System

class ObviousVisualization(Module):
    def compute(self):
        # data = self.getInputConnector('data')
        # params = self.getInputConnector('params')
        # generatedparams = self.parseParams(params)
        # visualizationFactoryName = self.getInputConnector('visualizationFactoryName')
        # System.setProperty('obvious.VisualizationFactory', visualizationFactoryName)
        # factory = VisualizationFactory.getInstance()
        # visualization = factory.createVisualization(data, None, None, generatedparams)
        # self.setResult('visualization', visualization)
        self.setResult('visualization', '!!visualization!!')

    def parseParams(self, params):
        return None
