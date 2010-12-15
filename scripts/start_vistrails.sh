#!/bin/bash

#settings
LOG_DIR=/server/vistrails/logs

VISTRAILS_DIR=/server/vistrails/trunk/vistrails
ADDRESS="crowdlabs.sci.utah.edu"
PORT="8081"
CONF_FILE="server.cfg"
NUMBER_OF_OTHER_VISTRAILS_INSTANCES="2"
MULTI_OPTION="-M"
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
       MULTI_OPTION="-M"
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

export PYTHONPATH=/home/emanuele/src/titan/build/lib:$PYTHONPATH
export LD_LIBRARY_PATH=/home/emanuele/src/titan/build/lib:$LD_LIBRARY_PATH
python vistrails_server.py -T $ADDRESS -R $PORT -C $CONF_FILE -O$NUMBER_OF_OTHER_VISTRAILS_INSTANCES $MULTI_OPTION&
echo $! > $PID

