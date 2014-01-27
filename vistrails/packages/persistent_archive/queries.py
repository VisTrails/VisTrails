from vistrails.core.modules.basic_modules import Constant, Integer, String
from vistrails.core.modules.config import IPort, OPort
from vistrails.core.modules.vistrails_module import Module, ModuleError


def find_subclass(cls, subname):
    """Find a subclass by name.
    """
    l = [cls]
    while l:
        l2 = []
        for c in l:
            if c.__name__ == subname:
                return c
            l2 += c.__subclasses__()
        l = l2
    return None


class QueryCondition(Constant):
    """Base class for query conditions.

    This is abstract and implemented by modules Query*
    """
    _input_ports = [
            IPort('key', String)]

    @staticmethod
    def translate_to_python(c):
        try:
            i = c.index('(')
        except ValueError:
            raise ValueError("Invalid QueryCondition syntax")
        clsname = c[:i]
        cls = find_subclass(QueryCondition, clsname)
        if cls is None:
            raise ValueError("No such condition type: %s" % clsname)
        return cls(*eval(c[i+1:-1]))

    @staticmethod
    def translate_to_string(cond):
        return str(cond)

    @staticmethod
    def validate(cond):
        return isinstance(cond, QueryCondition)

    def __str__(self):
        raise NotImplementedError

    def __repr__(self):
        return self.__str__()

QueryCondition._output_ports = [
        OPort('self', QueryCondition)]


class Metadata(QueryCondition):
    """Base class for metadata pairs.

    This is abstract and implemented by modules Equal*

    This both provides a metadata pair, as the 'metadata' attribute, for
    inserting, and a condition, through the 'condition' attribute.
    """
    _input_ports = [
            IPort('key', String),
            IPort('value', Module)]

    def __init__(self, *args):
        super(Metadata, self).__init__()

        if args:
            self.key, self.value = args
            self.set_results()
        else:
            self.key, self.value = None, None

    def compute(self):
        self.key = self.get_input('key')
        self.value = self.get_input('value')

        self.set_results()

    def set_results(self):
        self.condition = (self.key, {'type': self._type, 'equal': self.value})
        self.metadata = (self.key, self.value)

    def __str__(self):
        return '%s(%r, %r)' % (self.__class__.__name__, self.key, self.value)

Metadata._output_ports = [
        OPort('self', Metadata)]


class EqualString(Metadata):
    _input_ports = [
            IPort('key', String),
            IPort('value', String)]

    _type = 'str'


class EqualInt(Metadata):
    _input_ports = [
            IPort('key', String),
            IPort('value', Integer)]

    _type = 'int'


class IntInRange(QueryCondition):
    _input_ports = [
            IPort('key', String),
            IPort('lower_bound', Integer, optional=True),
            IPort('higher_bound', Integer, optional=True)]

    def __init__(self, *args):
        super(IntInRange, self).__init__()

        if args:
            self.key, self.low, self.high = args
            self.set_results()
        else:
            self.key, self.low, self.high = None, None, None

    def compute(self):
        self.key = self.get_input('key')
        if self.has_input('lower_bound'):
            self.low = self.get_input('lower_bound')
        if self.has_input('higher_bound'):
            self.high = self.get_input('higher_bound')
        if not (self.low is not None or self.high is not None):
            raise ModuleError(self, "No bound set")
        self.set_results()

    def set_results(self):
        dct = {}
        if self.low is not None:
            dct['gt'] = self.low
        if self.high is not None:
            dct['lt'] = self.high
        dct['type'] = 'int'

        self.condition = (self.key, dct)

    def __str__(self):
        return '%s(%r, %r, %r)' % ('IntInRange', self.key, self.low, self.high)
