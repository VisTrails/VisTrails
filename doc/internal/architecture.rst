Project architecture and concepts
*********************************

VisTrails is made of multiple components.

..  _concept-database:

Database
--------

The database layer is responsible for reading and writing objects to the disk. It is composed of the :mod:`vistrails.core.db` and :mod:`vistrails.db` packages.

The currect objects and their relationships are described in a schema, from which the system generates Python classes and code to load or save them from either XML files (with ElementTree) or an SQL database (with MySQLdb, soon to be replaced with SQLAlchemy). There is one set of specs, DB classes and loading/saving routines for each version of the schema (e.g. :mod:`vistrails.db.versions.v1_0_3`), along with code to translate from one version to the other.

Note that a ``.vt`` file is just a ZIP file that contains the XML vistrail and provenance log (along with optional data, such as subworkflows, version thumbnails, ...).

Objects loaded from the database eventually gets converted to core classes by assigning their ``__class__`` attribute, at which point they gain all the methods defined there.

..  _concept-registry:

Module registry
---------------

The :class:`~vistrails.core.modules.module_registry.ModuleRegistry` contains the list of all the modules currently available, in the form of :class:`~vistrails.core.modules.module_descriptor.ModuleDescriptor` objects. These contain the module identifier, name and namespace of the module, the input and output ports, the parent module if any, and also optional things like the constant widget and configuration widget class (see :ref:`widgets`) and fringe shape for the pipeline view. They also have a direct reference to the :ref:`~vistrails.core.modules.vistrails_module.Module` subclass in the defining package that the interpreter will instanciate for execution (see :ref:`interpreter`).

The module registry also sends some signals when modules get added or removed, which are used to update the module palette in the UI.

..  todo::

    Possible future directions: allow packages to provide a list of packages (for the palette), but to provide modules lazily. This would make packages that dynamically generate modules a lot faster, because they would only need to generate all the modules upfront (or at all).

..  _concept-packagemngr:

Package manager
---------------

The :class:`~vistrails.core.packagemanager.PackageManager` contains the list of available and enabled packages. Available packages are obtained by listing the ``vistrails/packages`` and ``.vistrails/userpackages`` directories. It handles dependencies between packages, and uses an :func:`__import__` override to discover the Python modules imported by each package; this is used to reload them automatically when the packages that imported them is reloaded.

..  todo::

    The __import__ override is a bit insane and it might be worth disabling it completely, and simply reloading packages under the package's codepath when "reload" is clicked.

    If this is kept, it should be fixed to use an actual full graph at the package manager level, since multiple packages might depend on the same library and the current logic will fail to see that.

..  _concept-application:

Application
-----------

The application logic is contained in two application classes: :class:`~vistrails.core.application.VistrailsCoreApplication`, used in non-graphical mode, for example through the :ref:`api_highlevel`, and :class:`vistrails.gui.application.VistrailsApplicationSingleton` which is a :class:`QtGui.QApplication`.

The application handles startup and configuration, notification delivery, output modes (see :ref:`output_modules`), jobs (see :ref:`jobs`), logging, and loading and saving vistrails (creating controllers from the database objects, or handing them out to the database layer).

The graphical application handles the single-instance mode (communicating with the main instance over shared memory, if a second one is opened) and setting the default application with the OS.

..  _concept-packages:

Packages and modules
--------------------

Packages are the name of the plugins in VisTrails that provide modules. Each package usually wraps a library or provide related functionalities. They are loaded by the package manager and are wrapped by :class:`vistrails.core.modules.package.Package`.

A VisTrails Package is a directory with the following structure::

    my_codepath
    |-- __init__.py
    |-- init.py
    +-- ...

``my_codepath`` is referred to as "codepath" in the code; concatenated with the "prefix", it gives the argument passed to import to load the package (set as :attr:`~vistrails.core.modules.packages.Package._module`).

ModuleDescriptor.module?

If ``my_codepath.init`` exists, it will be loaded as :attr:`~vistrails.core.modules.packages.Package._module` when the module is enabled instead of ``my_codepath``; this allows the bulk of the code (the part that usually has Python dependencies) to be separate from the package root, in which we find a bunch of functions and constants that are used by VisTrails before the package is enabled.

The package should contain (in ``__init__.py``) the following:

* ``name``: a human-readable name for the package, displayed in dialogs
* ``identifier``: a unique identifier for the package, used to refer to it everywhere (for dependency links in other packages, and in serialized workflows)
* ``version``: a version number (see :ref:`upgrades`)

It can also optionally have the following:

* ``configuration`` DOCTODO
* ``package_dependencies`` DOCTODO
* ``package_requirements`` DOCTODO
* ``can_handle_identifier`` DOCTODO
* ``can_handle_vt_file`` DOCTODO

The ``my_codepath.init`` (if separate, else ``my_codepath``) module is can contain the following:

* ``handle_all_errors`` DOCTODO
* ``handle_module_upgrade_request`` DOCTODO
* ``handle_missing_module`` DOCTODO
* ``contextMenuName`` DOCTODO
* ``callContextMenu`` DOCTODO
* ``loadVistrailFileHook`` DOCTODO
* ``saveVistrailFileHook`` DOCTODO
* ``_modules`` DOCTODO

..  _concept-interpreter:

The interpreter
---------------

DOCTODO

..  _concept-controller:

Vistrail and VistrailController
-------------------------------

DOCTODO

..  _concept-ui:

User interface
--------------

DOCTODO

..  _concept-log:

Provenance log
--------------

DOCTODO
