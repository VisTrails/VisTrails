###############################################################################
##
## Copyright (C) 2006-2011, University of Utah. 
## All rights reserved.
## Contact: contact@vistrails.org
##
## This file is part of VisTrails.
##
## "Redistribution and use in source and binary forms, with or without 
## modification, are permitted provided that the following conditions are met:
##
##  - Redistributions of source code must retain the above copyright notice, 
##    this list of conditions and the following disclaimer.
##  - Redistributions in binary form must reproduce the above copyright 
##    notice, this list of conditions and the following disclaimer in the 
##    documentation and/or other materials provided with the distribution.
##  - Neither the name of the University of Utah nor the names of its 
##    contributors may be used to endorse or promote products derived from 
##    this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
## AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
## THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR 
## PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR 
## CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; 
## OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
## WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR 
## OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF 
## ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
###############################################################################

from PyQt4 import QtCore, QtGui
import os

from core.db.locator import FileLocator, DBLocator
from core.publishing.parse_latex import parse_latex_file, parse_vt_command, \
    build_vt_command
from gui.common_widgets import QDockPushButton
from gui.vistrails_palette import QVistrailsPaletteInterface

class QLatexFigureItem(QtGui.QListWidgetItem):
    def __init__(self, opt_dict, parent=None):
        QtGui.QListWidgetItem.__init__(self, parent)
        self.opt_dict = opt_dict

    def update_opt_dict(self, opt_dict):
        self.opt_dict = opt_dict

    def get_opt_dict(self):
        return self.opt_dict


class QLatexAssistant(QtGui.QWidget, QVistrailsPaletteInterface):
    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
        QtGui.QWidget.__init__(self, parent, f)
        
        self.set_title("Export To LaTeX")

        # add button to select tex source
        # listview to select figure 
        # thumbnail display
        # set figure specific options (show workflow, show execution, show
        # set includegraphics options
        source_label = QtGui.QLabel("LaTeX Source:")
        self.source_edit = QtGui.QLineEdit()
        source_selector = QDockPushButton("Select...")
        # source_selector = QtGui.QToolButton()
        # source_selector.setIcon(QtGui.QIcon(
        #         self.style().standardPixmap(QtGui.QStyle.SP_DirOpenIcon)))
        # source_selector.setIconSize(QtCore.QSize(12,12))
        source_selector.setToolTip("Open a file chooser")
        # source_selector.setAutoRaise(True)
        self.connect(source_selector,
                     QtCore.SIGNAL('clicked()'),
                     self.selectSource)

        source_group = QtGui.QGroupBox("LaTeX Source")
        s_layout = QtGui.QHBoxLayout()
        s_layout.addWidget(source_label)
        s_layout.addWidget(self.source_edit)
        s_layout.addWidget(source_selector)
        s_layout.setStretch(1,1)
        source_group.setLayout(s_layout)

        self.figure_list = QtGui.QListWidget()
        self.figure_list.setSelectionMode(self.figure_list.SingleSelection)
        self.preview_image = QtGui.QLabel()
        self.preview_image.setScaledContents(False)
        self.preview_image.setMinimumSize(240, 240)
        add_figure = QDockPushButton("Add Figure")
        delete_figure = QDockPushButton("Delete Figure")
        
        self.connect(add_figure,
                     QtCore.SIGNAL("clicked()"),
                     self.addFigure)
        self.connect(delete_figure,
                     QtCore.SIGNAL("clicked()"),
                     self.deleteFigure)
        self.connect(self.figure_list,
                     QtCore.SIGNAL("itemSelectionChanged()"),
                     self.figureSelected)
        
        figure_group = QtGui.QGroupBox("Figures")
        figure_layout = QtGui.QGridLayout()
        figure_layout.addWidget(self.figure_list,0,0,1,2)
        figure_layout.addWidget(self.preview_image,0,2)
        figure_layout.addWidget(add_figure,1,0,QtCore.Qt.AlignRight)
        figure_layout.addWidget(delete_figure,1,1,QtCore.Qt.AlignRight)
        figure_group.setLayout(figure_layout)
        
        # figure type, vistrail reference (vt_locator), version (smart tag)
        # use current version
        self.figure_type = QtGui.QComboBox()
        self.figure_type.setEditable(False)
        # items = QtCore.QStringList()
        # items << "Workflow Results" << "Workflow Graph" << "History Tree Graph";
        self.figure_type.addItems(["Workflow Results", "Workflow Graph",
                                   "Version Tree"])
        self.figure_ref = QtGui.QLineEdit()
        version_label = QtGui.QLabel("Version:")
        self.figure_version = QtGui.QLineEdit()
        tag_label = QtGui.QLabel("Tag:")
        self.figure_tag = QtGui.QComboBox()
        self.figure_tag.setEditable(True)
        self.figure_smart = QtGui.QCheckBox("Smart Tag")
        current_button = QDockPushButton("Use Current")
        
        self.connect(current_button, QtCore.SIGNAL("clicked()"),
                     self.useCurrent)

        graphicx_label = QtGui.QLabel("Arguments for includegraphics:")
        self.graphicx_edit = QtGui.QLineEdit()

        self.def_group = QtGui.QGroupBox("Figure Definition")
        def_layout = QtGui.QVBoxLayout()
        def_h_layout = QtGui.QHBoxLayout()
        def_h_layout.addWidget(self.figure_ref)
        def_h_layout.addWidget(self.figure_type)
        def_h_layout.setStretch(0,1)
        def_layout.addLayout(def_h_layout)
        def_h_layout = QtGui.QHBoxLayout()        
        def_h_layout.addWidget(version_label)
        def_h_layout.addWidget(self.figure_version)
        def_h_layout.addWidget(tag_label)
        def_h_layout.addWidget(self.figure_tag)
        def_h_layout.addWidget(self.figure_smart)
        def_h_layout.addWidget(current_button)
        def_h_layout.setStretch(3,1)
        def_layout.addLayout(def_h_layout)
        def_h_layout = QtGui.QHBoxLayout()
        def_h_layout.addWidget(graphicx_label)
        def_h_layout.addWidget(self.graphicx_edit)
        def_h_layout.setStretch(1,1)
        def_layout.addLayout(def_h_layout)
        self.def_group.setLayout(def_layout)

        self.chbPdf = QtGui.QCheckBox("As PDF")
        self.chbCache = QtGui.QCheckBox("Cache Images")
        self.chbLatexVTL = QtGui.QCheckBox("Include .vtl")

        self.chbWorkflow = QtGui.QCheckBox("Include Workflow")
        self.chbFullTree = QtGui.QCheckBox("Include Full Tree")
        self.chbFullTree.setEnabled(False)
        self.chbExecute = QtGui.QCheckBox("Execute Workflow")
        self.chbSpreadsheet = QtGui.QCheckBox("Show Spreadsheet Only")

        self.gbEmbedOpt = QtGui.QGroupBox("Embed Options")
        gblayout = QtGui.QGridLayout()
        gblayout.addWidget(self.chbPdf, 0, 0)
        gblayout.addWidget(self.chbCache, 0, 1)
        gblayout.addWidget(self.chbLatexVTL, 1, 0)
        self.gbEmbedOpt.setLayout(gblayout)

        self.gbDownOpt = QtGui.QGroupBox("Download Options")
        gblayout = QtGui.QGridLayout()
        gblayout.addWidget(self.chbWorkflow, 0, 0)
        gblayout.addWidget(self.chbFullTree, 0, 1)
        gblayout.addWidget(self.chbExecute, 1, 0)
        gblayout.addWidget(self.chbSpreadsheet, 1, 1)
        self.gbDownOpt.setLayout(gblayout)

        revert_button = QDockPushButton("Revert...")
        save_button = QDockPushButton("Save...")
        save_button.setAutoDefault(True)

        self.connect(save_button, QtCore.SIGNAL("clicked()"),
                     self.saveLatex)
        
        main_layout = QtGui.QVBoxLayout()
        main_layout.addWidget(source_group)
        main_layout.addWidget(figure_group)
        main_layout.addWidget(self.def_group)
        main_h_layout = QtGui.QHBoxLayout()
        main_h_layout.addWidget(self.gbEmbedOpt)
        main_h_layout.addWidget(self.gbDownOpt)
        main_layout.addLayout(main_h_layout)
        main_h_layout = QtGui.QHBoxLayout()
        main_h_layout.setAlignment(QtCore.Qt.AlignRight)
        main_h_layout.addWidget(revert_button)
        main_h_layout.addWidget(save_button)
        main_layout.addLayout(main_h_layout)
        
        self.setLayout(main_layout)

        self.texts = None
        self.selected_item = None

    def selectSource(self):
        fname = QtGui.QFileDialog.getOpenFileName(self,
                                                  'Load LaTeX File...',
                                                  self.source_edit.text(),
                                                  'LaTeX files (*.tex)')
        if fname and not fname.isEmpty():
            self.source_edit.setText(fname)
            self.texts = parse_latex_file(fname)
            for cmd_tuple in self.texts[1]:
                if cmd_tuple:
                    opt_dict = parse_vt_command(*cmd_tuple)
                    item = QLatexFigureItem(opt_dict)
                    item.setText("Figure %d" % (self.figure_list.count() + 1))
                    self.figure_list.addItem(item)

    def readImage(self, opt_dict):
        if 'pdf' in opt_dict:
            out_type = 'pdf'
        else:
            out_type = 'png'
        if 'showtree' in opt_dict:
            version_str = ''
        else:
            version_str = '_%s' % opt_dict['version']
        if 'showworkflow' in opt_dict:
            graph_str = '_graph'
        else:
            graph_str = ''

        if 'filename' in opt_dict:
            figure_name = "%s%s_%s%s" % (opt_dict['filename'], version_str,
                                         out_type, graph_str)
        else:
            figure_name = "%s_%s_%s_%s%s_%s%s" % (opt_dict['host'],
                                                  opt_dict['db'],
                                                  opt_dict['port'],
                                                  opt_dict['vtid'],
                                                  version_str,
                                                  out_type,
                                                  graph_str)
        
        source_dir = os.path.dirname(str(self.source_edit.text()))
        path_to_figure = os.path.join(source_dir, 'vistrails_images',
                                      figure_name)

        #print 'LOOKING FOR %s' % path_to_figure
        if os.path.exists(path_to_figure):
            fnames = os.listdir(path_to_figure)
            for fname in fnames:
                #print "FOUND", fname
                if fname.endswith('png'):
                    pixmap = QtGui.QPixmap(os.path.join(path_to_figure, fname))
                    if pixmap.width() > pixmap.height():
                        pixmap = pixmap.scaledToWidth(240,
                                                      QtCore.Qt.SmoothTransformation)
                    else:
                        pixmap = pixmap.scaledToHeight(240, 
                                                       QtCore.Qt.SmoothTransformation)
                    self.preview_image.setPixmap(pixmap)
            

    def doCheckLink(self, do_set=False, opt_dict=None):
        check_links = {'pdf': self.chbPdf,
                       'buildalways': (self.chbCache, True, True),
                       'getvtl': self.chbLatexVTL,
                       'execute': self.chbExecute,
                       'showspreadsheetonly': self.chbSpreadsheet,
                       'embedworkflow': self.chbWorkflow,
                       'includefulltree': self.chbFullTree,
                       'tag': self.figure_smart}

        if opt_dict is None:
            opt_dict = {}
        for k, v in check_links.iteritems():
            opt_set = k in opt_dict
            if type(v) == tuple:
                chb = v[0]
                chb_default = v[1]
                if len(v) > 2:
                    chb_rev = v[2]
                else:
                    chb_rev = False
            else:
                chb = v
                chb_rev = False
                chb_default = False

            if do_set:
                if opt_set:
                    chb.setChecked(not chb_rev)
                else:
                    chb.setChecked(chb_default)
            else:
                if not chb_rev and chb.isChecked():
                    opt_dict[k] = None
                elif chb_rev and not chb.isChecked():
                    opt_dict[k] = None

        return opt_dict

    def setFigureInfo(self, opt_dict):
        self.doCheckLink(True, opt_dict)

        if 'showworkflow' in opt_dict:
            self.figure_type.setCurrentIndex(1)
        elif 'showtree' in opt_dict:
            self.figure_type.setCurrentIndex(2)
        else:
            self.figure_type.setCurrentIndex(0)
            
        if 'version' in opt_dict:
            self.figure_version.setText(str(opt_dict['version']))
        else:
            self.figure_version.setText("")
        if 'tag' in opt_dict:
            self.figure_tag.setEditText(str(opt_dict['tag'])[1:-1])
        else:
            self.figure_tag.setEditText("")
        
        if '_args' in opt_dict:
            self.graphicx_edit.setText(opt_dict['_args'])

        # build locator
        if 'filename' in opt_dict:
            # set using basedir of tex file
            fname = opt_dict['filename']
            if not os.path.isabs(fname):
                source_dir = os.path.dirname(str(self.source_edit.text()))
                #print 'source_dir:', str(self.source_edit.text()), source_dir
                fname = os.path.join(source_dir, fname)
            
            locator = FileLocator(fname)
        elif 'host' in opt_dict:
            if 'port' not in opt_dict:
                opt_dict['port'] = '3306'
            port = int(opt_dict['port'])
            locator = DBLocator(opt_dict['host'], port,
                                opt_dict['db'], '', '', 
                                obj_id=opt_dict['vtid'])
        else:
            locator = None
        if locator is not None:
            self.figure_ref.setText(locator.to_url())
        else:
            self.figure_ref.setText("")
        self.figure_ref.locator = locator

        self.readImage(opt_dict)

    def getFigureInfo(self):
        # return an opt_dict here...
        opt_dict = self.doCheckLink(False)
        if self.figure_type.currentIndex() == 1:
            opt_dict['showworkflow'] = None
        elif self.figure_type.currentIndex() == 2:
            opt_dict['showtree'] = None

        version_text = str(self.figure_version.text())
        if version_text:
            opt_dict['version'] = version_text
        tag_text = str(self.figure_tag.currentText())
        if self.figure_smart.isChecked() and tag_text:
            opt_dict['tag'] = '{%s}' % tag_text

        graphicx_text = str(self.graphicx_edit.text())
        if graphicx_text:
            opt_dict['_args'] = graphicx_text

        locator = self.figure_ref.locator
        if type(locator) == DBLocator:
            opt_dict['host'] = locator.host
            opt_dict['port'] = locator.port
            opt_dict['db'] = locator.db
            opt_dict['vtid'] = locator.obj_id
        else:
            fname = str(self.source_edit.text())
            if os.path.dirname(fname) == os.path.dirname(locator.name):
                # do relative
                # FIXME do relative via a checkbox!
                opt_dict['filename'] = os.path.basename(locator.name)
            else:
                opt_dict['filename'] = locator.name

        return opt_dict

    def figureSelected(self):
        selected_items = self.figure_list.selectedItems()
        if self.selected_item is not None:
            self.selected_item.update_opt_dict(self.getFigureInfo())
            #print "NEW OPTIONS:", self.selected_item.opt_dict
        if len(selected_items) < 1:
            self.gbEmbedOpt.setEnabled(False)
            self.gbDownOpt.setEnabled(False)
            self.def_group.setEnabled(False)
            self.selected_item = None
        else:
            self.gbEmbedOpt.setEnabled(True)
            self.gbDownOpt.setEnabled(True)
            self.def_group.setEnabled(True)
            item = selected_items[0]
            #print "OPTIONS:", item.opt_dict
            self.setFigureInfo(item.opt_dict)
            self.selected_item = item

    def addFigure(self):
        item = QLatexFigureItem({})
        item.setText("Figure %d" % (self.figure_list.count() + 1))
        self.figure_list.addItem(item)

    def deleteFigure(self):
        selected_items = self.figure_list.selectedItems()
        if len(selected_items) < 1:
            return
        idx = self.figure_list.row(selected_items[0])
        self.figure_list.takeItem(idx)

    def saveLatex(self):
        fname = '/vistrails/src/git/extensions/latex/head2.tex'
        f = open(fname, 'w')
        raw_texts = self.texts[0]
        figure_items = [self.figure_list.item(i) 
                        for i in xrange(self.figure_list.count())]
        for i in xrange(len(raw_texts)):
            f.write(raw_texts[i])
            if i < len(figure_items):
                f.write(build_vt_command(figure_items[i].get_opt_dict()))
        f.close()

    def openVersion(self):
        pass

    def useCurrent(self):
        pass

class QVersionEmbed(QtGui.QWidget, QVistrailsPaletteInterface):
    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
        QtGui.QWidget.__init__(self, parent, 
                               f | QtCore.Qt.Tool | QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowTitle('Publish Workflow')
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.versionNumber = None
        self.versionTag = ''
        label1 = QtGui.QLabel("Embed:")
        self.cbcontent = QtGui.QComboBox()
        self.cbcontent.setEditable(False)
        items = QtCore.QStringList()
        items << "Workflow Results" << "Workflow Graph" << "History Tree Graph";
        self.cbcontent.addItems(items)
        label2 = QtGui.QLabel("In:")
        
        self.cbtype = QtGui.QComboBox()
        self.cbtype.setEditable(False)
        items = QtCore.QStringList()
        items << "Wiki" << "Latex" << "Shared Memory";
        self.cbtype.addItems(items)
        
        self.controller = None
        self.pptag = 'Image(s) from (%s,%s,%s,%s,%s)'
        
        #options
        self.gbEmbedOpt = QtGui.QGroupBox("Embed Options")
        self.chbPdf = QtGui.QCheckBox("As PDF")
        self.chbSmartTag = QtGui.QCheckBox("Smart Tag")
        self.chbCache = QtGui.QCheckBox("Cache Images")
        self.chbLatexVTL = QtGui.QCheckBox("Include .vtl")
        self.chbLatexVTL.setEnabled(False)
        
        gblayout = QtGui.QGridLayout()
        gblayout.addWidget(self.chbPdf, 0, 0)
        gblayout.addWidget(self.chbSmartTag, 0, 1)
        gblayout.addWidget(self.chbCache, 1, 0)
        gblayout.addWidget(self.chbLatexVTL, 1, 1)
        self.gbEmbedOpt.setLayout(gblayout)
        
        self.gbDownOpt = QtGui.QGroupBox("Download Options")
        self.chbWorkflow = QtGui.QCheckBox("Include Workflow")
        self.chbFullTree = QtGui.QCheckBox("Include Full Tree")
        self.chbFullTree.setEnabled(False)
        self.chbExecute = QtGui.QCheckBox("Execute Workflow")
        self.chbSpreadsheet = QtGui.QCheckBox("Show Spreadsheet Only")
        
        gblayout = QtGui.QGridLayout()
        gblayout.addWidget(self.chbWorkflow, 0, 0)
        gblayout.addWidget(self.chbFullTree, 0, 1)
        gblayout.addWidget(self.chbExecute, 1, 0)
        gblayout.addWidget(self.chbSpreadsheet, 1, 1)
        self.gbDownOpt.setLayout(gblayout)
        
        self.embededt = QtGui.QTextEdit(self)
        self.embededt.setAcceptRichText(False)
        self.embededt.setReadOnly(False)
        # self.exportHtml = '<a href="export">Export...</a>'
        # self.copyHtml = '<a href="copy">Copy to Clipboard</a>'
        # self.copylabel = QtGui.QLabel(self.copyHtml)
        # self.copylabel.setCursor(QtCore.Qt.PointingHandCursor)
        self.copyButton = QtGui.QPushButton() # "Copy to Clipboard")
        self.copyButton.setMinimumSize(50, 30)
        self.link = "copy"
        
        self.helpLabel = QtGui.QLabel()
        # "After making your selection, "
        #                               "click on 'Copy To Clipboard'. "
        #                               "The code changes based on your "
        #                               "selection.")
        self.helpLabel.setWordWrap(True)
        
        font = QtGui.QFont("Arial", 10, QtGui.QFont.Normal)
        font.setItalic(True)
        self.helpLabel.setFont(font)
        
        layout = QtGui.QGridLayout()
        layout.addWidget(label1,0,0)
        layout.addWidget(self.cbcontent,0,1)
        layout.addWidget(label2,1,0)
        layout.addWidget(self.cbtype,1,1)
        layout.addWidget(self.gbEmbedOpt,2,0,1,2)
        layout.addWidget(self.gbDownOpt,3,0,1,2)
        layout.addWidget(self.embededt,4,0,1,-1)
        layout.addWidget(self.helpLabel,5,0,1,2)
        layout.addWidget(self.copyButton,6,1,QtCore.Qt.AlignRight)

        self.setLayout(layout)
        self.changeEmbedType("Wiki")
        
        #connect signals
        self.connect(self.cbtype,
                     QtCore.SIGNAL("activated(const QString &)"),
                     self.changeEmbedType)
        
        # self.connect(self.copylabel,
        #              QtCore.SIGNAL("linkActivated(const QString &)"),
        #              self.linkActivated)

        self.connect(self.copyButton,
                     QtCore.SIGNAL("clicked()"),
                     self.copyClicked)
        
        self.connect(self.cbcontent,
                     QtCore.SIGNAL("activated(const QString &)"),
                     self.changeOption)
        
        optlist = [self.cbcontent,
                   self.chbPdf,
                   self.chbSmartTag,
                   self.chbCache,
                   self.chbLatexVTL,
                   self.chbWorkflow,
                   self.chbFullTree,
                   self.chbExecute,
                   self.chbSpreadsheet]
        for cb in optlist:
            self.connect(cb, QtCore.SIGNAL("toggled(bool)"),
                         self.changeOption)
        #special cases
        self.connect(self.chbWorkflow, QtCore.SIGNAL("toggled(bool)"),
                     self.changeIncludeWorkflow)
        self.connect(self.chbSpreadsheet, QtCore.SIGNAL("toggled(bool)"),
                     self.changeShowSpreadsheet)
        self.connect(self.chbExecute, QtCore.SIGNAL("toggled(bool)"),
                     self.changeExecute)
        self.connect(self.cbcontent,
                     QtCore.SIGNAL("activated(const QString &)"),
                     self.changeContent)
        self.connect(self.chbSmartTag, QtCore.SIGNAL("toggled(bool)"),
                     self.changeSmartTag)
        self.connect(self.chbCache, QtCore.SIGNAL("toggled(bool)"),
                     self.changeCache)
        
    def set_controller(self, controller):
        self.controller = controller
        
    def closeEvent(self,e):
        """ closeEvent(e: QCloseEvent) -> None
        Doesn't allow the Legend widget to close, but just hide
        instead
        
        """
        e.ignore()
        self.hide()
    
    def focusInEvent(self, event):
        if self.controller:
            if self.controller.locator:
                from gui.vistrails_window import _app
                _app.ensureVistrail(self.controller.locator)
                    
                    
    def checkLocator(self):
        """checkLocator() -> bool
        Only vistrails on a database are allowed to embed a tag"""
        result = False
        if self.controller:
            if self.controller.locator:
                title = "Embed Options for %s"%self.controller.locator.name
                self.setWindowTitle(title)
                result = True
        return result

    def checkControllerStatus(self):
        """checkControllerStatus() -> bool
        this checks if the controller has saved the latest changes """
        result = False
        if self.controller:
            result = not self.controller.changed
        return result
    
    def updateEmbedText(self):
        ok = (self.checkLocator() and self.checkControllerStatus() and
              self.versionNumber > 0)
        self.embededt.setEnabled(ok)
        self.copyButton.setEnabled(ok)
        self.embededt.setText('')

        if self.controller and self.versionNumber > 0:
            if self.controller.locator and not self.controller.changed:
                loc = self.controller.locator
                if hasattr(loc,'host'):
                    self.updateCbtype('db')    
                elif hasattr(loc, 'name'):
                    self.updateCbtype('file')
                        
                if self.versionTag != "":
                    self.chbSmartTag.setEnabled(True)
                else:
                    self.chbSmartTag.setChecked(False)
                    self.chbSmartTag.setEnabled(False)
                    
                self.setEmbedText()
            elif self.controller.changed:
                self.embededt.setPlainText('You must save your vistrail to proceed')
            else:
                self.embededt.setPlainText('')
                
    def setEmbedText(self):
        #check options
        options = {}
        options['content'] = str(self.cbcontent.currentText())
        options['pdf'] = self.chbPdf.isChecked()
        options['smartTag'] = self.chbSmartTag.isChecked()
        options['buildalways'] = not self.chbCache.isChecked()
        options['includeWorkflow'] = self.chbWorkflow.isChecked()
        options['includeFullTree'] = self.chbFullTree.isChecked()
        options['execute'] = self.chbExecute.isChecked()
        options['showspreadsheetonly'] = self.chbSpreadsheet.isChecked()
        
        if str(self.cbtype.currentText()) == "Wiki":
            text = self.buildWikiTag(options)
        elif str(self.cbtype.currentText()) == "Latex":
            options['getvtl'] = self.chbLatexVTL.isChecked()
            text = self.buildLatexCommand(options)
        elif str(self.cbtype.currentText()) == "Shared Memory":
            text = self.pptag
        self.embededt.setPlainText(text)
            
    def updateVersion(self, versionNumber):
        self.versionNumber = versionNumber
        if versionNumber > 0:
            self.versionTag = self.controller.vistrail.getVersionName(self.versionNumber)
        self.updateEmbedText()

    def copyClicked(self):
        if self.link == 'copy':
            clipboard = QtGui.QApplication.clipboard()
            clipboard.setText(self.embededt.toPlainText())
        elif self.link=='export':
            app = QtCore.QCoreApplication.instance()
            app.builderWindow.interactiveExportCurrentPipeline()

    # def linkActivated(self, link):
    #     if link=='copy':
    #         clipboard = QtGui.QApplication.clipboard()
    #         clipboard.setText(self.embededt.toPlainText())
    #     elif link=='export':
    #         app = QtCore.QCoreApplication.instance()
    #         app.builderWindow.interactiveExportCurrentPipeline()
    
    def switchType(self, text):
        if text == 'Wiki':
            index = 0
        elif text == "Latex":
            if self.cbtype.count() > 1:
                index = 1
            else:
                index = 0
        else:
            index = 2
        self.cbtype.setCurrentIndex(index)
        self.changeEmbedType(text)
        
    def changeEmbedType(self, text):
        """changeEmbedType(text) -> None
        This is called when the combobox is activated so the proper gui elements
        are enabled.
        
        """
        if text!='Shared Memory':
            # self.copylabel.setText(self.copyHtml)
            self.link = 'copy'
            self.copyButton.setText("Copy to Clipboard")
            self.helpLabel.setText("After making your selections, "
                                   "click on 'Copy To Clipboard'. "
                                   "The code changes based on your "
                                   "selections.")
        else:
            # self.copylabel.setText(self.exportHtml)
            self.link = 'export'
            self.copyButton.setText("Export...")
            self.helpLabel.setText("After making your selections, "
                                   "click 'Export...'. The code changes "
                                   "based on your selections.")
        self.chbLatexVTL.setEnabled(text == 'Latex')
        self.chbPdf.setEnabled(text == 'Latex')
        if self.controller is not None:
            self.setEmbedText()
        
    def changeOption(self, value):
        self.setEmbedText()
        
    def changeContent(self, text):
        if text == "Workflow Results":
            self.chbExecute.setEnabled(True)
            self.chbSpreadsheet.setEnabled(True)
            self.chbCache.setEnabled(True)
            self.chbSmartTag.setEnabled(True)
        else:
            self.chbExecute.setChecked(False)
            self.chbSpreadsheet.setChecked(False)
            self.chbExecute.setEnabled(False)
            self.chbSpreadsheet.setEnabled(False)
            if text == "History Tree Graph":
                self.chbCache.setChecked(False)
                self.chbCache.setEnabled(False)
                self.chbSmartTag.setChecked(False)
                self.chbSmartTag.setEnabled(False)
            else:
                self.chbCache.setEnabled(True)
                self.chbSmartTag.setEnabled(True)
                
    def updateCbtype(self, type):
        currentText = self.cbtype.currentText()
        self.cbtype.clear()
        items = QtCore.QStringList()
        if type == 'db':
            items << "Wiki" << "Latex" << "Shared Memory";
        elif type == 'file':
            items << "Latex";
        self.cbtype.addItems(items)
        index = items.indexOf(currentText)
        if index > 0:
            self.cbtype.setCurrentIndex(index)
        text = str(self.cbtype.currentText())
        self.chbLatexVTL.setVisible(text == 'Latex')
        self.chbPdf.setEnabled(text == 'Latex')
            
    def buildLatexCommand(self, options):
        text = '\\vistrail['
        loc = self.controller.locator
        if hasattr(loc, 'host'):
            text += 'host=%s,\ndb=%s,\nport=%s,\nvtid=%s,\n'% (loc.host,
                                                               loc.db,
                                                               loc.port,
                                                               loc.obj_id)
        else:
            text += 'filename=%s,\n' % os.path.basename(loc.name)
        if options['content'] != "History Tree Graph":    
            text += 'version=%s,\n'%self.versionNumber
            if options['smartTag']:
                text += 'tag={%s},\n'%self.versionTag
        if options['pdf']:
            text += 'pdf,\n'
        if options['buildalways']:
            text+= 'buildalways,\n'
        if options['getvtl']:
            text += 'getvtl,\n'
        if options['includeWorkflow']:
            text+= 'embedworkflow,\n'
            if options['includeFullTree']:
                text += 'includefulltree,\n'
        if options['content'] == "Workflow Graph":
            text += 'showworkflow,\n'
        elif options['content'] == "History Tree Graph":
            text += 'showtree,\n'
        else:
            if options['execute']:
                text += 'execute,\n'
            if options['showspreadsheetonly']:
                text += 'showspreadsheetonly,\n'
        
        text = text[0:-2] + "]{}"
        return text        

    def buildWikiTag(self, options):
        text = '<vistrail '
        loc = self.controller.locator
        
        text += 'host="%s" db="%s" port="%s" vtid="%s" '% (loc.host,
                                                            loc.db,
                                                            loc.port,
                                                            loc.obj_id)
        if options['content'] != "History Tree Graph":
            text += 'version="%s" '%self.versionNumber
            if options['smartTag']:
                text += 'tag="%s " '%self.versionTag
        if options['buildalways']:
            text+= 'buildalways="True" '
        if options['includeWorkflow']:
            text+= 'embedworkflow="True" '
            if options['includeFullTree']:
                text += 'includefulltree="True" '
        if options['content'] == "Workflow Graph":
            text += 'showworkflow="True" ' #"Workflow Results" << "Workflow Graph" << "History Tree Graph";
        elif options['content'] == "History Tree Graph":
            text += 'showtree="True" '
        else:
            if options['execute']:
                text += 'execute="True" '
            if options['showspreadsheetonly']:
                text += 'showspreadsheetonly="True" '
        
        text += "/>"
        return text        

    def changeIncludeWorkflow(self,checked):
        self.chbFullTree.setEnabled(checked)
        if self.cbcontent.currentText() == "History Tree Graph":
            self.chbFullTree.setChecked(checked)
        
    def changeShowSpreadsheet(self, checked):
        if checked:
            self.chbExecute.setChecked(True)
            
    def changeExecute(self, checked):
        if not checked:
            self.chbSpreadsheet.setChecked(False)
            
    def changeSmartTag(self, checked):
        if checked and self.cbtype.currentText() == 'Latex':
            self.chbCache.setChecked(False)
            
    def changeCache(self, checked):
        if checked and self.cbtype.currentText() == 'Latex':
            self.chbSmartTag.setChecked(False)
