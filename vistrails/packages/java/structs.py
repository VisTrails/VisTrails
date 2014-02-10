class XMLError(RuntimeError):
    pass


class Unserializable(object):
    TAG = None
    ATTRIBUTES = []
    CHILDREN = {}

    @classmethod
    def from_xml(cls, node):
        # Checks tag
        if node.tag != cls.TAG:
            raise XMLError("Unexpected element %r (expected %r)" % (node.tag,
                                                                    cls.TAG))
        instance = cls()

        # Reads attributes
        for attribute in cls.ATTRIBUTES:
            if isinstance(attribute, basestring):
                source = target = attribute
            else:
                source, target = attribute
            setattr(instance, target, node.attrib[source])

        # Reads children
        children_tag_map = dict(
                (nodeclass.TAG, (nodeclass, target))
                for nodeclass, target in cls.CHILDREN.iteritems())
        for target in cls.CHILDREN.itervalues():
            setattr(instance, target, [])
        for child in node:
            try:
                nodeclass, target = children_tag_map[child.tag]
            except KeyError:
                raise XMLError("Unexpected children element %r (while parsing "
                               "%r)" % (child.tag, cls.TAG))
            getattr(instance, target).append(nodeclass.from_xml(child))

        return instance


class ReadParam(Unserializable):
    TAG = 'Parameter'
    ATTRIBUTES = [
            'name',
            'type']
    CHILDREN = {}


class ReadConstructor(Unserializable):
    TAG = 'Constructor'
    ATTRIBUTES = []
    CHILDREN = {ReadParam: 'parameters'}


class ReadMethod(Unserializable):
    TAG = 'Method'
    ATTRIBUTES = [
            'name',
            ('static', 'is_static'),
            'return_type']
    CHILDREN = {ReadParam: 'parameters'}

    @classmethod
    def from_xml(cls, node):
        instance = super(cls, cls).from_xml(node)
        instance.is_static = instance.is_static != '0'
        return instance


class ReadClass(Unserializable):
    TAG = 'Class'
    ATTRIBUTES = [
            ('name', 'fullname'),
            'superclass',
            ('abstract', 'is_abstract')]
    CHILDREN = {
            ReadMethod: 'methods',
            ReadConstructor: 'constructors'}

    @classmethod
    def from_xml(cls, node):
        instance = super(cls, cls).from_xml(node)
        instance.is_abstract = instance.is_abstract != '0'
        return instance


class PackageInfos(Unserializable):
    TAG = 'JavaPackage'
    ATTRIBUTES = []
    CHILDREN = {ReadClass: 'classes'}

    @classmethod
    def from_xml(cls, node):
        instance = super(cls, cls).from_xml(node)
        # Turns the 'classes' attribute from a list to a dict
        instance.classes = dict((clasz.fullname, clasz)
                                for clasz in instance.classes)
        return instance
