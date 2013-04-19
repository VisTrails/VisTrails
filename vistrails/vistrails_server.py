###############################################################################
##
## Copyright (C) 2011-2013, NYU-Poly.
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
"""Main file for running VisTrails in server mode"""
import os
import sys
if __name__ == '__main__':
    # Fix import path: add parent directory(so that we can
    # import vistrails.[gui|...] and remove other paths below it (we might have
    # been started from a subdir)

    # DAK: the deletes screw things up in the binary (definitely for
    #   Mac) and since subdir is unlikely, I'm commenting them out. A
    #   better solution is probably to move vistrails.py up a
    #   directory in the repo
    vistrails_dir = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
    # i = 0
    # print "vistrails_dir:", vistrails_dir
    # while i < len(sys.path):
    #     rpath = os.path.realpath(sys.path[i])
    #     if rpath.startswith(vistrails_dir):
    #         print " deleting", rpath, sys.path[i]
    #         del sys.path[i]
    #     else:
    #         i += 1
    sys.path.insert(0, vistrails_dir)

    import vistrails.gui
    import vistrails.gui.requirements
    vistrails.gui.requirements.check_pyqt4()

    from PyQt4 import QtGui
    import vistrails.gui.application_server
    import sys
    import os
    try:
        v = vistrails.gui.application_server.start_server()
        app = vistrails.gui.application_server.VistrailsServer()
    except SystemExit, e:
        print str(e)
        sys.exit(e)
    except Exception, e:
        print "Uncaught exception on initialization: %s" % e
        import traceback
        traceback.print_exc()
        sys.exit(255)
     
    v = app.run_server()
    vistrails.gui.application_server.stop_server()
    sys.exit(v)
