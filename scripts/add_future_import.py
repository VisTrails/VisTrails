#!/usr/bin/env python
from __future__ import absolute_import, unicode_literals

import argparse
import logging
import re
from rpaths import Path
import sys


def to_bytes(s):
    if isinstance(s, bytes):
        return s
    else:
        return s.encode('ascii')


FUTURES = set([b'absolute_import', b'division', b'print_function',
               b'unicode_literals'])


def make_import_statement(imports):
    statement = b'from __future__ import '
    for i, feature in enumerate(imports):
        notfirst = 2 if i != 0 else 0
        notlast = 4 if i != len(imports) - 1 else 0

        if len(statement) + notfirst + len(feature) + notlast <= 79:
            statement += (b', ' if notfirst else b'') + feature
        else:
            statement += (b', ' if notfirst else b'') + b'\\\n' + feature
    return statement + b'\n'


re_whitespace = re.compile(br'^\s*$')
re_comment = re.compile(br'^\s*#')
re_import = re.compile(br'^\s*from\s+__future__\s+import(\s.+)$')


def process_file(filename, enable):
    logging.debug("Processing %s..." % filename)
    with filename.open('rb') as fp:
        lines = fp.readlines()

    # Look for an import statement to check or fix
    i = 0
    nb = 0
    done = False
    while i < len(lines):
        nb += 1
        line = lines[i]

        # Merges lines on ending backslash
        if line.rstrip(b'\r\n').endswith(b'\\'):
            line += lines.pop(i+1)
            lines[i] = line

        f_import = re_import.match(line)
        if f_import is not None:
            imports = f_import.group(1).strip(b' \t\r\n()').split(b',')
            imports = [feature.strip() for feature in imports]
            missing = enable - set(imports)
            if not missing:
                logging.debug("Found needed imports (line %d)" % nb)
                done = True
            else:
                logging.debug("Enabling imports: %s (line %d)" % (
                              ', '.join(missing),
                              nb))
                imports = sorted(set(imports) | enable)
                line = make_import_statement(imports)
                lines[i] = line
                done = True
                break

        i += 1

    # Didn't find a statement, must add one
    # Where? Before first non-comment and non-docstring line
    if not done:
        i = 0
        docstring_seen = False
        while i < len(lines):
            line = lines[i]
            if re_whitespace.match(line):
                pass
            elif re_comment.match(line):
                pass
            elif not docstring_seen and '"""' in line:
                if line.count('"""') == 1:
                    i += 1
                    while '"""' not in lines[i]:
                        i += 1
                docstring_seen = True
            elif not docstring_seen and "'''" in line:
                if line.count("'''") == 1:
                    i += 1
                    while "'''" not in lines[i]:
                        i += 1
                docstring_seen = True
            else:
                # Code here! Insert before
                logging.debug("Inserting imports (line %d)" % (i + 1))
                lines.insert(i, make_import_statement(enable) + b'\n')
                break
            i += 1

    with filename.open('wb') as fp:
        fp.writelines(lines)


def main():
    parser = argparse.ArgumentParser(
            description="Adds __future__ imports to Python files")
    parser.add_argument('-v', '--verbose', action='count', dest='verbosity',
                        default=1)
    parser.add_argument('-e', '--enable', action='append',
                        help="Future import to enable")
    parser.add_argument('file',
                        nargs=argparse.ONE_OR_MORE,
                        help="File or directory in which to replace")
    args = parser.parse_args()
    levels = [logging.CRITICAL, logging.WARNING, logging.INFO, logging.DEBUG]
    logging.basicConfig(level=levels[args.verbosity])

    if not args.enable:
        logging.critical("Nothing to do")
        sys.exit(1)

    enable = set(to_bytes(feature) for feature in args.enable)
    unrecognized = enable - FUTURES
    if unrecognized:
        logging.critical("Error: unknown futures %s" % ', '.join(unrecognized))
        sys.exit(1)

    for target in args.file:
        target = Path(target)
        if target.is_file():
            if not target.name.endswith('.py'):
                logging.warning("File %s doesn't end with .py, processing "
                                "anyway..." % target)
            process_file(target, enable)
        elif target.is_dir():
            logging.info("Processing %s recursively..." % target)
            for filename in target.recursedir('*.py'):
                process_file(filename, enable)
        else:
            logging.warning("Skipping %s..." % target)


if __name__ == '__main__':
    main()
