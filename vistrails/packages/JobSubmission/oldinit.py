from core.modules.vistrails_module import Module, ModuleError, NotCacheable, InvalidOutput, ModuleSuspended
from batchq.core.batch import BatchQ, Function, Property, FunctionMessage,  Collection, Exportable
from batchq import queues
import copy
category_basic_submission = 'Basic Submission'
category_job_operations = "Job operations"
category_low_level = "Low-level operations"
QUEUE_REGISTER = {}
typeconversion = {str:'(edu.utah.sci.vistrails.basic:String)', bool:'(edu.utah.sci.vistrails.basic:Boolean)', int:'(edu.utah.sci.vistrails.basic:Integer)', float:'(edu.utah.sci.vistrails.basic:Float)'}
qlist = [(a, getattr(queues,a)) for a in dir(queues) if isinstance(getattr(queues,a),type) and issubclass(getattr(queues,a),BatchQ) ]
capitalise = lambda x: x[0].upper() + x[1:].lower()

####
# Machine definition

class Machine(Module):
    get_kwargs = lambda self, cls: dict([(a[0],self.getInputFromPort(a[0])) for a in self._input_ports if self.hasInputFromPort(a[0]) and hasattr(cls,a[0]) and isinstance(getattr(cls,a[0]),Property)], **{'q_interact': False})
#                                         and hasattr(cls,a[0]) and isinstance(getattr(cls,a[0]),Property)]).update({'q_interact': False})  

_modules = [(Machine,{'abstract':True})]


def machine_compute(self):
    global QUEUE_REGISTER
    kwargs = self.get_kwargs(self.queue_cls)
    inherits = self.getInputFromPort('inherits').queue if self.hasInputFromPort('inherits') else None

    qid = self.__class__.__name__
    print "Queue id is", qid
    if not inherits is None and qid in QUEUE_REGISTER:
        print "Inheriting already existing queue ", qid
        inherits = QUEUE_REGISTER[qid]
    
    if self.queue is None:
        self.queue = self.queue_cls(**kwargs) if inherits is None else self.queue_cls(inherits, **kwargs) 
    else:
        print "Reusing own queue "
        ## TODO: update properties of machine
        pass

    if not qid in QUEUE_REGISTER:
        print "Copying queue to ", qid
        QUEUE_REGISTER[qid] =  self.queue.create_job(q_empty_copy = True)
    print "OBJECT ID:", id(self.queue)
    self.setResult("machine", self)

####
## Creating queues/"machines"

job_properties = {}
operations = {}
operations_types = {}
operations_highlevel = {}
operations_generators = {}
for name, queue in qlist:
    properties = []
    for a in dir(queue):
        if isinstance(getattr(queue,a), Property):
            attr = getattr(queue,a)
            if attr.verbose and attr.invariant:
                properties.append( (a,typeconversion[attr.type])  )
            if not attr.password and not attr.invariant:
                job_properties[a] = (a,typeconversion[attr.type],not attr.verbose)
    members = { '_input_ports' : properties + [('inherits','(org.comp-phys.batchq:Machine)',True)], 'queue_cls': queue,
                '_output_ports': [('machine', '(org.comp-phys.batchq:Machine)')],
                'compute': machine_compute, 'queue':None}
    cls = type(name[0].upper()+name[1:].lower(), (Machine,), members)

    functions = [(a,getattr(queue,a).type) for a in dir(queue) if isinstance(getattr(queue,a), Function) and not a.startswith("_") and getattr(queue,a).enduser]
    for f, t in functions:
        if not f in operations:
            operations[f] = []
            operations_types[f] = []
        operations[f].append(name)
        if not t in operations_types[f]: operations_types[f].append(t)

    _modules.append((cls,{'namespace':category_basic_submission}))

class Job(Machine):
    pass
_modules.append((Job, {'abstract':True}))

class PrepareJob(Job):
    _input_ports = [b for b in job_properties.itervalues()]+[('machine', '(org.comp-phys.batchq:Machine)'),]
    _output_ports = [('job', '(org.comp-phys.batchq:Job)'),]

    def compute(self):  
        mac = self.getInputFromPort("machine")
        queue, cls = mac.queue, mac.queue_cls
        print "Settings for machine: ", queue.settings
        kwargs = self.get_kwargs(cls)
        print "Getting kwargs for ",cls,":", kwargs
        self.queue =cls(queue, **kwargs) 
        self.setResult("job", self)
        print "OBJECT ID II:", id(self.queue)

standard_namespace = {'namespace':category_basic_submission}
_modules += [(PrepareJob, standard_namespace)] 

#####
## Creating functions 
class JobOperation(Module,NotCacheable):
    def __init__(self, *args, **kwargs):
        super(JobOperation,self).__init__(*args,**kwargs)


_modules+=[(JobOperation,{'abstract':True})]

def function_compute(self):
    job = self.getInputFromPort('job')
    queue = job.queue
    print "Queue ID:", id(queue)
    print "Function name: ",self.function_name
    ret = getattr(queue, self.function_name)().val()
    if isinstance(ret, FunctionMessage) and ret.code != 0:
        raise ModuleSuspended(self, ret.message) if ret.code > 0 else ModuleError(self,ret.message)
    
    self.setResult("job", job)
    self.setResult("result", ret)
    self.setResult("string", str(ret))

members = [ ('_input_ports', [('job', '(org.comp-phys.batchq:Job)'),] ),
            ('_output_ports', [('job', '(org.comp-phys.batchq:Job)')] ),
            ('compute', function_compute ),]

low_level_functions = {}
for name in operations.iterkeys():
    for t in operations_types[name]:
        print "Setting function name:",name, t, typeconversion[t] if t in typeconversion else "Not supported"
        dct = dict(copy.deepcopy(members)+[('function_name',name)])
        if not t is None and not t in [FunctionMessage]:
            dct['_output_ports'].append( ('result', typeconversion[t]) )
        append = "" if len(operations_types[name]) == 1 else capiltalise(str(t))
        namespace = category_job_operations
        prepend = "" 
        if t in [str,int, float]: 
            namespace = category_low_level
            prepend = "Get"
            low_level_functions[name] = (name,typeconversion[t])
        if t in [bool]: 
            namespace = category_low_level
            prepend = "Is"
            low_level_functions[name] = (name,typeconversion[t])

        
        _modules.append((type(prepend + "".join([capitalise(a) for a in name.split("_")]) + append, (JobOperation,),dct), {'namespace': namespace} ))




class JobInfo(Job):
    _input_ports = [('job', '(org.comp-phys.batchq:Job)'),]
    _output_ports = [b for b in job_properties.itervalues()] + [b for b in low_level_functions.itervalues()]
    def compute(self):
        self.setResult("job", self)        
        ## TODO: fix me, set outputs
_modules += [(JobInfo, standard_namespace)] 

######
## Creating collective operations
class CollectiveOperation(Module,NotCacheable):
    pass
_modules.append((CollectiveOperation, {'abstract':True}))

def collective_compute(self):
    job = self.getInputFromPort('job')
    operation = self.getInputFromPort('operation')
    col = Collection() + job
    col2 = getattr(col, collection_name)()
    rets = getattr(col2, operation.function_name)().as_list()
    self.setResult('job', rets[0])

collective = dict([(name,getattr(Collection, name)) for name in dir(Collection) if isinstance(getattr(Collection, name),Exportable)])
members = [ ('_input_ports', [('operation', '(org.comp-phys.batchq:JobOperation)'),('job', '(org.comp-phys.batchq:Job)')] ),
            ('_output_ports', [('job', '(org.comp-phys.batchq:Job)')] ),
            ('compute', collective_compute ),
            ('collection_name', name)]
namespace = "Job operations"
for name, func in collective.iteritems():
    dct = dict(members)
    _modules.append((type( "".join([capitalise(a) for a in name.split("_")]) , (CollectiveOperation,),dct),{'namespace':namespace} ))



class TestModule(Module, NotCacheable):
    def compute(self):
        raise ModuleSuspended(self, "I was suspended")

_modules = _modules
