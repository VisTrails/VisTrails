# Break a Huge mesh in small ones
# WebGL index only support 65535
from datastructure.octree import Octree
from datastructure.basic import BasicNode, DivideMesh

class Mesh:
    def __init__ (self, _vert, _index, _normal, _color=None, _tcoord=None):
        self.useTexture = False
        self.transformation = []
        self.boundingbox = []
        self.root = None

        self.root = BasicNode()
        self.root.setValues(_vert, _index, _normal, _color, _tcoord)
        if (len(_vert)/3 > 65535):
            DivideMesh(self.root)
#            Octree(self.root)

    def isTextured(self):
        return self.useTexture

    def generateBoundingBox(self):
        bmin = [1000, 1000, 1000]
        bmax = [-999, -999, -999]
        for obj in self.vertices:
            for i in xrange(len(obj)/3):
                for j in xrange(3):
                    if obj[(i*3)+j] < bmin[j]: bmin[j] = obj[(i*3)+j] 
                    if obj[(i*3)+j] > bmax[j]: bmax[j] = obj[(i*3)+j]
        del self.boundingbox[:]
        self.boundingbox.append(bmin)
        self.boundingbox.append(bmax)

# SETS
    def setUseTexture(self, _haveTex):
        self.useTexture = _haveTex

    def setTransformation(self, _matrix):
        self.transformation = _matrix

# GETS
    def getBoundingBox(self):
        if (len(self.boundingbox) != 6):
            self.generateBoundingBox()
        return self.boundingbox

    def getTransformation(self):
        return self.transformation

    def getPart(self, pos):
        stack = [self.root]
        count = 0
        while len(stack) != 0:
            obj = stack.pop(0)
            if (obj.isLeaf() == True): 
                if (count == pos): return obj
                count += 1
            else:
                for i in obj.children:
                    stack.append(i)
        return None

    def getPartsCount(self):
        if (self.root == None): return 1

        stack = [self.root]
        count = 0
        while len(stack) != 0:
            obj = stack.pop(0)
            if (obj.isLeaf() == True): count += 1
            else:
                for i in obj.children:
                    stack.append(i)
        return count















#
