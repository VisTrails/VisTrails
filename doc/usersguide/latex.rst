***********************************
Embedding VisTrails Files Via Latex
***********************************

.. index:
   pair: embed; latex

The VisTrails Latex extension allows you to embed a result from a VisTrails file in a Latex document.  Images to be included in the Latex document will be generated through VisTrails and can be linked to the VisTrails file and version from which it was generated.  In other words, Latex call VisTrails to generate an image for a resulting PDF document.  The resulting image can be set up so, when clicked, the generating VisTrails file will be opened in Vistrails.

Latex Setup and Commands
========================

To use the Latex extension, copy vistrails.sty and includevistrail.py from the extensions/latex directory to the same directory as your .tex files.  Then, add the following line to the beginning of the latex file:

``\usepackage{vistrails}``

By default, vistrails will be executed at www.vistrails.org and the images
downloaded to your hard drive. 

If you want to use a different server, add the following to your tex file:

``\renewcommand{\vistrailspath}{http://yourwebserver.somethingelse/run_vistrails.php}``

Or, if you want to run a local copy of vistrails:

``\renewcommand{\vistrailspath}{/path/to/vistrails.py}``

To embed the links in the generated images, use 

``\renewcommand{\vistrailsdownload}{http://yourwebserver.somethingelse/download.php}``

or just set to empty to make the images not clickable:

``\renewcommand{\vistrailsdownload}{}``

This extension uses python. If you don't have python on your path, use this 
to set the python interpreter:

``\renewcommand{\vistrailspythonpath}{python}``

Including VisTrails Results in Latex
====================================

To include VisTrails Results in a Latex file:

  * Select the ``History`` view.  
  * Ensure that a version is selected.
  * Press the ``Embed`` button at the bottom of the Properties Panel.  This will launch a dialog with embedding options (see Figure :ref:`fig-configure-embedding`).  
  * Select the result that you would like to display.  The choices are: workflow results, workflow graph, and history tree graph.
  * Select ``Latex``.
  * You should then choose from a number of "Embed" and "Download" options which will be explained in the table below.
  * Select "Copy to Clipboard"
  * Paste clipboard contents into you Latex document 

.. tabularcolumns:: |p{2.8cm}|p{3.0cm}|p{7.5cm}|
   
.. _table-options:

.. only:: html

   Configuration Options

   +-----------------------+-----------------------+--------------------------------------------------------------------------+ 
   | Option                | Latex Flag            | Description                                                              |
   +=======================+=======================+==========================================================================+
   | | Workflow Results    | version=<...>         | Show the results of the specified version.                               |
   +-----------------------+-----------------------+--------------------------------------------------------------------------+
   | Workflow Graph        | | version=<...>       | Show the workflow instead of the results.                                |
   |                       | | showworkflow        |                                                                          |
   +-----------------------+-----------------------+--------------------------------------------------------------------------+
   | | History Tree Graph  | showtree              | Show the version tree instead of the results.                            |
   +-----------------------+-----------------------+--------------------------------------------------------------------------+
   | As PDF                | | pdf                 | Download images as pdf files.                                            |
   +-----------------------+-----------------------+--------------------------------------------------------------------------+
   | Smart Tag             | tag=<...>             | | Allows you to include a version's tag.  If a tag is provided, version  |
   |                       |                       |   can be omitted and buildalways is implicit.                            |
   +-----------------------+-----------------------+--------------------------------------------------------------------------+
   | Cache Images          | | buildalways         | | When caching desired, the buildalways flag should not be included.     |
   |                       | | (do not include     |   If it is included, VisTrails will be called regardless of whether or   |
   |                       |   for caching)        |   not it has been called for the same host, db, version, port and vt_id. |
   +-----------------------+-----------------------+--------------------------------------------------------------------------+
   | Include .vtl          | | getvtl              | Causes the .vtl file to be downloaded.                                   |
   +-----------------------+-----------------------+--------------------------------------------------------------------------+
   | | Include Workflow    | embedworkflow         |                                                                          |
   +-----------------------+-----------------------+--------------------------------------------------------------------------+
   | | Execute Workflow    | execute               | Will cause the workflow to be executed when it is opened.                |
   +-----------------------+-----------------------+--------------------------------------------------------------------------+
   | | Include Full Tree   | includefulltree       |                                                                          |
   +-----------------------+-----------------------+--------------------------------------------------------------------------+
   | | Show Spreadsheet    | showspreadsheetonly   | Will initially only show the spreadsheet.                                |
   |   Only                |                       |                                                                          |
   +-----------------------+-----------------------+--------------------------------------------------------------------------+

.. only:: latex

   .. csv-table:: Configuration Options
      :header: **Option**, **Latex Flag**, **Description**

      Workflow Results, version=<...>, "Show the results of the specified version."
      , ,
      Workflow Graph, version=<...>, "Show the workflow instead of the results."
      ,showworkflow,
      , ,
      History Tree Graph, showtree, "Show the version tree instead of the results."
      , ,
      As PDF, pdf, "Download images as pdf files."
      , ,
      Smart Tag, tag=<...>, "Allows you to include a version's tag.  If a tag is provided, version can be omitted and buildalways is implicit."
      , ,
      Cache Images, buildalways (do not include), "When caching desired, the buildalways flag should not be included.  If it is included, VisTrails will be called regardless of whether or not it has been called for the same host, db, version, port and vt_id."
      , ,
      Include .vtl, getvtl, "Causes the .vtl file to be downloaded."
      , ,
      Include Workflow, embedworkflow,
      , ,
      Execute Workflow, execute, "Will cause the workflow to be executed when it is opened."
      , ,
      Include Full Tree, includefulltree,
      , ,
      Show Spreadsheet Only, showspreadsheetonly, "Will initially only show the spreadsheet."

|

.. _fig-configure-embedding:

.. figure:: figures/latex/embedding.png
   :align: center

   Embedding Options

Example
^^^^^^^

The following is an example command for including a VisTrails image in Latex:

| ``\vistrails[host=vistrails.sci.utah.edu,``
| ``db=vistrails,``
| ``version=<version_number>,``
| ``vtid=<vistrails_id>,``
| ``tag=<tag>``
| ``port=3306,``
| ``buildalways,`` 
| ``execute,``
| ``showspreadsheetonly,`` 
| ``pdf,`` 
| ``showworkflow,`` 
| ``showtree,`` 
| ``getvtl,`` 
| ``]{width=0.45\linewidth}``

Additional Notes
^^^^^^^^^^^^^^^^
 
The default value for port is 3306. 

The options inside { }  are the options you would give to 
\includegraphics{} command.

After running at least once, VisTrails will cache the images and latex 
instructions. 
The latex code will be in the "cached" folder and the images in 
vistrails_images.

If you set the \vistrailspythonpath to a invalid path VisTrails will use 
the cached files.

The option -shell-escape needs to be activated on the latex command line:

pdflatex -shell-escape example.tex

Vistrails will create in the current directory a directory called 
vistrails_images/host_db_vtid_version with the png files generated by 
the spreadsheet.

See example.tex in the extensions/latex directory for a complete example of usage.


