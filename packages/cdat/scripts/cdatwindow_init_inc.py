    
    ##########################################################################
    # included from cdatwindow_init_inc.py
    display = sip.unwrapinstance(QtGui.QX11Info.display())
    vcs._vcs.setdisplay(display)

    #cdat GUI modules
    global cdatWindow
    cdatWindow = QCDATWindow()
    cdatWindow.show()

    reg.add_module(quickplot,namespace='cdat')
    reg.add_input_port(quickplot, 'dataset',
                       (TransientVariable,"variable to be plotted"))
    reg.add_input_port(quickplot, 'plot',
                       (core.modules.basic_modules.String,"Plot type"))

    # end of cdatwindow_init_inc.py
    ##########################################################################
    