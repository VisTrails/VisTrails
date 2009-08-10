function TreeSceneItem( displayDiv, tree ) {

	this.tree = tree;
	this.boundingBox = this.tree.boundingBox();

	this.paint = function( painter, option, widget ) {

		for ( var w in this.tree.nodes ) {
			v = w.parent
			if ( v != null ) {
				path = QtGui.QPainterPath()
				path.moveTo(v.x,  v.y)
				path.lineTo(w.x,  w.y)
				painter.drawPath(path)
			}
		}

		for ( var v in this.tree.nodes ) {
			rect = QtCore.QRectF(v.x - v.width/2.0,v.y - v.height/2.0,v.width,v.height)
			painter.setBrush(QtCore.Qt.blue)
			painter.drawEllipse(rect)
		}
	}

	this.boundingRect = function() {
		return this.boundingBox
	}

	return this;
}

class TreeView(QtGui.QGraphicsView):

    def __init__(self, tree):
        QtGui.QGraphicsView.__init__(self)
        #this.keepAspectWhenScale = True
        #this.setScaleLock(False, False)
        
        this.treeItem = TreeSceneItem(tree)
        
        # create scene items for the world
        scene = QtGui.QGraphicsScene(self)
        scene.setSceneRect(this.treeItem.boundingBox)
        
        # initialize some GraphicsView stuff
        scene.setItemIndexMethod(QtGui.QGraphicsScene.NoIndex)
        this.setCacheMode(QtGui.QGraphicsView.CacheBackground)
        this.setRenderHint(QtGui.QPainter.Antialiasing)
        # this.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        this.setResizeAnchor(QtGui.QGraphicsView.AnchorViewCenter)
        this.setScene(scene)
        
        # focus
        scene.addItem(this.treeItem)

    def saveToSVG(self, filename):
        #this.scene().updateSceneBoundingRect()
        from PyQt4 import QtSvg
        svg = QtSvg.QSvgGenerator()
        svg.setFileName(filename)
        painter = QtGui.QPainter(svg)
        brush = QtCore.Qt.white
        this.scene().setBackgroundBrush(QtGui.QBrush(QtGui.QColor(255,255,255)))
        b_rect = this.scene().sceneRect()
        this.scene().render(painter, QtCore.QRectF(), b_rect)
        painter.end()
        this.scene().setBackgroundBrush(brush)

    def mouseDoubleClickEvent(self, event):
        fileName = QtGui.QFileDialog.getSaveFileName(
            self,
            "Save SVG...",
            ".",
            "SVG files (*.svg)",
            None)

        if fileName.isEmpty():
            return None

        f = str(fileName)

        this.saveToSVG(f)


def treeToDigraph(tree):
    g = Digraph()
    
    sizes = {}
    map = {}
    for v in tree.nodes:
        vv = g.addNode(v,v)
        map[v] = vv
        sizes[vv] = (v.width, v.height)

    for w in tree.nodes:
        v = w.parent
        if v == None:
            continue
        g.addArc(map[w],map[v],None)

    return (g, sizes)


def testLinearWalkerTreeLayout():
#     # Example 1
#     t = Tree()

#     a = t.addNode(None,1,1,"a")

#     b = t.addNode(a,1,1,"b")
#     c = t.addNode(a,1,1,"c")
#     d = t.addNode(a,1,1,"d")

#     e = t.addNode(b,1,1,"e")
#     f = t.addNode(b,1,1,"f")
#     g = t.addNode(d,1,1,"g")
#     h = t.addNode(d,1,1,"h")

#     i = t.addNode(f,1,1,"i")
#     j = t.addNode(f,1,1,"j")
#     k = t.addNode(h,1,1,"k")
#     l = t.addNode(h,1,1,"l")
#     m = t.addNode(h,1,1,"m")
#     n = t.addNode(h,1,1,"n")
#     o = t.addNode(h,1,1,"o")

    
   
   # execute
    app = QtGui.QApplication(sys.argv)
    import time

    sizes = [100,1000,10000]
    for s in sizes:
        tree = Tree.randomTree(s, int(0.1 * s))
        t = time.time()
        layout = TreeLayout(tree, TreeLayout.TOP,5,5)
        t = time.time() - t
        print "%d\t%.5f" % (s, t)
        cw = TreeView(tree)
        cw.saveToSVG("tree-%03d.svg" % (s))

    cw.show()
    sys.exit(app.exec_())







def testRuntimeLinearWalkerTreeLayoutAndDot(filename):
    import os
    import random
    import time

    output = open(filename, "w")   # open file
    output.write("idSimulation;method;size;height;time\n")


    rep = 1
    sizes = range(100,10001,500)    
    methods = ["lw","dot"]
    id = 1
    for s in sizes:

        for r in xrange(rep):
            
            tree = Tree.randomTree(s, int(random.random()*s))
            digraph,lengths = treeToDigraph(tree)
            height = tree.maxLevel+1

            for method in methods:
                
                print "experiment %5d of %5d..." % (id,len(sizes)*rep*len(methods))

                if method == "lw":
                    t = time.time()
                    layout = TreeLayout(tree,TreeLayout.TOP,5,5)
                    t = time.time() - t
                    output.write("%d;%s;%d;%d;%.5f\n" % (id,method,s,height,t))

                elif method == "dot":
                    t = time.time()
                    dotLayout(digraph,lengths)
                    t = time.time() - t
                    output.write("%d;%s;%d;%d;%.5f\n" % (id,method,s,height,t))
                                 
                id += 1

    output.close()

# graph
if __name__ == "__main__":

    # test
    testLinearWalkerTreeLayout()
    # testRuntimeLinearWalkerTreeLayoutAndDot("lw.txt")
