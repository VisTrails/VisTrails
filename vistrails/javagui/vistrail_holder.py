from core.vistrail.controller import VistrailController
from db.services.locator import BaseLocator
class VistrailHolder(object):
    def __init__(self):
        self._controllers = dict()

    def add(self, controller, locator):
        self._controllers[controller] = locator

    def remove(self, arg):
        del self._controllers[arg]

    def find_controller(self, arg):
        if isinstance(arg, VistrailController):
            if arg in self._controllers:
                return arg
        elif isinstance(arg, BaseLocator):
            for controller, locator in self._controllers.iteritems():
                if locator == arg:
                    return controller
        raise KeyError
