version = '0.0.1'
name = 'ParaView'
identifier = 'edu.utah.sci.eranders.ParaView'

from configuration import configuration

def package_dependencies():
    import core.packagemanager
    manager = core.packagemanager.get_package_manager()
    if manager.has_package('edu.utah.sci.vistrails.spreadsheet'):
        return ['edu.utah.sci.vistrails.spreadsheet']
    else:
        return []

def package_requirements():
    import core.requirements
    if not core.requirements.python_module_exists('vtk'):
        raise core.requirements.MissingRequirement('vtk')
    if not core.requirements.python_module_exists('PyQt4'):
        print 'PyQt4 is not available. There will be no interaction',
        print 'between VTK and the spreadsheet.'
    import vtk