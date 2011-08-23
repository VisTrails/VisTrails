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
