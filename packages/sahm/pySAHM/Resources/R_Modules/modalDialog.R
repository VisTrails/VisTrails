#This function was robbed from the dynamicGraphic library
"modalDialog" <-
function (title, question, entryInit, top = NULL, entryWidth = 20, 
    returnValOnCancel = "ID_CANCEL", do.grab = FALSE) 
{
    dlg <- tktoplevel()
    tkwm.deiconify(dlg)
    if (do.grab) 
        tkgrab.set(dlg)
    tkfocus(dlg)
    tkwm.title(dlg, title)
    textEntryVarTcl <- tclVar(paste(entryInit))
    textEntryWidget <- tkentry(dlg, width = paste(entryWidth), 
        textvariable = textEntryVarTcl, background = "white")
    tkgrid(tklabel(dlg, text = "       "))
    tkgrid(tklabel(dlg, text = question), textEntryWidget)
    tkgrid(tklabel(dlg, text = "       "))
    ReturnVal <- returnValOnCancel
    "onOK" <- function() {
        ReturnVal <<- tclvalue(textEntryVarTcl)
        tkgrab.release(dlg)
        tkdestroy(dlg)
        if (!is.null(top)) 
            tkfocus(top)
    }
    "onCancel" <- function() {
        ReturnVal <<- returnValOnCancel
        tkgrab.release(dlg)
        tkdestroy(dlg)
        if (!is.null(top)) 
            tkfocus(top)
    }
    OK.but <- tkbutton(dlg, text = "   OK   ", command = onOK)
    Cancel.but <- tkbutton(dlg, text = " Cancel ", command = onCancel)
    tkgrid(OK.but, Cancel.but)
    tkgrid(tklabel(dlg, text = "    "))
    tkfocus(dlg)
    tkbind(dlg, "<Destroy>", function() {
        tkgrab.release(dlg)
        tkfocus(top)
    })
    tkbind(textEntryWidget, "<Return>", onOK)
    tkwait.window(dlg)
    return(ReturnVal)
}

