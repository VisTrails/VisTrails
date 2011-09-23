#!/usr/bin/env python
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
