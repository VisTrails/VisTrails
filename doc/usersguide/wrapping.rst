.. _chap-wrapping:

*************************
Python Wrapping Framework
*************************

Introduction
============

.. index:: Python wrapping framework

|vistrails| provides a framework for automating the wrapping of Python functions and classes into |vistrails| modules. It is located in ``vistrails.core.wrapping``. It uses introspection and docstrings to figure out arguments, type information, default values, and enum values. It creates a wrapping specification that is used to create a vistrails module. Currently numpy docstrings are supported, but parsers for other types of docstrings can be also be used.

It is also possible to use only parts of the framework, such as the specification, which gives you access to the diff and patch tools, but requires you write your own module generator.

Module wrapping specification
=============================

The framework contains a specification for describing the translation between modules and functions/classes located in :mod:`vistrails.core.wrapper.spec`. :class:`~vistrails.core.wrapper.specs.ModuleSpec` is the base specification. It describes the attributes of a module, similarly to :class:`~vistrails.core.modules.config.ModuleSettings`. Modules have :class:`~vistrails.core.wrapper.specs.InputPortSpec`\ s and :class:`~ vistrails.core.wrapper.specs.OutputPortSpec`\ s for describing port attributes and how they translate into function and class attributes.

``InputPortSpec``\ s can have alternate specs that describes alternate port types for inputs. This can be useful when wrapping functions with multiple call signatures, such as for ``VTK`` methods.

`ModuleSpec`` can be used directly but will need the implementation of a generator method that turns the specification into a vistrails module. See the ``sklearn`` package for an example.

For Python :ref:`functions <sec-wrapping_functions>` and :ref:`classes <sec-wrapping_classes>` there are module generators that can create vistrails modules from specifications.

Specs can be subclassed and extended by adding attributes to ``attr``. Diffing will then work on the new attributes. Creating subclasses are usually only needed when using custom module generators.

There are a few tools for working with specifications. They can be used for patching incomplete specifications, diff'ing to see differences between package and library versions. They are available in :mod:`vistrails.core.wrapper.diff`.

Patching
--------

Automatic wrapping often generates incomplete or incorrect wrappers, which will require patching of the wrapping specification. The spec is designed to be easily patched, and provides tools to help with this.

Attribute patching
^^^^^^^^^^^^^^^^^^

If the patch consists of only type or attribute changes, this can be done by editing the specification directly, or using code to update the specification before writing it to xml.

To avoid the patched specification being overwritten when the specification is regenerated, a diff/merge step is supported. After patches are added to the spec, a diff should be created between the unpatched and patched specifications.

.. code-block:: bash

  python core/wrapper/diff.py computef functions-raw.xml functions-patched.xml functions-diff.xml

And after rerunning the function parser, the diff should be applied to the unparsed spec to create the new patched spec.

.. code-block:: bash

  python core/wrapper/diff.py applyf functions-raw.xml functions-diff.xml functions-patched.xml

This can be combined into an update procedure:

  * Compute diff (if spec has been patched)
  * Re-run the function parser (if the parser/library has been updated)
  * Apply the diff (to get the new patched spec)

Code patching
^^^^^^^^^^^^^

Sometimes the called object itself needs to be patched, with custom code. Then the object will need to be wrapped and the wrapped object be called by the generated module that wraps the required behaviour. In addition, the module spec contains a few helper attributes for common cases such as:

  * compute - Run a specific method after executing inputs
  * cleanup - Run a specific method after outputs have been computed
  * callback - Name of method that assigns progress callback
  * tempfile - Name of method that assigns temporary file creation routine

Currently these are used mostly by the 'vtk' package.

If you are using a custom module generator you can of course do all the code wrapping there using either spec attributes or class checks. See the ``matplotlib14`` package for examples.

Diff'ing specifications
-----------------------

Besides patching, the diff too can be used to check differences between specs and to suggest upgrades. When calling ``wrapper.diff`` from the comand line, ``showf/showc`` shows differences between specifications and ``upgradef/upgradec`` prints upgrade path suggestions between specifications. The upgrade command supports custom functions for calculating module and port similarities. This can be useful because which module and port upgrades that are possible are usually very library-specific.

The Python wrapper
==================

The PythonParser is the main class for automatically wrapping functions and classes:

  vistrails.core.wrapper.python_parser.PythonParser

The wrapping often needs to be adjusted for different libraries. For instance, ``VTK`` classes contains many getter/setter methods, whereas ``numpy`` mostly expose operations as functions. Therefore the wrapper is designed to be extensible to support different types of wrappings. PythonParser options include:

  * default_type - default type to use
  * instance_type - default type for class instances
  * typed_lists - whether to use type lists of depth 1 when possible
  * key_to_type - defines which types will be parsed
  * list_types - types that can be converted from list to depth 1 type
  * parse_doc - docstring parser function (default is numpydoc)
  * type_string_parser - custom type string parser function
  * class_spec - class specification class
  * function_spec - function specification class

.. _sec-wrapping_functions:

Function wrapping
-----------------

Functions can be wrapped using :meth:`~vistrails.core.wrapper.python_parser.PythonParser.parse_function`. It takes the function or its import string and an optional namespace, and generates a function specification (:class:`~vistrails.core.wrapper.specs.FunctionSpec`). Some function syntax needs to be patched manually, e.g., if an argument should be supplied as an argv or kwarg.

FunctionSpec can be loaded as a module using the function generator:

.. code-block:: python

  module = vistrails.core.wrapper.pythonfunction.gen_function_module(functionspec)

Python functions can be wrapped without docstrings, using introspection only, but will then only have type information from argument default values. But this is usually enough to get at least a working module.

.. _sec-wrapping_classes:

Class wrapping
--------------

There is no straightforward mapping from Classes to Modules. Classes can have constructor arguments, attrubutes, and methods. The different types can all be put in the same module, or split up with separate modules for class constructors (:class:`~vistrails.core.wrapper.specs.ClassSpec`), attribute inspectors (``ClassSpec``), and class methods (:class:`~vistrails.core.wrapper.specs.FunctionSpec`).

ClassSpec describes a class and can be loaded as a module using the class generator:

.. code-block:: python

  module = vistrails.core.wrapper.pythonclass.gen_class_module(classspec)

The ``numpy`` and ``scipy`` packages are using both function and class specs.

Classes can be parsed with parse_class, with flags specifying whether to parse arguments, attributes, and methods.

One option is to have one class with constructor, one attribute inspector class, and one class for each class method, like this:

.. code-block:: python

  classes = [parse_class(c, attribute_parsing=False),
             parse_class(c, argument_parsing=False), name=classname + 'Inspector']
  functions = parse_class_methods(c, namespace=classname + 'Methods')

Automatic Port Translations
--------------------------

Sometimes functions use types that is similar to an
existing type, but not identical. It may then be better to convert the
value to the supported type, rather than to create a completely new
type. This is especially true for common types that are already
supported, such as ``Color`` and ``File``. A type translation will be used
for all ports in a specification file. The ``translations`` argument
``port_type: code_string``. ``port_type`` should match a port type as
specified in the specification. ``code_string`` should be python code
block declaring the functions ``input_f`` and ``output_f``, which will
be applied to input and output ports, respectively.  An example for
translating ``basic:Color`` to a tuple of floats would be:

.. code-block:: python

    # Translate File and Color ports
    translations = {
        'basic:Color':
            "def input_t(value):\n"
            "    return value.tuple\n"
            "def output_t(value):\n"
            "    from vistrails.core.utils import InstanceObject\n"
            "    return InstanceObject(tuple=value)"}


    specs = SpecList(specs_list, translations=translations)

Note that this will not automatically work on subclasses. Each
subclass will need its own translation.

For the translation to be used it needs to be passed to the final module:

.. code-block:: python

    modules = [gen_class_module(spec,
                                translations=speclist.get_translations())
                                for spec in speclist.module_specs]

Examples in Packages
====================

There are a few packages using this framework, and can be used to demonstrate different parts of the framework:

* ``numpy`` and ``scipy`` generates functions and classes using numpy docstrings.
* ``VTK`` generates modules for classes using methods, subclassing. alternate portspecs, and patched classes.
* ``matplotlib14`` uses a custom function specification to explicitly generate modules, and also uses spec patching.
* ``sklearn`` uses the function spec to generate the modules dynamically.
