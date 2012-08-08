import bisect

from javax.swing import JMenu, JMenuItem

import core.system
from core.vistrail.controller import VistrailController
from core.vistrail.vistrail import Vistrail
from db.services.locator import BaseLocator


class VistrailSelectionMenuItem(JMenuItem):
    def __init__(self, controller, name, callback):
        self._controller = controller
        self._callback = callback
        JMenuItem.__init__(self, name)
        self.actionPerformed = self._action_performed

    def _action_performed(self, event):
        self._callback(self._controller)


class VistrailSelectionMenu(JMenu):
    def __init__(self, callback):
        JMenu.__init__(self, "Windows")
        self.callback = callback


class VistrailHolder(object):
    """Class holding all the currently opened vistrails.
    """
    def __init__(self):
        self._controllers = set()
        self._menus = list()

        self._names = list()
        self._items = dict() # controller -> name

    def add(self, controller, locator):
        self._controllers.add(controller)

        if (isinstance(controller.locator, BaseLocator) and
                controller.locator.short_name):
            name = controller.locator.short_name
        else:
            name = "Untitled%s" % core.system.vistrails_default_file_type()
        pos = bisect.bisect(self._names, name)
        self._names.insert(pos, name)
        self._items[controller] = name
        for menu in self._menus:
            item = VistrailSelectionMenuItem(controller, name, menu.callback)
            menu.insert(item, pos)

    def remove(self, arg):
        controller = self.find_controller(arg)
        self._controllers.remove(controller)
        name = self._items.pop(controller)
        for i, n in enumerate(self._names):
            if n == name:
                for menu in self._menus:
                    menu.remove(i)
                del self._names[i]
                break

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

    def create_jmenu(self, callback):
        menu = VistrailSelectionMenu(callback)

        for controller in self._controllers:
            menu.addController(controller)

        self._menus.append(menu)
        return menu
