import copy

from core.application import get_vistrails_application
from core.inspector import PipelineInspector
from core.interpreter.default import get_default_interpreter
from core.modules.module_registry import get_module_registry
from core.utils import DummyView
from core.vistrail.controller import VistrailController
from extras.java_vm import get_java_vm, implement


_JAVA_VM = get_java_vm()

Spreadsheet = _JAVA_VM.edu.utah.sci.vistrails.javaspreadsheet.Spreadsheet


class SpreadsheetInterfaceImpl(object):
    """This interface is called back by the UI to perform VisTrails actions.
    """
    # @Override
    def executePipelineToCell(self, infos, dst_sheet, dst_loc):
        try:
            infos = CellInfos.getInfos(infos)
            pipeline = infos['pipeline']
            if pipeline is None:
                return False
            mod_id = infos['module_id']
            pipeline = assignPipelineCellLocations(
                    pipeline,
                    dst_sheet,
                    dst_loc,
                    [mod_id])
            interpreter = get_default_interpreter()
            interpreter.execute(
                    pipeline,
                    locator=infos['locator'],
                    current_version=infos['version'],
                    view=DummyView(),
                    actions=infos['actions'],
                    reason=infos['reason'],
                    sinks=[mod_id])
            return True
        except Exception:
            import traceback
            traceback.print_exc()
            return False

    # @Override
    def select_version(self, infos):
        infos = CellInfos.getInfos(infos)
        app = get_vistrails_application()
        return app.select_vistrail(infos['locator'], infos['version'])
SpreadsheetInterfaceImpl = implement(
        'edu.utah.sci.vistrails.javaspreadsheet.SpreadsheetInterface')(
        SpreadsheetInterfaceImpl)


# This is an adaptation of packages.spreadsheet.spreadsheet_execute
# FIXME : there must be a better way to do this
def assignPipelineCellLocations(pipeline, sheetName, 
                                dst_loc, modules=[]):
    """ assignPipelineCellLocations(pipeline: Pipeline, sheetName: str,
                                    dst_loc: (int, int),
                                    modules: [ids]) -> Pipeline                                  
    Modify the pipeline to have its cells (provided by modules) to
    be located at the specified location on this sheet.
    """
    col, row = dst_loc.x, dst_loc.y

    reg = get_module_registry()
    # These are the modules we need to edit
    spreadsheet_cell_desc = \
        reg.get_descriptor_by_name('edu.utah.sci.vistrails.javaspreadsheet',
                                   'AssignCell')

    create_module = VistrailController.create_module_static
    create_function = VistrailController.create_function_static
    create_connection = VistrailController.create_connection_static

    pipeline = copy.copy(pipeline)
    root_pipeline = pipeline
    if modules is None:
        inspector = PipelineInspector()
        inspector.inspect_spreadsheet_cells(pipeline)
        inspector.inspect_ambiguous_modules(pipeline)
        modules = inspector.spreadsheet_cells

    for id_list in modules:
        # find at which depth we need to be working
        try:                
            id_iter = iter(id_list)
            m = pipeline.modules[id_iter.next()]
            for mId in id_iter:
                pipeline = m.pipeline
                m = pipeline.modules[mId]
        except TypeError:
            mId = id_list

        m = pipeline.modules[mId]
        if not reg.is_descriptor_subclass(m.module_descriptor, 
                                          spreadsheet_cell_desc):
            continue

        # Walk through all connections and remove all CellLocation
        # modules connected to this spreadsheet cell
        conns_to_delete = []
        for conn_id, c in pipeline.connections.iteritems():
            if (c.destinationId==mId and pipeline.modules[c.sourceId].name in
                    ('CellLocation', 'SheetReference')):
                conns_to_delete.append(c.id)
        for c_id in conns_to_delete:
            pipeline.delete_connection(c_id)

        # a hack to first get the id_scope to the local pipeline scope
        # then make them negative by hacking the getNewId method
        # all of this is reset at the end of this block
        id_scope = pipeline.tmp_id
        orig_getNewId = pipeline.tmp_id.__class__.getNewId
        def getNewId(self, objType):
            return -orig_getNewId(self, objType)
        pipeline.tmp_id.__class__.getNewId = getNewId

        # Add a sheet reference with a specific name
        sheetReference = create_module(
                id_scope,
                'edu.utah.sci.vistrails.javaspreadsheet', 'SheetReference')
        sheetNameFunction = create_function(id_scope, sheetReference, 
                                            'sheet', [str(sheetName)])
        sheetReference.add_function(sheetNameFunction)

        # Add a cell location module with a specific row and column
        cellLocation = create_module(id_scope, 
                                     "edu.utah.sci.vistrails.javaspreadsheet",
                                     "CellLocation")
        rowFunction = create_function(id_scope, cellLocation, "row", [str(row)])
        colFunction = create_function(id_scope, cellLocation, "column", 
                                      [str(col)])

        cellLocation.add_function(rowFunction)
        cellLocation.add_function(colFunction)

        cell_module = pipeline.get_module_by_id(mId)
        # Then connect the SheetReference to the AssignCell
        sheet_conn = create_connection(id_scope, sheetReference, 'reference',
                                       cell_module, 'sheet')
        # Then connect the CellLocation to the spreadsheet cell
        cell_conn = create_connection(id_scope, cellLocation, 'location',
                                      cell_module, 'location')

        pipeline.add_module(sheetReference)
        pipeline.add_module(cellLocation)
        pipeline.add_connection(sheet_conn)
        pipeline.add_connection(cell_conn)
        # replace the getNewId method
        pipeline.tmp_id.__class__.getNewId = orig_getNewId

    return root_pipeline


class SheetReferenceImpl(object):
    def __init__(self, name=None):
        self.__name = name

    # @Override
    def getName(self):
        return self.__name
SheetReferenceImpl = implement(
        'edu.utah.sci.vistrails.javaspreadsheet.SheetReference')(
        SheetReferenceImpl)


class CellLocationImpl(object):
    def __init__(self, row=None, column=None):
        self.__row = row
        self.__column = column

    # @Override
    def getRow(self):
        return self.__row

    # @Override
    def getColumn(self):
        return self.__column
CellLocationImpl = implement(
        'edu.utah.sci.vistrails.javaspreadsheet.CellLocation')(
        CellLocationImpl)


class CellInfos(object):
    __ID_GEN = 1
    __ORIG_DATA = dict()

    def __init__(self, infos):
        self.__internal_id = self.__ID_GEN
        CellInfos.__ID_GEN += 1
        CellInfos.__ORIG_DATA[self.__internal_id] = infos

    # @Override
    def getVistrail(self):
        return CellInfos.__ORIG_DATA[self.__internal_id]['vistrail']

    # @Override
    def getVersion(self):
        return CellInfos.__ORIG_DATA[self.__internal_id]['version']

    # @Override
    def getModule(self):
        return CellInfos.__ORIG_DATA[self.__internal_id]['module_id']

    # @Override
    def getReason(self):
        return CellInfos.__ORIG_DATA[self.__internal_id]['reason']

    # @Override
    def getInternalID(self):
        return self.__internal_id

    @staticmethod
    def getInfos(infos):
        return CellInfos.__ORIG_DATA[infos.getInternalID()]
CellInfosImpl = implement(
        'edu.utah.sci.vistrails.javaspreadsheet.CellInfos')(
        CellInfos)


class SpreadsheetWrapper(object):
    def __init__(self):
        self._spreadsheet = Spreadsheet(SpreadsheetInterfaceImpl())

    def getSheet(self, sheetref=None):
        if sheetref is None:
            return SheetWrapper(self._spreadsheet.getSheet())
        else:
            return SheetWrapper(self._spreadsheet.getSheet(
                SheetReferenceImpl(sheetref.name)))

    def setVisible(self, vis):
        self._spreadsheet.setVisible(vis)


class SheetWrapper(object):
    def __init__(self, sheet):
        self._sheet = sheet

    def getCell(self, location=None):
        if location is None:
            return CellWrapper(self._sheet.getCell())
        else:
            return CellWrapper(self._sheet.getCell(CellLocationImpl(
                location.row, location.column)))


class CellWrapper(object):
    def __init__(self, cell):
        self._cell = cell

    def setWidget(self, widget):
        self._cell.setWidget(widget)

    def assign(self, infos):
        self._cell.assign(CellInfosImpl(infos))


def setup_spreadsheet():
    return SpreadsheetWrapper()
