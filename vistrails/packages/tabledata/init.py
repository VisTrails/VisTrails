from vistrails.core.modules.utils import make_modules_dict
from vistrails.core.packagemanager import get_package_manager

from .common import _modules as common_modules
from .convert import _modules as convert_modules
from .read import _modules as read_modules


_modules = [common_modules,
            convert_modules,
            read_modules]

if get_package_manager().has_package('org.vistrails.vistrails.spreadsheet'):
    from .viewer import _modules as viewer_modules
    _modules.append(viewer_modules)

_modules = make_modules_dict(*_modules)


###############################################################################
# DAT stuff
#

try:
    import dat.packages
except ImportError:
    pass # DAT is not available
else:
    from .dat_integration import *
