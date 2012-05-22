from zipfile import ZipFile
from core import debug


class JavaParser(object):
    """This class parses a Java source file to find the method signatures.
    """
    class Error(Exception):
        pass

    def __init__(self, file, filename):
        self._file = file
        self.filename = filename
        self.name = filename[:-5].replace('/', '.')
        self._stored = None
        self._line = 1
        self._last = None

    @staticmethod
    def _shortname(name):
        """Return the last component of a name.

        >>> JavaParser._shortname('java.lang.String')
        'String'
        >>> JavaParser._shortname('long')
        'long'
        """
        try:
            pos = name.rindex('.')
            return name[pos+1:]
        except ValueError:
            return name


    ################
    # Lexer stuff
    #

    def _read(self):
        if self._stored is None:
            c = self._file.read(1)
            if c == '\r' or (c == '\n' and self._last != '\r'):
                self._line += 1
            self._last = c
            return c or None
        else:
            c = self._stored
            self._stored = None
            return c

    def _unread(self, c):
        assert self._stored is None, "Internal parser error: _unread"
        self._stored = c

    def _skip_multiline_comment(self):
        b = self._read()
        last = False
        while True:
            if b is None:
                return
            elif b == '*':
                last = True
            elif b == '/' and last:
                return
            else:
                last = False
            b = self._read()

    def _skip_line(self):
        b = self._read()
        while True:
            if b == '\n':
                return # UNIX end-of-line
            elif b == '\r':
                n = self._read()
                if n == '\n':
                    return # Windows end-of-line
                else:
                    self._unread(n)
                    return # Mac end-of-line
            b = self._read()

    @staticmethod
    def _char_identifier(c, first):
        # Note that we also include '.' in the identifier
        return ('a' <= c <= 'z' or
                'A' <= c <= 'Z' or
                c == '_' or c == '$' or
                (not first and ('0' <= c <= '9' or c == '.')))

    def _next_token(self, throw=False, full_types=True):
        """Lexer method.
        """
        b = self._read()
        while b is not None:
            if b in ' \t\n\r':
                pass
            elif b == '"' or b == "'":
                n = self._read()
                while n != b:
                    if n is None:
                        raise JavaParser.Error("error matching %s%s" % (b, b))
                    elif n == '\\':
                        self._read()
                    n = self._read()
                return '""'
            elif b == '/':
                n = self._read()
                if n == '*':
                    self._skip_multiline_comment()
                elif n == '/':
                    self._skip_line()
                else:
                    # We shouldn't stumble on this outside of method
                    # definitions...
                    self._unread(n)
            # Keyword or identifier
            elif JavaParser._char_identifier(b, first=True):
                word = b
                n = self._read()
                while JavaParser._char_identifier(n, first=False):
                    word += n
                    n = self._read()
                if not full_types or word in JavaParser._MODIFIERS:
                    self._unread(n)
                    return word
                else:
                    # Let's try to find some [] (array type) or <> (template
                    # parameters)
                    while n in ' \t\n\r':
                        n = self._read()
                    if n == '[':
                        while n == '[':
                            n = self._read()
                            while n in ' \t\n\r':
                                n = self._read()
                            if n == ']':
                                word += '[]'
                                n = self._read()
                                while n in ' \t\n\r':
                                    n = self._read()
                            else:
                                raise JavaParser.Error("error matching []")
                        self._unread(n)
                        return word
                    elif n == '<':
                        open_line = self._line
                        word += '<'
                        depth = 1
                        n = self._read()
                        while depth > 0:
                            if n is None:
                                raise JavaParser.Error(
                                        "error matching <> ; started at line "
                                        "%d" % open_line)
                            elif n == '<':
                                depth += 1
                            elif n == '>':
                                depth -= 1
                            word += n
                            n = self._read()
                        self._unread(n)
                        return word
                    else:
                        # This is something else - keep it for later
                        self._unread(n)
                        return word
            # Ponctuation and whatnot
            else:
                return b
            # This is really simplified because we don't need to parse Java
            # code, only the declarations
            b = self._read()
        if throw:
            raise JavaParser.Error("Unexpected end-of-file")


    ################
    # Parser stuff
    #

    def _skip_statement(self):
        # A statement might contain blocks, because of anonymous classes...
        n = self._next_token(throw=True, full_types=False)
        depth = 0
        while depth > 0 or n != ';':
            if n == '{':
                depth += 1
            elif n == '}':
                depth -= 1
            n = self._next_token(throw=True, full_types=False)

    def _skip_block(self, depth = 1):
        while depth > 0:
            token = self._next_token(throw=True, full_types=False)
            if token == '{':
                depth += 1
            elif token == '}':
                depth -= 1

    def _skip_template_declaration(self, depth = 1):
        while depth > 0:
            token = self._next_token(throw=True, full_types=False)
            if token == '<':
                depth += 1
            elif token == '>':
                depth -= 1

    _MODIFIERS = set(['public', 'private', 'protected',
                     'static', 'final',
                     'abstract', 'native', 'synchronized',
                     'transient', 'volatile'])

    def parse(self):
        """Parser method.
        """
        classes = dict()
        token = self._next_token()
        stack = []
        modifiers = set()
        package = None
        while token is not None:
            # Package declaration
            if token == 'package':
                package = ''
                token = self._next_token(throw=True)
                while token != ';':
                    package += token
                    token = self._next_token(throw=True)
            # Import statement
            elif token == 'import':
                self._skip_statement()
            # Some kind of template parameter
            elif token == '<':
                self._skip_template_declaration()
                modifiers.add('template')
            # Some modifiers before a declaration
            elif token in JavaParser._MODIFIERS:
                modifiers.add(token)
            # Enum definition
            elif token == 'enum':
                enumname = self._next_token(throw=True)
                token = self._next_token(throw=True)
                if token != '{':
                    raise JavaParser.Error("invalid enum definition")
                self._skip_block()
            # Class definition
            elif token == 'class' or token == 'interface':
                interface = (token == 'interface')
                classname = self._next_token(throw=True)

                # Fix the class name: remove template parameters
                try:
                    pos = classname.index('<')
                except ValueError:
                    # No template parameters
                    template = False
                else:
                    classname = classname[:pos]
                    template = True

                if not stack:
                    if package + '.' + classname == self.name and interface:
                        return dict()
                # Build the full classname
                fullclassname = package
                for c in stack:
                    fullclassname += '.' + c['name']
                fullclassname += '.' + classname
                # Read the inheritance stuff
                token = self._next_token(throw=True)
                mode = None
                extends = None
                implements = set()
                while token != '{':
                    if token == 'extends':
                        mode = 'e'
                    elif token == 'implements':
                        mode = 'i'
                    elif token == ',':
                        pass
                    elif mode == 'e':
                        if extends is not None:
                            raise JavaParser.Error("Multiple parent classes")
                        extends = JavaParser._shortname(token)
                    elif mode == 'i':
                        implements.add(JavaParser._shortname(token))
                    token = self._next_token(throw=True)
                stack.append({'name': classname,
                              'fullname': fullclassname,
                              'filename': self.filename,
                              'line': self._line,
                              'interface': interface,
                              'template': template,
                              'modifiers': modifiers,
                              'extends': extends,
                              'implements': implements,
                              'methods': []})
                modifiers = set()
            # A static block or other block things
            elif token == '{':
                self._skip_block()
            # Useless stuff
            elif token == ';':
                pass
            # End of class definition
            elif token == '}':
                # Pop it from the stack and add it to the dict
                try:
                    c = stack.pop()
                    # Skip top-level classes
                    if stack or c['fullname'] == self.name:
                        classes[c['fullname']] = c
                except IndexError:
                    raise JavaParser.Error("found trailing '}' on line %d" %
                                           self._line)
            # Annotation
            elif token == '@':
                self._next_token(throw=True)
            # Some kind of identifier (type or constructor name)
            # -> method or field declaration
            else:
                if not stack:
                    raise JavaParser.Error("found method/field outside of "
                                           "class definition on line %d" %
                                           self._line)
                id1 = token
                id2 = self._next_token(throw=True)
                m_name = None
                if id2 == '(':
                    # This is a constructor: MyClass(...
                    m_type = None
                    m_name = id1
                else:
                    id3 = self._next_token(throw=True)
                    if id3 == '(':
                        # This is a method: type myMethod(...
                        m_type = id1
                        m_name = id2
                    elif id3 == ';':
                        # This is a field: type myField;
                        pass
                    elif id3 == '=':
                        # This is an initialized field: type myField = ...
                        self._skip_statement()
                    elif id3 == ',':
                        self._skip_statement()
                    else:
                        raise JavaParser.Error(
                                "unknown declaration on line %d" % self._line)
                # If we found some kind of method...
                if m_name is not None:
                    params = self._read_params()
                    if m_type is not None:
                        m_type = JavaParser._shortname(m_type)
                    stack[-1]['methods'].append({
                            'name': m_name,
                            'modifiers': modifiers,
                            'type': m_type,
                            'params': params})
                    token = self._next_token(throw = True)
                    while True:
                        if token == ';':
                            # No body
                            break
                        elif token == '{':
                            # Skip the body...
                            self._skip_block()
                            break
                        # There might be some stuff, like throws declarations here
                        token = self._next_token()
                modifiers = set()
            token = self._next_token()
        return classes

    def _read_params(self):
        params = []
        last = None
        token = self._next_token(throw=True)
        while token != ')':
            last = token
            token = self._next_token(throw=True)
            if token == ',' or token == ')':
                params.append(last)
        return params


def parse_jar(filename, dir):
    if dir and not dir.endswith('/'):
        dir = dir + '/'
    zip = ZipFile(filename)
    entries = zip.infolist()

    parsed_classes = dict()

    # zipfile.ZipFile#open() was introduced in 2.6
    try:
        zip.open
    except AttributeError:
        import StringIO
        def open_workaround(filename):
            return StringIO.StringIO(zip.read(filename))
        zip.open = open_workaround

    for entry in entries:
        filename = entry.filename
        if filename.startswith(dir) and filename.endswith('.java'):
            f = zip.open(filename)
            filename = filename[len(dir):]
            parser = JavaParser(f, filename)
            try:
                classes = parser.parse()
            except JavaParser.Error, e:
                debug.warning("couldn't parse %s from the Weka sources: %s" % (
                              filename, e))
            else:
                for name, klass in classes.iteritems():
                    try:
                        prev = parsed_classes[name]
                        debug.warning(
                                "found duplicate class %s:\n"
                                "  %s line %d\n"
                                "  %s line %d\n" % (
                                        name,
                                        klass['filename'], klass['line'],
                                        prev['filename'], prev['line']))
                    except KeyError:
                        parsed_classes[name] = klass
                print("parsed %s" % filename)
            finally:
                f.close()
    zip.close()


if __name__ == '__main__':
    debug.DebugPrint.getInstance().set_message_level(debug.DebugPrint.Log)

    import doctest
    doctest.testmod()

    parse_jar('C:\\Program Files (x86)\\Weka-3-6\\weka-src.jar',
              'src/main/java')
