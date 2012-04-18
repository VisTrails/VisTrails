from core.modules.vistrails_module import Module
# from obvious.data import DataFactory
# from obvious.impl import TableImpl, SchemaImpl
# from obviousx.io.impl import CSVTableImport, ObviousTableModel
# from java.lang import System
# from javax.swing import JTable, JFrame

class ObviousTable(Module):
    """A test module integrating the Obvious toolkit """

    def compute(self):
        # schema = SchemaImpl()
        # # Should find a way to pass the schema through a port
        # file = self.getInputConnector('file')
        # try:
        #     dataFactoryName = self.getInputConnector('dataFactoryName')
        #     System.setProperty('obvious.DataFactory', dataFactoryName)
        #     factory = DataFactory.getInstance()
        #     table = factory.createTable(schema)
        # except:
        #     table = TableImpl(schema)
        # importer = CSVTableImport(file, table, ",")
        # loadedtable = importer.loadTable()
        # obviousTableModel = ObviousTableModel(loadedtable)
        # jTable = JTable(obviousTableModel)
        # self.setResult('table', jTable)
        # frame = JFrame("An obvious table displayed as a JFrame on vistrails")
        # frame.add(jTable)
        # frame.pack()
        # frame.setVisible(True)
        # frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE)
        # self.setResult('frame', frame)
        self.setResult('table', '!!table!!')
        self.setResult('frame', '!!frame!!')
