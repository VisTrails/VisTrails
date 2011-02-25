.. _part2:

#############################
Learning VisTrails By Example
#############################

.. _chap-creating:

********************************
Creating and Modifying Workflows
********************************

.. index:: builder

Working with Modules
====================

.. index:: modules

In VisTrails, modules are represented by a rectangle in the
``Pipeline`` view of the Builder.  The name of the module is
shown in bold letters in the middle of the rectangle.  The input and
output ports for the module are denoted by small squares on the top
and bottom of the module, respectively.  Modules are connected
together to define the dataflow using curved black lines that go from
output to input ports between modules.  Each module may have also have
adjustable parameters that can be viewed when a module is selected.
Modules can be connected, disconnected, added, and deleted from a
workflow.