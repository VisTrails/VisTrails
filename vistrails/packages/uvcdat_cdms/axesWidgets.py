
from PyQt4 import QtGui, QtCore
import cdutil
import cdms2
import numpy
import genutil
import re, copy
import cdtime
import MV2
from gui.application import get_vistrails_application
import customizeUVCDAT

pins = {}

## class QAxisListTabWidget(QtGui.QTabWidget):
##     """ TabWidget where each tab contains a QAxisList """
    
##     def __init__(self, parent=None):
##         QtGui.QTabWidget.__init__(self, parent)
##         self.root = parent.root

##         self.connect(self, QtCore.SIGNAL('currentChanged(int)'),
##                      self.tabChangeEvent)        

##     def createNewTab(self, axisList, tabName):
##         """ Create a new tab given the axisList widget and tab name.  If a
##         tab with the same name exists already, replace it. Set the current tab
##         to the newly created tab """

##         if (self.tabExists(tabName)):
##             self.removeTab(self.getTabIndexFromName(tabName))

##         if str(tabName).find("(in file)")>-1:
##             if str(self.tabText(0)).find("(in file)")>-1:
##                 self.removeTab(0)
##             self.insertTab(0, axisList, tabName) # file is always first tab
##         else:
##             self.addTab(axisList, tabName)
            
##         self.setTabTip(tabName)
##         self.setCurrentIndex(self.getTabIndexFromName(tabName))

##     def setupQuickplotTab(self, axisList):
##         """ Create a new quickplot tab if one doesn't exist otherwise replace
##         the existing quickplot tab """

##         tabName = 'quickplot'
##         if (self.tabExists(tabName) == True):
##             index = self.getTabIndexFromName(tabName)
##             self.removeTab(index)
            
##         self.insertTab(0, axisList, tabName)
##         self.setTabTip(tabName)
##         self.setCurrentIndex(0)

##     def setTabTip(self, tabName):
##         if self.tabExists(tabName):
##             index = self.getTabIndexFromName(tabName)
##             toolTip = "'%s' axisList tab widget" % tabName
##             self.setTabToolTip(index, toolTip)        

##     def tabChangeEvent(self, tabIndex):
##         """ Event handler for when a tab is changed. Update the variable info
##         text box.
##         """
##         axisList = self.widget(tabIndex)
##         self.parent().parent().updateVarInfo(axisList) # double parent here 'cause it's on a splitter

##     def selectAndUpdateDefinedVarTab(self, tabName, cdmsFile, var):
##         """ This function selects a tab given the tabName and then updates the
##         tab's axisList using the passed var's values
##         """
##         if (not self.tabExists(tabName)):
##             raise NameError("Error: tab '%s' was not found" % tabName)

##         tabIndex = self.getTabIndexFromName(tabName)
##         self.setCurrentIndex(tabIndex)

##         if (tabName == 'quickplot'):
##             axisList = QAxisList(cdmsFile, var, self)            
##             self.setupQuickplotTab(axisList)
##             axisList.setupVariableAxes()
##         else:
##             axisList = self.currentWidget()
##             axisList.setupVariableAxes()

##         self.emit(QtCore.SIGNAL('updateVarInfo'), axisList)        

##     def tabExists(self, name):
##         """ Returns True if a tab with the given name exists """
##         numTabs = self.count()        
##         for i in range(numTabs):
##             if (name == self.tabText(i)):
##                 return True
##         return False

##     def getTabIndexFromName(self, name):
##         numTabs = self.count()
##         for i in range(numTabs):
##             if (name == self.tabText(i)):
##                 return i
##         return None

##     def currentTabName(self):
##         currentTab = self.currentIndex()
##         return str(self.tabText(currentTab))

#def copy_axis( axis ):
#    axis1 = axis.subAxis( 0, axis.length )
#    if axis.isCircular(): axis1.designateCircular(360.0)
#    return axis1

class QSliderCombo(QtGui.QWidget):
    """ Widget containing min slider, max slider, min label, max label, and a
    corresponding combo box.  The comboBox, labels, sliders must always be in
    sync with each other """

    def __init__(self, axis, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.isTime = axis.isTime()
        self.indexMode = False
        self.startIndex = 0
        self.isModuloed = False
        self.isLat = False
        self.isLon = False

        # Init Layout
        hbox = QtGui.QHBoxLayout()
        vbox = QtGui.QVBoxLayout()
        vbox.setSpacing(0)
        vbox.setMargin(0)        
        self.setLayout(hbox)

        # Init combo box
        self.axisCombo = QAxisComboWidget()
        hbox.addWidget(self.axisCombo)

        # Init sliders
        hbox.addLayout(vbox)
        self.topLabel = QtGui.QLabel('From', self)
        hbox = QtGui.QHBoxLayout()        
        hbox.addWidget(self.topLabel)
        vbox.addLayout(hbox)
        self.topSlider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.topSlider.setTickPosition(QtGui.QSlider.TicksAbove)
        tip = "Use left/right arrows to move slider by 1 unit"
        self.topSlider.setToolTip(tip)
        self.bottomSlider = QtGui.QSlider(QtCore.Qt.Horizontal)        
        self.bottomSlider.setTickPosition(QtGui.QSlider.TicksBelow)
        self.bottomSlider.setToolTip(tip)
        vbox.addWidget(self.topSlider)
        vbox.addWidget(self.bottomSlider)

        # Init axis slider value labels
        self.bottomLabel = QtGui.QLabel('To', self)
        self.bottomLabel.setAlignment(QtCore.Qt.AlignRight)
        aLabel = QtGui.QLabel('', self)
        hbox = QtGui.QHBoxLayout()        
        #hbox.addWidget(aLabel)
        hbox.addWidget(self.bottomLabel)
        vbox.addLayout(hbox)

        # Initialize the sliders' and comboBox's values
#        self.initialAxis = copy_axis( axis )
        self.initAxisValues(axis)
        self.setSlidersMinMax()
        reload(customizeUVCDAT)
        Trange = getattr(customizeUVCDAT,"timeRange",None)
        Zrange = getattr(customizeUVCDAT,"levelRange",None)
        Yrange = getattr(customizeUVCDAT,"latitudeRange",None)
        Xrange = getattr(customizeUVCDAT,"longitudeRange",None)
        if self.isModuloed:
            self.updateTopSlider(self.findAxisIndex(axis[0]))
        else:
            self.topSlider.setValue(self.minIndex)
            
        if self.isModuloed:
            self.updateBottomSlider(self.findAxisIndex(axis[-1]))
        else:
            self.bottomSlider.setValue(self.maxIndex)
        self.axisCombo.initValues(self.axisValues)

        # Connect Signals
        self.connect(self.topSlider, QtCore.SIGNAL('valueChanged (int)'),
                     self.updateMin)
        self.connect(self.bottomSlider, QtCore.SIGNAL('valueChanged (int)'),
                     self.updateMax)
        self.connect(self.axisCombo,
                     QtCore.SIGNAL('axisComboMinValueChanged (int)'),
                     self.updateTopSlider)
        self.connect(self.axisCombo,
                     QtCore.SIGNAL('axisComboMaxValueChanged (int)'),
                     self.updateBottomSlider)

        if axis.isTime() and Trange is not None:
            self.topSlider.setValue(self.findAxisIndex(Trange[0]))
            self.updateMin(self.findAxisIndex(Trange[0]))
            self.bottomSlider.setValue(self.findAxisIndex(Trange[1]))
            self.updateMax(self.findAxisIndex(Trange[1]))
        elif axis.isLevel() and Zrange is not None:
            self.topSlider.setValue(self.findAxisIndex(Zrange[0]))
            self.updateMin(self.findAxisIndex(Zrange[0]))
            self.bottomSlider.setValue(self.findAxisIndex(Zrange[1]))
            self.updateMax(self.findAxisIndex(Zrange[1]))
        elif axis.isLatitude() and Yrange is not None:
            self.topSlider.setValue(self.findAxisIndex(Yrange[0]))
            self.updateMin(self.findAxisIndex(Yrange[0]))
            self.bottomSlider.setValue(self.findAxisIndex(Yrange[1]))
            self.updateMax(self.findAxisIndex(Yrange[1]))
        elif axis.isLongitude() and Xrange is not None:
            self.topSlider.setValue(self.findAxisIndex(Xrange[0]))
            self.updateMin(self.findAxisIndex(Xrange[0]))
            self.bottomSlider.setValue(self.findAxisIndex(Xrange[1]))
            self.updateMax(self.findAxisIndex(Xrange[1]))
        elif self.isModuloed and not (axis.isLongitude() and Xrange is not None):
            self.updateMin(self.findAxisIndex(axis[0]))
            self.updateMax(self.findAxisIndex(axis[-1]))

        #Ok at tht point let see if it is a "pinned" axis
        if axis.isTime():
            k="UVTIMEAXIS"
        elif axis.isLatitude():
            k="UVLATAXIS"
            self.isLat = True
        elif axis.isLongitude():
            k="UVLONAXIS"
            self.isLon = True
        elif axis.isLevel():
            k="UVLEVELAXIS"
        else:
            k=axis.id
        if k in pins and pins[k]["pinned"]:
            v1,v2=pins[k]["vals"]
            if axis.isTime():
                v1=cdtime.s2r(v1,axis.units,axis.getCalendar()).value
                v2=cdtime.s2r(v2,axis.units,axis.getCalendar()).value
            try: # If this fails then we don't need to worry about resetting or pinning this guy he's outside the range
                # But if it fails other should still be able to be pinned
                i1,i2=axis.mapInterval((v1,v2))
                self.updateTopSlider(i1)
                self.updateBottomSlider(i2)
                self.parent().pin.click()
            except:
                pass
            
    def checkBounds( self, bounds, dataset ):
        from gui.application import get_vistrails_application
        values = sorted( self.axisValues )
        if ( bounds[0] < values[0] ) or ( bounds[1] > values[-1] ):
            bounds[0] = max( bounds[0], values[0]  )
            bounds[1] = min( bounds[1], values[-1] )
            parent = get_vistrails_application().uvcdatWindow.varProp.roiSelector
            if dataset == None: QtGui.QMessageBox.warning( parent, "UVCDAT Warning", "Selected bounds are out of range for the transient variable. Please reaccess this variable from the dataset.")
            else:               QtGui.QMessageBox.warning( parent, "UVCDAT Warning", "Selected bounds are out of range for the dataset.")
        return bounds
#            self.resetValues()
                
    def resetValues( self, axis = None ):     
        values = self.setDefaultAxisValues() if ( axis == None ) else self.initAxisValues( axis ) 
        if values <> None:
            self.setSlidersMinMax()
            if self.isModuloed:
                self.updateTopSlider(self.findAxisIndex(values[0]))
            else:
                self.topSlider.setValue(self.minIndex)
                
            if self.isModuloed:
                self.updateBottomSlider(self.findAxisIndex(values[-1]))
            else:
                self.bottomSlider.setValue(self.maxIndex)
            self.axisCombo.initValues(self.axisValues)
   
    def findAxisIndex(self,val):
        self.axisValues = numpy.array(self.axisValues)
        vals = self.axisValues
        n = len(vals)
        if vals[-1]<vals[0]:
            vals=vals[::-1]
        i=vals.searchsorted(val)
        if i>0 and i!=n:
            if (val-vals[i-1])<(vals[i]-val): # closer from lower bound
                i-=1
        if self.axisValues[-1]<self.axisValues[0]:
            i=n-1-i
        return i
    
    def initAxisValues(self, axis):
        """ Initialize list containing the axis values and set the top slider /
        combobox value to be the min value and the bottom slider / combobox
        value to be the max value"""
        
        if (axis != None):
            for coordlbls in ["coordinates","coord_labels",]:
                lbls=getattr(axis,coordlbls,None)
                if lbls is not None:
                    break
            if self.isTime:
                try:
                    self.axisValues = [repr(t.tocomponent(axis.getCalendar()))
                                       for t in axis.asRelativeTime()]
                except:
                    self.axisValues = axis.getValue()                    
            elif lbls is not None:
                try:
                    lbls = eval(lbls)
                except:
                    pass
                if isinstance(lbls,(list,tuple)):
                    self.axisValues = lbls
                elif isinstance(axis,cdms2.axis.FileAxis):
                    ## All right let's fecth the coords
                    try:
                        lbls = axis.parent(lbls)
                        vals =[]
                        if lbls.rank()!=2 or lbls.shape[0]!=len(axis):
                            vals = axis.getValue()
                        else:
                            for i in range(len(axis)):
                                vals.append(lbls[i].tostring().strip())
                        self.axisValues = vals
                    except:
                        self.axisValues = axis.getValue()
                else:
                    self.axisValues = axis.getValue()                    
            else:
                self.axisValues = axis.getValue()
        else:
            raise TypeError("Error: axis is not defined")

        self.axisIndices = range(len(self.axisValues))
        ## Ok here we check for circular axes
        if axis.isCircular():
            try:
                modulo = float(axis.modulo)
            except:
                if axis.isLongitude():
                    modulo=360.
                else:
                    modulo = None
            if modulo is not None and self.isModuloed is False:
                self.isModuloed = True
                n=len(axis)
                self.axisValues=numpy.concatenate((self.axisValues[:]-modulo,self.axisValues,self.axisValues[:]+modulo))
                self.axisIndices=numpy.concatenate((self.axisIndices[:],self.axisIndices,self.axisIndices[:]))
        self.updateMin(0)
        self.updateMax(len(self.axisValues) - 1)
        nticks = len(self.axisValues)
        if nticks > 15:
            nticks /= 15
        else:
            nticks=1
        self.topSlider.setTickInterval(nticks)
        self.bottomSlider.setTickInterval(nticks)
        return self.axisValues

    def setDefaultAxisValues( self ):               
        if self.isLat:  axisValues = [ float(fval) for fval in range(0,360) ]
        if self.isLon:  axisValues = [ float(fval) for fval in range(-90,90) ]
        else:           axisValues = None 
        if axisValues:
            n=len(axisValues)
            self.axisValues = numpy.array( axisValues )  
            self.axisIndices = range(n)
            if self.isLon:
                modulo = 360.0
                self.isModuloed = True
                self.axisValues=numpy.concatenate((self.axisValues[n/2:]-modulo,self.axisValues,self.axisValues[:n/2]+modulo))
                self.axisIndices=numpy.concatenate((self.axisIndices[n/2:],self.axisIndices,self.axisIndices[:n/2]))
                n=len(axisValues)
            self.updateMin(0)
            self.updateMax(n - 1)
            nticks = n
            if nticks > 15:
                nticks /= 15
            else:
                nticks=1
            self.topSlider.setTickInterval(nticks)
            self.bottomSlider.setTickInterval(nticks)
        return self.axisValues

    def setStartIndex(self, index):
        self.startIndex = index

    def setIndexMode(self, mode):
        """ Set the indexMode to True or False.  If indexMode is True the widget
        will display indices.  If indexMode is False the widget will display
        actual values """
        self.indexMode = mode

    def setSlidersMinMax(self):
        self.topSlider.setMinimum(self.minIndex)
        self.bottomSlider.setMinimum(self.minIndex)
        self.topSlider.setMaximum(self.maxIndex)
        self.bottomSlider.setMaximum(self.maxIndex)

    def updateMin(self, minIndex=None):
        """ Set min value, update the slider label and the comboBox line edit
        to show the new min value"""
        
        ## For longitude bug 373 requests that we cannot flip them, not sure it's right thing to do but "fixing" it.
        bindex = self.bottomSlider.value()
        if self.isLon and minIndex > bindex:
            minIndex = bindex
            self.topSlider.setValue(minIndex)
        if not minIndex is None:
            self.minIndex = minIndex
            
        if (self.indexMode == True):
            minValue = self.minIndex + self.startIndex
        else:
            minValue = self.axisValues[self.minIndex]
            
        self.topLabel.setText(str(minValue))
        self.axisCombo.setMinValue(minValue)
        if self.parent().pin.isChecked():
            self.parent().pin.click()
            
    def boundIndex( self, index ):
        if index >= len( self.axisValues ): return len( self.axisValues ) - 1
        if index <= 0: return 0
        return index

    def updateMax(self, maxIndex=None):
        """ Set max value, update the slider label and the comboBox line edit
        to show the new max value"""
        
        ## For longitude bug 373 requests that we cannot flip them, not sure it's right thing to do but "fixing" it.
        tindex = self.topSlider.value()
        if self.isLon and maxIndex < tindex:
            maxIndex = tindex
            self.bottomSlider.setValue(maxIndex)

        if not maxIndex is None:
            self.maxIndex = self.boundIndex( maxIndex )
            
        if (self.indexMode == True):
            maxValue = self.maxIndex + self.startIndex
        else:
            maxValue = self.axisValues[self.maxIndex]

        self.bottomLabel.setText(str(maxValue))
        self.axisCombo.setMaxValue(maxValue)
        if self.parent().pin.isChecked():
            self.parent().pin.click()

    def updateTopSlider(self, index):
        index = self.boundIndex( index )
        self.minIndex = index
        self.topSlider.setValue(index)
        if self.parent().pin.isChecked():
            self.parent().pin.click()

    def updateBottomSlider(self, index):
        index = self.boundIndex( index )
        self.maxIndex = index
        self.bottomSlider.setValue(index)
        if self.parent().pin.isChecked():
            self.parent().pin.click()

    def replaceComboBoxValues(self, values):
        self.axisCombo.replaceComboBoxValues(values)

    def getAxisIndices(self):
        return self.axisIndices
    
    def getAxisValues(self):
        return self.axisValues

    def getCurrentValues(self):
        if int(self.axisCombo.stride)==1:
            return (self.axisValues[self.minIndex], self.axisValues[self.maxIndex])
        else:
            return slice(self.minIndex,self.maxIndex,int(self.axisCombo.stride))

    def getCurrentValuesAsStr(self):
        if self.isTime:
            return "('%s', '%s')" % (self.axisValues[self.minIndex],
                                     self.axisValues[self.maxIndex])
        else:
            return "(%s, %s)" % (self.axisValues[self.minIndex],
                                 self.axisValues[self.maxIndex])

    def numValues(self):
        return len(self.axisValues)

    def getIndex(self):
        return (self.minIndex, self.maxIndex)


class QAxis(QtGui.QWidget):
    """ Axis widget containing: a button + popup-menu for modifying an axis, combobox
    and sliders for setting axis values, and a function def button + popup-menu """

    def __init__(self, axis, axisName, axisIndex, parent=None,virtual=False):
        QtGui.QWidget.__init__(self, parent)
        #self.root = parent.root
        self.axis = axis
        self.axisName = axisName # Axis name including the label
        self.axisIndex = axisIndex
        self.parent=parent
        self.virtual=virtual
            
        hbox = QtGui.QHBoxLayout()
        hbox.setSpacing(0)
        hbox.setMargin(0)                
        self.pin = QtGui.QToolButton()
        self.pin.setIcon(QtGui.QIcon(":/icons/resources/icons/unpinned.png"))
        self.pin.setCheckable(True)
        self.pin.clicked.connect(self.pinClicked)
        self.sliderCombo = QSliderCombo(axis, self)
        hbox.addWidget(self.sliderCombo)
        hbox.addWidget(self.pin)
        self.setLayout(hbox)        

        # These buttons aren't added to the layout here, instead they are added
        # in QAxisList which has a grid layout so they can line up properly
        self.axisOperationsButton = self.createAxisOperationsButtonAndMenu()
        self.axisButton = self.createAxisButtonAndMenu()
        self.setAxisButtonText(axisName)

        row = parent.gridLayout.rowCount()
        parent.gridLayout.addWidget(self.getAxisButton(), row, 0)
        parent.gridLayout.addWidget(self, row, 1)            
        parent.gridLayout.addWidget(self.getAxisOperationsButton(), row, 2)
        # Create separator line between each axis widget
        vline = QtGui.QFrame()
        vline.setFrameStyle(QtGui.QFrame.HLine | QtGui.QFrame.Sunken)
        vline.setMidLineWidth(37)
        palette = vline.palette()
        role = vline.backgroundRole()
        palette.setColor(role, QtGui.QColor(220,213,226))
        vline.setPalette(palette)
        vline.setAutoFillBackground(True)
        parent.gridLayout.addWidget(vline, row+1, 0, 1,
                                  parent.gridLayout.columnCount())

        #Nowturn off if can be replaced by lat/lon virtual
        if self.virtual==-1:
            self.hide()
            self.axisOperationsButton.hide()
            self.axisButton.hide()
            vline.hide()
            

        # Connect signals such that when the value of the axis slider is changed,
        # a signal will be emitted to update the value in the corresponding
        # Vistrails 'Variable' or 'Quickplot' box.
        ## self.connect(self.sliderCombo.topSlider,
        ##              QtCore.SIGNAL('valueChanged (int)'),
        ##              parent.setVistrailsVariableAxes)
        ## self.connect(self.sliderCombo.bottomSlider,
        ##              QtCore.SIGNAL('valueChanged (int)'),
        ##              parent.setVistrailsVariableAxes)

    def pinClicked(self):
        if self.axis.isTime():
            k="UVTIMEAXIS"
        elif self.axis.isLatitude():
            k="UVLATAXIS"
        elif self.axis.isLongitude():
            k="UVLONAXIS"
        elif self.axis.isLevel():
            k="UVLEVELAXIS"
        else:
            k=self.axisName
        if self.pin.isChecked():
            self.pin.setIcon(QtGui.QIcon(":/icons/resources/icons/pinned.png"))
            ## Ok now we need to remember the actual values
            try: # try because when setting up a new Axis it's not ready but we don't really care since it would be the same
                v1,v2 = self.getCurrentValues()
                pins[k]={"vals":(v1,v2),"pinned":True}
            except:
                pass
        else:
            self.pin.setIcon(QtGui.QIcon(":/icons/resources/icons/unpinned.png"))
            pins[k]["pinned"]=False
    def createAxisOperationsButtonAndMenu(self):
        """ Initialize the button to the right of the axis sliders and it's menu
        with operations: def, sum, avg, wgt, gtm, awt, std
        """
        button = QtGui.QToolButton()
        menu = QtGui.QMenu(self)        
        
        opDefs = ['def default axis points',
                  'sum summation of selected axis points',
                  'avg average of selected axis points',
                  'wgt weighted average of selected axis points',
                  'gtm geometrical mean of selected axis points',
                  'std standard deviation of selected axis points',]
        if self.axis.getBounds() is None:
            opDefs.pop(3)
        if self.virtual>0:
            opDefs = opDefs[:1]
        for op in opDefs:
            action = menu.addAction(op)
            self.connect(action, QtCore.SIGNAL('triggered ()'),
                         self.selectAxesOperationEvent)

        button.setText(' def  ')
        button.setMenu(menu)
        button.setPopupMode(QtGui.QToolButton.InstantPopup)

        # Connect Signals
        self.connect(button, QtCore.SIGNAL('clicked(bool)'),
                     button.showMenu)

        return button

    def selectAxesOperationEvent(self):
        """ Event handler for when a user selects an operation from the
        axes operations popup menu (located to right of the sliders):
        sum, avg, awt, gtm, etc ...
        """
        # Get the operation selected by getting the text of who sent the signal
        op = self.sender().text()[:3] # def, sum, avg, wgt, awt, gtm, or std

        # If the operation is 'awt' ask the user for an alternate weight var
        # C. Doutriaux 2012-12-19: Removing for now since code seems to have disappeared... nowhere in the repo....
        ## if op == 'awt':
        ##     definedVars = self.parent.parent.getDefinedVars()
        ##     QReplaceAxisWeightsDialog(definedVars, self).show()
        ##     return

        # Set button text to what the user selected
        self.axisOperationsButton.setText(" %s  " % op)

        # Update the vistrails 'Variable' module's axesOperations input
        #axesOperations = self.parent.getAxesOperations()
        #varWidget = self.parent.parent
        #varWidget.emit(QtCore.SIGNAL('updateModule'),
        #               self.parent.currentTabName(), 'axesOperations',
        #               str(axesOperations)) 

    def createAxisButtonAndMenu(self):
        """ createAxisButtonAndMenu(axesNames: list)

        Initialize the button to the left of the sliders / combo box and
        it's menu which currently has options: index, raw, get axis values,
        get axis weight values, replace axis values, re-order dimensions.
        """
        axisMenu = QtGui.QMenu(self)
        menuVbox = QtGui.QVBoxLayout()
        axisMenu.setLayout(menuVbox)

        # Add index options to the menu
        indexAction = axisMenu.addAction(self.axis.id + '_index')
        indexAction.setCheckable(True)

        # Add raw index option if this dimension is time
        if self.axis.isTime():
            rawIndexAction = axisMenu.addAction(self.axis.id + '_raw')
            rawIndexAction.setCheckable(True)
        
        axisMenu.addSeparator()

        # Add axis value options to the menu
        axisOptions = ['Get Axis Values', 'Get Axis Weight Values',
                       'Replace Axis Values','Virtual Lat/Lon On/Off']
        if self.virtual!=0:
            switchVirtualAxisAction = axisMenu.addAction(axisOptions[3])
        else:
            getAxisValuesAction = axisMenu.addAction(axisOptions[0])
            getAxisWeightValuesAction = axisMenu.addAction(axisOptions[1])
            replaceAxisValuesAction = axisMenu.addAction(axisOptions[2])
        if self.virtual<=0:
            # Add 're-order dimensions' option to menu
            axisMenu.addSeparator()
            reorderAxesMenu = axisMenu.addMenu('Re-Order Dimensions')
            axesNames = self.parent.getAxesNames()                
            for axisID in axesNames:
                reorderAction = reorderAxesMenu.addAction(axisID)
                self.connect(reorderAction, QtCore.SIGNAL('triggered()'),
                             self.reorderAxesEvent)

        # Create axis button
        axisButton = QtGui.QToolButton()
        axisButton.setMenu(axisMenu)
        axisButton.setPopupMode(QtGui.QToolButton.InstantPopup)

        # Connect signals emitted by the axis button menu
        axisButton.connect(axisButton, QtCore.SIGNAL('clicked(bool)'),
                           axisButton.showMenu)
        self.connect(indexAction, QtCore.SIGNAL('toggled (bool)'),
                     self.setIndexModeEvent)
        if self.virtual!=0:
            self.connect(switchVirtualAxisAction, QtCore.SIGNAL('triggered ()'),
                         self.switchVirtual)
        else:
            self.connect(getAxisValuesAction, QtCore.SIGNAL('triggered ()'),
                         self.getAxisValuesEvent)
            self.connect(replaceAxisValuesAction, QtCore.SIGNAL('triggered ()'),
                         self.getReplacementAxisValuesEvent)        
            self.connect(getAxisWeightValuesAction, QtCore.SIGNAL('triggered ()'),
                         self.getAxisWeightValuesEvent)
        
        if self.axis.isTime():
            self.connect(rawIndexAction, QtCore.SIGNAL('toggled (bool)'),
                         self.setRawIndexModeEvent)
            # Dont allow _raw and _index to be checked simultaneously
            self.connect(rawIndexAction, QtCore.SIGNAL('toggled (bool)'),
                         lambda : indexAction.setChecked(False))
            self.connect(indexAction, QtCore.SIGNAL('toggled (bool)'),
                         lambda : rawIndexAction.setChecked(False))                        
            
        return axisButton

    def switchVirtual(self):
        for i in range(self.parent.gridLayout.rowCount()):
            it=self.parent.gridLayout.itemAtPosition(i,1)
            if it is not None:
                a=it.widget()
                if hasattr(a,"virtual"):
                    if a.isHidden():
                        a.show()
                        a.getAxisButton().show()
                        a.getAxisOperationsButton().show()
                        self.parent.gridLayout.itemAtPosition(i+1,1).widget().show()
                    else:
                        a.hide()
                        a.getAxisButton().hide()
                        a.getAxisOperationsButton().hide()
                        self.parent.gridLayout.itemAtPosition(i+1,1).widget().hide()
    
    def reorderAxesEvent(self):
        """ reorderAxesEvent is called when the user selects 're-order
        dimensions from the axis button. Swap this axis with the selected axis
        and update the vistrails' Variable module's 'axes' input
        """
        axisB = self.sender().text()
        self.parent.swapAxes(self.axisName, axisB)
        #self.parent.setVistrailsVariableAxes()

    def getReplacementAxisValuesEvent(self):
        """ getReplacementAxisValuesEvent is called when the user selects
        'Replace Axis Values' Show a dialog box which asks the user to select
        a defined variable for replacement axis values
        """
        definedVars = self.parent.parent.getDefinedVars()
        QReplaceAxisValuesDialog(definedVars, self).show()
        
    def replaceAxisValues(self, newValuesVar):
        """ replaceAxisValues(newValuesVar: tvariable)

        replaceAxisValues is called after the user selects 'Replace Axis Values'
        and selects a replacement variable from the popup dialog.  This method
        replaces the axis' values with 'newValuesVar'
        """
        # TODO doesn't work
        var = self.parent.getVar()
        axis = var.getAxis(self.axisIndex)
        axis[:] = newValuesVar.astype(axis[:].dtype.char).filled()
        axis.setBounds(None)
        self.parent.setVar(var)

        # Generate teaching command string
        # TODO

    def getAxisWeightValuesEvent(self):
        """ getAxisWeightValuesEvent is called when the user selects 'Get Axis
        Weight Values' from the axis button menu.  This method will create and
        define a new variable / tab with the axis' weight values
        """
        var = self.parent.getVar()
        _app = get_vistrails_application()
        w=_app.uvcdatWindow.dockCalculator.widget()
        le=w.le
        #axisVar = genutil.getAxisWeightByName(var, self.axis.id)
        axisVarid = var.id +'_' + self.axis.id + '_weight'

        # Generate teaching command string
        fileID = self.parent.cdmsFile.id
        le.setText("cdmsFile=cdms2.open('%s')" % fileID)
        w.run_command()
        le.setText("%s = genutil.getAxisWeightByName(cdmsFile[\"%s\"], \"%s\")\n" % (axisVarid, var.id, self.axis.id))
        w.run_command()
        le.setText( "%s.id = \"%s\"\n" % (axisVarid, axisVarid) )
        w.run_command()

    def getAxisValuesEvent(self):
        """ getAxisValuesEvent is called when the user selects 'Get Axis
         Values' from the axis button menu.  This method will create and
        define a new variable / tab with the axis' values
        """        
        varID = self.parent.getVar().id
        _app = get_vistrails_application()
        w=_app.uvcdatWindow.dockCalculator.widget()
        le=w.le
        axisVarid = varID +'_' + self.axis.id + '_axis'
        le.setText("cdmsFile=cdms2.open('%s')" % self.parent.cdmsFile.id)
        w.run_command()
        le.setText("%s = MV2.array(cdmsFile['%s'],axes=[cdmsFile['%s'],],id='%s')" % (axisVarid,self.axis.id,self.axis.id,axisVarid))
        w.run_command()

    def setIndexModeEvent(self, indexMode):
        """ setIndexModeEvent(indexMode: bool)

        If indexMode is True then set the combobox and
        slider values to be indices.  If indexMode is False then set the
        combobox and slider values to be the actual axis values.
        """
        axisIndices = self.sliderCombo.getAxisIndices()
        axisValues = self.sliderCombo.getAxisValues()        
        
        self.sliderCombo.setIndexMode(indexMode)        
        if (indexMode == True):
            self.sliderCombo.setStartIndex(0)
            self.sliderCombo.replaceComboBoxValues(axisIndices)
        else:
            self.sliderCombo.replaceComboBoxValues(axisValues)

        self.sliderCombo.updateMax()
        self.sliderCombo.updateMin()

    def setRawIndexModeEvent(self, rawIndexMode):
        """ setRawIndexModeEvent(rawIndexMode: bool)
        
        If rawIndexMode is True then set the combobox and
        slider values to be indices since january 1st 1979.  
        otherwise set the combobox and slider values to be the actual axis
        values.
        """
        self.sliderCombo.setIndexMode(rawIndexMode)
        axisValues = self.sliderCombo.getAxisValues()
        axisIndices = self.sliderCombo.getAxisIndices()
        
        if (rawIndexMode == True):
            # Calculate months since jan 1st, 1979
            firstTimeEntry = axisValues[0]
            match = re.compile('(\d\d\d\d)(-)(.+)(-)(.*)').match(firstTimeEntry)

            if match is None:
                raise NameError("Invalid time string: %s" % firstTimeEntry)

            year = int(match.group(1))
            month = int(match.group(3))
            monthsSince1979 = 12 * (year - 1979) + (month - 1)
            self.sliderCombo.setStartIndex(monthsSince1979)

            # Add months since jan 1979 to indices
            rawIndices = map(lambda x: x + monthsSince1979, axisIndices)
            self.sliderCombo.replaceComboBoxValues(rawIndices)
        else:
            self.sliderCombo.replaceComboBoxValues(axisValues)

        self.sliderCombo.updateMax()
        self.sliderCombo.updateMin()

    def sumAxisPoints(self, var):
        """ Update the variable by applying the sum operation to the given
        axis. Note this function is called only when a variable is defined.
        """
        varID = var.id
        var = cdutil.averager(var, axis="(%s)" % self.axis.id, weight='equal',
                              action='sum')        
        var.id = varID
        return var

    def avgAxisPoints(self, var):
        """ Update the variable by applying the avg operation to the given
        axis.
        """
        varID = var.id
        var = cdutil.averager(var, axis="(%s)" % self.axis.id, weight='equal')
        var.id = varID
        return var

    def weightedAvgAxisPoints(self, var):
        """ Update the variable by applying the weighted avg operation to the
        the given axis.
        """
        varID = var.id
        var = cdutil.averager(var, axis="(%s)" % self.axis.id)
        var.id = varID
        return var

    def geoMeanAxisPoints(self, var):
        """ Update the variable by applying the geometrical mean operation to
        the given axis.
        """
        varID = var.id
        var = genutil.statistics.geometricmean(var, axis="(%s)" % self.axis.id)
        var.id = varID
        return var

    def stdAxisPoints(self, var):
        """ Update the variable by applying the standard deviation operation to
        the given axis.
        """
        varID = var.id
        var = genutil.statistics.std(var, axis="(%s)" % self.axis.id)
        var.id = varID
        return var

    def alteredWeightedAvgAxisPoints(self, var):
        """ Update the variable by applying the altered weighted avg operation
        to the given axis.
        """
        varID = var.id
        var = cdutil.averager(var, axis="(%s)" % self.axis.id,
                             weight=self.alteredWeightsVar.filled())
        var.id = varID
        return var

    def setAlteredWeights(self, var):
        self.alteredWeightsVar = var
        self.axisOperationsButton.setText(' awt  ')

    def setAxisButtonText(self, name):
        self.axisButton.setText(name + ' ')
        
    def getCurrentValues(self):
        return self.sliderCombo.getCurrentValues()

    def getCurrentValuesAsStr(self):
        return self.sliderCombo.getCurrentValuesAsStr()

    def numValues(self):
        return self.sliderCombo.numValues()

    def getIndexes(self):
        return self.sliderCombo.getIndexes()

    def getID(self):
        return self.axis.id

    def getAxisOperationsButton(self):
        return self.axisOperationsButton

    def getAxisButton(self):
        return self.axisButton

    def getAlteredWeightsVar(self):
        return self.alteredWeightsVar


class QAxisComboWidget(QtGui.QComboBox):
    """ Specialized ComboBox widget for Axis Values listing / selecting the
    axis' values. """
    
    def __init__(self, parent=None):
        QtGui.QComboBox.__init__(self, parent)
        self.setMin = False
        self.stride = 1 # TODO : Changing the stride does nothing as of now
        self.minValue = 0
        self.maxValue = 0

        self.setMouseTracking(True)
        self.setEditable(True)
        self.setMinimumContentsLength(10)
        self.setCurrentIndex(1)
        self.setMaxVisibleItems(10)
        self.setSizeAdjustPolicy(QtGui.QComboBox.AdjustToMinimumContentsLengthWithIcon)

        # Set highlighted text color to gray instead of default white
        comboPalette = self.view().palette()
        comboPalette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.darkGray)
        self.view().setPalette(comboPalette)

        # Connect Signals
        self.connect(self, QtCore.SIGNAL('currentIndexChanged(const QString&)'),
                     self.valueChangedEvent)
        self.connect(self, QtCore.SIGNAL('editTextChanged(const QString&)'),
                     self.valueChangedEvent)

    def initValues(self, axisValues):
        """ initValues(axisValues: list)

        Initialize the values in the combo box from a list of axis values.
        """
        for axisValue in axisValues:
            self.addItem(str(axisValue), ['variables', str(axisValue)])

        self.minValue = axisValues[0]
        self.maxValue = axisValues[-1]
        self.setLineEditText() # Set lineedit text to be valueA : valueB by stride

    def replaceComboBoxValues(self, axisValues):
        """ replaceComboBoxValues(axisValues: list)

        Replace the values in the comboBox with new values: raw indices, indices
        or actual values.
        """
        for i in range(len(axisValues)):
            data = ['variables', str(axisValues[i])]
            self.setItemData(i, data)
            self.setItemText(i, str(axisValues[i]))

        self.minValue = axisValues[0]
        self.maxValue = axisValues[-1]
        self.setLineEditText()

    def setMinValue(self, minValue):
        self.minValue = minValue
        self.setLineEditText()

    def setMaxValue(self, maxValue):
        self.maxValue = maxValue
        self.setLineEditText()
        
    def setLineEditText(self):
        """ Set the comboBox's lineEdit to show:  minValue : maxValue by stride
        """
        self.setEditText(str(self.minValue) + " : " + str(self.maxValue) + " by "
                         + str(self.stride))
        self.lineEdit().setCursorPosition(0)

    def valueChangedEvent(self, axisValue):
        """ valueChangedEvent(axisValue: str)

        Event handler for when a user changes a combobox value by selecting a
        value or entering a value into the line edit.  Update the corresponding
        slider / label with the same value
        """
        index = self.findData(['variables', str(axisValue)])
        # If user entered a value into the lineEdit.
        if 1:#index == -1:
            self.updateValueFromLineEditText(axisValue)
            return

        # If user selected a value from the combo box.
        # Selecting values from the combo box will alternate between setting the
        # min and max values & emit a signal to update corresponding slider
        if (self.setMin == True):
            self.setMin = False
            self.minValue = axisValue
            self.emit(QtCore.SIGNAL('axisComboMinValueChanged (int)'), self.currentIndex())
        else:
            self.setMin = True
            self.maxValue = axisValue
            self.emit(QtCore.SIGNAL('axisComboMaxValueChanged (int)'), self.currentIndex())

        self.setLineEditText()

    def updateValueFromLineEditText(self, axisValue):
        """ updateValueFromLineEditText(axisValue: str)

        Check if the user entered a valid string in the line edit and if the
        values exist. If it is valid & the values exist, set the values in the
        corresponding slidingAxisWidget so the combobox and sliders match.
        """
        # The lineEdit text must have format "ValueA : ValueB by Stride"
        pattern = re.compile("(.*)\s:\s(.*)\sby\s(\w*)")
        result = pattern.match(axisValue)
        # If invalid string format, do nothing
        if (result == None):
            return

        # Set stride if it is a valid digit
        # Stride functionality not implemented yet
        if (str(result.group(3)).isdigit() == True):
            self.stride = result.group(3)

        minValue = result.group(1)
        maxValue = result.group(2)
        #minIndex,maxIndex = self.parent().parent().axis.mapInterval((float(minValue),float(maxValue)))
        minIndex = self.findData(['variables', str(minValue)])
        maxIndex = self.findData(['variables', str(maxValue)])
        # If min or max values are not in the list of values do nothing
        if (minIndex == -1 or maxIndex == -1):
            return

        # LineEdit string is valid, emit signal to update the corresponding axis sliders
        self.emit(QtCore.SIGNAL('axisComboMinValueChanged (int)'), minIndex)
        self.emit(QtCore.SIGNAL('axisComboMaxValueChanged (int)'), maxIndex)            

class QAxisList(QtGui.QWidget):
    """ Widget containing a list of axis widgets for the selected variable """

    def __init__(self, cdmsFile=None, var=None, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.axisWidgets = [] # List of QAxis widgets
        self.axesNames = [] # List of axis names (including labels)
        self.axisOrder = [] # List of ints to specify axes ordering
        self.cdmsFile = cdmsFile # cdms file associated with the variable
        self.var = var # variable associated with the axes
        self.axisList = None # list of axes from the variable
        #self.root = parent.root
        self.parent=parent
        
        # Init & set the layout
        vbox = QtGui.QVBoxLayout()
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setMargin(0)
        self.gridLayout.setSpacing(0)
        #l=QtGui.QLabel("Dimensions")
        #vbox.addWidget(l)
        vbox.addLayout(self.gridLayout)
        vbox.addStretch()
        vbox.setSpacing(0)
        vbox.setMargin(5)
        self.setLayout(vbox)

    def clear(self):
        """ Remove the QAxis widgets, empty axisWidgets and axesNames lists from
        the grid layout
        """
        self.gridLayout.setRowStretch(self.gridLayout.rowCount()-1, 0)
        for i in reversed(range(self.gridLayout.count())):
            item = self.gridLayout.itemAt(i)
            axis = item.widget()
            if axis:
                self.gridLayout.removeWidget(axis)
                axis.hide()
                axis.deleteLater()
            else:
                self.gridLayout.removeItem(item)
                
        self.axisWidgets = []
        self.axesNames = []

    def setupVariableAxes(self):
        """ Iterate through the variable's axes and create and initialize an Axis
        object for each axis.
        """
        if self.var is None:
            return
        
        if (self.axisList is None):
            if self.cdmsFile is None:
                self.axisList = self.var.getAxisList()
                self.grid=self.var.getGrid()
            else:
                try:
                    self.axisList = self.cdmsFile[self.var].getAxisList()
                    self.grid=self.cdmsFile[self.var].getGrid()
                except:
                    ## Ok this is probably a simple axis
                    self.axisList=[self.cdmsFile[self.var],]
                    self.grid=None
            self.axisOrder = range(len(self.axisList))

        self.clear()            
        self.setAxesNames()
        
        # Iterate through the variables axes & init each axis widget
        axisIndex = 0
        didVirtual=False
        for axis, axisName in zip(self.axisList, self.axesNames):
            virtual = 0
            if  isinstance(self.grid,(cdms2.hgrid.AbstractHorizontalGrid,cdms2.gengrid.AbstractHorizontalGrid)) and axis in self.grid.getLatitude().getAxisList():
                    virtual = -1
                    if didVirtual is False:
                        didVirtual=True
                        minLat,maxLat=genutil.minmax(self.grid.getLatitude())
                        minLon,maxLon=genutil.minmax(self.grid.getLongitude())
                        vLat=cdms2.createAxis(numpy.arange(numpy.floor(minLat),numpy.ceil(maxLat)+.1,.1),id="latitude")
                        vLon=cdms2.createAxis(numpy.arange(numpy.floor(minLon),numpy.ceil(maxLon)+.1,.1),id="longitude")
                        virtualLatWidget=QAxis(vLat, "latitude", axisIndex, self,virtual=1)
                        virtualLonWidget=QAxis(vLon, "longitude", axisIndex, self,virtual=2)
                        self.axisWidgets.append(virtualLatWidget)
                        self.axisWidgets.append(virtualLonWidget)
            # Create the axis widget
            # Virtual: 0: Not virtual
            #         -1: options to switch to virtual
            #          1: is latitude virtual needs option to switch back
            #          2: is longitude virtual needs option to switch back
            axisWidget = QAxis(axis, axisName, axisIndex, self,virtual=virtual)
            self.axisWidgets.append(axisWidget)
            axisIndex += 1
        self.gridLayout.setRowStretch(self.gridLayout.rowCount(), 1)

    def defineVarAxis(self, var, teachingCommand):
        self.parent.defineVarAxis(var, teachingCommand)

    def swapAxes(self, axisA, axisB):
        """ swapAxes(axisA: QAxis, axisB: QAxis)

        swap the axis widgets: axisA and axisB
        """
        if (axisA == axisB):
            return

        if axisA in self.axesNames and axisB in self.axesNames:
            i = self.axesNames.index(axisA)
            j = self.axesNames.index(axisB)
            self.axisList[i], self.axisList[j] = self.axisList[j], self.axisList[i]
            self.axisOrder[i], self.axisOrder[j] = self.axisOrder[j], self.axisOrder[i]
            self.setupVariableAxes()

    def execAxesOperations(self, var):
        """ Return the updated variable by doing the 'sum', 'avg', 'wgt', 'awt',
        'gtm' and 'std' operations.
        """
        for axis in self.axisWidgets:
            op = str(axis.getAxisOperationsButton().text()).strip()
            if op == 'sum':
                var = axis.sumAxisPoints(var)
            elif op == 'avg':
                var = axis.avgAxisPoints(var)
            elif op == 'wgt':
                var = axis.weightedAvgAxisPoints(var)
            elif op == 'gtm':
                var = axis.geoMeanAxisPoints(var)
            elif op == 'std':
                var = axis.stdAxisPoints(var)
            elif op == 'awt':
                var = axis.alteredWeightedAvgAxisPoints(var)
        return var

    # * At this point in fixing up the code

    def getAxesOperationsTeachingCommands(self, varID):
        """ Create and return the  teaching commands for the axes operations:
        def, sum, avg, wgt, awt, gtm, std
        """
        commands = ""
        for axis in self.axisWidgets:
            axisID = axis.getID()
            op = str(axis.getAxisOperationsButton().text()).strip()
            
            if op == 'sum':
                commands += "%s=cdutil.averager(%s, axis='(%s)', weight='equal', action='sum')\n" % (varID, varID, axisID)
                commands += "%s.id = '%s'\n" % (varID, varID)                
            elif op == 'avg':
                commands += "%s=cdutil.averager(%s, axis='(%s)', weight='equal')\n" % (varID, varID, axisID)                
                commands += "%s.id = '%s'\n" % (varID, varID)
            elif op == 'wgt':
                commands += "%s=cdutil.averager(%s, axis='(%s)')\n" % (varID, varID, axisID)                
                commands += "%s.id = '%s'\n" % (varID, varID)
            elif op == 'awt':
                alteredWeightsID = axis.getAlteredWeightsVar().id
                commands += "%s=cdutil.averager(%s, axis='(%s)', weight=%s.filled())" % (varID, varID, axisID, alteredWeightsID)
                commands += "\n# Currently, VCDAT cannot record the altered average weight command."
            elif op == 'gtm':
                commands += "%s=genutil.statistics.geometricmean(%s, axis='(%s)')\n" % (varID, varID, axisID)
                commands += "%s.id = '%s'\n" % (varID, varID)
            elif op == 'std':
                commands += "%s=genutil.statistics.std(%s, axis='(%s)')\n" % (varID, varID, axisID)
                commands += "%s.id = '%s'\n" % (varID, varID)                                
        return commands

    def getAxesOperations(self):
        """ Return a dict where keys are axis names, and values are the
        operation to be done on the axis such as: def, sum, avg, etc ... """
        
        axisOpsDict = {}
        
        #init with values from var module if any
        varname = None
        if self.var is not None:
            if hasattr(self.var, 'id'):
                varname = self.var.id
            elif isinstance(self.var, basestring):
                varname = self.var
            else:
                print "Warning: unkown self.var param in axis list"
            
         
        # FIXME: Removed for DAT
        #if varname is not None:
        #    projectController = self.root.get_current_project_controller()
        #    
        #    varModule = None
        #    
        #    if varname in projectController.defined_variables:
        #        varModule = projectController.defined_variables[varname]
        #    elif varname in projectController.computed_variables_ops:
        #        varModule = projectController.computed_variables_ops[varname]
        #    
        #    if varModule is not None and varModule.axesOperations.strip() != '':
        #        try:
        #            axisOpsDict = eval(varModule.axesOperations)
        #        except:
        #            format = "Warning: invalid string 'axesOperations': %s"
        #            print format % str(varModule.axesOperations)
        
        for axis in self.axisWidgets:
            op = str(axis.getAxisOperationsButton().text()).strip()
            axisOpsDict[axis.getID()] = op
            
        return axisOpsDict

    def getAxesNames(self):
        return self.axesNames

    def getAxisWidgets(self):
        return self.axisWidgets

    def getFile(self):
        return self.cdmsFile

    def getFileID(self):
        return self.cdmsFile.id

    def getVar(self):
        if self.cdmsFile is not None and isinstance(self.var, basestring):
            return self.cdmsFile[self.var]
        return self.var

    def getVarID(self):
        return self.var.id

    def getAxesOrderString(self):
        """ Return a string with the axes' order """
        
        order = list(self.axisOrder)
        return ''.join(map(str, order))

    def setAxesNames(self):
        """ Generate a list with the axis label + axis name and store it in
        self.axesNames """
        
        labels = ['T', 'Z', 'Y', 'X'] + [chr(ord('S')-i) for i in xrange(18)]
        if (len(self.axisList) >= 4):
            i = 0
        else:
            i = 4 - len(self.axisList)
            
        for axis in self.axisList:
            self.axesNames.append(labels[i] + ' - ' + axis.id)
            i += 1
            
    def setFile(self, cdmsFile):
        self.cdmsFile = cdmsFile

    def setVar(self, var):
        self.var = var

    ## def currentTabName(self):
    ##     return self.parent.tabWidget.currentTabName()

    ## def setVistrailsVariableAxes(self):
    ##     """ Vistrails: Update the vistrails Variable modules 'axes' input. This
    ##     method is called whenever the sliders values are changed.
    ##     """
    ##     axesKwargs = {}
    ##     # Add the each axes' args for example: latitude: (-90, 90)
    ##     for axisWidget in self.axisWidgets:
    ##         axesKwargs[axisWidget.axis.id] = axisWidget.getCurrentValues()
    ##     # Add other args
    ##     axesKwargs['squeeze'] = 0
    ##     axesKwargs['order'] = self.getAxesOrderString()

    ##     self.parent.emit(QtCore.SIGNAL('updateModule'),
    ##                      self.parent.currentTabName(), 'axes', str(axesKwargs))
