'''
Created on Sep 17, 2010

@author: talbertc
'''

import time
import os, sys
import csv
import itertools
import traceback

import subprocess

from optparse import OptionParser

#from core.modules.vistrails_module import Module, ModuleError, ModuleConnector
#from core.system import execute_cmdline



import utilities
#from packages.sahm.pySAHM.Utilites import self.writetolog

from osgeo import gdalconst
from osgeo import gdal
from osgeo import osr

class MAXENTRunner(object):
    
    def __init__(self):
        self.verbose = False
        self.maxentpath = ''
        self.inputMDS = ''
        self.projectionlayers = ''
        self.testCSV = ''
        self.trainingCSV = ''
        self.backgroundCSV = ''
        self.outputDir = ''
        self.categoricals = []
        self.argsCSV = ''
        self.logger = None
      
    def run(self):
        self.loadArgs()
        self.args['outputdirectory'] = self.outputDir
    
#        if self.projectionlayers <> '':
#            #A command line input overrides an input in the args csv
#            self.args['projectionlayers'] = self.projectionlayers
#    
        self.validateInputs()
    
        if self.inputMDS <> '':
            self.prepInputs()
        else:
            raise Exception, "No MDS supplied."

        if not self.args.has_key('projectionlayers'):
            self.args['projectionlayers'] = ''

        if self.trainingCSV <> '':
            self.args['samplesfile'] = self.trainingCSV
        else:
            raise Exception, "No Samples file supplied"
        
        if self.testCSV <> '':
            self.args['testsamplesfile'] = self.testCSV
        
        if self.backgroundCSV <> '':
            self.args['environmentallayers'] = self.backgroundCSV
        
        
        self.args['autorun'] = 'true'
        #self.args['outputgrids'] = 'false'
        
        if ' ' in self.args['species_name']:
            self.args['species_name'] = self.args['species_name'].replace(' ', '_')
        
        strargs = ['='.join((str(k),str(v))) for k,v in self.args.iteritems() if k <> "species_name"]
        for categorical in self.categoricals:
            strargs += ['togglelayertype=' + categorical.replace('_categorical', '')]
        #strargs = ' '.join(strargs)
        #print strargs
        
        if not self.maxentpath.endswith('.jar'):
            jar = os.path.join(self.maxentpath, 'maxent.jar')
        else:
            jar = self.maxentpath
            
        self.run_cmd_line_jar(jar, strargs)
        
           
    def run_cmd_line_jar(self, jar_name, args):
        #arg_items = list(itertools.chain(*args.items()))
        #arg_items = ['='.join((str(k),str(v))) for k,v in args.iteritems()]
        
        cmd = ' '.join(['java', '-mx512m',  '-jar', jar_name] + args)
         
        self.writetolog('    running:  ' + cmd, True, False)
        #res = execute_cmdline(['java', '-jar', jar_name] + args, output)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.writetolog('    Finished running:  ', True, False)
        
        
        ret = p.communicate()
        self.writetolog('    Maxent strOut:  ' + str(ret[0]))
        if ret[1] is not None:
            msg = "An error was encountered running the Maxent jar file.  The error message is below - \n"
            msg += ret[1]
            writetolog(msg)
            raise RuntimeError , msg
        del ret

    def loadArgs(self):
        argsReader = csv.reader(open(self.argsCSV, 'r'))
        header = argsReader.next()
        self.args = {}
        for row in argsReader:
            self.args[row[0]] = row[1]
    
    def validateInputs(self):
        if not os.path.exists(self.argsCSV):
            raise RuntimeError(self, 'Input argsFile, ' + self.argsCSV + ', could not be found on file system')
        
        if not os.path.exists(self.inputMDS):
            raise RuntimeError(self, 'Input MDS, ' + self.inputMDS + ', could not be found on file system')
        
        if not self.args.has_key('projectionlayers'):
             self.args['projectionlayers'] = ''
             
        if self.args['projectionlayers'] <> '':
             dirs = self.args['projectionlayers'].split(',')
             for dir in dirs:
                 if not os.path.isdir(dir):
                     raise RuntimeError(self, "Input 'projectionlayers' must be a directory")
        
        if not utilities.isMDSFile(self.inputMDS):
            raise RuntimeError(self, 'Input MDS, ' + self.inputMDS + ', does not appear to be formated as an MDS file.')
    
        if not os.path.exists(self.outputDir):
            raise RuntimeError(self, 'Output directory, ' + self.outputDir + ', could not be found on file system')
        
        if self.logger is None:
            self.logger = utilities.logger(outDir, self.verbose)
        self.writetolog = self.logger.writetolog
    
    def prepInputs(self):
        '''parses out input MDS file into the 1 to 3 SWD files that Maxent requires.
        '''
        
        #Create the outputs in our outputdirectory
        self.testCSV = os.path.join(self.outputDir, 'testSamples.csv')
        self.trainingCSV = os.path.join(self.outputDir, 'trainingSamples.csv')
        self.backgroundCSV = os.path.join(self.outputDir, 'backgroundPoints.csv')
        
        testWriter = csv.writer(open(self.testCSV, 'wb'))
        trainingWriter = csv.writer(open(self.trainingCSV, 'wb'))
        backgroundWriter = csv.writer(open(self.backgroundCSV, 'wb'))
        
        #Read through the MDS and pull the headers
        MDSreader = csv.reader(open(self.inputMDS, 'r'))
        header1 = MDSreader.next()
        header2 = MDSreader.next()
        header3 = MDSreader.next()
        
        self.pullCategoricals(header1)

        #The split column indicates that this file has been run through the 
        #test training split and testing data should be writen to the test file.
        splitcol = None
        try:
            splitcol = header1.index('Split')
            deleteTest = False
        except ValueError:
            self.writetolog("    The supplied MDS does not have a 'Split' column defaulting to having Maxent apply test/training split.")        
            deleteTest = True
            
        covariateIndexes = self.usedIndexes(header1, header2)        
        covariateNames = self.usedValues(header1, covariateIndexes)
        covariateNamesClean = [name.replace('_categorical', '') for name in covariateNames]
        usedCovariateFiles = self.usedValues(header3, covariateIndexes)
        
        self.writetolog('    Used covariates:' +  ", ".join(covariateNames), False, False)
             
        testWriter.writerow(['full_name', 'x', 'y'] + covariateNamesClean)
        trainingWriter.writerow(['full_name', 'x', 'y'] + covariateNamesClean)
        backgroundWriter.writerow(['full_name', 'x', 'y'] + covariateNamesClean)
        
        #loop through the rows sending each row to the appropriate file
        hasBackground = False
        for row in MDSreader:
            if row[2] == '-9999':
                hasBackground = True
                vals = self.usedValues(row, covariateIndexes)
                backgroundWriter.writerow([''] + row[:2] + vals)
            elif splitcol is None and row[2] <> 0:
                vals = self.usedValues(row, covariateIndexes)
                trainingWriter.writerow([self.args['species_name']] + row[:2] + vals)
            elif (row[splitcol] == 'test' and row[2] <> 0) or \
                self.testCSV == '':
                vals = self.usedValues(row, covariateIndexes)
                testWriter.writerow([self.args['species_name']] + row[:2] + vals)
            elif row[splitcol] == 'train'  and row[2] <> 0:
                vals = self.usedValues(row, covariateIndexes)
                trainingWriter.writerow([self.args['species_name']] + row[:2] + vals)
            #any absense points (row[2] == 0) will be ignored for maxent
        
        if not hasBackground:
            msg = "    No background points were detected in the input file."
            msg += "\n    This implementation of Maxent does not have access to prepared ASCII environmental layers"
            msg += " from which to extract values.  Background points must be supplied in the MDS file."
            self.writetolog(msg)
            raise RuntimeError(msg)
        
        #del our writers 
        try:
            del testWriter
            if deleteTest:
                os.remove(self.testCSV)
                self.testCSV = ''
            del backgroundWriter
            if not hasBackground:
                os.remove(self.backgroundCSV)
                self.backgroundCSV = ''
            del trainingWriter
        except:
            print ' '.join([str(i) for i in sys.exc_info()[:2]])
            pass
        
        #First we have to figure out what they passed us
        #either a directory, a SWD file, or a csv with a list of files
        
        if self.args['projectionlayers'] <> '':
            pass
        else:
            self.args['outputgrids'] = 'false'

    def usedIndexes(self, header1, header2):
        covariateIndexes = []
        for i in range(len(header1)):
            if header2[i] == '1' and header1[i] <> 'Split':
                covariateIndexes.append(i)
        return covariateIndexes
      
    def usedValues(self, values, indexes):
        usedvals = []
        for i in indexes:
            usedvals.append(values[i])
        return usedvals
    
    def pullCategoricals(self, headerline):
        for item in headerline:
            if item.endswith('_categorical'):
                self.categoricals.append(item)
        
        
    def isSWD(self, file):
        '''Checks the format of a file to see if it is in the 
        Maxent samples with data (SWD) format.
        '''
        if os.path.exists(file):
            reader = csv.reader(open(file, 'r'))
            header = reader.next()
            if header[0].lower() in ['species', 'full_name', 'fullname']:
                return True
        
        return False


def main(argv):
    '''Process our command line args and initiate a Maxent run
    '''
    usageStmt = "usage:  -m --MDSFile -a --argsCSV -o --outputDir"
    desc = "Formats and prepares input for running the Maxent Jar in a SAHM workflow"

    parser = OptionParser(usage=usageStmt, description=desc)
    parser.add_option("-m", "--MDSFile", 
                      dest="MDSFile", 
                      help="The MDS file with our sample data.")
#    parser.add_option("-p", "--projectionData", 
#                      dest="projectionData", 
#                      help="An optional CSV with a projection file for each of our environemnetal layers.")
    parser.add_option("-a", "--argsCSV", 
                      dest="argsCSV", 
                      help="A CSV with each Maxent argument name and it's value on separate lines.")
    parser.add_option("-e", "--maxentExecutable", 
                  dest="maxentExecutable", 
                  help="The full path to the maxent executable jar file.")
    parser.add_option("-o", "--outputDir", 
                      dest="outputDir", 
                      help="The directory to save output files.")
    parser.add_option("-v", "--verbose", 
                  dest="verbose", 
                  default=False, 
                  action="store_true",
                  help="the verbose flag causes diagnostic output to print")

    (options, args) = parser.parse_args(argv)

    ourMaxent = MAXENTRunner()
    ourMaxent.verbose = options.verbose
    ourMaxent.maxentpath = options.maxentExecutable
    ourMaxent.inputMDS = options.MDSFile
    ourMaxent.outputDir = options.outputDir
    ourMaxent.argsCSV = options.argsCSV
    ourMaxent.projectionDataFile = options.projectionData

    utilities.createsessionlog(options.outputDir, options.verbose)
    ourMaxent.run()

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
    





