import sys
from PyQt4 import QtGui
from upload_files import Ui_UploadFiles
app = QtGui.QApplication(sys.argv)
window = Ui_UploadFiles()
window.show()
sys.exit(app.exec_())
