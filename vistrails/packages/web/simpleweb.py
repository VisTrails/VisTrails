import BaseHTTPServer
import socket
import threading

from vistrails.core import debug

from vistrails.packages.web import configuration
from vistrails.packages.web.common import finalizer, random_strings


class WebServer(object):
    """An HTTP server running in a background thread.

    Clients can register with it to obtain a prefix through which they can
    serve files.
    """
    _server = None

    @classmethod
    def get_server(cls):
        if WebServer._server is None:
            WebServer._server = cls()
        return WebServer._server.new_prefix()

    class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
        def do_GET(self):
            server = WebServer._server
            debug.debug("HTTP request: %s" % self.path)
            try:
                prefix_name = self.path.split('/', 2)[1]
                prefix = server._prefixes[prefix_name]
            except KeyError:
                self.send_response(404)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write("Invalid URL (prefix not found)\n")
            else:
                prefix.get(self.path[len(prefix_name) + 2:], self)

    class Prefix(object):
        def __init__(self, prefix):
            server = WebServer._server
            self.prefix = prefix
            self.address = server.address + prefix + '/'
            self._resources = {}

        def get(self, uri, handler):
            debug.debug("prefix=%r, uri=%r" % (self.prefix, uri))
            try:
                res = self._resources[uri]
            except KeyError:
                type_, args = None, ()
            else:
                type_, args = res[0], res[1:]
            if type_ == 'file':
                with open(args[0], 'rb') as fp:
                    blob = fp.read()
            elif type_ == 'blob':
                blob = args[0]
            else:
                handler.send_response(404)
                handler.send_header('Content-type', 'text/plain')
                handler.end_headers()
                handler.wfile.write("Invalid URL (not found in prefix)\n")
                return
            handler.send_response(200)
            handler.end_headers()
            handler.wfile.write(blob)

        def add_file(self, uri, filename):
            self._resources[uri] = ('file', filename)

        def add_resource(self, uri, blob):
            self._resources[uri] = ('blob', blob)

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
                    self.RequestHandler)
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
        debug.log("Stopping web server...")
        self._httpd.shutdown()
        self._thread.join()
        debug.log("Web server has stopped")

    def new_prefix(self):
        name = next(random_strings)
        prefix = self.Prefix(name)
        self._prefixes[name] = prefix
        debug.log("Created prefix %r" % name)
        return prefix
