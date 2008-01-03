#!/usr/bin/env python
import sys
import re

re_list = []

if len(sys.argv) < 4:
    print "Usage:"
    print "%s file_to_process path_to_data_files data_file_1 data_file_2 ..." % sys.argv[0]
    sys.exit(1)

for i in xrange(3, len(sys.argv)):
    re_list.append((sys.argv[i], re.compile(r"val='[^']*" + sys.argv[i] + r"[^']*'")))

f = file(sys.argv[1])
for l in f:
    for (s, re_obj) in re_list:
        l = re_obj.sub("val='" + sys.argv[2] + s + "'", l)
    print l[:-1]
