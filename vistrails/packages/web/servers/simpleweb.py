import BaseHTTPServer
import os
import socket
import threading

from vistrails.core import debug

from .. import configuration
from ..common import finalizer, random_strings


class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    """The RequestHandler class for HTTPServer.

    Just finds the right prefix and forwards it the request.
    """
    def log_message(self, format, *args):
        debug.debug("web - %s" % (format % args))

    def do_GET(self):
        server = WebServer._server
        if self.path == '/favicon.ico':
            self.send_response(200)
            self.send_header('Content-type', 'image/x-icon')
            self.end_headers()
            with open(os.path.join(os.path.dirname(__file__),
                                   '../vistrails_favicon.ico'), 'rb') as fp:
                chunk = fp.read(4096)
                if chunk:
                    self.wfile.write(chunk)
                    while len(chunk) == 4096:
                        chunk = fp.read(4096)
                        if chunk:
                            self.wfile.write(chunk)
            return
        code, headers, contents = 500, None, None
        try:
            prefix_name = self.path.split('/', 2)[1]
            prefix = server._prefixes[prefix_name]
        except KeyError:
            code, headers, contents = (404, {'Content-type': 'text/plain'},
                                       "Invalid prefix\n")
        else:
            code, headers, contents = prefix.get(
                    self.path[len(prefix_name) + 2:])

        if contents is None:
            self.send_error(code)
        else:
            self.send_response(code)
            if headers is None:
                headers = {}
            header_keys = set(key.lower() for key in headers)
            for key, value in headers.iteritems():
                self.send_header(key, value)
            self.end_headers()
            if isinstance(contents, bytes):
                self.wfile.write(contents)
            else:
                for chunk in contents:
                    self.wfile.write(chunk)


class Prefix(object):
    """Objects returned by `get_server()`, with which you register resources.
    """
    def __init__(self, prefix):
        self.prefix = prefix
        self.address = self._server.address + prefix + '/'
        self._resources = {}

    @property
    def _server(self):
        return WebServer._server

    def get(self, uri):
        try:
            res = self._resources[uri]
        except KeyError:
            type_, args = None, ()
        else:
            type_, args = res[0], res[1:]
        if type_ == 'file':
            filename, ctype = args
            with open(filename, 'rb') as fp:
                blob = fp.read()
        elif type_ == 'blob':
            blob, ctype = args
        else:
            return 404, None, None
        headers = {}
        if ctype is not None:
            headers['Content-type'] = ctype
        return 200, headers, blob

    def add_file(self, uri, filename, content_type=None):
        if uri.startswith('/'):
            uri = uri[1:]
        self._resources[uri] = ('file', filename, content_type)

    def add_resource(self, uri, blob, content_type=None):
        if uri.startswith('/'):
            uri = uri[1:]
        self._resources[uri] = ('blob', blob, content_type)

    def stop(self):
        del self._server._prefixes[self.prefix]


class WebServer(object):
    """An HTTP server running in a background thread.

    WebServer gets you a prefix on an HTTP server, for instance
    ``/abcdef1234/``, from which you can serve simple files, using the
    BaseHTTPServer module from the standard library.
    """
    _server = None

    @classmethod
    def get_server(cls):
        """Gets a prefix on the server, starting it first if necessary.
        """
        if WebServer._server is None:
            WebServer._server = cls()
        return WebServer._server._new_prefix()

    def __init__(self):
        orig_port = configuration.server_port
        debug.log("Starting web server, requested port is %d" % orig_port)
        self._prefixes = {}

        port = orig_port
        tries = 10
        while tries > 0:
            try:
                self._httpd = BaseHTTPServer.HTTPServer(
                    ('127.0.0.1', port),
                    RequestHandler)
            except socket.error, e:
                debug.warning("Can't grab port %d" % port, e)
                tries -= 1
                if orig_port < 1024:
                    port += 1500
                else:
                    port += 1
            else:
                break
        if not tries:
            raise RuntimeError("Couldn't grab a port for the server")
        debug.log("Web server started on port %d" % port)
        self.address = 'http://127.0.0.1:%d/' % port

        self._thread = threading.Thread(target=self._httpd.serve_forever)
        self._thread.start()

        finalizer.add_function(self.stop)

    def stop(self):
        """Stops the server; called when the package is unloaded.
        """
        debug.log("Stopping web server...")
        self._httpd.shutdown()
        self._thread.join()
        debug.log("Web server has stopped")

    def _new_prefix(self):
        """Builds a new random prefix.
        """
        name = next(random_strings)
        prefix = Prefix(name)
        self._prefixes[name] = prefix
        debug.log("Created prefix %r" % name)
        return prefix
