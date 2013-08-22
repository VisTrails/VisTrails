# Here we have two different schemes:
#
# * We can send the serialized module over to the engine, like we do with
# multiprocessing. This is reliable.
#
# * Or we can build a fake module object with the getInputFromPort()/... and
# setResult() methods and execute that. This only works if the module doesn't
# use additional methods in its Module subclass or any of VisTrails features
# (since we don't use VisTrails on the remote side).
# This allows to execute a simple piece of code without the need for VisTrails
# to be installed on every machine.

from .engine_manager import EngineManager

from .default import IPythonScheme
from .standalone import IPythonStandaloneScheme
