from vistrails.core.modules.basic_modules import Integer, String
from vistrails.core.modules.vistrails_module import Module, ModuleError


class QueryCondition(Module):
    """Base class for query conditions.

    This is abstract and implemented by modules Query*
    """

    _input_ports = [
            ('key', String)]

    def compute(self):
        self.condition = (self.getInputFromPort('key'),
                          self.make_condition_dict())

    def make_condition_dict(self):
        raise NotImplementedError('make_condition_dict')

QueryCondition._output_ports = [
        ('self', QueryCondition)]


class Metadata(QueryCondition):
    """Base class for metadata pairs.

    This is abstract and implemented by modules Equal*

    This both provides a metadata pair, as the 'metadata' attribute, for
    inserting, and a condition, through the 'condition' attribute.
    """
    _input_ports = [
            ('key', String),
            ('value', Module)]

    def compute(self):
        super(Metadata, self).compute()
        self.metadata = (self.getInputFromPort('key'),
                         self.getInputFromPort('value'))

Metadata._output_ports = [
        ('self', Metadata)]


class EqualString(Metadata):
    _input_ports = [
            ('key', String),
            ('value', String)]

    def make_condition_dict(self):
        return {'type': 'str', 'equal': self.getInputFromPort('value')}


class EqualInt(Metadata):
    _input_ports = [
            ('key', String),
            ('value', Integer)]

    def make_condition_dict(self):
        return {'type': 'int', 'equal': self.getInputFromPort('value')}


class IntInRange(QueryCondition):
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
