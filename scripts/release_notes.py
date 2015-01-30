#!/usr/bin/env python
###############################################################################
##
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
"""This will write text of a release notes file based on commit messages and trac
tickets. Use the configuration section below to tune the start and end commits.
The text will be written to the standard output.
"""

import xmlrpclib
import git
import getpass
import os
import sys
import re
import tempfile
import subprocess
import shutil

#### configuration ####
commit_start = "269e4808eca3" # hash of version used on last release notes
commit_end = "HEAD" # current hash
branch = "v2.1" # git branch to be used
release_name = "2.1.4"
clonepath = None    # set this to the complete path of a vistrails clone to be
                    # used
                    # if None, the remote repository will be cloned to a
                    # temporary folder and removed at the end of the script
#clonepath = '/Users/tommy/git/vistrails'
cloneremote = 'git://www.vistrails.org/vistrails.git'
#### end configuration #####

## The script will ask for your Trac user and password
## so no need to change this now
username = None
password = None
need_cleanup = False

################################################################################
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

def clone_vistrails_git_repository(path_to):
    global cloneremote
    cmdlist = ['git', 'clone', cloneremote,
               path_to]
    print "Cloning vistrails from:"
    print "  %s to"%cloneremote
    print "  %s"%path_to
    print "Be patient. This may take a while."
    process = subprocess.Popen(cmdlist, shell=False,
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
    process.wait()
    if process.returncode == 0:
        print "repository is cloned."
    return process.returncode

################################################################################

def init_repo():
    global clonepath, need_cleanup, branch
    ok = False
    if clonepath is None:
        clonepath = tempfile.mkdtemp(prefix="vtrel")
        try:
            if clone_vistrails_git_repository(clonepath) == 0:
                ok = True
                init_branch(clonepath,branch)
            need_cleanup = True
        except Exception, e:
            print "ERROR: Could not clone vistrails repository!"
            print str(e)
            shutil.rmtree(clonepath)
            sys.exit(1)
    else:
        init_branch(clonepath,branch)
        pull_changes(clonepath)
        ok = True
    if ok:
        repo = git.Repo(clonepath)
        return repo
    else:
        print "ERROR: git clone failed."
        sys.exit(1)

################################################################################

def cleanup_repo():
    global clonepath, need_cleanup
    if need_cleanup:
        shutil.rmtree(clonepath)
        
################################################################################

def init_branch(path_to, branch):
    cmdlist = ['git', 'checkout', "%s"%branch]
    print "Checking out %s branch..."%branch
    current_dir = os.getcwd()
    os.chdir(path_to)
    process = subprocess.Popen(cmdlist, shell=False,
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
    process.wait()
    lines = process.stdout.readlines()
    for line in lines:
        print "   ", line
    if process.returncode == 0:
        print "Branch %s was checked out."%branch
    os.chdir(current_dir)    
    return process.returncode

################################################################################

def pull_changes(path_to):
    cmdlist = ['git', 'pull']
    print "Pulling changes into the branch..."
    current_dir = os.getcwd()
    os.chdir(path_to)
    process = subprocess.Popen(cmdlist, shell=False,
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
    process.wait()
    lines = process.stdout.readlines()
    for line in lines:
        print "   ", line
    if process.returncode == 0:
        print "Changes were pulled."
    os.chdir(current_dir)    
    return process.returncode

################################################################################

def checkout_branch(repo, branch):
    repobranch = getattr(repo.heads, branch)
    repobranch.checkout()

##############################################################################

def build_release_notes(repo, branch):
    global username
    global password
    global commit_start, commit_end
    
    def check_inside_skip(skip_list, message):
        found = False
        for s in skip_list:
            if s.find(message) != -1:
                found = True
                break
        return found
    
    re_ticket_old = re.compile(r'<ticket>(.*?)</ticket>', re.M | re.S)
    re_ticket = re.compile(r'^Ticket: (.*?)$', re.M | re.S)
    re_ticket2 = re.compile(r'^Fixes: (.*?)$', re.M | re.S)
    re_bugfix_old = re.compile(r'<bugfix>(.*?)</bugfix>', re.M | re.S)
    re_bugfix = re.compile(r'^Bugfix: (.*?)$', re.M | re.S)
    re_feature_old = re.compile(r'<feature>(.*?)</feature>', re.M | re.S)
    re_feature = re.compile(r'^Feature:(.*?)$', re.M | re.S)
    re_skip = re.compile(r'<skip>(.*?)</skip>', re.M | re.S)

    #build list and dictionary with commits
    logs = []
    log_map_time = {}
    checkout_branch(repo,branch)
    for c in repo.iter_commits("%s..%s"%(commit_start,commit_end)):
        logs.append(c)
        log_map_time[c.hexsha] = c.committed_date
        
    #populate dictionaries
    bugfixes = {}
    tickets = {}
    features = {}
    changes = {}
    ticket_info = {}
    
    for log in logs:
        ls = re_skip.findall(log.message)
        lf = re_feature.findall(log.message)
        lf.extend(re_feature_old.findall(log.message))
        lt = re_ticket.findall(log.message)
        lt.extend(re_ticket2.findall(log.message))
        lt.extend(re_ticket_old.findall(log.message))
        lb = re_bugfix.findall(log.message)
        lb.extend(re_bugfix_old.findall(log.message))
        for s in ls:
            changes[s.strip()] = log.hexsha
        for f in lf:
            features[f.strip()] = log.hexsha
        for t in lt:
            # handle tickets with # (should not be used)
            t = t.strip()
            if t.startswith('#'):
                t = t[1:]
            try:
                tickets[int(t)] = log.hexsha
            except ValueError:
                pass
        for b in lb:
            bugfixes[b.strip()] = log.hexsha
        if len(ls) == 0 and len(lf) == 0 and len(lt) == 0 and len(lb) == 0:
            changes[log.message] = log.hexsha
                

    #get ticket summaries from xmlrpc plugin installed on vistrails trac
    print "Will connect to VisTrails Trac with authentication..."
    if not username:
        print "Username:",
        sys.stdout.flush()
        username = raw_input()
        password = getpass.getpass()

    url = "https://%s:%s@www.vistrails.org/login/xmlrpc"%(username,
                                                               password)
    server = xmlrpclib.ServerProxy(url)
    print "downloading tickets.",
    for (tid,r) in tickets.items():
        print ".",
        sys.stdout.flush()
        try:
            ticket_info[tid] = server.ticket.get(tid)
        except Exception, e:
            del tickets[tid]
            print "commit %s: Could not get info for ticket %s"%(r,tid)
    print "done."

    #place tickets on bugfixes or enhancements
    for (tid,r) in tickets.iteritems():
        txt = "Ticket %s: %s"%(tid,ticket_info[tid][3]['summary'])
        if ticket_info[tid][3]['type'] == 'enhancement':
            features[txt] = r
        elif ticket_info[tid][3]['type'] in ['defect', 'defect+question']:
            bugfixes[txt] = r
        else:
            #put the rest as changes
            changes[txt] = r
    if commit_end == "HEAD" and len(logs) > 0:
        commit_end = logs[0].hexsha

    print
    print
    print "Release Name: v%s build %s from %s branch" % (release_name,
                                                         commit_end[0:12],
                                                         branch)
    print 
    print "Enhancements: "
    times = []
    for t, r in features.iteritems():
        times.append((log_map_time[r], t))
    revisions = sorted(times)
    revisions.reverse()
    for (t,text) in revisions:
        r = features[text]
        print " - %s (%s)" %(text,r[0:12])
    
    print
    print "Bug fixes: "
    times = []
    for t, r in bugfixes.iteritems():
        times.append((log_map_time[r], t))
    revisions = sorted(times)
    revisions.reverse()
    for (t,text) in revisions:
        r = bugfixes[text]
        print " - %s (%s)" %(text,r[0:12])

    print
    print "Other changes: "
    times = []
    for t, r in changes.iteritems():
        times.append((log_map_time[r], t))
    revisions = sorted(times)
    revisions.reverse()
    for (t,text) in revisions:
        r = changes[text]
        print " - %s (%s)" %(text.split('\n')[0][0:100],r[0:12])

if __name__ == "__main__":
    repo = init_repo()
    build_release_notes(repo, branch)
    cleanup_repo()


