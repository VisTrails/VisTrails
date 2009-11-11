#!/bin/bash

#settings
LOG_DIR=/server/wiki/vistrails/main/vistrails/logs
LOG_XVFB=$LOG_DIR/xvfb.log
Xvfb_CMD=/usr/X11R6/bin/Xvfb
VIRTUAL_DISPLAY=":7"
Xvfb_PARAM="$VIRTUAL_DISPLAY -screen 0 1280x960x24"
PID=$LOG_DIR/pid.vistrails
VISTRAILS_DIR=/server/wiki/vistrails/main/vistrails/trunk/vistrails

#try to find Process ID of running X-Server
pid=`ps -eaf | grep $Xvfb_CMD | grep $VIRTUAL_DISPLAY | awk '{print $2}'`
if [ $pid ]; then
    echo "Xvfb already running [pid=${pid}]"
else
    #start a virtual server
    if [ -x $Xvfb_CMD ]; then
	$Xvfb_CMD $Xvfb_PARAM>& $LOG_XVFB &
	
	sleep 5

	#Make sure it started
	pid=`ps -eaf | grep $Xvfb_CMD | grep $VIRTUAL_DISPLAY | awk '{print $2}'`
	if [ $pid ]; then
	    echo "done."
	else
	    echo "FAILED."
	fi
    else
	echo "Error: Could not find $Xvfb_CMD. Cannot start Xvfb."
    fi
fi
echo -n "Starting VisTrails in Server Mode on display $VIRTUAL_DISPLAY.0 - "
cd $VISTRAILS_DIR
export DISPLAY=$VIRTUAL_DISPLAY
python stop_vistrails_server.py http://vistrails.sci.utah.edu:8080
LD_LIBRARY_PATH=/usr/local/lib:/usr/local/lib/vtk-5.4 PYTHONPATH=/usr/local/lib64/python2.4/site-packages:$PYTHONPATH python vistrails_server.py -T "vistrails.sci.utah.edu" -R 8080&
echo $! > $PID

