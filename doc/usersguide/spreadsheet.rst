.. _chap-spreadsheet:

***********
Spreadsheet
***********

.. index:: spreadsheet

.. _fig-spreadsheet:

.. figure:: figures/spreadsheet/spreadsheet.png
   :width: 5in
   :align: center

   The VisTrails Spreadsheet.

As described in Section :ref:`sec-versions-diff`, |vistrails| has a
powerful built-in mechanism to compare workflows.  However, this
comparison shows changes in the *design* of the workflows, and we
are often also interested in differences in the *results* of
workflows.  The |vistrails| Spreadsheet provides a simple, flexible,
and extensible interface to display and compare results from
workflows.  Coupled with the version differences, users can explore
the evolution of their workflows.

The Spreadsheet package is installed with |vistrails| by default, and
it can display a variety of data ranging from VTK renderings to
webpages without additional configuration.

..  %% TODO add this sentence back in once the Custom Cell chapter is complete!
..  %In addition to the included types of viewers, users can create and register additional viewers using customized cell widgets (see Chapter :ref:`chap-custom_cells`).

.. _sec-spreadsheet-layout:

The Spreadsheet Layout
======================

.. index::
   pair: spreadsheet; layout
   triple: spreadsheet; sheets; adding
   triple: spreadsheet; sheets; deleting

As should be expected, the |vistrails| Spreadsheet consists of one or more sheets, each with a customizable number of rows and columns.  Users can add additional sheets either by clicking the ``New Sheet`` button in the ``Spreadsheet`` toolbar or choosing the menu item with the same name from the ``Main`` menu.  Similarly, a sheet can be deleted by clicking the red 'X' button in the lower-right corner or choosing the ``Delete Sheet`` menu item.

.. index::
   pair: spreadsheet; rows
   pair: spreadsheet; columns
   pair: spreadsheet; cells

To modify the layout for the active sheet, you can change both the number of rows and columns and resize individual cells.  The number of rows is controlled by the left spinner in the toolbar and the number of columns by the right spinner.  To resize a given row or column, click and drag on one edge of the row or column header.  In addition, you can resize an individual cell by moving the mouse to lower-right corner of the cell until the cursor changes and clicking and dragging to the desired size (see
Figure :ref:`fig-cell_states`\(d\)).  Note that this will affect the entire
layout, compressing or expanding rows and columns to generate or fill
space for the resized cell.

Using the Spreadsheet
=====================

.. index:: 
   pair: spreadsheet; modes

Currently, there are two operating modes in the Spreadsheet: Interactive Mode and Editing Mode.  Interactive Mode allows users to view and interact with the spreadsheet cells, while Editing Mode provides operations for manipulating cells.  The modes can be toggled via the ``View`` menu or their corresponding keyboard shortcuts ('Ctrl-Shift-I') and 'Ctrl-Shift-E').

Interactive Mode
^^^^^^^^^^^^^^^^

.. index::
  triple: spreadsheet; modes; interactive

In Interactive Mode, users can interact directly with the viewer for an individual cell, interact with multiple cells at once, or change the layout of the sheet.  Because cells can differ in their contents, interacting with a cell changes based on the type of data displayed.  For example, in a cell displaying VTK data (a ``VTKCell``), a user can rotate, pan, and zoom in or out using the mouse.

.. _fig-cell_states:

.. figure:: figures/spreadsheet/cell_states.png
   :width: 6.5in
   :align: center

   Different states of a spreadsheet cell. \(a\) inactive and unselected, \(b\) active and unselected, \(c\) active and selected, \(d\) an active cell with its toolbar and resizer.

.. index::
   pair: spreadsheet; cells

In a sheet, a cell can be both *active* and *selected*.  There can only be one active cell, and that cell is highlighted by a yellow or grey border.  Clicking on any cell will make it active.  This active cell will respond to keyboard shortcuts as well as mouse input.  In constrast to the active cell, one or more cells can be selected, and the active cell need not be selected.  To select multiple cells, either click on a row or column heading to toggle selection or 'Ctrl'-click to add or remove a cell from the group of selected cells.  The backgrounds of selected cells are highlighted using a platform-dependent selection color.  See Figure :ref:`fig-cell_states` for examples of the different cell states.

Depending on the cell type, additional controls may appear in the
toolbar when a cell is activated. These controls affect only the
active cell, and change for different cell types. As shown by
Figure :ref:`fig-cell_states`\(d\), a cell optimized for rendering 2D images (a ``ImageViewerCell``) adds
controls for resizing, flipping, and rotating the image in the active
cell.

Arranging Cells
^^^^^^^^^^^^^^^

As described in Section :ref:`sec-spreadsheet-layout`, cells can be
resized by either resizing rows, columns, or an individual cell.  In
addition to resizing, a row or column can be moved by clicking on its
header and dragging it along the header bar to the desired position.
See Section :ref:`sec-spreadsheet-editing` for instructions on moving a
specific cell to a different location.

.. _fig-spreadsheet_sync:

.. figure:: figures/spreadsheet/spreadsheet_sync.png
   :width: 3in
   :align: center

   When selecting all cells, interacting with one VTK cell \(A1\) causes the other two VTK cells \(B1 and B2\) to change their camera to the same position.

Synchronizing Cells
^^^^^^^^^^^^^^^^^^^

Often, when a group of cells all display results from similar
workflows, it is useful to interact with all of these cells at the
same time.  For example, for a group of ``VTKCell``s, it is
instructive to rotate or zoom in on multiple cells at once and compare
the results.  For this reason, if a group of cells is selected, mouse
and keyboard events for a single cell of the selection are propogated
to each of the other selected cells.  Currently, this feature only
works for ``VTKCell``s, but we plan to add this to other
cell types as well.  An example of this functionality is shown in
Figure :ref:`fig-spreadsheet_sync`.

.. _sec-spreadsheet-editing:

Editing Mode
^^^^^^^^^^^^

.. _fig-editing_mode:

.. figure:: figures/spreadsheet/editing_mode.png
   :width: 6.5in
   :align: center

   The spreadsheet in Editing Mode. \(a\) All cell widgets are replaced with an information widget \(b\) Two cells are swapped after drag and drop the 'Move' icon from A1 to B1.

.. index::
   triple: spreadsheet; modes; editing

Recall that Editing Mode can be entered either by accessing the ``View`` menu or by keying 'Ctrl-Shift-E'. Editing Mode provides more
operations to layout and organize spreadsheet cells.  In this mode,
the view for each cell is frozen and overlaid with additional
information and controls (see Figure :ref:`fig-editing_mode`).  The top
of the overlay displays information about which vistrail, version, and
type of execution were used to generate the cell.  The bottom piece of
the overlay contains a variety of controls to manipulate the cell
depending on the its state.

Cells can be moved or copied to different locations on the spreadsheet
by clicking and dragging the appropriate icons (``Move`` or
``Copy``) for a given cell to its desired location.  To move
a cell to a location on a different sheet, drag the icon over the
target sheet tab to bring that sheet into focus first and then drop it
at the desired location. If you move a cell to an already-occupied
cell, the contents of the two cells will be swapped.  See
Figure :ref:`fig-editing_mode` for an example of swapping two cells.

Clicking the ``Locate Version`` icon will highlight the node in the version tree (in the ``History`` view) from which the visualization in that cell was generated. The next two icons, ``Create Analogy`` and ``Apply Analogy``, help with creating visualizations by analogy. Please refer to Chapter :ref:`chap-analogies` for information about this feature.

If a cell was generated via parameter exploration (see
Chapter :ref:`chap-paramexploration`), the ``Create Version``
button will be available to save the workflow that generated the
result back to the vistrail.  Clicking this button modifies the
vistrail from which the cell was generated by adding a new version
with the designated parameter settings.  Thus, if you go back to the
``History`` mode of the |vistrails| Builder for that
vistrail, you will find that a new version has been added to the
version tree.

Saving a Spreadsheet
====================

.. warning::

   This is currently an experimental feature and as such is not robust.  If you rename or move the vistrails used by the saved spreadsheet, the spreadsheet will not load correctly.

.. index::
   pair: spreadsheet; saving

Because spreadsheets can include several workflow executions or parameter explorations, it is helpful to be
able to save the layout of the current spreadsheet.  To save a
spreadsheet, simply choose the ``Save`` menu item from the
``Main`` menu, and complete the dialog.  After saving a
spreadsheet, you can reopen it using the ``Open`` menu item.

.. index:: spreadsheet
