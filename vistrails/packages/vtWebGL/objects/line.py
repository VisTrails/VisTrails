# Object Line

class Line:
    def __init__ (self, _points, _index, _color):
        self.points = []
        self.index = []
        self.colors = []
        self.partsCount = 0
        self.transformation = []

        if (len(_points)/3 < 65535):
            self.points.append(_points)
            self.index.append(_index)
            self.colors.append(_color)
            self.partsCount = 1
        else:
            #Break into parts
            print "nice"

# SETS
    def setTransformation(self, _matrix):
        self.transformation = _matrix

# GETS
    def getTransformation(self):
        return self.transformation

    def getPoints(self, _pos=0):
        return self.points[_pos]

    def getIndexes(self, _pos=0):
        return self.index[_pos]

    def getColors(self, _pos=0):
        return self.colors[_pos]

