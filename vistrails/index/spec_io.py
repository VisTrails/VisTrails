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
import sys
import cPickle
import MySQLdb
from __core import Pipeline

DBHOST = 'localhost'
DBUSER = 'specuser'
DBPASS = 'specpass'
DBDB   = 'wfspec'

class Spec:
    def __init__(self):        
        try:
            self.db = MySQLdb.connect(DBHOST, DBUSER, DBPASS, DBDB)
        except MySQLdb.Error, e:
            print "1Database Connection Error %d: %s" % (e.args[0], e.args[1])
            sys.exit(1)
        self.cursor = MySQLdb.cursors.DictCursor(self.db)

    def _exec(self, command):
        try:
            self.cursor.execute(command)
        except MySQLdb.Error, e:
            try:
                self.db = MySQLdb.connect(DBHOST, DBUSER, DBPASS, DBDB)
                self.cursor = MySQLdb.cursors.DictCursor(self.db)
                self.cursor.execute(command)
            except MySQLdb.Error, e:
                print "3Database Connection Error %d: %s"%(e.args[0],e.args[1])
                sys.exit(1)
        return self.cursor.fetchall()

    def get(self, name):
        """ Given a name - returns the specification as a pickle object """
        command = "SELECT wf FROM single_spec WHERE name='%s'" % name
        for r in self._exec(command):
            wf = r['wf']
            # change class of pickle object (core module not allowed)-UGLY hack
            if wf[0:14] == '(iindex.__core':
                wf = wf.replace('(iindex.__core\n', '(i__core\n')
            return cPickle.loads(wf)
        return None

    def names(self):
        """ returns all names in db """
        command = "SELECT name FROM single_spec"
        return [name['name'] for name in self._exec(command)]

    def getIndex(self, name):
        command = "SELECT paths FROM spec_index WHERE name='%s'" % name
        for r in self._exec(command):
            return cPickle.loads(r['paths'])

    def add(self, wf):
        """ Inserts name, wf to single_spec """
        dump = cPickle.dumps(wf)
        dump = MySQLdb.escape_string(dump)
        command = "REPLACE INTO single_spec VALUES ('%s', '%s')"%(wf.id, dump)
        self._exec(command)
    
    def __del__(self):
        self.cursor.close()
        self.db.close()

spec = Spec()

idf = False
def get_idf(module):
    global idf
    if not idf:
        idf = cPickle.load(open("/server/crowdlabs/apps/vistrails/index/module.idf"))
    return idf.get(module.type, 9.0)
def getIDF(type):
    global idf
    if not idf:
        idf = cPickle.load(open("/server/crowdlabs/apps/vistrails/index/module.idf")) 
    return idf.get(type, 9.0)

idf2 = False
def get2IDF(type):
    global idf2
    if not idf2:
        idf2 = cPickle.load(open("2grams.idf"))
    return idf2.get(type, 9.0)

# right now actually just DF
path_idf = False
def getPathIDF(path):
    global path_idf
    if not path_idf:
        path_idf = cPickle.load(open("idf.pi"))
    return path_idf.get(path, 0)

# right now actually just DF
coIndex = False
def getCoIndex(pair):
    global coIndex
    if not coIndex:
        coIndex = cPickle.load(open("coindex.pi"))
    return coIndex.get(pair, 1)



