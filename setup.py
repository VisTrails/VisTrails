import os
from setuptools import setup
import sys


os.chdir(os.path.abspath(os.path.dirname(__file__)))


packages = []
for rootdir, dirs, files in os.walk('vistrails'):
    if '__init__.py' in files:
        packages.append(rootdir.replace('\\', '.').replace('/', '.'))


requirements = [
    # 'PyQt<5.0',
    'numpy',
    'scipy',
    'certifi',
    'backports.ssl_match_hostname',
    'file_archive>=0.6',
    'requests',
    'usagestats>=0.3',
    'xlrd',
    'xlwt',
]

if sys.version_info < (2, 7):
    requirements.append('argparse')


description = """
VisTrails is an open-source data analysis and visualization tool. It provides a comprehensive provenance infrastructure that maintains detailed history information about the steps followed and data derived in the course of an exploratory task: VisTrails maintains provenance of data products, of the computational processes that derive these products and their executions.

For more information, take a look at the `documentation <http://www.vistrails.org/index.php/Documentation>`_, the `users guide <http://www.vistrails.org/usersguide/v2.0/html/>`_, or our `publications <http://www.vistrails.org/index.php/Publications,_Tutorials_and_Presentations>`_.

Binary releases are available on our `download <http://www.vistrails.org/index.php/Downloads>`_ page. To report bugs, please use the github `issue tracker <https://github.com/VisTrails/VisTrails/issues>`_, after checking our `FAQ <http://www.vistrails.org/index.php/FAQ>`_ for known issues.

Homepage: http://www.vistrails.org

Who we are: http://www.vistrails.org/index.php/People
"""
setup(name='vistrails',
      version='2.2.4',
      packages=packages,
      include_package_data=True,
      entry_points={
        'console_scripts': [
          'vistrails = vistrails.run:main']},
      zip_safe=False,
      install_requires=requirements,
      description='Data analysis and visualization tool',
      author="New York University",
      author_email='vistrails-dev@vistrails.org',
      url='http://www.vistrails.org/',
      long_description=description,
      license='BSD',
      keywords=['vistrails', 'provenance', 'visualization', 'vtk', 'nyu',
                'matplotlib', ],
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 2 :: Only',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Visualization'])
