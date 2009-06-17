#!/usr/bin/env python

# THIS IS NOT FINISHED

import pysvn

def userpass(realm, username, may_save):
    username = 'your username'
    password = 'your password'
    return True, username, password, False

################################################################################

client = pysvn.Client()
client.callback_get_login = userpass

logs = client.log('https://vistrails.sci.utah.edu/svn/trunk',
                  revision_end=pysvn.Revision(pysvn.opt_revision_kind.number, 1520))

for log in logs:
    for k, v in log.iteritems():
        print "<<Key: %s>>" % k
        print "<<Value: %s>>" % v
    print "-=-=-=-=-=-=-=-=-=-"


