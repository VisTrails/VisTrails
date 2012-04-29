from core.modules.vistrails_module import Module
from batchq.core.batch import Property
QUEUE_REGISTER = {}
####
# Machine definition
class Machine(Module):
    def get_kwargs(self, cls):
        
        ret = dict([(a[0],self.getInputFromPort(a[0])) for a in self._input_ports if self.hasInputFromPort(a[0]) and a[0] in cls.__new_fields__ and isinstance(cls.__new_fields__[a[0]],Property)])
        ret.update({'q_interact': False})
        return ret

    def compute(self):
        global QUEUE_REGISTER
        kwargs = self.get_kwargs(self.queue_cls)
        inherits = self.getInputFromPort('inherits').queue if self.hasInputFromPort('inherits') else None

        if self.signature in QUEUE_REGISTER:
            q = QUEUE_REGISTER[self.signature]
            if hasattr(q, "disconnect"):
                q.disconnect()


        self.queue = self.queue_cls(**kwargs) if inherits is None else self.queue_cls(inherits, **kwargs) 

        QUEUE_REGISTER[str(self.signature)] = self.queue

        self.setResult("machine", self)

module_definitions = [(Machine,{'abstract':True})]
