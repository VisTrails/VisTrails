from setuptools import setup


description = """
VisTrails is an open-source data analysis and visualization tool. It provides a comprehensive provenance infrastructure that maintains detailed history information about the steps followed and data derived in the course of an exploratory task: VisTrails maintains provenance of data products, of the computational processes that derive these products and their executions.

For more information, take a look at the [documentation](http://www.vistrails.org/index.php/Documentation), the [users guide](http://www.vistrails.org/usersguide/v2.0/html/), or our [publications](http://www.vistrails.org/index.php/Publications,_Tutorials_and_Presentations).

Binary releases are available on our [download](http://www.vistrails.org/index.php/Downloads) page. To report bugs, please use the github [issue](https://github.com/VisTrails/VisTrails/issues) tracker, after checking our [FAQ](http://www.vistrails.org/index.php/FAQ) for known issues.

Homepage: <http://www.vistrails.org>

Who we are: <http://www.vistrails.org/index.php/People>
"""
setup(name='vistrails',
      version='2.1.2',
      packages=['vistrails'],
      entry_points={
        'console_scripts': [
          'vistrails = vistrails.run:main']},
      zip_safe=False,
      # FIXME: package_data?
      install_requires=[
        # 'PyQt<5.0',
        'ctypes',
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
