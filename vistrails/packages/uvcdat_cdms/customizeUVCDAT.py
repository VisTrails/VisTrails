from PyQt4 import QtGui, QtCore
import os,cdms2
import uvcdatCommons

## default values
ICONPATH = os.path.join(cdms2.__path__[0], '..', '..', '..', '..', 'share','icons')
appIcon = ":/icons/resources/icons/UV-CDAT_logo_sites.gif"
esgfOpenDapIcon = ":/icons/resources/icons/file_document_paper_blue_g38942.ico"
esgfGridFtpIcon = ":/icons/resources/icons/file_document_paper_blue_g13494.ico"
esgfHttpIcon = ":/icons/resources/icons/file_document_paper_blue_g13247.ico"
esgfLasIcon = ":/icons/resources/icons/file_document_paper_blue_g9845.ico"
esgfUnknownIcon = ":/icons/resources/icons/file_document_paper_blue_g9432.ico"
esgfFolderIcon = ":/icons/resources/icons/generic_folder_stripe.ico"
esgfFileIcon = ":/icons/resources/icons/file_document_paper_blue_g21510.ico"
esgfSearchIcon = ":/icons/resources/icons/toolbar_find.ico"
esgfLoginIcon = ":/icons/resources/icons/login.ico"
esgfTreeIconSize = 22
saveMovie = ":/icons/resources/icons/save_movie.ico"
loadMovie = ":/icons/resources/icons/load_movie.ico"

iconsize=24
defaultTextColor = uvcdatCommons.blackColor
templatesColor = uvcdatCommons.defaultTemplatesColor
gmsColor = uvcdatCommons.defaultGmsColor
errorColor = uvcdatCommons.redColor
commentsColor = uvcdatCommons.redColor
recordCommands = True
defaultTemplateName = "starter"
defaultGraphicsMethodName = "starter"
colorSelectedStyle = "border:2px solid black"
colorNotSelectedStyle = "border:2px solid white"
#defaultEsgfNode = "esg-datanode.jpl.nasa.gov"
defaultEsgfNode = "esg-dn1.nsc.liu.se"
defaultEsgfGateway = "%s/esg-search/search" % defaultEsgfNode
#defaultEsgfMapping="%(datasetid).%(variable)"
defaultEsgfMapping=None
## General Styles
appStyles = {}
confirmB4Exit=True
saveB4Exit=True
defaultPlot="None"
##  cdms2 stuff
timeAliases=[]
levelAliases=[]
longitudeAliases=[]
latitudeAliases=[]
squeezeVariables=True
deselectVariables=True
ncShuffle=cdms2.getNetcdfShuffleFlag()
ncDeflate=cdms2.getNetcdfDeflateFlag()
ncDeflateLevel=cdms2.getNetcdfDeflateLevelFlag()

lastDirectory=os.getcwd()
fileBookmarks=[]

## Calculator Styles
#scientificButtonsStyles = {"background-color":"#3F3B3C",
scientificButtonsStyles = {"background-color":"qradialgradient(cx:0.3, cy:-0.4, radius:1.35, fx:.3, fy:-0.4, stop:0 white, stop:1 black)",
                           "color":"white",
                           "font":"bold ",
                           "font-size":"12px",
                           }

validateButtonsStyles = {"background-color":"qradialgradient(cx:0.3, cy:-0.4, radius:1.35, fx:.3, fy:-0.4, stop:0 white, stop:1 #7C0404)",
                         "color":"white",
                         "font":"bold",
                         "font-size":"12px",
                         }

numberButtonsStyles = {"background-color":"qradialgradient(cx:0.3, cy:-0.4, radius:1.35, fx:.3, fy:-0.4, stop:0 white, stop:1 #6491DA)",
                       "color":"white",
                       "font":"bold ",
                       "font-size":"12px",
                       }

operatorButtonsStyles = {"background-color":"qradialgradient(cx:0.3, cy:-0.4, radius:1.35, fx:.3, fy:-0.4, stop:0 white, stop:1 #B79626)",
                            "color":"black",
                         "font":"bold ",
                         "font-size":"12px",
                         }

constantsButtonStyles = {"background-color":"qradialgradient(cx:0.3, cy:-0.4, radius:1.35, fx:.3, fy:-0.4, stop:0 white, stop:1 #578038)",
                         "color":"black",
                         "font":"bold ",
                         "font-size":"12px",
                             }

## scientificButtonsStyles = {}
## validateButtonsStyles = {}
## numberButtonsStyles = { }
## operatorButtonsStyles = { }
## constantsButtonStyles = { }

plotTypes = uvcdatCommons.plotTypes
defaultAspectRatio = "Auto (lat/lon)"
#this is a dictionary {plotname: plot object}
extraPlotTypes = {}
