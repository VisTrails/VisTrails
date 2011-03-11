.. _chap-packages:

**************************
Writing VisTrails Packages
**************************

Introduction
============

.. highlight:: python
   :linenothreshold: 5

.. index::
   pair: modules; writing new
   single: packages

.. role:: red

|vistrails| provides a
plugin infrastructure to integrate user-defined functions and
libraries. Specifically, users can incorporate their own visualization
and simulation code into pipelines by defining custom modules. These
modules are bundled in what we call *packages*. A \vistrails
package is simply a collection of Python classes stored in one or more
files, respecting some conventions that will be described shortly.
Each of these classes will represent a new module. In this chapter, we
will build progressively more complicated modules.
Note that even though each section introduces a specific large
feature of the |vistrails| package mechanism, new small features are
highlighted and explained as we go along. Because of this, we
recommend at least skimming through the entire chapter at least once.

Who Should Read This Chapter?
=============================

This chapter is written for developers who wish to extend |vistrails| with customized modules, tailored for their specific needs. It is assumed that you have experience writing code in the Python programming language. Teaching the syntax of Python is beyond the scope of this manual; for experienced programmers who would like a compact introduction to Python, we recommend the book *Python in a Nutshell* by Alex Martelli (published by O'Reilly).

However, if you do not yet know Python but are familiar with another object-oriented language such as Java or C#, you should be able to get the gist of these examples from looking at the code and by reading our line-by-line commentaries.

.. _sec-packages-simple_example:

A Simple Example
================

Let us start with a minimal complete example of a very simple
calculator:

.. include:: pythoncalc.rst

To try this out in VisTrails, save the file above in the ``.vistrails/userpackages`` subdirectory of your home directory, with the filename ``pythoncalc.py``. Then, click on the ``Edit`` menu
and select the ``Preferences`` option. (On Mac~OS~X, this option is under the ``|vistrails|`` menu.) A dialog similar to what is shown
in Figure :ref:`fig-packages-enablepackage` should appear. Select the
``pythonCalc`` package, then click on
``Enable``. This should move the package to the
``Enabled packages`` list. Close the dialog. The package and
module should now be visible in the VisTrails builder.

.. _fig-packages-enablepackage:

.. figure:: figures/packages/enable_package.png
   :align: center
   :width: 100%

   All available packages can be enabled and disabled with the VisTrails preferences dialog.

.. _fig-packages-pythoncalcworkflow:

.. figure:: figures/packages/pythoncalc_workflow.png
   :align: center
   :width: 100%

   A simple workflow that uses ``PythonCalc``, a user-defined module.

Now create a workflow similar to what is shown in Figure
:ref:`fig-packages-pythoncalcworkflow`. When executed, this workflow
will print the following on your terminal:

``7.0``

Let's now examine how this works. The first
two lines simply import required components. The next three lines
give |vistrails| meta-information about the
package. ``version`` is simply information about the package
version. This might be tied to the underlying library or not. The only
recommended guideline is that compatibility is not broken across minor
releases, but this is not enforced in any way. ``name`` is a
human-readable name for the package. 

.. %\paragraph*{Choosing a good identifier}

The most important piece of metadata,
however, is the package *identifier*, stored in the variable called
``identifier``. This is a string that must be globally unique
across all packages, not only in your system, but in any possible
system. We recommend using an identifier similar to Java's package
identifiers. These look essentially like regular DNS names, but the
word order is reversed. This makes sorting on the strings a lot more
meaningful. You should generally go for
``institution.project.packagename`` for a package related to a
certain project from some institution, and
``institution.creatorname`` for a personally developed
package. If you are wrapping third-party functionality, *do not*
use their institution's DNS, use your own. The rationale for this is
that the third party itself might decide to create their own \vistrails
package, and you do not want to introduce conflicts.

Line :ref:`package-defineclass` is where we actually start defining a new module.
Every |vistrails| module corresponds
to a Python class that ultimately derives from the ``Module`` class, which is defined in ``core.modules.vistrails_module``. Each module must implement a ``compute`` method that takes no extra parameters, such as on Line :ref:`package-compute`. This method
represents the actual computation that happens in a module.
This computation typically involves getting the necessary input and
generating the output. We will now see how that works.

Line :ref:`package-getinputfromport` shows how to extract input from a
port. Specifically, we're getting the values passed to input ports
``value1`` and ``value2``. We then perform some
operation with these values, and need to report the output on an
output port, so that it is available for downstream modules. This is
done on Line :ref:`package-setresult`, where the result is set to port
``value``.

.. index:: 
   pair: modules; ``ModuleError``

Let us now look more carefully at the remainder of the class definition. Notice
that developers are allowed to define extra helper methods, for example the ``op`` method on Line
:ref:`package-extramethods`. These helper methods can naturally use the ports
API. The other important feature of the ``op`` method is
*error checking*. ``PythonCalc`` requires a string that
represents the operation to be performed with the two numbers. If the
string is invalid, it signals an error by simply raising a Python
exception, ``ModuleError``, that is provided in
``core.modules.vistrails_module``. This exception expects two
parameters: the module that generated the exception (typically
``self``) and a string describing the error. In the Pipeline view, this error message is displayed in the tooltip that appears when the user "mouses over" the ``PythonCalc`` module icon.

.. index::
   pair: packages; ``initialize``
   pair: Module registry; ``addModule``
   pair: Module registry; ``add_input_port``
   pair: Module registry; ``add_output_port``

That is all that it takes in terms of module behavior. The rest of the
code is meant to interact with |vistrails|, and let the system know
about the modules and ports being exposed. To do that, you must
provide a function called ``initialize`` in the main body of the
package file (the function starting on Line
:ref:`package-initialize`). The first thing is usually to register the
module itself, such as on Line :ref:`package-addmodule`. Then, we need
to tell |vistrails| about the input and output ports we want to
expose.  Input ports are set with the ``add_input_port`` method
in the registry, and output ports with ``add_output_port``. These calls take three parameters. The
first parameter is the module you're adding a new port to. The second
one is simply the name of the port, and the third one is a description
of the parameter. In most cases, this is just a pair, where the
first element is a |vistrails| module representing the module type
being passed, and the second element is a string describing it.
Notice that the
types being used are |vistrails| modules (Line :ref:`package-float`),
and not Python types.

.. %Later, we will see how to pass more complicated data types.

That is it --- you have successfully created a new package and
module. From now on, we will look at more complicated examples, and
more advanced features of the package mechanism.

.. _sec-wrapping_cmdline_tools:

Wrapping Command-line tools
===========================

.. index::
   pair: packages; wrapping command-line tools

Many existing programs are readily available through a command-line
interface. Also, many existing workflows are first implemented
through scripts, which work primarily with command-line
tools. This section describes how to wrap command-line applications so
they can be used with VisTrails. We will use as a running example the
``afront`` package, which wraps ``afront``, a command-line program
for generating 3D triangle meshes.  [#]_We will wrap the basic
functionality in three different modules: ``Afront``, ``AfrontIso``, and ``MeshQualityHistogram``.

Each of these modules will be implemented by a Python
class, and they will all invoke the ``afront`` binary.
``Afront`` is the base execution module, and
``AfrontIso`` requires extra parameters on top of the original
ones. Because of this, we will implement ``AfrontIso`` as a
subclass of ``Afront``. ``MeshQualityHistogram``,
however, requires entirely different parameters, and so will not be
a subclass of ``Afront``. A first attempt at writing this package might look something like this:

.. code-block::python

   from core.modules.vistrails_module import Module
   ... # other import statements

   name = "Afront"
   version = "0.1.0"
   identifier = "edu.utah.sci.vistrails.afront"

   class Afront(Module):
       def compute(self):
           ... # invokes afront

   class AfrontIso(Afront):
       def compute(self):
           ... # invokes afront with additional parameters

   class MeshQualityHistogram(Module):
       def compute(self):
           ... # invokes afront with completely different parameters

   def initialize():
       ...

Class Mixins
^^^^^^^^^^^^

While this approach is a good start, it does require significant duplication of effort. Each module must contain code to invoke the ``afront`` binary and pass it some parameters. Since this functionality is required by all three modules, we would like to put this code in a separate class called, say, ``AfrontRun``, and let each of our modules inherit from it. ``AfrontRun`` itself is not a module, and thus does not extend the ``Module`` class. So our three modules will inherit from *both* ``AfrontRun`` *and* ``Module``. Helper classes such as this are often referred to as *mixin classes*.[#]_

.. %It should be clear that all three modules share some functionality (invoking ``afront``), but not all. We would like to avoid duplicate code, but there is not a single class where we can implement the base code. The solution is to create a *mixin class*, where we implement the necessary functionality, and then inherit from both classes. In the following snippets, we will highlight the changes in the code.

.. code-block::python

   from core.modules.vistrails_module import Module, ModuleError
   :red:`from core.system import list2cmdline`
   :red:`import os`

   :red:`class AfrontRun(object):`
   :red:`    _debug = False`
   :red:`    def run(self, args):`
   :red:`        cmd = ['afront', '-nogui'] + args`
   :red:`        cmdline = list2cmdline(cmd)`
   :red:`        if self._debug:`
   :red:`            print cmdline`
   :red:`        result = os.system(cmdline)`
   :red:`        if result != 0:`
   :red:`            raise ModuleError(self, "Execution failed")`

   class Afront(Module:red:`, AfrontRun`):
       ...

   class MeshQualityHistogram(Module:red:`, AfrontRun`):
       ...

Now every module in the ``afront`` package has access to
``run()``.  The other new feature in this snippet is
``list2cmdline``, which turns a list of strings into a command
line. It does this in a careful way (protecting arguments with spaces,
for example). Notice that we use a call to a shell
(``os.system()``) to invoke ``afront``. This is
frequently the easiest way to get third-party functionality into |vistrails|.

.. _sec-pkg_config:

Package Configuration
^^^^^^^^^^^^^^^^^^^^^

.. index::
   pair: packages; congiguration

There are two obvious shortcomings in the way ``run()`` is
implemented. First, the code assumes ``afront`` is available
in the system path, which might not be true in practice. Second, the
debugging variable is inaccessible from the GUI, where it could be
very useful. |vistrails| provides a way to configure a package
through the |vistrails| ``Preferences`` dialog. It is very simple to provide your own configuration;
just add a ``configuration`` attribute to your package, as follows:

.. code-block::python

   :red:`from core.configuration import ConfigurationObject`
   from core.modules.vistrails_module import Module, ModuleError
   from core.system import list2cmdline
   import os

   .. _ref-packages=configconstructor1:
   :red:`configuration = ConfigurationObject(path=(None, str),
   .. _ref-packages-configconstructor2:
   :red:`                                    debug=False)`

   class AfrontRun(object):

       def run(self, args):
   .. _ref-packages-configurationcheck:
   :red:`        if configuration.check('path'): # there's a set directory`
   :red:`            afront_cmd = configuration.path + '/afront'`
   :red:`        else: # Assume afront is on path`
   :red:`            afront_cmd = 'afront'`
           cmd = [:red:`afront_cmd`, '-nogui'] + args
           cmdline = list2cmdline(cmd)
   .. _ref-packages-configurationdebug:
   :red:`        if configuration.debug: 
               print cmdline
           ...
   ...

.. index:: ``ConfigurationObject``

Let us first look at how to specify configuration options. Named
arguments passed to the ``ConfigurationObject`` constructor (Lines~:ref:`ref-packages-configconstructor1` and~:ref:`ref-packages-configconstructor2`) become
attributes in the object. If the attribute has a default value, simply
pass it to the constructor. If the attribute should be unset by default, pass the constructor a pair whose first element is ``None`` and second element is the *type* of the expected
parameter. Currently, the valid types are ``bool``,
``int``, ``float`` and ``str``.

To use the configuration object in your code, you can simply access
the attributes (as on line
:ref:`ref-packages-configurationdebug`). This is fine when there is a
default value set for the attribute. In the case of ``path``,
however, the absence of a value is encoded by a tuple
``(None, str)``, so using it directly is inconvenient. That is
where the ``check()`` method comes in (line
:ref:`ref-packages-configurationcheck`). It returns ``False``
if there is no set value, and returns the value otherwise.

Perhaps the biggest advantage of using a configuration object is that the values can
be changed through a GUI, and they are persistent across VisTrails
sessions. To configure a package, open the ``Preferences``
menu (``|vistrails|``:math:`\rightarrow`
``Preferences`` on Mac~OS~X, or ``Edit`` :math:`\rightarrow`
``Preferences`` on other platforms). Then, select the package you want to
configure by clicking on it (a package must be enabled to be
configurable). If the ``Configure`` button is disabled, it
means the package does not have a configuration object. When you do
click ``Configure``, a dialog like the one in Figure~:ref:`fig-packages-afrontconfigurationwindow` will appear.

.. _fig-packages-afrontconfigurationwindow:

.. figure:: figures/packages/afront_configuration_window.png
   :align: center
   :width: 40%

   Configuration window for a package that provides a configuration object.

To edit the value for a particular field, double-click on it, and change the
value. The values set in this dialog are persistent across VisTrails
sessions, being saved on a per-user basis.

Temporary File Management
^^^^^^^^^^^^^^^^^^^^^^^^^

.. index::
   pair: packages; temporary files
   pair: packages; ``filePool``

Command-line programs typically generate files as outputs. On
complicated pipelines, many files get created and passed to other
modules. To facilitate the use of files as communication
objects, VisTrails provides basic infrastructure for temporary file
management. This way, package developers do not have to worry about
file ownership and lifetimes.

To use this infrastructure, it must be possible to tell the program
being called which filename to use as output. VisTrails can accommodate
some filename requirements (in particular, specific
filename extensions might be important in Windows environments, and
these can be set), but it must be possible to direct the output to a
certain filename.

We will use ``Afront``'s ``compute()`` method to
illustrate the feature.

.. code-block::python

   ...
   class Afront(Module, AfrontRun):
           
       def compute(self):
   .. _ref-packages-tfcreate:
   :red:`        o = self.interpreter.filePool.create_file(suffix='.m')`
           args = []
   .. _ref-packages-hasInputFromPort1:
   :red:`        if not self.hasInputFromPort("file"):`
               raise ModuleError(self, "Needs input file")
           args.append(self.getInputFromPort("file").name)
   .. _ref-packages-hasInputFromPort2:
   :red:`        if self.hasInputFromPort("rho"):`
               args.append("-rho")
               args.append(str(self.getInputFromPort("rho")))
   .. _ref-packages-hasInputFromPort3:
   :red:`        if self.hasInputFromPort("eta"):`
               args.append("-reduction")
               args.append(str(self.getInputFromPort("eta")))
           args.append("-outname")
   .. _ref-packages-tfname:
   :red:`        args.append(o.name)`
           args.append("-tri")
           self.run(args)
   .. _ref-packages-tfsetresult:
   :red:`        self.setResult("output", o)`
   ...

Line :ref:`ref-packages-tfcreate` shows how to create a temporary file
during the execution of a pipeline. There are a few new things
happening, so let us look at them one at a time. Every module holds a
reference to the current *interpreter*, the object responsible
for orchestrating the execution of a pipeline. This object has a
``filePool``, which is what we will use to create a pipeline,
through the ``create_file`` method. This method takes
optionally a named parameter ``suffix``, which forces the
temporary file that will be created to have the right extension.

The file pool returns an instance of ``basic_modules.File``,
a module that is provided by the basic VisTrails packages. There are
two important things you should know about ``File``. First, it
has a ``name`` attribute that stores the name of the file it
represents. In this case, it is the name of the
recently-created temporary file. This allows you to safely use this
file when calling a shell, as seen on Line :ref:`ref-packages-tfname`.
The other important feature is that it can be passed directly to an
output port, so that this file can be used by subsequent modules. This
is shown on Line :ref:`ref-packages-tfsetresult`.

The above code also introduces the boolean function ``hasInputFromPort`` (see Lines~:ref:`ref-packages-hasInputFromPort1`, :ref:`ref-packages-hasInputFromPort2`, and :ref:`ref-packages-hasInputFromPort3`). This is a simple error-checking function that verifies that the port has incoming data before the program attempts to read from it. It is considered good practice to call this function before invoking ``getInputFromPort`` for any input port.

**Accommodating badly-designed programs** Even though it is
considered bad design for a command-line program not to allow the specification of an output
filename, there do exist programs that lack this functionality. In this case, a possible
workaround is to execute the command-line tool, and move the generated
file to the name given by VisTrails.

Interfacing with the |vistrails| Menu
=====================================

As we saw in Section~:ref:`sec-pkg_config`, using the ``ConfigurationObject`` class is one way to "hook" your custom package into the |vistrails| GUI.  However, this is not the only way to integrate your package with the user interface. |vistrails| also supports a mechanism whereby your package can add new options underneath the ``Packages`` menu (Figure~:ref:`fig-packages-package_menu`).

.. _fig-packages_menu:

.. figure:: figures/packages/package_menu.png
   :align: center
   :width: 5in

   Packages can integrate their own commands into the main |vistrails| menu.

This is done by adding a function named ``menu_items`` to your main package file. This function takes no parameters, and should return a tuple of pairs for each new menu item to be added. The first element of each pair is the label of the menu item as it should appear in the GUI. The second element of the pair is the name of the callback function to be invoked when the user selects that menu item. 

As an example, we include below the implementation of ``menu_items`` from the |vistrails| Spreadsheet package:

.. code-block::python

   def menu_items():
       """menu_items() -> tuple of (str,function)
       It returns a list of pairs containing text for the menu and a
       callback function that will be executed when that menu item is selected.    
       """

       def show_spreadsheet():
           spreadsheetWindow.show()
       lst = []
       .. _ref-pkg-append_menu_item
       :red:`lst.append(("Show Spreadsheet", show_spreadsheet))`
       return tuple(lst)

Writing your own ``menu_items`` function is straightforward; simply use the provided example as a basis, and substitute labels and callback functions as appropriate for your specific module. Although the Spreadsheet package currently only implements one new menu option, you are free to add as many as you see fit; just append additional pairs to the list (see Line~:ref:`ref-pkg-append_menu_item` of the example code) before the function returns.

The ``Packages`` menu is organized hierarchically, as illustrated in Figure~:ref:`fig-packages-package_menu`. Each package that contributes a ``menu_items`` function will receive an entry in the ``Packages`` menu. The actual menu items for each package will appear in a submenu.

.. _sec-interpackage_dependencies:

Interpackage Dependencies
=========================

.. index::
   pair: packages; dependencies

When creating more sophisticated VisTrails packages, you might want to
create a new module that requires a module *from another package*. For example, using modules from different packages as
input ports, or even subclassing modules from other packages, require
management of interpackage dependencies. VisTrails needs to know about
these so that packages can be initialized in the correct order. To specify these dependencies, you should add a function named
``package_dependencies`` to your package. This function should return a list containing the identifier strings of the required packages.

As an example of this function's usage, let's take a look at a (simplified) code segment from the VTK package, which is included in the standard |vistrails| distribution:

.. code-block::python

   def package_dependencies():
       return ['edu.utah.sci.vistrails.spreadsheet']


As you can see, the ``package_dependencies`` function is quite straightforward; it simply returns a list of the identifiers for the packages required by the VTK package. In this case, the list contains just a single string, as the |vistrails| Spreadsheet is the only package dependency for the VTK package.

The simple approach taken by the above code works well for the majority of cases, but in practice you may want to add some error-checking to your ``package_dependencies`` function. This allows |vistrails| to recover gracefully in the unlikely event that the Spreadsheet package is missing. Below is the complete ``package_dependencies`` function for the VTK package:

.. code-block::python

   def package_dependencies():
       import core.packagemanager
       manager = core.packagemanager.get_package_manager()
       if manager.has_package('edu.utah.sci.vistrails.spreadsheet'):
           return ['edu.utah.sci.vistrails.spreadsheet']
       else:
           return []


The above code segment also demonstrates the |vistrails| API function ``has_package`` which simply verifies that a given package exists in the system.

Package Requirements
====================

In Section~:ref:`sec-interpackage_dependencies`, we saw how packages can depend on other packages. However, some packages may also depend on the presence of external libraries (in the form of Python modules) or executable files in order to run correctly.

Required Python Modules
^^^^^^^^^^^^^^^^^^^^^^^

To check for the presence of a required Python module, you should add a function named ``package_requirements`` to your package. This function need not return any value; however it may raise exceptions or output error messages as necessary.
Here is an example of the syntax of the ``package_requirements`` function, taken from the |vistrails| VTK package:

.. code-block::python

   def package_requirements():
       import core.requirements
   .. _ref-packages-module_exists1
       if not core.requirements.python_module_exists('vtk'):
           raise core.requirements.MissingRequirement('vtk')
   .. _ref-packages-module_exists2
       if not core.requirements.python_module_exists('PyQt4'):
           print 'PyQt4 is not available. There will be no interaction',
           print 'between VTK and the spreadsheet.'
       import vtk


A key element of ``package_requirements`` is the use of the function ``python_module_exists``  (see Lines~:ref:`ref-packages-module_exists1` and~:ref:`ref-packages-module_exists2`), which checks whether a given module has been installed in your local Python system.

Required Executables
^^^^^^^^^^^^^^^^^^^^

As explained in Section~:ref:`sec-wrapping_cmdline_tools`, a common motivation for writing new |vistrails| modules is to wrap existing command-line tools. To this end, the |vistrails| API provides a function called ``executable_file_exists`` which checks for the presence of specific executables on the path.

Here is an example of its usage, taken from the ``initialize`` function of the ``ImageMagick`` package. This package is included in the standard |vistrails| distribution. The following code snippet checks to see if ``convert``, a command-line program associated with the *ImageMagick* suite of graphics utilities, is on the path.

.. code-block::python

   import core.requirements

   ...

       if (not core.requirements.executable_file_exists('convert')):
           raise core.requirements.MissingRequirement("ImageMagick suite")


Note that this function is not strictly required in order to wrap third party executables into a module. Using a ``Configuration`` object (see Section~:ref:`sec-pkg_config`) that lets the user specify the path to an executable may be a cleaner solution.

For additional information or examples of any of the functions described above, please refer to the |vistrails| source code or contact the |vistrails| development team.

Interaction with Caching
========================

For optimization purposes, |vistrails| caches the results of intermediate computations performed as part of a workflow. This is generally a safe practice because most computations are deterministic. However, if a module's operation includes any randomization, then its behavior will likely change with each execution of the workflow, and thus should not be cached.

The ``Module`` superclass defines a function called ``is_cacheable``, which determines whether or not a module should allow itself to be cached. The default implementation of this function returns ``True``. You can override this function in your own subclasses of ``Module``, if desired.

*Note: Caching is an advanced topic. Please contact the |vistrails| development team if you have questions about how this applies to your own custom modules.*

For System Administrators
=========================
Most users will want to put their custom packages in their

 :math:`\sim`\ ``/.vistrails/userpackages``

directory, as described in Section~:ref:`sec-packages-simple_example`. This makes the package available to the current user only. However, if you are a power user or a system administrator, you may wish to make certain packages available to all users of a |vistrails| installation. To do this, copy the appropriate package files and/or directories to the

 ``vistrails/packages``

directory of the |vistrails| distribution.
The packages will be made visible to users the next time they launch |vistrails|.

.. %Advanced: Wrapping a big API
.. ============================
.. %In the future, there will be a walkthrough of the VTK package wrapping mechanism. 

.. rubric:: Footnotes
.. [#] This package is not included in binary distributions of |vistrails|, but is available in the source code distribution. The stand-alone ``Afront`` utility is available at http://afront.sourceforge.net.
.. [#] Programmers who are more comfortable with single-inheritance languages like Java and C# may be unfamiliar with mixins. A mixin class is similar to an *interface* in Java or C#, except that a mixin provides an implementation as well. Python's support for multiple inheritance allows subclasses to "import" functionality as needed from a mixin class, without artificially cluttering the base class's interface.