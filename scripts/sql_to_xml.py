import sys
sys.path.append('/vistrails/src/trunk/vistrails')
from db.services import io
import MySQLdb

def convert_sql_to_xml(filename, id):
    config = {'host': 'vistrails.sci.utah.edu', 
              'port': 3306,
              'user': 'vistrails',
              'passwd': '8edLj4',
              'db': 'vistrails'}
    try:
        db_connection = io.open_db_connection(config)        
        vistrail = io.open_vistrail_from_db(db_connection, id)
        io.save_vistrail_to_xml(vistrail, filename)
        io.close_db_connection(db_connection)
    except MySQLdb.Error, e:
        print e

if __name__ == '__main__':
    convert_sql_to_xml('/tmp/vt_from_db.xml', 4)
