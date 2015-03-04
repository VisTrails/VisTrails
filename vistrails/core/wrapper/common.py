from vistrails.core.modules.basic_modules import Color, Path, PathObject
from vistrails.core.utils import InstanceObject

#### Automatic conversion between some vistrail and python types ####
def convert_input_param(value, _type):
    if issubclass(_type, Path):
        return value.name
    if issubclass(_type, Color):
        return value.tuple
    return value

def convert_output_param(value, _type):
    if issubclass(_type, Path):
        return PathObject(value)
    if issubclass(_type, Color):
        return InstanceObject(tuple=value)
    return value

def convert_input(value, signature):
    if len(signature) == 1:
        return convert_input_param(value, signature[0][0])
    return tuple([convert_input_param(v, t[0]) for v, t in zip(value, signature)])

def convert_output(value, signature):
    if len(signature) == 1:
        return convert_output_param(value, signature[0][0])
    return tuple([convert_output_param(v, t[0]) for v, t in zip(value, signature)])


def get_input_spec(cls, name):
    """ Get named input spec from self or superclass
    """
    klasses = iter(cls.__mro__)
    base = cls
    while base and hasattr(base, '_input_spec_table'):
        if name in base._input_spec_table:
            return base._input_spec_table[name]
        base = klasses.next()
    return None

def get_output_spec(cls, name):
    """ Get named output spec from self or superclass
    """
    klasses = iter(cls.__mro__)
    base = cls
    while base and hasattr(base, '_output_spec_table'):
        if name in base._output_spec_table:
            return base._output_spec_table[name]
        base = klasses.next()
    return None

