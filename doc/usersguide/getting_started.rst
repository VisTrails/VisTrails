***************
Getting Started
***************

The |vistrails| system is distributed both as source code and pre-built
binaries, and instructions for obtaining either can be found at our
website: http://www.vistrails.org.  Because the system is
written in Python using a Qt interface, it can be run on most
architectures that support these two components, even if a pre-built
binary is not available for your system.
Section :ref:`sec-start-installing` provides instructions to guide you
through installation procedures, and Section :ref:`sec-start-quick`
gives a quick orientation and serves as a springboard for
exploring the different features of |vistrails|.

.. _sec-start-installing:

Installation 
============ 

There are two types of |vistrails| installations. The first is a
binary installation that lets you use |vistrails| by running the
precompiled executable. The second is a full source code installation
that requires you to install and compile |vistrails| and all of its
dependencies. Of the two types of installations, the binary version is
much easier, and we encourage first-time users to use this option
whenever possible.  Precompiled binaries are currently available for
Microsoft Windows (XP and Vista) and Mac OS X (10.5.x or higher).  To
obtain either a binary or source copy of |vistrails|, please see our
website: http://www.vistrails.org.

.. _sec-binary_installation_windows:

Installing |vistrails| on Windows XP/Vista
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To install |vistrails| on Windows, download the installation bundle for
Windows from the |vistrails| website: http://www.vistrails.org.
Unzip the file using the decompression program of your choice, then
double-click the executable to begin installation
(Figure :ref:`Installation wizard for Microsoft Windows XP/Vista<fig-start-windows_installation>`). Follow the prompts in
the installation wizard to complete the installation process.

.. _fig-start-windows_installation:

.. figure:: /figures/getting_started/windows_installation_wizard.png
   :width: 4in
   :align: center
   
   Installation wizard for Microsoft Windows XP/Vista.

.. _sec-binary_installation_macosx:

Installing |vistrails| on Mac OS X
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To install |vistrails| on Mac OS X, download the installation bundle
for Mac from the |vistrails| website:
http://www.vistrails.org. The precompiled binary currently only
supports Mac OS X 10.5.x or higher. The disk image should be mounted automatically
(Figure :ref:`Installing VisTrails on Mac OS X <fig-start-mac_installation>`). Once the disk image is mounted, drag the |vistrails| folder to the Applications
folder to install the software.

.. _fig-start-mac_installation:

.. figure:: /figures/getting_started/mac_post_uncompress_window.png
   :width: 5in
   :align: center

   Installing |vistrails| on Mac OS X.
   
.. _sec-binary_installation_ubuntu:

Installing |vistrails| on Ubuntu Linux
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Although not a binary installation *per se*, installing
|vistrails| on Ubuntu Linux is nonetheless quite straightforward.
|vistrails| now interfaces with "apt" directly via a Python API. This
allows dynamic installation of necessary packages. As a result, you do
not need to manually install any of the dependent packages. Just
download the |vistrails| source code and execute it with::

   python vistrails.py

and |vistrails| should detect all necessary software and, if necessary,
ask for your permission to install it.

.. _sec-src_installation:

Installing |vistrails| from source
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Installing |vistrails| from source code is a non-trivial task.  Rather
than listing full compilation instructions in this manual, we instead
provide a list of software packages upon which |vistrails| is
dependent, and refer you to the |vistrails| website for additional
details.

* Python 2.6 or higher
* Qt 4.4 or higher
* PyQt4
* SciPy
* VTK (needed to run the examples in this book)

There may also be additional dependencies, depending on which optional
features of |vistrails| you plan to use.

Please refer to http://www.vistrails.org/index.php/Mac_Intel_Instructions for more details.

.. _sec-start-quick:

Quick Start
===========

On Windows and Mac OS X, you can launch |vistrails| by double-clicking
on the |vistrails| application icon. In general, however, it is
possible to start |vistrails| on any system by navigating to the
directory where the file ``vistrails.py`` is located (usually
the root directory of your installation) and executing the command::

   python vistrails.py

Depending on a number of factors, it can take a few seconds for the
system to start up. As |vistrails| loads, you may see some messages
that detail the packages being loaded and initialized. This is normal
operation, but if the system fails to load, these messages will
provide information that may help you understand why.  

The Vistrails Builder Window
============================

After everything has loaded, you will see the |vistrails| Builder window as
shown in Figure :ref:`fig-start-builder`. If you have enabled the
|vistrails| Spreadsheet (Packages :math:`\rightarrow` VisTrails Spreadsheet :math:`\rightarrow` Show Spreadsheet), you will also see a second window like that in
Figure :ref:`fig-start-spreadsheet`.  Note that if the spreadsheet window is not visible, it will open upon execution of a workflow that uses it.

.. _fig-start-builder:

.. figure:: /figures/getting_started/builder.png
   :width: 5in

   |vistrails| Builder Window

.. _fig-start-spreadsheet:

.. figure:: /figures/getting_started/spreadsheet.png
   :width: 5in

   |vistrails| Spreadsheet Window

The VisTrails Toolbar
^^^^^^^^^^^^^^^^^^^^^

.. _fig-start-toolbar:

.. figure:: /figures/getting_started/toolbar.png  
   :width: 100%
   
   |vistrails| Toolbar

.. index:: toolbar

The |vistrails| toolbar both allows you to execute the current workflow or function, and switch between various modes.  A brief description of each member of the toolbar follows:

**Pipeline** This view shows the current workflow.  See Chapter :ref:`chap-creating` for information about creating a workflow.

**History** This view shows different versions of the workflow(s) as it has  progressed over time.  See Chapter :ref:`chap-version_tree`.

**Search** Use this mode to search for modules or subpipeline within the current version, the current vistrail, or all vistrails.  See Chapter :ref:`chap-querying`.

**Explore** This option allows you to select one or more parameter(s) for which a set of values is created.  The workflow is then executed once for each value in the set and displayed in the spreadsheet for comparison purposes.  See Chapter :ref:`chap-paramexploration`.

**Provenance** The ``Provenance`` mode shows the user a given vistrail's execution history.  When a particular execution is selected, its pipeline view with modules colored according to its associated execution result is shown.  See Chapter :ref:`chap-provenance_browser`.

**Mashup** The ``Mashup`` mode allows you to create a small application that allows you to explore different values for a selected set of parameters.  See Chapter :ref:`chap-mashups`
for more information.

**Execute** ``Execute`` will either execute the current pipeline when the ``Pipeline``, ``History``, or ``Provenance`` views are selected, or perform the search or exploration when in ``Search`` or ``Exploration`` mode.  This button is disabled for ``Mashup`` mode, or when there is not a current workflow to execute.

The ``New``, ``Open``, and ``Save`` buttons will create, open, and save a vistrail, as expected.

Palettes and Associated Views
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. index:: 
   pair: palette; views

**Palettes**

As you can see, the builder window has a center widget with a palette on each side.  There are a number of views (listed in the 4th group of the views menu) that when made visible, will be opened in these palettes.  In this section, we will discuss how the views are arranged. 

Notice that when VisTrails first launches the builder window, both palettes contain two views.  The left palette is split so both views are visible, whereas the right palette uses tabs to display one view at a time.        By default, additional views will be shown in the right, and lower left panels when they are made visible.  To make a view visible, either switch to a mode that requires it, or select it from the views menu.  For example, the ``Mashup`` mode will add the ``Mashup Pipeline`` and ``Mashups Inspector`` views to the panels.  When the mode is changed from ``Mashup``, these two views will be removed (hidden).  

**Buttons**

Notice that there is a button with a pin icon in the upper right corner of each view (see Figure :ref:`fig-panel-buttons`).  If you don't want a view to disappear when you change modes, make sure it is pinned.  When the pin points up, it is unpinned and the view is likely to disappear when you change modes.

The other two buttons, the one with the 'X' and the one with the rectangular outlines (see Figure :ref:`fig-panel-buttons`), will either close the view, or undock the view, depending on which one you push.  Alternatively, you may undock a view by clicking on the view's title bar and pulling it out of the palette.  The view can then either remain in its own window, or can be docked by placing it in either palette.

.. _fig-panel-buttons:

.. figure:: /figures/getting_started/panel_buttons.png
   
   Buttons - Close, Detach, and Pin

**View Locations**

.. index::
   pair: view;location

The following table gives the view that is visible in each palette for each of the main views/modes:

+-------------++---------------------+--------------------+
|             || Lower Left Palette  | Right Palette      |
+=============++=====================+====================+
| Pipeline    || Modules             | Module Information |
+-------------++---------------------+--------------------+
| History     || Modules             | Properties         |
+-------------++---------------------+--------------------+
| Explore     || Explore Properties  | Set Methods        |
+-------------++---------------------+--------------------+
| Provenance  || Modules             | Log Details        |
+-------------++---------------------+--------------------+
| Mashup      || Mashups Inspector   | Mashup Pipeline    |
+-------------++---------------------+--------------------+

Notice that the ``Workspace``, ``Diff Properties``, and ``Vistrail Variables`` views are not in the table.  That is because, the ``Workspace`` view is always visible, the ``Diff Properties`` view opens in the right palette when a visual diff is performed in the ``History`` view, and the ``Vistrail Variables`` view is opened from the ``Views`` menu.  Note: with the ``Vistrail Variables`` view especially, if you don't want it to disappear, you should make sure it is pinned.

The Center Widget
^^^^^^^^^^^^^^^^^

The center widget is somewhat larger than the side panels as it is intended to be the main workspace.  It displays the following views: ``Pipeline``, ``History``, ``Search``- query and results, ``Visual Diff`` results, ``Explore``, ``Provenance``, and ``Mashup``.  By default, one view is shown.  To open an additional view, type CTRL-t to create a new tab.  The new tab starts out in the ``Pipeline`` view, but you are free to change it to any of the other views.  Note that the tabs from only one vistrail are displayed at a time.  When you switch to a different vistrail, the other vistrail's set of open tabs are displayed.

If you would like to see views from more than one vistrail at a time, you may do this by right-clicking on the vistrail (listed in ``Current Vistrails`` of the ``Workspace`` view), and selecting the option to open in a new window.  The side palettes will stay with the original window, but can be moved to the current window by selecting ``Dock Palettes`` from the ``Views`` menu.

If you would like to see multiple views from the same vistrail, double-click the title of the view to detach it.  It is not possible to reattach the view, so once you are finished with the detached view, you may close it.  If you would like the view to be reattached, you should close it and open it again in a new tab.

.. _sec-start-file:

Manipulating |vistrails| Files
==============================

.. index::
   pair: open; vistrail 
   pair: open; from a database
   single: tab

To open a |vistrails| file, or *vistrail*, you can either click the
``Open`` button in the toolbar or select ``Open`` from the ``File``
menu. This brings up a standard file dialog where you can select a
vistrail to open.  Vistrails are identified by the ``.vt`` file
extension. Alternatively, if the vistrail is listed under `My Vistrails` in the ``Workspace Panel``, double clicking its name will open it.  When a vistrail is opened, it is listed in the ``Workspace`` (upper left panel) under `Current Vistrails`.  Since only one open vistrail is displayed at a time, the ``Workspace`` allows you to select which one to display.  Vistrails can also be stored in a database, enabling a central repository for workflows. See Chapter :ref:`chap-database` for more details about this feature.

.. index::
   pair: close; vistrail
   pair: save; vistrail

To close a vistrail, you can either choose the
``Close`` option from the ``File`` menu or type Ctrl-w.  If
the vistrail has not been saved, you will be asked if you wish to save
your work. To save a vistrail, there is both a
button and a menu item in the ``File`` menu.  If you would
like to save the vistrail with a different name or in a different
location, you can use the ``Save As`` option.

.. _sec-start-basics:

|vistrails| Basics
==================

.. index::
   single: workflow
   pair: modules; definition
   pair: connections; definition

In general, a *workflow* is a way to structure a complex
computational process that may involve a variety of different
resources and services.  Instead of trying to keep track of multiple
programs, scripts, and their dependencies, workflows abstract the
details of computations and dependencies into a graph consisting of
computational *modules* and *connections* between these
modules.

The ``Pipeline`` button on the |vistrails| toolbar accesses VisTrails'
interface for building workflows. Similar to many existing workflow
systems, it allows you to interactively create workflows using an
extensible library of modules and a connection protocol that helps you
determine how to connect modules.  To add a module to a workflow,
simply drag the module's name from the list of available modules to
the workflow canvas.  Each module has a set of input and output ports,
and outputs from one module can be connected to inputs of another
module, provided that the types match.  For more information on
building workflows in |vistrails|, see Chapter :ref:`chap-creating`.

.. index:: 
   pair: vistrail; definition

In addition to VisTrail's *Pipeline* interface for manipulating
individual workflows, the *History* interface (accessed through
the ``History`` button on the toolbar) contains a number of
features that function on a collection of workflows.
A *vistrail* is a collection of
related workflows.  As you explore different computational approaches
or visualization techniques, a workflow may evolve in a lot of
directions.  |vistrails| captures all of these changes automatically
and transparently.  Thus, you can revisit a previous version of a
workflow and modify it without worrying about saving intermediate
versions.  This history is displayed by the |vistrails| Version Tree,
and different ways of interacting with this tree are discussed in
Chapter :ref:`chap-version_tree`.

With a collection of workflows, one of the necessary tasks is to
search for specific workflows.  VisTrail's search functionality is
accessed by clicking the ``Query`` button on the toolbar.
The criteria for these searches may
vary from finding workflows modified within a specific time frame to
finding workflows that contain a specific module.  Because of the
version history that |vistrails| captures, these tasks are natural to
implement and query.  |vistrails| has two methods for querying
workflows, a simple text-based query language and a query-by-example
canvas that lets you build exactly the workflow structure you
are looking for.  Both of these techniques are described in
Chapter :ref:`chap-querying`.

The ``Exploration`` button 
allows you to explore workflows by running the same
workflow with different parameters.  Parameter Exploration provides an
intuitive interface for computing workflows with parameters that vary
in multiple dimensions.  When coupled with the |vistrails| Spreadsheet,
parameter exploration allows you to quickly compare results and
discover optimal parameter settings.  See
Chapter :ref:`chap-paramexploration` for specific information on using
Parameter Exploration.

.. _sec-start-interact:

|vistrails| Interaction
=======================

Workflow Execution
^^^^^^^^^^^^^^^^^^

.. index:: execute

The ``Execute`` button on the toolbar serves as the "play" button for
each of the modes described above.  In both the Builder and Version
Tree modes, it executes the current workflow.  In Query mode, it
executes the query, and in Parameter Exploration mode, it executes the
workflow for each of the possible parameter settings.  

When a workflow is executed, the module color is determined as follows:

   * lilac: module was not executed
   * yellow: module is currently being executed
   * green: module was successfully executed
   * orange: module was cached
   * red: module execution failed

.. topic:: Note

   VisTrails caches by default, so after a workflow is executed, if none of its parameters change, it won't be executed again.

   If a workflow reads a file using the basic module File, VisTrails does check whether the file was modified since the last run. It does so by keeping a signature that is based on the modification time of the file. And if the file was modified, the File module and all downstream modules (the ones which depend on File) will be executed.

   If you do not want VisTrails to cache executions, you can turn off caching: go to Menu Edit :math:`\rightarrow` Preferences and in the General Configuration tab, change Cache execution results to Never.

   If you would like your input and output data to be versioned, you can use the Persistence package.

Additional Interactions
^^^^^^^^^^^^^^^^^^^^^^^

.. index:: undo, redo

From the ``Edit`` menu, ``Undo`` and ``Redo`` function in the standard way, but note that these
actions are implicitly switching between different versions of a
workflow.  Thus, you will notice that as you undo or redo a change to
a workflow, the selected version in the version tree changes.

.. index:: select, pan, zoom

For all modes except Parameter Exploration, the center pane of
|vistrails| is a canvas where you can manipulate the current workflow,
version tree, or query.  The buttons on the right side of the toolbar
allow you to change the default behavior of the primary mouse button
(the left button for most multiple button mice) within this canvas.
You can choose the behavior to select items in the scene, pan around
the scene, or zoom in and out of the scene by selecting the given
button.  In addition, if you are using a 3-button mouse, the right
button will zoom, and the middle button will pan.  To use the zoom
functionality, click and drag up to zoom out and drag down to zoom in.

.. index:: center

.. topic:: Note

   Pressing Ctrl-R will recenter the window.

