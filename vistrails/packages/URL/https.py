# Python's handling of certificate verification is irresponsible and wrong.
# Having to include the code below to get what should be the only acceptable
# default behavior is a shame

# Code from https://gist.github.com/schlamar/2993700

import httplib
import urllib2
import ssl

import certifi
from backports.ssl_match_hostname import match_hostname


class CertValidatingHTTPSConnection(httplib.HTTPConnection):
    default_port = httplib.HTTPS_PORT

    def __init__(self, host, port=None, key_file=None, cert_file=None,
                             ca_certs=None, strict=None, **kwargs):
        httplib.HTTPConnection.__init__(self, host, port, strict, **kwargs)
        self.key_file = key_file
        self.cert_file = cert_file
        self.ca_certs = ca_certs
        if self.ca_certs:
            self.cert_reqs = ssl.CERT_REQUIRED
        else:
            self.cert_reqs = ssl.CERT_NONE

    def connect(self):
        httplib.HTTPConnection.connect(self)
        self.sock = ssl.wrap_socket(self.sock, keyfile=self.key_file,
                                    certfile=self.cert_file,
                                    cert_reqs=self.cert_reqs,
                                    ca_certs=self.ca_certs)
        if self.cert_reqs & ssl.CERT_REQUIRED:
            cert = self.sock.getpeercert()
            hostname = self.host.split(':', 0)[0]
            match_hostname(cert, hostname)


class VerifiedHTTPSHandler(urllib2.HTTPSHandler):
    def __init__(self, **kwargs):
        urllib2.HTTPSHandler.__init__(self)
        self._connection_args = kwargs

    def https_open(self, req):
        def http_class_wrapper(host, **kwargs):
            full_kwargs = dict(self._connection_args)
            full_kwargs.update(kwargs)
            return CertValidatingHTTPSConnection(host, **full_kwargs)

        return self.do_open(http_class_wrapper, req)


https_handler = VerifiedHTTPSHandler(ca_certs=certifi.where())


def build_opener(*handlers, **kwargs):
    # Keyword-only argument 'insecure'
    insecure = kwargs.pop('insecure', False)
    if kwargs:
        raise TypeError("build_opener() got unexpected keyword argument %r" %
                        next(iter(kwargs)))

    if not insecure:
        handlers = handlers + (https_handler,)
    handlers = handlers + (urllib2.ProxyHandler(),)
    return urllib2.build_opener(*handlers)
