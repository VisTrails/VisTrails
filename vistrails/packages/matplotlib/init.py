###############################################################################
##
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

import copy
import time
import urllib

import vistrails.core.modules
import vistrails.core.modules.module_registry
from vistrails.core import debug
from vistrails.core.modules.basic_modules import File, String, Boolean
from vistrails.core.modules.vistrails_module import Module, NotCacheable, InvalidOutput

from vistrails.core.bundles import py_import
try:
    mpl_dict = {'linux-ubuntu': 'python-matplotlib',
                'linux-fedora': 'python-matplotlib'}
    matplotlib = py_import('matplotlib', mpl_dict)
    matplotlib.use('Qt4Agg', warn=False)
    pylab = py_import('pylab', mpl_dict)
    import matplotlib.transforms as mtransforms
except Exception, e:
    debug.critical("Exception: %s" % e)

from bases import _modules as _base_modules
from plots import _modules as _plot_modules
from artists import _modules as _artist_modules

################################################################################

#list of modules to be displaced on matplotlib.new package
_modules = _base_modules + _plot_modules + _artist_modules

def initialize(*args, **kwargs):
    reg = vistrails.core.modules.module_registry.get_module_registry()
    if reg.has_module('edu.utah.sci.vistrails.spreadsheet',
                      'SpreadsheetCell'):
        from figure_cell import MplFigureCell
        _modules.append(MplFigureCell)
