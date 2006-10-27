import sys
from PyQt4 import QtGui
from db.gui.fetch_files import Ui_FetchFiles

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = Ui_FetchFiles()
    window.show()
    sys.exit(app.exec_())

