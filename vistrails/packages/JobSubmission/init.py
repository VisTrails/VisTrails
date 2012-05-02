from common_definitions import categories, capitalise, \
    type_conversion, batch_queue_list, remove_underscore, name_formatter, \
    generator_definitions, exporter_definitions
from core.modules.vistrails_module import Module, ModuleError, \
    NotCacheable, InvalidOutput, ModuleSuspended
from batchq.core.batch import BatchQ, Function, Property, FunctionMessage, \
    Collection, Exportable
from batchq.queues import NoHUP
import copy
from machine import module_definitions, Machine
_modules = module_definitions



#######################################
## Creating queues/"machines"
#######################################

## Stores exportable properties 
## (property_name, vistrails_type, port visibility) for
## each key = property_name
exp_job_properties = {}

## Stores all non-auto-generated 
## properties (property_name, vistrails type, port visibility) 
## for each key = property_name
in_job_properties = {}

## Stores property for each key = property_name
job_properties = {}

## Stores (property_name, vistrails type, generator)
## for each key = property_name
auto_job_properties = {}  

operations = {}
operations_types = {}
operations_highlevel = {}
for queue_name, queue in batch_queue_list:

    ## Generating queue classes
    properties = []
    for prop_name in dir(queue):
        if isinstance(getattr(queue,prop_name), Property):
            attr = getattr(queue,prop_name)

            ## Properties which are machine dependent
            if attr.verbose and attr.invariant:
                properties.append( (prop_name,type_conversion[attr.type])  )

            ## Properties which are job dependent
            if not attr.password and not attr.invariant:
                job_properties[prop_name] = attr

                # Sorting auto generated fields
                if attr.generator is None:
                    in_job_properties[prop_name] = (prop_name, 
                                                    type_conversion[attr.type], 
                                                    not attr.verbose)
                elif attr.generator.type in generator_definitions:

                    auto_job_properties[prop_name] = (prop_name,
                                                      type_conversion[attr.type],
                                                      generator_definitions[attr.generator.type])

                # Sorting exportable fields
                if attr.exporter is None:
                    exp_job_properties[prop_name] = (prop_name,type_conversion[attr.type], 
                                                     not attr.verbose)
                else:
                    t, _ = exporter_definitions[attr.exporter.type]
                    exp_job_properties[prop_name] = (prop_name, t, not attr.verbose)

    ## Definiting machines/queuing systems
    members = { '_input_ports' : [('inherits',
                                   '(org.comp-phys.batchq:Machine)',
                                   True)] + properties, 
                'queue_cls'    : queue,
                '_output_ports': [('machine', 
                                   '(org.comp-phys.batchq:Machine)')],
                'queue'        : None
                }

    if hasattr(queue, "__descriptive_name__"):
        descriptive_name =  queue.__descriptive_name__
    else:
        descriptive_name = capitalise(queue_name)

    cls = type(name_formatter(descriptive_name), (Machine,), members)

    ## Extracing all functions from the queues - these will be used later 
    ## for module generation
    functions = [(a,getattr(queue,a)) for a in dir(queue) 
                 if isinstance(getattr(queue,a), Function) and 
                 not a.startswith("_") and getattr(queue,a).enduser ]

    for f, fnc in functions:
        t = fnc.type
        if not f in operations:
            operations[f] = []
            operations_types[f] = []
            operations_highlevel[f] = False

        operations[f].append(queue_name)
        operations_highlevel[f] = operations_highlevel[f] or fnc.highlevel

        if not t in operations_types[f]: operations_types[f].append(t)

    _modules.append((cls,{'namespace':categories['basic_submission']}))

functions = dict(functions)

#######################################
## Basic Job and Job creation module
#######################################
class Job(Machine):
    pass
_modules.append((Job, {'abstract':True}))


def compute_jobpreparation(self):  
    mac = self.getInputFromPort("machine")
    queue, cls = mac.queue, mac.queue_cls
    kwargs = self.get_kwargs(cls)

    for f, t, generator in auto_job_properties.itervalues():
        kwargs[f] = generator(self)

    self.queue = cls(queue, **kwargs) 

    self.setResult("job", self)

dct = {'_input_ports'   : [b for b in in_job_properties.itervalues()] \
           + [('machine', '(org.comp-phys.batchq:Machine)'),],
       '_output_ports'  : [('job', '(org.comp-phys.batchq:Job)'),],
       'compute'        : compute_jobpreparation
       }

PrepareJob = type(name_formatter("Prepare Job"), (Job,), dct)

_modules += [(PrepareJob, {'namespace':categories['basic_submission']})] 

#######################################
## Creating functions 
#######################################
class JobOperation(NotCacheable,Module):
    pass

def joboperation_compute(self):
    if self.hasInputFromPort("job"):
        job = self.getInputFromPort('job')
        queue = job.queue
#    print "TERMINAL ID", id(queue.terminal), id(queue.local_terminal)
        self.anno_counter = 1
        self.anno_dict = {}
        def annotate(fncself, *args, **kwargs):
            if len(args) == 1:
                self.anno_dict.update( {"note%d"%self.anno_counter: args[0]} )
            elif len(kwargs) == 0:
                self.anno_dict.update( {"note%d"%self.anno_counter:" ".join(args)} )
            else:
                self.anno_dict.updateself.annotate( kwargs )
            self.anno_counter +=1
            return None
        function = getattr(queue, self.function_name)
        pnt = function.Qprint
        function.Qprint = annotate
        ret = function().val()
        function.Qprint = pnt 
        
        ## TODO: annotate does not seem to work
        self.annotate(self.anno_dict)

        if isinstance(ret, FunctionMessage) and ret.code != 0:
            raise ModuleSuspended(self, ret.message) if ret.code > 0 \
                else ModuleError(self,ret.message)

        self.setResult("job", job)
        self.setResult("result", ret)
        self.setResult("string", str(ret))
    self.setResult("operation", self)

_modules+=[(JobOperation,{'abstract':True})]

members = [ ('_input_ports', [('job', '(org.comp-phys.batchq:Job)'),] ),
            ('_output_ports', [('job', '(org.comp-phys.batchq:Job)')] ),
            ('compute', joboperation_compute)]

low_level_functions = {}
high_level_functions = {}
high_level_modules = []
for name in operations.iterkeys():
    for t in operations_types[name]:
        dct = dict(copy.deepcopy(members)+[('function_name',name)])
        if not t is None and not t in [FunctionMessage]:
            dct['_output_ports'].append( ('result', type_conversion[t]) )

        #  TODO: Multiple types yet to be implemented
        ## append = "" if len(operations_types[name]) == 1 else capiltalise(str(t))
        namespace = categories['low_level']

        descriptive_name = remove_underscore(" ",name)
        if t in [str,int, float, bool]: 
            if functions[name].exporter is None:
                low_level_functions[name] = (name,type_conversion[t])
            else:
                tt, _ = exporter_definitions[functions[name].exporter.type]
                low_level_functions[name] = (name,tt)

            if t in [bool]: 
                descriptive_name = "Is" + remove_underscore("",name)
            else:
                descriptive_name = "Get" + remove_underscore("",name)

        if not operations_highlevel[name]:
            dct['_output_ports'].append( ('operation', '(org.comp-phys.batchq:JobOperation)') )
            cls = ( type(name_formatter(descriptive_name), 
                         (JobOperation,),dct), 
                    {'namespace': namespace} )
            _modules.append(cls)
        else:
            namespace = categories['basic_submission']
            if t in type_conversion:
                high_level_functions[name] = (name,type_conversion[t]) 
            else: 
                high_level_functions[name] = (name,None)
            high_level_modules.append((descriptive_name, dct, namespace))
#        namespace = categories['basic_submission']


def jobinfo_compute(self):
    job = self.getInputFromPort("job")
    queue = job.queue
    for function in self.queue_functions:
        name = function[0]
        function =getattr(queue, name)
        ret =function().val()
        if function.exporter is None:
            self.setResult(name, ret)
        else:
            ## If the field is exported to a vistrails 
            ## type the conversion is done here
            exporter = function.exporter
            _, exp = exporter_definitions[exporter.type]
            ret = function.exporter.as_str()
            self.setResult(name, exp(self,ret))

    for prop in self.queue_properties:
        name = prop[0]
        field = queue.fields[name]
        ret = field.get()
        if field.exporter is None:
            self.setResult(name, ret)
        else:
            exporter = field.exporter
            _, exp = exporter_definitions[exporter.type]

            ret = exporter.as_str()
            self.setResult(name, exp(self,ret))

    self.setResult("job", job)


queue_properties = [b for b in exp_job_properties.itervalues()]
queue_functions = [b for b in low_level_functions.itervalues()]
dct = {'_input_ports': [('job', '(org.comp-phys.batchq:Job)'),],
       '_output_ports': queue_properties  + queue_functions,
       'compute': jobinfo_compute,
       'queue_properties': queue_properties,
       'queue_functions':  queue_functions}
JobInfo = type(name_formatter("Job Info"), (NotCacheable,Job,), dct)

_modules += [(JobInfo, {'namespace':categories['basic_submission']})] 

####
# High-level function
def highlevel_compute(self):
    joboperation_compute(self)
    jobinfo_compute(self)

for descriptive_name, dct, namespace in high_level_modules:
    dct['compute'] = highlevel_compute
    dct['is_cacheable'] = lambda self: True
    _modules.append((type(name_formatter(descriptive_name), (JobInfo,),dct), {'namespace': namespace} ))

######
## Creating collective operations
class CollectiveOperation(NotCacheable,Module):
    pass
_modules.append((CollectiveOperation, {'abstract':True}))

def collective_compute(self):
    job = self.getInputFromPort('job')
    operation = self.getInputFromPort('operation')
    col = Collection() 
    col += job.queue

    col2 = getattr(col, self.collection_name)()
    rets = getattr(col2, operation.function_name)().as_list()
    ## TODO: ad results
    self.setResult('job', job)

collective = dict([(name,getattr(Collection, name)) for name in dir(Collection) if isinstance(getattr(Collection, name),Exportable)])
members = [ ('_input_ports', [('operation', '(org.comp-phys.batchq:JobOperation)'),('job', '(org.comp-phys.batchq:Job)')] ),
            ('_output_ports', [('job', '(org.comp-phys.batchq:Job)')] ),
            ('compute', collective_compute ),
            ('collection_name', name)]
namespace = categories['job_collective_operations']
for name, func in collective.iteritems():
    dct = dict(members)
    _modules.append((type( "".join([capitalise(a) for a in name.split("_")]) , (CollectiveOperation,),dct),{'namespace':namespace} ))



_modules = _modules
