import sys
##
# TODO list:
# (V) 1) Write the JobInfo module
# (V) 2) Make implement generator functionality
# (V) 4) write generator and exporter functions 
# (V) 9) Move generators.py, exporters.py -> containers.py
# (V) 10) auto_generated_types -> generator_definitions 
# (V) 11) Local file transfer fails when no visible files are present
# 12) Qprint -> annotate
# 13) Disconnect and kill process if queue exist
# 14) Write the clean up and add it to run job
# 15) There is an error with terminal selection


## TODO:
# 1) Fix the last things whatever they are
# 9) Pull the git repository
# 10) Add the package and update


### TESTING
# 1) Test collective operations
# 2) check wether it uploads anything
# 3) Try to see what happens when things are connected different from what you are supposed to do
# 4) Test queue reusing - something tells me that this might fail
version = '0.2'
identifier = 'org.comp-phys.batchq'
name = 'Job Submission'

def package_requirements():
    import core.requirements
    if not core.requirements.python_module_exists('batchq'):
        raise core.requirements.MissingRequirement('batchq')

