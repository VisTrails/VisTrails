from vistrails.core.modules.vistrails_module import ModuleError

from common import TableObject, Table, InternalModuleError

# FIXME use pandas?

class JoinedTables(TableObject):
    def __init__(self, left_t, right_t, left_key_col, right_key_col,
                 case_sensitive=False, always_prefix=False):
        self.left_t = left_t
        self.right_t = right_t
        self.left_key_col = left_key_col
        self.right_key_col = right_key_col
        self.case_sensitive = case_sensitive
        self.always_prefix = always_prefix

        self.build_column_names()

        self._rows = None
        self.row_map = None
        self.column_cache = {}

    def build_column_names(self):
        left_name = self.left_t.name
        if left_name is None:
            left_name = "left"
        right_name = self.right_t.name
        if right_name is None:
            right_name = "right"

        def get_col_names(table, other, prefix):
            names = []
            for i in xrange(table.columns):
                should_prefix = self.always_prefix
                if table.names is not None:
                    n = table.names[i]
                else:
                    n = "col %d" % i
                    should_prefix = True
                if not should_prefix and other.names is not None:
                    if n in other.names:
                        should_prefix = True
                names.append("%s%s" % (prefix + "." if should_prefix else "",
                                       n))
            return names

        self.names = (get_col_names(self.left_t, self.right_t, left_name) +
                      get_col_names(self.right_t, self.left_t, right_name))
        self.columns = len(self.names)

    def get_column(self, index, numeric=False):
        if (index, numeric) in self.column_cache:
            return self.column_cache[(index, numeric)]

        if self.row_map is None:
            self.compute_row_map()

        result = []        
        if index < self.left_t.columns:
            column = self.left_t.get_column(index)
            for i in xrange(self.left_t.rows):
                if i in self.row_map:
                    result.append(column[i])
        else:
            column = self.right_t.get_column(index - self.left_t.columns)
            for i in xrange(self.left_t.rows):
                if i in self.row_map:
                    j = self.row_map[i]
                    result.append(column[j])

        if numeric:
            result = [float(x) for x in result]

        self.column_cache[(index, numeric)] = result
        return result

    def compute_row_map(self):
        def build_key_dict(table, key_col):
            key_dict = {}
            if self.case_sensitive:
                key_dict = dict((val.strip(), i) for i, val in 
                                enumerate(table.get_column(key_col)))
            else:
                key_dict = dict((val.strip().upper(), i) for i, val in
                                enumerate(table.get_column(key_col)))
            return key_dict

        right_keys = build_key_dict(self.right_t, self.right_key_col)
        print 'right_keys:', right_keys
        
        new_data = []
        self.row_map = {}
        for left_row_idx, key in enumerate(
                self.left_t.get_column(self.left_key_col)):
            if (self.case_sensitive and key.strip() in right_keys):
                self.row_map[left_row_idx] = right_keys[key.strip()]
            elif (not self.case_sensitive and key.strip().upper() in right_keys):
                self.row_map[left_row_idx] = right_keys[key.strip().upper()]
        print "ROW MAP:", self.row_map

    @property
    def rows(self):
        if self._rows is not None:
            return self._rows
        self.compute_row_map()
        return len(self.row_map)

class JoinTables(Table):
    _input_ports = [('left_table', 'Table'),
                    ('right_table', 'Table'),
                    ('left_column_idx', 'basic:Integer'),
                    ('left_column_name', 'basic:String'),
                    ('right_column_idx', 'basic:Integer'),
                    ('right_column_name', 'basic:String'),
                    ('case_sensitive', 'basic:Boolean',
                     {"optional": True, "defaults": str(["False"])}),
                    ('always_prefix', 'basic:Boolean',
                     {"optional": True, "defaults": str(["False"])})]
    _output_ports = [('value', 'Table')]

    def compute(self):
        left_t = self.get_input('left_table')
        right_t = self.get_input('right_table')
        case_sensitive = self.get_input('case_sensitive')
        always_prefix = self.get_input('always_prefix')

        def get_column_idx(table, prefix):
            col_name_port = "%s_column_name" % prefix
            col_idx = None
            if self.has_input(col_name_port):
                col_name = self.get_input(col_name_port)
                try:
                    if table.names is None:
                        raise ValueError
                    col_idx = table.names.index(col_name)
                except ValueError:
                    raise ModuleError(self, '%s_table does not contain column '
                                      '"%s"' % (prefix, col_name))
            col_idx_port = '%s_column_idx' % prefix
            if self.has_input(col_idx_port):
                port_col_idx = self.get_input(col_idx_port)
                if col_idx is not None and col_idx != port_col_idx:
                    raise ModuleError(self,
                                      "Both %s_column_name and "
                                      "%s_column_index were "
                                      "specified, and they don't agree" %
                                      (prefix, prefix))
                else:
                    col_idx = port_col_idx
            if col_idx is None:
                raise ModuleError(self, "You must set one of %s_column_name "
                                  "or %s_column_index" % (prefix, prefix))

            return col_idx

        left_key_col = get_column_idx(left_t, "left")
        right_key_col = get_column_idx(right_t, "right")

        table = JoinedTables(left_t, right_t, left_key_col, right_key_col,
                             case_sensitive, always_prefix)
        self.set_output('value', table)
                    
_modules = [JoinTables]
