import json
import uuid
import sys

from vistrails.core.modules.vistrails_module import ModuleError

from vistrails.packages.spreadsheet.basic_widgets import SpreadsheetCell
from vistrails.packages.spreadsheet.widgets.webview.webview import WebViewCellWidget


class GMapCell(SpreadsheetCell):
    """
    TableCell is a custom Module to view TabularData using QTableWidget
    
    """
    _input_ports = [("table", "tabledata:Table"),
                    ("zoom", "basic:Integer", True),
                    ("colormapName", "basic:String", True)]

    def compute(self):
        """ compute() -> None
        Dispatch the URL to the spreadsheet
        """
        table = self.get_input("table")
        if table.columns < 2:
            raise ModuleError(self, "Must have at least (Latitude, Longitude)")
        if self.has_input("zoom"):
            zoom = self.get_input("zoom")
        else:
            zoom = 11
        if self.has_input("colormapName"):
            cmap = self.get_input('colormapName')
        else:
            cmap = 'default'
        self.displayAndWait(GMapCellWidget, (table, zoom, cmap,
                                             self.interpreter))

GMAP_TEMPLATE = """
<html>
  <head>
    <meta name="viewport" content="initial-scale=1.0, user-scalable=no">
    <meta charset="utf-8">
    <title>Google Maps</title>
    <style>
      html, body {
      height: 100%%;
      margin: 0;
      padding: 0;
      }

      #map-canvas, #map_canvas {
      height: 100%%;
      }
    </style>
    <script src="https://maps.googleapis.com/maps/api/js?v=3.exp&sensor=false"></script>
    <script>
function get_symbol(c) {
  return {"path": google.maps.SymbolPath.CIRCLE,
    "fillColor": c, "scale": 5, "strokeColor": "black", "fillOpacity": "1.0", "strokeWeight": 1.0};
}

function initialize() {
  var map = new google.maps.Map(document.getElementById('map-canvas'), %s);

  %s
}

google.maps.event.addDomListener(window, 'load', initialize);

    </script>
  </head>
  <body>
    <div id="map-canvas"></div>
  </body>
</html>
"""

MARKER_TEMPLATE = "var marker%d = new google.maps.Marker(%s);"

# {
#       position: %s,
#       map: map,
#       title: 'Hello World!'
#   });


class RawJavaScriptText(object):
    def __init__(self, jstext=None):
        self.jstext = jstext

    def get_jstext(self):
        return self.jstext

class GMapLatLng(RawJavaScriptText):
    def __init__(self, lat, lng):
        RawJavaScriptText.__init__(self)
        self.lat = lat
        self.lng = lng

    def get_jstext(self):
        return "new google.maps.LatLng(%s, %s)" % (self.lat, self.lng)

class RawJsJSONEncoder(json.JSONEncoder):
    def __init__(self, *args, **kwargs):
        json.JSONEncoder.__init__(self, *args, **kwargs)
        self._replacement_map = {}

    def default(self, o):
        if isinstance(o, RawJavaScriptText):
            key = uuid.uuid4().hex
            self._replacement_map[key] = o.get_jstext()
            return key
        else:
            return json.JSONEncoder.default(self, o)

    def encode(self, o):
        result = json.JSONEncoder.encode(self, o)
        for k, v in self._replacement_map.iteritems():
            result = result.replace('"%s"' % k, v)
        return result

class GMapCellWidget(WebViewCellWidget):
    """
    GMapCellWidget has a QTableWidget to display tables
    
    """

    def updateContents(self, inputPorts):
        """ updateContents(inputPorts: tuple) -> None
        Updates the contents with a new changed in filename
        
        """
        self.urlSrc = None

        (table, zoom, cmap, interpreter) = inputPorts
        header = table.names

        marker_str = ""
        locs = []
        marker_size = 10

        if cmap == 'redgreen':
            _color_map = {'blue': [(0.0, 0.14901961386203766,
0.14901961386203766), (0.10000000000000001, 0.15294118225574493,
0.15294118225574493), (0.20000000000000001, 0.26274511218070984,
0.26274511218070984), (0.29999999999999999, 0.3803921639919281,
0.3803921639919281), (0.40000000000000002, 0.54509806632995605,
0.54509806632995605), (0.5, 0.74901962280273438, 0.74901962280273438),
(0.59999999999999998, 0.54509806632995605, 0.54509806632995605),
(0.69999999999999996, 0.41568627953529358, 0.41568627953529358),
(0.80000000000000004, 0.38823530077934265, 0.38823530077934265),
(0.90000000000000002, 0.31372550129890442, 0.31372550129890442), (1.0,
0.21568627655506134, 0.21568627655506134)],

             'green': [(0.0, 0.0, 0.0), (0.10000000000000001,
    0.18823529779911041, 0.18823529779911041), (0.20000000000000001,
    0.42745098471641541, 0.42745098471641541), (0.29999999999999999,
    0.68235296010971069, 0.68235296010971069), (0.40000000000000002,
    0.87843137979507446, 0.87843137979507446), (0.5, 1.0, 1.0),
    (0.59999999999999998, 0.93725490570068359, 0.93725490570068359),
    (0.69999999999999996, 0.85098040103912354, 0.85098040103912354),
    (0.80000000000000004, 0.74117648601531982, 0.74117648601531982),
    (0.90000000000000002, 0.59607845544815063, 0.59607845544815063),
    (1.0, 0.40784314274787903, 0.40784314274787903)],

             'red': [(0.0, 0.64705884456634521, 0.64705884456634521),
    (0.10000000000000001, 0.84313726425170898, 0.84313726425170898),
    (0.20000000000000001, 0.95686274766921997, 0.95686274766921997),
    (0.29999999999999999, 0.99215686321258545, 0.99215686321258545),
    (0.40000000000000002, 0.99607843160629272, 0.99607843160629272),
    (0.5, 1.0, 1.0), (0.59999999999999998, 0.85098040103912354,
    0.85098040103912354), (0.69999999999999996, 0.65098041296005249,
    0.65098041296005249), (0.80000000000000004, 0.40000000596046448,
    0.40000000596046448), (0.90000000000000002, 0.10196078568696976,
    0.10196078568696976), (1.0, 0.0, 0.0)]}
        else:
            _color_map = {'blue': [(0.0, 0.94117647409439087,
0.94117647409439087), (0.125, 0.82352942228317261,
0.82352942228317261), (0.25, 0.63137257099151611,
0.63137257099151611), (0.375, 0.44705882668495178,
0.44705882668495178), (0.5, 0.29019609093666077, 0.29019609093666077),
(0.625, 0.17254902422428131, 0.17254902422428131), (0.75,
0.11372549086809158, 0.11372549086809158), (0.875,
0.08235294371843338, 0.08235294371843338), (1.0, 0.050980392843484879,
0.050980392843484879)],

                          'green': [(0.0, 0.96078431606292725, 0.96078431606292725), (0.125,
    0.87843137979507446, 0.87843137979507446), (0.25,
    0.73333334922790527, 0.73333334922790527), (0.375,
    0.57254904508590698, 0.57254904508590698), (0.5,
    0.41568627953529358, 0.41568627953529358), (0.625,
    0.23137255012989044, 0.23137255012989044), (0.75,
    0.094117648899555206, 0.094117648899555206), (0.875,
    0.058823529630899429, 0.058823529630899429), (1.0, 0.0, 0.0)],

                          'red': [(0.0, 1.0, 1.0), (0.125, 0.99607843160629272,
    0.99607843160629272), (0.25, 0.98823529481887817,
    0.98823529481887817), (0.375, 0.98823529481887817,
    0.98823529481887817), (0.5, 0.9843137264251709,
    0.9843137264251709), (0.625, 0.93725490570068359,
    0.93725490570068359), (0.75, 0.79607844352722168,
    0.79607844352722168), (0.875, 0.64705884456634521,
    0.64705884456634521), (1.0, 0.40392157435417175,
    0.40392157435417175)]}

        # _hot_data = {'red':   ((0., 0.0416, 0.0416),
        #                        (0.365079, 1.000000, 1.000000),
        #                        (1.0, 1.0, 1.0)),
        #              'green': ((0., 0., 0.),
        #                        (0.365079, 0.000000, 0.000000),
        #                        (0.746032, 1.000000, 1.000000),
        #                        (1.0, 1.0, 1.0)),
        #              'blue':  ((0., 0., 0.),
        #                        (0.746032, 0.000000, 0.000000),
        #                        (1.0, 1.0, 1.0))}

        min_value = None
        max_value = None

        lat_col = table.get_column(0)
        long_col = table.get_column(1)
        value_col = None
        title_col = None

        if table.columns > 2:
            # third column is the "value"
            min_value = sys.float_info.max
            max_value = sys.float_info.min
            value_col = table.get_column(2, True)
            for v in value_col:
                if v < min_value:
                    min_value = v
                if v > max_value:
                    max_value = v
            if cmap == 'redgreen':
                if abs(min_value) > abs(max_value):
                    max_value = abs(min_value)
                else:
                    min_value = -abs(max_value)
        if table.columns > 3:
            title_col = table.get_column(3)

        web_color = None
        # for i, row in enumerate(data):
        for i in xrange(table.rows):
            # M 100, 100
            # m -75, 0
            # a 75,75 0 1,0 150,0
            # a 75,75 0 1,0 -150,0
            if value_col is not None:
                color = {}
                val = value_col[i]
                norm_val = (val - min_value) / (max_value - min_value)
                for comp in ['red', 'green', 'blue']:
                    seg = _color_map[comp]
                    for j in xrange(len(seg)-1):
                        if norm_val >= seg[j][0] and norm_val <= seg[j+1][0]:
                            norm2 = (norm_val-seg[j][0]) / (seg[j+1][0] - seg[j][0])
                            color[comp] = norm2 * seg[j][1] + (1.0-norm2) * seg[j+1][1]
                            break
                web_color = '#%02x%02x%02x' % (int(255 * color['red']),
                                          int(255 * color['green']),
                                          int(255 * color['blue']))
                # marker_str += 'symbol["fillColor"] = "%s";' % web_color

            marker_options = {'position': GMapLatLng(lat_col[i], long_col[i]),
                              'map': RawJavaScriptText("map")}
            if value_col is not None:
                if title_col is not None:
                    # have description
                    marker_options['title'] = "%s: %f" % (title_col[i].strip(),
                                                          value_col[i])
                else:
                    marker_options['title'] = unicode(value_col[i])
            if web_color is not None:
                marker_options['icon'] = RawJavaScriptText('get_symbol("%s")' %
                                                           web_color)

            # locs.append((lat_col[i], long_col[i]))
            marker_str += MARKER_TEMPLATE % (i, json.dumps(marker_options,
                                                           cls=RawJsJSONEncoder))

        file_module = interpreter.filePool.create_file('.html')
        fname = file_module.name

        center = (sum(float(x) for x in lat_col)/len(lat_col),
                  sum(float(x) for x in long_col)/len(long_col))
        # (sum(float(x[0]) for x in locs)/len(locs),
        #           sum(float(x[1]) for x in locs)/len(locs))
        map_options = {"zoom": zoom,
                       "center": GMapLatLng(*center),
                       "mapTypeId": RawJavaScriptText("google.maps.MapTypeId.ROADMAP")}
        with open(fname, 'w') as f:
            print >>f, GMAP_TEMPLATE % (json.dumps(map_options, cls=RawJsJSONEncoder), marker_str)

        WebViewCellWidget.updateContents(self, (None, file_module))

