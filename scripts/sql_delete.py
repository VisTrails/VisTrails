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
