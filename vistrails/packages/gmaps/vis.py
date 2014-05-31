import colorsys
import copy
import json
from string import Template
import sys
import uuid

from vistrails.core.modules.config import IPort, OPort, ModuleSettings
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

class GMapVis(Module, OptionsMixin):
    _input_ports = [IPort('table', 'tabledata:Table'),
                    IPort('latitudeColIdx', 'basic:Integer', optional=True),
                    IPort('latitudeColName', 'basic:String', optional=True),
                    IPort('longitudeColIdx', 'basic:Integer', optional=True),
                    IPort('longitudeColName', 'basic:String', optional=True)]
    _output_ports = [OPort('self', 'GMapVis')]
    _settings = ModuleSettings(abstract=True)

    def get_positions(self, table=None):
        if table is None:
            table = self.get_input("table")
        
        lat_col_idx = self.force_get_input('latitudeColIdx')
        lat_col_name = self.force_get_input('latitudeColName')
        lng_col_idx = self.force_get_input('longitudeColIdx')
        lng_col_name = self.force_get_input('longitudeColName')
        lat_idx = 0
        if lat_col_idx is not None or lat_col_name is not None:
            lat_idx = choose_column(table.columns, table.names, 
                                    lat_col_name, lat_col_idx)
        lng_idx = 1
        if lng_col_idx is not None or lng_col_name is not None:
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

class GMapMarkers(GMapVis):
    TEMPLATE = Template("""
  var positions = $marker_data;
  var options = $marker_options;

  for (var i=0; i < positions.length; i++) {
    marker = new google.maps.Marker({"position": positions[i],
                                      "map": map});
    marker.setOptions(options);
  }
""")
    SPECS = ['flat']
    _input_ports = [IPort("flat", "basic:Boolean", optional=True)]
    
    def compute(self):
        (positions, center) = self.get_positions()
        marker_options = self.get_options(self.SPECS)
        data = {"marker_options": marker_options,
                "marker_data": positions}
        
        vis_data = GMapVisData([], self.TEMPLATE, data, center)
        self.set_output("self", vis_data)

class GMapValueVis(GMapVis):
    _input_ports = [IPort('valueColIdx', 'basic:Integer', optional=True),
                    IPort('valueColName', 'basic:String', optional=True)]
    _settings = ModuleSettings(abstract=True)
    def get_values(self, table=None):
        if table is None:
            table = self.get_input("table")
        value_col_idx = self.force_get_input("valueColIdx")
        value_col_name = self.force_get_input("valueColName")
        if value_col_idx is not None or value_col_name is not None:
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
    _input_ports = [IPort("strokeColor", "basic:Color", optional=True,
                          default=InstanceObject(tuple=(0,0,0))),
                    IPort("strokeWeight", "basic:Integer", optional=True),
                    IPort("strokeOpacity", "basic:Float", optional=True),
                    IPort("fillColor", "basic:Color", optional=True),
                    IPort("fillOpacity", "basic:Float", optional=True),
                    IPort("scale", "basic:Float", optional=True)]
    
    def compute(self):
        (positions, center) = self.get_positions()
        values = self.get_values()
        circle_data = [[positions[i], float(values[i])/200.0] 
                       for i in xrange(len(positions))]
        circle_options = self.get_options(self.SPECS)
        data = {"circle_options": circle_options,
                "circle_data": circle_data}
        vis_data = GMapVisData([], self.TEMPLATE, data, center)
        self.set_output("self", vis_data)

class GMapSymbols(GMapValueVis):
    TEMPLATE = Template("""
  var data = $symbol_data;

  for (var i=0; i < data.length; i++) {
    var options = $symbol_options;
    options["fillColor"] = data[i][1];
    marker = new google.maps.Marker({"position": data[i][0],
                                     "map": map,
                                     "icon": options});
  }  
""")

    SPECS = [('strokeColor', convert_color, True),
             ('fillStartColor', None, True),
             ('fillEndColor', None, True),
             'strokeWeight', 
             'strokeOpacity',
             ('fillOpacity', None, True),
             'scale']
    _input_ports = [IPort("strokeColor", "basic:Color", optional=True,
                          default=InstanceObject(tuple=(0,0,0))),
                    IPort("strokeWeight", "basic:Integer", optional=True),
                    IPort("strokeOpacity", "basic:Float", optional=True),
                    IPort("fillStartColor", "basic:Color", optional=True,
                          default=InstanceObject(tuple=(1,1,1))),
                    IPort("fillEndColor", "basic:Color", optional=True,
                          default=InstanceObject(tuple=(1,0,0))),
                    IPort("fillOpacity", "basic:Float", optional=True,
                          default=1.0),
                    IPort("scale", "basic:Float", optional=True)]

    def compute(self):
        (positions, center) = self.get_positions()
        values = [float(x) for x in self.get_values()]
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
        data = {"symbol_data": symbol_data,
                "symbol_options": symbol_options}
        vis_data = GMapVisData([], self.TEMPLATE, data, center)
        self.set_output("self", vis_data)

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
    _input_ports = [IPort("dissipating", "basic:Boolean", optional=True,
                          default=True),
                    IPort("maxIntensity", "basic:Float", optional=True),
                    IPort("opacity", "basic:Float", optional=True,
                     default=0.6),
                    IPort("radius", "basic:Float", optional=True)]
    
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
        self.set_output("self", vis_data)

_modules = [GMapVis, GMapMarkers, GMapValueVis, GMapCircles, GMapSymbols,
            GMapHeatmap]
