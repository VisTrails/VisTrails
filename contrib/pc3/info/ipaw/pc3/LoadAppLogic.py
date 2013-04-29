import MySQLdb
import os
import uuid

from LoadConstants import LoadConstants
from LoadSql import LoadSql

class LoadAppLogic(object):

    #region Database Constants
    SQL_SERVER = "localhost"
    SQL_USER = "ipaw"
    SQL_PASSWORD = "pc3_load-2009"
    #endregion

    #region Helper data structures
    class CSVFileEntry(object):
        def __init__(self):
            self.FilePath = None
            self.HeaderPath = None
            self.RowCount = None
            self.TargetTable = None
            self.Checksum = None
            self.ColumnNames = []

    class DatabaseEntry(object):
        def __init__(self):
            self.DBGuid = None
            self.DBName = None
            self.ConnectionString = None
    #endregion

    #region Pre-Load Sanity Checks

    @staticmethod
    def IsCSVReadyFileExists(CSVRootPath):
        """<summary>
        Checks if the CSV Ready File exists in the given rooth path to the 
        CSV Batch
        </summary>
        <param name="CSVRootPath">Path to the root directory for the batch
        </param>
        <returns>true if the csv_ready.csv file exists in the CSVRoothPath. 
        False otherwise.</returns>
        """

        # 1. Check if parent directory exists.
        if not os.path.exists(CSVRootPath):
            return False
            
        # 2. Check if CSV Ready file exists. We assume a static name for the ready file.
        CSVReadyFilePath = os.path.join(CSVRootPath, "csv_ready.csv")
        return os.path.exists(CSVReadyFilePath)  

    @staticmethod
    def ReadCSVReadyFile(CSVRootPath):
        """<summary>
    
        </summary>
        <param name="CSVRootPath"></param>
        <returns></returns>
        """

        # 1. Initialize output list of file entries
        CSVFileEntryList = []
      
        # 2. Open input stream to read from CSV Ready File
        CSVReadyFilePath =  os.path.join(CSVRootPath, "csv_ready.csv")
        ReadyFileStream  = open(CSVReadyFilePath);

        # 3. Read each line in CSV Ready file and split the lines into 
        #    individual columns separated by commas
        for ReadyFileLine in ReadyFileStream:
            
            # 3.a. Expect each line in the CSV ready file to be of the format:
            # <FileName>,<NumRows>,<TargetTable>,<MD5Checksum>        
            ReadyFileLineTokens = ReadyFileLine.split(',')

            # 3.b. Create an empty FileEntry and populate it with the columns
            FilePath = os.path.join(CSVRootPath,
                                    ReadyFileLineTokens[0].strip())

            # CSVFileEntry FileEntry  = new CSVFileEntry();
            FileEntry = LoadAppLogic.CSVFileEntry()
            FileEntry.FilePath = FilePath
            FileEntry.HeaderPath = FilePath + ".hdr"
            FileEntry.RowCount = int(ReadyFileLineTokens[1].strip())
            FileEntry.TargetTable = ReadyFileLineTokens[2].strip()
            FileEntry.Checksum = ReadyFileLineTokens[3].strip()

            # 3.c. Add file entry to output list
            CSVFileEntryList.append(FileEntry);

        # 4. Close input stream and return output file entry list
        ReadyFileStream.close();

        return CSVFileEntryList;
    
    @staticmethod
    def IsMatchCSVFileTables(FileEntries):
        """<summary>
        Check if the correct list of files/table names are present in this batch
        </summary>
        <param name="FileEntries"></param>
        <returns></returns>
        """

        # check if the file count and the expected number of tables match
        if (len(LoadConstants.EXPECTED_TABLES) != len(FileEntries)):
            return false;

        # for each expected table name, check if it is present 
        # in the list of file entries
        for TableName in LoadConstants.EXPECTED_TABLES:
            TableExists = False
            for FileEntry in FileEntries:
                if TableName == FileEntry.TargetTable:
                    TableExists = True
                    break
                
            # if the table name did not exist in list of CSV files, 
            # this check fails.
            if not TableExists:
                return False

        return True

    @staticmethod
    def IsExistsCSVFile(FileEntry):
        """<summary>
        Test if a CSV File defined in the CSV Ready list actually exists on disk.
        </summary>
        <param name="FileEntry">FileEntry for CSVFile to test</param>
        <returns>True if the FilePath in the given FileEntry exists on disk. False otherwise.</returns>
        """
        if not os.path.exists(FileEntry.FilePath):
            return False

        return os.path.exists(FileEntry.HeaderPath)

    @staticmethod
    def ReadCSVFileColumnNames (FileEntry):
        """<summary>
        
        </summary>
        <param name="FileEntry"></param>
        <param name="FileEntry"></param>
        <returns></returns>
        """

        # 2. Read the header line of the CSV File.
        CSVFileReader = open(FileEntry.HeaderPath)
        HeaderRow = CSVFileReader.readline()

        # 3. Extract the comma-separated columns names of the CSV File from its header line.
        # Strip empty spaces around column names.
        ColumnNames = HeaderRow.split(',')
        FileEntry.ColumnNames = []
        for ColumnName in ColumnNames:
            FileEntry.ColumnNames.append(ColumnName.strip())

        CSVFileReader.close()

        return FileEntry

    @staticmethod
    def IsMatchCSVFileColumnNames(FileEntry):
        """<summary>
        Checks if the correct list of column headers is present for the CSV file
        to match the table
        </summary>
        <param name="FileEntry">FileEntry for CSV File whose column headers to test</param>
        <returns>True if the column headers present in the CSV File are the same as the 
        expected table columns. False otherwise.</returns>
        """
      
        # determine expected columns
        ExpectedColumns = None

        ExpectedColumnsLookup = {"P2DETECTION": \
                                     LoadConstants.EXPECTED_DETECTION_COLS,
                                 "P2FRAMEMETA": \
                                     LoadConstants.EXPECTED_FRAME_META_COLS,
                                 "P2IMAGEMETA": \
                                     LoadConstants.EXPECTED_IMAGE_META_COLS,
                                 }
        if FileEntry.TargetTable.upper() in ExpectedColumnsLookup:
            ExpectedColumns = \
                ExpectedColumnsLookup[FileEntry.TargetTable.upper()]
        else:
            return False
            
        # test if the expected and present column name counts are the same
        if len(ExpectedColumns) != len(FileEntry.ColumnNames):
            return False

        # test of all expected names exist in the columns present
        for ColumnName in ExpectedColumns:
            if ColumnName not in FileEntry.ColumnNames:
                return False

        # all columns match
        return True;
    #endregion

    #region Loading Section
    @staticmethod
    def CreateEmptyLoadDB(JobID):
        """<summary>
        
        </summary>
        <param name="JobID"></param>
        <returns></returns>
        """

        # initialize database entry for storing database properties
        DBEntry = LoadAppLogic.DatabaseEntry()
        DBEntry.DBName = JobID + "_LoadDB"
        DBEntry.DBGuid = str(uuid.uuid4())
        DBEntry.ConnectionString = {'host': LoadAppLogic.SQL_SERVER,
                                    'user': LoadAppLogic.SQL_USER,
                                    'passwd': LoadAppLogic.SQL_PASSWORD,
                                    }

        # initialize Sql Connection String to sql server
        SqlConn = MySQLdb.connect(**DBEntry.ConnectionString)

        # Create empty database instance
        SqlCur = SqlConn.cursor()
        SqlCur.execute("CREATE DATABASE " + DBEntry.DBName)
        DBEntry.ConnectionString['db'] = DBEntry.DBName

        # update Sql Connection String to new create tables
        SqlCur = SqlConn.cursor()
        SqlCur.execute("use %s" % DBEntry.DBName)
        SqlCur.execute(LoadSql.CREATE_DETECTION_TABLE)
        SqlCur.execute(LoadSql.CREATE_FRAME_META_TABLE)
        SqlCur.execute(LoadSql.CREATE_IMAGE_META_TABLE)
        SqlCur.close()
        SqlConn.close()

        return DBEntry
    
    # derby bulk load: SYSCS_UTIL.SYSCS_IMPORT_TABLE
    @staticmethod
    def LoadCSVFileIntoTable(DBEntry, FileEntry):
        """<summary>
        Loads a CSV File into an existing table using Sql BULK INSERT command
        </summary>
        <param name="DBEntry">Database into which to load the CSV file</param>
        <param name="FileEntry">File to be bulk loaded into database table</param>
        <returns>True if the bulk load ran without exceptions. False otherwise.</returns>
        """
        try:
            # connect to database instance
            SqlConn = MySQLdb.connect(**DBEntry.ConnectionString)
            SqlCur = SqlConn.cursor()
            # execute bulk insert command
            SqlCur.execute(("LOAD DATA INFILE %%s INTO TABLE %s "
                            "FIELDS TERMINATED BY ','") % \
                               FileEntry.TargetTable, 
                           (FileEntry.FilePath,))
            SqlCur.close()
            SqlConn.close()
        except Exception, e:
            # print e
            # bulk insert failed
            SqlCur.close()
            SqlConn.close()
            return False
        # bulk insert success
        return True

    @staticmethod
    def UpdateComputedColumns(DBEntry, FileEntry):
        """<summary>
        
        </summary>
        <param name="DBEntry"></param>
        <param name="FileEntry"></param>
        """

        def P2Detection(SqlCur):
            # Update ZoneID
            SqlCur.execute('UPDATE P2Detection '
                           'SET zoneID = (`dec`+(90.0))/(0.0083333)')
            # Update cx
            SqlCur.execute('UPDATE P2Detection '
                           'SET cx = (COS(RADIANS(`dec`))*COS(RADIANS(ra)))')
            # Update cy
            SqlCur.execute('UPDATE P2Detection '
                           'SET cy = COS(RADIANS(`dec`))*SIN(RADIANS(ra))')
            # Update cz
            SqlCur.execute('UPDATE P2Detection '
                           'SET cz = (SIN(RADIANS(`dec`)))')

        def P2FrameMeta(SqlCur):
            # No columns to be updated for FrameMeta
            pass

        def P2ImageMeta(SqlCur):
            # No columns to be updated for ImageMeta
            pass

        TargetTableLookup = {"P2DETECTION": P2Detection,
                             "P2FRAMEMETA": P2FrameMeta,
                             "P2IMAGEMETA": P2ImageMeta,
                             }
            
        try:
            # connect to database instance
            SqlConn = MySQLdb.connect(**DBEntry.ConnectionString)
            SqlCur = SqlConn.cursor()
            if FileEntry.TargetTable.upper() in TargetTableLookup:
                TargetTableLookup[FileEntry.TargetTable.upper()](SqlCur)
            else:
                # none of the table types matches...invalid
                SqlCur.close()
                SqlConn.close()
                return False

        except Exception, e:
            print e
            # update column failed
            SqlCur.close()
            SqlConn.close()
            return False
        # update column success
        return True

    #endregion

    #region Post-Load Checks
    @staticmethod
    def IsMatchTableRowCount(DBEntry, FileEntry):
        """<summary>
        
        </summary>
        <param name="DBEntry"></param>
        <param name="FileEntry"></param>
        <returns></returns>
        """

        # does the number of rows expected match the number of rows loaded
        SqlConn = MySQLdb.connect(**DBEntry.ConnectionString)
        SqlCur = SqlConn.cursor()
        # execute row count command
        SqlCur.execute("SELECT COUNT(*) FROM %s" % FileEntry.TargetTable)
        RowCount = SqlCur.fetchone()[0]
        SqlCur.close()
        SqlConn.close()
        # check if row count matches expected row count
        return RowCount == FileEntry.RowCount

    @staticmethod
    def IsMatchTableColumnRanges(DBEntry, FileEntry):
        """<summary>
        
        </summary>
        <param name="DBEntry"></param>
        <param name="FileEntry"></param>
        <returns></returns>
        """
      
        # determine expected column ranges
        ExpectedColumnRanges = None
        ExpectedColumnRangesLookup = \
            {"P2DETECTION": LoadConstants.EXPECTED_DETECTION_COL_RANGES,
             "P2FRAMEMETA": [],
             "P2IMAGEMETA": [],
             }
        if FileEntry.TargetTable.upper() in ExpectedColumnRangesLookup:
            ExpectedColumnRanges = \
                ExpectedColumnRangesLookup[FileEntry.TargetTable.upper()]
        else:
            # none of the table types matches...invalid
            return False

        # connect to database instance
        SqlConn = MySQLdb.connect(**DBEntry.ConnectionString)
        SqlCur = SqlConn.cursor()
        
        # For each column in available list, test if rows in table fall 
        # outside expected range
        for Column in ExpectedColumnRanges:
            # build SQL command for error count
            SqlCur.execute("SELECT COUNT(*) FROM %s "
                           "WHERE (%s < %s OR %s > %s) AND %s != -999" % \
                               (FileEntry.TargetTable, Column.ColumnName,
                                Column.MinValue, Column.ColumnName, 
                                Column.MaxValue, Column.ColumnName))

            ErrorCount = SqlCur.fetchone()[0]
            if ErrorCount > 0:
                print "ERROR COUNT", ErrorCount
                SqlCur.close()
                SqlConn.close()
                return False

        SqlCur.close()
        SqlConn.close()

        return True # no range errors found

    @staticmethod
    def CompactDatabase(DBEntry):
        """<summary>
        
        </summary>
        <param name="DBEntry"></param>
        """

        # Shrink database instance
        SqlConn = MySQLdb.connect(**DBEntry.ConnectionString)
        SqlCur = SqlConn.cursor()
        
        SqlCur.execute("SHOW TABLES")
        SqlTables = SqlCur.fetchall()
        for SqlTable in SqlTables:
            SqlCur.execute("OPTIMIZE TABLE %s" % SqlTable)
        SqlCur.close()
        SqlConn.close()

    #endregion

    #region Histogram
    @staticmethod
    def DetectionsHistogram(DBEntry, HighQuality=False):
        SqlConn = MySQLdb.connect(**DBEntry.ConnectionString)
        SqlCur = SqlConn.cursor()
        if HighQuality:
            where_clause = "WHERE raErr < 0.1 and decErr < 0.05 "
        else:
            where_clause = ""

        SqlCur.execute("SELECT ceiling(zoneId/10) as zoneGroup, " 
                       "count(*) as detectionCount FROM P2Detection "
                       "%s"
                       "GROUP BY ceiling(zoneId/10) "
                       "ORDER BY ceiling(zoneId/10)" % where_clause)
        return SqlCur.fetchall()
