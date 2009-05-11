import sys
from xml.etree import cElementTree as ElementTree

def run(filename, account=None):
    root = ElementTree.parse(filename)
    node_id = 0
    lookup = {}
    
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
        for child in process.getiterator('value').next().getchildren():
            if child.tag == 'moduleExec':
                process_label = child.get('moduleName')
            elif child.tag == 'groupExec':
                process_label = child.get('groupName')
        print '%d [label="%s", shape=box, color=blue];' % \
            (node_id, process_label)
        lookup[process_id] = node_id
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
                        param_val = param_val[:32] + '...'
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
    print "}"
    

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Usage: python %s <opm_file> [account]" % sys.argv[0]
        sys.exit(42)
    account = sys.argv[2] if len(sys.argv) > 2 else None
    run(sys.argv[1], account)
