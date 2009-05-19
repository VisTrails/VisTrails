""" This script upgrades the db to the current schema by exporting the vistrails
on the database to files and later importing them.
Please backup your database before using this script.

"""
# MACOSX binary install stuff
import os
import os.path
os.environ['EXECUTABLEPATH'] = '/vistrails/VisTrails.app/Contents/MacOS'
import sys
sys.path.append("../..")
from db.services import io
import db.versions
vistrails = []

current_version = db.versions.currentVersion

def get_db_connection(host, port, user, passwd, db):
    try:
        
        return db_connection
    except Exception, e:
        print str(e)
        raise
        
def setup_tables(config):    
    try:
        db_connection = io.open_db_connection(config)
        io.setup_db_tables(db_connection)
    except Exception, e:
        print e
        raise

def export_all_vistrails_to_files(vistrails_path, config, db_version):
    try:
        db.versions.currentVersion = db_version
        vt_list = io.get_db_object_list(config,'vistrail')
        db_connection = io.open_db_connection(config)
        for (id,obj,date) in vt_list:
            id = int(id)
            name = str(obj)
            vt = io.open_vistrail_from_db(db_connection, id)
            filename = os.path.join(vistrails_path, "%s.vt"%id)
            vistrails.append((id,name,filename))
            io.save_vistrail_to_zip_xml(vt,filename)
        db.versions.currentVersion = current_version
        
    except Exception, e:
        print str(e)
        raise e
        
if __name__ == '__main__':
    args = sys.argv
    if len(args) > 6:
        host = str(args[1])
        port = 3306
        user = str(args[2])
        passwd = str(args[3])
        db_name = str(args[4])
        db_version = str(args[5])
        vistrails_path = str(args[6])
        config = {'host': host, 
              'port': port,
              'user': user,
              'passwd': passwd,
              'db': db_name}
        export_all_vistrails_to_files(vistrails_path, config, db_version)
        #setup_tables(host, port, user, passwd, db)
    else:
        print "Usage: %s host user passwd db db_version path_where_to_save_vistrails_files" % args[0]
