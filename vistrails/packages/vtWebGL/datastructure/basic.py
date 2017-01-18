import objects.mesh
from utils.vector import Vector3

# -=-=-=-=-=-=-=[ BASIC NODE CLASS ]=-=-=-=-=-=-=-
class BasicNode:

    def __init__(self):
        self.boundingbox = []
        self.children = []
        self.vertices = []
        self.index = []
        self.normals = []
        self.colors = None
        self.tcoord = None

    def clearValues(self):
        del self.vertices[:]
        del self.index[:]
        del self.normals[:]
        if (self.colors != None): del self.colors[:]
        if (self.tcoord != None): del self.tcoord[:]

    def generateBoundingBox(self):
        bmin = [1000, 1000, 1000]
        bmax = [-999, -999, -999]
        for i in xrange(len(self.vertices)/3):
            for j in xrange(3):
                if self.vertices[(i*3)+j] < bmin[j]: bmin[j] = self.vertices[(i*3)+j]
                if self.vertices[(i*3)+j] > bmax[j]: bmax[j] = self.vertices[(i*3)+j]
        del self.boundingbox[:]
        aux = 0.00001
        bmin[0] -= aux; bmin[1] -= aux; bmin[2] -= aux;
        bmax[0] += aux; bmax[1] += aux; bmax[2] += aux;
        self.boundingbox.append(bmin)
        self.boundingbox.append(bmax)

    def addChild(self, node):
        self.children.append(node)

    def addTriangle(self, _vert, _norm, _colr, _tcrd):
        _index = len(self.vertices)/3
        self.index.append(_index)
        self.index.append(_index+1)
        self.index.append(_index+2)

        if(_colr != None and len(_colr) != 0): 
            if (self.colors == None): self.colors = []
        if(_tcrd != None and len(_tcrd) != 0): 
            if (self.tcoord == None): self.tcoord = []

        appendVert = self.vertices.append
        appendNorm = self.normals.append
        for i in xrange(9):
            appendVert(_vert[i]) #self.vertices.append(_vert[i])
            appendNorm(_norm[i]) #self.normals.append(_norm[i])            

        if(self.colors != None):            
            appendColor = self.colors.append
            for i in xrange(12):
                appendColor(_colr[i]) #self.colors.append(_colr[i])

        if(self.tcoord != None):
            appendTCoor = self.tcoord.append
            for i in xrange(6): 
                appendTCoor(_tcrd[i]) #self.tcoord.append(_tcrd[i])

    def isLeaf(self):
        return len(self.children) == 0 and len(self.vertices) != 0

    # SETS
    def setBoundingBox(self, bmin, bmax):
        del self.boundingbox[:]
        self.boundingbox.append(bmin)
        self.boundingbox.append(bmax)
        self.boxcenter = Vector3((bmax[0]+bmin[0])/2., (bmax[1]+bmin[1])/2., (bmax[2]+bmin[2])/2.)

    def setValues(self, _vert, _index, _normal, _color=None, _tcoord=None):
        self.vertices = _vert
        self.index = _index
        self.normals = _normal
        self.colors = _color
        self.tcoord = _tcoord
        self.generateBoundingBox()

    # GETS
    def getBoundingBox(self):
        return self.boundingbox

    def getTriangle(self, i):
        pos = self.index[i*3:(i*3)+3]     

        _vert = self.vertices[pos[0]*3:(pos[0]*3) + 3]
        _norm = self.normals[pos[0]*3:(pos[0]*3) + 3]
        _colr = _tcrd = []

        if (self.colors != None): _colr = self.colors[pos[0]*4:(pos[0]*4) + 4]
        if (self.tcoord != None): _tcrd = self.tcoord[pos[0]*2:(pos[0]*2) + 2]

        for j in xrange(2):
            _vert.extend(self.vertices[pos[j+1]*3:(pos[j+1]*3) + 3])
            _norm.extend(self.normals[pos[j+1]*3:(pos[j+1]*3) + 3])
            if (self.colors != None): _colr.extend(self.colors[pos[j+1]*4:(pos[j+1]*4) + 4])
            if (self.tcoord != None): _tcrd.extend(self.tcoord[pos[j+1]*2:(pos[j+1]*2) + 2])

        return _vert, _norm, _colr, _tcrd

    def getVertices(self):
        return self.vertices

    def getIndexes(self):
        return self.index

    def getNormals(self):
        return self.normals

    def getColors(self):
        return self.colors

    def getTCoords(self):
        return self.tcoord



class DivideMesh:

    def __init__(self, node):
        self.node = node
        self.generate(self.node)

    def generate(self, node):
        from datetime import datetime
        a = datetime.now()        
        count = 0
        vert = []
        n = []
        c = []
        t = []
        nn = BasicNode()

        for i in xrange(len(node.index)/3):
            if count >= 65530:
                node.addChild(nn)
                nn = BasicNode()
                count = 0

            vert, n, c, t = node.getTriangle(i)
            nn.addTriangle(vert, n, c, t); 
            count += 3
        node.addChild(nn)
        node.clearValues()
        b = datetime.now()
        c = b-a
        print c.seconds, c.microseconds/1000.




