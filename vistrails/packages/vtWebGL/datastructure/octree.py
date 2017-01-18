import objects.mesh
from utils import intersection
from utils.vector import Vector3
from datetime import datetime
from datastructure.basic import BasicNode


#-=-=-=-= CLASS OCTREE =-=-=-=-
"""p1     p2
    +-----+       y
   /     /|       |
p3+-----p4|       |  / z
  |     | + p6    | /
  |     |/        |/_______x
p7+-----+ p8      
"""

class Octree:

    def __init__(self, node):
        self.node = node
        self.generate(self.node)

    def generate(self, node):        
        if (not node.isLeaf()): return
        bmin, bmax = node.getBoundingBox()

        half = [(bmax[0]-bmin[0])/2., (bmax[1]-bmin[1])/2., (bmax[2]-bmin[2])/2.]

        p1 = BasicNode(); p1.setBoundingBox([bmin[0], bmin[1]+half[1], bmin[2]+half[2]], [bmin[0]+half[0], bmax[1], bmax[2]])
        p2 = BasicNode(); p2.setBoundingBox([bmin[0]+half[0], bmin[1]+half[1], bmin[2]+half[2]], bmax)
        p3 = BasicNode(); p3.setBoundingBox([bmin[0], bmin[1]+half[1], bmin[2]], [bmin[0]+half[0], bmax[1], bmin[2]+half[2]])
        p4 = BasicNode(); p4.setBoundingBox([bmin[0]+half[0], bmin[1]+half[1], bmin[2]], [bmax[0], bmax[1], bmin[2]+half[2]])
        p5 = BasicNode(); p5.setBoundingBox([bmin[0], bmin[1], bmin[2]+half[2]], [bmin[0]+half[0], bmin[1]+half[1], bmax[2]])
        p6 = BasicNode(); p6.setBoundingBox([bmin[0]+half[0], bmin[1], bmin[2]+half[2]], [bmax[0], bmin[1]+half[1], bmax[2]])
        p7 = BasicNode(); p7.setBoundingBox(bmin, [bmin[0]+half[0], bmin[1]+half[1], bmin[2]+half[2]])
        p8 = BasicNode(); p8.setBoundingBox([bmin[0]+half[0], bmin[1], bmin[2]], [bmax[0], bmin[1]+half[1], bmin[2]+half[2]])

        # For each vertices
        print len(node.index)/3
        from datetime import datetime
        a = datetime.now()
        for i in xrange(len(node.index)/3):
        #   # Test for each cube
            vert, n, c, t = node.getTriangle(i)
            aaa = False
            if(intersection.TriangleBox(p1.boundingbox[0], p1.boundingbox[1], vert, p1.boxcenter) == True):
                p1.addTriangle(vert, n, c, t); aaa = True
            if(intersection.TriangleBox(p2.boundingbox[0], p2.boundingbox[1], vert, p2.boxcenter) == True):
                p2.addTriangle(vert, n, c, t); aaa = True
            if(intersection.TriangleBox(p3.boundingbox[0], p3.boundingbox[1], vert, p3.boxcenter) == True): 
                p3.addTriangle(vert, n, c, t); aaa = True
            if(intersection.TriangleBox(p4.boundingbox[0], p4.boundingbox[1], vert, p4.boxcenter) == True): 
                p4.addTriangle(vert, n, c, t); aaa = True
            if(intersection.TriangleBox(p5.boundingbox[0], p5.boundingbox[1], vert, p5.boxcenter) == True): 
                p5.addTriangle(vert, n, c, t); aaa = True
            if(intersection.TriangleBox(p6.boundingbox[0], p6.boundingbox[1], vert, p6.boxcenter) == True): 
                p6.addTriangle(vert, n, c, t); aaa = True
            if(intersection.TriangleBox(p7.boundingbox[0], p7.boundingbox[1], vert, p7.boxcenter) == True): 
                p7.addTriangle(vert, n, c, t); aaa = True
            if(intersection.TriangleBox(p8.boundingbox[0], p8.boundingbox[1], vert, p8.boxcenter) == True): 
                p8.addTriangle(vert, n, c, t); aaa = True
        b = datetime.now()
        c = b-a
        print c.seconds, c.microseconds/1000.
        node.clearValues()
        node.addChild(p1)
        node.addChild(p2)
        node.addChild(p3)
        node.addChild(p4)
        node.addChild(p5)
        node.addChild(p6)
        node.addChild(p7)
        node.addChild(p8)

        for i in self.node.children:
            if len(i.getVertices())/3 > 65535:
                print "ramu lah"
                self.generate(i)

"""
cria os 8 nos filhos
para cada 3 index
- pega o trianglo
- 8 verificacoes
-- se intersecta, adiciona no OctreeNode
"""

