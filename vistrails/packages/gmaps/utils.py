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

import json
import uuid

###############################################################################
# Utility classes

class OptionsMixin(object):
    def get_options(self, specs):
        options = {}
        for spec in specs:
            convert_f = None
            use_default = False
            if type(spec) == tuple:
                key = spec[0]
                if len(spec) > 1:
                    convert_f = spec[1]
                if len(spec) > 2:
                    use_default = spec[2]
            else:
                key = spec

            if self.has_input(key) or use_default:
                val = self.get_input(key)
                if convert_f is not None:
                    val = convert_f(val)
                options[key] = val

        return options

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

class GMapColor(RawJavaScriptText):
    def __init__(self, r, g, b, a=1):
        RawJavaScriptText.__init__(self)
        self.r = r
        self.g = g
        self.b = b
        self.a = a
        
    def get_jstext(self):
        return "\"rgba(%d, %d, %d, %d)\"" % (self.r, self.g, self.b, self.a)

class GMapWeightedLoc(RawJavaScriptText):
    def __init__(self, lat, lng, val):
        RawJavaScriptText.__init__(self)
        self.lat = lat
        self.lng = lng
        self.val = val

    def get_jstext(self):
        return "new google.maps.visualization.WeightedLocation(new google.maps.LatLng(%s, %s), %s)" % (self.lat, self.lng, self.val)

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

