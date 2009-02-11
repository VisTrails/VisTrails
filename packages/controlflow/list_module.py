from core.modules.basic_modules import new_constant

#################################################################################
## The ListOfElements Module

def list_conv(l):
    if (l[0] != '[') and (l[-1] != ']'):
        raise ValueError('List from String in VisTrails should start with \
"[" and end with "]".')
    else:
        l = eval(l)
        return l

ListOfElements = new_constant('ListOfElements' , staticmethod(list_conv), [],\
                              staticmethod(lambda x: type(x) == list))
