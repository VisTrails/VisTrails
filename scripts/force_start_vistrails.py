#!/usr/bin/env python
""" This script will read vistrails pids from files, kill them and call
the script to start vistrails. """

import os.path
import os

#settings
LOG_DIR = '/server/vistrails/logs'
VISTRAILS_SCRIPTS_DIR = '/server/vistrails/trunk/scripts'
SCRIPT = 'start_vistrails.sh'
PORTS = ['8081','8082','8083']


if __name__ == '__main__':
    cmds = []
    for port in PORTS:
        filename = os.path.join(LOG_DIR,
	                        "pid.%s.vistrails"%port)
	f = open(filename)
	pid = f.read()
	f.close()
	cmd = "kill -9 %s"%pid
	cmds.append(cmd)

    start_cmd = "nohup " + os.path.join(VISTRAILS_SCRIPTS_DIR,SCRIPT)
    cmds.append(start_cmd)

    for cmd in cmds:
        os.system(cmd)
