#!/usr/bin/env python

""" This script assumes that VisTrails.command file is located at ../ 
Run this script after you copied the VisTrails folder and run from where it 
is located. 

"""
import os, os.path

if __name__ == "__main__":
    # get VisTrails folder
    vt_folder = os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
    app_command = os.path.join(vt_folder,'VisTrails.app/Contents/MacOS/vistrails')
    command_file = os.path.join(vt_folder, 'VisTrails.command')
    
    file_header = """#This will execute VisTrails in a separate terminal window
#If you get an error saying:
#Found another instance of VisTrails running
#Sending parameters to main instance  []
#Failed:  QLocalSocket::connectToServer: Connection refused 
#make sure VisTrails is not already running and simply try to run the script again
#This might indicate that VisTrails did not quit properly 

"""
    file_contents = "DYLD_LIBRARY_PATH= " + app_command
    f = open(command_file, 'w')
    f.write(file_header)
    f.write(file_contents)
    f.close()
    
