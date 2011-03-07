from core.configuration import ConfigurationObject

name = "SAHM"
identifier = "gov.usgs.sahm"
version = '0.0.4'

sahm_path = None
models_path = None
configuration = \
    ConfigurationObject(sahm_path='I:/VisTrails/Central_SAHM',
                        models_path='I:/VisTrails/Central_SAHM/Resources/ModelBuilder',
                        layers_path = 'I:/VisTrails/Central_VisTrailsInstall/VisTrails/vistrails/packages/sahm/layers.csv',
                        r_path = 'I:/VisTrails/Central_VisTrailsInstall/Central_R/R-2.12.1/bin',
                        verbose = 'true')
