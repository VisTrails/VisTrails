.. _chap-persistence:

*************************
Persistence in VisTrails
*************************

.. index::persistence

The ``Persistence`` package in Vistrails helps improve reproducibility by associating versions of data files with their provenance, and minimize the need to rerun lengthy executions by keeping intermediate persistent files. 
Although, we will focus primarily on the use of persistent files, persistent directories are used in the same manner.  The difference is that a persistent directory deals with multiple files within a directory rather than a single file.

Getting Started With Persistence
================================

To begin, notice that there are three persistent file/directory types: input, intermediate, and output. It is helpful to understand the differences among these files as well as the differences between these files and regular files.

Input Files
^^^^^^^^^^^




How do I use the output of one workflow as the input for another using the persistence package?
You need to configure the persistence modules using the module's configuration dialog. After adding a PersistentOutputFile to the workflow, click on the triangle in the upper-right corner of the PersistentOutputFile, and select "Edit Configuration" from the menu that appears. In this dialog, select "Create New Reference" and give the reference a name (and any space-delimited tags). Upon running that workflow, the data will be written to the persistent store. In the second workflow where you wish to use that file, add a PersistentInputFile and go to its configuration dialog in the same manner as with the output file. In that dialog, select "Use Existing Reference" and select the data that you just added in the first workflow in the list of files below. Now, when you run that workflow, it will grab the data from the persistent store.

Here is an example: offscreen_persistent.vt. Run the "persistent offscreen" workflow first, and then run the "display persistent output" to use the output of the first workflow as the input for the second.

1. captures versions of the data (and workflows and inputs).
2. strong link - links workflow to data - derived from file content, workflow, and parameters.
3. persistent cache of intermediate and final results
4. signatures of workflows are used to identify intermediate and output data, content hashing it identify input data
5. New versions of output files are created by default, but users can change this behavior to version their outputs.
6. Output files and input files can either be saved to a local file, or the version store.
7. Contents of intermediate files are used in further calculations.
8. Intermediate files do not need to be annotated or named
9. What if it takes too much space?  Deleting/managing files.
10.  content hash and signature will be the same for similar files.§

Deleting and Managing Files
===========================
We are currently working on support for deleting persistent files via the VisTrails interface.  Files are stored in the ``.vistrails/persistent_files`` directory.