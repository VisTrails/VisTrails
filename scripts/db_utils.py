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

import getopt
import getpass
import sys

def usage(usageDict):
    usageStr = ''
    unrequired = ''
    required = ''
    align_len = 15
    for (opt, info) in usageDict.iteritems():
        if info[1]:
            required += '-%s <%s> ' % (opt[0], info[2])
            usageStr += '    -%s <%s> %s' % (opt[0], info[2], 
                                             ' ' * (align_len - 
                                                    len(info[2]) - 3))
        else:
            if len(opt) > 1:
                unrequired += '[-%s <%s>] ' % (opt[0], info[2])
                usageStr += '    -%s <%s> %s' % (opt[0], info[2], 
                                                 ' ' * (align_len - 
                                                        len(info[2]) - 3))
            else:
                unrequired += '[-%s] ' % opt[0]
                usageStr += '    -%s %s' % (opt[0], ' ' * align_len)
        usageStr += '%s\n' % info[0]
    print 'Usage: %s %s %s%s\n%s' % (sys.executable,
                                     sys.argv[0],
                                     required, 
                                     unrequired, 
                                     usageStr)

def parse_db_cmd_line(argv, more_options={}):
    options = {}
    optionsUsage = {'h:': ('set database host/port', False, 'host:port'),
                    'p': ('use password', False),
                    'u:': ('set database user', False, 'user'),
                    'D:': ('set database name', False, 'database'),
                    }
    optionsUsage.update(more_options)

    optStr = ''.join(optionsUsage.keys())
    optKeys = optStr.replace(':','')
    for idx in xrange(len(optKeys)):
        options[optKeys[idx]] = False

    try:
	(optlist, args) = getopt.getopt(argv[1:], optStr)
	for opt in optlist:
            if opt[1] is not None and opt[1] != '':
                options[opt[0][1:]] = opt[1]
            else:
                options[opt[0][1:]] = True
    except getopt.GetoptError:
        usage(optionsUsage)
        sys.exit(23)

    for opt, spec in optionsUsage.iteritems():
        if spec[1] and not options[opt[0]]:
            usage(optionsUsage)
            sys.exit(23)
        
    config = {'host': 'localhost',
              'port': 3306,
              'user': 'vistrails',
              'db': 'vistrails'}

    if options['p']:
        config['passwd'] = getpass.getpass()
    if options['h']:
        host_arr = options['h'].split(':', 1)
        config['host'] = host_arr[0]
        if len(host_arr) > 1:
            config['port'] = int(host_arr[1])
    if options['u']:
        config['user'] = options['u']
    if options['D']:
        config['db'] = options['D']

    return (config, options)
