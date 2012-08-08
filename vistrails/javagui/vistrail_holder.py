from core.vistrail.controller import VistrailController
from core.vistrail.vistrail import Vistrail
from db.services.locator import BaseLocator


class VistrailHolder(object):
    """Class holding all the currently opened vistrails.
    """
    def __init__(self):
        self._controllers = set()

    def add(self, controller, locator):
        self._controllers.add(controller)

    def remove(self, arg):
        self._controllers.remove(arg)

    def find_controller(self, arg):
        """Find the controller for an already opened vistrail.

        The argument might be either a controller, a locator or a vistrail.
        KeyError is raised if there is no matching opened controller.
        """
        if isinstance(arg, VistrailController):
            if arg in self._controllers:
                return arg
        elif isinstance(arg, BaseLocator):
            for controller in self._controllers:
                if controller.locator == arg:
                    return controller
        elif isinstance(arg, Vistrail):
            for controller in self._controllers:
                if controller.vistrail == arg:
                    return controller
        raise KeyError

    def __iter__(self):
        return iter(self._controllers)

    def empty(self):
        return not self._controllers
