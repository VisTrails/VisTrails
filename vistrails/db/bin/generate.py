#!/usr/bin/env python
# pragma: no testimport
###############################################################################
##
## Copyright (C) 2014-2016, New York University.
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
##  - Neither the name of the New York University nor the names of its
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
"""auto-generates code given specs"""

# requires mako python package (easy_install Mako) and 
# uses emacs via subprocess call for python indentation
# the emacs call is slow because it checks all of the indentation

from __future__ import division

from mako.template import Template

import os
import re
import shutil
import subprocess
import sys
import tempfile
import getopt
from parser import AutoGenParser
import xml_gen_objects
import sql_gen_objects

BASE_DIR = os.path.dirname(os.getcwd())

DOMAIN_INIT = """from auto_gen import *"""
PERSISTENCE_INIT = \
"""from xml.auto_gen import XMLDAOListBase
from sql.auto_gen import SQLDAOListBase

class DAOList(dict):
    def __init__(self):
        self['xml'] = XMLDAOListBase()
        self['sql'] = SQLDAOListBase()

"""
COPYRIGHT_NOTICE = \
"""###############################################################################
##
## Copyright (C) 2014-2016, New York University.
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
##  - Neither the name of the New York University nor the names of its
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

"""

def preprocess_template(in_fname, out_fname=None):
    in_file = open(in_fname)
    if out_fname is not None:
        out_file = open(out_fname, 'w')
    else:
        out_file = sys.stdout

    single_slash = re.compile(r'\s*\\$')
    double_slash = re.compile(r'\s*\\\\$')
    triple_slash = re.compile(r'\s*\\\\\\$')
    slash_bang = re.compile(r'\s*\\!$')
    python_block = re.compile(r'^\s+<%')
    strip_whitespace = False
    for line in in_file:
        if strip_whitespace:
            line = line.lstrip()
        if python_block.search(line):
            line = python_block.sub(r'<%', line)
        if triple_slash.search(line):
            line = triple_slash.sub(r' ${"\\\\"}', line)
            strip_whitespace = False
        elif double_slash.search(line):
            line = double_slash.sub(r'\\', line)
            strip_whitespace = False
        elif slash_bang.search(line):
            line = line[:-3].rstrip()
            strip_whitespace = True
        elif single_slash.search(line):
            line = line[:-2].rstrip() + ' '
            strip_whitespace = True
        else:
            strip_whitespace = False
        out_file.write(line)

    if out_fname is not None:
        out_file.close()
    in_file.close()

def indent_python(fname):
    subprocess.Popen(["emacs", "-batch", fname, "-f", "mark-whole-buffer",
                      "-f", "indent-region", "-f", "save-buffer", "-kill"],
                     stdout=subprocess.PIPE).communicate()

def run_template(template_fname, objects, version, version_string, output_file,
                 indent=False):
    [prefix, suffix] = os.path.basename(template_fname).split('.', 1)
    (fd, p_fname) = tempfile.mkstemp(prefix=prefix, suffix=suffix)
    os.close(fd)
    try:
        preprocess_template(template_fname, p_fname)
        template = Template(filename=p_fname, module_directory='/tmp/mako')

        f = open(output_file, 'w')
        f.write(template.render(objs=objects,
                                version=version,
                                version_string=version_string))
        f.close()
        if indent:
            indent_python(output_file)
    finally:
        os.remove(p_fname)

def usage(usageDict):
    usageStr = ''
    unrequired = ''
    required = ''
    for (opt, info) in usageDict.iteritems():
        if info[1]:
            required += '-%s <%s> ' % (opt[0], info[2])
            usageStr += '    -%s <%s>  ' % (opt[0], info[2])
        else:
            if len(opt) > 1:
                unrequired += '[-%s <%s>] ' % (opt[0], info[2])
                usageStr += '    -%s <%s>  ' % (opt[0], info[2])
            else:
                unrequired += '[-%s] ' % opt[0]
                usageStr += '    -%s            ' % opt[0]
        usageStr += '%s\n' % info[0]
    print 'Usage: python generate.py %s%s\n%s' % (required, 
                                                             unrequired, 
                                                             usageStr)

def dirStructure(baseDir):
    dirs = {}
    dirs['base'] = baseDir
    dirs['specs'] = os.path.join(dirs['base'], 'specs')
    dirs['persistence'] = os.path.join(dirs['base'], 'persistence')
    dirs['domain'] = os.path.join(dirs['base'], 'domain')
    dirs['schemas'] = os.path.join(dirs['base'], 'schemas')
    dirs['xmlPersistence'] = os.path.join(dirs['persistence'], 'xml')
    dirs['sqlPersistence'] = os.path.join(dirs['persistence'], 'sql')
    dirs['xmlSchema'] = os.path.join(dirs['schemas'], 'xml')
    dirs['sqlSchema'] = os.path.join(dirs['schemas'], 'sql')
    return dirs

def makeAllDirs(dirs):
    for (name, dir) in dirs.iteritems():
        if not os.path.exists(dir):
            print "creating directory '%s'" % dir
            os.makedirs(dir)
        if name not in set(['specs', 'schemas', 'xmlSchema', 'sqlSchema']):
            init_file = os.path.join(dir, '__init__.py')
            if not os.path.exists(init_file):
                print "creating file '%s'" % init_file
                f = open(init_file, 'w')
                f.write(COPYRIGHT_NOTICE)
                if name == 'domain':
                    f.write(DOMAIN_INIT)
                elif name == 'persistence':
                    f.write(PERSISTENCE_INIT)
                else:
                    f.write('pass')
                f.close()
                    
def main(argv=None):
    options = {}
    objects = None

    optionsUsage = {'a': ('generate all database information (-p -s -x)', 
                          False),
                    'b:': ('base directory', False, 'dir'),
                    'd:': ('versions directory', False, 'dir'),
                    'p': ('generate python domain classes', False),
                    's': ('generate sql schema and persistence classes', False),
                    'x': ('generate xml schema and persistence classes', False),
                    'v:': ('vistrail version tag', True, 'version'),
                    'm': ('make all directories', False),
                    'n': ('do not change current version', False)}

    optStr = ''.join(optionsUsage.keys())
    optKeys = optStr.replace(':','')
    for idx in xrange(len(optKeys)):
        options[optKeys[idx]] = False

    try:
        (optlist, args) = getopt.getopt(sys.argv[1:], optStr)
        for opt in optlist:
            if opt[1] is not None and opt[1] != '':
                options[opt[0][1:]] = opt[1]
            else:
                options[opt[0][1:]] = True
    except getopt.GetoptError:
        usage(optionsUsage)
        return

    if options['b']:
        baseDir = options['b']
    else:
        baseDir = BASE_DIR
    baseDirs = dirStructure(baseDir)

    if not options['v']:
        usage(optionsUsage)
        return

    version = options['v']
    # make sure version use dot-style
    assert(len(version.split('.'))==3)
    versionName = 'v' + version.replace('.', '_')
    if options['d']:
        versionsDir = options['d']
    else:
        versionsDir = os.path.join(baseDir, 'versions')
    versionDir = os.path.join(versionsDir, versionName)
    versionDirs = dirStructure(versionDir)

    print baseDirs
    print versionDirs

    if options['m']:
        makeAllDirs(baseDirs)
        makeAllDirs(versionDirs)

    # check whether we should use existing specs for version
    use_base_specs = True
    if options['n'] and os.path.exists(versionDirs['specs']):
        for file in os.listdir(versionDirs['specs']):
            if file.lower().endswith('.xml'):
                # assume we've already copied the specs
                use_base_specs = False

    if use_base_specs:
        # copy specs to version        
        print "copying base specs to version directory..."
        for file in os.listdir(baseDirs['specs']):
            if file.lower().endswith('.xml'):
                print 'copying %s' % file
                filename = os.path.join(baseDirs['specs'], file)
                toFile = os.path.join(versionDirs['specs'], file)
                shutil.copyfile(filename, toFile)
    else:
        print "using existing specs from version directory..."

    if options['p'] or options['a']:
        # generate python domain objects
        print "generating python domain objects..."
        if objects is None:
            parser = AutoGenParser()
            objects = parser.parse(versionDirs['specs'])
        run_template('templates/domain.py.mako', objects, version, versionName,
                     os.path.join(versionDirs['domain'], 'auto_gen.py'),
                     True)

        if not options['n']:
            domainFile = os.path.join(baseDirs['domain'], '__init__.py')
            f = open(domainFile, 'w')
            f.write(COPYRIGHT_NOTICE)
            f.write('from vistrails.db.versions.%s.domain import *\n' % \
                        versionName)
            f.close()

    if options['x'] or options['a']:
        # generate xml schema and dao objects
        print "generating xml schema and dao objects..."
        if objects is None:
            parser = AutoGenParser()
            objects = parser.parse(versionDirs['specs'])
        xml_objects = xml_gen_objects.convert(objects)
        
        run_template('templates/xml_schema.xsd.mako', 
                     xml_gen_objects.convert_schema_order(xml_objects, 
                                                          'vistrail'),
                     version, versionName,
                     os.path.join(versionDirs['xmlSchema'], 'vistrail.xsd'),
                     False)

        run_template('templates/xml_schema.xsd.mako', 
                     xml_gen_objects.convert_schema_order(xml_objects, 
                                                          'workflow'),
                     version, versionName,
                     os.path.join(versionDirs['xmlSchema'], 'workflow.xsd'),
                     False)

        run_template('templates/xml_schema.xsd.mako', 
                     xml_gen_objects.convert_schema_order(xml_objects, 
                                                          'log'),
                     version, versionName,
                     os.path.join(versionDirs['xmlSchema'], 'log.xsd'),
                     False)

        run_template('templates/xml.py.mako', xml_objects, version, versionName,
                     os.path.join(versionDirs['xmlPersistence'], 'auto_gen.py'),
                     True)

    if options['s'] or options['a']:
        # generate sql schema and dao objects
        print "generating sql schema and dao objects..."
        if objects is None:
            parser = AutoGenParser()
            objects = parser.parse(versionDirs['specs'])
        sql_objects = sql_gen_objects.convert(objects)

        run_template('templates/sql_schema.sql.mako', sql_objects, 
                     version, versionName,
                     os.path.join(versionDirs['sqlSchema'], 'vistrails.sql'),
                     False)

        run_template('templates/sql_delete.sql.mako', sql_objects, 
                     version, versionName,
                     os.path.join(versionDirs['sqlSchema'], 
                                  'vistrails_drop.sql'),
                     False)
        
        run_template('templates/sql.py.mako', sql_objects,
                     version, versionName,
                     os.path.join(versionDirs['sqlPersistence'], 'auto_gen.py'),
                     True)

    if not options['n']:
        domainFile = os.path.join(baseDirs['persistence'], '__init__.py')
        f = open(domainFile, 'w')
        f.write(COPYRIGHT_NOTICE)
        f.write('from vistrails.db.versions.%s.persistence import *\n' % \
                    versionName)
        f.close()
            
if __name__ == '__main__':
    main()
