"""Main file for the VisTrails distribution."""

import gui.vis_application
import sys
try:
    app = gui.vis_application.VistrailsApplication(sys.argv)
except SystemExit, e:
    sys.exit(e)
except Exception, e:
    print "Uncaught exception on initialization: %s" % e
    import traceback
    traceback.print_exc()
    sys.exit(255)
if app.configuration.interactiveMode:
    v = app.exec_()
    sys.exit(v)
    
