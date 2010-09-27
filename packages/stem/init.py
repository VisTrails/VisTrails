import os

from core.modules.basic_modules import File, Directory, new_constant
from core.modules.module_registry import get_module_registry
from core.modules.vistrails_module import Module, ModuleError, ModuleConnector

reg = get_module_registry()
RSource = \
    reg.get_descriptor_by_name('edu.utah.sci.vistrails.rpy', 'RSource').module
RFigure = reg.get_descriptor_by_name('edu.utah.sci.vistrails.rpy',
                                     'RFigure', 'Figures').module

def create_file_module(fname, f=None):
    if f is None:
        f = File()
    f.name = fname
    f.upToDate = True
    return f

def create_dir_module(dname, d=None):
    if d is None:
        d = Directory()
    d.name = dname
    d.upToDate = True
    return d

def get_path(fname=''):
    return os.path.join(os.path.dirname(__file__), fname)

def build_params(input_ports, remap={}):
    def get_name(port):
        if port in remap:
            return remap[port]
        return port
    params = ",\n".join(["%s=%s" % (get_name(port[0]), get_name(port[0]))
                         for port in input_ports
                         if port[0] not in remap.keys() or (port[0] in remap.keys() and remap[port[0]] is not None)])
    return params



def processActivePortData(inputPorts, object):
    portData = []

    if object.hasInputFromPort('stem.globals'):       
        stemGlobals = object.getInputFromPort('stem.globals')
    else :
        stemGlobals = None

    for port in inputPorts:
        if port[0] != 'stem.globals' and object.hasInputFromPort(port[0]) and object.getInputFromPort(port[0]) is not None:       
            portData.append((port[0], port[0]))
            if port[1] == '(edu.utah.sci.vistrails.basic:Directory)' or port[1] == '(edu.utah.sci.vistrails.basic:File)':
                object.set_variable(port[0], object.getInputFromPort(port[0]).name)                          
            else:
                object.set_variable(port[0], object.getInputFromPort(port[0]))                          
        elif stemGlobals:
            if stemGlobals.global_vars.has_key(port[0]) and stemGlobals.global_vars[port[0]] is not None:          
                portData.append((port[0], port[0]))
 
    return portData

class STEMConfiguration(RSource):
    _input_ports = []
    _output_ports = [('config', '(edu.cornell.birds.stem:STEMConfiguration)')]
    def compute(self):
        self.chdir(get_path())
        self.run_file(get_path('STEM_Configuration.R'), 
                      excluded_outputs=set(['config']))
        self.setResult('config', self)

class RunModels(RSource):
    _input_ports = [('config', '(edu.cornell.birds.stem:STEMConfiguration)'),
                    ('spp.name', '(edu.utah.sci.vistrails.basic:String)'),
                    ('spp.common', '(edu.utah.sci.vistrails.basic:String)')]
    _output_ports = [('config', '(edu.cornell.birds.stem:STEMConfiguration)')]
    def compute(self):
        self.chdir(get_path())
        self.set_variable('spp.dir.name', self.getInputFromPort('spp.name'))
        self.run_file(get_path('STEM_ModelingEngine.R'),
                      excluded_inputs=set(['source', 'config']), 
                      excluded_outputs=set(['config']))
        self.setResult('config', self.getInputFromPort('config'))

class BuildVisualizations(RSource):
    _input_ports = [('config', '(edu.cornell.birds.stem:STEMConfiguration)')]
    _output_ports = [('results.dir', 
                      '(edu.utah.sci.vistrails.basic:Directory)')]
    def compute(self):
        self.chdir(get_path())
        self.run_file(get_path('STEM.nfold.pp.comp_2.12.10.R'),
                      excluded_inputs=set(['source', 'config']),
                      excluded_outputs=set(['results.dir']))
        dname = list(self.get_variable('results.dir'))[0]
        self.setResult('results.dir', create_dir_module(dname))
        
class STEMFigure(RFigure):
    """Write only the R figure code.  You do not need the png or pdf
    graphics setup code or the dev.off calls"""
    _input_ports = [('results.dir',
                     '(edu.utah.sci.vistrails.basic:Directory)', ),
                    ('pp.metric', '(edu.utah.sci.vistrails.basic:String)')]
    def compute(self):
        self.chdir(get_path())
        self.set_variable('results.dir', 
                          self.getInputFromPort('results.dir').name)
        self.run_figure_file(get_path('STEM_Figure.R'), 'png', 800, 600, 
                             excluded_inputs=set(['source',
                                                  'results.dir']))

# class STEMCreateData(Module):
#     """Data preparation"""
#     def compute(self):
#         self.run_file(get_path('STEM.erd.data.creation.R'))

class STEMGlobals(RSource):
    _input_ports = [('debugOutput', '(edu.utah.sci.vistrails.basic:Boolean)'),
                    ('platform', '(edu.utah.sci.vistrails.basic:String)'),
                    ('parent.dir', '(edu.utah.sci.vistrails.basic:Directory)'),
                    ('code.directory', '(edu.utah.sci.vistrails.basic:Directory)'),
                    ('species.name', '(edu.utah.sci.vistrails.basic:String)'),
                    ('common.name', '(edu.utah.sci.vistrails.basic:String)'),
                    ('erd.data.file', '(edu.utah.sci.vistrails.basic:File)'),
                    ('srd.pred.design.file', '(edu.utah.sci.vistrails.basic:File)')]
    _output_ports = [('self', '(edu.cornell.birds.stem:STEMGlobals)')]
    def compute(self):
        # run the requires and the loading of STEM libs
        parent_dir = self.getInputFromPort('parent.dir')
        self.chdir(self.getInputFromPort('code.directory').name)
        self.set_variable('parent.dir', parent_dir.name)
        # FIXME code.directory defaults to parent.dir
        if not self.hasInputFromPort('code.directory'):
            self.set_variable('code.directory', parent_dir.name)
        else:
            self.set_variable('code.directory',
                              self.getInputFromPort('code.directory').name)
        self.set_variable('erd.data.filename',
                              ''.join([parent_dir.name, "Data/", self.getInputFromPort('erd.data.file').name]))
        self.set_variable('srd.pred.design.filename',
                          ''.join([parent_dir.name, "Data/", self.getInputFromPort('srd.pred.design.file').name]))
        species_name = self.getInputFromPort('species.name')
        stem_directory = create_dir_module(os.path.join(parent_dir.name, species_name))
        self.set_variable('stem.directory', stem_directory.name)
        self.set_variable('species.name', species_name)
        self.set_variable('common.name', self.getInputFromPort('common.name'))

        # FIXME add erd.data.filename and srd.pred.design.filename
        # No tags needed, then

        self.run_code(''.join(["source(\"", "STEM_Globals.R", "\")"]),
                      excluded_inputs=set(['source', 'parent.dir', 
                                           'code.directory', 'erd.data.file',
                                            'srd.pred.design.file']))

        # FIXME need to actually use and output the globals
        global_var_list = ['debugOutput',
                           'platform',
                           'parent.dir',
                           'code.directory',
                           'species.name',
                           'common.name',
                           'erd.data.filename',
                           'srd.pred.design.filename',
                           'stem.directory',
                           'spatial.extent.list',
                           'temporal.extent.list',
                           'predictor.names',
                           'response.family',
                           'cv.folds',
                           'cv.folds.par.list',
                           'cv.list',
                           'stem.init.par.list',
                           'base.model.par.list', 
                           'srd.max.sample.size',
                           'split.par.list',
                           'st.matrix.name',
                           'jdate.seq',
                           'year.seq',
                           'conditioning.vars',
                           'st.matrix.ave.maps',
                           'begin.seq',
                           'end.seq',
                           'pred.grid.size',
                           'map.plot.width',
                           'spatial.extent.list',
                           'z.max',
                           'z.min',
                           'map.tag',
                           'date.bar',
                           'print.date',
                           'county.map', 
                           'county.map.lwd',
                           'state.map',
                           'state.map.lwd']
        self.global_vars = dict((name, self.get_variable(name)) 
                                for name in global_var_list)


class InitERDMapAnalysis(RSource):
    _input_ports = [('project.directory', '(edu.utah.sci.vistrails.basic:String)'),
                    ('species.directory.nametag', '(edu.utah.sci.vistrails.basic:String)'),
                    ('map.directory.nametag', '(edu.utah.sci.vistrails.basic:String)'),
                    ('map.file.nametag', '(edu.utah.sci.vistrails.basic:String)'),
                    ('map.rows', '(edu.utah.sci.vistrails.basic:Integer)'),
                    ('z.max', '(edu.utah.sci.vistrails.basic:Float)'),
                    ('z.min', '(edu.utah.sci.vistrails.basic:Float)'),
                    ('map.number', '(edu.utah.sci.vistrails.basic:Integer)'),
                    ('lat.max', '(edu.utah.sci.vistrails.basic:Float)'),
                    ('lat.min', '(edu.utah.sci.vistrails.basic:Float)'),
                    ('lon.max', '(edu.utah.sci.vistrails.basic:Float)'),
                    ('lon.min', '(edu.utah.sci.vistrails.basic:Float)')]
    _output_ports = [('self', '(edu.cornell.birds.stem:InitERDMapAnalysis)')]
    def compute(self):
        # run the requires and the loading of STEM libs
        self.chdir(self.getInputFromPort('project.directory'))

        self.set_variable('project.directory', self.getInputFromPort('project.directory'))
        self.set_variable('species.directory.nametag', self.getInputFromPort('species.directory.nametag'))
        self.set_variable('map.directory.nametag', self.getInputFromPort('map.directory.nametag'))
        self.set_variable('map.file.nametag', self.getInputFromPort('map.file.nametag'))
        self.set_variable('map.rows', self.getInputFromPort('map.rows'))
        self.set_variable('z.max', self.getInputFromPort('z.max'))
        self.set_variable('z.min', self.getInputFromPort('z.min'))
        self.set_variable('map.number', self.getInputFromPort('map.number'))

        latMax = self.getInputFromPort('lat.max')
        if latMax:
            self.set_variable('lat.max', latMax)
        else:
            ## self.set_variable('lat.max', "as.null(lat.max)")
            self.run_code("lat.max <- NULL")

        latMin = self.getInputFromPort('lat.min')
        if latMin:
            self.set_variable('lat.min', latMin)
        else :
            self.run_code("lat.min <- NULL")

        lonMax = self.getInputFromPort('lon.max') 
        if lonMax:
            self.set_variable('lon.max', lonMax)
        else:
            self.run_code("lon.max <- NULL")

        lonMin = self.getInputFromPort('lon.min')
        if lonMin:
            self.set_variable('lon.min', lonMin)
        else:
            self.run_code("lon.min <- NULL")

        self.run_code(''.join(["source(\"", self.getInputFromPort('project.directory'), '/code/stem.vt.erd.map.function.R', "\")"]))

        global_var_list = ['project.directory', 
                           'species.directory.nametag', 
                           'map.directory.nametag', 
                           'map.file.nametag', 
                           'map.rows',
                           'z.max',
                           'z.min',
                           'map.number',
                           'lat.max',
                           'lat.min',
                           'lon.max',
                           'lon.min'] 

        self.global_vars = dict((name, self.get_variable(name)) 
                                for name in global_var_list if name is not None)

class PlotERDMaps(RSource):
    _input_ports = [('stem.globals', '(edu.cornell.birds.stem:InitERDMapAnalysis)'),
                    ('project.directory', '(edu.utah.sci.vistrails.basic:Directory)'),
                    ('species.directory.nametag', '(edu.utah.sci.vistrails.basic:String)'),
                    ('map.directory.nametag', '(edu.utah.sci.vistrails.basic:Directory)'),
                    ('map.file.nametag', '(edu.utah.sci.vistrails.basic:File)'),
                    ('map.rows', '(edu.utah.sci.vistrails.basic:Integer)'),
                    ('z.max', '(edu.utah.sci.vistrails.basic:Float)'),
                    ('z.min', '(edu.utah.sci.vistrails.basic:Float)'),
                    ('map.number', '(edu.utah.sci.vistrails.basic:Integer)'),
                    ('lat.max', '(edu.utah.sci.vistrails.basic:Float)'),
                    ('lat.min', '(edu.utah.sci.vistrails.basic:Float)'),
                    ('lon.max', '(edu.utah.sci.vistrails.basic:Float)'),
                    ('lon.min', '(edu.utah.sci.vistrails.basic:Float)')]
    _output_ports = [('map_file', '(edu.utah.sci.vistrails.basic:File)')]

    def compute(self):
        ## stem_globals = self.getInputFromPort('stem.globals')
        ## for k, v in stem_globals.global_vars.iteritems():
        ##     self.set_variable(k,v)                          

        activePorts = processActivePortData(PlotERDMaps._input_ports, self)

        remap = {'stem.globals': None}
        params = build_params(activePorts, remap)
        code_str = "mapFile <-stem.erd.maps(%s)" % params

        self.run_code(code_str)

        self.setResult('map_file', create_file_module(str(list(self.get_variable('mapFile'))[0])))


class ERDDataCreation(RSource):
    _input_ports = [('protocol.tag', '(edu.utah.sci.vistrails.basic:String)'),
                    ('max.effort.hours', 
                     '(edu.utah.sci.vistrails.basic:Float)'),
                    ('max.effort.distance.fm', 
                     '(edu.utah.sci.vistrails.basic:Float)'),
                    ('min.obs.time', '(edu.utah.sci.vistrails.basic:Float)'),
                    ('max.obs.time', '(edu.utah.sci.vistrails.basic:Float)'),
                    ('response.type', '(edu.utah.sci.vistrails.basic:String)'),
                    ('ebird.data.dir', 
                     '(edu.utah.sci.vistrails.basic:Directory)'),
                    ('erd.data.tag', '(edu.utah.sci.vistrails.basic:String)'),
                    ('spatial.erd.tag', 
                     '(edu.utah.sci.vistrails.basic:String)'),
                    ('checklist.covariate.names', 
                     '(edu.utah.sci.vistrails.rpy:RVector:Types)'),
                    ('core.covariate.names', 
                     '(edu.utah.sci.vistrails.rpy:RVector:Types)'),
                    ('NLCD.class.neighborhood.size', 
                     '(edu.utah.sci.vistrails.rpy:RVector:Types)'),
                    ('NLCD.names', 
                     '(edu.utah.sci.vistrails.rpy:RVector:Types)'),
                    ('class.level.fragstats', 
                     '(edu.utah.sci.vistrails.rpy:RVector:Types)'),
                    ('landscape.fragstat.tags', 
                     '(edu.utah.sci.vistrails.rpy:RVector:Types)'),
                    ('landscape.neighborhood.size', 
                     '(edu.utah.sci.vistrails.rpy:RVector:Types)')]
    _output_ports = [('srd.pred.design.file', 
                      '(edu.utah.sci.vistrails.basic:File)'),
                     ('erd.design.file',
                      '(edu.utah.sci.vistrails.basic:File)')]
    def compute(self):
        self.chdir(get_path())
        self.set_variable('ebird.data.dir',
                          self.getInputFromPort('ebird.data.dir').name)
        self.run_file(get_path('STEM_Globals.R'),
                      excluded_inputs=set(['source', 'ebird.data.dir']))
        srd_fname = list(self.get_variable('srd.pred.design.filename'))[0]
        erd_fname = list(self.get_variable('erd.design.filename'))[0]
        self.setResult('srd.pred.design.file', create_file_module(srd_fname))
        self.setResult('erd.design.file', create_file_module(erd_fname))
                    

class ERDDataSubsetting(RSource):
    _input_ports = [('stem.globals', '(edu.cornell.birds.stem:STEMGlobals)'),
                    ('erd.data.filename', '(edu.utah.sci.vistrails.basic:File)'),
                    ('srd.pred.design.filename', '(edu.utah.sci.vistrails.basic:File)'),
                    ('spatial.extent.list', '(edu.utah.sci.vistrails.rpy:RList:Types)'),
                    ('temporal.extent.list', '(edu.utah.sci.vistrails.rpy:RList:Types)'),
                    ('species.name', '(edu.utah.sci.vistrails.basic:String)'),
                    ('predictor.names', '(edu.utah.sci.vistrails.rpy:RVector:Types)'),
                    ('response.family', '(edu.utah.sci.vistrails.basic:String)'),
                    ('srd.max.sample.size', '(edu.utah.sci.vistrails.basic:Integer)'),
                    ('split.par.list', '(edu.utah.sci.vistrails.rpy:RList:Types)')]
    _output_ports = [('train.data', '(edu.utah.sci.vistrails.rpy:RList:Types)'),
                     ('test.data', '(edu.utah.sci.vistrails.rpy:RList:Types)'),
                     ('pred.data', '(edu.utah.sci.vistrails.rpy:RList:Types)'),
                     ('stem.predictor.names', '(edu.utah.sci.vistrails.rpy:RVector:Types)')]
    # Get train.data, test.data, srd.data from eBird.data and expose
    # these three as the output ports
    def compute(self):
        ## stem_globals = self.getInputFromPort('stem.globals')
        ## for k, v in stem_globals.global_vars.iteritems():
        ##     self.set_variable(k,v)

        activePorts = processActivePortData(ERDDataSubsetting._input_ports, self)

        remap = {'srd.pred.design.file': 'srd.pred.design.filename',
                 'stem.globals': None}
        params = build_params(activePorts, remap)
        code_str = "eBird.data <- erd.srd.data.subsetting(%s)" % params

        self.run_code(code_str, 
                      excluded_inputs=set(['source', 'srd.pred.design.file']),
                      excluded_outputs=set(['eBird.data']))

        train = self.get_variable('eBird.data$train.data')
        test = self.get_variable('eBird.data$test.data')
        srd = self.get_variable('eBird.data$srd.data')

        self.run_code("stem.predictor.names <- names(eBird.data$train.data$X)")
        stem_predictor_names = self.get_variable('stem.predictor.names')
        
        self.setResult('train.data', train)
        self.setResult('test.data', test)
        self.setResult('pred.data', srd)
        self.setResult('stem.predictor.names', stem_predictor_names)
    
class FitSTEM(RSource):
    _input_ports = [('stem.globals', '(edu.cornell.birds.stem:STEMGlobals)'),
                    ('train.data', '(edu.utah.sci.vistrails.rpy:RList:Types)'),
                    ('stem.directory', '(edu.utah.sci.vistrails.basic:Directory)'),
                    ('response.family', '(edu.utah.sci.vistrails.basic:String)'),
                    ('cv.folds', '(edu.utah.sci.vistrails.basic:Integer)'),
                    ('cv.folds.par.list', '(edu.utah.sci.vistrails.rpy:RList:Types)'),
                    ('stem.init.par.list', '(edu.utah.sci.vistrails.rpy:RList:Types)'),
                    ('base.model.par.list', '(edu.utah.sci.vistrails.rpy:RList:Types)')]
    _output_ports = [('models.directory', '(edu.utah.sci.vistrails.basic:Directory)')]

    def compute(self):
        # use a single models dir with a variable number of
        # subdirectories depending on the cv.folds value
        # same for results, now -- models/stem.models.[1-10]
        ## stem_globals = self.getInputFromPort('stem.globals')
        ## for k, v in stem_globals.global_vars.iteritems():
        ##     self.set_variable(k,v)

        activePorts = processActivePortData(FitSTEM._input_ports, self)

        remap = {'stem.globals': None}
        params = build_params(activePorts, remap)
        code_str = "stem(%s)" % params

        self.run_code(code_str)


class ERDPredictivePerformance(RSource):
    _input_ports = [('stem.globals', '(edu.cornell.birds.stem:STEMGlobals)'),
                    ('test.data', '(edu.utah.sci.vistrails.rpy:RList:Types)'),
                    ('stem.directory', 
                     '(edu.utah.sci.vistrails.basic:Directory)'),
                    ('pp.directory', 
                     '(edu.utah.sci.vistrails.basic:Directory)'),
                    ('cv.list',
                     '(edu.utah.sci.vistrails.rpy:RVector:Types)'),
                    ('n.mc',
                     '(edu.utah.sci.vistrails.basic:Integer)'),
                    ('grid.cell.min.lat',
                     '(edu.utah.sci.vistrails.basic:Float)'),
                    ('grid.cell.min.lon',
                     '(edu.utah.sci.vistrails.basic:Float)'),
                    ('min.val.cell.locs',
                     '(edu.utah.sci.vistrails.basic:Integer)'),
                    ('threshold',
                     '(edu.utah.sci.vistrails.basic:Float)'),
                    ('min.testset.sample.size',
                     '(edu.utah.sci.vistrails.basic:Integer)'),
                    ('plot.it',
                     '(edu.utah.sci.vistrails.basic:Boolean)')]
    # pp.directory specifies where, but we can move this, i think
    _output_ports = [('pp.directory',
                      '(edu.utah.sci.vistrails.basic:Directory)')]
    def compute(self):
        self.set_variable('stem.directory', 
                          self.getInputFromPort('stem.directory').name)
        pp_directory = self.getInputFromPort('pp.directory')
        self.set_variable('pp.directory', pp_directory.name)
        self.run_file('')
        self.setResult('pp.directory', pp_directory)
    
class PredictSTEM(RSource):
    _input_ports = [('stem.globals', '(edu.cornell.birds.stem:STEMGlobals)'),
                    ('stem.directory', 
                     '(edu.utah.sci.vistrails.basic:Directory)'),
                    ('pred.data', '(edu.utah.sci.vistrails.rpy:RList:Types)'),
                    ('cv.list', '(edu.utah.sci.vistrails.rpy:RVector:Types)'),
                    ('st.pred.tag', '(edu.utah.sci.vistrails.basic:String)'),
                    ('st.prediction.filename', 
                     '(edu.utah.sci.vistrails.basic:File)')]
    _output_ports = [('st.pred', '(edu.utah.sci.vistrails.rpy:RList:Types)')]
    def compute(self):
        pas

class ERDPredictSTMatrix(RSource):
    _input_ports = [('stem.globals', '(edu.cornell.birds.stem:STEMGlobals)'),
                    ('stem.directory',
                     '(edu.utah.sci.vistrails.basic:Directory)'),
                    ('pred.data', '(edu.utah.sci.vistrails.rpy:RList:Types)'),
                    ('cv.list', '(edu.utah.sci.vistrails.rpy:RVector:Types)'),
                    ('stem.predictor.names', 
                     '(edu.utah.sci.vistrails.rpy:RVector:Types)'),
                    ('st.matrix.name', 
                     '(edu.utah.sci.vistrails.basic:String)'),
                    ('jdate.seq',
                     '(edu.utah.sci.vistrails.rpy:RVector:Types)'),
                    ('year.seq',
                     '(edu.utah.sci.vistrails.rpy:RVector:Types)'),
                    ('conditioning.vars',
                     '(edu.utah.sci.vistrails.rpy:RList:Types)')]
    _output_ports = [('st.matrix.directory',
                      '(edu.utah.sci.vistrails.basic:Directory)')]
    def compute(self): 
        stem_globals = self.getInputFromPort('stem.globals')
        ## for k, v in stem_globals.global_vars.iteritems():
        ##     self.set_variable(k,v)
                                          
        activePorts = processActivePortData(ERDPredictSTMatrix._input_ports, self)
 
        remap = {'stem.globals': None}
        params = build_params(activePorts, remap)
        code_str = "predict.erd.st.matrix(%s)" % params

        self.run_code(code_str)

        if self.hasInputFromPort('stem.directory'):
           if self.hasInputFromPort('st.matrix.name'):
               self.setResult('st.matrix.directory', create_dir_module(os.path.join(self.getInputFromPort('stem.directory').name,
                                                       self.getInputFromPort('st.matrix.name'))))
           else:
               self.setResult('st.matrix.directory', create_dir_module(os.path.join(self.getInputFromPort('stem.directory').name,
                                                       str(list(stem_globals.global_vars['st.matrix.name'])[0]))))
        else:
           if self.hasInputFromPort('st.matrix.name'):
               self.setResult('st.matrix.directory', create_dir_module(os.path.join(str(list(stem_globals.global_vars['stem.directory'])[0]),
                                                       self.getInputFromPort('st.matrix.name'))))
           else:
               self.setResult('st.matrix.directory', create_dir_module(os.path.join(str(list(stem_globals.global_vars['stem.directory'])[0]),
                                                       str(list(stem_globals.global_vars['st.matrix.name'])[0]))))


class STMatrixCVAvg(RSource):
    _input_ports = [('stem.globals', '(edu.cornell.birds.stem:STEMGlobals)'),
                    ('stem.directory', '(edu.utah.sci.vistrails.basic:Directory)'),
                    ('st.matrix.input.directory', '(edu.utah.sci.vistrails.basic:Directory)'),
                    ('cv.list', '(edu.utah.sci.vistrails.rpy:RVector:Types)'),
                    ('jdate.seq', '(edu.utah.sci.vistrails.rpy:RVector:Types)'),
                    ('year.seq', '(edu.utah.sci.vistrails.rpy:RVector:Types)'),
                    ('st.matrix.output.directory', '(edu.utah.sci.vistrails.basic:Directory)')]
    _output_ports = [('st.matrix.directory', '(edu.utah.sci.vistrails.basic:Directory)'),
                     ('map.directory', '(edu.utah.sci.vistrails.basic:Directory)')]
    def compute(self):
        self.set_variable('st.matrix.input.directory', self.getInputFromPort('st.matrix.input.directory').name)        
        st_matrix_output_directory = self.getInputFromPort('st.matrix.input.directory')
        self.set_variable('st.matrix.output.directory', st_matrix_output_directory.name)

        stem_globals = self.getInputFromPort('stem.globals')
        ## for k, v in stem_globals.global_vars.iteritems():
        ##     self.set_variable(k,v)

        activePorts = processActivePortData(STMatrixCVAvg._input_ports, self)
 
        remap = {'stem.globals': None}
        params = build_params(activePorts, remap)
        code_str = "st.matrix.cv.average(%s)" % params

        self.run_code(code_str)

        self.setResult('st.matrix.directory', st_matrix_output_directory)
        self.setResult('map.directory', create_dir_module(os.path.join(str(list(stem_globals.global_vars['stem.directory'])[0]),
                                                                       str(list(stem_globals.global_vars['st.matrix.ave.maps'])[0]))))



class STMatrixMaps(RSource):
    _input_ports = [('stem.globals', '(edu.cornell.birds.stem:STEMGlobals)'),
                    ('st.matrix.directory',
                     '(edu.utah.sci.vistrails.basic:Directory)'),
                    ('map.directory',
                     '(edu.utah.sci.vistrails.basic:Directory)'),
                    ('jdate.seq',
                     '(edu.utah.sci.vistrails.rpy:RVector:Types)'),
                    ('year.seq',
                     '(edu.utah.sci.vistrails.rpy:RVector:Types)'),
                    ('begin.seq',
                     '(edu.utah.sci.vistrails.basic:Integer)'),
                    ('end.seq',
                     '(edu.utah.sci.vistrails.basic:Integer)'),
                    ('pred.grid.size',
                     '(edu.utah.sci.vistrails.basic:Integer)'),
                    ('map.plot.width',
                     '(edu.utah.sci.vistrails.basic:Integer)'),
                    ('spatial.extent.list',
                     '(edu.utah.sci.vistrails.rpy:RVector:Types)'),
                    ('z.max',
                     '(edu.utah.sci.vistrails.basic:Float)'),
                    ('z.min',
                     '(edu.utah.sci.vistrails.basic:Float)'),
                    ('map.tag',
                     '(edu.utah.sci.vistrails.basic:String)'),
                    ('date.bar',
                     '(edu.utah.sci.vistrails.basic:Boolean)'),
                    ('print.date',
                     '(edu.utah.sci.vistrails.basic:Boolean)'),
                    ('county.map',
                     '(edu.utah.sci.vistrails.basic:Boolean)'),
                    ('county.map.lwd',
                     '(edu.utah.sci.vistrails.basic:Float)'),
                    ('state.map',
                     '(edu.utah.sci.vistrails.basic:Boolean)'),
                    ('state.map.lwd',
                     '(edu.utah.sci.vistrails.basic:Float)')]
    _output_ports = [('map.directory',
                      '(edu.utah.sci.vistrails.basic:Directory)'),
                     ('map_file_1', 
                      '(edu.utah.sci.vistrails.basic:File)')]
    def compute(self):
        self.set_variable('st.matrix.directory', ''.join([self.getInputFromPort('st.matrix.directory').name]))
        map_directory = self.getInputFromPort('map.directory')
        self.set_variable('map.directory', map_directory.name)

        ## stem_globals = self.getInputFromPort('stem.globals')
        ## for k, v in stem_globals.global_vars.iteritems():
        ##     self.set_variable(k,v)                          

        activePorts = processActivePortData(STMatrixMaps._input_ports, self)

        remap = {'stem.globals': None}
        params = build_params(activePorts, remap)
        code_str = "st.matrix.maps(%s)" % params

        self.run_code(code_str)

        self.setResult('map.directory', map_directory)



class ERD_CV_Avg_Maps(RSource):
    _input_ports = [('stem.globals', '(edu.cornell.birds.stem:STEMGlobals)'),
                    ('stem.directory', 
                     '(edu.utah.sci.vistrails.basic:Directory)'),
                    ('st.matrix.file.tag',
                     '(edu.utah.sci.vistrails.basic:String)'),
                    ('cv.list', '(edu.utah.sci.vistrails.rpy:RVector:Types)'),
                    ('maps.directory', 
                     '(edu.utah.sci.vistrails.basic:Directory)'),
                    ('map.file.tag', '(edu.utah.sci.vistrails.basic:String)'),
                    ('ns.rows', '(edu.utah.sci.vistrails.basic:Integer)'),
                    ('map.plot.pixel.width', 
                     '(edu.utah.sci.vistrails.basic:Integer)'),
                    ('mapping.spatial.extent', 
                     '(edu.utah.sci.vistrails.rpy:RList:Types)'),
                    ('z.max', '(edu.utah.sci.vistrails.basic:Float)')]
    _output_ports = [('erd.cv.avg.maps.directory',
                     '(edu.utah.sci.vistrails.basic:Directory)')]
    def compute(self):
        pass

# _modules = [STEMConfiguration, 
#             RunModels, 
#             BuildVisualizations, 
#             STEMFigure]
            
_modules = [ERDDataCreation,
            ERDDataSubsetting,
            FitSTEM,
            ERDPredictivePerformance,
            PredictSTEM,
            ERDPredictSTMatrix,
            STMatrixCVAvg,
            STMatrixMaps,
            # ERD_CV_Avg_Maps,
            STEMGlobals,
            InitERDMapAnalysis,
            PlotERDMaps
            ]
