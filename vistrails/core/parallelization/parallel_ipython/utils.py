import re
import sys


_ansi_code = re.compile(r'%s(?:(?:\[[^A-Za-z]*[A-Za-z])|[^\[])' % '\x1B')

def strip_ansi_codes(s):
    return _ansi_code.sub('', s)


def print_remoteerror(e):
    sys.stderr.write("Got exception from IPython engine:\n")
    sys.stderr.write("%s: %s\n" % (e.ename, e.evalue))
    sys.stderr.write("Traceback:\n%s\n" % strip_ansi_codes(e.traceback))
