"""TODO: This module is broken in the plugin branch. Fix it."""

import xml_parser

def run(input, workflow):
    """ Run the workflow 'workflow' in the 'input' file and generates 
    the 'outputfile' """ 
    parser = xml_parser.XMLParser()
    parser.openVistrail(input)
    v = parser.getVistrail()
    parser.closeVistrail()
    pip = v.getPipeline(workflow)
    import interpreter
    error = False
    (objs, errors) = interpreter.Interpreter().execute(pip)
    for obj in objs.itervalues():
        i = obj.id
        if errors.has_key(i):
            error = True
    if error:
        print "There was an error when executing the workflow."
    else:
        print "Success"
