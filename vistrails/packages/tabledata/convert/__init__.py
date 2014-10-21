from vistrails.core.modules.utils import make_modules_dict

from convert_dates import _modules as dates_modules


_modules = make_modules_dict(dates_modules, namespace='convert')
