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

VISTRAILS_DIR=../vistrails
ADDRESS="localhost"
PORT="8081"
CONF_FILE="server.cfg"
NUMBER_OF_OTHER_VISTRAILS_INSTANCES="2"
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

PID="$LOG_DIR/pid.$PORT.vistrails"

echo -n "Starting VisTrails in Server Mode on display :0 - "
cd $VISTRAILS_DIR
export DISPLAY=:0
python stop_vistrails_server.py http://$ADDRESS:$PORT
sleep 5
#try again because sometimes it doesn't quit
python stop_vistrails_server.py http://$ADDRESS:$PORT

#finally kill it if it still did not respond because it was hanging
kill -9 `cat $PID`

export PYTHONPATH=/home/emanuele/src/titan/build/lib:$PYTHONPATH
export LD_LIBRARY_PATH=/home/emanuele/src/titan/build/lib:$LD_LIBRARY_PATH
python vistrails_server.py --rpc-server $ADDRESS --rpc-port $PORT --rpc-config $CONF_FILE --rpc-instances $NUMBER_OF_OTHER_VISTRAILS_INSTANCES $MULTI_OPTION&
echo $! > $PID

