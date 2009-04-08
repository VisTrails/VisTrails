from LoadAppLogic import LoadAppLogic

class LoadWorkflow(object):
    @staticmethod
    def run(args):
        JobID, CSVRootPath = args[1:3]
        

        # /////////////////////////////////////
        # //////   Batch Initialization  //////
        # /////////////////////////////////////
        
        # 1. IsCSVReadyFileExists
        IsCSVReadyFileExistsOutput = \
            LoadAppLogic.IsCSVReadyFileExists(CSVRootPath)

        # 2. Control Flow: Decision
        if not IsCSVReadyFileExistsOutput:
            raise Exception("IsCSVReadyFileExists failed")


        # 3. ReadCSVReadyFile
        ReadCSVReadyFileOutput = LoadAppLogic.ReadCSVReadyFile(CSVRootPath)


        # 4. IsMatchCSVFileTables
        IsMatchCSVFileTablesOutput = \
            LoadAppLogic.IsMatchCSVFileTables(ReadCSVReadyFileOutput)
        # 5. Control Flow: Decision
        if not IsMatchCSVFileTablesOutput:
            raise Exception("IsMatchCSVFileTables failed")


        # 6. CreateEmptyLoadDB
        CreateEmptyLoadDBOutput = LoadAppLogic.CreateEmptyLoadDB(JobID)


        # 7. Control Flow: Loop. ForEach LoadAppLogic.CSVFileEntry 
        # in ReadCSVReadyFileOutput Do...
        for FileEntry in ReadCSVReadyFileOutput:
        
            # /////////////////////////////////////
            # //////   Pre Load Validation   //////
            # /////////////////////////////////////
            # 7.a. IsExistsCSVFile
            IsExistsCSVFileOutput = LoadAppLogic.IsExistsCSVFile(FileEntry)
            # 7.b. Control Flow: Decision
            if not IsExistsCSVFileOutput:
                raise Exception("IsExistsCSVFile failed")


            # 7.c. ReadCSVFileColumnNames
            ReadCSVFileColumnNamesOutput = \
                LoadAppLogic.ReadCSVFileColumnNames(FileEntry)


            # 7.d. IsMatchCSVFileColumnNames
            IsMatchCSVFileColumnNamesOutput = \
                LoadAppLogic.IsMatchCSVFileColumnNames(ReadCSVFileColumnNamesOutput)
            # 7.e. Control Flow: Decision
            if not IsMatchCSVFileColumnNamesOutput:
                raise Exception("IsMatchCSVFileColumnNames failed")


            # /////////////////////////////////////
            # //////        Load File        //////
            # /////////////////////////////////////
            # 7.f. LoadCSVFileIntoTable
            IsLoadedCSVFileIntoTableOutput = \
                LoadAppLogic.LoadCSVFileIntoTable(CreateEmptyLoadDBOutput, 
                                                  ReadCSVFileColumnNamesOutput)
            # 7.g. Control Flow: Decision
            if not IsLoadedCSVFileIntoTableOutput:
                raise Exception("LoadCSVFileIntoTable failed")


            # 7.h. UpdateComputedColumns
            IsUpdatedComputedColumnsOutput = \
                LoadAppLogic.UpdateComputedColumns(CreateEmptyLoadDBOutput, 
                                                   ReadCSVFileColumnNamesOutput)
            # 7.i. Control Flow: Decision
            if not IsUpdatedComputedColumnsOutput:
                raise Exception("UpdateComputedColumns failed")


            # /////////////////////////////////////
            # //////   PostLoad Validation   //////
            # /////////////////////////////////////
            # 7.j. IsMatchTableRowCount
            IsMatchTableRowCountOutput = \
                LoadAppLogic.IsMatchTableRowCount(CreateEmptyLoadDBOutput, 
                                                  ReadCSVFileColumnNamesOutput)
            # 7.k. Control Flow: Decision
            if not IsMatchTableRowCountOutput:
                raise Exception("IsMatchTableRowCount failed")


            # 7.l. IsMatchTableColumnRanges
            IsMatchTableColumnRangesOutput = \
                LoadAppLogic.IsMatchTableColumnRanges(CreateEmptyLoadDBOutput, 
                                                      ReadCSVFileColumnNamesOutput)
            # 7.m. Control Flow: Decision
            if not IsMatchTableColumnRangesOutput:
                raise Exception("IsMatchTableColumnRanges failed")


        # 8. CompactDatabase
        LoadAppLogic.CompactDatabase(CreateEmptyLoadDBOutput)

if __name__ == '__main__':
    import sys
    LoadWorkflow.run(sys.argv)
