############################################################################
##
## Copyright (C) 2006-2007 University of Utah. All rights reserved.
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

"""Routines common to Linux and OSX."""

import popen2
import core.utils
import subprocess

def executable_is_in_path(filename):
    """executable_is_in_path(filename): string
    Tests if filename corresponds to an executable file on the path. Returns
the filename if true, or an empty string if false."""
    cmdline = 'which %s' % filename
    process = popen2.Popen4(cmdline)
    result = -1
    while result == -1:
        result = process.poll()
    if result == 256:
        return ""
    if result != 0:
        msg = ("'%s' failed. Return code %s" %
               (cmdline, result))
        raise core.utils.VistrailsInternalError(msg)
    else:
        conv_output = process.fromchild
        output = conv_output.readlines()[0][:-1]
        return output

def list2cmdline(lst):
    for el in lst:
        assert type(el) == str
    return subprocess.list2cmdline(lst)

