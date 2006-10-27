#!/usr/bin/env python

# class to detect intersections between shapes

from gui.shape import *
import math
from PyQt4 import QtGui

class Intersect:
    def __init__(self):
        self.m = 1000 #multiplier, since qregions are all ints
    
    def intersect(self, s1, s2):
        """ Finds whether the two shapes intersect
        Parameters
        ----------
        s1 - 'Shape' - either some sort of ellipse or rectangle
        s2 - same as s1
        Returns
        -------
        'Boolean'
        """
        #adjust for the fact that QRegions are only ever ints.
        #the max number is somewhere around 35000, I think it is 37000, but I don't know
        self.m = 35000/max(s1.x,s1.y,s1.width/2,s1.height/2,s2.x,s2.y,s2.width/2,s2.height/2) 
        if isEllipse(s1):
            r1=self.convertEllipse(s1)
        elif isRect(s1):
            r1=self.convertRect(s1)
        else:
            print "Intersection class supports Ellipses and Rectangles."
            return False

        if isEllipse(s2):
            r2=self.convertEllipse(s2)
        elif isRect(s2):
            r2=self.convertRect(s2)
        else:
            print "Intersection class supports Ellipses and Rectangles."
            return False

        result = r1.intersect(r2)
        return (not result.isEmpty())

    def convertRect(self, r):
        """Since rectangles in the shape class are represented
        by a middle point, then width and height, this funct
        converts them to represent a corner (top left) point, w and h
        the params must be ints, so a multiplier m is used to get the
        right scope on the params.
        
        Parameters
        ----------
        -r : 'Shape' - must be some sort of rectangle

        Returns
        -------
        'QtGui.QRegion'
        """
        m=self.m
        w = abs(r.width)
        h = abs(r.height)
        return QtGui.QRegion(m*(r.x-(w/2)), m*(r.y - (h/2)),
                             m*w, m*h, QtGui.QRegion.Rectangle)
    

    def convertEllipse(self, e):
        m=self.m
        w = abs(e.width)
        h = abs(e.height)
        return QtGui.QRegion(m*(e.x-(w/2)), m*(e.y - (h/2)),
                             m*w, m*h, QtGui.QRegion.Ellipse)
        #return QtGui.QRegion(m*e.x, m*e.y, m*w, m*h, QtGui.QRegion.Ellipse)
        
                 
def isEllipse(s):
    """determines whether the given shape is an ellipse
    Parameters
    ----------
    -s: 'Shape'
    
    Returns: Boolean
    """
    return isinstance(s,Ellipse) or isinstance(s, VersionShape) or isinstance(s, ShadowEllipse)

def isRect(s):
    """determines whether the given shape is a rectangle
    Parameters
    ----------
    -s: 'Shape'
    
    Returns: Boolean
    """
    return isinstance(s,Rectangle) or isinstance(s,ShadowRectangle) or isinstance(s,PortShape) or isinstance(s,ModuleShape)
    
