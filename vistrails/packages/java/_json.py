has_fast_json = False
try:
    import simplejson as json
    try:
        import simplejson.speedups
        has_fast_json = True
    except ImportError:
        pass
except ImportError:
    import json


__all__ = ['has_fast_json', 'json']
