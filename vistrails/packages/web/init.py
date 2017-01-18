import os
import urllib

from vistrails.core.modules.basic_modules import File
from vistrails.core.modules.config import ModuleSettings
from vistrails.core.modules.vistrails_module import Module
from vistrails.packages.spreadsheet.basic_widgets import SpreadsheetCell
from vistrails.packages.spreadsheet.widgets.webview.webview import \
    WebViewCellWidget

from .common import finalizer
from .servers.simpleweb import WebServer


class WebWidget(WebViewCellWidget):
    def updateContents(self, inputPorts):
        url, server = inputPorts
        self.server = server  # Keeps a reference so the server stays alive
        super(WebWidget, self).updateContents((url,))

    def deleteLater(self):
        self.server.stop()
        super(WebWidget, self).deleteLater()


class WebSite(SpreadsheetCell):
    """General web visualization cell.

    You can add both direct-entry files, stored as a url-encoded parameter
    value, and File input ports to this module. It will serve them from the
    web server and create a web cell to display the page.
    """
    _settings = ModuleSettings(configure_widget=
            'vistrails.packages.web.widgets:WebSiteWidget')
    _input_ports = [('spreadsheet_page', 'basic:String',
                     {'optional': True, 'defaults': "['/index.html']"})]

    def __init__(self):
        SpreadsheetCell.__init__(self)
        self.ordered_input_ports = []

    def transfer_attrs(self, module):
        Module.transfer_attrs(self, module)
        self.ordered_input_ports = list(module.input_port_specs)

    def compute(self):
        # Gets a WebServer
        server = WebServer.get_server()

        for port_spec in self.ordered_input_ports:
            name = port_spec.name
            is_direct = port_spec.signature[0][0] is not File
            value = self.get_input(name)

            if is_direct:
                server.add_resource(name, urllib.unquote(value))
            else:
                server.add_file(name, value.name)

        # Displays on the spreadsheet
        page = self.get_input('spreadsheet_page')
        if page.startswith('/'):
            page = page[1:]
        self.display(WebWidget, (server.address + page, server))


def finalize():
    finalizer.finalize()


_modules = [WebSite]
