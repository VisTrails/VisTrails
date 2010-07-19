from PyQt4 import QtCore
import imp
import sys

def copyDir(src, dst):
    for info in src.entryInfoList():
        if info.isDir():
            dst.mkdir(info.fileName())
            src.cd(info.fileName())
            dst.cd(info.fileName())
            copyDir(src, dst)
            src.cd('..')
            dst.cd('..')
        elif info.isFile():
            QtCore.QFile.copy(info.filePath(), dst.filePath(info.fileName()))
        
if __name__=="__main__":
    if len(sys.argv)!=2:
        print "Usage: python extract.py resource_rc"
        sys.exit(0)

    moduleName = sys.argv[1]
    imp.load_source('resModule', moduleName)
    copyDir(QtCore.QDir(":"), QtCore.QDir("."))
