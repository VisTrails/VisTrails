###############################################################################
##
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
##  - Neither the name of the University of Utah nor the names of its 
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
"""Contains compatibility functions between Python versions.
"""

from __future__ import division

import urllib


def ascii_s(s):
    """Makes sure `s` is the native str type, encoding as ASCII if necessary.
    """
    if isinstance(s, unicode):
        return s.encode('ascii')
    else:
        return s


def quote(s):
    """Quotes bytes or unicode to unicode (uses UTF-8).
    """
    if isinstance(s, unicode):
        s = s.encode('utf-8')
    return urllib.quote(s).decode('ascii')


def unquote(s):
    """Unquotes unicode to unicode (assumes UTF-8).
    """
    if isinstance(s, unicode):
        s = s.encode('ascii')
    return urllib.unquote(s).decode('utf-8')


def new_type(name, bases, dct):
    """Variant of type() that won't choke on unicode names.
    """
    return type(ascii_s(name), bases, dct)

################################################################################

# Only works for functions with NO kwargs!
def memo_method(method, cache_size=1024):
    """Memoizing decorator.

    This retains past results of the decorated method.
    """
    attrname = "_%s_memo_result" % id(method)
    cache = {}
    def decorated(self, *args, **kwargs):
        key = args, frozenset(kwargs.iteritems())
        try:
            return cache[key]
        except KeyError:
            result = method(self, *args, **kwargs)
            if len(cache) > cache_size:
                cache.clear()
            cache[key] = result
            return result
    warn = ("(This is a memoized method: Don't mutate the return value you're "
            "given.)")
    if method.__doc__:
        decorated.__doc__ = method.__doc__ + "\n\n" + warn
    else:
        decorated.__doc__ = warn
    return decorated
