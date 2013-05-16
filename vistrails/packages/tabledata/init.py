from read import _modules as read_modules


_modules = read_modules


###############################################################################
# DAT stuff
#

try:
    import dat.packages
except ImportError:
    pass # DAT is not available
else:
    from .dat_integration import *
