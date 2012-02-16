############################################################################
##
## Copyright (C) 2006-2010 University of Utah. All rights reserved.
##
## This file is part of VisTrails.
##
## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of
## this file.  Please review the following to ensure GNU General Public
## Licensing requirements will be met:
## http://www.opensource.org/licenses/gpl-license.php
##
## If you are unsure which license is appropriate for your use (for
## instance, you are interested in developing a commercial derivative
## of VisTrails), please contact us at contact@vistrails.org.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################
"""This package provides interaction with mobile devices.
It contains modules to represent a geolocation, to get an image and a sound memo.
Executing on a desktop will do nothing for now.

"""
import base64
from datetime import datetime

from core.configuration import ConfigurationObject
from core.modules.vistrails_module import Module, ModuleError
from core.modules.basic_modules import Constant, Float, File, String
from core.system import get_elementtree_library

from time import strptime
from datetime import datetime

ElementTree = get_elementtree_library()

name = "Mobile"
identifier = "edu.utah.sci.vistrails.mobile"
version = '0.0.1'

class LocationCoordinate2D(Constant):
    """A structure that contains a geographical coordinate using the 
    WGS 84 reference frame."""
    def __init__(self):
        Constant.__init__(self) 
        self.latitude = None
        self.longitude = None
        LocationCoordinate2D.default_value = self
    
    @staticmethod
    def from_xml_string(xml_string):
        node = ElementTree.fromstring(xml_string)
        if node.tag != 'coordinate':
            return None
        #read attributes
        data = node.get('latitude', None)
        lati = float(data)
        
        data = node.get('longitude', None)
        longi = float(data)
        
        coord = LocationCoordinate2D()
        coord.latitude = lati
        coord.longitude = longi
        return coord
    
    @staticmethod
    def to_xml_string(x):
        node = ElementTree.Element('coordinate')
        node.set('latitude', str(x.latitude))
        node.set('longitude', str(x.longitude))  
        return ElementTree.tostring(node)       
    
    @staticmethod
    def translate_to_python(x):
        result = LocationCoordinate2D.from_xml_string(x)
        result.setResult("value", result)
        return result

    @staticmethod
    def translate_to_string(x):
        return LocationCoordinate2D.to_xml_string(x)
        
    def compute(self):
        if self.hasInputFromPort("value"):
            data = self.getInputFromPort("value")
            self.latitude = data.latitude
            self.longitude = data.longitude
        
        if self.latitude is None or self.longitude is None:
            self.checkInputPort("latitude")
            self.checkInputPort("longitude")
            self.latitude = self.getInputFromPort("latitude")
            self.longitude = self.getInputFromPort("longitude")
        self.setResult("value", self)
        self.setResult("value_as_string", self.translate_to_string(self))
        
    @classmethod
    def provide_input_port_documentation(cls, port_name):
        if port_name == "latitude":
            return """The latitude in degrees. 
Positive values indicate latitudes north of the equator. 
Negative values indicate latitudes south of the equator."""
        elif port_name == "longitude":
            return """The longitude in degrees. 
Measurements are relative to the zero meridian with positive values extending 
east of the meridian and negative values extending west of the meridian."""
    
LocationCoordinate2D._input_ports = [('value', LocationCoordinate2D),
                                     ('latitude', Float, True), 
                                     ('longitude', Float, True)]
    
LocationCoordinate2D._output_ports = [('value', LocationCoordinate2D)]
     
class Location(Constant):
    """This class represents the geographical coordinates and altitude of the 
    device's location along with values indicating the accuracy of the 
    measurements and when those measurements were made. In devices with a GPS, 
    this class also reports information about the speed and heading in which 
    the device is moving."""
    def __init__(self):
        Constant.__init__(self)
        self.coordinate = None
        self.altitude = None
        self.horizontal_accuracy = None
        self.vertical_accuracy = None
        self.timestamp = None
        self.speed = None
        self.course = None
        Location.default_value = self
        
    @staticmethod
    def from_xml_string(xml_string):
        node = ElementTree.fromstring(xml_string)
        if node.tag != 'location':
            return None
        #read attributes
        data = node.get('altitude', None)
        alti = float(data)
        
        data = node.get('horizontalAccuracy', None)
        hAcc = float(data)
        
        data = node.get('verticalAccuracy', None)
        vAcc = float(data)
    
        data = node.get('timestamp', None)
        timestamp = datetime(*strptime(data, '%Y-%m-%d %H:%M:%S')[0:6])
        
        data = node.get('speed', None)
        speed = float(data)
        
        data = node.get('course', None)
        course = float(data)
        
        coord = None
        for child in node.getchildren():
            if child.tag == "coordinate":
                text = ElementTree.tostring(child)
                coord = LocationCoordinate2D.from_xml_string(text)
        
        loc = Location()
        loc.coordinate = coord
        loc.altitude = alti
        loc.horizontal_accuracy = hAcc
        loc.vertical_accuracy = vAcc
        loc.timestamp = timestamp
        loc.speed = speed
        loc.course = course
        
        return loc
    
    @staticmethod
    def to_xml_string(x):
        node = ElementTree.Element('location')
        node.set('altitude', str(x.altitude))
        node.set('horizontalAccuracy',str(x.horizontal_accuracy))
        node.set('verticalAccuracy',str(x.vertical_accuracy))
        node.set('timestamp', x.timestamp.strftime('%Y-%m-%d %H:%M:%S'))
        node.set('speed', str(x.speed))
        node.set('course', str(x.course))
        
        child_str = LocationCoordinate2D.to_xml_string(x.coordinate)
        child = ElementTree.fromstring(child_str)
        node.append(child)
        
        return ElementTree.tostring(node)       
    
    @staticmethod
    def translate_to_python(x):
        result = Location.from_xml_string(x)
        result.setResult("value", result)
        return result

    @staticmethod
    def translate_to_string(x):
        return Location.to_xml_string(x)
    
    def compute(self):
        if self.hasInputFromPort("value"):
            data = self.getInputFromPort("value")
            self.coordinate = data.coordinate
            self.altitude = data.altitude
            self.horizontal_accuracy = data.horizontal_accuracy
            self.vertical_accuracy = data.vertical_accuracy
            self.timestamp = data.timestamp
            self.speed = data.speed
            self.course = data.course
        
        if self.coordinate is None or self.altitude is None:
            self.checkInputPort("coordinate")
            self.checkInputPort("altitude")
            self.coordinate = self.getInputFromPort("coordinate")
            self.altitude = self.getInputFromPort("altitude")
            
            #check optional ports
            if self.hasInputFromPort("horizontalAccuracy"):
                self.horizontal_accuracy = \
                              self.getInputFromPort("horizontalAccuracy")
                              
            if self.hasInputFromPort("verticalAccuracy"):
                self.vertical_accuracy = \
                              self.getInputFromPort("verticalAccuracy")
                              
            if self.hasInputFromPort("timestamp"):
                data = self.getInputFromPort("timestamp")
                self.timestamp = \
                            datetime(*strptime(data, '%Y-%m-%d %H:%M:%S')[0:6])
            if self.hasInputFromPort("speed"):
                self.speed = self.getInputFromPort("speed")
                
            if self.hasInputFromPort("course"):
                self.course = self.getInputFromPort("course")
        
        self.setResult("value", self)
        self.setResult("value_as_string", self.translate_to_string(self))
    
    @classmethod
    def provide_input_port_documentation(cls, port_name):
        if port_name == "coordinate":
            return """The geographical coordinate information 
(latitude and longitude)."""
        elif port_name == "altitude":
            return """The altitude in meters.
Positive values indicate altitudes above sea level.
Negative values indicate altitudes below sea level."""
        elif port_name == "horizontalAccuracy":
            return """The radius of uncertainty for the location, 
measured in meters.
The coordinate's latitude and longitude identify the center of the circle and 
this value indicates the radius of that circle. A negative value indicates 
that the coordinate's latitude and longitude are invalid."""
        elif port_name == "verticalAccuracy":
            return """The accuracy of the altitude value in meters.
The value in the altitude port could be plus or minus the value indicated 
by this port. A negative value indicates that the altitude value is invalid.

Determining the vertical accuracy requires a device with GPS capabilities. 
Thus, on some earlier iPhone OS-based devices, this property always contains a
negative value."""
        elif port_name == "timestamp":
            return """The time at which this location was determined.
Format: '%Y-%m-%d %H:%M:%S' """
        elif port_name == "speed":
            return """The instantaneous speed of the device in meters per second.
This value reflects the instantaneous speed of the device in the direction of 
its current heading. A negative value indicates an invalid speed. 
Because the actual speed can change many times between the delivery of 
subsequent location events, you should use this property for informational 
purposes only."""
        elif port_name == "course":
            return """The direction in which the device is travelling.
Course values are measured in degrees starting at due north and continuing 
clockwise around the compass. Thus, north is 0 degrees, east is 90 degrees, 
south is 180 degrees, and so on. Course values may not be available on all 
devices. A negative value indicates that the direction is invalid."""
        
Location._input_ports = [('value', Location),
                         ('coordinate', LocationCoordinate2D, True), 
                         ('altitude', Float, True),
                         ('horizontalAccuracy', Float, True),
                         ('verticalAccuracy', Float, True),
                         ('timestamp', String, True),
                         ('speed', Float, True),
                         ('course', Float, True)]

Location._output_ports = [('value', Location)]

class B64EncodedContents(Constant):
    def __init__(self):
        Constant.__init__(self)
        self.contents = None
        B64EncodedContents.default_value = self
    
    @staticmethod
    def translate_to_python(x):
        result = B64EncodedContents()
        result.contents = str(x)
        result.setResult("value", result)
        return result
        
    @staticmethod
    def translate_to_string(x):
        return x.contents
    
    def compute(self):
        if self.hasInputFromPort("value"):
            data = self.getInputFromPort("value")
            self.contents = data.contents
        
        if self.contents is None:
            if self.hasInputFromPort("file"):
                file_ = self.getInputFromPort("file")
                c = open(file_.name)
                self.contents = base64.b64encode(c.read()) 
            
        self.setResult("value", self)
        self.setResult("value_as_string", self.translate_to_string(self))
        
B64EncodedContents._input_ports = [('value', B64EncodedContents),
                                   ('contents', String, True), 
                                   ('file', File, True)]
    
B64EncodedContents._output_ports = [('value', B64EncodedContents)]
    
class Image(B64EncodedContents):
    def __init__(self):
        B64EncodedContents.__init__(self)
        Image.default_value = self  
        
    @staticmethod
    def translate_to_python(x):
        result = Image()
        result.contents = str(x)
        result.setResult("value", result)
        return result
    
Image._input_ports = [('value', Image)]
    
Image._output_ports = [('value', Image)]
    
class Audio(B64EncodedContents):
    def __init__(self):
        B64EncodedContents.__init__(self)
        Audio.default_value = self  
        
    @staticmethod
    def translate_to_python(x):
        result = Audio()
        result.contents = str(x)
        result.setResult("value", result)
        return result
    
Audio._input_ports = [('value', Audio)]
    
Audio._output_ports = [('value', Audio)]
    
_modules = [LocationCoordinate2D,
            Location,
            B64EncodedContents,
            Image,
            Audio]
