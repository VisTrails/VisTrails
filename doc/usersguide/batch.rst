.. _chap-cli:

**********************
Command-line Arguments
**********************

Starting |vistrails| via the Command Line
=========================================

.. index:: command line arguments

|vistrails| supports a number of command-line arguments that let you modify certain attributes and behaviors of the program. When invoking |vistrails| from the command line, the arguments are placed after the "vistrails.py" filename. For example,

   ``python vistrails.py -n``

suppresses the |vistrails| splash screen. Table :ref:`table-batch-cli` contains a complete list of the command line switches supported by \vistrails. Each command line switch has both a short form and a long form. The two forms are logically equivalent, and which one you use is a matter of personal preference. The short form consists of a single minus sign "-" followed by a single letter. The longer form uses two minus signs "--" followed by a descriptive word. For example, the above command to suppress the splash screen could have been written as:

   ``python vistrails.py --nosplash``


In addition to the explicit switches listed in Table :ref:`table-batch-cli`, the |vistrails| command line also lets you indicate the filename of the vistrail you wish to open. For example, assuming your "examples" directory is one level above your current working directory, this is how you would tell |vistrails| to load the "lung.vt" example at startup:

   ``python vistrails.py ../examples/lung.vt``


Moreover, if you want |vistrails| to start on a *specific version* of the pipeline within the vistrail, you can indicate that version's tag name on the command line. The filename and version tag should be separated by a colon. For example, to start |vistrails| with the ``colormap`` version of the "lung.vt" vistrail, use:

   ``python vistrails.py ../examples/lung.vt:colormap``


In the event that the version you want to open contains a space in its tag name, simply surround the entire "filename:tag" pair in double quotes. For example:

   ``python vistrails.py "../examples/lung.vt:Axial View"``


You can also open up multiple vistrails at once by listing more than one vistrail file on the command line. This causes the vistrails to be opened in separate tabs, just as if you had opened them via the GUI. For example:

   ``python vistrails.py ../examples/lung.vt ../examples/head.vt``


You can specify version tags in conjunction with multiple filenames. Here is an example of an elaborate command-line invocation that opens two vistrails and sets each one to a specific version:

   ``python vistrails.py "../examples/lung.vt:Axial View" ../examples/head.vt:bone``



.. topic:: Note:

   As of this writing, the |vistrails| development team is refactoring the implementation of many of the command-line switches presented in Table :ref:`table-batch-cli`. As such, depending on your version of |vistrails|, the results you achieve may not match those described. For a list of known issues with the command line switches, please refer to the |vistrails| website.


.. _table-batch-cli:

.. csv-table:: Command line arguments supported by |vistrails|.
   :header: **Short form**, **Long form**, **Description**
   :widths: 10, 15, 30

   -h, :math:`--`\ help, Print a help message and exit.
   -S */path*, -\ -startup=\ */path*, Set user configuration directory (default is :math:`\sim`\ ``/.vistrails``)
   -?, , Print a help message and exit.
   -v, --version, Print version information and exit.
   -V *num*, --verbose=\ *num*, "Set verboseness level (0--2, default=0, higher means more verbose)."
   -b, --noninteractive, Run in non-interactive (batch) mode.
   -n, --nosplash, Do not display splash screen on startup.
   -c *num*, --cache=\ *num*, "Enable/disable caching (0 to disable, nonzero to enable. Default is enabled)."
   -m *num*, --movies=\ *num*, "Set automatic movie creation on spreadsheet (0 or 1, default=1). Set this to zero to work around VTK bug with offscreen renderer and OpenGL texture3D mappers."
   -s, --multiheads, Display the Builder and Spreadsheet on different screens (if available).
   -x, --maximized, Maximize Builder and Spreadsheet windows at startup.
   -l, --nologger, Disable logging.
   -d, --debugsignals, Debug Qt Signals.
   -a *params*, --parameters=\ *params*, Set workflow parameters (non-interactive mode only).
   -e *dir*, --dumpcells=\ *dir*, Set directory to dump spreadsheet cells before exiting (non-interactive mode only).
   -t *host*, --host=\ *host*, Set hostname or IP address of database server.
   -r *port*, --port=\ *port*, Set database port.
   -f *dbName*, --db=\ *dbName*, Set database name.
   -u *userName*, --user=\ *userName*, Set database username.

.. _sec-cli-db:

Passing Database Parameters on the Command Line
===============================================

As discussed in Chapter :ref:`chap-database`, |vistrails| can read and write vistrails stored in a relational database as well as in a filesystem. |vistrails| allows you to specify the name of the database server, the database name, the port number, and the username on the command line. This potentially saves you the trouble of filling out the same information on the database connection dialog. Note that, for security reasons, |vistrails| does not allow you to include a database password on the command line; you must still type your password into the database connection dialog when |vistrails| opens.

The last four rows of Table :ref:`table-batch-cli` show the command-line switches that pertain to database connectivity. Be advised that these switches were designed primarily for use by VTL files (see Section :ref:`sec-cli-vtl`) and as such, are not necessarily user-friendly. In particular, these switches are ignored unless you also specify the vistrail ID and version name on the command line. For example, to open the ``contour`` version of the the "spx" vistrail (whose ID is 5) from the database "vistrails" residing on the host "vistrails.sci.utah.edu" with a username of "vistrails":

   ``python vistrails.py -t vistrails.sci.utah.edu -f vistrails -u vistrails 5:contour``


Once |vistrails| opens, you will be prompted to enter the password. Upon successful authentication, the vistrail is loaded from the database and opened to the pipeline corresponding to the specified version.

.. _sec-cli-vtl:

Using "Vistrail Link" Files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As discussed in Chapter :ref:`chap-database`, one of the advantages of storing your vistrails on a database is that you can collaborate with others without having to pass around a .vt file or force all users to use a shared filesystem. A disadvantage is that you need to remember the parameters with which to connect to the database. Using a "Vistrail Link" (VTL) file reduces this inconvenience, and also eliminates the need to include the associated command-line switches to connect to the database.

A VTL is a very small text (XML) file that contains the parameters required to load a vistrail from a database. VTL files are intended for use with a |vistrails|-enabled wiki. You can open a VTL either by saving the file and passing its filename to the command line, or by configuring your web browser to do this for you. Here is the syntax for using a VTL file on the command line:

   ``python vistrails.py sample.vtl``


Internally, |vistrails| parses the VTL file and loads the vistrail from the database exactly as if you had included its full parameter list on the command line.

.. topic:: Note:

   VTL is a relatively new feature of |vistrails|, and as such is neither fully developed nor completedly documented. Please contact the |vistrails| development team with any bug reports and/or suggestions.

.. _sec-cli-batch:

Running |vistrails| in Batch Mode
=================================

.. index::
   single: batch mode
   single: non-interactive mode

Although |vistrails| is primarily intended to be run as an interactive, graphical client application, it also supports non-interactive use. |vistrails| can thus be invoked programmatically, \eg as part of a shell script. You can tell |vistrails| to start in non-interactive mode by using the "-b" or "--noninteractive" command line switch when launching \vistrails. [#]_

Running |vistrails| in non-interactive mode has little effect, however, without an additional command line argument indicating which vistrail to load. Since we are running |vistrails| as part of a batch process, it only makes sense to execute vistrails whose output is something tangible, such as a file. A vistrail whose only output is an interactive rendering in a ``VTKCell``, for instance, would not be well-suited for running in batch mode.

.. _fig-batch-version_tree:

.. figure:: figures/batch/offscreen_version_tree.png
   :align: center
   :width: 3in

   The different versions of the "offscreen.vt" vistrail offer various forms of output.

Consider the following example. The "offscreen.vt" vistrail (included in the "examples" directory) has a variety of output options, depending on which version you select in the ``History`` view (Figure :ref:`fig-batch-version_tree`). The version tagged ``only vtk`` displays its output as an interactive VTK rendering. The version tagged ``html`` creates a simple web page in the Spreadsheet. The ``offscreen`` version, however, outputs an image file named "image.png". Since its output (a file) can be easily accessed outside of |vistrails|, this version is an ideal candidate for running in batch mode.  To try it, invoke |vistrails| as shown, specifying both the name of the vistrail file and the desired version:

   ``python vistrails.py -b ../examples/offscreen.vt:offscreen``


As you would expect, this command runs to completion without opening any windows. Instead, it silently loads the requested pipeline, executes it, and closes.
Assuming it ran correctly, this pipeline should have created a file named "image.png" in the current directory.  When you view this file, it should resemble the picture in Figure :ref:`fig-batch-image_png`.

.. _fig-batch-image_png:

.. figure:: figures/batch/offscreen_output.png
   :align: center
   :width: 2in

   ``offscreen`` version of "offscreen.vt" in batch mode produces an image named "image.png".

.. %TODO should we cover aliases here?

Accessing a Database in Batch Mode
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As discussed in Section :ref:`sec-cli-db`, you can specify most of the parameters of your database connection on the command line, but the password must be entered through the GUI. This poses a problem for running |vistrails| in non-interactive mode, since no database connection dialog will be opened. If your batch process needs to access vistrails stored on a database, the current workaround is to create a special account on the database (probably one with read-only access) that does *not* require a password, and use this account for connecting to the database in batch mode.

.. rubric:: Footnotes
.. [#] The parameter "-b" stands for "batch." In this chapter, we use the terms "batch mode" and "non-interactive mode" synonymously.