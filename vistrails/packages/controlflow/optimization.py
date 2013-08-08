import copy

from core.modules.vistrails_module import Module, InvalidOutput, \
    ModuleSuspended, ModuleError


class Optimize(Module):
    """
    The Optimize Module runs a module over and over until the condition port
    is true. Then, it returns the result.
    """

    def __init__(self):
        Module.__init__(self)
        self.is_fold_module = True

    def updateUpstream(self):
        """A modified version of the updateUpstream method."""

        # everything is the same except that we don't update anything
        # upstream of FunctionPort
        for port_name, connector_list in self.inputPorts.iteritems():
            if port_name == 'FunctionPort':
                for connector in connector_list:
                    connector.obj.updateUpstream()
            else:
                for connector in connector_list:
                    connector.obj.update()
        for port_name, connectorList in copy.copy(self.inputPorts.items()):
            if port_name != 'FunctionPort':
                for connector in connectorList:
                    if connector.obj.get_output(connector.port) is \
                            InvalidOutput:
                        self.removeInputConnector(port_name, connector)

    def compute(self):
        name_output = self.getInputFromPort('OutputPort')
        name_condition = self.getInputFromPort('ConditionPort')
        max_iterations = self.getInputFromPort('MaxIterations')

        connectors = self.inputPorts.get('FunctionPort')
        if len(connectors) != 1:
            raise ModuleError(self,
                              "Multiple modules connected on FunctionPort")
        module = connectors[0].obj

        for i in xrange(max_iterations):
            if not self.upToDate:
                module.upToDate = False
                module.already_computed = False

                # For logging
                module.is_fold_operator = True
                module.first_iteration = i == 0
                module.last_iteration = False
                module.fold_iteration = i

            module.update()
            if hasattr(module, 'suspended') and module.suspended:
                raise ModuleSuspended(module._module_suspended)

            if name_condition not in module.outputPorts:
                raise ModuleError(module,
                                  "Invalid output port: %s" % name_condition)
            if module.get_output(name_condition):
                break

        if name_output not in module.outputPorts:
            raise ModuleError(module,
                              "Invalid output port: %s" % name_output)
        result = copy.copy(module.get_output(name_output))
        self.setResult('Result', result)
