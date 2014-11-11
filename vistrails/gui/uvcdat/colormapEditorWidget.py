from PyQt4 import QtCore,QtGui
import customizeUVCDAT
import os
import uvcdatCommons
import core
import core.db
from packages.uvcdat_cdms.pipeline_helper import CDMSPipelineHelper
from core.modules.module_registry import get_module_registry
import core.system
import api


def parseLayout(l,prefix=""):
    for i in range(l.count()):
        it=l.itemAt(i)
        print prefix,i,it.__class__
        if isinstance(it,QtGui.QWidgetItem):
            w=it.widget()
            print prefix,w,
            if isinstance(w,(QtGui.QPushButton,QtGui.QLabel)):
                print prefix,w.text()
            else:
                print
        elif isinstance(it,QtGui.QLayoutItem):
            print prefix,it.__class__
            l2 = it.layout()
            if l2 is None:
                print "No Layout"
            else:
                parseLayout(l2,"%s\t" % prefix)
                
class QColormapEditor(QtGui.QColorDialog):
    def __init__(self,parent):
        QtGui.QColorDialog.__init__(self,parent)
        self.parent=parent
        self.root=parent.root
        self.setOption(QtGui.QColorDialog.DontUseNativeDialog,True)
        self.activeCanvas = self.root.canvas[0]

        self.vcscolor=[0,0,0]
        self.ignoreColorMapComboChange = False
        ## l = QtGui.QVBoxLayout()

        l = self.layout()

        self.nclicks = 0
        self.clicks=[None,None]
        self.currentPlots = []
        #parseLayout(l)

        editColor = l.itemAt(0)
        buttons = l.takeAt(1)
        #l.removeItem(editColor)
        #l.removeItem(buttons)
        #l.addItem(editColor)

        ## Colormap selection Area
        f = QtGui.QFrame()
        h = QtGui.QHBoxLayout()
        colormaps = sorted(self.activeCanvas.listelements("colormap"))
        self.colormap = QtGui.QComboBox(self)
        for i in colormaps:
            self.colormap.addItem(i)
            
        h.addWidget(self.colormap)
        self.newname = QtGui.QLineEdit()
        h.addWidget(self.newname)
        b=QtGui.QPushButton("Rename")
        self.connect(b,QtCore.SIGNAL("clicked()"),self.renamed)
        h.addWidget(b)
        f.setLayout(h)
        l.addWidget(f)

        ## Toolbar section
        self.toolBar = QtGui.QToolBar()
        self.toolBar.setIconSize(QtCore.QSize(customizeUVCDAT.iconsize, customizeUVCDAT.iconsize))
        icons_base = os.path.join(core.system.vistrails_root_directory(),
                                  'gui/uvcdat/resources/icons')
        action_info = [
            (icons_base + '/folder_blue.png', 'Save Colormap To File.', self.save, True),
            (icons_base + '/blender.png', 'Blend From First To Last Highlighted Colors.', self.blend, True),
            (icons_base + '/refresh.png', 'Reset Changes.', self.resetChanges, True),
            (icons_base + '/check.png', 'Apply Changes.', self.applyChanges, True),
        ]
        for icon_name, tooltip, callback, enabled in action_info:
            icon = QtGui.QIcon(os.path.join(customizeUVCDAT.ICONPATH, icon_name))
            action = self.toolBar.addAction(icon, 'help')
            action.setToolTip(tooltip)
            self.connect(action, QtCore.SIGNAL("triggered()"), callback)
            action.setEnabled(enabled)

        # add combo box to select which plot's colormap to update
        # self.plotCb = QtGui.QComboBox(self)
        # self.toolBar.addWidget(self.plotCb)

        l.addWidget(self.toolBar)

        # Color Buttons Are
        self.colors=QtGui.QFrame()
        self.grid = QtGui.QGridLayout()
        self.grid.setHorizontalSpacing(1)
        self.grid.setVerticalSpacing(1)
        self.colors.setLayout(self.grid)
        l.addWidget(self.colors)

        # Ok/Cancel Buttons
        self.connect(buttons.widget(),QtCore.SIGNAL("accepted()"),self.applyChanges)
        #self.connect(buttons.widget(),QtCore.SIGNAL("rejected()"),self.resetChanges)
        l.addItem(buttons)
        self.buttons = buttons
        
        ## select the colormap before connecting
        self.colormap.setCurrentIndex(colormaps.index(self.activeCanvas.getcolormapname()))

        ## Need to deactivate if default (not editable)
        if self.activeCanvas.getcolormapname() == "default":
            self.buttons.widget().setEnabled(False)

        ## SIGNALS
        self.connect(self.colormap,QtCore.SIGNAL("currentIndexChanged(int)"),self.colorMapComboChanged)
        self.connect(self,QtCore.SIGNAL("currentColorChanged(QColor)"),self.colorChanged)
        #self.connect(self.plotCb,QtCore.SIGNAL("currentIndexChanged(int)"),self.plotsComboChanged)


    def getRgb(self,i,j=None,max=255):
        if j is None:
            if max>=100:
                mx = max/100.
            else:
                mx=max
            nr,ng,nb = self.cmap.index[i]
            nr=int(nr*mx)
            ng=int(ng*mx)
            nb=int(nb*mx)
        else:
            if max>=100:
                mx=max/255.
            else:
                mx=max
            styles = str(self.grid.itemAtPosition(i,j).widget().styleSheet()).split(";")
            for style in styles:
                sp =style.split(":")
                if sp[0].strip() == "background-color":
                        
                    r,g,b = eval(sp[1].strip()[4:-1])
                    r=int(r*mx)
                    g=int(g*mx)
                    b=int(b*mx)
                    return r,g,b
            return 0,0,0
            
        return nr,ng,nb

    def activateFromCell(self,canvas):
        self.activeCanvas = canvas
        self.setColorsFromCanvas()
        
        self.controller = api.get_current_controller()
        self.version = self.controller.current_version
        self.pipeline = self.controller.vistrail.getPipeline(self.version)
        self.plots = CDMSPipelineHelper.find_plot_modules(self.pipeline)
        
        #set up plot combo box
#        self.plotCb.clear()
#        for i in range(len(self.plots)):
#            found = False
#            for func in self.plots[i].functions:
#                if func.name == 'graphicsMethodName':
#                    self.plotCb.addItem(self.plots[i].module_descriptor.module.plot_type \
#                        + '_' + func.params[0].strValue, userData=i)
#                    found = True                
#            if not found:
#                self.plotCb.addItem(self.plots[i].module_descriptor.module.plot_type, userData=i)                
#        self.plotCb.setCurrentIndex(0)
        
        self.mapNameChanged = False
        self.cellsDirty = False
        self.show()        
        
    def plotsComboChanged(self):
        self.setColorsFromPlot(self.currentPlot())
            
    def currentPlot(self):
        return self.plots[0] # remove this when switch to multi-colormap cells
        if self.plotCb.count() > 0:
            (localPlotIndex, success) = self.plotCb.itemData(self.plotCb.currentIndex()).toInt()
            if success:
                return self.plots[localPlotIndex]
            else:
                return self.plots[0]
        else:
            return None
        
    def colorMapComboChanged(self):
        if not self.ignoreColorMapComboChange:
            self.mapNameChanged = True
            self.setColorsFromMapName()
        
    def setColorsFromMapName(self):
        #n = self.layout().count()
        ## Need to deactivate if default (not editable)
        if str(self.colormap.currentText()) == "default":
            self.buttons.widget().setEnabled(False)
        else:
            self.buttons.widget().setEnabled(True)
        self.cellsDirty = False
        cmap = self.activeCanvas.getcolormap(str(self.colormap.currentText()))
        #self.colors=QtGui.QFrame()
        #rec= "##Changing colormap\nvcs_canvas[%i].setcolormap('%s')" % (self.activeCanvas.canvasid()-1,str(self.colormap.currentText()))
        #self.activeCanvas.setcolormap(str(self.colormap.currentText()))

        n = 0
        for i in range(15):
            for j in range(16):
                r,g,b = cmap.index[n]
                r=int(r*2.55)
                g=int(g*2.55)
                b=int(b*2.55)
                self.setButton(i,j,n,r,g,b)
                n+=1
        self.update()
        
    def setColorsFromCanvas(self):
        # get current colormapname from canvas
        self.ignoreColorMapComboChange = True
        newIdx = self.colormap.findText(self.activeCanvas.getcolormapname())
        self.colormap.setCurrentIndex(newIdx)
        self.ignoreColorMapComboChange = False
        
        n = 0
        for i in range(15):
            for j in range(16):
                r,g,b = self.activeCanvas.getcolorcell(n)
                r=int(r*2.55)
                g=int(g*2.55)
                b=int(b*2.55)
                self.setButton(i,j,n,r,g,b)
                n+=1
        
        
    def setColorsFromPlot(self, plot):
        pass
#        mapName = None
#        cells = None
#        loadedBaseColorMap = False
#        colorMapModule = self.colorMapModuleFromPlot(plot)
#        if colorMapModule is not None:
#            mapName = colorMapModule.colorMapName            
#            if mapName is not None:
#                currentIdx = self.colormap.currentIndex()
#                newIdx = self.colormap.findText(mapName)
#                if newIdx != currentIdx:
#                    self.colormap.setCurrentIndex(newIdx)
#                    loadedBaseColorMap = True
#                cells = colorMapModule.colorCells
#        
#        if not loadedBaseColorMap:
#            self.setColorsFromMapName()
#                
#        #set custom user defined colors
#        if cells is not None:
#            for (n,r,g,b) in cells:
#                j = n % 16
#                i = (n-j) / 16
#                r=int(r*2.55)
#                g=int(g*2.55)
#                b=int(b*2.55)
#                self.setButton(i,j,n,r,g,b)
#                
#        self.update()
        
    def colorMapModuleFromPlot(self, plot):
        conns = self.controller.get_connections_to(self.pipeline, [plot.id], 
                                                   port_name="colorMap")
        if len(conns) > 0:
            if len(conns) > 1:
                print "WARNING: Multiple colormaps for a single plot"
            return self.pipeline.modules[conns[0].source.moduleId]
        return None
        
    def applyChanges(self):
        plot = self.currentPlot()
        
        rec="## Updating colorcells"
        self.root.record(rec)
#        cnm = self.activeCanvas.getcolormapname()
#        self.activeCanvas.setcolormap(cnm)

        if not self.mapNameChanged and not self.cellsDirty:
            return;
        
        rec="vcs_canvas[%i].setcolormap(\"%s\")" \
            % (self.activeCanvas.canvasid()-1,self.colormap.currentText())
        self.root.record(rec)
        self.activeCanvas.setcolormap(str(self.colormap.currentText()))
            
        cells = []
        if self.cellsDirty:
            n=0
            for i in range(15):
                for j in range(16):
                    r,g,b = self.getRgb(i,j,max=100)
                    ored,og,ob = self.activeCanvas.getcolorcell(n)
                    if r!=ored or og!=g or ob!=b:
                        rec="vcs_canvas[%i].setcolorcell(%i,%i,%i,%i)" % (self.activeCanvas.canvasid()-1,n,r,g,b)
                        self.root.record(rec)
                        #self.activeCanvas.setcolorcell(n,r,g,b)
                        #calling this directly to avoid flushing and updating segments on every cell update
                        self.activeCanvas.setcolorcell(n,r,g,b);
                        cells.append((n,r,g,b))
                    n+=1
            #see vcs.Canvas.setcolorcell
            self.activeCanvas.update(self.activeCanvas.mode) # pass down self and mode to _vcs module
            self.activeCanvas.flush() # update the canvas by processing all the X events
        
        self.controller.change_selected_version(self.controller.current_version)
        
        functions = [("colorMapName",[str(self.colormap.currentText())])]
        functions.append(("colorCells",[str(cells)]))
        
        action = None        
        colorMapModule = self.colorMapModuleFromPlot(plot)
        if colorMapModule is not None: #update module
            action = self.controller.update_functions(colorMapModule, functions)
        else: #create module
            reg = get_module_registry()
            color_descriptor = reg.get_descriptor_by_name('gov.llnl.uvcdat.cdms', 
                                           'CDMSColorMap')
            colorMapModule = self.controller.create_module_from_descriptor(color_descriptor)
            module_functions = self.controller.create_functions(colorMapModule, functions)
            for f in module_functions:
                colorMapModule.add_function(f)
            conn = self.controller.create_connection(colorMapModule, 'self', plot, 'colorMap')
    
            ops = [('add', colorMapModule), ('add', conn)]
            action = core.db.action.create_action(ops)
            
            if action is not None:             
                self.controller.add_new_action(action)
                self.controller.perform_action(action)
            
        if action is not None:
            if hasattr(self.controller, 'uvcdat_controller'):
                self.controller.uvcdat_controller.cell_was_changed(action)
            #self.controller.change_selected_version(action.id)
        
    def resetChanges(self):
        #self.setColorsFromPlot(self.currentPlot())
        self.activateFromCell(self.activeCanvas)
                
    def colorChanged(self):
        current = self.currentColor()
        #nr,ng,nb = self.getRgb(self.vcscolor[2])
        cr,cg,cb,ca = current.getRgb()
        #if cr!=nr or cg!=ng or cb!=nb:
        b = self.setButton(self.vcscolor[0],self.vcscolor[1],self.vcscolor[2],cr,cg,cb)
        self.setAButtonFrame(b)
        self.cellsDirty = True
            
    def save(self): 
        out = QtGui.QFileDialog.getSaveFileName(self,"JSON File",filter="json Files (*.json *.jsn *.JSN *.JSON) ;; All Files (*.*)",options=QtGui.QFileDialog.DontConfirmOverwrite)
        cmap = self.activeCanvas.getcolormap(str(self.colormap.currentText()))
        cmap.script(out)

    def renamed(self):
        newname = str(self.newname.text())
        newcmap = self.activeCanvas.createcolormap(newname,str(self.colormap.currentText()))
        self.colormap.addItem(newname)
        self.colormap.model().sort(0)
        self.colormap.setCurrentIndex(self.colormap.findText(newname))
        pass

    def colorButtonClicked(self,b):
# Ben: not sure why this is needed
#        current = self.currentColor()
#        nr,ng,nb = self.getRgb(b.vcscolor[2])
#        cr,cg,cb,ca = current.getRgb()
#        if cr!=nr or cg!=ng or cb!=nb:
        self.vcscolor = b.vcscolor
#            self.setCurrentColor(QtGui.QColor(nr,ng,nb))
        self.nclicks+=1
        if self.nclicks==3:
            self.nclicks=1
        else:
            self.clicks[self.nclicks-1]=b.vcscolor
        self.setButtonFrame(b)
        self.clicks[self.nclicks-1]=b.vcscolor

    def setButtonFrame(self,button):
        firstButton = self.clicks[0]
        i0,j0 = firstButton[:2]
        lastButton = self.clicks[1]
        if lastButton is not None: # Not the first time
            i1,j1 = lastButton[:2]
            if i1<i0:
                tmp1 = i0
                tmp2=j0
                i0=i1
                j0=j1
                i1=tmp1
                j1=tmp2
            elif i0==i1 and j1<j0:
                tmp1=j0
                j0=j1
                j1=tmp1
                
            for i in range(i0,i1+1):
                if i==i0:
                    ij0=j0
                else:
                    ij0=0
                if i==i1:
                    ij1=j1+1
                else:
                    ij1=16
                for j in range(ij0,ij1):
                    ob = self.grid.itemAtPosition(i,j).widget()
                    if self.nclicks==2:
                        self.setAButtonFrame(ob)
                    else:
                        self.setAButtonFrame(ob,on=False)
            if self.nclicks==1:
                self.setAButtonFrame(button)
        else:
            self.setAButtonFrame(button)


    def blend(self):
        first = None
        last = None
        n=0
        for i in range(15):
            for j in range(16):
                b= self.grid.itemAtPosition(i,j).widget()
                stsh = str(b.styleSheet())
                if stsh.find(customizeUVCDAT.colorSelectedStyle)>-1:
                    n+=1
                    if first is None:
                        first = b.vcscolor
                    else:
                        last = b.vcscolor
        if n<2:
            return

        fr,fg,fb = self.getRgb(*first[:2])
        lr,lg,lb = self.getRgb(*last[:2])

        
        dr = float(lr-fr)/float(n-1)
        dg = float(lg-fg)/float(n-1)
        db = float(lb-fb)/float(n-1)

        n=0
        if first[0] < last[0]+1:
            self.cellsDirty = True
        for i in range(first[0],last[0]+1):
            if i == first[0]:
                j0 = first[1]
            else:
                j0=0
            if i== last[0]:
                j1=last[1]+1
            else:
                j1=16
            for j in range(j0,j1):
                button = self.grid.itemAtPosition(i,j).widget()
                r= int(fr+n*dr)
                g= int(fg+n*dg)
                b= int(fb+n*db)
                self.setButton(i,j,button.vcscolor[2],r,g,b)
                self.setAButtonFrame(button)
                n+=1
        
        button = self.grid.itemAtPosition(first[0],first[1]).widget()
        button.click()
        button = self.grid.itemAtPosition(last[0],last[1]).widget()
        button.click()
        
    def setAButtonFrame(self,button,on=True):
        styles = str(button.styleSheet()).split(";")
        newstyles=[]
        for style in styles:
            sp=style.split(":")
            if sp[0].strip() not in ["border"]:
                newstyles.append(":".join(sp))
        if on:
            newstyles.append(customizeUVCDAT.colorSelectedStyle)
        else:
            newstyles.append(customizeUVCDAT.colorNotSelectedStyle)
            
        styles=";".join(newstyles)
        button.setStyleSheet(styles)
        
        
    def setButton(self,i,j,icolor,r,g,b):
        it = self.grid.itemAtPosition(i,j)
        if it is not None:
            self.grid.removeItem(it)
            it.widget().destroy()
        button = uvcdatCommons.CalcButton("%i" % icolor,styles={},signal="clickedVCSColorButton",minimumXSize=15,minimumYSize=15)
        stsh = button.styleSheet()
        stsh+=" background-color : rgb(%i,%i,%i)" % (r,g,b)
        if g<200:
            stsh+=";color : white"
        button.setStyleSheet(stsh)
        button.vcscolor=(i,j,icolor)
        self.connect(button,QtCore.SIGNAL("clickedVCSColorButton"),self.colorButtonClicked)
        self.grid.addWidget(button,i,j)
        return button
        
        
    
