import re
import subprocess
import sys


re_setup = re.compile(r'setup\(')
re_version = re.compile(r'(?<=\bversion=[\'"])([0-9a-zA-Z._+-]+)')


if __name__ == '__main__':
    # Get version from git describe
    version = subprocess.check_output(['git', 'describe',
                                       '--always', '--tags']).strip()

    setup_py = sys.argv[1]

    # Update setup.py file
    with open(setup_py, 'rb') as fp:
        lines = fp.readlines()

    i = 0
    setup_found = False
    version_replaced = False
    while i < len(lines):
        line = lines[i]
        if not setup_found and re_setup.search(line):
            setup_found = True
        if setup_found:
            m = re_version.search(line)
            if m is not None:
                lines[i] = re_version.sub(version, line)
                version_replaced = True
                break
        i += 1

    if not version_replaced:
        sys.stderr.write("Didn't find version number to replace\n")
        sys.exit(1)

    with open(setup_py, 'wb') as fp:
        for line in lines:
            fp.write(line)
