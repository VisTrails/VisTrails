#!/usr/bin/env python
# Updates the binary changelogs, version numbers, hash, and branch from CHANGELOG
# Run and commit changes to git before building release
import re
import subprocess
import sys

CHANGELOG="../../CHANGELOG"

CHANGELOG_FILES=["../mac/Input/README",
                 "../windows/Input/releaseNotes.txt"]

re_base = r'(?<=%s)([0-9a-zA-Z._+-]+)'

# [filename, preceding string]
VERSION_FILES = [
   ["../../scripts/create_release_wiki_table.py", r'VT_VERSION = [\'"]'],
   ["../../scripts/create_release_wiki_table.py", r'SF_FOLDER_NAME = [\'"]v'], # a second pass
   ["../../vistrails/core/system/__init__.py", r'VERSION = [\'"]'],
   ["../mac/setup.py", r'VERSION = [\'"]'],
   ["../windows/vistrails.iss", r'AppVerName=VisTrails '],
   ["../windows/vistrailsx64.iss", r'AppVerName=VisTrails x64 '],
   ["../windows/custom/vistrails-gdal.iss", r'AppVerName=VisTrails '],
   ["../windows/custom/vistrailsx64-gdal.iss", r'AppVerName=VisTrails x64 '],
   ["../source/make-vistrails-src-release.py", r'VT_VERSION = [\'"]'],
   ["../../doc/usersguide/conf.py", r'release = [\'"]']]

HASH_FILES = [["../../scripts/create_release_wiki_table.py", r'VT_REVISION = [\'"]'],
              ["../../vistrails/core/system/__init__.py", r'RELEASE = [\'"]'],
              ["../source/make-vistrails-src-release.py", r'VT_HASH = [\'"]']]

BRANCH_FILES = [
   ["../source/make-vistrails-src-release.py", r'VT_BRANCH = [\'"]v'],
   ["../../doc/usersguide/conf.py", r'version = [\'"]']]

def update_value(fname, pre, value):
    """
    fname: file name
    rexp: regular expression to search for
    value: new value

    """
    rexp = re.compile(re_base % pre)


    with open(fname, 'rb') as fp:
        lines = fp.readlines()

    i = 0
    replaced = False
    while i < len(lines):
        line = lines[i]
        m = rexp.search(line)
        if m is not None:
            lines[i] = rexp.sub(value, line)
            print fname, '---', lines[i],
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
    # Read CHANGELOG
    with open(CHANGELOG, 'rb') as fp:
        lines = fp.readlines()

    # copy changelog to win and mac binary
    for fname in CHANGELOG_FILES:
        with open(fname, 'wb') as fp:
            for line in lines:
                fp.write(line)

    # Get info from CHANGELOG
    # Assume 3:rd line and non-changing format
    line = lines[2].split()
    VERSION = line[2][1:] # Drop "v" prefix
    HASH = line[4]
    BRANCH = line[6][1:] # Drop "v" prefix
    print "Updating to:", VERSION, HASH, "on branch v%s" % BRANCH

    for fname, pre in VERSION_FILES:
       update_value(fname, pre, VERSION)

    for fname, pre in HASH_FILES:
       update_value(fname, pre, HASH)

    for fname, pre in BRANCH_FILES:
       update_value(fname, pre, BRANCH)

    # TODO: Update splash
