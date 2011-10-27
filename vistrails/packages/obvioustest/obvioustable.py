import core.modules.module_registry
from core.modules.vistrails_module import Module, ModuleError
from obvious.data import DataFactory
from obvious.impl import TableImpl, SchemaImpl
from obviousx.io.impl import  CSVTableImport, ObviousTableModel
from java.lang import String, System, Integer
from javax.swing import JTable, JFrame

version = "0.0.1"
name = "ObviousTable"
identifier = "com.googlecode.obvious.data.obvioustable"

class ObviousTable(Module):
    """A test module integrating the Obvious toolkit """

    def compute(self):
        schema = SchemaImpl()
        #should fin a way to pass the schema through a port
        file = self.getInputConnector("file")
        try:
            dataFactoryName = self.getInputConnector("dataFactoryName")
            System.setProperty("obvious.DataFactory", dataFactoryName)
            factory = DataFactory.getInstance()
            table = factory.createTable(schema)
        except:
            table = TableImpl(schema)
        importer = CSVTableImport(file, table, ",")
        loadedtable = importer.loadTable()
        obviousTableModel = ObviousTableModel(loadedtable)
        jTable = JTable(obviousTableModel)
        frame = JFrame("An obvious table displayed as a JFrame on vistrails")
        frame.add(jTable)
        frame.pack()
        frame.setVisible(True)
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE)
        self.setResult("frame", frame)
    
def initialize(*args, **keywords):
    reg = core.modules.module_registry.registry
    reg.addModule(ObviousTable)
    reg.add_input_port(ObviousTable, "file",
                       (core.modules.basic_modules.File, "a csv file describing table content"))
    reg.add_input_port(ObviousTable, "dataFactoryName"
                       (core.modules.basic_modules.String, "name of the datafactory"))
    reg.add_output_port(ObviousTable, "frame",
                        (JFrame, "a Java swing JFrame containing a JTable"))