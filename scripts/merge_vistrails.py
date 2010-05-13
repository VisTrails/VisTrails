#!/usr/bin/env python

#FIXME !!! DOES NOT MERGE EXECUTION LOGS STORED IN VT FILE !!!

import sys
if '../vistrails' not in sys.path:
    sys.path.append('../vistrails')

import db.services.vistrail
from db.domain import DBModule, DBConnection, DBPort, DBFunction, \
    DBParameter, DBLocation, DBPortSpec, DBTag, DBAnnotation, DBVistrail, \
    DBAction
from db.services import io

def main(out_fname, in_fnames):
    """main(out_fname: str, in_fnames: list<str>) -> None
    Combines all vistrails specified in in_fnames into a single vistrail
    by renumbering their ids

    """
    # FIXME this breaks when you use abstractions!
    (save_bundle, vt_save_dir) = io.open_bundle_from_zip_xml(DBVistrail.vtType, in_fnames[0])
    for in_fname in in_fnames[1:]:
        (new_save_bundle, new_save_dir) = io.open_bundle_from_zip_xml(DBVistrail.vtType, in_fname)
        db.services.vistrail.merge(save_bundle, new_save_bundle, "", True, vt_save_dir, new_save_dir)
    io.save_bundle_to_zip_xml(save_bundle, out_fname)
    
if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "Usage: %s [output filename] [list of input vistrails]" % \
            sys.argv[0]
        sys.exit(0)
    main(sys.argv[1], sys.argv[2:])
