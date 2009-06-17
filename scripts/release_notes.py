#!/usr/bin/env python

import pysvn
import getpass
import sys
import re

username = None
password = None

def userpass(realm, u, may_save):
    global username
    global password
    if not username:
        print "Username:",
        sys.stdout.flush()
        username = raw_input()
        password = getpass.getpass()
    return True, username, password, False

################################################################################

def rev(n):
    return pysvn.Revision(pysvn.opt_revision_kind.number, n)

client = pysvn.Client()
client.callback_get_login = userpass

version_start = 1530
version_end = 1537

logs = client.log('https://vistrails.sci.utah.edu/svn',
                  revision_end=rev(1520))

##############################################################################

def release_changed(path):
    if path.startswith('trunk/vistrails'):
        return 'trunk'
    elif path.startswith('branches/v1.2'):
        return '1.2'
    elif path.startswith('branches/v1.3'):
        return '1.3'
    else:
        return 'other'

def print_changes(release):
    if release not in release_changes:
        return
    print "Changes in '%s': " % release
    for (v, log, diff_summaries) in release_changes[release]:
        print "version %s:" % v
        print "  Affected files:"
        for summary in diff_summaries:
            if release_changed(summary.path) == release:
                print "    %s - %s" % (str(summary.summarize_kind)[0].upper(),
                                       summary.path)

re_ticket = re.compile(r'<ticket>(.*)</ticket>')
re_bugfix = re.compile(r'<bugfix>(.*)</bugfix>')
def get_ticket_closes(release):
    if release not in release_changes:
        return
    print "Ticket closes in '%s': " % release
    for (v, log, diff_summaries) in release_changes[release]:
        s = re_ticket.search(log.message)
        if s:
            print "revision %s closed ticket %s" % (v, s.groups()[0])

def get_bugfixes(release):
    if release not in release_changes:
        return
    print "Bugfixes in '%s': " % release
    for (v, log, diff_summaries) in release_changes[release]:
        s = re_bugfix.search(log.message)
        if s:
            print " - %s (r%s)" % (s.groups()[0], v)
    
#             print "  Affected files:"
#             for summary in diff_summaries:
#                 if release_changed(summary.path) == release:
#                     print "    %s - %s" % (str(summary.summarize_kind)[0].upper(),
#                                            summary.path)

################################################################################
# collect all changes

change_sets = []

for version in xrange(version_start, version_end):
    ds = client.diff_summarize('https://vistrails.sci.utah.edu/svn',
                               rev(version),
                               'https://vistrails.sci.utah.edu/svn',
                               rev(version+1))
    log = client.log('https://vistrails.sci.utah.edu/svn',
                     rev(version),
                     rev(version))[0]
    change_sets.append((version, log, ds))
    print version, "/", version_end

release_changes = {}

for (v, log, diff_summaries) in change_sets:
    which_releases = set()
    for diff in diff_summaries:
        which = release_changed(diff.path)
        which_releases.add(which)
    for which in which_releases:
        release_changes.setdefault(which, []).append((v, log, diff_summaries))

# print_changes('trunk')
get_ticket_closes('trunk')
get_bugfixes('trunk')


