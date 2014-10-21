#!/bin/bash
###############################################################################
##
## Copyright (C) 2011-2014, NYU-Poly.
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
#settings
LOG_DIR=/server/vistrails/logs
Xvfb_CMD=/usr/bin/Xvfb
VIRTUAL_DISPLAY=":6"
VISTRAILS_DIR=/server/vistrails/git/vistrails
ADDRESS="vis-7.sci.utah.edu"
PORT="8081"
CONF_FILE="server.cfg"
NUMBER_OF_OTHER_VISTRAILS_INSTANCES="1"
MULTI_OPTION="--multithread"
if (("$#" > "0")); then
    VIRTUAL_DISPLAY="$1"
fi
if (("$#" > "1")); then
    ADDRESS="$2"
fi
if (("$#" > "2")); then
    PORT="$3"
fi
if (("$#" > "3")); then
    NUMBER_OF_OTHER_VISTRAILS_INSTANCES="$4"
fi
if (("$#" == "5")); then
   if(("$5" == "0")); then
       MULTI_OPTION=""
   else
       MULTI_OPTION="--multithread"
   fi
fi

Xvfb_PARAM="$VIRTUAL_DISPLAY -screen 0 1280x960x24"
PID="$LOG_DIR/pid.$PORT.vistrails"
LOG_XVFB="$LOG_DIR/xvfb$VIRTUAL_DISPLAY.log"

#try to find Process ID of running X-Server
echo "checking if Xvfb is already running..."
echo "ps -eaf | grep $Xvfb_CMD | grep $VIRTUAL_DISPLAY | awk '{print \$2}'"
pid=`ps -eaf | grep $Xvfb_CMD | grep $VIRTUAL_DISPLAY | awk '{print \$2}'`
if [ "$pid" ]; then
    echo "Xvfb already running [pid=${pid}]"
else
    #start a virtual server
    if [ -x $Xvfb_CMD ]; then
	$Xvfb_CMD $Xvfb_PARAM>& $LOG_XVFB &
	
	sleep 5

	#Make sure it started
	pid=`ps -eaf | grep $Xvfb_CMD | grep $VIRTUAL_DISPLAY | awk '{print $2}'`
	if [ "$pid" ]; then
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
python stop_vistrails_server.py http://$ADDRESS:$PORT
#give some time for quitting                                                             
sleep 5
#try again because sometimes it doesn't quit                                           
python stop_vistrails_server.py http://$ADDRESS:$PORT
sleep 5

#finally kill it if it still did not respond because it was hanging
kill -9 `cat $PID`

python vistrails_server.py --rpc-server=$ADDRESS --rpc-port $PORT --rpc-config $CONF_FILE --rpc-instances $NUMBER_OF_OTHER_VISTRAILS_INSTANCES $MULTI_OPTION&
echo $! > $PID

