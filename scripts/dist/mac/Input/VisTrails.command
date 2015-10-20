#!/bin/sh

# This will execute VisTrails in a separate terminal window
# If you get an error saying:
#     Found another instance of VisTrails running
#     Sending parameters to main instance  []
#     Failed:  QLocalSocket::connectToServer: Connection refused
# make sure VisTrails is not already running and simply try to run the script
# again; this might indicate that VisTrails did not quit properly

cd "$(dirname "$0")"
DYLD_LIBRARY_PATH= VisTrails.app/Contents/MacOS/vistrails
