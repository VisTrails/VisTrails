from utils.vector import Vector3
import math

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Intersection: Plane-Box
# - Assume the box is centered in the origin
#
# Vars:
# - Vector3 normal: normal of the plane
# - float d: D value of the plane equation
# - Vector3 maxbox: half the size of the box
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
def PlaneBox(normal, d, maxbox):
    vmin = Vector3(0, 0, 0)
    vmax = Vector3(0, 0, 0)
    for q in xrange(3):
        if( normal[q] > 0. ):
            vmin[q] = -maxbox[q]
            vmax[q] = maxbox[q]
        else:
            vmin[q] = maxbox[q]
            vmax[q] = -maxbox[q]
    if( normal.dot(vmin)+d > 0. ): return False
    if( normal.dot(vmax)+d >= 0.): return True

    return False

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Intersection: Triangle-Box
# Based on:
#   Fast 3D Triangle-Box Overlap Testing
#   Tomas Akenine-Moller
#
# Vars:
# - float[3] bmin: Min. values of the boundingbox
# - float[3] bmax: Max. values of the boundingbox
# - float[9] vertices: Vertices values
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
def TriangleBox(bmin, bmax, vertices, boxcenter):

    def __axisTestX01(a, b, fa, fb):
        p0 = a*v0.y - b*v0.z
        p2 = a*v2.y - b*v2.z
        if (p0<p2):
            _min = p0
            _max = p2
        else:
            _min = p2
            _max = p0
        rad = fa*boxhalfsize.y + fb*boxhalfsize.z
        if (_min > rad or _max < -rad): return -1
        else: return 0

    def __axisTestX2(a, b, fa, fb):
        p0 = a*v0.y - b*v0.z
        p1 = a*v1.y - b*v1.z
        if (p0<p1):
            _min = p0
            _max = p1
        else:
            _min = p1
            _max = p0
        rad = fa * boxhalfsize.y + fb * boxhalfsize.z
        if (_min>rad or _max<-rad): return -1
        else: return 0

    def __axisTestY02(a, b, fa, fb):
        p0 = -a*v0.x + b*v0.z
        p2 = -a*v2.x + b*v2.z
        if(p0<p2):
            _min = p0
            _max = p2
        else:
            _min = p2
            _max = p0
        rad = fa * boxhalfsize.x + fb * boxhalfsize.z
        if(_min>rad or _max<-rad): return -1
        else: return 0

    def __axisTestY1(a, b, fa, fb):
        p0 = -a*v0.x + b*v0.z
        p1 = -a*v1.x + b*v1.z
        if (p0<p1):
            _min = p0
            _max = p1
        else:
            _min = p1
            _max = p0
        rad = fa * boxhalfsize.x + fb * boxhalfsize.z
        if(_min>rad or _max<-rad): return -1
        else: return 0

    def __axisTestZ12(a, b, fa, fb):
        p1 = a*v1.x - b*v1.y
        p2 = a*v2.x - b*v2.y
        if (p2<p1):
            _min = p2
            _max = p1
        else:
            _min = p1
            _max = p2
        rad = fa * boxhalfsize.x + fb * boxhalfsize.y
        if(_min>rad or _max<-rad): return -1
        return 0

    def __axisTestZ0(a, b, fa, fb):
        p0 = a*v0.x - b*v0.y
        p1 = a*v1.x - b*v1.y
        if (p0<p1):
            _min = p0
            _max = p1
        else:
            _min = p1
            _max = p0
        rad = fa * boxhalfsize.x + fb * boxhalfsize.y
        if(_min>rad or _max<-rad): return -1
        else: return 0

    def __findMinMax(a, b, c):
        _min = _max = a
        if (b<_min): _min = b
        if (b>_max): _max = b
        if (c<_min): _min = c
        if (c>_max): _max = c
        return _min, _max


    """  use separating axis theorem to test overlap between triangle and box 
         need to test for overlap in these directions: 
         1) the {x,y,z}-directions (actually, since we use the AABB of the triangle 
            we do not even need to test these) 
         2) normal of the triangle 
         3) crossproduct(edge from tri, {x,y,z}-directin) 
            this gives 3x3=9 more tests                                          """

    #boxcenter = Vector3((bmax[0]-bmin[0])/2., (bmax[1]-bmin[1])/2., (bmax[2]-bmin[2])/2.)
    v0 = Vector3(vertices[0], vertices[1], vertices[2])
    v1 = Vector3(vertices[3], vertices[4], vertices[5])
    v2 = Vector3(vertices[6], vertices[7], vertices[8])

    boxhalfsize = Vector3((bmax[0]-bmin[0])/2., (bmax[1]-bmin[1])/2., (bmax[2]-bmin[2])/2.)

    # This is the fastest branch on Sun
    # move everything so that the boxcenter is in (0,0,0)
    v0 = v0.sub(boxcenter)
    v1 = v1.sub(boxcenter)
    v2 = v2.sub(boxcenter)

    # compute triangle edges 
    e0 = v1.sub(v0)  # tri edge 0
    e1 = v2.sub(v1)  # tri edge 1
    e2 = v0.sub(v2)  # tri edge 2

    # Bullet 3: 
    # - test the 9 tests first (this was faster) 
    fex = math.fabs(e0.x)
    fey = math.fabs(e0.y)
    fez = math.fabs(e0.z)
    if __axisTestX01(e0.z, e0.y, fez, fey) != 0: return False,1
    if __axisTestY02(e0.z, e0.x, fez, fex) != 0: return False,2
    if __axisTestZ12(e0.y, e0.x, fey, fex) != 0: return False,3

    fex = math.fabs(e1.x)
    fey = math.fabs(e1.y)
    fez = math.fabs(e1.z)
    if __axisTestX01(e1.z, e1.y, fez, fey) != 0: return False,4
    if __axisTestY02(e1.z, e1.x, fez, fex) != 0: return False,5
    if __axisTestZ0(e1.y, e1.x, fey, fex) != 0: return False,6

    fex = math.fabs(e2.x)
    fey = math.fabs(e2.y)
    fez = math.fabs(e2.z)
    if __axisTestX2(e2.z, e2.y, fez, fey) != 0: return False,7
    if __axisTestY1(e2.z, e2.x, fez, fex) != 0: return False,8
    if __axisTestZ12(e2.y, e2.x, fey, fex) != 0: return False,9


    # Bullet 1:
    # - first test overlap in the {x,y,z}-directions
    # - find min, max of the triangle each direction, and test for overlap in 
    # - that direction -- this is equivalent to testing a minimal AABB around 
    # - the triangle against the AABB 
    _min, _max = __findMinMax(v0.x,v1.x,v2.x)
    if (_min>boxhalfsize.x or _max<-boxhalfsize.x): return False, 10

    _min, _max = __findMinMax(v0.y,v1.y,v2.y)
    if (_min>boxhalfsize.y or _max<-boxhalfsize.y): return False, 11

    _min, _max = __findMinMax(v0.z,v1.z,v2.z)
    if (_min>boxhalfsize.z or _max<-boxhalfsize.z): return False, 12

    # Bullet 2:
    # - test if the box intersects the plane of the triangle
    # - compute plane equation of triangle: normal*x+d=0
    normal = e0.cross(e1)
    d = normal.dot(v0)  # plane eq: normal.x+d=0
    if(not PlaneBox(normal, d, boxhalfsize)): return False, 13

    return True         # Box and triangle overlaps

















#
