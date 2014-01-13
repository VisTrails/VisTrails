from vistrails.core.modules.utils import make_modules_dict

from write_csv import _modules as csv_modules


_modules = make_modules_dict(numpy_modules, csv_modules, excel_modules,
                             namespace='write')
