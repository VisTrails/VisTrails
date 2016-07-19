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

class MplCorrBaseMixin(object):
    def compute_after():
        if 'usevlines' in kwargs and kwargs['usevlines']:
            output = output + (output[2],)
        else:
            output = output + (None, None)

class MplAcorrMixin(MplCorrBaseMixin):
    pass

class MplXcorrMixin(MplCorrBaseMixin):
    pass

class MplBoxplotMixin(object):
    def compute_after():
        if 'patch_artist' in kwargs and kwargs['patch_artist']:
            output['boxPatches'] = output['boxes']
            output['boxes'] = []
        else:
            output['boxPatches'] = []

class MplContourBaseMixin(object):
    def compute_before():
        if self.has_input("N") and self.has_input("V"):
            del args[-1]

class MplContourMixin(MplContourBaseMixin):
    def compute_inner():
        contour_set = matplotlib.pyplot.contour(*args, **kwargs)
        output = (contour_set, contour_set.collections)

class MplContourfMixin(MplContourBaseMixin):
    def compute_inner():
        contour_set = matplotlib.pyplot.contourf(*args, **kwargs)
        output = (contour_set, contour_set.collections)

class MplPieMixin(object):
    def compute_after():
        if len(output) < 3:
            output = output + ([],)

class MplAnnotateMixin(object):
    def compute_before():
        if self.has_input("fancyArrowProperties"):
            kwargs['arrowprops'] = \
                self.get_input("fancyArrowProperties").props
        elif self.has_input("arrowProperties"):
            kwargs['arrowprops'] = \
                self.get_input("arrowProperties").props

class MplSpyMixin(object):
    def compute_after():
        if "marker" not in kwargs and "markersize" not in kwargs and \
                not hasattr(kwargs["Z"], 'tocoo'):
            output = (output, None)
        else:
            output = (None, output)

class MplBarMixin(object):
    def compute_before(self):
        if not kwargs.has_key('left'):
            kwargs['left'] = range(len(kwargs['height']))
