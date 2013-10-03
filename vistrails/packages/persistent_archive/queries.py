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


class Metadata(Module):
    """Base class for metadata pairs.

    This is abstract and implemented by modules Metadata*

    This both provides a metadata pairs, as the 'metadata' attribute, for
    inserting, and a condition, through the 'condition' attribute.
    """
    _input_ports = [
            ('key', String),
            ('value', Module)]

    def compute(self):
        self.condition = (self.getInputFromPort('key'),
                          self.make_condition_dict())
        self.metadata = (self.getInputFromPort('key'),
                         self.getInputFromPort('value'))


# Mixin classes used for both QueryCondition and Metadata

class StringValue(object):
    _input_ports = [
            ('key', String),
            ('value', String)]

    def make_condition_dict(self):
        return {'type': 'str', 'equal': self.getInputFromPort('value')}


class IntValue(object):
    _input_ports = [
            ('key', String),
            ('value', Integer)]

    def make_condition_dict(self):
        return {'type': 'int', 'equal': self.getInputFromPort('value')}


# QueryConditon implementations

class QueryStringEqual(StringValue, QueryCondition):
    pass

class QueryIntEqual(QueryCondition, IntValue):
    pass


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


# Metadata implementations

class MetadataString(StringValue, Metadata):
    pass


class MetadataInt(IntValue, Metadata):
    pass
