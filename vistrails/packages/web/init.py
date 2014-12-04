import os

from vistrails.packages.spreadsheet.basic_widgets import SpreadsheetCell
from vistrails.packages.spreadsheet.widgets.webview.webview import \
    WebViewCellWidget

from vistrails.packages.web.common import finalizer
from vistrails.packages.web.servers.simpleweb import WebServer


class TestWeb(SpreadsheetCell):
    """A test module.
    """
    def compute(self):
        # Gets some space on the web server, using WebServer
        server = WebServer.get_server()

        # Registers the image
        server.add_file('logo', os.path.join(
                            os.path.dirname(__file__),
                            '../../gui/resources/images/dockback.png'),
                        'image/png')

        # Registers the page
        server.add_resource('', b"""\
<!DOCTYPE html>
<html>
  <head><title>Some page</title></head>
  <body>
    <img src="logo" />
    <p>Text</p>
  </body>
</html>
""")

        # Displays on the spreadsheet
        self.display(WebViewCellWidget, (server.address,))


def finalize():
    finalizer.finalize()


_modules = [TestWeb]
