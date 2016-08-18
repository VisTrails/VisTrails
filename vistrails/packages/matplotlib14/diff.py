###############################################################################
##
## Copyright (C) 2014-2015, New York University.
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

import sys

from vistrails.core.wrapper.diff import compute_diff, apply_diff, compute_upgrade

from mpl_specs import MPLFunctionSpec


def run_compute():
    compute_diff(MPLFunctionSpec, "mpl_artists_raw.xml",
                 "mpl_artists.xml", "mpl_artists_diff.xml")
    compute_diff(MPLFunctionSpec, "mpl_plots_raw.xml",
                 "mpl_plots.xml", "mpl_plots_diff.xml")


def run_apply():
    apply_diff(MPLFunctionSpec, "mpl_artists_raw.xml", "mpl_artists_diff.xml", "mpl_artists.xml")
    apply_diff(MPLFunctionSpec, "mpl_plots_raw.xml", "mpl_plots_diff.xml", "mpl_plots.xml")


def usage():
    print "Usage: %s %s [apply|compute|upgrade spec1 spec2|spec1, spec2)]" % (sys.executable, sys.argv[0])


if __name__ == '__main__':
    if len(sys.argv) < 2:
        usage()
    elif sys.argv[1] == "apply":
        run_apply()
    elif sys.argv[1] == "compute":
        run_compute()
    elif sys.argv[1] == "upgrade":
        compute_upgrade(MPLFunctionSpec, sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 3:
        compute_diff(MPLFunctionSpec, sys.argv[1], sys.argv[2], show_docstring=False)
    else:
        usage()
