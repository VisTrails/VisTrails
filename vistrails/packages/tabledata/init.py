from vistrails.core.modules.utils import make_modules_dict

from .common import _modules as common_modules
from .convert import _modules as convert_modules
from .read import _modules as read_modules


_modules = make_modules_dict(common_modules, convert_modules, read_modules)
