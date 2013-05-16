from vistrails.core.modules.utils import make_modules_dict

from read_numpy import _modules as numpy_modules
from read_csv import _modules as csv_modules


_modules = make_modules_dict(numpy_modules, csv_modules, namespace='read')
