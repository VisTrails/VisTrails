# Based on sphinxcontrib.napoleon
# http://google.github.io/styleguide/pyguide.html
"""google docstring parsing and formatting."""

import re
from sphinx.ext.napoleon.iterators import modify_iter


_directive_regex = re.compile(r'\.\. \S+::')
_field_parens_regex = re.compile(r'\s*(\w+)\s*\(\s*(.+?)\s*\)')


class GoogleDocstring(object):
    """Parse Google style docstrings.

    Convert Google style docstrings to reStructuredText.

    Parameters
    ----------
    docstring : str or list of str
        The docstring to parse, given either as a string or split into
        individual lines.
    config : sphinxcontrib.napoleon.Config or sphinx.config.Config, optional
        The configuration settings to use. If not given, defaults to the
        config object on `app`; or if `app` is not given defaults to the
        a new `sphinxcontrib.napoleon.Config` object.

        See Also
        --------
        :class:`sphinxcontrib.napoleon.Config`

    Other Parameters
    ----------------
    app : sphinx.application.Sphinx, optional
        Application object representing the Sphinx process.
    what : str, optional
        A string specifying the type of the object to which the docstring
        belongs. Valid values: "module", "class", "exception", "function",
        "method", "attribute".
    name : str, optional
        The fully qualified name of the object.
    obj : module, class, exception, function, method, or attribute
        The object to which the docstring belongs.
    options : sphinx.ext.autodoc.Options, optional
        The options given to the directive: an object with attributes
        inherited_members, undoc_members, show_inheritance and noindex that
        are True if the flag option of same name was given to the auto
        directive.

    Example
    -------
    >>> from sphinx.ext.napoleon import Config
    >>> config = Config(napoleon_use_param=True, napoleon_use_rtype=True)
    >>> docstring = '''One line summary.
    ...
    ... Extended description.
    ...
    ... Args:
    ...   arg1(int): Description of `arg1`
    ...   arg2(str): Description of `arg2`
    ... Returns:
    ...   str: Description of return value.
    ... '''
    >>> print(GoogleDocstring(docstring, config))
    One line summary.
    <BLANKLINE>
    Extended description.
    <BLANKLINE>
    :param arg1: Description of `arg1`
    :type arg1: int
    :param arg2: Description of `arg2`
    :type arg2: str
    <BLANKLINE>
    :returns: Description of return value.
    :rtype: str

    """
    def __init__(self, docstring, config=None, app=None, what='', name='',
                 obj=None, options=None):
        self._config = config
        self._app = app
        if not self._config:
            from sphinx.ext.napoleon import Config
            self._config = self._app and self._app.config or Config()
        self._what = what
        self._name = name
        self._obj = obj
        self._opt = options
        if isinstance(docstring, str):
            docstring = docstring.splitlines()
        self._lines = docstring
        self._line_iter = modify_iter(docstring, modifier=lambda s: s.rstrip())
        self._parsed_lines = []
        self._is_in_section = False
        self._section_indent = 0
        if not hasattr(self, '_directive_sections'):
            self._directive_sections = []
        if not hasattr(self, '_sections'):
            self._sections = {
                'args': self._parse_parameters_section,
                'arguments': self._parse_parameters_section,
                'attributes': self._parse_attributes_section,
                'keyword args': self._parse_keyword_arguments_section,
                'keyword arguments': self._parse_keyword_arguments_section,
                'methods': self._parse_methods_section,
                'other parameters': self._parse_parameters_section,
                'parameters': self._parse_parameters_section,
                'return': self._parse_returns_section,
                'returns': self._parse_returns_section,
            }

        self.arguments = []
        self.attributes = []
        self.kwargs = []
        self.methods = []
        self.returns = []

        self._parse()

    def __str__(self):
        """Return the parsed docstring in reStructuredText format.

        Returns
        -------
        str
            UTF-8 encoded version of the docstring.

        """
        return str(self).encode('utf-8')

    def __unicode__(self):
        """Return the parsed docstring in reStructuredText format.

        Returns
        -------
        unicode
            Unicode version of the docstring.

        """
        return '\n'.join(self.lines())

    def lines(self):
        """Return the parsed lines of the docstring in reStructuredText format.

        Returns
        -------
        list of str
            The lines of the docstring in a list.

        """
        return self._parsed_lines

    def _consume_indented_block(self, indent=1):
        lines = []
        line = self._line_iter.peek()
        while(not self._is_section_break()
              and (not line or self._is_indented(line, indent))):
            lines.append(next(self._line_iter))
            line = self._line_iter.peek()
        return lines

    def _consume_contiguous(self):
        lines = []
        while (self._line_iter.has_next()
               and self._line_iter.peek()
               and not self._is_section_header()):
            lines.append(next(self._line_iter))
        return lines

    def _consume_empty(self):
        lines = []
        line = self._line_iter.peek()
        while self._line_iter.has_next() and not line:
            lines.append(next(self._line_iter))
            line = self._line_iter.peek()
        return lines

    def _consume_field(self, parse_type=True, prefer_type=False):
        line = next(self._line_iter)
        _name, _, _desc = line.partition(':')
        _name, _type, _desc = _name.strip(), '', _desc.strip()
        match = _field_parens_regex.match(_name)
        if parse_type and match:
            _name = match.group(1)
            _type = match.group(2)
        if prefer_type and not _type:
            _type, _name = _name, _type
        indent = self._get_indent(line) + 1
        _desc = [_desc] + self._dedent(self._consume_indented_block(indent))
        _desc = self.__class__(_desc, self._config).lines()
        return _name, _type, _desc

    def _consume_fields(self, parse_type=True, prefer_type=False):
        self._consume_empty()
        fields = []
        while not self._is_section_break():
            _name, _type, _desc = self._consume_field(parse_type, prefer_type)
            if _name or _type or _desc:
                fields.append((_name, _type, _desc,))
        return fields

    def _consume_returns_section(self):
        lines = self._dedent(self._consume_to_next_section())
        if lines:
            if ':' in lines[0]:
                _type, _, _desc = lines[0].partition(':')
                _name, _type, _desc = '', _type.strip(), _desc.strip()
                match = _field_parens_regex.match(_type)
                if match:
                    _name = match.group(1)
                    _type = match.group(2)
                lines[0] = _desc
                _desc = lines
            else:
                _name, _type, _desc = '', '', lines
            _desc = self.__class__(_desc, self._config).lines()
            return [(_name, _type, _desc,)]
        else:
            return []

    def _consume_section_header(self):
        section = next(self._line_iter)
        stripped_section = section.strip(':')
        if stripped_section.lower() in self._sections:
            section = stripped_section
        return section

    def _consume_to_next_section(self):
        self._consume_empty()
        lines = []
        while not self._is_section_break():
            lines.append(next(self._line_iter))
        return lines + self._consume_empty()

    def _dedent(self, lines, full=False):
        if full:
            return [line.lstrip() for line in lines]
        else:
            min_indent = self._get_min_indent(lines)
            return [line[min_indent:] for line in lines]

    def _format_admonition(self, admonition, lines):
        lines = self._strip_empty(lines)
        if len(lines) == 1:
            return ['.. %s:: %s' % (admonition, lines[0].strip()), '']
        elif lines:
            lines = self._indent(self._dedent(lines), 3)
            return ['.. %s::' % admonition, ''] + lines + ['']
        else:
            return ['.. %s::' % admonition, '']

    def _format_block(self, prefix, lines, padding=None):
        if lines:
            if padding is None:
                padding = ' ' * len(prefix)
            result_lines = []
            for i, line in enumerate(lines):
                if line:
                    if i == 0:
                        result_lines.append(prefix + line)
                    else:
                        result_lines.append(padding + line)
                else:
                    result_lines.append('')
            return result_lines
        else:
            return [prefix]

    def _format_field(self, _name, _type, _desc):
        separator = any([s for s in _desc]) and ' --' or ''
        if _name:
            if _type:
                field = ['**%s** (*%s*)%s' % (_name, _type, separator)]
            else:
                field = ['**%s**%s' % (_name, separator)]
        elif _type:
            field = ['*%s*%s' % (_type, separator)]
        else:
            field = []
        return field + _desc

    def _format_fields(self, field_type, fields):
        field_type = ':%s:' % field_type.strip()
        padding = ' ' * len(field_type)
        multi = len(fields) > 1
        lines = []
        for _name, _type, _desc in fields:
            field = self._format_field(_name, _type, _desc)
            if multi:
                if lines:
                    lines.extend(self._format_block(padding + ' * ', field))
                else:
                    lines.extend(self._format_block(field_type + ' * ', field))
            else:
                lines.extend(self._format_block(field_type + ' ', field))
        return lines

    def _get_current_indent(self, peek_ahead=0):
        line = self._line_iter.peek(peek_ahead + 1)[peek_ahead]
        while line != self._line_iter.sentinel:
            if line:
                return self._get_indent(line)
            peek_ahead += 1
            line = self._line_iter.peek(peek_ahead + 1)[peek_ahead]
        return 0

    def _get_indent(self, line):
        for i, s in enumerate(line):
            if not s.isspace():
                return i
        return len(line)

    def _get_min_indent(self, lines):
        min_indent = None
        for line in lines:
            if line:
                indent = self._get_indent(line)
                if min_indent is None:
                    min_indent = indent
                elif indent < min_indent:
                    min_indent = indent
        return min_indent or 0

    def _indent(self, lines, n=4):
        return [(' ' * n) + line for line in lines]

    def _is_indented(self, line, indent=1):
        for i, s in enumerate(line):
            if i >= indent:
                return True
            elif not s.isspace():
                return False
        return False

    def _is_section_header(self):
        section = self._line_iter.peek().lower()
        if section.strip(':') in self._sections:
            header_indent = self._get_indent(section)
            section_indent = self._get_current_indent(peek_ahead=1)
            return section_indent > header_indent
        elif self._directive_sections:
            if _directive_regex.match(section):
                for directive_section in self._directive_sections:
                    if section.startswith(directive_section):
                        return True
        return False

    def _is_section_break(self):
        line = self._line_iter.peek()
        return (not self._line_iter.has_next()
                or self._is_section_header()
                or (self._is_in_section
                    and line
                    and not self._is_indented(line, self._section_indent)))

    def _parse(self):
        self._parsed_lines = self._consume_empty()
        while self._line_iter.has_next():
            if self._is_section_header():
                try:
                    section = self._consume_section_header()
                    self._is_in_section = True
                    self._section_indent = self._get_current_indent()
                    if _directive_regex.match(section):
                        lines = [section] + self._consume_to_next_section()
                    else:
                        lines = self._sections[section.lower()](section)
                finally:
                    self._is_in_section = False
                    self._section_indent = 0
            else:
                if not self._parsed_lines:
                    lines = self._consume_contiguous() + self._consume_empty()
                else:
                    lines = self._consume_to_next_section()
            self._parsed_lines.extend(lines)

    def _parse_attributes_section(self, section):
        self.attributes.extend(self.join_docs(self._consume_fields()))
        return 'attributes\n'

    def _parse_keyword_arguments_section(self, section):
        self.arguments.extend(self.join_docs(self._consume_fields()))
        return 'arguments\n'


    def _parse_methods_section(self, section):
        self.methods.extend(self.join_docs(self._consume_fields(parse_type=False)))
        return 'methods\n'

    def _parse_parameters_section(self, section):
        self.arguments.extend(self.join_docs(self._consume_fields()))
        return 'arguments\n'

    def _parse_returns_section(self, section):
        self.returns.extend(self.join_docs(self._consume_fields()))
        return 'returns\n'

    def _strip_empty(self, lines):
        if lines:
            start = -1
            for i, line in enumerate(lines):
                if line:
                    start = i
                    break
            if start == -1:
                lines = []
            end = -1
            for i in reversed(range(len(lines))):
                line = lines[i]
                if line:
                    end = i
                    break
            if start > 0 or end + 1 < len(lines):
                lines = lines[start:end + 1]
        return lines

    def join_docs(self, attributes):
        new_doc = [(a, b, (c if isinstance(c, basestring) else '\n'.join(c)))
                   for a, b, c in attributes]
        return new_doc

if __name__ == "__main__":
    import pydoc
#    from bokeh.charts import BoxPlot
#    docstring = pydoc.getdoc(BoxPlot)
    from tensorflow import reduce_all
    docstring = pydoc.getdoc(reduce_all)
    print docstring
    d = GoogleDocstring(docstring)

    print d.attributes, d.arguments, d.returns