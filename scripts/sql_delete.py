###############################################################################
##
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
import sys
if '/vistrails/src/trunk/vistrails' not in sys.path:
    sys.path.append('/vistrails/src/trunk/vistrails')
import db.services.io
import urlparse
import getpass

def run(url, type, id):
    scheme, rest = url.split('://', 1)
    url = 'http://' + rest
    (_, net_loc, db_name, args_str, _) = urlparse.urlsplit(url)
    db_name = db_name[1:]
    net_loc_arr = net_loc.split('@',1)
    if len(net_loc_arr) > 1:
        user, rest = net_loc_arr
    else:
        user = 'root'
        rest = net_loc_arr[0]

    host_port_arr = rest.split(':', 1)
    if len(host_port_arr) > 1:
        host, port = host_port_arr
    else:
        host = host_port_arr[0]
        port = '3306'

    config = {'host': host, 'port': int(port),
              'user': user, 'db': db_name}
    print config
    try:
        conn = db.services.io.open_db_connection(config)
    except Exception:
        passwd = getpass.getpass()
        config['passwd'] = passwd
        conn = db.services.io.open_db_connection(config)
        
    db.services.io.delete_from_db(conn, type, id)

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print "Usage: %s %s <db_connection_str> <type> <id>" % \
            (sys.executable, sys.argv[0])
        print "   <db_connection_str> := [<user>@]<host>[:<port>]/<db>"
        print "   Password prompt displayed if required"
        sys.exit(61)
    run(*sys.argv[1:])
