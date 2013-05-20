from vistrails.core.modules.utils import make_modules_dict

from convert import _modules as convert_modules
from read import _modules as read_modules


_modules = make_modules_dict(convert_modules, read_modules)


###############################################################################
# DAT stuff
#

try:
    import dat.packages
except ImportError:
    pass # DAT is not available
else:
    from .dat_integration import *
