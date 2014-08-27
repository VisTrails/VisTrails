import os
from setuptools import setup


os.chdir(os.path.abspath(os.path.dirname(__file__)))


packages = []
for rootdir, dirs, files in os.walk('vistrails'):
    if '__init__.py' in files:
        packages.append(rootdir.replace('\\', '.').replace('/', '.'))


def list_files(d, root):
    files = []
    for e in os.listdir(os.path.join(root, d)):
        if os.path.isdir(os.path.join(root, d, e)):
            files.extend(list_files('%s/%s' % (d, e), root))
        elif not e.endswith('.pyc'):
            files.append('%s/%s' % (d, e))
    return files


package_data = {
    'vistrails.core.collection': ['schema.sql', 'test.db'],
    'vistrails.core': list_files('resources', 'vistrails/core'),
    'vistrails.db': ['specs/all.xml'],
    'vistrails.gui': list_files('resources/images', 'vistrails/gui') + ['resources/vistrails-mime.xml'],
    'vistrails.packages.analytics': ['*.vt'], # FIXME : what is this?
    'vistrails.packages.CLTools': ['icons/*.png', 'test_files/*'],
    'vistrails.packages.persistence': ['schema.sql'],
    'vistrails.packages.tabledata': ['test_files/*'],
    'vistrails.tests': list_files('resources', 'vistrails/tests'),
    }
for version in os.listdir('vistrails/db/versions'):
    if not version.startswith('v'):
        continue
    package_data['vistrails.db.versions.%s' % version] = [
        'schemas/sql/vistrails.sql',
        'schemas/sql/vistrails_drop.sql',
        'schemas/xml/log.xsd',
        'schemas/xml/vistrail.xsd',
        'schemas/xml/vtlink.xsd',
        'schemas/xml/workflow.xsd',
        'specs/all.xml',
]


description = """
VisTrails is an open-source data analysis and visualization tool. It provides a comprehensive provenance infrastructure that maintains detailed history information about the steps followed and data derived in the course of an exploratory task: VisTrails maintains provenance of data products, of the computational processes that derive these products and their executions.

For more information, take a look at the `documentation <http://www.vistrails.org/index.php/Documentation>`_, the `users guide <http://www.vistrails.org/usersguide/v2.0/html/>`_, or our `publications <http://www.vistrails.org/index.php/Publications,_Tutorials_and_Presentations>`_.

Binary releases are available on our `download <http://www.vistrails.org/index.php/Downloads>`_ page. To report bugs, please use the github `issue tracker <https://github.com/VisTrails/VisTrails/issues>`_, after checking our `FAQ <http://www.vistrails.org/index.php/FAQ>`_ for known issues.

Homepage: http://www.vistrails.org

Who we are: http://www.vistrails.org/index.php/People
"""
setup(name='vistrails',
      version='2.1.4',
      packages=packages,
      package_data=package_data,
      entry_points={
        'console_scripts': [
          'vistrails = vistrails.run:main']},
      zip_safe=False,
      install_requires=[
        # 'PyQt<5.0',
        'numpy',
        'scipy'],
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
