from vistrails.core.modules.vistrails_module import Module, ModuleError


class Table(Module):
    columns = None
    rows = None

    names = None

    def get_column(self, i): # pragma: no cover
        raise NotImplementedError


class ExtractColumn(Module):
    _input_ports = [
            ('table', Table),
            ('column_name', '(org.vistrails.vistrails.basic:String)',
             {'optional': True}),
            ('column_index', '(org.vistrails.vistrails.basic:Integer)',
             {'optional': True}),
            ('numeric', '(org.vistrails.vistrails.basic:Boolean)',
             {'optional': True, 'defaults': "['False']"})]
    _output_ports = [
            ('value', '(org.vistrails.vistrails.basic:List)')]

    def compute(self):
        table = self.getInputFromPort('table')
        if self.hasInputFromPort('column_index'):
            column_index = self.getInputFromPort('column_index')
        if self.hasInputFromPort('column_name'):
            name = self.getInputFromPort('column_name')
            if isinstance(name, unicode):
                name = name.encode('utf-8')
            if table.names is None:
                raise ModuleError("Unable to get column by names: table "
                                  "doesn't have column names")
            try:
                index = table.names.index(name)
            except ValueError:
                try:
                    name = name.strip()
                    index = table.column_names.index(name)
                except:
                    raise ModuleError(self, "Column name was not found")
            if self.hasInputFromPort('column_index'):
                if column_index != index:
                    raise ModuleError(self,
                                      "Both column_name and column_index were "
                                      "specified, and they don't agree")
        elif self.hasInputFromPort('column_index'):
            index = column_index
        else:
            raise ModuleError(self,
                              "You must set one of column_name or "
                              "column_index")

        result = table.get_column(
                index,
                numeric=self.getInputFromPort('numeric', allowDefault=True))

        self.setResult('value', result)


_modules = [(Table, {'abstract': True}), ExtractColumn]
