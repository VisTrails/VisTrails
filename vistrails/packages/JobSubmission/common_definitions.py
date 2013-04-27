from batchq import queues
from batchq.core.batch import BatchQ
from batchq.queues import containers

from vistrails.core.modules.basic_modules import File, Directory
from vistrails.core.system import get_vistrails_basic_pkg_id

###
# Categories
categories = {
'basic_submission': 'Basic Submission',
'job_collective_operations': "Collective operations",
'low_level': "Low-level operations"
}
##
# Helper functions
name_formatter = lambda x: x
capitalise = lambda x: x[0].upper() + x[1:].lower()
remove_underscore = lambda j, name: j.join([capitalise(a) for a in name.split("_")])

basic_pkg = get_vistrails_basic_pkg_id()
type_conversion = {str:'(%s:String)' % basic_pkg, bool:'(%s:Boolean)' % basic_pkg, int:'(%s:Integer)' % basic_pkg, float:'(%s:Float)' % basic_pkg}

batch_queue_list = [(a, getattr(queues,a)) for a in dir(queues) if isinstance(getattr(queues,a),type) and issubclass(getattr(queues,a),BatchQ) ]


def create_directory(self, generator = None):
    x = self.interpreter.filePool.create_directory()
    return x.name

def create_file(self, contents, generator = None):
    ext=''
    if not generator is None:
        ext = generator.extension
    f = self.interpreter.filePool.create_file(suffix=ext)
    h = open(f.name,'w')
    h.write(contents)
    h.close()
    return f, f.name

def directory_wrapper(self, path, generator = None):
    ret = Directory.translate_to_python(path)
    return ret


generator_definitions = { containers.DirectoryName:create_directory }

exporter_definitions = { containers.TextFile: ('(%s:File)' % basic_pkg, 
                                               create_file),
                        containers.DirectoryName: ('(%s:Directory)' % basic_pkg,
                                                   directory_wrapper)}
