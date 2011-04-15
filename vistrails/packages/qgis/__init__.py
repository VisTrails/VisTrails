identifier = 'edu.utah.sci.vistrails.qgis'
version = '0.0.1'
name = "QGIS"

def package_dependencies():
    import core.packagemanager
    manager = core.packagemanager.get_package_manager()
    if manager.has_package('edu.utah.sci.vistrails.spreadsheet'):
        return ['edu.utah.sci.vistrails.spreadsheet']
    else:
        return []

