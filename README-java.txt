This README file concerns the Java version of VisTrails.


# Introduction

Some work has been done on VisTrails to make it run on Jython 2.5.3. The
changes include:
  * Use of 2.5 syntax (for example in exception catching)
  * Various fixes for code relying on unsupported behaviors of CPython (ex:
    reference counting and immediate garbage collection)
  * Platform specific code (core.system)
  * Alternative GUI using Swing (javagui)


# Usage

Currently, because of some left-over dependencies in the core package and in
modules, you should use the stub PyQt4 package to avoid import errors.
You can download the stub from:
    http://dl.dropbox.com/u/13131521/jython-fake-site-packages.zip

In addition to Jython (which in turn requires a JVM), you will need the
following Java dependencies:
  * piccolo2d-core (used for the pipeline view)
    http://piccolo2d.org/download.html
    License: BSD Public License
  * VLDocking (used for the interface)
    http://code.google.com/p/vldocking/
    License: GNU Lesser GPL

Note that while this is not only necessary for the Java version of VisTrails,
you probably want to use the Java Spreadsheet package. Instructions on setting
up this module for both versions of VisTrails can be found in the
'README-javaspreadsheet.txt' file.


# Examples

## obvioustest (included)

The 'obvioustest' package wraps the Obvious visualization framework. This
example uses it to display a simple network visualization using Prefuse,
inside the Java spreadsheet.


## python_modules (included)

This is a very simple exampe that uses Python modules, and thus run the same
way on Python and Jython. The HTTP, ImageMagick and PythonCalc packages are
used.


## form_classification

This example was provided to me by Fernando Seabra Chirigati. It was
originally running using CLTools-wrapped java calls only.

It now uses the 'native' Weka package.

    http://dl.dropbox.com/u/13131521/20120627-weka-form_classification/l.html
