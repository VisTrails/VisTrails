Project architecture and concepts
*********************************

VisTrails is made of multiple components. This page gives a high-level overview of what they are, and links to relevant pages of the documentation.

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

The :class:`~vistrails.core.modules.module_registry.ModuleRegistry` contains the list of all the modules currently available, in the form of :class:`~vistrails.core.modules.module_descriptor.ModuleDescriptor` objects. These contain the module identifier, name and namespace of the module, the input and output ports, the parent module if any, and also optional things like the constant widget and configuration widget class (see :ref:`widgets`) and fringe shape for the pipeline view. They also have a direct reference to the :class:`~vistrails.core.modules.vistrails_module.Module` subclass in the defining package that the interpreter will instanciate for execution (see :ref:`concept-interpreter`).

The module registry also sends some signals when modules get added or removed, which are used to update the module palette in the UI.

..  todo::

    Possible future directions: allow packages to provide a list of packages (for the palette), but to provide modules lazily. This would make packages that dynamically generate modules a lot faster, because they would only need to generate all the modules upfront (or at all).

    :issue:`1117`

..  _concept-packagemngr:

Package manager
---------------

The :class:`~vistrails.core.packagemanager.PackageManager` contains the list of available and enabled packages. Available packages are obtained by listing the ``vistrails/packages`` and ``.vistrails/userpackages`` directories. It handles dependencies between packages, and uses an :func:`__import__` override to discover the Python modules imported by each package; this is used to reload them automatically when the packages that imported them is reloaded.

..  todo::

    The __import__ override is a bit insane and it might be worth disabling it completely, and simply reloading packages under the package's codepath when "reload" is clicked.

    If this is kept, it should be fixed to use an actual full graph at the package manager level, since multiple packages might depend on the same library and the current logic will fail to see that.

    :issue:`959`

..  _concept-application:

Application
-----------

The application logic is contained in two application classes: :class:`~vistrails.core.application.VistrailsCoreApplication`, used in non-graphical mode, for example through the :ref:`concept-api`, and :class:`vistrails.gui.application.VistrailsApplicationSingleton` which is a :class:`QtGui.QApplication`.

The application handles startup and configuration, notification delivery, output modes (see :ref:`output_modules`), jobs (see :ref:`jobs`), logging, and loading and saving vistrails (creating controllers from the database objects, or handing them out to the database layer).

The graphical application handles the single-instance mode (communicating with the main instance over shared memory, if a second one is opened) and setting the default application with the OS.

..  _concept-packages:

Packages and modules
--------------------

Packages are the name of the plugins in VisTrails that provide modules. Each package usually wraps a library or provide related functionalities. They are loaded by the package manager and are wrapped by :class:`vistrails.core.modules.package.Package`.

A VisTrails Package is a Python module or package in a location where the package manager will find it (either ``vistrails/packages`` or ``.vistrails/userpackages``). See :ref:`packages`.

..  _concept-interpreter:

The interpreter
---------------

The interpreter takes a :class:`~vistrails.core.vistrail.pipeline.Pipeline` and executes it, by creating the :class:`~vistrails.core.modules.vistrails_module.Module` objects defined by packages from the pipeline :class:`~vistrails.core.vistrail.module.Module` and connecting them. Currently, the execution strategy is very simple: the sink modules's update() methods are called by the interpreter, and they recursively call their upstream's update() methods before doing their compute() logic.

Instanciated modules are also kept in a global cache, the *persistent pipeline*, keyed on their subpipeline signature (a hash computed recursively for a module and its upstream).

..  todo::

    This strategy is very limited as it is completely local. It makes it difficult to add "smart" logic to get us towards better caching, parallel execution, ... We are considering rewriting the interpreter and building into it the looping/streaming, group and parallel execution code, using the opportunity to improve caching, persistence and job submission.

..  _concept-controller:

Vistrail and VistrailController
-------------------------------

:class:`~vistrails.core.vistrail.vistrail.Vistrail` represents a full tree of pipeline versions. It is a project in the VisTrails application. There are no pipeline descriptions in a Vistrail, only actions which add/remove modules and connections from an empty pipeline (and annotations).

a Vistrail is wrapped in :class:`~vistrails.core.vistrail.controller.VistrailController` (or the GUI version: :class:`~vistrails.gui.vistrail_controller.VistrailController`) that provide all the pipeline manipulation logic. It has a notion of current pipeline which is efficiently changed by actions when moving around the version tree, and provides methods to create such actions. It also handles upgrading versions when needed (see :ref:`upgrades`) and interactions with subworkflows.

..  _concept-ui:

User interface
--------------

The user interface lives in :mod:`vistrails.gui`. It is based on PyQt4 and allows the user to display and manipulate versions and pipelines through a VistrailController.

In graphical mode, most visualizations end up in the spreadsheet, which is implemented as a package.

..  _concept-log:

Provenance log
--------------

When a pipeline is executed, structured information from each module is appended to an XML file called the provenance log. Each module gets its own entry, with information such as time, status (executed, up to date in the cache, exception info), plus "annotations" from modules.

..  todo::

    This provenance information should be made available to modules so they can reuse a past context exactly.

    :issue:`548`

..  _concept-api:

High-level API
--------------

A high-level API, directly importable under :mod:`vistrails`, makes it possible to use VisTrails workflows from scripts or other applications. It automatically builds an application when first used, provides easy-to-use wrappers for VistrailController and friends, and integration with the IPython notebook. See :mod:`vistrails.core.api`.
