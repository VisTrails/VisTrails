from core.modules.vistrails_module import Module


# These modules exist as they represent datatypes referenced by ports
# However they should never be placed on a pipeline (and thus shouldn't be
# available in the module panel) as they don't do anything

# obvious.viz.Visualization
class ObviousVisualization(Module):
    pass
# obvious.data.Network
class ObviousNetwork(Module):
    pass
