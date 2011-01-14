from entity import Entity

class WorkflowExecEntity(Entity):
    type_id = 3

    def __init__(self, workflow_exec=None):
        Entity.__init__(self)
        self.id = None
        self.update(workflow_exec)

    @staticmethod
    def load(*args):
        entity = WorkflowExecEntity()
        Entity.load(entity, *args)
        return entity

    def update(self, workflow_exec):
        self.workflow_exec = workflow_exec
        if self.workflow_exec is not None:
            self.name = "Execution #%s" % self.workflow_exec.id
            self.user = self.workflow_exec.user
            self.mod_time = \
                self.workflow_exec.ts_end.strftime('%d %b %Y %H:%M:%S') \
                if self.workflow_exec.ts_end else '1 Jan 0000 00:00:00'
            self.create_time = \
                self.workflow_exec.ts_start.strftime('%d %b %Y %H:%M:%S') \
                if self.workflow_exec.ts_start else '1 Jan 0000 00:00:00'
            self.size = len(self.workflow_exec.item_execs)
            self.description = ""
            self.url = 'test'
            self.was_updated = True
        
    # returns boolean, True if search input is satisfied else False
    def match(self, search):
        raise Exception("Not implemented")

