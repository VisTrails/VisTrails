"""Main file for the VisTrails distribution."""

if __name__ == '__main__':
    import gui.vis_application
    import sys
    try:
        app = gui.vis_application.VistrailsApplication()
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
