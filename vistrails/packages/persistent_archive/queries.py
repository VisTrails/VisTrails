from vistrails.core.modules.basic_modules import Integer, String
from vistrails.core.modules.vistrails_module import Module, ModuleError


class QueryCondition(Module):
    _input_ports = [
            ('key', String)]

    def compute(self):
        self.condition = (
                self.getInputFromPort('key'),
                self.make_condition_dict())

    def make_condition_dict(self):
        raise NotImplementedError('make_condition_dict')

QueryCondition._output_ports = [
        ('self', QueryCondition)]


class QueryStringEqual(QueryCondition):
    _input_ports = [
            ('key', String),
            ('value', String)]

    def make_condition_dict(self):
        return {'type': 'str', 'equal': self.getInputFromPort('value')}


class QueryIntEqual(QueryCondition):
    _input_ports = [
            ('key', String),
            ('value', Integer)]

    def make_condition_dict(self):
        return {'type': 'int', 'equal': self.getInputFromPort('value')}


class QueryIntRange(QueryCondition):
    _input_ports = [
            ('key', String),
            ('lower_bound', Integer, True),
            ('higher_bound', Integer, True)]

    def make_condition_dict(self):
        dct = {}
        if self.hasInputFromPort('lower_bound'):
            dct['gt'] = self.getInputFromPort('lower_bound')
        if self.hasInputFromPort('higher_bound'):
            dct['lt'] = self.getInputFromPort('higher_bound')
        if not dct:
            raise ModuleError(self, "No bound set")
        dct['type'] = 'int'
        return dct
