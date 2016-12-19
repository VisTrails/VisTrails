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

import colorsys
from string import Template

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

class TitlesMixin(object):
    def get_titles(self, table=None, default_col=None):
        if table is None:
            table = self.get_input("table")
        title_col_idx = self.force_get_input('titleColIdx')
        title_col_name = self.force_get_input('titleColName')
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
    _input_ports = [IPort('table', 'tabledata:Table'),
                    IPort('latitudeColIdx', 'basic:Integer', optional=True,
                          default=0),
                    IPort('latitudeColName', 'basic:String', optional=True),
                    IPort('longitudeColIdx', 'basic:Integer', optional=True,
                          default=1),
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
        if lat_col_idx is None and lat_col_name is None:
            lat_idx = self.get_input('latitudeColIdx') # default 0
        else:
            lat_idx = choose_column(table.columns, table.names, 
                                    lat_col_name, lat_col_idx)
        if lng_col_idx is None and lng_col_name is None:
            lng_idx = self.get_input('longitudeColIdx') # default 1
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
    _input_ports = [IPort("flat", "basic:Boolean", optional=True),
                    IPort('titleColIdx', 'basic:Integer', optional=True),
                    IPort('titleColName', 'basic:String', optional=True)]
    
    def compute(self):
        (positions, center) = self.get_positions()
        marker_options = self.get_options(self.SPECS)
        titles = self.get_titles()
        print "got titles:", titles
        data = {"marker_options": marker_options,
                "marker_data": positions,
                "marker_titles": titles}
        
        vis_data = GMapVisData([], self.TEMPLATE, data, center)
        self.set_output("self", vis_data)

class GMapValueVis(GMapVis):
    _input_ports = [IPort('valueColIdx', 'basic:Integer', optional=True,
                          default=2),
                    IPort('valueColName', 'basic:String', optional=True),]
    _settings = ModuleSettings(abstract=True)
    def get_values(self, table=None):
        if table is None:
            table = self.get_input("table")
        value_col_idx = self.force_get_input("valueColIdx")
        value_col_name = self.force_get_input("valueColName")
        if value_col_idx is None and value_col_name is None:
            value_idx = self.get_input("valueColIdx") # default 2
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
    _input_ports = [IPort("strokeColor", "basic:Color", optional=True,
                          default=InstanceObject(tuple=(0,0,0))),
                    IPort("strokeWeight", "basic:Integer", optional=True,
                          default=1),
                    IPort("strokeOpacity", "basic:Float", optional=True),
                    IPort("fillStartColor", "basic:Color", optional=True,
                          default=InstanceObject(tuple=(1,1,1))),
                    IPort("fillEndColor", "basic:Color", optional=True,
                          default=InstanceObject(tuple=(1,0,0))),
                    IPort("fillOpacity", "basic:Float", optional=True,
                          default=1.0),
                    IPort("scale", "basic:Float", optional=True,
                          default=5.0),
                    IPort('titleColIdx', 'basic:Integer', optional=True),
                    IPort('titleColName', 'basic:String', optional=True),
                    IPort("allowLegacy", "basic:Boolean", optional=True,
                          default=False)]

    def compute(self):
        (positions, center) = self.get_positions()
        legacy = self.get_input("allowLegacy")
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
