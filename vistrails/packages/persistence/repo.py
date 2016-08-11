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

from vistrails.core.bundles import py_import
py_import('dulwich', {
        'pip': 'dulwich',
        'linux-debian': 'python-dulwich',
        'linux-ubuntu': 'python-dulwich',
        'linux-fedora': 'python-dulwich'})
from vistrails.core import debug

from dulwich.errors import NotCommitError, NotGitRepository
from dulwich.repo import Repo
from dulwich.objects import Commit, Blob, Tree, object_header
from dulwich.pack import iter_sha1
from dulwich.walk import Walker
from itertools import chain
import os
import shutil
import stat
import tempfile

class GitRepo(object):
    def __init__(self, path):
        if os.path.exists(path):
            if not os.path.isdir(path):
                raise IOError('Git repository "%s" must be a directory.' %
                              path)
        try:
            self.repo = Repo(path)
        except NotGitRepository:
            # repo does not exist
            self.repo = Repo.init(path, not os.path.exists(path))
    
        self.temp_persist_files = []

    def _get_commit(self, version="HEAD"):
        commit = self.repo[version]
        if not isinstance(commit, Commit):
            raise NotCommitError(commit)
        return commit

    def get_type(self, name, version="HEAD"):
        commit = self._get_commit(version)

        tree = self.repo.tree(commit.tree)
        if name not in tree:
            raise KeyError('Cannot find object "%s"' % name)
        if tree[name][0] & stat.S_IFDIR:
            return "tree"
        else:
            return "blob"

    def get_path(self, name, version="HEAD", path_type=None, out_name=None,
                 out_suffix=''):
        if path_type is None:
            path_type = self.get_type(name, version)
        if path_type == 'tree':
            return self.get_dir(name, version, out_name, out_suffix)
        elif path_type == 'blob':
            return self.get_file(name, version, out_name, out_suffix)

        raise TypeError("Unknown path type '%s'" % path_type)

    def _write_blob(self, blob_sha, out_fname=None, out_suffix=''):
        if out_fname is None:
            # create a temporary file
            (fd, out_fname) = tempfile.mkstemp(suffix=out_suffix,
                                               prefix='vt_persist')
            os.close(fd)
            self.temp_persist_files.append(out_fname)
        else:
            out_dirname = os.path.dirname(out_fname)
            if out_dirname and not os.path.exists(out_dirname):
                os.makedirs(out_dirname)
        
        blob = self.repo.get_blob(blob_sha)
        with open(out_fname, "wb") as f:
            for b in blob.as_raw_chunks():
                f.write(b)
        return out_fname

    def get_file(self, name, version="HEAD", out_fname=None, 
                 out_suffix=''):
        commit = self._get_commit(version)
        tree = self.repo.tree(commit.tree)
        if name not in tree:
            raise KeyError('Cannot find blob "%s"' % name)
        blob_sha = tree[name][1]
        out_fname = self._write_blob(blob_sha, out_fname, out_suffix)
        return out_fname

    def get_dir(self, name, version="HEAD", out_dirname=None, 
                out_suffix=''):
        if out_dirname is None:
            # create a temporary directory
            out_dirname = tempfile.mkdtemp(suffix=out_suffix,
                                           prefix='vt_persist')
            self.temp_persist_files.append(out_dirname)
        elif not os.path.exists(out_dirname):
            os.makedirs(out_dirname)
        
        commit = self._get_commit(version)
        tree = self.repo.tree(commit.tree)
        if name not in tree:
            raise KeyError('Cannot find tree "%s"' % name)
        subtree_id = tree[name][1]
        # subtree = self.repo.tree(subtree_id)
        for entry in self.repo.object_store.iter_tree_contents(subtree_id):
            out_fname = os.path.join(out_dirname, entry.path)
            self._write_blob(entry.sha, out_fname)
        return out_dirname

    def get_hash(self, name, version="HEAD", path_type=None):
        commit = self._get_commit(version)
        tree = self.repo.tree(commit.tree)
        if name not in tree:
            raise KeyError('Cannot find object "%s"' % name)
        return tree[name][1]

    @staticmethod
    def compute_blob_hash(fname, chunk_size=1<<16):
        obj_len = os.path.getsize(fname)
        head = object_header(Blob.type_num, obj_len)
        with open(fname, "rb") as f:
            def read_chunk():
                return f.read(chunk_size)
            my_iter = chain([head], iter(read_chunk,''))
            return iter_sha1(my_iter)

    @staticmethod
    def compute_tree_hash(dirname):
        tree = Tree()
        for entry in sorted(os.listdir(dirname)):
            fname = os.path.join(dirname, entry)
            if os.path.isdir(fname):
                thash = GitRepo.compute_tree_hash(fname)
                mode = stat.S_IFDIR # os.stat(fname)[stat.ST_MODE]
                tree.add(entry, mode, thash)
            elif os.path.isfile(fname):
                bhash = GitRepo.compute_blob_hash(fname)
                mode = os.stat(fname)[stat.ST_MODE]
                tree.add(entry, mode, bhash)
        return tree.id

    @staticmethod
    def compute_hash(path):
        if os.path.isdir(path):
            return GitRepo.compute_tree_hash(path)
        elif os.path.isfile(path):
            return GitRepo.compute_blob_hash(path)
        raise TypeError("Do not support this type of path")

    def get_latest_version(self, path):
        head = self.repo.head()
        walker = Walker(self.repo.object_store, [head], max_entries=1, 
                        paths=[path])
        return iter(walker).next().commit.id

    def _stage(self, filename):
        fullpath = os.path.join(self.repo.path, filename)
        if os.path.islink(fullpath):
            debug.warning("Warning: not staging symbolic link %s" % os.path.basename(filename))
        elif os.path.isdir(fullpath):
            for f in os.listdir(fullpath):
                self._stage(os.path.join(filename, f))
        else:
            if os.path.sep != '/':
                filename = filename.replace(os.path.sep, '/')
            self.repo.stage(filename)

    def add_commit(self, filename):
        self.setup_git()
        self._stage(filename)
        commit_id = self.repo.do_commit('Updated %s' % filename)
        return commit_id

    def setup_git(self):
        config_stack = self.repo.get_config_stack()

        try:
            config_stack.get(('user',), 'name')
            config_stack.get(('user',), 'email')
        except KeyError:
            from vistrails.core.system import current_user
            from dulwich.config import ConfigFile
            user = current_user()
            repo_conf = self.repo.get_config()
            repo_conf.set(('user',), 'name', user)
            repo_conf.set(('user',), 'email', '%s@localhost' % user)
            repo_conf.write_to_path()

current_repo = None

def get_current_repo():
    return current_repo
def set_current_repo(repo):
    global current_repo
    current_repo = repo

def get_repo(path):
    return GitRepo(path)

def run_get_file_test():
    r = GitRepo("/vistrails/src/git")
    r.get_file("README.md", "HEAD", "testREADMEout.md")

def run_get_dir_test():
    r = GitRepo("/vistrails/src/git")
    r.get_dir("scripts", "HEAD", "testScriptsout")

def run_get_type_test():
    r = GitRepo("/vistrails/src/git")
    print "README.md:", r.get_type("README.md")
    print "scripts:", r.get_type("scripts")

def run_compute_sha_test():
    r = GitRepo("/vistrails/src/git")
    print r.get_hash("README.md")
    # print r.compute_blob_hash("/Users/dakoop/Downloads/xcode_2.4.1_8m1910_6936315.dmg")        
    print r.compute_blob_hash("/vistrails/src/git/README.md")

def run_compute_sha_dir_test():
    r = GitRepo("/vistrails/src/git")
    print r.get_hash("scripts")
    print r.compute_tree_hash("/vistrails/src/git/scripts")

def run_get_latest_test():
    r = GitRepo("/vistrails/src/git")
    print r.get_latest_version("README.md")

def run_init_add_test():
    r = GitRepo("/Users/dakoop/.vistrails/git_test")
    shutil.copy("/vistrails/src/git/README.md", 
                "/Users/dakoop/.vistrails/git_test")
    print r.add_commit("README.md")

if __name__ == '__main__':
    run_init_add_test()
