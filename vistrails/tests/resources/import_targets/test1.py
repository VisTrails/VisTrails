# pragma: no testimport
try:
    import core.packagemanager
except ImportError:
    pass
else:
    raise AssertionError("Importing without prefix from outside the package "
                         "didn't raise ImportError")
