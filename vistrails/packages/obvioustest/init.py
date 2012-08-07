# VisTrails module imports
from core.modules.module_registry import get_module_registry
from core.modules import basic_modules

# This represents a swing component, that may be added to a spreadsheet cell
from packages.javaspreadsheet.component import Component

# Import the Module's of this package, to be registered by initialize()
from prefuse_grid_network import PrefuseGridNetwork
from prefuse_network_viz import PrefuseNetworkViz
from prefuse_view import PrefuseView


# We need to create modules to represent our data types that are used by ports
import data


def initialize(*args, **keywords):
    reg = get_module_registry()

    # Data types for ports
    reg.add_module(data.ObviousNetwork, hide_descriptor=True)
    reg.add_module(data.ObviousVisualization, hide_descriptor=True)

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
             (data.ObviousNetwork, "an obvious network"))

    # PrefuseNetworkViz
    reg.add_module(PrefuseNetworkViz)
    reg.add_input_port(
            PrefuseNetworkViz, 'network',
            (data.ObviousNetwork, "an obvious network"))
    reg.add_output_port(
            PrefuseNetworkViz, 'visualization',
            (data.ObviousVisualization, "an obvious network visualization"))

    # PrefuseView
    reg.add_module(PrefuseView)
    reg.add_input_port(
            PrefuseView, 'visualization',
            (data.ObviousVisualization, "an obvious prefuse visualization"))
    reg.add_output_port(
            PrefuseView, 'view',
            (Component, "the view as a swing component"))
