from vistrails.core.requirements import require_python_module

identifier = 'org.vistrails.vistrails.sklearn'
name = 'sklearn'
version = '0.15.2'


def package_requirements():
    require_python_module('sklearn', {
                          'pip': 'scikit-learn',
                          'linux-debian': 'python-sklearn',
                          'linux-ubuntu': 'python-sklearn'})
