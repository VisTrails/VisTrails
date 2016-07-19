###############################################################################
##
## Copyright (C) 2014-2016, New York University.
## Copyright (C) 2011-2014, NYU-Poly.
## Copyright (C) 2006-2011, University of Utah.
## All rights reserved.
## Contact: contact@vistrails.org
##
## This file is part of VisTrails.
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met:
##
##  - Redistributions of source code must retain the above copyright notice,
##    this list of conditions and the following disclaimer.
##  - Redistributions in binary form must reproduce the above copyright
##    notice, this list of conditions and the following disclaimer in the
##    documentation and/or other materials provided with the distribution.
##  - Neither the name of the New York University nor the names of its
##    contributors may be used to endorse or promote products derived from
##    this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
## AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
## THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
## PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
## CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
## OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
## WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
## OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
## ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
###############################################################################
from __future__ import division

import os
import sys
import getpass
import socket
import datetime
import platform
import tempfile
import warnings

from vistrails.core import debug
from vistrails.core.utils import VistrailsDeprecation


__all__ = ['touch', 'mkdir', 'python_version',
           'current_user', 'current_ip', 'current_time',
           'current_machine', 'current_architecture', 'current_processor',
           'get_elementtree_library', 'temporary_directory']

###############################################################################

def touch(file_name):
    """touch(file_name) -> None Equivalent to 'touch' in a shell. If
    file exists, updates modified time to current time. If not,
    creates a new 0-length file.

    """
    if os.path.isfile(file_name):
        os.utime(file_name, None)
    else:
        open(file_name, 'w')

def mkdir(dir_name):
    """mkdir(dir_name) -> None Equivalent to 'mkdir' in a shell except
    that if the directory exists, it will not be overwritten.

    """
    if not os.path.isdir(dir_name):
        os.mkdir(dir_name)

def python_version():
    """python_version() -> (major, minor, micro, release, serial)
    Returns python version info."""
    return sys.version_info

def current_user():
    return getpass.getuser()

def current_ip():
    """ current_ip() -> str
    Gets current IP address trying to avoid the IPv6 interface """
    try:
        info = socket.getaddrinfo(socket.gethostname(), None)
        # Try to find an IPv4
        for i in info:
            if i[0] == socket.AF_INET:
                return i[4][0]
        # Return any address
        for i in info:
            if i[0] in (socket.AF_INET, socket.AF_INET6):
                return i[4][0]
    except Exception, e:
        debug.unexpected_exception(e)
        return ''

def current_time():
    """current_time() -> datetime.datetime
    Returns the current time

    """
    # FIXME should use DB if available...
    return datetime.datetime.now()

def current_machine():
    return socket.getfqdn()

def current_architecture():
    bit_string = platform.architecture()[0]
    if bit_string.endswith('bit'):
        return int(bit_string[:-3])
    else:
        return 32 # default value

def current_processor():
    proc = platform.processor()
    if not proc:
        proc = 'n/a'
    return proc

def get_elementtree_library():
    try:
        import cElementTree as ElementTree
    except ImportError:
        # try python 2.5-style
        import xml.etree.cElementTree as ElementTree
    return ElementTree

def temporary_directory():
    warnings.warn(
            "temporary_directory() is deprecated; use the tempfile module "
            "instead",
            category=VistrailsDeprecation)
    return tempfile.gettempdir()
