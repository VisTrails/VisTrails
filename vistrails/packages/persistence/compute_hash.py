############################################################################
##
## Copyright (C) 2006-2009 University of Utah. All rights reserved.
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

import os
try:
    import hashlib
    sha_hash = hashlib.sha1
except ImportError:
    import sha
    sha_hash = sha.new

def compute_hash(persistent_path, is_dir=None):
    def hash_file(filename, hasher):
        f = open(filename, 'rb')
        while True:
            block = f.read(8192)
            if not block:
                break
            hasher.update(block)

    sha_hasher = sha_hash()
    if is_dir is None:
        is_dir = os.path.isdir(persistent_path)
    if is_dir:
        # get all of the files we need to hash
        fnames = []
        base_dir = persistent_path
        dir_stack = ['.']
        while dir_stack:
            dir = dir_stack.pop()
            for base in sorted(os.listdir(os.path.join(base_dir, dir))):
                name = os.path.join(dir, base)
                if os.path.isdir(os.path.join(base_dir, name)):
                    dir_stack.append(name)
                else:
                    fnames.append(name)

        # hash filenames and files to ensure directory structure
        # is accounted for
        for fname in fnames:
            # print fname
            sha_hasher.update(fname)
            hash_file(os.path.join(base_dir, fname), sha_hasher)
    else:
        hash_file(persistent_path, sha_hasher)
    return sha_hasher.hexdigest()

if __name__ == '__main__':
    import sys
    print compute_hash(sys.argv[1])
