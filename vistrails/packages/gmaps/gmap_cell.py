###############################################################################
##
## Copyright (C) 2014-2016, New York University.
## Copyright (C) 2011-2014, NYU-Poly.
## Copyright (C) 2006-2011, University of Utah.
## All rights reserved.
## Contact: contact@vistrails.org
##
## This file is part of VisTrails.
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met:
##
##  - Redistributions of source code must retain the above copyright notice,
##    this list of conditions and the following disclaimer.
##  - Redistributions in binary form must reproduce the above copyright
##    notice, this list of conditions and the following disclaimer in the
##    documentation and/or other materials provided with the distribution.
##  - Neither the name of the New York University nor the names of its
##    contributors may be used to endorse or promote products derived from
##    this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
## AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
## THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
## PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
## CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
## OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
## WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
## OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
## ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
###############################################################################

from __future__ import division

from string import Template

from vistrails.core.modules.config import IPort
from vistrails.core.modules.vistrails_module import ModuleError

from vistrails.packages.spreadsheet.basic_widgets import SpreadsheetCell
from vistrails.packages.spreadsheet.widgets.webview.webview import WebViewCellWidget

from .utils import *

class GMapCell(SpreadsheetCell, OptionsMixin):
    """
    GMapCell is a custom Module to view TabularData geographically
    
    """

    SPECS = [('zoom', None, True), 
             'center']
    _input_ports = [IPort("layers", "GMapVis"),
                    IPort("zoom", "basic:Integer", optional=True, default=11),
                    IPort("center", "basic:Float,basic:Float", optional=True)]

    def compute(self):
        """compute() -> None
        Dispatch the URL to the spreadsheet

        """

        layers = self.get_input_list("layers")
        if len(layers) < 1:
            raise ModuleError(self, "Must provide at least one layer")
        map_options = self.get_options(self.SPECS)
        self.displayAndWait(GMapCellWidget, (layers, map_options, 
                                             self.interpreter))

class GMapCellWidget(WebViewCellWidget):
    TEMPLATE = Template("""
<html>
  <head>
    <meta name="viewport" content="initial-scale=1.0, user-scalable=no">
    <meta charset="utf-8">
    <title>Google Maps</title>
    <style>
      html, body {
      margin: 0;
      padding: 0;
      }

      #map-canvas, #map_canvas {
      height: 100vh;
      width: 100vw;
      }
    </style>
    <script src="https://maps.googleapis.com/maps/api/js?v=3.exp&libraries=visualization&sensor=false"></script>
    <script>
function initialize() {
  var map = new google.maps.Map(document.getElementById('map-canvas'), $map_options);

  $layers
}

google.maps.event.addDomListener(window, 'load', initialize);

    </script>
  </head>
  <body>
    <div id="map-canvas"></div>
  </body>
</html>
""")

    def updateContents(self, inputPorts):
        self.urlSrc = None
        
        (layers, map_options, interpreter) = inputPorts
 
        file_module = interpreter.filePool.create_file('.html')
        fname = file_module.name

        with open(fname, 'w') as f:
            layers_js = ""
            center = [0.0, 0.0]
            for layer in layers:
                layer_data = dict((k, json.dumps(v, cls=RawJsJSONEncoder))
                                   for k, v in layer.data.iteritems())
                layers_js += layer.init_template.substitute(layer_data)
                center[0] += layer.center[0]
                center[1] += layer.center[1]
            center[0] /= float(len(layers))
            center[1] /= float(len(layers))
            
            if 'center' not in map_options:
                map_options['center'] = GMapLatLng(*center)
            template_options = {'map_options': 
                                json.dumps(map_options, cls=RawJsJSONEncoder),
                                'layers':
                                layers_js}
            print >>f, self.TEMPLATE.substitute(template_options)
        print "GMAP FILENAME:", fname

        WebViewCellWidget.updateContents(self, (None, file_module))

# def create_json_gradient(color_list):
#     colors = []
#     for c in color_list:
#         if len(c) > 3:
#             a = c[3]
#         else:
#             a = 1
#         colors.append(GMapColor(c[0], c[1], c[2], a))
#     return colors

# PURPLE_GRADIENT = create_json_gradient([(252,251,253,0),
#                                         # (239,237,245),
#                                         # (218,218,235),
#                                         (188,189,220),
#                                         (158,154,200),
#                                         (128,125,186),
#                                         (106,81,163),
#                                         (84,39,143),
#                                         (63,0,125)])            

# GMAP_HEATMAP_TEMPLATE = """
# <html>
#   <head>
#     <meta name="viewport" content="initial-scale=1.0, user-scalable=no">
#     <meta charset="utf-8">
#     <title>Google Maps</title>
#     <style>
#       html, body {
#       height: 100%%;
#       margin: 0;
#       padding: 0;
#       }

#       #map-canvas, #map_canvas {
#       height: 100%%;
#       }
#     </style>
#     <script src="https://maps.googleapis.com/maps/api/js?v=3.exp&libraries=visualization&sensor=false"></script>
#     <script>
# var heatmap1, heatmap2;
# function initialize() {
#   var map = new google.maps.Map(document.getElementById('map-canvas'), %s);

#   var weightedLocs1 = %s;
#   var weightedLocs2 = %s;

#   heatmap1 = new google.maps.visualization.HeatmapLayer({data: weightedLocs1, radius: 20.0});
#   heatmap1.setMap(map);
#   var gradient1 = ['rgba(255,255,191,0)',
#                    'rgba(255,255,191,1)',
#                    'rgba(254,224,139,1)',
#                    'rgba(253,174,97,1)',
#                    'rgba(244,109,67,1)',
#                    'rgba(215,48,39,1)',
#                    'rgba(215,48,39,1)',
#                    'rgba(165,0,38,1)'];
#   heatmap1.set('gradient', gradient1);
#   heatmap2 = new google.maps.visualization.HeatmapLayer({data: weightedLocs2, radius: 20.0});
#   heatmap2.setMap(map);
#   var gradient2 = ['rgba(255,255,191,0)',
#                    'rgba(255,255,191,1)',
#                    'rgba(217,239,139,1)',
#                    'rgba(166,217,106,1)',
#                    'rgba(102,189,99,1)',
#                    'rgba(26,152,80,1)',
#                    'rgba(0,104,55,1)'];
#   heatmap2.set('gradient', gradient2);
# }

# google.maps.event.addDomListener(window, 'load', initialize);

#     </script>
#   </head>
#   <body>
#     <div id="map-canvas"></div>
#   </body>
# </html>
# """

# class GMapHeatmapWidget(WebViewCellWidget):
#     def updateContents(self, inputPorts):
#         """ updateContents(inputPorts: tuple) -> None
#         Updates the contents with a new changed in filename
        
#         """
#         self.urlSrc = None

#         (table, zoom, cmap, interpreter) = inputPorts
#         header = table.names

#         min_value = None
#         max_value = None

#         lat_col = table.get_column(0)
#         long_col = table.get_column(1)
#         value_col = table.get_column(2)

#         # weighted_locs = [GMapWeightedLoc(lat_col[i], long_col[i], value_col[i])
#         #                  for i in xrange(table.rows)]
#         heatmap_data1 = [{"location": GMapLatLng(lat_col[i], long_col[i]),
#                          "weight": -float(value_col[i])}
#                          for i in xrange(table.rows)
#                          if float(value_col[i]) < 0.0]
#         heatmap_data2 = [{"location": GMapLatLng(lat_col[i], long_col[i]),
#                           "weight": float(value_col[i])}
#                          for i in xrange(table.rows)
#                          if float(value_col[i]) >= 0.0]

#         file_module = interpreter.filePool.create_file('.html')
#         fname = file_module.name

#         center = (sum(float(x) for x in lat_col)/len(lat_col),
#                   sum(float(x) for x in long_col)/len(long_col))
#         map_options = {"zoom": zoom,
#                        "center": GMapLatLng(*center),
#                        "mapTypeId": RawJavaScriptText("google.maps.MapTypeId.ROADMAP")}
#         with open(fname, 'w') as f:
#             print >>f, GMAP_HEATMAP_TEMPLATE % \
#                 (json.dumps(map_options, cls=RawJsJSONEncoder),
#                  json.dumps(heatmap_data1, cls=RawJsJSONEncoder),
#                  json.dumps(heatmap_data2, cls=RawJsJSONEncoder))
#         print "GMAP FILENAME:", fname

#         WebViewCellWidget.updateContents(self, (None, file_module))


_modules = [GMapCell]
