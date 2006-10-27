from core import modules
from core.modules.vistrails_module import ModuleConnector, ModuleError
from core.modules.module_utils import FilePool
from core.common import withIndex, InstanceObject
import threading

################################################################################

_lock = threading.Lock()

class Interpreter(object):
    def __init__(self):
        pass

    typeConversion = {'Float': float,
                      'Integer': int,
                      'String': lambda x: x}

    

    def execute(self, pipeline, vistrailName, currentVersion, view, logger, useLock=True):
        try:
            if useLock:
                _lock.acquire()
            self.filePool = FilePool()
            objects = {}
            errors = {}
            executed = {}
            def addToExecuted(obj):
                executed[obj.id] = True
            def beginCompute(obj):
                view.setModuleComputing(obj.id)
            def beginUpdate(obj):
                view.setModuleActive(obj.id)
                name = modules.module_registry.registry.getDescriptor(obj.__class__).name
                if logger:
                    logger.startModuleExecution(vistrailName, currentVersion, obj.id, name)
            def endUpdate(obj, error=''):
                if not error:
                    view.setModuleSuccess(obj.id)
                else:
                    view.setModuleError(obj.id, error)
                if logger:
                    logger.finishModuleExecution(vistrailName, currentVersion, obj.id)
            def annotate(obj, d):
                if logger:
                    logger.insertAnnotationDB(vistrailName, currentVersion, obj.id, d)
            logging_obj = InstanceObject(signalSuccess=addToExecuted,
                                         beginUpdate=beginUpdate,
                                         beginCompute=beginCompute,
                                         endUpdate=endUpdate,
                                         annotate=annotate)
            # create objects
            for id, module in pipeline.modules.items():
    #            print "Will summon module", id, module
                objects[id] = module.summon()
                objects[id].interpreter = self
                objects[id].id = id
                if view:
                    objects[id].logging = logging_obj
                objects[id].vistrailName = vistrailName
                objects[id].currentVersion = currentVersion
    #            print "result: ", objects[id]
                for f in module.functions:
                    if len(f.params)==0:
                        nullObject = modules.module_registry.registry.getDescriptorByName('Null').module()
                        objects[id].setInputPort(f.name, ModuleConnector(nullObject, 'value'))
                    if len(f.params)==1:
                        p = f.params[0]
                        constant = modules.module_registry.registry.getDescriptorByName(p.type).module()
                        constant.setValue(p.evaluatedStrValue)
                        objects[id].setInputPort(f.name, ModuleConnector(constant, 'value'))
                    if len(f.params)>1:
                        value_list = []
                        tupleModule = modules.module_registry.registry.getDescriptorByName('Tuple').module()
                        tupleModule.length = len(f.params)
                        for (i,p) in withIndex(f.params):
                            constant = modules.module_registry.registry.getDescriptorByName(p.type).module()
                            constant.setValue(p.evaluatedStrValue)
                            tupleModule.setInputPort(i, ModuleConnector(constant, 'value'))
                        objects[id].setInputPort(f.name, ModuleConnector(tupleModule, 'value'))
                        
            # create connections
            for id, conn in pipeline.connections.items():
    #             print "Will connect ",conn.sourceId,"and",conn.destinationId,
    #             print "with",conn
                src = objects[conn.sourceId]
                dst = objects[conn.destinationId]
    #             print "src:",src
    #             print "dst:",dst
                conn.makeConnection(src, dst)

            for v in pipeline.graph.sinks():
                try:
                    objects[v].update()
                except ModuleError, me:
                    me.module.logging.endUpdate(me.module, False)
#                     print "Module failed during execution."
#                     print "Module:",me.module
#                     print "Error:",me.msg
                    errors[me.module.id] = me
        finally:
            if useLock:
                _lock.release()
            self.filePool.cleanup()
            del self.filePool
        
        return (objects, errors, executed)
        
################################################################################
