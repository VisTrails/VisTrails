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
# This file was created automatically by SWIG 1.3.27.
# Don't modify this file, modify the SWIG interface instead.

import _TetGen

# This file is compatible with both classic and new-style classes.
def _swig_setattr_nondynamic(self,class_type,name,value,static=1):
    if (name == "this"):
        if isinstance(value, class_type):
            self.__dict__[name] = value.this
            if hasattr(value,"thisown"): self.__dict__["thisown"] = value.thisown
            del value.thisown
            return
    method = class_type.__swig_setmethods__.get(name,None)
    if method: return method(self,value)
    if (not static) or hasattr(self,name) or (name == "thisown"):
        self.__dict__[name] = value
    else:
        raise AttributeError("You cannot add attributes to %s" % self)

def _swig_setattr(self,class_type,name,value):
    return _swig_setattr_nondynamic(self,class_type,name,value,0)

def _swig_getattr(self,class_type,name):
    method = class_type.__swig_getmethods__.get(name,None)
    if method: return method(self)
    raise AttributeError,name

import types
try:
    _object = types.ObjectType
    _newclass = 1
except AttributeError:
    class _object : pass
    _newclass = 0
del types


class tetgenio(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, tetgenio, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, tetgenio, name)
    def __repr__(self):
        return "<%s.%s; proxy of C++ tetgenio instance at %s>" % (self.__class__.__module__, self.__class__.__name__, self.this,)
    FILENAMESIZE = _TetGen.tetgenio_FILENAMESIZE
    INPUTLINESIZE = _TetGen.tetgenio_INPUTLINESIZE
    __swig_getmethods__["init"] = lambda x: _TetGen.tetgenio_init
    if _newclass:init = staticmethod(_TetGen.tetgenio_init)
    __swig_setmethods__["firstnumber"] = _TetGen.tetgenio_firstnumber_set
    __swig_getmethods__["firstnumber"] = _TetGen.tetgenio_firstnumber_get
    if _newclass:firstnumber = property(_TetGen.tetgenio_firstnumber_get, _TetGen.tetgenio_firstnumber_set)
    __swig_setmethods__["mesh_dim"] = _TetGen.tetgenio_mesh_dim_set
    __swig_getmethods__["mesh_dim"] = _TetGen.tetgenio_mesh_dim_get
    if _newclass:mesh_dim = property(_TetGen.tetgenio_mesh_dim_get, _TetGen.tetgenio_mesh_dim_set)
    __swig_setmethods__["pointlist"] = _TetGen.tetgenio_pointlist_set
    __swig_getmethods__["pointlist"] = _TetGen.tetgenio_pointlist_get
    if _newclass:pointlist = property(_TetGen.tetgenio_pointlist_get, _TetGen.tetgenio_pointlist_set)
    __swig_setmethods__["pointattributelist"] = _TetGen.tetgenio_pointattributelist_set
    __swig_getmethods__["pointattributelist"] = _TetGen.tetgenio_pointattributelist_get
    if _newclass:pointattributelist = property(_TetGen.tetgenio_pointattributelist_get, _TetGen.tetgenio_pointattributelist_set)
    __swig_setmethods__["addpointlist"] = _TetGen.tetgenio_addpointlist_set
    __swig_getmethods__["addpointlist"] = _TetGen.tetgenio_addpointlist_get
    if _newclass:addpointlist = property(_TetGen.tetgenio_addpointlist_get, _TetGen.tetgenio_addpointlist_set)
    __swig_setmethods__["addpointattributelist"] = _TetGen.tetgenio_addpointattributelist_set
    __swig_getmethods__["addpointattributelist"] = _TetGen.tetgenio_addpointattributelist_get
    if _newclass:addpointattributelist = property(_TetGen.tetgenio_addpointattributelist_get, _TetGen.tetgenio_addpointattributelist_set)
    __swig_setmethods__["pointmarkerlist"] = _TetGen.tetgenio_pointmarkerlist_set
    __swig_getmethods__["pointmarkerlist"] = _TetGen.tetgenio_pointmarkerlist_get
    if _newclass:pointmarkerlist = property(_TetGen.tetgenio_pointmarkerlist_get, _TetGen.tetgenio_pointmarkerlist_set)
    __swig_setmethods__["numberofpoints"] = _TetGen.tetgenio_numberofpoints_set
    __swig_getmethods__["numberofpoints"] = _TetGen.tetgenio_numberofpoints_get
    if _newclass:numberofpoints = property(_TetGen.tetgenio_numberofpoints_get, _TetGen.tetgenio_numberofpoints_set)
    __swig_setmethods__["numberofpointattributes"] = _TetGen.tetgenio_numberofpointattributes_set
    __swig_getmethods__["numberofpointattributes"] = _TetGen.tetgenio_numberofpointattributes_get
    if _newclass:numberofpointattributes = property(_TetGen.tetgenio_numberofpointattributes_get, _TetGen.tetgenio_numberofpointattributes_set)
    __swig_setmethods__["numberofaddpoints"] = _TetGen.tetgenio_numberofaddpoints_set
    __swig_getmethods__["numberofaddpoints"] = _TetGen.tetgenio_numberofaddpoints_get
    if _newclass:numberofaddpoints = property(_TetGen.tetgenio_numberofaddpoints_get, _TetGen.tetgenio_numberofaddpoints_set)
    __swig_setmethods__["tetrahedronlist"] = _TetGen.tetgenio_tetrahedronlist_set
    __swig_getmethods__["tetrahedronlist"] = _TetGen.tetgenio_tetrahedronlist_get
    if _newclass:tetrahedronlist = property(_TetGen.tetgenio_tetrahedronlist_get, _TetGen.tetgenio_tetrahedronlist_set)
    __swig_setmethods__["tetrahedronattributelist"] = _TetGen.tetgenio_tetrahedronattributelist_set
    __swig_getmethods__["tetrahedronattributelist"] = _TetGen.tetgenio_tetrahedronattributelist_get
    if _newclass:tetrahedronattributelist = property(_TetGen.tetgenio_tetrahedronattributelist_get, _TetGen.tetgenio_tetrahedronattributelist_set)
    __swig_setmethods__["tetrahedronvolumelist"] = _TetGen.tetgenio_tetrahedronvolumelist_set
    __swig_getmethods__["tetrahedronvolumelist"] = _TetGen.tetgenio_tetrahedronvolumelist_get
    if _newclass:tetrahedronvolumelist = property(_TetGen.tetgenio_tetrahedronvolumelist_get, _TetGen.tetgenio_tetrahedronvolumelist_set)
    __swig_setmethods__["neighborlist"] = _TetGen.tetgenio_neighborlist_set
    __swig_getmethods__["neighborlist"] = _TetGen.tetgenio_neighborlist_get
    if _newclass:neighborlist = property(_TetGen.tetgenio_neighborlist_get, _TetGen.tetgenio_neighborlist_set)
    __swig_setmethods__["numberoftetrahedra"] = _TetGen.tetgenio_numberoftetrahedra_set
    __swig_getmethods__["numberoftetrahedra"] = _TetGen.tetgenio_numberoftetrahedra_get
    if _newclass:numberoftetrahedra = property(_TetGen.tetgenio_numberoftetrahedra_get, _TetGen.tetgenio_numberoftetrahedra_set)
    __swig_setmethods__["numberofcorners"] = _TetGen.tetgenio_numberofcorners_set
    __swig_getmethods__["numberofcorners"] = _TetGen.tetgenio_numberofcorners_get
    if _newclass:numberofcorners = property(_TetGen.tetgenio_numberofcorners_get, _TetGen.tetgenio_numberofcorners_set)
    __swig_setmethods__["numberoftetrahedronattributes"] = _TetGen.tetgenio_numberoftetrahedronattributes_set
    __swig_getmethods__["numberoftetrahedronattributes"] = _TetGen.tetgenio_numberoftetrahedronattributes_get
    if _newclass:numberoftetrahedronattributes = property(_TetGen.tetgenio_numberoftetrahedronattributes_get, _TetGen.tetgenio_numberoftetrahedronattributes_set)
    __swig_setmethods__["facetlist"] = _TetGen.tetgenio_facetlist_set
    __swig_getmethods__["facetlist"] = _TetGen.tetgenio_facetlist_get
    if _newclass:facetlist = property(_TetGen.tetgenio_facetlist_get, _TetGen.tetgenio_facetlist_set)
    __swig_setmethods__["facetmarkerlist"] = _TetGen.tetgenio_facetmarkerlist_set
    __swig_getmethods__["facetmarkerlist"] = _TetGen.tetgenio_facetmarkerlist_get
    if _newclass:facetmarkerlist = property(_TetGen.tetgenio_facetmarkerlist_get, _TetGen.tetgenio_facetmarkerlist_set)
    __swig_setmethods__["numberoffacets"] = _TetGen.tetgenio_numberoffacets_set
    __swig_getmethods__["numberoffacets"] = _TetGen.tetgenio_numberoffacets_get
    if _newclass:numberoffacets = property(_TetGen.tetgenio_numberoffacets_get, _TetGen.tetgenio_numberoffacets_set)
    __swig_setmethods__["holelist"] = _TetGen.tetgenio_holelist_set
    __swig_getmethods__["holelist"] = _TetGen.tetgenio_holelist_get
    if _newclass:holelist = property(_TetGen.tetgenio_holelist_get, _TetGen.tetgenio_holelist_set)
    __swig_setmethods__["numberofholes"] = _TetGen.tetgenio_numberofholes_set
    __swig_getmethods__["numberofholes"] = _TetGen.tetgenio_numberofholes_get
    if _newclass:numberofholes = property(_TetGen.tetgenio_numberofholes_get, _TetGen.tetgenio_numberofholes_set)
    __swig_setmethods__["regionlist"] = _TetGen.tetgenio_regionlist_set
    __swig_getmethods__["regionlist"] = _TetGen.tetgenio_regionlist_get
    if _newclass:regionlist = property(_TetGen.tetgenio_regionlist_get, _TetGen.tetgenio_regionlist_set)
    __swig_setmethods__["numberofregions"] = _TetGen.tetgenio_numberofregions_set
    __swig_getmethods__["numberofregions"] = _TetGen.tetgenio_numberofregions_get
    if _newclass:numberofregions = property(_TetGen.tetgenio_numberofregions_get, _TetGen.tetgenio_numberofregions_set)
    __swig_setmethods__["facetconstraintlist"] = _TetGen.tetgenio_facetconstraintlist_set
    __swig_getmethods__["facetconstraintlist"] = _TetGen.tetgenio_facetconstraintlist_get
    if _newclass:facetconstraintlist = property(_TetGen.tetgenio_facetconstraintlist_get, _TetGen.tetgenio_facetconstraintlist_set)
    __swig_setmethods__["numberoffacetconstraints"] = _TetGen.tetgenio_numberoffacetconstraints_set
    __swig_getmethods__["numberoffacetconstraints"] = _TetGen.tetgenio_numberoffacetconstraints_get
    if _newclass:numberoffacetconstraints = property(_TetGen.tetgenio_numberoffacetconstraints_get, _TetGen.tetgenio_numberoffacetconstraints_set)
    __swig_setmethods__["segmentconstraintlist"] = _TetGen.tetgenio_segmentconstraintlist_set
    __swig_getmethods__["segmentconstraintlist"] = _TetGen.tetgenio_segmentconstraintlist_get
    if _newclass:segmentconstraintlist = property(_TetGen.tetgenio_segmentconstraintlist_get, _TetGen.tetgenio_segmentconstraintlist_set)
    __swig_setmethods__["numberofsegmentconstraints"] = _TetGen.tetgenio_numberofsegmentconstraints_set
    __swig_getmethods__["numberofsegmentconstraints"] = _TetGen.tetgenio_numberofsegmentconstraints_get
    if _newclass:numberofsegmentconstraints = property(_TetGen.tetgenio_numberofsegmentconstraints_get, _TetGen.tetgenio_numberofsegmentconstraints_set)
    __swig_setmethods__["nodeconstraintlist"] = _TetGen.tetgenio_nodeconstraintlist_set
    __swig_getmethods__["nodeconstraintlist"] = _TetGen.tetgenio_nodeconstraintlist_get
    if _newclass:nodeconstraintlist = property(_TetGen.tetgenio_nodeconstraintlist_get, _TetGen.tetgenio_nodeconstraintlist_set)
    __swig_setmethods__["numberofnodeconstraints"] = _TetGen.tetgenio_numberofnodeconstraints_set
    __swig_getmethods__["numberofnodeconstraints"] = _TetGen.tetgenio_numberofnodeconstraints_get
    if _newclass:numberofnodeconstraints = property(_TetGen.tetgenio_numberofnodeconstraints_get, _TetGen.tetgenio_numberofnodeconstraints_set)
    __swig_setmethods__["pbcgrouplist"] = _TetGen.tetgenio_pbcgrouplist_set
    __swig_getmethods__["pbcgrouplist"] = _TetGen.tetgenio_pbcgrouplist_get
    if _newclass:pbcgrouplist = property(_TetGen.tetgenio_pbcgrouplist_get, _TetGen.tetgenio_pbcgrouplist_set)
    __swig_setmethods__["numberofpbcgroups"] = _TetGen.tetgenio_numberofpbcgroups_set
    __swig_getmethods__["numberofpbcgroups"] = _TetGen.tetgenio_numberofpbcgroups_get
    if _newclass:numberofpbcgroups = property(_TetGen.tetgenio_numberofpbcgroups_get, _TetGen.tetgenio_numberofpbcgroups_set)
    __swig_setmethods__["trifacelist"] = _TetGen.tetgenio_trifacelist_set
    __swig_getmethods__["trifacelist"] = _TetGen.tetgenio_trifacelist_get
    if _newclass:trifacelist = property(_TetGen.tetgenio_trifacelist_get, _TetGen.tetgenio_trifacelist_set)
    __swig_setmethods__["adjtetlist"] = _TetGen.tetgenio_adjtetlist_set
    __swig_getmethods__["adjtetlist"] = _TetGen.tetgenio_adjtetlist_get
    if _newclass:adjtetlist = property(_TetGen.tetgenio_adjtetlist_get, _TetGen.tetgenio_adjtetlist_set)
    __swig_setmethods__["trifacemarkerlist"] = _TetGen.tetgenio_trifacemarkerlist_set
    __swig_getmethods__["trifacemarkerlist"] = _TetGen.tetgenio_trifacemarkerlist_get
    if _newclass:trifacemarkerlist = property(_TetGen.tetgenio_trifacemarkerlist_get, _TetGen.tetgenio_trifacemarkerlist_set)
    __swig_setmethods__["numberoftrifaces"] = _TetGen.tetgenio_numberoftrifaces_set
    __swig_getmethods__["numberoftrifaces"] = _TetGen.tetgenio_numberoftrifaces_get
    if _newclass:numberoftrifaces = property(_TetGen.tetgenio_numberoftrifaces_get, _TetGen.tetgenio_numberoftrifaces_set)
    __swig_setmethods__["edgelist"] = _TetGen.tetgenio_edgelist_set
    __swig_getmethods__["edgelist"] = _TetGen.tetgenio_edgelist_get
    if _newclass:edgelist = property(_TetGen.tetgenio_edgelist_get, _TetGen.tetgenio_edgelist_set)
    __swig_setmethods__["edgemarkerlist"] = _TetGen.tetgenio_edgemarkerlist_set
    __swig_getmethods__["edgemarkerlist"] = _TetGen.tetgenio_edgemarkerlist_get
    if _newclass:edgemarkerlist = property(_TetGen.tetgenio_edgemarkerlist_get, _TetGen.tetgenio_edgemarkerlist_set)
    __swig_setmethods__["numberofedges"] = _TetGen.tetgenio_numberofedges_set
    __swig_getmethods__["numberofedges"] = _TetGen.tetgenio_numberofedges_get
    if _newclass:numberofedges = property(_TetGen.tetgenio_numberofedges_get, _TetGen.tetgenio_numberofedges_set)
    def initialize(*args): return _TetGen.tetgenio_initialize(*args)
    def deinitialize(*args): return _TetGen.tetgenio_deinitialize(*args)
    def load_node_call(*args): return _TetGen.tetgenio_load_node_call(*args)
    def load_node(*args): return _TetGen.tetgenio_load_node(*args)
    def load_addnodes(*args): return _TetGen.tetgenio_load_addnodes(*args)
    def load_pbc(*args): return _TetGen.tetgenio_load_pbc(*args)
    def load_var(*args): return _TetGen.tetgenio_load_var(*args)
    def load_mtr(*args): return _TetGen.tetgenio_load_mtr(*args)
    def load_poly(*args): return _TetGen.tetgenio_load_poly(*args)
    def load_off(*args): return _TetGen.tetgenio_load_off(*args)
    def load_ply(*args): return _TetGen.tetgenio_load_ply(*args)
    def load_stl(*args): return _TetGen.tetgenio_load_stl(*args)
    def load_medit(*args): return _TetGen.tetgenio_load_medit(*args)
    def load_plc(*args): return _TetGen.tetgenio_load_plc(*args)
    def load_tetmesh(*args): return _TetGen.tetgenio_load_tetmesh(*args)
    def save_nodes(*args): return _TetGen.tetgenio_save_nodes(*args)
    def save_elements(*args): return _TetGen.tetgenio_save_elements(*args)
    def save_faces(*args): return _TetGen.tetgenio_save_faces(*args)
    def save_edges(*args): return _TetGen.tetgenio_save_edges(*args)
    def save_neighbors(*args): return _TetGen.tetgenio_save_neighbors(*args)
    def save_poly(*args): return _TetGen.tetgenio_save_poly(*args)
    def readline(*args): return _TetGen.tetgenio_readline(*args)
    def findnextfield(*args): return _TetGen.tetgenio_findnextfield(*args)
    def readnumberline(*args): return _TetGen.tetgenio_readnumberline(*args)
    def findnextnumber(*args): return _TetGen.tetgenio_findnextnumber(*args)
    def __init__(self, *args):
        _swig_setattr(self, tetgenio, 'this', _TetGen.new_tetgenio(*args))
        _swig_setattr(self, tetgenio, 'thisown', 1)
    def __del__(self, destroy=_TetGen.delete_tetgenio):
        try:
            if self.thisown: destroy(self)
        except: pass


class tetgenioPtr(tetgenio):
    def __init__(self, this):
        _swig_setattr(self, tetgenio, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, tetgenio, 'thisown', 0)
        self.__class__ = tetgenio
_TetGen.tetgenio_swigregister(tetgenioPtr)

tetgenio_init = _TetGen.tetgenio_init

class polygon(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, polygon, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, polygon, name)
    def __repr__(self):
        return "<%s.%s; proxy of C++ tetgenio::polygon instance at %s>" % (self.__class__.__module__, self.__class__.__name__, self.this,)
    def __init__(self, *args):
        _swig_setattr(self, polygon, 'this', _TetGen.new_polygon(*args))
        _swig_setattr(self, polygon, 'thisown', 1)
    def __del__(self, destroy=_TetGen.delete_polygon):
        try:
            if self.thisown: destroy(self)
        except: pass


class polygonPtr(polygon):
    def __init__(self, this):
        _swig_setattr(self, polygon, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, polygon, 'thisown', 0)
        self.__class__ = polygon
_TetGen.polygon_swigregister(polygonPtr)

class facet(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, facet, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, facet, name)
    def __repr__(self):
        return "<%s.%s; proxy of C++ tetgenio::facet instance at %s>" % (self.__class__.__module__, self.__class__.__name__, self.this,)
    def __init__(self, *args):
        _swig_setattr(self, facet, 'this', _TetGen.new_facet(*args))
        _swig_setattr(self, facet, 'thisown', 1)
    def __del__(self, destroy=_TetGen.delete_facet):
        try:
            if self.thisown: destroy(self)
        except: pass


class facetPtr(facet):
    def __init__(self, this):
        _swig_setattr(self, facet, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, facet, 'thisown', 0)
        self.__class__ = facet
_TetGen.facet_swigregister(facetPtr)

class pbcgroup(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, pbcgroup, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, pbcgroup, name)
    def __repr__(self):
        return "<%s.%s; proxy of C++ tetgenio::pbcgroup instance at %s>" % (self.__class__.__module__, self.__class__.__name__, self.this,)
    def __init__(self, *args):
        _swig_setattr(self, pbcgroup, 'this', _TetGen.new_pbcgroup(*args))
        _swig_setattr(self, pbcgroup, 'thisown', 1)
    def __del__(self, destroy=_TetGen.delete_pbcgroup):
        try:
            if self.thisown: destroy(self)
        except: pass


class pbcgroupPtr(pbcgroup):
    def __init__(self, this):
        _swig_setattr(self, pbcgroup, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, pbcgroup, 'thisown', 0)
        self.__class__ = pbcgroup
_TetGen.pbcgroup_swigregister(pbcgroupPtr)


tetrahedralize = _TetGen.tetrahedralize

allocate_array = _TetGen.allocate_array

set_val = _TetGen.set_val

get_val = _TetGen.get_val

allocate_facet_array = _TetGen.allocate_facet_array

add_tri = _TetGen.add_tri


