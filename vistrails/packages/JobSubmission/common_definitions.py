from batchq import queues
from batchq.core.batch import BatchQ
from batchq.queues import containers

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

type_conversion = {str:'(edu.utah.sci.vistrails.basic:String)', bool:'(edu.utah.sci.vistrails.basic:Boolean)', int:'(edu.utah.sci.vistrails.basic:Integer)', float:'(edu.utah.sci.vistrails.basic:Float)'}

batch_queue_list = [(a, getattr(queues,a)) for a in dir(queues) if isinstance(getattr(queues,a),type) and issubclass(getattr(queues,a),BatchQ) ]

from core.modules.basic_modules import File, Directory

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

exporter_definitions = { containers.TextFile: ('(edu.utah.sci.vistrails.basic:File)', create_file),
                        containers.DirectoryName: ('(edu.utah.sci.vistrails.basic:Directory)', directory_wrapper)}
