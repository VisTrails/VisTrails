#!/usr/bin/env python
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

from mako.template import Template
import sys
from specs import SpecList

def generate_from_specs(fname, out_fname, template_fname):
    specs = SpecList.read_from_xml(fname)
    
    template = Template(filename=template_fname, 
                        module_directory='/tmp/mako')

    f = open(out_fname, 'wb') # 'b' ensures that we always use LF line endings
    f.write(template.render(specs=specs))
    f.close()        

def run(which="all"):
    if which == "all" or which == "plots":
        generate_from_specs("mpl_plots.xml", "plots.py", 
                            "plots_template.py.mako")
    if which == "all" or which == "artists":
        generate_from_specs("mpl_artists.xml", "artists.py", 
                            "artists_template.py.mako")
    
if __name__ == '__main__':
    if len(sys.argv) <= 1:
        run()
    elif len(sys.argv) == 2:
        run(sys.argv[1])
    else:
        raise TypeError("usage: python parse.py [all|artists|plots]")
