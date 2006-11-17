""" Module used when running  vistrails uninteractively """
from core import xml_parser
from core import interpreter

def run(input, workflow):
    """ Run the workflow 'workflow' in the 'input' file and generates """ 
    parser = xml_parser.XMLParser()
    parser.openVistrail(input)
    v = parser.getVistrail()
    parser.closeVistrail()
    pip = v.getPipeline(workflow)

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
