import sys
from PyQt4 import QtGui
from db.gui.upload_files import Ui_UploadFiles

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = Ui_UploadFiles()
    window.show()
    sys.exit(app.exec_())
