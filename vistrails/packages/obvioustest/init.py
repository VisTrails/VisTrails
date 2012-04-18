# VisTrails module imports
from core.modules.vistrails_module import Module
from core.modules.module_registry import get_module_registry
from core.modules import basic_modules

# Java standard library
from javax.swing import JFrame, JTable

# Set up the path so we can load from the bundled JAR's
import sys
sys.path.append('packages/obvioustest/jar/obvious-1.0.jar')
sys.path.append('packages/obvioustest/jar/obvious-test.jar')
sys.path.append('packages/obvioustest/jar/obviousx.jar')

# Import Obvious stuff from the JAR's
import obvious.data
import obvious.viz

# Import the Module's of this package, to be registered by initialize()
from obviousvisualization import ObviousVisualization
from obviousview import ObviousView
from obvioustable import ObviousTable
from obviousnetwork import ObviousNetwork


# We need to create module to represent our data types that are used by ports
# obvious.data.Data
class Data_ObviousData(Module):
    def compute(self):
        pass
# obvious.viz.Visualization
class Data_ObviousVisualization(Module):
    def compute(self):
        pass
# obvious.data.Network
class Data_ObviousNetwork(Module):
    def compute(self):
        pass
# JFrame
class Data_JFrame(Module):
    def compute(self):
        pass
# JTable
class Data_JTable(Module):
    def compute(self):
        pass


def initialize(*args, **keywords):
    reg = get_module_registry()

    # Data types for ports
    reg.add_module(Data_ObviousData)
    reg.add_module(Data_ObviousVisualization)
    reg.add_module(Data_ObviousNetwork)
    reg.add_module(Data_JFrame)
    reg.add_module(Data_JTable)

    # ObviousVisualization
    reg.add_module(ObviousVisualization)
    reg.add_input_port(
            ObviousVisualization, 'data',
            (Data_ObviousData, "obvious network or data"))
    reg.add_input_port(
            ObviousVisualization, 'visualizationFactoryName',
            (basic_modules.String, "obvious network or data"))
    reg.add_input_port(
            ObviousVisualization, 'params',
            (basic_modules.String, "parameters for the visualization factory"))
    reg.add_output_port(
            ObviousVisualization, 'visualization',
            (Data_ObviousVisualization, "an obvious visualization"))

    # ObviousView
    reg.add_module(ObviousView)
    reg.add_input_port(
            ObviousView, 'visualization',
            (Data_ObviousVisualization, "obvious visualization"))
    reg.add_input_port(
            ObviousView, 'viewFactoryName',
            (basic_modules.String, "name of the viewfactory"))
    reg.add_output_port(
            ObviousView, 'jframe',
            (Data_JFrame, "Resulting JFrame"))

    # ObviousTable
    reg.add_module(ObviousTable)
    reg.add_input_port(
            ObviousTable, 'file',
            (basic_modules.File, "a csv file describing table content"))
    reg.add_input_port(
            ObviousTable, 'dataFactoryName',
            (basic_modules.String, "name of the datafactory"))
    reg.add_output_port(
            ObviousTable, 'table',
            (Data_JTable, "the resulting JTable"))
    reg.add_output_port(
            ObviousTable, 'frame',
            (Data_JFrame, "a Java swing JFrame containing the table"))

    # ObviousNetwork
    reg.add_module(ObviousNetwork)
    reg.add_input_port(
            ObviousNetwork, 'file',
            (basic_modules.File, "a graphml file describing graph content"))
    reg.add_input_port(
            ObviousNetwork, 'dataFactoryName',
            (basic_modules.String, "name of the datafactory"))
    reg.add_output_port(
            ObviousNetwork, 'network',
            (Data_ObviousNetwork, "an Obvious network"))
