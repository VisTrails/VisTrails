.. _chap-parallelization:

******************************************
Using parallelization in VisTrails modules
******************************************

This chapters presents different techniques for using parallelization inside
the code of your |vistrails| modules.

Threading
=========

|vistrails| is single-threaded: the modules are executed one after the other,
and while you are free to use threads in your module's ``compute()`` method,
you should not interact with |vistrails| from other threads.

Note that because of the restrictions of the CPython interpreter, you might not
improve performance by using this type of parallelization: the interpreter has
a lock, preventing two threads from executing Python code at the same time. If
you are not already, consider using packages such as NumPy_ which provides
efficient numerical functions implemented in C (and parallelizable).

.. _NumPy: http://www.numpy.org/

Multiprocessing
===============

Use of the ``multiprocessing`` package introduced with Python 2.6 is possible
in |vistrails|. This is generally the preferred way of performing multiple
computational tasks in parallel in Python, and will effectively leverage
multiple cores; please refer to the `official documentation
<http://docs.python.org/2/library/multiprocessing.html>`_ for more details.

IPython
=======

You can access IPython clusters through the :ref:`Parallel Flow
<chap-parallelflow>` package, via the provided API. Simply declare it in your
package's dependencies, and import ``vistrails.packages.parallelflow.api``.
This module provides the following:

``get_client(ask=True) -> IPython.parallel.Client or None``
    Low-level function giving you a Client connected to the cluster, or None.
    If not connected to a cluster or if no engines are available, the ``ask``
    parameter controllers whether to offer the user to take automatic action.

``direct_view(ask=True) -> IPython.parallel.DirectView or None``
    Gives you a view on the engines of the cluster, which you can use to submit
    tasks. This is currently equivalent to calling ``get_client()[:]``.

    You should probably use ``load_balanced_view()`` instead.

``load_balanced_view(ask=True) -> IPython.parallel.LoadBalancedView or None``
    Gives you a load-balanced view on the engines of the cluster, which you can *
    use to submit tasks. It is the preferred way of submitting tasks. This is
    currently equivalent to calling ``get_client().load_balanced_view()``.
