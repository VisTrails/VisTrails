from core.modules.basic_modules import String, Boolean, File, Integer
from core.modules.module_registry import get_module_registry
from core.modules.vistrails_module import Module, ModuleError
from core.upgradeworkflow import UpgradeWorkflowHandler

from info.ipaw.pc3.LoadAppLogic import LoadAppLogic

import os

name = "Provenance Challenge 3"
identifier = "edu.utah.sci.dakoop.pc3"
version = '1.0.1'

# class Module(object):
#     pass

# class String(Module):
#     pass

# class Boolean(Module):
#     pass

# class Integer(Module):
#     pass

class Collection(Module):
    def __init__(self, lst, klass=None):
        Module.__init__(self)
        self.lst = lst
        self.klass = klass

    def compute(self):
        self.lst = self.forceGetInputListFromPort('elements')
        self.setResult('collection', self.list)

    _input_ports = [('elements', Module)]
    _output_ports = []
    # _output_ports = [('self', Collection)]
Collection._output_ports.append(('self', Collection))
    
class CSVFileEntry(Module):
    def __init__(self, file_entry=None):
        Module.__init__(self)
        if file_entry is not None:
            self.file_entry = file_entry
        else:
            self.file_entry = LoadAppLogic.CSVFileEntry()

    def compute(self):
        self.checkInputPort('filePath')
        self.checkInputPort('headerPath')
        self.checkInputPort('rowCount')
        self.checkInputPort('targetTable')
        self.checkInputPort('checksum')
        self.checkInputPort('columnNames')
        self.file_entry.FilePath = self.getInputFromPort('filePath')
        self.file_entry.HeaderPath = self.getInputFromPort('headerPath')
        self.file_entry.RowCount = self.getInputFromPort('rowCount')
        self.file_entry.TargetTable = self.getInputFromPort('targetTable')
        self.file_entry.Checksum = self.getInputFromPort('checksum')
        self.file_entry.ColumnNames = self.getInputFromPort('columnNames').lst
        self.setResult('self', self)

    _input_ports = [('filePath', String), 
                    ('headerPath', String),
                    ('rowCount', Integer),
                    ('targetTable', String),
                    ('checksum', String),
                    ('columnNames', Collection)]
    _output_ports = []
    # _output_ports = [('self', CSVFileEntry)]
CSVFileEntry._output_ports.append(('self', CSVFileEntry))
    
class DatabaseEntry(Module):
    def __init__(self, db_entry=None):
        Module.__init__(self)
        if db_entry is not None:
            self.db_entry = db_entry
        else:
            self.db_entry = LoadAppLogic.DatabaseEntry()
    
    def compute(self):
        self.checkInputPort('dbGuid')
        self.checkInputPort('dbName')
        self.checkInputPort('connectionString')
        self.db_entry.DBGuid = self.getInputFromPort('dbGuid')
        self.db_entry.DBName = self.getInputFromPort('dbName')
        self.db_entry.ConnectionString = \
            self.getInputFromPort('connectionString')
        self.setResult('self', self)

    _input_ports = [('dbGuid', String),
                    ('dbName', String),
                    ('connectionString', String)]
    _output_ports = []
    # _output_ports = [('self', DatabaseEntry)]
DatabaseEntry._output_ports.append(('self', DatabaseEntry))

class IsCSVReadyFileExists(Module):
    def compute(self):
        self.checkInputPort('csvRootPath')
        path = self.getInputFromPort('csvRootPath')
        res = LoadAppLogic.IsCSVReadyFileExists(path)
        self.setResult('fileExists', res)

    _input_ports = [('csvRootPath', String)]
    _output_ports = [('fileExists', Boolean)]
    
class ReadCSVReadyFile(Module):
    def compute(self):
        self.checkInputPort('csvRootPath')
        path = self.getInputFromPort('csvRootPath')
        self.annotate({'used_files':
                           str([os.path.join(path, "csv_ready.csv")])})
        csv_files = LoadAppLogic.ReadCSVReadyFile(path)
        # wrapped_res = Collection([CSVFileEntry(e) for e in res], CSVFileEntry)
        list_of_elts = [CSVFileEntry(f) for f in csv_files]
        for elt in list_of_elts:
            elt.upToDate = True
        self.setResult('csvFiles', list_of_elts)

    _input_ports = [('csvRootPath', String)]
    # _output_ports = [('csvFiles', [Collection, CSVFileEntry])]
    _output_ports = [('csvFiles', 
                      '(edu.utah.sci.vistrails.basic:List)')]

class IsMatchCSVFileTables(Module):
    def compute(self):
        self.checkInputPort('csvFiles')
        csv_files = self.getInputFromPort('csvFiles')
        res = LoadAppLogic.IsMatchCSVFileTables([f.file_entry 
                                                 for f in csv_files])
        self.setResult('tablesMatch', res)

    # _input_ports = [('csvFiles', [Collection, CSVFileEntry])]
    _input_ports = [('csvFiles', 
                     '(edu.utah.sci.vistrails.basic:List)')]
    _output_ports = [('tablesMatch', Boolean)]

class IsExistsCSVFile(Module):
    def compute(self):
        self.checkInputPort('csvFile')
        csv_file = self.getInputFromPort('csvFile')
        res = LoadAppLogic.IsExistsCSVFile(csv_file.file_entry)
        self.setResult('fileExists', res)

    _input_ports = [('csvFile', CSVFileEntry)]
    _output_ports = [('fileExists', Boolean)]
    
class ReadCSVFileColumnNames(Module):
    def compute(self):
        self.checkInputPort('csvFile')
        csv_file = self.getInputFromPort('csvFile')
        self.annotate({'used_files':
                          str([csv_file.file_entry.HeaderPath])})
        res = LoadAppLogic.ReadCSVFileColumnNames(csv_file.file_entry)
        self.setResult('csvFile', CSVFileEntry(res))

    _input_ports = [('csvFile', CSVFileEntry)]
    _output_ports = [('csvFile', CSVFileEntry)]
    
class IsMatchCSVFileColumnNames(Module):
    def compute(self):
        self.checkInputPort('csvFile')
        csv_file = self.getInputFromPort('csvFile')
        res = LoadAppLogic.IsMatchCSVFileColumnNames(csv_file.file_entry)
        self.setResult('columnsMatch', res)

    _input_ports = [('csvFile', CSVFileEntry)]
    _output_ports = [('columnsMatch', Boolean)]

class CreateEmptyLoadDB(Module):
    def compute(self):
        self.checkInputPort('jobID')
        job_id = self.getInputFromPort('jobID')
        res = LoadAppLogic.CreateEmptyLoadDB(job_id)
        self.setResult('dbEntry', DatabaseEntry(res))

    _input_ports = [('jobID', String)]
    _output_ports = [('dbEntry', DatabaseEntry)]

class LoadCSVFileIntoTable(Module):
    def compute(self):
        self.checkInputPort('csvFile')
        self.checkInputPort('dbEntry')
        csv_file = self.getInputFromPort('csvFile')
        db_entry = self.getInputFromPort('dbEntry')
        self.annotate({'used_files':
                          str([csv_file.file_entry.FilePath]),
                       'generated_tables':
                           str([(db_entry.db_entry.ConnectionString, 
                                 db_entry.db_entry.DBName,
                                 csv_file.file_entry.TargetTable)])})
        res = LoadAppLogic.LoadCSVFileIntoTable(db_entry.db_entry,
                                                csv_file.file_entry)
        self.setResult('success', res)

    _input_ports = [('csvFile', CSVFileEntry), ('dbEntry', DatabaseEntry)]
    _output_ports = [('success', Boolean)]

class UpdateComputedColumns(Module):
    def compute(self):
        self.checkInputPort('csvFile')
        self.checkInputPort('dbEntry')
        csv_file = self.getInputFromPort('csvFile')
        db_entry = self.getInputFromPort('dbEntry')
        if csv_file.file_entry.TargetTable.upper() == 'P2DETECTION':
            self.annotate({'used_tables':
                           str([(db_entry.db_entry.ConnectionString, 
                                 db_entry.db_entry.DBName,
                                 csv_file.file_entry.TargetTable)])})
        res = LoadAppLogic.UpdateComputedColumns(db_entry.db_entry,
                                                 csv_file.file_entry)
        self.setResult('success', res)

    _input_ports = [('csvFile', CSVFileEntry), ('dbEntry', DatabaseEntry)]
    _output_ports = [('success', Boolean)]

class IsMatchTableRowCount(Module):
    def compute(self):
        self.checkInputPort('csvFile')
        self.checkInputPort('dbEntry')
        csv_file = self.getInputFromPort('csvFile')
        db_entry = self.getInputFromPort('dbEntry')
        self.annotate({'used_tables':
                           str([(db_entry.db_entry.ConnectionString, 
                                 db_entry.db_entry.DBName,
                                 csv_file.file_entry.TargetTable)])})
        res = LoadAppLogic.IsMatchTableRowCount(db_entry.db_entry,
                                                csv_file.file_entry)
        self.setResult('countsMatch', res)

    _input_ports = [('csvFile', CSVFileEntry), ('dbEntry', DatabaseEntry)]
    _output_ports = [('countsMatch', Boolean)]

class IsMatchTableColumnRanges(Module):
    def compute(self):
        self.checkInputPort('csvFile')
        self.checkInputPort('dbEntry')
        csv_file = self.getInputFromPort('csvFile')
        db_entry = self.getInputFromPort('dbEntry')
        if csv_file.file_entry.TargetTable.upper() == 'P2DETECTION':
            self.annotate({'used_tables':
                               str([(db_entry.db_entry.ConnectionString, 
                                     db_entry.db_entry.DBName,
                                     csv_file.file_entry.TargetTable)])})
        res = LoadAppLogic.IsMatchTableColumnRanges(db_entry.db_entry,
                                                    csv_file.file_entry)
        self.setResult('rangesMatch', res)

    _input_ports = [('csvFile', CSVFileEntry), ('dbEntry', DatabaseEntry)]
    _output_ports = [('rangesMatch', Boolean)]

class CompactDatabase(Module):
    def compute(self):
        self.checkInputPort('dbEntry')
        db_entry = self.getInputFromPort('dbEntry')
        self.annotate({'used_tables':
                           str([(db_entry.db_entry.ConnectionString, 
                                 db_entry.db_entry.DBName,
                                 "P2Detection"),
                                (db_entry.db_entry.ConnectionString, 
                                 db_entry.db_entry.DBName,
                                 "P2FrameMeta"),
                                (db_entry.db_entry.ConnectionString, 
                                 db_entry.db_entry.DBName,
                                 "P2ImageMeta")])})
        LoadAppLogic.CompactDatabase(db_entry.db_entry)
        self.setResult('dbEntry', db_entry)
        

    _input_ports = [('dbEntry', DatabaseEntry)]
    _output_ports = [('dbEntry', DatabaseEntry)]

class GetCSVFiles(Module):
    def compute(self):
        self.checkInputPort('csvRootPath')
        path = self.getInputFromPort('csvRootPath')
        if not LoadAppLogic.IsCSVReadyFileExists(path):
            raise ModuleError(self, "IsCSVReadyFileExists failed")
        self.annotate({'used_files':
                           str([os.path.join(path, "csv_ready.csv")])})
        csv_files = LoadAppLogic.ReadCSVReadyFile(path)
        if not LoadAppLogic.IsMatchCSVFileTables(csv_files):
            raise ModuleError(self, "IsMatchCSVFileTables failed")
#         getter = get_module_registry().get_descriptor_by_name
#         descriptor = getter('edu.utah.sci.vistrails.basic', 
#                             'List')
#         list_of_elts = descriptor.module()
#         list_of_elts.value = [CSVFileEntry(f) for f in csv_files]
#         self.setResult('csvFiles', list_of_elts)
        list_of_elts = [CSVFileEntry(f) for f in csv_files]
        for elt in list_of_elts:
            elt.upToDate = True
        print 'list_of_elts:', list_of_elts
        self.setResult('csvFiles', list_of_elts)
#         wrapped_res = Collection([CSVFileEntry(f) for f in csv_files], 
#                                  CSVFileEntry)
#         self.setResult('csvFiles', wrapped_res)

    _input_ports = [('csvRootPath', String)]
    _output_ports = [('csvFiles', 
                      '(edu.utah.sci.vistrails.basic:List)')]
    # _output_ports = [('csvFiles', [Collection, CSVFileEntry])]

class ReadCSVFile(Module):
    def compute(self):
        self.checkInputPort('csvFile')
        csv_file = self.getInputFromPort('csvFile')
        if not LoadAppLogic.IsExistsCSVFile(csv_file.file_entry):
            raise ModuleError(self, "IsExistsCSVFile failed")
        self.annotate({'used_files':
                          str([csv_file.file_entry.HeaderPath])})
        csv_file.file_entry = \
            LoadAppLogic.ReadCSVFileColumnNames(csv_file.file_entry)
        if not LoadAppLogic.IsMatchCSVFileColumnNames(csv_file.file_entry):
            raise ModuleError(self, "IsMatchCSVFileColumnNames failed")
        self.setResult('csvFile', csv_file)

    _input_ports = [('csvFile', CSVFileEntry)]
    _output_ports = [('csvFile', CSVFileEntry)]
    
class LoadCSVFileIntoDB(Module):
    def compute(self):
        self.checkInputPort('csvFile')
        self.checkInputPort('dbEntry')
        csv_file = self.getInputFromPort('csvFile')
        print 'csv_file:', csv_file
        db_entry = self.getInputFromPort('dbEntry')
        self.annotate({'used_files':
                          str([csv_file.file_entry.FilePath])})
        self.annotate({'generated_tables':
                           str([(db_entry.db_entry.ConnectionString, 
                                 db_entry.db_entry.DBName,
                                 csv_file.file_entry.TargetTable)])})
        if not LoadAppLogic.LoadCSVFileIntoTable(db_entry.db_entry,
                                                 csv_file.file_entry):
            raise ModuleError(self, "LoadCSVFileIntoTable failed")
        self.setResult('dbEntry', db_entry)

    _input_ports = [('csvFile', CSVFileEntry), ('dbEntry', DatabaseEntry)]
    _output_ports = [('dbEntry', DatabaseEntry)]

class ComputeColumns(Module):
    def compute(self):
        self.checkInputPort('csvFile')
        self.checkInputPort('dbEntry')
        csv_file = self.getInputFromPort('csvFile')
        db_entry = self.getInputFromPort('dbEntry')
        self.annotate({'used_tables':
                           str([(db_entry.db_entry.ConnectionString, 
                                 db_entry.db_entry.DBName,
                                 csv_file.file_entry.TargetTable)])})
        if not LoadAppLogic.UpdateComputedColumns(db_entry.db_entry,
                                                  csv_file.file_entry):
            raise ModuleError(self, "UpdateComputedColumns failed")
        if not LoadAppLogic.IsMatchTableRowCount(db_entry.db_entry,
                                                 csv_file.file_entry):
            raise ModuleError(self, "IsMatchTableRowCount failed")
        if not LoadAppLogic.IsMatchTableColumnRanges(db_entry.db_entry,
                                                     csv_file.file_entry):
            raise ModuleError(self, "IsMatchTableColumnRanges failed")
        self.setResult('dbEntry', db_entry)

    _input_ports = [('csvFile', CSVFileEntry), ('dbEntry', DatabaseEntry)]
    _output_ports = [('dbEntry', DatabaseEntry)]

class DetectionsHistogram(Module):
    def compute(self):
        self.checkInputPort('dbEntry')
        db_entry = self.getInputFromPort('dbEntry')
        high_quality = False
        if self.hasInputFromPort('highQuality'):
            high_quality = self.getInputFromPort('highQuality')
        self.annotate({'used_tables':
                           str([(db_entry.db_entry.ConnectionString, 
                                 db_entry.db_entry.DBName,
                                 "P2Detection")])})
        histogram = LoadAppLogic.DetectionsHistogram(db_entry.db_entry, 
                                                     high_quality)
        self.setResult('histogram', histogram)
    
    _input_ports = [('dbEntry', DatabaseEntry), ('highQuality', Boolean, True)]
    _output_ports = [('histogram', 
                      '(edu.utah.sci.vistrails.basic:List)')]

_modules = [Collection,
            CSVFileEntry,
            DatabaseEntry,
            IsCSVReadyFileExists,
            ReadCSVReadyFile,
            IsMatchCSVFileTables,
            IsExistsCSVFile,
            ReadCSVFileColumnNames,
            IsMatchCSVFileColumnNames,
            CreateEmptyLoadDB,
            LoadCSVFileIntoTable,
            UpdateComputedColumns,
            IsMatchTableRowCount,
            IsMatchTableColumnRanges,
            CompactDatabase,
            GetCSVFiles,
            ReadCSVFile,
            LoadCSVFileIntoDB,
            ComputeColumns,
            DetectionsHistogram,
            ]

def package_dependencies():
    return ['edu.utah.sci.vistrails.control_flow']

def handle_module_upgrade_request(controller, module_id, pipeline):
    module_remap = {'ReadCSVReadyFile': [(None, '1.0.1', None, {})],
                    'IsMatchCSVFileTables': [(None, '1.0.1', None, {})],
                    'GetCSVFiles': [(None, '1.0.1', None, {})],
                    'DetectionsHistogram': [(None, '1.0.1', None, {})],
                    }

    return UpgradeWorkflowHandler.remap_module(controller, module_id, pipeline,
                                               module_remap)
