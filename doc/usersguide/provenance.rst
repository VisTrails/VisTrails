.. _chap-provenance_browser:

******************
Provenance Browser
******************

The ``Provenance Browser`` allows you to browse through all executions performed on a vistrail.  When the ``Provenance`` mode is selected, executions are displayed in the ``Log Details`` panel on the right (see figure :ref:`Provenance Browser <fig-browser>`).  Selecting an execution from the ``Log Details`` panel will display the pipeline with modules colored according to their execution results.  Alternatively, this pipeline is displayed by double-clicking on the execution in the ``Workspace`` panel.  Executions in the ``Workspace`` panel are displayed under the version to which they belong and are made visible or invisible by toggling the panel's ``executions`` button.  Notice that only executions that belong to tagged versions are displayed in the ``Workspace``, but all executions are displayed in the ``Log Details``.

.. _fig-browser:

.. figure:: figures/provenance/browser.png
   :width: 100%

   Provenance Browser - *Left:* The ``Workspace`` has a button to enable/disable executions.  When enabled, executions of each tagged version in the vistrail will appear when each respective version is expanded.  *Right:* The ``Provenance Browser`` keeps track of all executions whether they belong to tagged versions or not.  When selected, the color coded execution pipeline will appear in the center panel.