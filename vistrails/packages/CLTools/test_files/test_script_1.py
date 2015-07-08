# pragma: no testimport

from __future__ import division

import sys


if __name__ == '__main__':
    args = sys.argv[1:]

    if len(args) != 10:
        sys.stderr.write("Wrong number of parameters\n")
        sys.exit(1)

    fin = args.pop(0)
    fout = args.pop(0)

    if args != ['-t', '42', '-l', 'a', '-l', 'b', '-l', 'c']:
        sys.stderr.write("Wrong parameters\n")
        sys.exit(1)

    stdin = sys.stdin.readline()
    if stdin != 'some line\n':
        sys.stderr.write("Wrong line on stdin\n")
        sys.exit(1)

    if not fin.endswith('.cltest'):
        sys.stderr.write("Wrong extension for f_in '%s'\n" % fin)
        sys.exit(1)

    with open(fin, 'r') as fpin:
        fcin = fpin.read()
    if fcin != 'this is a\ntest':
        sys.stderr.write("Wrong content in f_in '%s'\n" % fin)
        sys.exit(1)

    if not fout.endswith('.cltest'):
        sys.stderr.write("Wrong extension for f_out '%s'\n" % fout)
        sys.exit(1)

    with open(fout, 'wb') as fpout:
        fpout.write('ok\nmessage received')

    sys.stdout.write("program output here")

    sys.exit(0)
