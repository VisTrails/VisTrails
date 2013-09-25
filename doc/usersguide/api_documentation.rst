.. _chap-api-documentation:

VisTrails API Documentation
***************************

Module Definition
=================

Module
^^^^^^

.. autoclass:: vistrails.core.modules.vistrails_module.Module
    :members: set_output, get_input, has_input, check_input,
       get_input_list, force_get_input_list, force_get_input, annotate
    :member-order: bysource

ModuleSettings
^^^^^^^^^^^^^^

.. autoclass:: vistrails.core.modules.config.ModuleSettings

Port Specification
==================

InputPort
^^^^^^^^^

.. autoclass:: vistrails.core.modules.config.InputPort

OutputPort
^^^^^^^^^^

.. autoclass:: vistrails.core.modules.config.OutputPort

CompoundInputPort
^^^^^^^^^^^^^^^^^

.. autoclass:: vistrails.core.modules.config.CompoundInputPort

CompoundOutputPort
^^^^^^^^^^^^^^^^^^

.. autoclass:: vistrails.core.modules.config.CompoundOutputPort

InputPortItem
^^^^^^^^^^^^^

.. autoclass:: vistrails.core.modules.config.InputPortItem

OutputPortItem
^^^^^^^^^^^^^^

.. autoclass:: vistrails.core.modules.config.OutputPortItem

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
