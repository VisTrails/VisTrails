import sys
from PyQt4 import QtGui
from fetch_files import Ui_FetchFiles
app = QtGui.QApplication(sys.argv)
window = Ui_FetchFiles()
window.show()
sys.exit(app.exec_())

