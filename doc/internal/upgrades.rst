..  _upgrades:

Pipeline upgrades
*****************

The upgrade mechanism allows VisTrails to deal with workflow written with older versions of packages.

Each package has, in addition to its identifier, a version number. The package's version number is written alongside the package and module names in serialized workflows; when it is loaded, the package will have a chance to replace this old module, else VisTrails will just bump the version number of the module. If the module has changed, and the connections that appear in the workflow don't match the port names or signature that the current package declares, the pipeline will be invalid and the user will have to fix it manually.

A package can upgrade older modules using a function `handle_module_upgrade_request()` in its ``init`` module. That function takes the controller, module id and current pipeline, and performs actions to fix that module. Packages usually use :class:`~vistrails.core.upgradeworkflow.UpgradeWorkflowHandler` to do this, for example by passing a remap object to :func:`~vistrails.core.upgradeworkflow.UpgradeWorkflowHandler.remap_module`.

..  autoclass:: vistrails.core.upgradeworkflow.UpgradeWorkflowHandler
    :members:

The controller triggers the upgrade of a version when it gets selected. Since each version has to be upgraded separately, the upgrade will be created (so the pipeline can be shown) but will not be flushed to the vistrail unless another change is made (based on that upgraded version) or the pipeline is executed.

..  todo::

    There are currently some issues with how the controller keeps these unflushed upgrades.

    :issue:`907`

..  todo::

    Upgrades should be triggered when necessary during diff, query, subworkflow update, parameter exploration.

    :issue:`695,1054,1071,1087`
