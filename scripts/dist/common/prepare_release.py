#!/usr/bin/env python
# Updates the binary changelogs, version numbers, hash, and branch from CHANGELOG
# First updates hash in changelog if git is available
# Run and commit changes to git before building release
import os
import re
import subprocess
import sys

CHANGELOG = "CHANGELOG"

RE_BASE = r'(?<=%s)([0-9a-zA-Z._+-]+)'

# [filename, preceding string]
VERSION_FILES = [
    ["scripts/create_release_wiki_table.py", r'VT_VERSION = [\'"]'],
    ["scripts/create_release_wiki_table.py", r'SF_FOLDER_NAME = [\'"]v'], # a second pass
    ["vistrails/core/system/__init__.py", r'VERSION = [\'"]'],
    ["scripts/dist/mac/setup.py", r'VERSION = [\'"]'],
    ["scripts/dist/windows/vistrails.iss", r'AppVerName=VisTrails '],
    ["scripts/dist/windows/vistrailsx64.iss", r'AppVerName=VisTrails x64 '],
    ["scripts/dist/windows/vistrails-gdal.iss", r'AppVerName=VisTrails '],
    ["scripts/dist/windows/vistrailsx64-gdal.iss", r'AppVerName=VisTrails x64 '],
    ["scripts/dist/source/make-vistrails-src-build.py", r'VT_VERSION = [\'"]'],
    ["setup.py", r'version=[\'"]'],
    ["doc/usersguide/conf.py", r'release = [\'"]'],
    ["scripts/dist/common/splash/splash.svg", r'tspan4025">'],
    ["scripts/dist/common/splash/splash.svg", r'tspan4025-7">']] # second pass for shadow

HASH_FILES = [["scripts/create_release_wiki_table.py", r'VT_REVISION = [\'"]'],
              ["scripts/dist/source/make-vistrails-src-build.py", r'VT_HASH = [\'"]']]

BRANCH_FILES = [ # For places that should not use 'v' prefix
   ["doc/usersguide/conf.py", r'version = [\'"]']]

BRANCH_FILES_V = [
   ["scripts/dist/source/make-vistrails-src-build.py", r'VT_BRANCH = [\'"]']]

BRANCH_URLS = [ # For places that should use dev for master
   ["scripts/get_usersguide.py", r'http://www.vistrails.org/usersguide/']]

def update_value(fname, pre, value):
    """
    fname: file name
    pre: prefix to search for
    value: new value

    """
    rexp = re.compile(RE_BASE % pre)

    with open(fname, 'rb') as fp:
        lines = fp.readlines()

    i = 0
    replaced = False
    while i < len(lines):
        line = lines[i]
        m = rexp.search(line)
        if m is not None:
            lines[i] = rexp.sub(value, line)
            if line != lines[i]:
                print '%s:\n' % fname, line, lines[i],
            replaced = True
            break
        i += 1

    if not replaced:
        sys.stderr.write(fname + ": Didn't find version number to replace\n")
        sys.exit(1)

    with open(fname, 'wb') as fp:
        for line in lines:
            fp.write(line)

if __name__ == '__main__':
    os.chdir(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

    # Read CHANGELOG
    with open(CHANGELOG, 'rb') as fp:
        lines = fp.readlines()

    # Get info from CHANGELOG
    # Assumes 3:rd line and fixed format
    line = lines[2].split()
    version = line[2][1:] # Drop "v" prefix
    hash = line[4]
    branch = line[6]

    try:
        read_hash = subprocess.check_output(['git', 'rev-parse', '--verify', 'HEAD',
                                             '--short=12']).strip()
        if read_hash != hash:
            # update hash in changelog
            update_value('CHANGELOG', r'Release Name: v%s build ' % version, read_hash)
            hash = read_hash
    except subprocess.CalledProcessError: # Not a git repository
        pass

    for fname, pre in VERSION_FILES:
       update_value(fname, pre, version)

    for fname, pre in HASH_FILES:
       update_value(fname, pre, hash)

    for fname, pre in BRANCH_FILES:
        # Cut off 'v' in versioned branches
        file_branch = branch[1:] if branch[0] == 'v' else branch
        update_value(fname, pre, file_branch)

    for fname, pre in BRANCH_FILES_V:
        update_value(fname, pre, branch)

    for fname, pre in BRANCH_URLS:
        # master version of usersguide url is 'dev'
        url_branch = 'dev' if branch in ['dev', 'master'] else branch
        update_value(fname, pre, url_branch)

    # Update splash using inkscape
    try:
        subprocess.check_call([
            'inkscape',
            '-e', 'vistrails/gui/resources/images/vistrails_splash.png',
            '-w', '546',
            'scripts/dist/common/splash/splash.svg'])
    except (OSError, subprocess.CalledProcessError):
        print "Calling inkscape failed, skipping splash screen update!"
