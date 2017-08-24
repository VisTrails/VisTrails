from __future__ import division, print_function

from vistrails.core.modules.utils import make_modules_dict
from vistrails.core.packagemanager import get_package_manager
from vistrails.core.upgradeworkflow import UpgradeWorkflowHandler

# from .common import _modules as common_modules
# from .convert import _modules as convert_modules
from .operations import _modules as operation_modules
# from .read import _modules as read_modules
# from .write import _modules as write_modules


_modules = [
            # common_modules,
            # convert_modules,
            operation_modules,
            # read_modules,
            # write_modules
]

_modules = make_modules_dict(*_modules)

