crondir=`pwd`
export DISPLAY=localhost:1.0
vistrails_dir="/server/wiki/vistrails/main/vistrails/v1.2/vistrails"
cd $vistrails_dir
python stop_vistrails_server.py http://vistrails.sci.utah.edu:8080
nohup python vistrails_server.py -T vistrails.sci.utah.edu -R 8080&