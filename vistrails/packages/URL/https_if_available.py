import urllib2

from vistrails.core.bundles.pyimport import py_import
from vistrails.core import debug


try:
    py_import('certifi', {
            'pip': 'certifi'})
    py_import('backports.ssl_match_hostname', {
            'pip': 'backports.ssl_match_hostname',
            'linux-fedora': 'python-backports-ssl_match_hostname'})
except ImportError:
    def build_opener(*args, **kwargs):
        insecure = kwargs.pop('insecure', False)
        if not insecure:
            debug.warning("Unable to use secure SSL requests -- please "
                          "install certifi and ssl_match_hostname")
        return urllib2.build_opener(*args, **kwargs)
else:
    from .https import *
