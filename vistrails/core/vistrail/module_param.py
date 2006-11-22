""" This module contains class definitions for:
    * VistrailModuleType
    * ModuleParam

 """
from core.utils import enum

################################################################################

VistrailModuleType = enum('VistrailModuleType',
                          ['Invalid', 'Abstract', 'Filter', 
                           'Object', 'Plugin', 'Module'])

################################################################################

class ModuleParam(object):
    __fields__ = ['type', 'strValue', 'name', 'minValue', 'maxValue', 'alias']
    """ Stores a parameter setting for a vistrail function """
    def __init__(self):
        self.type = ""
        self.strValue = ""
        self.name = ""
        self.alias = ""
        self.minValue = ""
        self.maxValue = ""
        self.evaluatedStrValue = ""
        
    def serialize(self, dom, element):
        """ serialize(dom, element) -> None 
        Writes itself in XML 

        """
        child = dom.createElement('param')
        child.setAttribute('name',self.name)
        ctype = dom.createElement('type')
        cval = dom.createElement('val')
        calias = dom.createElement('alias')
        ttype = dom.createTextNode(self.type)
        tval = dom.createTextNode(self.strValue)        
        talias = dom.createTextNode(self.alias)
        child.appendchild(ctype)
        child.appendChild(cval)
        ctype.appendChild(ttype)
        cval.appendChild(tval)
        calias.appendChild(talias)
        element.appendChild(child)

    def value(self):
        """  value() -> any type 
        Returns its strValue as a python type.

        """
        if self.strValue == "":
            self.strValue = ModuleParam.defaultValue[self.type][0]
            return ModuleParam.defaultValue[self.type][1]
        return ModuleParam.dispatchValue[self.type](self.strValue)

    dispatchValue = {'Float': float,
                     'Integer': int,
                     'String': str,
                     'Boolean': bool}

    defaultValue = {'Float': ("0", 0.0),
                    'Integer': ("0", 0),
                    'String': ("", ""),
                    'Boolean': ("False", "False")}

#     dispatchValue = {'float': float,
#                      'double': float,
#                      'int': int,
#                      'vtkIdType': int,
#                      'string': str,
#                      'str': str,
#                      'const char *': str,
#                      'const char*': str,
#                      'char *': str,
#                      'char*': str}

    def quoteValue(self):
        """ quoteValue() -> str -  Returns its strValue as an quote string."""
        return ModuleParam.dispatchQuoteValue[self.type](self.strValue)
    
    dispatchQuoteValue = {'float': str,
                          'double': str,
                          'int': str,
                          'vtkIdType': str,
                          'str': lambda x: "'" + str(x) + "'",
                          'string': lambda x: "'" + str(x) + "'",
                          'const char *': lambda x: "'" + str(x) + "'",
                          'const char*': lambda x: "'" + str(x) + "'",
                          'char *': lambda x: "'" + str(x) + "'",
                          'char*': lambda x: "'" + str(x) + "'"}

    def __str__(self):
        """ __str__() -> str - Returns a string representation of itself """
        if self.minValue != "":
            f = (self.name, self.type, self.strValue, 
                 self.minValue, self.maxValue, self.alias)
            return "<<name='%s' type='%s' strValue='%s' minValue='%s' " \
                " maxValue='%s' alias='%s'>>" % f
        else:
            return "<<name='%s' type='%s' strValue='%s' " \
                "alias='%s'>>" % (self.name,
                                  self.type,
                                  self.strValue,
                                  self.alias)

###############################################################################
##TODO: include test cases
