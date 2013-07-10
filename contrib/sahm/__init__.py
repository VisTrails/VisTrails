from core.configuration import ConfigurationObject

name = "SAHM"
identifier = "gov.usgs.sahm"
version = '0.0.5'

configuration = \
    ConfigurationObject(output_dir= r'C:\temp\SAHM_workspace',
                        r_path = r'..\\Central_R\R-2.12.1\bin',
                        gdal_path = r'..\\Central_GDAL',
                        maxent_path = r'..\\Central_Maxent',
                        qgis_path = r'..\\Central_QGIS',
                        projection_layers_path = r'I:\WorldClim_Future_Climate\RenamedBILs', #This only applies to instances running in the FORT Infrastructure
                        verbose = 'True')
