###########################################################
# Nightly Git Release to Sourceforge                      #
# Author: Daniel S. Rees                                  #
#                                                         #
# Description:                                            #
#     Creates and archives a tarball of a git             #
#     repository and uploads it to Sourceforge.           #
#     Intended for use as a cronjob / scheduled task.     #
#                                                         #
# Instructions:                                           #
#     Place this python script in a directory of its own. #
#     Edit the configuration as needed.  If changes to    #
#     a default git export are desired, modify the        #
#     last_minute_changes() function as needed.           #
#     Create a cronjob or scheduled task to run this      #
#     python script nightly (or on some other interval).  #
#                                                         #
# Requires 'git' and 'scp' to be installed and accessible #
# from a default environment (use Cygwin if on Windows).  #
###########################################################

import os
import shutil
import logging
import tarfile
import datetime
import traceback
import subprocess as proc
from StringIO import StringIO

####################
###### Config ######
####################

# URL of the git repository to export
GIT_URL = "git://www.vistrails.org/vistrails.git"

# Global arguments for calls to the git command
GIT_ARGS = ""

# Prefix of target git export dir (also used as prefix for log files)
EXPORT_DIR_PREFIX = "vistrails-src-nightly"

# Suffix of target git export dir (instances of '?' will be replaced with git revision)
EXPORT_DIR_SUFFIX = "-?"

# Paths of files and/or directories to be removed from the exported repository (relative to export dir)
EXPORT_DELETE_PATHS = [".git", ".gitignore", "scripts/dist", "contrib"]

# Distribution Tarball name (Do not add ".tar.gz")
TARBALL_NAME = "vistrails-src-nightly"

# Sourceforge User Name
SF_USERNAME = "CHANGEME"

# Sourceforge Project Name (unix name)
SF_PROJECT = "vistrails"

# Sourceforge target directory for upload (relative path from project root)
SF_DIRNAME = "vistrails/nightly"

# Path to private key for secure connection to Sourceforge (absolute path)
SF_PRIVKEY_PATH = "/path/to/private/key/CHANGEME"

# Flag determines if tarball is uploaded (Can be set manually here or conditionally in last_minute_changes())
SF_DO_UPLOAD = True

# Flag determines if tarball upload is forced - if True, overrides SF_DO_UPLOAD (don't set in last_minute_changes())
SF_FORCE_UPLOAD = False

# Number of upload attempts before giving up (Setting this to 0 guarantees that no upload will occur)
SF_UPLOAD_ATTEMPTS = 3

# Flag determines whether all nightly tarballs are archived, or only tarballs successfully uploaded to Sourceforge
ARCHIVE_UPLOADS_ONLY = True

# Timestamp format (used to name logs and archives)
TS_FORMAT = "%Y-%m-%d_%H-%M-%S"

# Directory in which log files are stored
LOG_DIR = "log"

# Directory in which tarball archives are stored
ARCHIVE_DIR = "archive"

# Indentation level for tracebacks and git export log in the logfile
INDENT = " "*12

#################################
###### Last Minute Changes ######
#################################

# Executed after export, but before unwanted path deletion, and before a tarball is created and uploaded.
# Any exceptions that occur in this function should be raised so the caller can exit gracefully.
# Example uses might include:
# - Changing a revision number in a specific file
# - Adding/renaming/moving a specific file
# - Copying/Moving a file to a different place from a directory scheduled for deletion
#
# Other available Globals:
#     - REVISION: int - Git revision number.
#     - TIMESTAMP: str - Timestamp of archival operation, formatted by TS_FORMAT
#     - DATETIME_START: datetime.datetime - Actual datetime object of timestamp
#     - EXPORT_DIRNAME: str - Revision tagged dir name with the exported files.

def last_minute_changes():
    global REVISION
    global TIMESTAMP
    global DATETIME_START
    global EXPORT_DIRNAME
    ######
    global EXPORT_DIR_PREFIX
    global GIT_URL
    global GIT_BASE_CMD
    global SF_DO_UPLOAD

    # Copy License
    srcfile = "scripts/dist/mac/Input/LICENSE"
    info("Copying '%s' to export base dir ..." % srcfile)
    try:
        shutil.copy(os.path.join(EXPORT_DIRNAME, srcfile), os.path.join(EXPORT_DIRNAME, os.path.basename(srcfile)))
    except:
        error("Couldn't copy '%s' to export base dir.")
        raise

    # Get Last Release Revision and Update Revision Number for nightly distro
    import re
    revision_filename = "vistrails/core/system/__init__.py"
    info("Updating revision number in '%s' ..." % revision_filename)
    last_revision = None
    f = None
    try:
        relpath = os.path.join(EXPORT_DIRNAME, revision_filename)
        f = open(relpath, "rb")
        data = f.read()
        pattern = re.compile(r"(^\s*?def vistrails_revision\(\):.*?release = ['\"])([a-fA-F0-9]+?)(['\"].*?return release)", re.DOTALL | re.MULTILINE)
        matchobj = pattern.search(data)
        if matchobj is None:
            raise Exception("Couldn't find revision number in '%s'." % revision_filename)
        last_revision = matchobj.group(2)
        (data, count) = pattern.subn(r"\g<1>" + REVISION[0:12] + r"\g<3>", data)
        if count != 1:
            raise Exception("Replaced revision number %s times in '%s' - should only replace 1." % (count, revision_filename))
        f.close()
        f = open(relpath, "wb")
        f.write(data)
    except:
        error("Couldn't change revision number in '%s'" % revision_filename)
        raise
    finally:
        if f is not None:
            f.close()

    # Write changelist with all revisions since last release
    info("Writing CHANGELIST for revisions (%s - %s] ..." % (last_revision, REVISION))
    f = None
    try:
        clist_filename = os.path.join(EXPORT_DIRNAME, "CHANGELIST")
        if REVISION != last_revision:
            f = open(clist_filename, "wb")
            full_line = '-'*70
            half_line = '-'*35
            git_changelist_args = '--stat --pretty=format:"' + full_line + '%n' + full_line + '%n%nRevision: %H%nDate:     %ad%n%n%s%n%n%b%n' + half_line + '%n%nSummary of changes:%n"'
            proc.call("%s log %s %s..%s" % (GIT_BASE_CMD, git_changelist_args, last_revision, REVISION), shell=True, stdout=f)
            f.write(full_line + '\n' + full_line + '\n')
        else:
            f = open(clist_filename, "wb")
            f.write("No changes since last release.")
        if not os.path.isfile(clist_filename):
            raise Exception("CHANGELIST file does not exist after write attempt.")
    except:
        error("Couldn't write CHANGELIST.")
        raise
    finally:
        if f is not None:
            f.close()

    # Don't upload if there were no changes made today
    if SF_DO_UPLOAD:
        try:
            data = proc.Popen('%s log --pretty=format:"%%ai" %s^..' % (GIT_BASE_CMD, REVISION), shell=True, stdout=proc.PIPE).communicate()[0]
            match = re.search(r"^([0-9]+-[0-9]+-[0-9]+) ", data)
            if match.group(1) != DATETIME_START.strftime("%Y-%m-%d"):
                info("No revisions made today - Disabling upload to Sourceforge ...")
                SF_DO_UPLOAD = False
            else:
                info("Revisions made today - Allowing upload to Sourceforge ...")
        except:
            error("Couldn't determine if new revisions were made today.")
            raise

############################################
###### Don't Modify Beyond This Point ######
############################################


#####################
###### Globals ######
#####################

# Starting datetime
DATETIME_START = datetime.datetime.now()  - datetime.timedelta(days=1)

# Timestamp for archival operation
TIMESTAMP = DATETIME_START.strftime(TS_FORMAT)

# Log file path
LOG_FILENAME = os.path.join(LOG_DIR, "%s_%s.log" % (EXPORT_DIR_PREFIX, TIMESTAMP))

# Log file object (initialized in main)
LOG_FILE = None

# Actual export directory name (revision gets appended)
EXPORT_DIRNAME = str(EXPORT_DIR_PREFIX)

# Tarball file name
TARBALL_FILENAME = TARBALL_NAME + ".tar.gz"

# Archived tarball file name
ARCHIVE_TARBALL_FILENAME = os.path.join(ARCHIVE_DIR, "%s_%s.tar.gz" % (TARBALL_NAME, TIMESTAMP))

# Git Revision Number (set in main)
REVISION = None

# Git Command with args (used as base for all git commands)
GIT_BASE_CMD = ("git --git-dir=%s/.git %s" % (EXPORT_DIRNAME, GIT_ARGS)).strip()

# Git export command
GIT_EXPORT_CMD = "%s clone -v --progress %s %s" % (GIT_BASE_CMD, GIT_URL, EXPORT_DIRNAME)

# Git revision command
GIT_REVISION_CMD = "%s rev-parse HEAD" % GIT_BASE_CMD

# Sourceforge upload command
SF_UPLOAD_CMD = "scp -v -i %s %s %s,%s@frs.sourceforge.net:/home/frs/project/%s/%s/%s/%s" % (
                    SF_PRIVKEY_PATH, TARBALL_FILENAME, SF_USERNAME, SF_PROJECT, SF_PROJECT[0],
                    SF_PROJECT[0:2], SF_PROJECT, SF_DIRNAME)

###################################################################################################################
###### Error Code Tuples (in case an automated build script wants a specific point-of-failure via exit code) ######
###################################################################################################################
# (exit_code: int, error_message: str)
ERROR_CREATE_DIRS            = ( 1, "Couldn't create log or archive directory.")
ERROR_CREATE_LOG             = ( 2, "Couldn't create log file.")
ERROR_CLEAN_DIRS             = ( 3, "Couldn't remove old export directories.")
ERROR_EXPORT_GIT             = ( 4, "Couldn't export git repository.")
ERROR_GET_REVISION           = ( 5, "Couldn't get revision number from git log.")
ERROR_RENAME_EXPORT_DIR      = ( 6, "Couldn't rename exported directory to include revision number.")
ERROR_DELETE_PATHS           = ( 7, "Couldn't remove '%s' from the git export directory.")
ERROR_LAST_MINUTE_CHANGES    = ( 8, "Failed while making user-defined last minute changes.")
ERROR_MAKE_TARBALL           = ( 9, "Couldn't make tarball.")
ERROR_CLEAN_EXPORT_DIR       = (10, "Couldn't remove export directory.")
ERROR_ARCHIVE_TARBALL        = (11, "Couldn't copy tarball to archive.")
ERROR_SF_UPLOAD              = (12, "Couldn't upload tarball to Sourceforge.")


def debug(msg):
    if os.path.isfile(LOG_FILENAME):
        logging.debug(msg)

def info(msg):
    if os.path.isfile(LOG_FILENAME):
        logging.info(msg)
    print "INFO: " + msg

def error(msg):
    if os.path.isfile(LOG_FILENAME):
        logging.error(msg)
    print "ERROR: " + msg

def errexit(errcodeobj, showtrace=True, *args):
    errcode = errcodeobj[0]
    errmsg = errcodeobj[1]
    if args:
        errmsg = errmsg % args
    if showtrace:
        errio = StringIO()
        errio.write(errmsg + "\n")
        traceio = StringIO()
        traceback.print_exc(file=traceio)
        traceio.seek(0)
        errio.writelines([INDENT + line for line in traceio.readlines()])
        errio.seek(0)
        errmsg = errio.read()
    error(errmsg)
    exit(errcode)


if __name__ == "__main__":
    info("Checking log and archive directories ...")
    try:
        if not os.path.isdir(LOG_DIR):
            info("Creating log directory: '%s' ..." % LOG_DIR)
            os.mkdir(LOG_DIR)
        if not os.path.isdir(ARCHIVE_DIR):
            info("Creating archive directory: '%s' ..." % ARCHIVE_DIR)
            os.mkdir(ARCHIVE_DIR)
    except:
        errexit(ERROR_CREATE_DIRS)

    info("Creating log file ...")
    try:
        logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)
    except:
        errexit(ERROR_CREATE_LOG)

    info("Cleaning up any existing export directories ...")
    try:
        cleanuplist = [fd for fd in os.listdir(".") if fd.startswith(EXPORT_DIRNAME) and os.path.isdir(fd)]
        for fd in cleanuplist:
            shutil.rmtree(fd)
    except:
        errexit(ERROR_CLEAN_DIRS)

    info("Exporting git repository ...")
    debug("Export Command: %s" % GIT_EXPORT_CMD)
    try:
        export_proc = proc.Popen(GIT_EXPORT_CMD, shell=True, stdout=proc.PIPE, stderr=proc.STDOUT)
        export_log = export_proc.communicate()[0]
        # Indent export log and write to logfile
        export_log = "\n".join([INDENT + line for line in export_log.splitlines()])
        debug("Git Export Log:\n%s" % export_log)
        if export_proc.returncode != 0:
            raise Exception("Git export failed with return code: %s" % export_proc.returncode)
    except:
        errexit(ERROR_EXPORT_GIT)

    info("Getting revision number ...")
    debug("Revision Command: %s" % GIT_REVISION_CMD)
    try:
        revision_proc = proc.Popen(GIT_REVISION_CMD, shell=True, stdout=proc.PIPE, stderr=proc.STDOUT)
        REVISION = (revision_proc.communicate()[0]).strip()
        if revision_proc.returncode != 0:
            raise Exception("Git revision number retrieval failed with return code: %s" % revision_proc.returncode)
        sha1chars = ['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f','A','B','C','D','E','F']
        if (not REVISION) or (len(REVISION) != 40) or (sum([REVISION.count(c) for c in sha1chars]) != 40):
            raise Exception("Git revision number wasn't a valid sha-1 hash: %s" % REVISION)
    except:
        errexit(ERROR_GET_REVISION)

    info("Tagging export dir with revision suffix: '%s' ..." % EXPORT_DIR_SUFFIX.replace("?", REVISION[0:12]))
    try:
        new_export_dirname = EXPORT_DIRNAME + EXPORT_DIR_SUFFIX.replace("?", REVISION[0:12])
        os.rename(EXPORT_DIRNAME, new_export_dirname)
        EXPORT_DIRNAME = new_export_dirname
        # Update git base cmd to point to renamed dir (in case it is needed in last_minute_changes())
        GIT_BASE_CMD = ("git --git-dir=%s/.git %s" % (EXPORT_DIRNAME, GIT_ARGS)).strip()
    except:
        errexit(ERROR_RENAME_EXPORT_DIR)

    info("Making user-defined last minute changes ...")
    try:
        last_minute_changes()
    except:
        errexit(ERROR_LAST_MINUTE_CHANGES)
    info("Finished making user-defined last minute changes.")

    # Remove unwanted paths from export dir
    try:
        for path in EXPORT_DELETE_PATHS:
            relpath = os.path.join(EXPORT_DIRNAME, path)
            if os.path.exists(relpath):
                info("Removing '%s' from export directory ..." % path)
                if os.path.isdir(relpath):
                    shutil.rmtree(relpath)
                else:
                    os.remove(relpath)
            else:
                info("Could not remove '%s' from export directory because it does not exist ..." % path)
    except:
        errexit(ERROR_DELETE_PATHS, True, path)

    info("Creating tarball: '%s' ..." % TARBALL_FILENAME)
    tarball = None
    try:
        tarball = tarfile.open(TARBALL_FILENAME, "w:gz")
        tarball.add(EXPORT_DIRNAME)
    except:
        errexit(ERROR_MAKE_TARBALL)
    finally:
        if tarball is not None:
            tarball.close()

    info("Removing export directory: '%s' ..." % EXPORT_DIRNAME)
    try:
        shutil.rmtree(EXPORT_DIRNAME)
    except:
        errexit(ERROR_CLEAN_EXPORT_DIR)

    info("Archiving tarball to: '%s' ..." % ARCHIVE_TARBALL_FILENAME)
    try:
        shutil.copy(TARBALL_FILENAME, ARCHIVE_TARBALL_FILENAME)
    except:
        errexit(ERROR_ARCHIVE_TARBALL)

    # Upload to sourceforge
    uploaded = False
    if (SF_DO_UPLOAD or SF_FORCE_UPLOAD) and SF_UPLOAD_ATTEMPTS > 0:
        upload_attempts = 0
        while not uploaded and upload_attempts < SF_UPLOAD_ATTEMPTS:
            upload_attempts += 1
            info("Uploading tarball to Sourceforge (attempt %d of %d): '%s' ..." % (upload_attempts, SF_UPLOAD_ATTEMPTS, SF_UPLOAD_CMD))
            try:
                upload_proc = proc.Popen(SF_UPLOAD_CMD, shell=True, stdout=proc.PIPE, stderr=proc.STDOUT)
                upload_log = upload_proc.communicate()[0]
                # Indent upload log and write to logfile
                upload_log = "\n".join([INDENT + line for line in upload_log.splitlines()])
                debug("Sourceforge Upload Log (attempt %d of %d):\n%s" % (upload_attempts, SF_UPLOAD_ATTEMPTS, upload_log))
                if upload_proc.returncode != 0:
                    raise Exception("Tarball upload (attempt %d of %d) failed with return code: %s" % (upload_attempts, SF_UPLOAD_ATTEMPTS, upload_proc.returncode))
                else:
                    info("Tarball upload completed on attempt %d of %d." % (upload_attempts, SF_UPLOAD_ATTEMPTS))
                    uploaded = True
            except Exception, e:
                if upload_attempts == SF_UPLOAD_ATTEMPTS:
                    errexit(ERROR_SF_UPLOAD)
                else:
                    info(e.args[0])
            finally:
                if upload_attempts == SF_UPLOAD_ATTEMPTS and ARCHIVE_UPLOADS_ONLY and not uploaded:
                    info("Only archiving uploads and upload failed.  Removing archived tarball ...")
                    if os.path.isfile(ARCHIVE_TARBALL_FILENAME):
                        os.remove(ARCHIVE_TARBALL_FILENAME)
    else:
        info("Skipping tarball upload to Sourceforge ...")
        if ARCHIVE_UPLOADS_ONLY:
            info("Only archiving uploads and upload was skipped.  Removing archived tarball ...")
            if os.path.isfile(ARCHIVE_TARBALL_FILENAME):
                os.remove(ARCHIVE_TARBALL_FILENAME)

    # Display total time
    info("Completed Nightly Build in %s second(s)." % (datetime.datetime.now() - DATETIME_START).seconds)
