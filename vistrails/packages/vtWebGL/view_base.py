# Class that generates the HTML + WebGL
# In the HTML we have the Fragment/Vertex Shader
# It also have the WebGL canvas size
import os
from objects.mesh import Mesh
from objects.line import Line
import json

class webglHTML:
    html   = ""
    title  = "Title Here"
    width  = 640
    height = 480   

    def __init__(self, _title="WebGL Visualization", _width=640, _height=480):
        self.title = _title
        self.width = _width
        self.height = _height

        final = ""
        final += self.__getBeginHTML()
        #final += self.__getFragmentShader()
        #final += self.__getVertexShader()
        final += self.__getEndHTML()
        self.html = final

    def getHTML(self):
        return self.html

    shaderList = ['color', 'texture', 'line']
    def __getFragmentShader(self):
        fs = '\n'

        for i in self.shaderList:
            fs += '<script id="shader-fs-' + i.upper() + '" type="x-shader/x-fragment">\n'
            f = open('/home/wendelbsilva/Dropbox/Projetos/webGL/shaders/' + i + '.fs', 'r')
            fs += f.read()
            fs += '</script>'
            f.close()

        return fs

    def __getVertexShader(self):
        vs = '\n'

        for i in self.shaderList:
            vs += '<script id="shader-vs-' + i.upper() + '" type="x-shader/x-vertex"> '
            f = open('/home/wendelbsilva/Dropbox/Projetos/webGL/shaders/' + i + '.vs', 'r')
            vs += f.read()
            vs += '</script>'
            f.close()

        return vs

    def __getBeginHTML(self):
        begin = '\n'
        begin += '<html><head><title>' + self.title + '</title>\n'
        begin += '<meta http-equiv="content-type" content="text/html; charset=ISO-8859-1">\n'
        begin += '<script type="text/javascript" src="main.js"></script>                  \n'
        begin += '<script type="text/javascript" src="renderingObjs.js"></script>         \n'
        begin += '<script type="text/javascript" src="sylvester.js"></script>             \n'
        begin += '<script type="text/javascript" src="glUtils.js"></script>               \n'
        return begin

    def __getEndHTML(self):
        end = '\n'
        end += '</head><body onload="webGLStart();" oncontextmenu="return false;">\n'
        end += '<canvas id="glcanvas" style="border: none;" \
width="' + str(self.width) + '" height="' + str(self.height) + '">\n'
        end += '  Your browser doesn\'t appear to support the HTML5 \
<code>&lt;canvas&gt;</code> element.\n'
        end += '</canvas></body></html>\n'
        return end




class webglMainJS():

    def initVars(self):   
        self.html = ''
        self.base = ''
    
        self.meshObjects = []
        self.lineObjects = []

        self.cameraPos = [0, 0,-5]
        self.cameraUp  = [0, 1, 0]
        self.cameraEye = [0, 0, 0]
        self.cameraFov = 45.0

        self.transfMatrix = []
        self.backgroundColor = [0.0, 0.0, 0.0]
        self.backgroundColor2 = [1.0, 1.0, 1.0];
        self.isgradient = False;


    def __init__(self, resource_path):  
        self.initVars() 
        self.lineCount = 0
        self.path = resource_path
        self.__loadBase()
        self.generate()
        #raise Exception(os.path.expanduser("~"))
     
    def generate(self):
        final = ""
        final += self.base
        final += self.__getWebGLStart()       #Init Method Called by the HTML
        final += self.__getDrawSceneMethod()  #Method called every frame
        final += self.__getRenderObj()        #
        self.html = final

    def getHTML(self):
        return self.html

    def __loadBase(self):
        f = open(os.path.join(self.path, 'mainBase.js'), 'r')
        self.base = f.read()
        f.close()

    def addObject(self, obj):
        if (isinstance(obj, Mesh)):
            self.addMesh(obj)
        elif (isinstance(obj, Line)):
            self.addLine(obj)
        else:
            print "Error: Is not an acceptable object."

    def addMesh(self, mesh):
        self.meshObjects.append(mesh)

    def addLine(self, line):
        self.lineObjects.append(line)

    def setCameraLookAt(self, fov, pos, up, eye):
        self.cameraFov = fov
        self.cameraPos = pos
        self.cameraUp  = up
        self.cameraEye = eye

    def setBackgroundColor(self, color):
        self.backgroundColor = color;

    def setBackgroundColor2(self, color):
        self.backgroundColor2 = color;

    def isBackgroundGradient(self, b):
        self.isgradient = b;

    def __generateTextCoordinate(self, size):
        aux = "["
        for i in xrange(size):
            aux = aux + "0.0, 0.0,"
        return aux + "]"

    #GET METHODS
    def __getRenderObj(self):
        numObjs = len(self.lineObjects)

        for i in xrange(len(self.meshObjects)):
            if (self.meshObjects[i].getPartsCount() == 0):
                numObjs = numObjs + 1
            else:
                numObjs = numObjs + self.meshObjects[i].getPartsCount()

        f = open('data.txt', 'wb');
        import struct

        # Write Camera Info in the first file
        f.write(struct.pack("f", self.cameraFov))
        f.write(struct.pack(3*"f", *self.cameraEye))
        f.write(struct.pack(3*"f", *self.cameraPos))
        f.write(struct.pack(3*"f", *self.cameraUp))        
        f.write(struct.pack("i", numObjs))

        for i in xrange(len(self.meshObjects)):
            mesh = self.meshObjects[i]
            if (mesh.getPartsCount() == 0):
                obj = mesh.root
                f.write("M")
                # Vertices
                aux = obj.getVertices()
                f.write(struct.pack("i", len(aux)))
                f.write(struct.pack(len(aux)*"f", *aux))
                # Normals
                aux = obj.getNormals()
                f.write(struct.pack("i", len(aux)))
                f.write(struct.pack(len(aux)*"f", *aux))
                # Colors
                aux = obj.getColors()
                f.write(struct.pack("i", len(aux)))
                f.write(struct.pack(len(aux)*"f", *aux))
                # Indices
                aux = obj.getIndexes()
                f.write(struct.pack("i", len(aux)))
                f.write(struct.pack(len(aux)*"f", *aux))
                # Matrix
                aux = self.meshObjects[i].getTransformation()
                f.write(struct.pack(16*"f", *aux))
            else:
                for j in xrange(mesh.getPartsCount()):
                    obj = mesh.getPart(j)
                    f.write("M")
                    # Vertices
                    aux = obj.getVertices()
                    f.write(struct.pack("i", len(aux)))
                    f.write(struct.pack(len(aux)*"f", *aux))
                    # Normals
                    aux = obj.getNormals()
                    f.write(struct.pack("i", len(aux)))
                    f.write(struct.pack(len(aux)*"f", *aux))
                    # Colors
                    aux = obj.getColors()
                    f.write(struct.pack("i", len(aux)))
                    f.write(struct.pack(len(aux)*"f", *aux))
                    # Indices
                    aux = obj.getIndexes()
                    f.write(struct.pack("i", len(aux)))
                    f.write(struct.pack(len(aux)*"f", *aux))
                    # Matrix
                    aux = self.meshObjects[i].getTransformation()
                    f.write(struct.pack(16*"f", *aux))

        #Adding Line Objects
        for i in xrange(len(self.lineObjects)):
            obj = self.lineObjects[i]
            f.write("L")
            # Points
            aux = obj.getPoints()
            f.write(struct.pack("i", len(aux)))
            f.write(struct.pack(len(aux)*"f", *aux))
            # Colors
            aux = obj.getColors()
            f.write(struct.pack("i", len(aux)))
            f.write(struct.pack(len(aux)*"f", *aux))
            # Indices
            aux = obj.getIndexes()
            f.write(struct.pack("i", len(aux)))
            f.write(struct.pack(len(aux)*"f", *aux))
            # Matrix
            aux = self.lineObjects[i].getTransformation()
            f.write(struct.pack(16*"f", *aux))

        #Global Parameters
        if(self.isgradient): f.write("Y");
        else: f.write("N");
        print self.isgradient
        f.write(struct.pack(3*"f", *self.backgroundColor))
        f.write(struct.pack(3*"f", *self.backgroundColor2))

        f.close()

        return "";    

    def listToStr(self, _list):
        if _list == None: return '[]'
        ret = '['
        for r in _list:
            ret += str(r) + ','
        ret += ']'
        return ret

    def __getLineIndex(self, x):
        index = '['
        for i in self.lineIndex[x]:
            index += str(i) + ','
        index += ']'
        return index

    def __getLineColors(self, x):
        color = '['
        for c in self.lineColors[x]:
            color += str(c) + ','
        color += ']'
        return color

    def __getLinePoints(self, x):
        points = '['
        for p in self.linePoints[x]:
           points += str(p) + ','
        points += ']'
        return points

    def __getDrawSceneMethod(self):
        pos = self.cameraPos
        up = self.cameraUp
        lookat = self.cameraEye
        drawscene = "\n"
        drawscene += "function drawScene() {                                 \n"
        drawscene += "  gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT); \n"
        drawscene += "\n"
        drawscene += "  perspectiveMatrix = makePerspective(" + str(self.cameraFov) + ", gl.viewportWidth/gl.viewportHeight, 0.1, 1000000.0);\n"
        drawscene += "  eye = [" + str(pos[0]) + "," + str(pos[1]) + "," + str(pos[2]) + "];\n"
        drawscene += "  center = [" + str(lookat[0]) + "," + str(lookat[1]) + "," + str(lookat[2]) + "];\n"
        drawscene += "  up = [" + str(up[0]) + "," + str(up[1]) + "," + str(up[2]) + "];\n"
        drawscene += "  loadIdentity();\n"
        drawscene += "  mvMatrix = makeLookAt(eye[0], eye[1], eye[2], center[0], center[1], center[2], up[0], up[1], up[2]);\n"
        drawscene += "  \n"
        drawscene += "  //RENDER MESHS\n"
        drawscene += "  renderObj();\n"
        drawscene += "}\n"
        return drawscene

    def __getWebGLStart(self):
        bg = self.backgroundColor
        glstart = "\n"
        glstart += "// Initial Function\n"
        glstart += "// The name of the function to be called first is set in the html\n"
        glstart += "function webGLStart() {\n"
        glstart += "  canvas = document.getElementById('glcanvas');\n"
        glstart += "\n"
        glstart += "  initWebGL(canvas);                          // Initialize the GL context\n"
        glstart += "\n"  
        glstart += "  // Only continue if WebGL is available and working \n"
        glstart += "  if (gl) {\n"
        glstart += "    gl.clearColor(" + str(bg[0]) + "," + str(bg[1]) + "," + str(bg[2]) + ", 1.0);\n"
        glstart += "    gl.clearDepth(1.0);                       // Clear everything\n"
        glstart += "    gl.enable(gl.DEPTH_TEST);                 // Enable depth testing\n"
        glstart += "    gl.depthFunc(gl.LEQUAL);                  // Near things obscure far things    \n"
        glstart += "\n"
        glstart += "    // Initialize the shaders\n"
        glstart += "    initShaders();\n"   
        glstart += "    // Initialize Geometry Buffers\n"
        glstart += "    initBuffers();\n"
        glstart += "    // Initialize Textures\n"
        glstart += "    initTexture();\n"
        glstart += "\n"
        glstart += "    // Bind mouse events\n"
        glstart += "    canvas.onmousedown = handleMouseDown;\n"
        glstart += "    document.onmouseup = handleMouseUp;\n"
        glstart += "    document.onmousemove = handleMouseMove;\n"
        glstart += "    \n"
        glstart += "    // Set up to draw the scene periodically.    \n"
        glstart += "    setInterval(drawScene, 15);\n"
        glstart += "  }\n"
        glstart += "}\n"
        return glstart
