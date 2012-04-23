# VisTrails module imports
from core.modules.vistrails_module import Module
from core.modules.module_registry import get_module_registry
from core.modules import basic_modules

# Java standard library
from javax.swing import JFrame

# Set up the path so we can load from the bundled JAR's
import sys
sys.path.append('packages/obvioustest/jar/obvious.jar')

sys.path.append('packages/obvioustest/jar/lucene-1.4.3.jar')
sys.path.append('packages/obvioustest/jar/prefuse.jar')
sys.path.append('packages/obvioustest/jar/obvious-prefuse.jar')

# Import the Module's of this package, to be registered by initialize()
from prefuse_grid_network import PrefuseGridNetwork
from prefuse_network_viz import PrefuseNetworkViz
from prefuse_view import PrefuseView


# We need to create module to represent our data types that are used by ports
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


def initialize(*args, **keywords):
    reg = get_module_registry()

    # Data types for ports
    reg.add_module(Data_ObviousNetwork)
    reg.add_module(Data_ObviousVisualization)
    reg.add_module(Data_JFrame)

    # PrefuseGridNetwork
    reg.add_module(PrefuseGridNetwork)
    basic_modules
    reg.add_input_port(
            PrefuseGridNetwork, 'm',
            (basic_modules.Integer, "width of the grid"))
    reg.add_input_port(
            PrefuseGridNetwork, 'n',
            (basic_modules.Integer, "height of the grid"))
    reg.add_output_port(
             PrefuseGridNetwork, 'network',
             (Data_ObviousNetwork, "an obvious network"))

    # PrefuseNetworkViz
    reg.add_module(PrefuseNetworkViz)
    reg.add_input_port(
            PrefuseNetworkViz, 'network',
            (Data_ObviousNetwork, "an obvious network"))
    reg.add_output_port(
             PrefuseNetworkViz, 'visualization',
             (Data_ObviousVisualization, "an obvious network visualization"))

    # PrefuseView
    reg.add_module(PrefuseView)
    reg.add_input_port(
             PrefuseView, 'visualization',
             (Data_ObviousVisualization, "an obvious prefuse visualization"))
    reg.add_output_port(
            PrefuseView, 'frame',
            (Data_JFrame, "a JFrame containing the view"))
