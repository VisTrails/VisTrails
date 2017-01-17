#!/usr/bin/env python
###########################################################
# Builds Source Release and uploads to Sourceforge        #
# Author: Daniel S. Rees (Modified by Tommy Ellqvist)     #
#                                                         #
# Description:                                            #
#     Creates and archives a tarball of a git             #
#     repository and uploads it to Sourceforge.           #
#     Intended for use as a scheduled task or             #
#     run by a buildbot.                                  #
#                                                         #
# Instructions:                                           #
#     Check out a clean version from git, then run        #
#     dist/common/prepare_release.py to update hash.      #
#     Running this script will create a tarball in the    #
#     root directory with the files in EXPORT_PATHS.      #
#     Specify sourceforge username and path to private    #
#     key to upload to sourceforge.                       #
#                                                         #
# Requires 'scp' to be installed and accessible from a    #
# default environment (use Cygwin if on Windows).         #
###########################################################

import os
import sys
import tarfile
import subprocess

####################
###### Config ######
####################

# Paths of files and/or directories to be included in the exported repository (relative to export dir)
EXPORT_PATHS = "vistrails doc examples extensions scripts CHANGELOG LICENSE".split()

# VisTrails Release Version
VT_VERSION = '2.x'

# Branch to be used to build release
VT_BRANCH = 'master'

# Hash used in the release
VT_HASH = '0fddb5bfe72c'

# Distribution Tarball name (Do not add ".tar.gz")
#TARBALL_NAME = "vistrails-src-%s-%s" % (VT_VERSION, VT_HASH)
TARBALL_NAME = "vistrails-src"

# Tarball file name
TARBALL_FILENAME = TARBALL_NAME + ".tar.gz"

# Flag determines if tarball is uploaded (Can be set manually here or conditionally in last_minute_changes())
SF_DO_UPLOAD = False

# Sourceforge User Name
SF_USERNAME = "CHANGEME"

# Sourceforge Project Name (unix name)
SF_PROJECT = "vistrails"

# Sourceforge target directory for upload (relative path from project root)
SF_DIRNAME = "vistrails/v%s"%VT_VERSION

# Path to private key for secure connection to Sourceforge (absolute path)
SF_PRIVKEY_PATH = "/path/to/private/key/CHANGEME"

# Number of upload attempts before giving up (Setting this to 0 guarantees that no upload will occur)
SF_UPLOAD_ATTEMPTS = 3

# Directory in which tarball archives are stored
ARCHIVE_DIR = "archive"


#########################################
###### Read command-line arguments ######
#########################################

# If called with 2 arguments, get [sf_username, sf_privkey_path] and upload so sourceforge
if len(sys.argv)==3:
    SF_DO_UPLOAD = True
    SF_USERNAME = sys.argv[1]
    SF_PRIVKEY_PATH = sys.argv[2]

    TARBALL_NAME = "vistrails-src-nightly"
    TARBALL_FILENAME = TARBALL_NAME + ".tar.gz"
    SF_DIRNAME = "vistrails/nightly"

#####################
###### Globals ######
#####################

# Sourceforge upload command
SF_UPLOAD_CMD = "scp -v -i %s %s %s,%s@frs.sourceforge.net:/home/frs/project/%s/%s/%s/%s" % (
                    SF_PRIVKEY_PATH, TARBALL_FILENAME, SF_USERNAME, SF_PROJECT, SF_PROJECT[0],
                    SF_PROJECT[0:2], SF_PROJECT, SF_DIRNAME)

if __name__ == "__main__":
    os.chdir(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

    # prepare release
    proc = subprocess.Popen(['scripts/dist/common/prepare_release.py'],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    proc.wait()
    if proc.returncode != 0:
        print "ERROR: preparing release."
        if proc.stdout:
            print proc.stdout.readlines()
        sys.exit(1)

    print "Creating tarball: '%s' ..." % TARBALL_FILENAME
    tarball = None
    try:
        tarball = tarfile.open(TARBALL_FILENAME, "w:gz")
        ignore = [os.path.join('scripts', 'dist'),
                  os.path.join('doc', 'dist')]

        def filter_(member):
            if any(member.name.startswith(ignored) for ignored in ignore):
                return None
            return member

        for fname in EXPORT_PATHS:
            tarball.add(fname, filter=filter_)
    except:
        print "ERROR: Failed to create tarball"
        raise
    finally:
        if tarball is not None:
            tarball.close()

    if SF_DO_UPLOAD and SF_UPLOAD_ATTEMPTS > 0:
        # Upload to sourceforge
        uploaded = False
        upload_attempts = 0
        while not uploaded and upload_attempts < SF_UPLOAD_ATTEMPTS:
            upload_attempts += 1
            print "Uploading tarball to Sourceforge (attempt %d of %d): '%s' ..." % (upload_attempts, SF_UPLOAD_ATTEMPTS, SF_UPLOAD_CMD)
            try:
                upload_proc = subprocess.Popen(SF_UPLOAD_CMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                upload_log = upload_proc.communicate()[0]
                # Indent upload log and print
                upload_log = "\n".join(['    ' + line for line in upload_log.splitlines()])
                print "Sourceforge Upload Log (attempt %d of %d):\n%s" % (upload_attempts, SF_UPLOAD_ATTEMPTS, upload_log)
                if upload_proc.returncode != 0:
                    raise Exception("Tarball upload (attempt %d of %d) failed with return code: %s" % (upload_attempts, SF_UPLOAD_ATTEMPTS, upload_proc.returncode))
                else:
                    print "Tarball upload completed on attempt %d of %d." % (upload_attempts, SF_UPLOAD_ATTEMPTS)
                    uploaded = True
            except Exception, e:
                if upload_attempts == SF_UPLOAD_ATTEMPTS:
                    print "ERROR: Could not upload to sourceforge"
                else:
                    print e.args[0]
        print "tarball uploaded to Sourceforge, deleting local tarball"
        if os.path.isfile(TARBALL_FILENAME):
            os.remove(TARBALL_FILENAME)

    print "Completed Source Build"
