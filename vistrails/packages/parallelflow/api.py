"""Provides access to IPython to packages.

get_client() returns the Client object, from which you can construct a view.
This may return None if no client is available, if the user cancels, etc, in
which case you can raise an exception.

direct_view() returns a DirectView of the whole cluster. It is equivalent to
get_client()[:], with the difference that it will prompt the user to create new
engines if none are started.

load_balanced_view() returns a LoadBalancedView of the cluster. It is
equivalent to get_client().load_balanced_view(), with the difference that it
will prompt the user to create new engines if none are started.

parallel_map() might use IPython's parallel map_sync(), or the standard map()
function if IPython cannot be used.
If the 'ipython' keyword argument is True, the function will return an
additional boolean indicating whether this was computed through IPython (True)
or with the default map() function (False).

All of these functions have an 'ask' parameter, that indicates whether to
prompt the user to start a cluster if none is available. It is True by default
(except for parallel_map).
"""


__all__ = ['get_client', 'direct_view', 'load_balanced_view', 'parallel_map']


def get_client(ask=True):
    """Returns a Client object, from which you can construct a view.

    This may return None if no client is available, if the user cancels, etc.
    In this case, you might want to raise a ModuleError.
    """
    from engine_manager import EngineManager

    c = EngineManager.ensure_controller(connect_only=not ask)
    if c is not None and ask and not c.ids:
        EngineManager.start_engines(
                prompt="A module requested an IPython cluster, but no engines "
                       "are started. Do you want to start some?")
    if c is not None and c.ids:
        return c
    else:
        return None


def direct_view(ask=True):
    """Returns a DirectView of the whole cluster.

    This is equivalent to get_client()[:], with the difference that it will
    prompt the user to create new engines if none are started.
    """
    c = get_client()
    if c is not None:
        return c[:]
    else:
        return None


def load_balanced_view(ask=True):
    """Returns a LoadBalancedView of the cluster.

    This is equivalent to get_client().load_balanced_view(), with the
    difference that it will prompt the user to create new engines if none are
    started.
    """
    c = get_client()
    if c is not None:
        return c.load_balanced_view()
    else:
        return None


def parallel_map(function, *args, **kwargs):
    """Wrapper around IPython's map_sync() that defaults to map().

    This might use IPython's parallel map_sync(), or the standard map()
    function if IPython cannot be used.

    If the 'ask' keyword argument is true, the user will be prompted to start
    IPython engines, but the function will still default to map() if the user
    cancels.
    If the 'ipython' keyword argument is True, the function will return an
    additional boolean indicating whether this was computed through IPython
    (True) or with the default map() function (False).
    """
    say_ipython = kwargs.pop('ipython', False)
    ask = kwargs.pop('ask', False)
    if kwargs:
        raise TypeError("map() got unexpected keyword arguments")

    try:
        import IPython.parallel
    except ImportError:
        result, ipython = map(function, *args), False
    else:
        from engine_manager import EngineManager
        c = EngineManager.ensure_controller(connect_only=not ask)
        if c is not None and not c.ids:
            EngineManager.start_engines(
                    prompt="A module is performing a parallelizable "
                    "operation, however no IPython engines are running. Do "
                    "you want to start some?")

        if c is None or not c.ids:
            result, ipython = map(function, *args), False
        else:
            ldview = c.load_balanced_view()
            result, ipython = ldview.map_sync(function, *args), True

    if say_ipython:
        return result, ipython
    else:
        return result
