from core.configuration import ConfigurationObject

configuration = ConfigurationObject(pvserver_bin=(None, str), 
                                    mpiexec_bin=(None, str),
                                    start_server=False,
                                    num_proc=4,
                                    port=11111)