############################################################################
##
## Copyright (C) 2006-2010 University of Utah. All rights reserved.
##
## This file is part of VisTrails.
##
## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of
## this file.  Please review the following to ensure GNU General Public
## Licensing requirements will be met:
## http://www.opensource.org/licenses/gpl-license.php
##
## If you are unsure which license is appropriate for your use (for
## instance, you are interested in developing a commercial derivative
## of VisTrails), please contact us at vistrails@sci.utah.edu.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################
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
