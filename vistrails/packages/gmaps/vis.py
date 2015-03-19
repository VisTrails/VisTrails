from __future__ import division

import colorsys
from string import Template

from vistrails.core.modules.vistrails_module import ModuleError, Module
from vistrails.core.utils import InstanceObject
# FIXME make package imports better
from vistrails.packages.tabledata.common import choose_column

from .utils import *

###############################################################################
# Modules and Data

class GMapVisData(object):
    def __init__(self, gmaps_libs, init_template, data, center=None):
        self.gmaps_libs = gmaps_libs
        self.init_template = init_template
        self.data = data
        self.center = center

def convert_color(c):
    c = c.tuple
    return GMapColor(c[0] * 255.0, c[1] * 255.0, c[2] * 255.0)

class TitlesMixin(object):
    def get_titles(self, table=None, default_col=None):
        if table is None:
            table = self.getInputFromPort("table")
        title_col_idx = self.forceGetInputFromPort('titleColIdx')
        title_col_name = self.forceGetInputFromPort('titleColName')
        print "title_col_idx:", title_col_idx
        print "title_col_name:", title_col_name

        if (title_col_idx is None and
                title_col_name is None and 
                default_col is not None and
                default_col < table.columns):
                # only allow default if in range
                title_col_idx = default_col

        if title_col_idx is not None or title_col_name is not None:
            title_idx = choose_column(table.columns, table.names, 
                                      title_col_name, title_col_idx)
            title_col = table.get_column(title_idx)
            return title_col
        return None

class GMapVis(Module, OptionsMixin):
    _input_ports = [('table', 'tabledata:Table'),
                    ('latitudeColIdx', 'basic:Integer', {
                        'optional': True, 'defaults': "['0']"}),
                    ('latitudeColName', 'basic:String', {'optional': True}),
                    ('longitudeColIdx', 'basic:Integer', {
                        'optional': True, 'defaults': "['1']"}),
                    ('longitudeColName', 'basic:String', {'optional': True})]
    _output_ports = [('self', 'GMapVis')]

    def get_positions(self, table=None):
        if table is None:
            table = self.getInputFromPort("table")
        
        lat_col_idx = self.forceGetInputFromPort('latitudeColIdx')
        lat_col_name = self.forceGetInputFromPort('latitudeColName')
        lng_col_idx = self.forceGetInputFromPort('longitudeColIdx')
        lng_col_name = self.forceGetInputFromPort('longitudeColName')
        if lat_col_idx is None and lat_col_name is None:
            lat_idx = self.getInputFromPort('latitudeColIdx') # default 0
        else:
            lat_idx = choose_column(table.columns, table.names, 
                                    lat_col_name, lat_col_idx)
        if lng_col_idx is None and lng_col_name is None:
            lng_idx = self.getInputFromPort('longitudeColIdx') # default 1
        else:
            lng_idx = choose_column(table.columns, table.names, 
                                    lng_col_name, lng_col_idx)
        lat_col = table.get_column(lat_idx, True)
        lng_col = table.get_column(lng_idx, True)
        center = (sum(float(x) for x in lat_col)/len(lat_col),
                  sum(float(x) for x in lng_col)/len(lng_col))
        positions = []
        for i in xrange(table.rows):
            positions.append(GMapLatLng(lat_col[i], lng_col[i]))
        return (positions, center)

class GMapMarkers(GMapVis, TitlesMixin):
    TEMPLATE = Template("""
  var positions = $marker_data;
  var options = $marker_options;
  var titles = $marker_titles;

  for (var i=0; i < positions.length; i++) {
    marker = new google.maps.Marker({"position": positions[i],
                                      "map": map});
    marker.setOptions(options);
    if (titles) {
      marker.setTitle(titles[i]);
    }
  }
""")
    SPECS = ['flat']
    _input_ports = [("flat", "basic:Boolean", {'optional': True}),
                    ('titleColIdx', 'basic:Integer', {'optional': True}),
                    ('titleColName', 'basic:String', {'optional': True})]
    
    def compute(self):
        (positions, center) = self.get_positions()
        marker_options = self.get_options(self.SPECS)
        titles = self.get_titles()
        print "got titles:", titles
        data = {"marker_options": marker_options,
                "marker_data": positions,
                "marker_titles": titles}
        
        vis_data = GMapVisData([], self.TEMPLATE, data, center)
        self.setResult("self", vis_data)

class GMapValueVis(GMapVis):
    _input_ports = [('valueColIdx', 'basic:Integer', {
                        'optional': True, 'defaults': "['2']"}),
                    ('valueColName', 'basic:String', {'optional': True})]
    def get_values(self, table=None):
        if table is None:
            table = self.getInputFromPort("table")
        value_col_idx = self.forceGetInputFromPort("valueColIdx")
        value_col_name = self.forceGetInputFromPort("valueColName")
        if value_col_idx is None and value_col_name is None:
            value_idx = self.getInputFromPort("valueColIdx") # default 2
        else:
            value_idx = choose_column(table.columns, table.names, 
                                      value_col_name, value_col_idx)
        value_col = table.get_column(value_idx, True)
        return value_col

class GMapCircles(GMapValueVis):
    TEMPLATE = Template("""
  var data = $circle_data;
  
  for (var i=0; i < data.length; i++) {
    var options = $circle_options;
    options["center"] = data[i][0];
    options["radius"] = data[i][1];
    options["map"] = map;
    circle = new google.maps.Circle(options);
  }
""")
    
    SPECS = [('strokeColor', convert_color, True),
             ('fillColor', convert_color),
             'strokeWeight', 
             'strokeOpacity',
             'fillOpacity']
    _input_ports = [("strokeColor", "basic:Color", {
                        'optional': True,
                        'defaults': "['0,0,0']"}),
                    ("strokeWeight", "basic:Integer", {'optional': True}),
                    ("strokeOpacity", "basic:Float", {'optional': True}),
                    ("fillColor", "basic:Color", {'optional': True}),
                    ("fillOpacity", "basic:Float", {'optional': True}),
                    ("scale", "basic:Float", {'optional': True})]
    
    def compute(self):
        (positions, center) = self.get_positions()
        values = self.get_values()
        circle_data = [[positions[i], float(values[i])/200.0]
                       for i in xrange(len(positions))]
        circle_options = self.get_options(self.SPECS)
        data = {"circle_options": circle_options,
                "circle_data": circle_data}
        vis_data = GMapVisData([], self.TEMPLATE, data, center)
        self.setResult("self", vis_data)

class GMapSymbols(GMapValueVis, TitlesMixin):
    TEMPLATE = Template("""
  var data = $symbol_data;
  var titles = $symbol_titles;

  for (var i=0; i < data.length; i++) {
    var marker_options = {"position": data[i][0],
                          "map": map};
    if (titles) {
      marker_options["title"] = titles[i];
    }
    if ($use_values) {
      var icon_options = $symbol_options;
      icon_options["fillColor"] = data[i][1];
      marker_options["icon"] = icon_options;
    }
    marker = new google.maps.Marker(marker_options);
  }  
""")

    SPECS = [('strokeColor', convert_color, True),
             ('fillStartColor', None, True),
             ('fillEndColor', None, True),
             ('strokeWeight', None, True),
             'strokeOpacity',
             ('fillOpacity', None, True),
             ('scale', None, True)]
    _input_ports = [("strokeColor", "basic:Color", {
                        'optional': True,
                        'defaults': "['0,0,0']"}),
                    ("strokeWeight", "basic:Integer", {
                        'optional': True, 'defaults': "['1']"}),
                    ("strokeOpacity", "basic:Float", {'optional': True}),
                    ("fillStartColor", "basic:Color", {
                        'optional': True,
                        'defaults': "['1,1,1']"}),
                    ("fillEndColor", "basic:Color", {
                        'optional': True,
                        'defaults': "['1,0,0']"}),
                    ("fillOpacity", "basic:Float", {'optional': True,
                                                    'defaults': "['1.0']"}),
                    ("scale", "basic:Float", {'optional': True,
                                              'defaults': "['5.0']"}),
                    ('titleColIdx', 'basic:Integer', {'optional': True}),
                    ('titleColName', 'basic:String', {'optional': True}),
                    ("allowLegacy", "basic:Boolean", {
                        'optional': True, 'defaults': "['False']"})]

    def compute(self):
        (positions, center) = self.get_positions()
        legacy = self.getInputFromPort("allowLegacy")
        use_values = True
        try:
            values = [float(x) for x in self.get_values()]
        except ValueError, e:
            # LEGACY SUPPORT
            if legacy:
                use_values = False
            else:
                raise ModuleError(self, "Must provide values column")
        if not use_values:
            symbol_data = positions
            symbol_options = {}
        else:
            symbol_options = self.get_options(self.SPECS)
            symbol_options["path"] = \
                            RawJavaScriptText("google.maps.SymbolPath.CIRCLE")
            min_value = min(values)
            max_value = max(values)

            # if we have black or white, we want hue to match the other side
            def white_or_black(c):
                return ((c[0] < 1e-8 and c[1] < 1e-8 and c[2] < 1e-8) or
                        (c[0] > 1-1e-8 and c[1] > 1-1e-8 and c[2] > 1-1e-8))
            start_c = symbol_options.pop("fillStartColor").tuple
            end_c = symbol_options.pop("fillEndColor").tuple
            start_wb = white_or_black(start_c)
            end_wb = white_or_black(end_c)
            start_c = list(colorsys.rgb_to_hsv(*start_c))
            end_c = list(colorsys.rgb_to_hsv(*end_c))
            if start_wb:
                start_c[0] = end_c[0]
            elif end_wb:
                end_c[0] = start_c[0]

            symbol_data = []
            for i in xrange(len(positions)):
                val = values[i]
                if max_value - min_value < 1e-8:
                    norm_val = 1.0
                else:
                    norm_val = (val - min_value) / (max_value - min_value)
                color = []
                for j in xrange(len(start_c)):
                    color.append((1.0 - norm_val) * start_c[j] + 
                                 norm_val * end_c[j])
                color = colorsys.hsv_to_rgb(*color)
                symbol_data.append([positions[i],
                                    GMapColor(255 * color[0],
                                              255 * color[1],
                                              255 * color[2])])
        symbol_titles = self.get_titles(default_col=(3 if legacy else None))
        data = {"symbol_data": symbol_data,
                "symbol_options": symbol_options,
                "symbol_titles": symbol_titles,
                "use_values": use_values}
        vis_data = GMapVisData([], self.TEMPLATE, data, center)
        self.setResult("self", vis_data)

class GMapHeatmap(GMapValueVis):
    TEMPLATE = Template("""
  var data = $heatmap_data;
  var options = $heatmap_options;
  options["data"] = data;
  options["map"] = map;
  heatmap = new google.maps.visualization.HeatmapLayer(options);
""")

    SPECS = ['dissipating',
             'maxIntensity',
             'opacity',
             'radius']
    _input_ports = [("dissipating", "basic:Boolean", {'optional': True,
                                                      'defaults': "['True']"}),
                    ("maxIntensity", "basic:Float", {'optional': True}),
                    ("opacity", "basic:Float", {'optional': True,
                                                'defaults': "['0.6']"}),
                    ("radius", "basic:Float", {'optional': True})]
    
    def compute(self):
        (positions, center) = self.get_positions()
        values = self.get_values()
        heatmap_data = [{"location": positions[i],
                         "weight": float(values[i])} 
                        for i in xrange(len(positions))]
        heatmap_options = self.get_options(self.SPECS)
        data = {"heatmap_data": heatmap_data,
                "heatmap_options": heatmap_options}
        vis_data = GMapVisData([], self.TEMPLATE, data, center)
        self.setResult("self", vis_data)

_modules = [(GMapVis, {'abstract': True}), (GMapValueVis, {'abstract': True}),
            GMapMarkers, GMapCircles, GMapSymbols, GMapHeatmap]
