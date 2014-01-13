from vistrails.core.modules.utils import make_modules_dict

try:
    # write_numpy requires numpy
    import numpy
except ImportError:
    numpy_modules = []
else:
    from write_numpy import _modules as numpy_modules

from write_csv import _modules as csv_modules
from write_excel import _modules as excel_modules


_modules = make_modules_dict(numpy_modules, csv_modules, excel_modules,
                             namespace='write')
