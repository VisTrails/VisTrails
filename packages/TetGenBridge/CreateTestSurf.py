############################################################################
##
## Copyright (C) 2006-2007 University of Utah. All rights reserved.
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
import core.modules
import core.modules.module_registry
from core.modules.vistrails_module import Module, ModuleError
import packages.TetGenBridge
import TetGen
import re
import os

# TetGen output on this mesh. -pqAz
## Statistics:

##   Input points: 149
##   Input facets: 294
##   Input holes: 0
##   Input regions: 0

##   Mesh points: 2184
##   Mesh tetrahedra: 7462
##   Mesh faces: 16726
##   Mesh subfaces: 3604
##   Mesh subsegments: 2037

nodes_exp = re.compile('([\d\-\.]+)\s+([\d\-\.]+)\s+([\d\-\.]+)')
def getTestNodes() :
    nodes = []
    p = "%spackages%sTetGenBridge%s" % (os.sep, os.sep, os.sep)
    f = open('%s%spill.nodes' % (os.getcwd(), p))
    for l in f.readlines() :
        mo = nodes_exp.match(l)
        if mo != None :
            nodes.append((float(mo.group(1)), float(mo.group(2)),
                          float(mo.group(3)))) 
    return nodes

tris_exp = re.compile('(\d+)\s+(\d+)\s+(\d+)')
def getTestTris() :
    tris = []
    p = "%spackages%sTetGenBridge%s" % (os.sep, os.sep, os.sep)
    f = open('%s%spill.tri' % (os.getcwd(), p))
    for l in f.readlines() :
        mo = tris_exp.match(l)
        if mo != None :
            tris.append((int(mo.group(1)), int(mo.group(2)),
                         int(mo.group(3)))) 
    return tris

def addSurfaceInfo(tgio, marker = 0) :
    
    #iterate over nodes and add the points.    
    nodes = getTestNodes()
    sz = len(nodes)
    tgio.pointlist = TetGen.allocate_array(sz * 3)
    tgio.numberofpoints = sz
    idx = 0
    for n in nodes :
        TetGen.set_val(tgio.pointlist, idx * 3, n[0])
        TetGen.set_val(tgio.pointlist, idx * 3 + 1, n[1])
        TetGen.set_val(tgio.pointlist, idx * 3 + 2, n[2])
        idx = idx + 1

    #iterate over faces and add the facets.    
    tris = getTestTris()
    fsz = len(tris)
    tgio.facetlist = TetGen.allocate_facet_array(fsz)
    tgio.numberoffacets = fsz;
    idx = 0
    for t in tris :
        TetGen.add_tri(tgio.facetlist, idx, t[0], t[1], t[2])
        idx = idx + 1
    
class CreateTestSurf(Module):
    def compute(self):
        out  = packages.TetGenBridge.tetgenio_wrapper()
        addSurfaceInfo(out.data, 0)
        self.setResult("tgio out", out)

def initialize(reg):
    reg.add_module(CreateTestSurf)
    reg.add_output_port(CreateTestSurf, "tgio out",
                      (packages.TetGenBridge.tetgenio_wrapper,
                       'output test surface'))
