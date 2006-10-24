from vis_application import VistrailsApplication
import sys

try:
    app = VistrailsApplication(sys.argv)
except SystemExit, e:
    sys.exit(e)
except Exception, e:
    print "Uncaught exception on initialization: %s" % e
    import traceback
    traceback.print_exc()
    sys.exit(255)
# there's no need to run the application on console mode
if app.configuration.interactiveMode:
    v = app.exec_()
#     sys.exit(v)

