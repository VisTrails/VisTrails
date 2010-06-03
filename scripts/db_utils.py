############################################################################
##
## Copyright (C) 2006-2010 University of Utah. All rights reserved.
##
## This file is part of VisTrails.
##
## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of
## this file.  Please review the following to ensure GNU General Public
## Licensing requirements will be met:
## http://www.opensource.org/licenses/gpl-license.php
##
## If you are unsure which license is appropriate for your use (for
## instance, you are interested in developing a commercial derivative
## of VisTrails), please contact us at vistrails@sci.utah.edu.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################

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
