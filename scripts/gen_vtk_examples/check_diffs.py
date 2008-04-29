############################################################################
##
## Copyright (C) 2006-2007 University of Utah. All rights reserved.
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

if __name__ == '__main__':
    import sys
    import os
    import re

    def collectFilenames(dir):
        # create the regular expression matcher machines
        fileNameParser = re.compile('.*\.py')

        result = []
        for file in os.listdir(dir):
            # print childDirOrFile
            childDirOrFile = os.path.join(dir,file)
            if os.path.isfile(childDirOrFile):
                # file does match?
                if fileNameParser.match(childDirOrFile):
                    result.append(childDirOrFile)
            elif os.path.isdir(childDirOrFile):
                result += collectFilenames(childDirOrFile)
        return result

    if len(sys.argv) < 3:
        print 'Usage: %s <in_directory> <out_directory>' % sys.argv[0]
    
    all_files = collectFilenames(sys.argv[1])

    in_base = os.path.basename(sys.argv[1])
    out_base = os.path.basename(sys.argv[2])
    for fname in all_files:
        path_before = os.path.dirname(fname)
        path_end = os.path.basename(fname)
        while os.path.basename(path_before) != in_base:
            path_end = os.path.join(os.path.basename(path_before), path_end)
            path_before = os.path.dirname(path_before)
        other_fname = os.path.join(sys.argv[2], path_end)

        cmd_line = "diff %s %s" % (fname, other_fname)
        print cmd_line
        os.system(cmd_line)
