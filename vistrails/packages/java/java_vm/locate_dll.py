import os
import platform
import sys


USING_WINDOWS = platform.system() == 'Windows'


def find_executable_from_path(filename):
    pathlist = os.environ['PATH'].split(os.pathsep) + ["."]
    for p in pathlist:
        # On Windows, paths may be enclosed in ""
        if USING_WINDOWS:
            if p.startswith('"') and p.endswith('"'):
                p = p[1:-1]
        fullpath = os.path.join(p, filename)
        if os.path.isfile(fullpath):
            return fullpath
        elif USING_WINDOWS and os.path.isfile(fullpath + '.exe'):
            return fullpath + '.exe'
    return None


def find_java_dll():
    if USING_WINDOWS:
        # First attempt to locate the java executable, and use the DLL of that
        # distribution
        java = find_executable_from_path('java')
        if java is not None:
            # If the 'java' command comes from a JDK, the DLL is located in a
            # 'jre' subdirectory
            path = os.path.realpath(os.path.join(
                java, '../../jre/bin/client/jvm.dll'))
            if os.path.exists(path):
                return path
            else:
                path = os.path.realpath(os.path.join(
                    java, '../client/jvm.dll'))
                if not os.path.exists(path):
                    path = None

        # Else, look for a Java distribution in standard locations
        if sys.maxint > (2 << 32): # 64-bit Python
            paths = ['C:/Program Files/Java']
        else:
            paths = ['C:/Program Files (x86)/Java', 'C:/Program Files/Java']
        for path in paths:
            # First attempt to use the 'jre7' version
            try:
                if os.stat(os.path.join(path, 'jre7')):
                    return os.path.join(path, 'jre7/bin/client/jvm.dll')
            except OSError:
                pass
            # Else, any version
            for subdir in os.listdir(path):
                dll = os.path.join(path, subdir, 'bin/client/jvm.dll')
                try:
                    if os.stat(dll):
                        return dll
                except OSError:
                    pass
        return None
    else:
        # Assume UNIX
        # Attempt to locate the java executable
        java = find_executable_from_path('java')
        java = os.path.realpath(java)

        # Attempt to find libjvm.so around here
        java_home = os.path.realpath(os.path.join(java, '../../lib'))
        for dirpath, dirnames, filenames in os.walk(java_home):
            if 'libjvm.so' in filenames:
                return os.path.join(java_home, dirpath, 'libjvm.so')
