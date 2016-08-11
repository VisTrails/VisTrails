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

from io import BytesIO
import zipfile
import sys

from vistrails.core.system import get_elementtree_library
import vistrails.db.services.io as vtdbio
from vistrails.core.db.locator import FileLocator
import vistrails.db.versions
import vistrails.db.versions.v2_0_0.translate.v1_0_4 as uuid_translate

ElementTree = get_elementtree_library()

def run(fname, new_fname=None):

    if fname.endswith('.xml'):
        # no bundle, straightforward
        tree = ElementTree.parse(fname)
        version = vtdbio.get_version_for_xml(tree.getroot())
        # disable translation by passing current version
        vistrail = vtdbio.open_vistrail_from_xml(fname, version)
    elif fname.endswith('.vt'):
        # have bundle
        with zipfile.ZipFile(fname) as zf:
            vistrail_f = BytesIO(zf.read("vistrail"))
            tree = ElementTree.parse(vistrail_f)
            version = vtdbio.get_version_for_xml(tree.getroot())

        # disable translation by hacking currentVersion
        current_version = vistrails.db.versions.currentVersion
        vistrails.db.versions.currentVersion = version
        try:
            (bundle, save_dir) = vtdbio.open_vistrail_bundle_from_zip_xml(fname)
            vistrail = bundle.vistrail
        finally:
            vistrails.db.versions.currentVersion = current_version

    elif fname.endswith('.vtl'):
        # locator file
        pass

    # now want to translate vistrail but preserve the id_remap
    # make translation to 1.0.5, then rest manually
    # may need to watch through translations...?
    # otherwise, could just set currentVersion to 1.0.4 and skip version checks
    vistrail = vistrails.db.versions.translate_vistrail(vistrail, version, '1.0.4')

    external_data = {"id_remap": {}}
    new_vistrail = uuid_translate.translateVistrail(vistrail, external_data)

    for k,v in external_data["id_remap"].iteritems():
        print k, '->', v

    vtdbio.save_vistrail_to_xml(new_vistrail, new_fname)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python {} <vt-file>".format(sys.argv[0]))

    run(*sys.argv[1:])
