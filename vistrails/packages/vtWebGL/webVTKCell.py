import vtk
from view_base import webglHTML, webglMainJS
from objects.mesh import Mesh
from objects.line import Line
import random
import os
import sys
from math import floor
import colorsys
import shutil
from datetime import datetime

#### TODO
#- Package: fix the directory thing. receive name as parameter.
#- Fix translation and rotation
#- Colormap still wrong.
#- change webVTKCell to VTK Wrapper.
#- Get Line Color Information
#- Get lights
#- Isnt Updating the Texture
#- See why example PerlinTerrain isnt working
#- Isnt getting the informations from the example GenerateTextureCoords
#- Gradient Background
#- create a real log

class webVTKCell:

    # renderer   = vtkRenderer of your pipeline
    # saveFolder = folder where the html/js will be generated
    # Title      = Title of the html
    # Width      = dimension of the webgl/canvas
    # Height     = dimension of the webgl/canvas
    def __init__(self, renderer, saveFolder, title="WebGL Visualization", width=640, height=480, resource_path="", showInfo=False):
        #SET INITIAL INFO
        self.objects = []
        self.saveFolder = saveFolder
        self.render = renderer
        self.title = title
        self.width = width
        self.height = height
        self.showInformation = showInfo
        if (resource_path == ""):
            resource_path = os.getcwd() + "/"
        self.path = os.path.normpath(resource_path)

        #Get all the objects
        actors = self.render.GetActors()
        for i in xrange(actors.GetNumberOfItems()):
            print "> Actor:", i
            actor = actors.GetItemAsObject(i)            
            mapper = actor.GetMapper()
            ppp = actor.GetMapper().GetInput()
            ppp.Update()
            #vtkStructuredGrid
            if (isinstance(ppp, vtk.vtkUnstructuredGrid) or isinstance(ppp, vtk.vtkStructuredGrid)):
                geomFilter = vtk.vtkGeometryFilter()
                geomFilter.SetInputConnection(0, ppp.GetProducerPort())                
                aux = geomFilter.GetOutputPort(0)
                polydata = vtk.vtkTriangleFilter()
                polydata.SetInputConnection(aux)
                polydata.Update()
            else:
                polydata = vtk.vtkTriangleFilter()
                polydata.SetInput(ppp)
                polydata.Update()
            
            self.__log("Object: #" + str(i+1))
            self.__log("Amount of Polygons:" + str(polydata.GetOutput(0).GetNumberOfPolys()))
            self.__log("Amount of Lines:" + str(polydata.GetOutput(0).GetNumberOfLines()))

            if (actor.GetProperty().GetRepresentation() == vtk.VTK_WIREFRAME):
                self.__getLinesFromPolygon(actor.GetMapper(), actor)
            else:
                if (mapper.GetScalarMode() == 3):#VTK_SCALAR_MODE_USE_POINT_FIELD_DATA
                    self.__gettingMeshInfo(polydata, actor)
                elif (mapper.GetScalarMode() == 4):#VTK_SCALAR_MODE_USE_CELL_FIELD_DATA
                    self.__gettingMeshInfo(polydata, actor) #TODO: Give support to cell data
                else:
                    self.__gettingMeshInfo(polydata, actor)

            self.__gettingLinesInfo(actor.GetMapper(), polydata, actor)


        #Get camera info and Generate the HTML
        self.__configuringCamera()
        self.__generateHTML()  

    def __log(self, message):
        if (self.showInformation):
            print message

    def __gettingTransformation(self, actor):        
        mm = []
        if (actor):
            matrix = actor.GetMatrix()
            for i in xrange(16):
                mm.append(matrix.GetElement(i/4, i%4))
        else:
            mm = [1, 0, 0, 0,
                  0, 1, 0, 1,
                  0, 0, 1, 0,
                  0, 0, 0, 1]
        self.objects[-1].setTransformation(mm)

    def __gettingMeshInfo(self, polydata, actor):
        if (polydata.GetOutput(0).GetNumberOfPolys() != 0):
            print "> Getting Mesh"

            t1 = vtk.vtkPolyDataNormals()
            t1.SetInputConnection(polydata.GetOutputPort(0))
            t1.Update()
            aux = t1.GetOutput(0)

            point = aux.GetPointData()
            poly = aux.GetPolys()
            data = poly.GetData()

            ## VERTICES
            _vert = []
            _vertSize = 0
            for k in xrange(aux.GetNumberOfPoints()):
                for w in xrange(3):
                    _vert.append(float(aux.GetPoint(k)[w]))
                    _vertSize += 1           
            ## INDEX
            # The index return the amount of index per polygon + indexes
            # ex: 3 (0, 1, 2).
            # The hack is removing the first value. I know will be always 3 anyways (Triangulate).
            _index = []
            _indexSize = 0
            hack = 3
            for i in xrange(data.GetSize()):
                if (hack != 3):
                    _index.append(int(data.GetValue(i)))
                    _indexSize += 1
                    hack += 1
                else: 
                    hack = 0

            ## NORMALS
            _normal = []
            _normalSize = point.GetNormals().GetSize()
            for i in xrange(_normalSize):
                _normal.append(float(point.GetNormals().GetValue(i)))
            ## TCoords
            _tcoord = []
            _tcoordSize = 0
            if (point.GetTCoords()):
                _tcoordSize = point.GetTCoords().GetSize()
            for i in xrange(_tcoordSize):
                _tcoord.append(float(point.GetTCoords().GetValue(i)))

            ## COLORS
            _color = []
            _colorSize = 0
            _color = self.__getColorFromPointData(point, polydata, actor, point.GetNormals().GetSize()/3)

            # Creating Object
            mesh = Mesh(_vert, _index, _normal, _color, _tcoord)
            havetex = self.__gettingTextures(actor)

            mesh.setUseTexture(havetex)
            self.objects.append(mesh)
            self.__gettingTransformation(actor)

            self.__log("istextured:" + str(havetex))


    def __getColorFromPointData(self, pointdata, polydata, actor, size):
        colorSize = size
        array = None
        _color = []

        rgb = [1.0, 1.0, 1.0]
        alpha = 0
        mag = 0
        celldata = vtk.mutable(1)

        polynormals = vtk.vtkPolyDataNormals()
        polynormals.SetInputConnection(polydata.GetOutputPort(0))
        polynormals.Update()
        data = polynormals.GetOutput()

        array = vtk.vtkAbstractMapper.GetScalars(data, actor.GetMapper().GetScalarMode(),
                                      actor.GetMapper().GetArrayAccessMode(), actor.GetMapper().GetArrayId(),
                                      actor.GetMapper().GetArrayName(), celldata)

        #VTK_COLOR_MODE_DEFAULT = 0
        if (actor.GetMapper().GetScalarVisibility()==1 and actor.GetMapper().GetColorMode() == 0 and array):
            table = actor.GetMapper().GetLookupTable()

            if (table.GetTable().GetNumberOfTuples() == 0): 
                cor = actor.GetMapper().MapScalars(1.0)
            else:
                cor = table.MapScalars(array, int(table.GetVectorMode()), int(table.GetVectorComponent()))

            for i in xrange(colorSize):
                rgb = [1, 1, 1]
                rgb = cor.GetTuple(i);

                _color.append(rgb[0]/255.0)
                _color.append(rgb[1]/255.0)
                _color.append(rgb[2]/255.0)
                _color.append(1.0)
        else:
            rgb = actor.GetProperty().GetColor()
            alpha = actor.GetProperty().GetOpacity()
            for i in xrange(colorSize):
                _color.append(rgb[0])
                _color.append(rgb[1])
                _color.append(rgb[2])
                _color.append(alpha)
        return _color


    def __gettingTextures(self, actor1):
        if (actor1.GetTexture()):
            texture = actor1.GetTexture()
            imgWriter = vtk.vtkBMPWriter()  # vtk.vtkPNMWriter()
            imgWriter.SetFileName(self.saveFolder + "test.bmp")
            imgWriter.SetInput(texture.GetInput())
            imgWriter.Write()
            return True
        else:
            return False

    def __gettingLinesInfo(self, mapper, polydata, actor):
        print "> Getting Line"
        if (polydata.GetOutput(0).GetNumberOfLines() == 0): return;

        lines = polydata.GetOutput(0).GetLines()

        # For each cell
        _point = []
        _index = []
        _color = []
        count = 0

        #init index, final index, dont care
        for i in xrange(lines.GetData().GetSize()):
            if (i%3 != 0): 
                _index.append(lines.GetData().GetValue(i))

        for i in xrange(polydata.GetOutput(0).GetNumberOfPoints()):
            point = polydata.GetOutput(0).GetPoint(i)
            _point.append(point[0])
            _point.append(point[1])
            _point.append(point[2])

        _color = self.__GetColorsFromPolyData(polydata.GetOutput(0), actor)
        line = Line(_point, _index, _color)
        self.objects.append(line)
        self.__gettingTransformation(actor)

    def __getLinesFromPolygon(self, mapper, actor):
        print "> Getting Wireframe" #Wendel
        _point = []
        _index = []
        _color = []

        dObj = mapper.GetInputDataObject(0, 0)
        cd = vtk.vtkCompositeDataSet.SafeDownCast(dObj) 
        if (cd and isinstance(cd, vtk.vtkCompositeDataSet)):
            gf = vtk.vtkCompositeDataGeometryFilter()
            gf.SetInput(cd)
            gf.Update()
            tempDS = gf.GetOutput()
            dataset = tempDS
        else:
            dataset = mapper.GetInput()

        table = mapper.GetLookupTable()
        array = None
        if (mapper.GetScalarMode() == vtk.VTK_SCALAR_MODE_USE_CELL_FIELD_DATA):
            celldata = dataset.GetCellData()
            if (mapper.GetArrayAccessMode() == vtk.VTK_GET_ARRAY_BY_ID):
                array = celldata.GetArray(mapper.GetArrayId())
            else:
                array = celldata.GetArray(mapper.GetArrayName())
        else:
            pointdata = dataset.GetPointData()
            if (mapper.GetArrayAccessMode() == vtk.VTK_GET_ARRAY_BY_ID):
                array = pointdata.GetArray(mapper.GetArrayId())
            else:
                array = pointdata.GetArray(mapper.GetArrayName())

        mode = table.GetVectorMode()
        rgb = [1.0, 1.0, 1.0]
        if (array == None or array.GetNumberOfComponents() == 0):
            rgb = actor.GetProperty().GetColor()
            mode = -1

        #Count will be used to create the index
        count = 0
        #Create the lines from all cells
        for i in xrange(dataset.GetNumberOfCells()):
            cell = dataset.GetCell(i)
            #firstI will be used to create a Index from last point to first
            firstI = count
            for j in xrange(cell.GetNumberOfPoints()):
                p = cell.GetPoints().GetPoint(j)
                _point.append(p[0])
                _point.append(p[1])
                _point.append(p[2])
                _index.append(count)
                count += 1
                if (j != cell.GetNumberOfPoints()-1):
                    _index.append(count)
                else:
                    _index.append(firstI)

                #Get Color
                if (mode == 0): #MAGNITUDE
                    c = array.GetTuple(cell.GetPointIds().GetId(j))
                    mag = c[0]*c[0] + c[1]*c[1] + c[2]*c[2]
                    table.GetColor(mag, rgb)
                elif (mode == 1): #COMPONENT
                    mag = array.GetComponent(cell.GetPointIds().GetId(j), table.GetVectorComponent())
                    table.GetColor(mag, rgb)
                elif (mode == 2): #RGBCOLORS
                    rgb = array.GetTuple(cell.GetPointIds().GetId(j))
                    rgb[0] /= 255.0
                    rgb[1] /= 255.0
                    rgb[2] /= 255.0
                _color.append(rgb[0])
                _color.append(rgb[1])
                _color.append(rgb[2])
                _color.append(1.0)
        line = Line(_point, _index, _color)
        self.objects.append(line)
        self.__gettingTransformation(actor)


    def __GetColorsFromPolyData(self, polydata, actor):
        _colors = []

        celldata = vtk.mutable(1)
        array = vtk.vtkAbstractMapper.GetScalars(polydata, actor.GetMapper().GetScalarMode(),
                actor.GetMapper().GetArrayAccessMode(), actor.GetMapper().GetArrayId(),
                actor.GetMapper().GetArrayName(), celldata)
        if (actor.GetMapper().GetScalarVisibility() and array):
            table = actor.GetMapper().GetLookupTable()
            mode = table.GetVectorMode()
            rgb = table.MapScalars(array, table.GetVectorMode(), table.GetVectorComponent())
            for i in xrange(polydata.GetNumberOfPoints()):
                c = [1.0, 1.0, 1.0]
                alpha = 1.0

                if (mode == 0):#MAGNITUDE):
                    c = rgb.GetTuple(i)
                    mag = c[0]*c[0] + c[1]*c[1] + c[2]*c[2]
                    mag = sqrt(mag)
                    table.GetColor(mag, c)
                    alpha = table.GetOpacity(mag);
                elif (mode == 1):#COMPONENT):   #TODO: NOT WORKING YET
                    mag = rgb.GetComponent(i, table.GetVectorComponent())
                    table.GetColor(mag, c);
                    alpha = table.GetOpacity(mag)
                elif (mode == 2):#RGBCOLORS):
                    c = rgb.GetTuple(i);
                    alpha = actor.GetProperty().GetOpacity()
                    c[0] = c[0]/255.0
                    c[1] = c[1]/255.0
                    c[2] = c[2]/255.0
                _colors.append(c[0])
                _colors.append(c[1])
                _colors.append(c[2])
                _colors.append(alpha)
        else:
            for i in xrange(polydata.GetNumberOfPoints()):
                _colors.append(0.0)
                _colors.append(0.0)
                _colors.append(0.0)
                _colors.append(0.0)
        return _colors


    def __configuringCamera(self):
        if (self.render.IsActiveCameraCreated()):
            camera = self.render.GetActiveCamera()
            self.cameraPos = camera.GetFocalPoint()
            self.cameraUp  = camera.GetViewUp()
            self.cameraEye = camera.GetPosition()
            self.cameraFov = camera.GetViewAngle()
        else:
            #Default VTK Camera
            self.cameraPos = (0.0, 0.0, 1.0)
            self.cameraUp  = (0.0, 1.0, 0.0)
            self.cameraEye = (0.0, 0.0, 0.0)
            self.cameraFov = 30.0

    def __generateHTML(self):
        html = webglHTML(self.title, self.width, self.height)

        #Generating the JavaScript
        js = webglMainJS(self.path)
        for i in xrange(len(self.objects)):
            js.addObject(self.objects[i])

        js.setCameraLookAt(self.cameraFov, self.cameraPos, self.cameraUp, self.cameraEye)
        js.isBackgroundGradient(self.render.GetGradientBackground())
        js.setBackgroundColor(self.render.GetBackground())
        js.setBackgroundColor2(self.render.GetBackground2())
        js.generate()       







