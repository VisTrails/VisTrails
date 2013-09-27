.. _chap-api-documentation:

VisTrails API Documentation
***************************

Module Definition
=================

Module
^^^^^^

.. py:module:: vistrails.core.modules.vistrails_module

.. autoclass:: vistrails.core.modules.vistrails_module.Module
   :members: compute, set_output, get_input, has_input, check_input,
	     get_input_list, force_get_input_list, force_get_input, annotate
   :member-order: bysource

   .. py:attribute:: _input_ports

        Class attribute that stores the list of input ports for the module.  May include instances of :py:class:`~vistrails.core.modules.config.InputPort` and :py:class:`.CompoundInputPort`.

   .. py:attribute:: _output_ports
 
        Class attribute that defines the list of output ports for the module.  May include instances of :py:class:`~vistrails.core.modules.config.OutputPort` and :py:class:`.CompoundOutputPort`.

   .. py:attribute:: _settings

        Class attribute that stores a :py:class:`.ModuleSettings` object that controls appearance, configuration widgets, and other module settings.

ModuleError
^^^^^^^^^^^

.. autoclass:: vistrails.core.modules.vistrails_module.ModuleError

ModuleSettings
^^^^^^^^^^^^^^

.. py:module:: vistrails.core.modules.config

.. autoclass:: vistrails.core.modules.config.ModuleSettings

Port Specification
==================

InputPort (IPort)
^^^^^^^^^^^^^^^^^

.. autoclass:: vistrails.core.modules.config.InputPort

.. py:class:: vistrails.core.modules.config.IPort

    Synonym for :py:class:`~vistrails.core.modules.config.InputPort`


OutputPort (OPort)
^^^^^^^^^^^^^^^^^^

.. autoclass:: vistrails.core.modules.config.OutputPort

.. py:class:: vistrails.core.modules.config.OPort

    Synonym for :py:class:`~vistrails.core.modules.config.OutputPort`


CompoundInputPort (CIPort)
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: vistrails.core.modules.config.CompoundInputPort

.. py:class:: vistrails.core.modules.config.CIPort

    Synonym for :py:class:`~vistrails.core.modules.config.CompoundInputPort`

CompoundOutputPort (COPort)
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: vistrails.core.modules.config.CompoundOutputPort

.. py:class:: vistrails.core.modules.config.COPort

    Synonym for :py:class:`~vistrails.core.modules.config.CompundOutputPort`

InputPortItem (IPItem)
^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: vistrails.core.modules.config.InputPortItem

.. py:class:: vistrails.core.modules.config.IPItem

    Synonym for :py:class:`~vistrails.core.modules.config.InputPortItem`

OutputPortItem (OPItem)
^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: vistrails.core.modules.config.OutputPortItem

.. py:class:: vistrails.core.modules.config.OPItem

    Synonym for :py:class:`~vistrails.core.modules.config.OutputPortItem`

Parameter Widget Configuration
==============================

ConstantWidgetConfig
^^^^^^^^^^^^^^^^^^^^

.. autoclass:: vistrails.core.modules.config.ConstantWidgetConfig

QueryWidgetConfig
^^^^^^^^^^^^^^^^^

.. autoclass:: vistrails.core.modules.config.QueryWidgetConfig

ParamExpWidgetConfig
^^^^^^^^^^^^^^^^^^^^

.. autoclass:: vistrails.core.modules.config.ParamExpWidgetConfig
