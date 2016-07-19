VisTrails Packages
******************

..  _packages:

Packages
--------

Packages are the name of the plugins in VisTrails that provide modules. Each package usually wraps a library or provide related functionalities. They are loaded by the package manager and are wrapped by :class:`vistrails.core.modules.package.Package`.

A VisTrails Package is a Python module or package in a location where the package manager will find it (either ``vistrails/packages`` or ``.vistrails/userpackages``). It is either a single module or a directory with the following structure::

    my_codepath
    |-- __init__.py
    |-- init.py
    +-- ...

``my_codepath`` is referred to as "codepath" in the code; concatenated with the "prefix", it gives the argument passed to import to load the package (set as :attr:`~vistrails.core.modules.packages.Package._module`).

``my_codepath.__init__`` has to exist for the directory to be importable. If ``my_codepath.init`` exists, it will be loaded as :attr:`~vistrails.core.modules.packages.Package._module` when the module is enabled instead of ``my_codepath``; this allows the bulk of the code (the part that usually has Python dependencies) to be separate from the package root, in which we find a bunch of functions and constants that are used by VisTrails before the package is enabled.

The package should contain (in ``__init__.py``) the following:

* ``name``: a human-readable name for the package, displayed in dialogs
* ``identifier``: a unique identifier for the package, used to refer to it everywhere (for dependency links in other packages, and in serialized workflows)
* ``version``: a version number (see :ref:`upgrades`)

It can also optionally have the following:

* ``configuration``: A :class:`~vistrails.core.configuration.ConfigurationObject` holding the configuration of this package, that will be persisted to ``.vistrails``. It is currently injected in ``init`` and you can thus use it without importing it, but it's good practice to import it from somewhere anyway (at the very least, it makes IDE not report it as undefined reference).
* ``package_dependencies``: A simple function that returns a list of package identifiers this package depends on. It will not be possible to enable this package if they are not available. The package manager will also make sure they are enabled first, so cyclic dependencies are not possible here.
* ``package_requirements``: A function that checks that the other requirements are met. For example, a VisTrails package wrapping a library might want to check that the library is importable there, to give out a clean error message to the user if it isn't (and optionally, grab it automatically with the bundle system; use :func:`vistrails.core.requirements.require_python_module` in there for example).
* ``can_handle_identifier`` DOCTODO
* ``can_handle_vt_file`` DOCTODO

..  autofunction:: vistrails.core.requirements.require_python_module

..  autofunction:: vistrails.core.requirements.require_executable

The ``my_codepath.init`` (if separate, else ``my_codepath``) module is can contain the following:

* ``initialize``: The "entry point" of the package, called when initializing. Registers :class:`~vistrails.core.modules.vistrails_module.Module`s with the :class:`~vistrails.core.modules.module_registry.ModuleRegistry` (after generating them dynamically, for example; else ``_modules`` might be more convenient).
* ``_modules``: A list of :class:`~vistrails.core.modules.vistrails_module.Module` subclasses to register with the module registry automatically. It can also be a dict mapping a namespace to a list of modules. A module can also be replaced with a tuple ``(ModuleClass, options)`` where ``options`` is a dict with the module's settings.
* ``contextMenuName``: The single entry of the context menu shown when right-clicking a module in the module palette. The module name (or package name) is the only argument. ``callContextMenu`` is called with the same argument if the user clicks the menu entry.
* ``callContextMenu``: Callback for the context menu. The module name (or package name) is the only argument.
* ``handle_module_upgrade_request`` DOCTODO
* ``handle_all_errors`` DOCTODO
* ``handle_missing_module`` DOCTODO
* ``loadVistrailFileHook`` DOCTODO
* ``saveVistrailFileHook`` DOCTODO

..  todo::

    Right now, ``contextMenuName()`` only allows package creator to display a one-element context menu.

    :issue:`1115`

..  autoclass:: vistrails.core.modules.package.Package
    :members:

..  autoclass:: vistrails.core.packagemanager.PackageManager
    :members:

..  _modules:

Modules
-------

Package register modules with VisTrails. These are the boxes that can be assembled in pipelines and run code when executing.

A module is simply a subclass of :class:`~vistrails.core.modules.vistrails_module.Module`. It represents both a **datatype** (e.g., the type of a port or a connection) and a **computation unit** (e.g. a box in the pipeline view, with ports from and to which you draw connections). Modules can use single-inheritance, which will inherit the ports from the parent unless they are overridden. It is possible to connect one port to a port of a parent type. The special type `Variant` can connect to and from any other type.

Note that the type of a port, which is a Module, is different from the actual type of Python objects that are passed on the connection. In fact, `Module` instances are not passed on connections anymore since they cause problems (they have references to the pipeline, the interpreter, ... which make them very unsafe to serialize). For example, an SQLAlchemy Connection object is passed on `DBConnection` ports, the figure number is passed unwrapped on `MplFigure` ports, and either numpy arrays or Python `list`s are passed on `List` ports. The association between a `Module` and the actual type passed on connections is just convention, although VisTrails will check it in specific cases (such as when one end of the connection is a `Variant` port) by calling :func:`~vistrails.core.modules.vistrails_module.Module.validate` on the value.

..  autoclass:: vistrails.core.modules.vistrails_module.Module
    :members:
