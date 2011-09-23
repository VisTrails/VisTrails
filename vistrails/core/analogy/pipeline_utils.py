###############################################################################
##
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
##  - Neither the name of the University of Utah nor the names of its 
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


############################################################################
# Utility functions for debugging on eigen.py

from core.data_structures.point import Point

def smart_sum(v):
    try:
        fst = v.next()
        return sum(v, fst)
    except:
        pass
    fst = v[0]
    return sum(v[1:], fst)

def pipeline_centroid(pipeline):
    """Returns the centroid of a given pipeline."""
    return (smart_sum(x.location for
                      x in pipeline.modules.itervalues()) *
            (1.0 / len(pipeline.modules)))

def pipeline_bbox(pipeline):
    mn_x = 1000000000.0
    mn_y = 1000000000.0
    mx_x = -1000000000.0
    mx_y = -1000000000.0
    for m in pipeline.modules.itervalues():
        mn_x = min(mn_x, m.location.x)
        mn_y = min(mn_y, m.location.y)
        mx_x = max(mx_x, m.location.x)
        mx_y = max(mx_y, m.location.y)
    return (Point(mn_x, mn_y), Point(mx_x, mx_y))
