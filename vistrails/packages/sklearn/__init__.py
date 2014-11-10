identifier = 'org.vistrails.vistrails.sklearn'
name = 'sklearn'
version = '0.15.2'


def package_dependencies():
    import core.packagemanager
    manager = core.packagemanager.get_package_manager()
    dependencies = []
    if manager.has_package('org.vistrails.vistrails.spreadsheet'):
        dependencies.append('org.vistrails.vistrails.spreadsheet')
    return dependencies


def package_requirements():
    import core.requirements
    if not core.requirements.python_module_exists('sklearn'):
        raise core.requirements.MissingRequirement('sklearn')
    if not core.requirements.python_module_exists('numpy'):
        raise core.requirements.MissingRequirement('numpy')
    if not core.requirements.python_module_exists('scipy'):
        raise core.requirements.MissingRequirement('scipy')
