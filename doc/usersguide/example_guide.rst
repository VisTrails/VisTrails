.. _chap-example_guide:

********************************
Module Descriptions and Examples
********************************

.. index:: VisTrails VTK modules

VisTrails VTK modules
=====================

Although most VTK modules in VisTrails would be familiar to vtk users, or at least in the vtk documentation, there are a few modules that VisTrails introduces.  They are used as follows:

* **PythonSource** - Although a PythonSource is in the Basic Modules list rather than VTK, it is mentioned here for convenience.  This module allows you write python statements to be executed as part of the workflow.  See Section :ref:`sec-pythonsource` for more information.

* **VTKCell** - VTKCell is a VisTrails module that can display a vtkRenderWindow inside a cell.  Simply pass it a vtkRenderer and any additional optional inputs, and it will display the results in the spreadsheet.

* **VTKRenderOffscreen** - Takes the output of a vtkRenderer and produces a PNG image of size width X height.  Default values of width and height are 512.  The output can then be written to a file using a FileSink.

* **VTKViewCell** - This is similar to the VTKCell except that you pass it a vtkRenderView.

* **vtkInspectors: vtkDataArrayInspector, vtkDataSetAttributesInspector, vtkDataSetInspector, vtkPolyDataInspector** - These inspectors were created to allow easy access to information that is not otherwise exposed by module ports, but would be accessible through vtk objects.  This information includes: normals, scalars, tensors, and vectors as well as statistical information such as bounds, center, length, max, min.  Looking at the output ports of these inspectors gives an idea of the information available.

.. index:: vtkInteractionHandler

* **vtkInteractionHandler** - The vtkInteractionHandler is used when a callback function is needed.  To setup this handler:

   * Connect the Observer input port to the output port of the object that needs the callback function.  
   * Connect the SharedData input port to the modules that would be passed as parameters to the callback function.  Multiple modules can be connected (see terminator.vt - Images Slices SW).
   * Connect the output port to the VTKCell.
   * Select configure to write the callback function.

      * Name the function after the event that initiates it, but replace 'Event' with 'Handler'.  If the function should be called when a ``StartInteractionEvent`` occurs, the function should be named ``startInteractionHandler``.
      * The function should take the parameters observer, and shareddata.
      * Add the contents of the function.

   There are a number of examples that use the vtkInteractionHandler.  If there is any confusion, comparing the callback/interaction handler portions of the .py and .vt files in the vtk_examples/GUI directory is helpful.

   **Accessing vtkObjects in vtkInteractionHandler** VtkObjects passed to the vtkInteractionHandler are VisTrails modules.  The vtkObject within that module is called a vtkInstance and is accessed by calling myModule.vtkInstance.  See Section :ref:`sec-pythonsource` for more information.

* **vtkScaledTransferFunction** - Allows you to add a transfer function through the use of an interactive widget.  See head.vt - volume rendering or terminator.vt for example usage.

.. _sec-module-example:

Modules and Corresponding Examples
==================================

Here we provide a list of the .vt files in the examples directory that use the following modules:

.. index:: 
   pair: modules; list of examples

* **AreaFilter**: 
   triangle_area.vt* **CellLocation**: 
   offscreen.vt, terminator.vt, vtk.vt* **ConcatenateString**: 
   KEGG_SearchEntities_webservice.vt* **Cross**: 
   triangle_area.vt* **fetchData**: 
   structure_or_id_webservice.vt, protein_visualization.vt* **FileSink**: 
   offscreen.vt - offscreen* **Filter**: 
   triangle_area.vt* **If**: 
   structure_or_id_webservice.vt, protein_visualization.vt* **ImageViewerCell**: 
   r_stats.vt* **List**: 
   triangle_area.vt* **Map**: 
   triangle_area.vt* **MplFigure**: 
   plot.vt, terminator.vt - Histrogram, triangle_area.vt, vtk.vt - Three Cells* **MplFigureCell**: 
   plot.vt, terminator.vt - Histrogram, triangle_area.vt, vtk.vt - Three Cells* **MplPlot**: 
   plot.vt, terminator.vt - Histrogram, triangle_area.vt, vtk.vt - Three Cells* **PythonCalc**: 
   ProbeWithPointWidget.vt, officeTube.vt* **PythonSource**: 
   infovis.vt, noaa_webservices.vt, offscreen.vt, KEGG_SearchEntities_webservice.vt, chebi_webservice.vt, EMBOSS_webservices.vt, structure_or_id_webservice.vt, vtk_http.vt, protein_visualization.vt, terminator.vt, triangle_area.vt* **RichTextCell**: 
   noaa_webservices.vt, offscreen.vt, KEGG_SearchEntities_webservice.vt, chebi_webservice.vt, EMBOSS_webservices.vt, protein_visualization.vt* **RPNGFigure**: 
   r_stats.vt* **RReadCSV**: 
   r_stats.vt* **Rsource**: 
   r_stats.vt* **SheetReference**: 
   offscreen.vt, vtk.vt* **StandardOutput**: 
   r_stats.vt, triangle_area.vt* **Tuple**: 
   marching.vt, ProbingWithPlaneWidget.vt, TransformWithBoxWidget.vt, BandContourTerrain.vt, probeComb.vt, ImplicitPlaneWidget.vt, BuildUGrid.vt, ProbeWithPointWidget.vt, VolumeRenderWithBoxWidget.vt, PerlinTerrain.vt* **Untuple**: 
   probeComb.vt, BandContourTerrain.vt* **vtk3DSImporter**: 
   flamingo.vt* **vtkAppendPolyData**: 
   vtk.vt - Implicit Plane Clipper, xyPlot.vt, TransformWithBoxWidget.vt, probeComb.vt, ImplicitPlaneWidget.vt, warpComb.vt* **vtkAssembly**: 
   assembly.vt* **vtkAxes**: 
   textOrigin.vt* **vtkBandedPolyDataContourFilter**: 
   BandContourTerrain.vt* **vtkBMPReader**: 
   Tplane.vt, imageWarp.vt, GenerateTextureCoords.vt* **vtkBoxWidget**: 
   TransformWithBoxWidget.vt, VolumeRenderWithBoxWidget.vt, cone.vt - 6* **vtkBYUReader**: 
   cubeAxes.vt, ClipCow.vt* **vtkCastToConcrete**: 
   ExtractUGrid.vt* **vtkCellArray**: 
   constrainedDelaunay.vt, Arrays.vt, CreateStrip.vt* **vtkClipPolyData**: 
   terminator.vt, vtk.vt - Implicit Plane Clipper, ImplicitPlaneWidget.vt, ClipCow.vt* **vtkColorTransferFunction**: 
   lung.vt, SimpleRayCast.vt, mummy.xml - volume rendering, SimpleTextureMap2D.vt, VolumeRenderWithBoxWidget.vt* **vtkCone**: 
   iceCream.vt* **vtkConeSource**: 
   vtk_book_3rd_p193.vt, vtk.vt - Implicit Plane Clipper, TransformWithBoxWidget.vt, Cone.vt, ImplicitPlaneWidget.vt, ProbeWithPointWidget.vt, assembly.vt* **vtkConnectivityFilter**: 
   ExtractUGrid.vt, pointToCellData.vt* **vtkContourFilter**: 
   brain_vistrail.vt, spx.vt, vtk_http.vt, marching.vt, head.vt - alias, mummy.xml - Isosurface, terminator.vt, pointToCellData.vt, triangle_area.vt - CalculateArea, Medical1.vt, hello.vt, VisQuad.vt, probeComb.vt, vtk_book_3rd_p189.vt, Medical2.vt, iceCream.vt, Contours2D.vt, Medical3.vt, PerlinTerrain.vt, ColorIsosurface.vt, PseudoVolumeRendering.vt* **vtkCubeAxesActor2D**: 
   cubeAxes.vt* **vtkCubeSource**: 
   assembly.vt, marching.vt* **vtkCutter**: 
   ClipCow.vt, CutCombustor.vt, PseudoVolumeRendering.vt* **vtkCylinderSource**: 
   assembly.vt, cylinder.vt* **vtkDataArrayInspector**: 
   CutCombuster.vt, officeTube.vt* **vtkDataSetAttributesInspector**: 
   officeTube.vt, CutCombustor.vt* **vtkDataSetInspector**: 
   ProbingWithPlaneWidget.vt, StreamlinesWithLineWidget.vt, CutCombustor.vt, officeTube.vt, TextureThreshold.vt, BandContourTerrain.vt, probeComb.vt, ProbeWithPointWidget.vt, rainbow.vt, streamSurface.vt, warpComb.vt* **vtkDataSetMapper**: 
   offscreen.vt, spx.vt, structure_or_id_webservice.vt, vtk_http.vt, SubsampleGrid.vt, TextureThreshold.vt, imageWarp.vt, protein_visualization.vt, head.vt - alias, mummy.xml - Isosurface, terminator.vt - Histogram, pointToCellData.vt, ExtractUGrid.vt, ExtractGeometry.vt, vtk.vt, BuildUGrid.vt, GenerateTextureCoords.vt* **vtkDataSetReader**: 
   brain_vistrail.vt, vtk_http.vt, triangle_area.vt, ExtractUGrid.vt, vtk.vt* **vtkDecimatePro**: 
   smoothFran.vt* **vtkDelaunay2D**: 
   constrainedDelaunay.vt, faultLines.vt* **vtkDelaunay3D**: 
   GenerateTextureCoords.vt* **vtkDEMReader**: 
   BandContourTerrain.vt* **vtkDoubleArray**: 
   Arrays.vt* **vtkExtractEdges**: 
   constrainedDelaunay.vt, marching.vt* **vtkExtractGeometry**: 
   ExtractGeometry.vt* **vtkExtractGrid**: 
   SubsampleGrid.vt, PseudoVolumeRendering.vt - vtkPlane* **vtkExtractUnstructuredGrid**: 
   ExtractUGrid.vt* **vtkExtractVOI**: 
   Contours2D.vt* **vtkFloatArray**: 
   Arrays.vt, BuildUGrid.vt, marching.vt* **vtkFollower**: 
   textOrigin.vt* **vtkGeometryFilter**: 
   ExtractUGrid.vt, pointToCellData.vt* **vtkGlyph3D**: 
   vtk_book_3rd_p193.vt, marching.vt, vtk.vt - Implicit Plane Clipper, TransformWithBoxWidget.vt, ImplicitPlaneWidget.vt, ProbeWithPointWidget.vt, spikeF.vt* **vtkGraphLayoutView**: 
   infovis.vt* **vtkHexahedron**: 
   BuildUGrid.vt* **vtkIcicleView**: 
   infovis.vt* **vtkIdList**: 
   BuildUGrid.vt, marching.vt* **vtkImageActor**: 
   Medical3.vt* **vtkImageDataGeometryFilter**: 
   BandContourTerrain.vt, imageWarp.vt* **vtkImageLuminance**: 
   imageWarp.vt* **vtkImageMapToColors**: 
   brain_vistrail.vt, Medical3.vt* **vtkImageReslice**: 
   terminator.vt* **vtkImageShiftScale**: 
   lung.vt - raycasted* **vtkImageShrink3D**: 
   BandContourTerrain.vt* **vtkImplicitBoolean**: 
   iceCream.vt, ExtractGeometry.vt* **vtkImplicitModeller**: 
   hello.vt* **vtkImplicitPlaneWidget**: 
   terminator.vt, vtk.vt, ImplicitPlaneWidget.vt* **vtkImplicitSum**: 
   PerlinTerrain.vt* **vtkIntArray**: 
   Arrays.vt* **vtkInteractionHandler**: 
   ProbingWithPlaneWidget.vt, StreamlinesWithLineWidget.vt, terminator.vt, vtk.vt - Implicit Plane Clipper, TransformWithBoxWidget.vt, Cone.vt - 6 , ImplicitPlaneWidget.vt, ProbeWithPointWidget.vt, VolumeRenderWithBoxWidget.vt* **vtkInteractorStyleImage**: 
   terminator.vt* **vtkInteractorStyleTrackballCamera**: 
   Cone.vt - 5* **vtkLight**: 
   cubeAxes.vt, faultLines.vt* **vtkLine**: 
   BuildUGrid.vt* **vtkLineSource**: 
   streamSurface.vt, xyPlot.vt* **vtkLineWidget**: 
   StreamlinesWithLineWidget.vt* **vtkLODActor**: 
   TestText.vt, stl.vt, CADPart.vt, vtk.vt - Implicit Plane Clipper, TransformWithBoxWidget.vt, BandContourTerrain.vt, cubeAxes.vt, ImplicitPlaneWidget.vt, FilterCADPart.vt, ColorIsosurface.vt* **vtkLookupTable**: 
   brain_vistrail.vt, vtk_book_3rd_p193.vt, pointToCellData.vt, BandContourTerrain.vt, ExtractUGrid.vt, Medical3.vt, rainbow.vt, PseudoVolumeRendering.vt* **vtkMaskPoints**: 
   vtk_book_3rd_p193.vt, spikeF.vt* **vtkMassProperties**: 
   triangle_area.vt - CalculateArea* **vtkMergeFilter**: 
   imageWarp.vt* **vtkOpenGLVolumeTextureMapper3D**: 
   lung.vt - TextureWithShading* **vtkOutlineFilter**: 
   VisQuad.vt, probeComb.vt, ExtractGeometry.vt, vtk_book_3rd_p189.vt, cubeAxes.vt, VolumeRenderWithBoxWidget.vt, Contours2D.vt, Medical1.vt, Medical2.vt, Medical3.vt* **vtkPDBReader**: 
   protein_visualization.vt, structure_or_id_webservice.vt* **vtkPerlinNoise**: 
   PerlinTerrain.vt* **vtkPiecewiseFunction**: 
   lung.vt, SimpleRayCast.vt, mummy.xml - volume rendering, SimpleTextureMap2D.vt, VolumeRenderWithBoxWidget.vt* **vtkPixel**: 
   BuildUGrid.vt* **vtkPlane**: 
   lung.vt - TS and plane, CutCombustor.vt, terminator.vt, vtk.vt - Implicit Plane Clipper, ImplicitPlaneWidget.vt, iceCream.vt, PerlinTerrain.vt, ClipCow.vt* **vtkPlanes**: 
   VolumeRenderWithBoxWidget.vt* **vtkPlaneSource**: 
   Tplane.vt, terminator.vt, probeComb.vt* **vtkPlaneWidget**: 
   ProbingWithPlaneWidget.vt* **vtkPLOT3DReader**: 
   ProbingWithPlaneWidget.vt, StreamlinesWithLineWidget.vt, CutCombustor.vt, SubsampleGrid.vt, TextureThreshold.vt, xyPlot.vt, probeComb.vt, ProbeWithPointWidget.vt, rainbow.vt, ColorIsosurface.vt, streamSurface.vt, warpComb.vt, PseudoVolumeRendering.vt* **vtkPointData**: 
   marching.vt, Arrays.vt, BuildUGrid.vt* **vtkPointDataToCellData**: 
   pointToCellData.vt* **vtkPoints**: 
   CreateStrip.vt, marching.vt, constrainedDelaunay.vt, Arrays.vt, BuildUGrid.vt* **vtkPointSource**: 
   GenerateTextureCoords.vt, officeTube.vt* **vtkPointWidget**: 
   ProbeWithPointWidget.vt* **vtkPolyData**: 
   CreateStrip.vt, ProbingWithPlaneWidget.vt, constrainedDelaunay.vt, StreamlinesWithLineWidget.vt, Arrays.vt, ProbeWithPointWidget.vt, ClipCow.vt* **vtkPolyDataInspector**: 
   ClipCow.vt* **vtkPolyDataNormals**: 
   brain_vistrail.vt, pointToCellData.vt, Medical1.vt , faultLines.vt, ExtractUGrid.vt, smoothFran.vt, cubeAxes.vt, Medical2.vt, Medical3.vt, ClipCow.vt, ColorIsosurface.vt, warpComb.vt, PerlinTerrain.vt, spikeF.vt, PseudoVolumeRendering.vt, BandContourTerrain.vt* **vtkPolyDataReader**: 
   hello.vt, faultLines.vt, smoothFran.vt, spikeF.vt* **vtkPolygon**: 
   BuildUGrid.vt* **vtkPolyLine**: 
   BuildUGrid.vt* **vtkPolyVertex**: 
   BuildUGrid.vt* **vtkProbeFilter**: 
   brain_vistrail.vt, ProbingWithPlaneWidget.vt, xyPlot.vt, probeComb.vt, ProbeWithPointWidget.vt* **vtkProperty2D**: 
   xyPlot.vt* **vtkPyramid**: 
   BuildUGrid.vt* **vtkQuad**: 
   BuildUGrid.vt* **vtkQuadraticDecimation**: 
   spx.vt - Decimate* **vtkQuadric**: 
   VisQuad.vt, ExtractGeometry.vt, vtk_book_3rd_p189.vt, Contours2D.vt* **vtkRandomGraphSource**: 
   infovis.vt - hello_world* **VTKRenderOffscreen**: 
   offscreen.vt* **vtkRibbonFilter**: 
   StreamlinesWithLineWidget.vt* **vtkRuledSurfaceFilter**: 
   streamSurface.vt* **vtkRungeKutta4**: 
   StreamlinesWithLineWidget.vt, officeTube.vt, streamSurface.vt* **vtkSampleFunction**: 
   VisQuad.vt, ExtractGeometry.vt, vtk_book_3rd_p189.vt, iceCream.vt, Contours2D.vt, PerlinTerrain.vt* **vtkScaledTransferFunction**: 
   head.vt - volume rendering, terminator.vt* **vtkShrinkFilter**: 
   ExtractGeometry.vt* **vtkShrinkPolyData**: 
   marching.vt, filterCADPart.vt* **vtkSmoothPolyDataFilter**: 
   xyPlot.vt* **vtkSphere**: 
   iceCream.vt, ExtractGeometry.vt* **vtkSphereSource**: 
   TestText.vt, marching.vt, assembly.vt, vtk.vt - Implicit Plane Clipper, TransformWithBoxWidget.vt, ImplicitPlaneWidget.vt* **vtkSTLReader**: 
   stl.vt, CADPart.vt, FilterCADPart.vt* **vtkStreamLine**: 
   StreamlinesWithLineWidget.vt, officeTube.vt, streamSurface.vt* **vtkStripper**: 
   brain_vistrail.vt, Medical2.vt, Medical3.vt, ClipCow.vt* **vtkStructuredGridGeometryFilter**: 
   CutCombuster.vt, officeTube.vt, TextureThreshold.vt, rainbow.vt, warpComb.vt* **vtkStructuredGridOutlineFilter**: 
   StreamlinesWithLineWidget.vt, officeTube.vt, SubsampleGrid.vt, TextureThreshold.vt, xyPlot.vt, probeComb.vt, ProbeWithPointWidget.vt, rainbow.vt, ColorIsosurface.vt, streamSurface.vt, warpComb.vt, PseudoVolumeRendering.vt, ProbingWithPlaneWidget.vt, CutCombustor.vt* **vtkStructuredGridReader**: 
   officeTube.vt* **vtkStructuredPointsReader**: 
   lung.vt, vtk_book_3rd_p193.vt, SimpleRayCast.vt, TextureThreshold.vt, head.vt - volume rendering, mummy.xml - volume rendering, head.vt - alias, mummy.xml - Isosurface, terminator.vt, SimpleTextureMap2D.vt* **vtkTetra**: 
   BuildUGrid.vt* **vtkTextActor**: 
   TestText.vt* **vtkTextProperty**: 
   TestText.vt, xyPlot.vt, cubeAxes.vt* **vtkTexture**: 
   Tplane.vt, TextureThreshold.vt, terminator.vt, GenerateTextureCoords.vt* **vtkTextureMapToCylinder**: 
   GenerateTextureCoords.vt* **vtkThreshold**: 
   pointToCellData.vt* **vtkThresholdPoints**: 
   vtk_book_3rd_p193.vt, marching.vt* **vtkThresholdTextureCoords**: 
   TextureThreshold.vt* **vtkTransform**: 
   marching.vt, terminator.vt, xyPlot.vt, TransformWithBoxWidget.vt, Cone.vt - 6, probeComb.vt, ExtractGeometry.vt, spikeF.vt* **vtkTransformPolyDataFilter**: 
   marching.vt, xyPlot.vt, probeComb.vt, spikeF.vt* **vtkTransformTextureCoords**: 
   GenerateTextureCoords.vt* **vtkTreeMapView**: 
   infovis.vt* **vtkTreeRingView**: 
   infovis.vt* **vtkTriangle**: 
   BuildUGrid.vt* **vtkTriangleFilter**: 
   triangle_area.vt - CalculateArea, ClipCow.vt* **vtkTriangleStrip**: 
   BuildUGrid.vt* **vtkTubeFilter**: 
   marching.vt, constrainedDelaunay.vt, officeTube.vt, officeTubes.vt, xyPlot.vt, faultLines.vt, PseudoVolumeRendering.vt* **vtkUnstructuredGrid**: 
   BuildUGrid.vt, marching.vt* **vtkUnstructuredGridReader**: 
   offscreen.vt, spx.vt, pointToCellData.vt* **vtkVectorText**: 
   textOrigin.vt, marching.vt* **vtkVertex**: 
   BuildUGrid.vt* **VTKViewCell**: 
   infovis.vt* **vtkViewTheme**: 
   infovis.vt - cone_layout* **vtkVolume**: 
   lung.vt, SimpleRayCast.vt, head.vt - volume rendering, mummy.xml - volume rendering, terminator.vt, SimpleTextureMap2D.vt, VolumeRenderWithBoxWidget.vt* **vtkVolume16Reader**: 
   VolumeRenderWithBoxWidget.vt, Medical1.vt, Medical2.vt, Medical3.vt* **vtkVolumeProperty**: 
   lung.vt, SimpleRayCast.vt, head.vt - volume rendering, mummy.xml - volume rendering, terminator.vt, SimpleTextureMap2D.vt, VolumeRenderWithBoxWidget.vt* **vtkVolumeRayCastCompositeFunction**: 
   lung.vt - raycasted, SimpleRayCast.vt, mummy.xml - volume rendering, terminator.vt - SW, VolumeRenderWithBoxWidget.vt* **vtkVolumeRayCastMapper**: 
   lung.vt - raycasted, SimpleRayCast.vt, mummy.xml - volume rendering, terminator.vt - SW, VolumeRenderWithBoxWidget.vt* **vtkVolumeTextureMapper2D**: 
   SimpleTextureMap2D.vt* **vtkVolumeTextureMapper3D**: 
   head.vt - volume rendering, terminator.vt - HW* **vtkVoxel**: 
   BuildUGrid.vt* **vtkWarpScalar**: 
   imageWarp.vt, BandContourTerrain.vt, warpComb.vt* **vtkWarpVector**: 
   pointToCellData.vt, ExtractUGrid.vt* **vtkWedge**: 
   BuildUGrid.vt* **vtkWindowLevelLookupTable**: 
   terminator.vt* **vtkXMLTreeReader**: 
   infovis.vt* **vtkXYPlotActor**: 
   xyPlot.vt
