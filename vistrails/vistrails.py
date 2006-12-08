"""Main file for the VisTrails distribution."""

if __name__ == '__main__':
    import gui.application
    import sys
    try:
        gui.application.start_application()
        app = gui.application.VistrailsApplication()
    except SystemExit, e:
        sys.exit(e)
    except Exception, e:
        print "Uncaught exception on initialization: %s" % e
        import traceback
        traceback.print_exc()
        sys.exit(255)
    if app.configuration.interactiveMode:
        v = app.exec_()
        gui.application.stop_application()
        sys.exit(v)
