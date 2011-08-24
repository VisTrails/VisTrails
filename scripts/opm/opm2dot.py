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
import os
import sys
from xml.etree import cElementTree as ElementTree

def run(filename, account=None):
    root = ElementTree.parse(filename)
    node_id = 0
    lookup = {}
    error_edges = []

    def should_include(obj):
        if account is None:
            return True
        else:
            for an_account in obj.getiterator('account'):
                if an_account.get('id') == account:
                    return True
        return False
        
    print 'digraph {'
    print 'edge [dir = "back", style="dashed"];'
    for process in root.getiterator('processes').next().getiterator('process'):
        if not should_include(process):
            continue
        process_id = process.get('id')
        error = None
        for child in process.getiterator('value').next().getchildren():
            if child.tag == 'moduleExec':
                process_label = child.get('moduleName')
                if child.get('completed') == '-1':
                    error = child.get('error')
            elif child.tag == 'groupExec':
                process_label = child.get('groupName')
                if child.get('completed') == '-1':
                    error = child.get('error')
        if child.tag == 'groupExec':
            shape = 'hexagon'
        elif child.tag == 'moduleExec' and child.get('moduleName') == 'Map':
            shape = 'hexagon'
        else:
            shape = 'box'
        print '%d [label="%s", shape=%s, color=blue];' % \
            (node_id, process_label, shape)
        lookup[process_id] = node_id
        node_id += 1
        if error is not None:
            print '%d [label="ERROR: %s", shape=octagon, color=black];' % (node_id,
                                                                    error)
            error_edges.append((node_id - 1, node_id))
        node_id += 1

    for artifact in root.getiterator('artifacts').next().getiterator('artifact'):
        if not should_include(artifact):
            continue
        artifact_id = artifact.get('id')
        for child in artifact.getiterator('value').next().getchildren():
            if child.tag == 'portSpec':
                port_name = str(child.get('name'))
                # artifact_label = '[' + str(child.get('name')) + ']'
                spec = str(child.get('sigstring'))
                if spec:
                    artifact_label = port_name + ' = [' + spec[spec.index(':')+1:spec.index(')')] + ']'
                else:
                    artifact_label = port_name
            elif child.tag == 'function':
                artifact_label = str(child.get('name')) + ' = ('
                comma = ''
                for param in child.getiterator('parameter'):
                    param_val = param.get('val')
                    if len(param_val) > 32:
                        if param.get('type') == \
                                'edu.utah.sci.vistrails.basic:File':
                            print >>sys.stderr, "got here"
                            dir_names = []
                            dir_name = param_val
                            while os.path.split(dir_name)[1]:
                                (dir_name, next_name) = os.path.split(dir_name)
                                dir_names.append(next_name)
                            dir_names.append('/')
                            if len(dir_names) <= 1:
                                param_val = param_val
                            dir_names.reverse()
                            if len(dir_names[-1]) > 28:
                                i = 1
                                j = 1
                                arr = dir_names[-1].split('_')
                                while len('_'.join(arr[:i] + ['...'] + arr[-j:])) < 28:
                                    if i == j:
                                        i += 1
                                    else:
                                        j += 1
                                dir_names[-1] = '_'.join(arr[:i] + ['...'] + arr[-j:])
                            print >>sys.stderr, dir_names
                            i = 1
                            while (len(os.path.join(dir_names[0], dir_names[1],
                                                    '...', 
                                                    *dir_names[-i:])) < 32 and
                                   i+1 < len(dir_names)):
                                print >>sys.stderr, \
                                    len(os.path.join(dir_names[0], 
                                                     dir_names[1],
                                                     '...', 
                                                     *dir_names[-i:]))
                                i += 1
                            print >>sys.stderr, i
                            param_val = os.path.join(dir_names[0], 
                                                     dir_names[1], '...',
                                                     *dir_names[-i:])
                        else:
                            param_val = param_val[:24] + '...' + param_val[-8:]
                    artifact_label += comma + param_val
                    comma = ', '
                artifact_label += ')'
            else:
                print >>sys.stderr, "ERROR:", child.tag
                artifact_label = artifact.get('id')
        print '%d [label="%s", color=red];' % (node_id, artifact_label)
        lookup[artifact_id] = node_id
        node_id += 1
    for used in root.getiterator('causalDependencies').next().getiterator('used'):
        if not should_include(used):
            continue

        print "%d -> %d;" % \
            (lookup[used.getiterator('cause').next().get('id')], 
             lookup[used.getiterator('effect').next().get('id')])
    for wgb in root.getiterator('causalDependencies').next().getiterator('wasGeneratedBy'):
        if not should_include(wgb):
            continue

        print "%d -> %d;" % \
            (lookup[wgb.getiterator('cause').next().get('id')], 
             lookup[wgb.getiterator('effect').next().get('id')])
    for wtb in root.getiterator('causalDependencies').next().getiterator('wasTriggeredBy'):
        if not should_include(wtb):
            continue
        print "%d -> %d;" % \
            (lookup[wtb.getiterator('cause').next().get('id')], 
             lookup[wtb.getiterator('effect').next().get('id')])

    for error_edge in error_edges:
        print "%d -> %d;" % error_edge
    print "}"
    

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Usage: python %s <opm_file> [account]" % sys.argv[0]
        sys.exit(42)
    account = sys.argv[2] if len(sys.argv) > 2 else None
    run(sys.argv[1], account)
