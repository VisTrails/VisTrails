'''
Created on Nov 18, 2010

@author: talbertc
'''
import os
from core.modules.basic_modules import File, Directory, new_constant, Constant

def map_ports(module, port_map):
    args = {}
    for port, (flag, access, required) in port_map.iteritems():
        if required or module.hasInputFromPort(port):
            value = module.getInputFromPort(port)
            if access is not None:
                value = access(value)
            args[flag] = value
    return args

def path_value(value):
    return value.name

def create_file_module(fname, f=None):
    if f is None:
        f = File()
    f.name = fname
    f.upToDate = True
    return f

def create_dir_module(dname, d=None):
    if d is None:
        d = Directory()
    d.name = dname
    d.upToDate = True
    return d


if __name__ == '__main__':
    pass