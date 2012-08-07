"""The module palette, from which modules can be added.

This palette is a hierarchical view of the modules available in the loaded
packages. These can be dragged and dropped on the pipeline view to add a new
module instance.
"""

from java.lang import Object as JavaObject
from java.awt.datatransfer import DataFlavor, Transferable
from javax.swing import JScrollPane, JTree, TransferHandler
from javax.swing.tree import DefaultMutableTreeNode

from com.vlsolutions.swing.docking import DockKey, Dockable

from core import get_vistrails_application
from core.modules.module_registry import get_module_registry


moduleData = DataFlavor(
        JavaObject,
        'X-Vistrails-Module; class=<java.lang.Object>')


class ModuleTransferable(Transferable):
    """The data that is dragged and dropped from the palette to the pipeline.
    """
    def __init__(self, descriptor):
        self.descriptor = descriptor
    
    # @Override
    def getTransferData(self, flavor):
        if flavor == moduleData:
            return self.descriptor
        else:
            return None
    
    # @Override
    def getTransferDataFlavors(self):
        return [moduleData]
    
    # @Override
    def isDataFlavorSupported(self, flavor):
        return flavor == moduleData


class ModuleTreeNode(DefaultMutableTreeNode):
    """A custom tree node that holds the module descriptor.
    """
    def __init__(self, descriptor):
        self.descriptor = descriptor
    
    # @Override
    def getAllowsChildren(self):
        return False
    
    # @Override
    def isLeaf(self):
        return True
    
    # @Override
    def toString(self):
        return self.descriptor.name


class NamespaceTreeNode(DefaultMutableTreeNode):
    """A custom tree node for namespaces inside a package.
    """
    def __init__(self, name):
        super(NamespaceTreeNode, self).__init__(name)
        self._namespaces = {} # name:str -> namespace:NamespaceTreeNode

    # @Override
    def getAllowsChildren(self):
        return True

    # @Override
    def isLeaf(self):
        return False

    def _findInsertionPoint(self, newChild, namespace=False):
        newLabel = newChild.toString()

        # We put the namespaces first
        if namespace:
            low = 0
            high = len(self._namespaces) - 1
        else:
            low = len(self._namespaces)
            high = self.getChildCount() - 1

        while low <= high:
            mid = (low + high)/2
            midVal = self.getChildAt(mid).toString()

            if midVal < newLabel:
                low = mid + 1
            elif newLabel < midVal:
                high = mid - 1
            else:
                return mid # key found
        return low # key not found

    # @Override
    def add(self, newChild):
        ns = isinstance(newChild, NamespaceTreeNode)
        idx = self._findInsertionPoint(newChild, namespace=ns)
        self.insert(newChild, idx)

    def get_namespace(self, names):
        try:
            ns = self._namespaces[names[0]]
        except KeyError:
            ns = NamespaceTreeNode(names[0])
            self.add(ns) # Overridden for sorting
            self._namespaces[names[0]] = ns
        if len(names) > 1:
            return ns.get_namespace(names[1:])
        else:
            return ns


class PackageTreeNode(NamespaceTreeNode):
    """A custom tree node for packages.
    """
    def __init__(self, name, identifier):
        super(PackageTreeNode, self).__init__(name)
        self.identifier = identifier


class SourceTransferHandler(TransferHandler):
    # @Override
    def getSourceActions(self, c):
        return TransferHandler.COPY
    
    # @Override
    def createTransferable(self, tree):
        node = tree.getSelectionPath().getLastPathComponent()
        if isinstance(node, ModuleTreeNode):
            return ModuleTransferable(node.descriptor)
        else:
            return None


class JModulePalette(JScrollPane, Dockable):
    """The module palette, that allows the addition of modules to the pipeline.
    """
    def __init__(self):
        self._key = DockKey('module_palette')

        self.root = DefaultMutableTreeNode("Available modules")
        self.tree = JTree(self.root)
        self.tree.setRootVisible(False)

        self.tree.setDragEnabled(True)
        self.tree.setTransferHandler(SourceTransferHandler())

        self.setViewportView(self.tree)
        self.setVerticalScrollBarPolicy(JScrollPane.VERTICAL_SCROLLBAR_ALWAYS)
        self.setHorizontalScrollBarPolicy(JScrollPane.HORIZONTAL_SCROLLBAR_NEVER)

        self.packages = {}
        self.modules = {}

    def connect_registry_signals(self):
        app = get_vistrails_application()
        app.register_notification('reg_new_package', self.newPackage)
        app.register_notification('reg_new_module', self.newModule)
        app.register_notification('reg_deleted_module', self.deletedModule)
        # Ignore that, we'll delete a package when it becomes empty
        #app.register_notification('reg_deleted_package', ...)
        app.register_notification('reg_show_module', self.showModule)
        app.register_notification('reg_hide_module', self.hideModule)
        app.register_notification('reg_module_updated', self.switchDescriptors)

    def newPackage(self, package_identifier, prepend=False):
        registry = get_module_registry()
        package_name = registry.packages[package_identifier].name

        try:
            # The package might already exist...
            return self.packages[package_identifier]
        except KeyError:
            # I don't know what this 'prepend' thing is about, I'll assume that we
            # have to honor it -- no automatic sorting of packages here

            package_item = PackageTreeNode(package_name, package_identifier)
            self.packages[package_identifier] = package_item
            # Add it at either the beginning or the end, as requested
            if prepend:
                self.root.insert(package_item, 0)
            else:
                self.root.add(package_item)

            self.tree.getModel().nodeStructureChanged(self.root)
            return package_item

    def newModule(self, descriptor, recurse=False):
        if not descriptor.module_abstract() and not descriptor.is_hidden:
            package_identifier = (
                    descriptor.ghost_identifier or
                    descriptor.identifier)
            if package_identifier not in self.packages:
                package_item = self.newPackage(package_identifier, True)
            else:
                package_item = self.packages[package_identifier]

            if descriptor.ghost_namespace is not None:
                namespace = descriptor.ghost_namespace
            else:
                namespace = descriptor.namespace
            if descriptor.namespace_hidden or not namespace:
                parent_item = package_item
            else:
                parent_item = package_item.get_namespace(namespace.split('|'))

            item = ModuleTreeNode(descriptor)
            self.modules[descriptor] = item
            parent_item.add(item) # Overridden for sorting
        if recurse:
            for child in descriptor.children:
                self.newModule(child, recurse)
        self.tree.getModel().nodeStructureChanged(self.root)

    def deletedModule(self, descriptor):
        try:
            obj = self.modules[descriptor]
            del self.modules[descriptor]
            parent = obj.getParent()
            obj.removeFromParent()
            obj = parent
            while (obj is not None and
                    obj.getChildCount() == 0 and
                    isinstance(obj, NamespaceTreeNode)):
                parent = obj.getParent()
                if isinstance(obj, PackageTreeNode):
                    del self.packages[obj.identifier]
                obj.removeFromParent()
                obj = parent
        except KeyError:
            pass
        self.tree.getModel().nodeStructureChanged(self.root)

    def showModule(self, descriptor):
        print "TODO : show_module"
        pass

    def hideModule(self, descriptor):
        print "TODO : hide_module"
        pass

    def switchDescriptors(self, old_descriptor, new_descriptor):
        print "TODO : module_updated"
        pass
    
    def link_registry(self):
        self.updateFromModuleRegistry()
        self.connect_registry_signals()

    def updateFromModuleRegistry(self):
        registry = get_module_registry()
        for package in registry.package_list:
            self.newPackage(package.identifier)
        self.newModule(registry.root_descriptor, True)

    # @Override
    def getDockKey(self):
        return self._key

    # @Override
    def getComponent(self, *args):
        if len(args) == 0:
            return self
        else:
            return JScrollPane.getComponent(self, *args)
