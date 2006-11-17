from core import vis_pipeline
from core import vis_action
from core import vistrail
from core import vis_types
import copy
import __builtin__

from core.utils import any,VistrailsInternalError

################################################################################

class ParameterEnumerator(object):

    def __init__(self, pipeline):
        self.pipeline = pipeline

    def enumerateUserSetters(self):
        return dict([(id, vtk_rtti.VTKRTTI().vtkUserSetMethods(m.name,False,False,True,True))
                     for (id, m) in self.pipeline.modules.iteritems()])

    def runPipeline(self, paramSpecs=None):
        g = vtk_graph.VTKGraph()
        g.loadPipeline(self.pipeline)
        return g.run()

################################################################################

class Interpolator(object):
    
    def stepCount(self):
        abstract()
        
    def perform(self, pipeline, step):
        abstract()

class InterpolateAnd(Interpolator):

    def __init__(self, interps=[]):
        self.__interps = interps
        self.checkStepCount()
        
    def checkStepCount(self):
        steps = [interp.stepCount() for interp in self.interps]
        if steps == []:
            return
        if not self.myStepCount:
            self.myStepCount = steps[0]
        if common.any(steps, lambda x: x != self.myStepCount):
            raise VistrailsInternalError("Interpolators must have matching stepCount")
        
    def addInterpolator(self, interp):
        self.__interps.append(interp)
        self.checkStepCount()
        
    def stepCount(self):
        return self.myStepCount
    
    def perform(self, pipeline, step):
        [interp.perform(pipeline, step)
         for interp in self.__interps]

class InterpolateDiscreteParam(Interpolator):

    def __init__(self, module, function, range):
        self.module = module
        self.function = function
        self.range = range
        
    def stepCount(self):
        return len(self.range)
    
    def perform(self, pipeline, step):
        # Remember that range is always a range of tuples!
        m = pipeline.modules[self.module]
        f = vis_types.ModuleFunction()
        f.name = self.function
        f.returnType = 'void'
        value = self.range[step]
        for v in value:
            p = vis_types.ModuleParam()
            convert = {'int':'Integer', 'str':'String', 'float':'Float', 'double':'Float'}
            p.type = convert[type(v).__name__]
            p.strValue = str(v)
            f.params.append(p)
        m.functions.append(f)

class InterpolateFloatParam(Interpolator):

    def __init__(self, module, function, range, stepCount):
        self.module = module
        self.function = function
        self.range = range
        self.myStepCount = stepCount
        
    def stepCount(self):
        return self.myStepCount
    
    def perform(self, pipeline, step):
        t = float(step) / float(self.myStepCount-1)
        (mn, mx) = self.range
        v = mn + (mx - mn) * t
        m = pipeline.modules[self.module]
        f = vis_types.ModuleFunction()
        f.name = self.function
        f.returnType = 'void'
        p = vis_types.ModuleParam()
        p.type = 'float'
        p.strValue = str(v)
        f.params.append(p)
        m.functions.append(f)

class InterpolateId(Interpolator):

    def stepCount(self):
        return 1

    def perform(*args):
        pass

################################################################################

class ParameterStudy(object):
    
    def interpolate1D(self, pipeline, interp):
        """interpolate1D(pipeline, interpolator) -> [pipeline]
Returns a list of interpolated pipelines, by applying the interpolator"""
        stepCount = interp.stepCount()
        result = []
        for step in range(stepCount):
            newp = copy.copy(pipeline)
            interp.perform(newp, step)
            result.append(newp)
        return result

    def interpolateList(self, pipelineList, interpList, stepCount):
        """interpolate1D(pipeline, interpolator) -> [pipeline]
Returns a list of interpolated pipelines, by applying the interpolator"""
        if len(interpList)<1: return pipelineList
        result = []
        for step in range(stepCount):
            for pipeline in pipelineList:
                newp = copy.copy(pipeline)
                for interp in interpList:
                    interp.perform(newp, step)
                result.append(newp)
        return result
    
    def parameterStudy(self, pipeline, paramSpecs):
        """parameterStudy(pipeline, paramSpecs: [interpolator]) -> [pos, pipeline]
Returns a parameter study of a pipeline, which is a list of pipelines and their
position inside the n-dimensional parameter slice. n = len(paramSpecs). Each element
of paramSpecs is an interpolator, or a 'basis vector' of the slice."""
        result = [((), pipeline)]
        for spec in paramSpecs:
            newresult = []
            for (pos, oldp) in result:
                pipelinelist = self.interpolate1D(oldp, spec)
                stepCount = spec.stepCount()
                newresult.extend(zip([pos + (thispos,) for thispos in range(stepCount)],
                                     pipelinelist))
            result = newresult
        dims = self.paramSpecDims(paramSpecs)
        return (result, dims)

    def parameterStudyTime(self, pipeline, paramSpecs):
        """parameterStudyTime(pipeline, paramSpecs: [interpolator]) -> [pos, pipeline]
Same approach as the previous parameterStudy but take into account time dimension"""
        result = [((), pipeline)]
        realSpecs = []
        for spec,byTime in paramSpecs:
            newresult = []
            if not byTime: realSpecs += [spec]
            for (pos, oldp) in result:
                pipelinelist = self.interpolate1D(oldp, spec)
                stepCount = spec.stepCount()
                if byTime:
                    newresult.extend(zip([pos for thispos in range(stepCount)],
                                         pipelinelist))
                else:
                    newresult.extend(zip([pos + (thispos,) for thispos in range(stepCount)],
                                         pipelinelist))
                    
            result = newresult
        dims = self.paramSpecDims(realSpecs)
        return (result, dims)

    def paramSpecDims(self, paramSpecs):
        return [spec.stepCount()
                for spec in paramSpecs]

    def parameterStudyExplicit(self, pipeline, stepCounts, paramSpecs):
        """parameterStudyExplicit:[interpolator]) -> (dim, pipeline, matrix pipelines)
        dim = [frame per cell, columns, rows, sheets]
Same approach as the previous parameterStudy use explicit paramSpecs"""
        pipelineList = [pipeline]
        for i in range(len(paramSpecs)):
            pipelineList = self.interpolateList(pipelineList, paramSpecs[i], stepCounts[i])
        return (stepCounts, pipelineList)

    

################################################################################

class TestPipelineAnalyzer(object):
    def setUp(self):
        import vistrail
        import xml_parser
        parser = xml_parser.XMLParser()
        parser.openVistrail('test_files/brain_vistrail.xml')
        v = parser.getVistrail()
        parser.closeVistrail()
        self.pipeline = v.getPipeline('Nice layout')

        parser.openVistrail('test_files/vtk_book_3rd_p189.xml')
        self.pipeline2 = parser.getVistrail().getPipeline('final')
        parser.closeVistrail()

    def testDuh(self):
        print self.pipeline.modules[1].functions[0].stringAsUserSetter()

    def testBasic(self):
        # test for not crashing, is all
        userSetters = ParameterEnumerator(self.pipeline).enumerateUserSetters()
        for (id, setters) in userSetters.iteritems():
            print "----- ",id
            for (classname, modulefunctions) in setters:
                print "  -- ", classname
                for f in modulefunctions:
                    print "    ", f.stringAsUserSetter()

    def testParameterStudy(self):
        class TestI1(object):
            def stepCount(self):
                return 6
            def perform(self, pipeline, step):
                v1 = str(float(step / 6.0))
                v2 = str(float((step + 1) / 6.0))
                pipeline.modules[12].functions[0].params[0].strValue = v1
                pipeline.modules[12].functions[0].params[1].strValue = v2
        class TestI2(object):
            def stepCount(self):
                return 4
            def perform(self, pipeline, step):
                fv = 0.25 + (0.6 * (step / 4.0))
                v = str(fv)
                pipeline.modules[1].functions[0].params[1].strValue = v
        p = ParameterStudy()
        specs = [TestI1(), TestI2()]
        result, dims = p.parameterStudy(self.pipeline, specs)
        vtk_graph.run_many_pipelines(result, dims)

    def testCrash(self):
        p1 = copy.copy(self.pipeline)
        p2 = copy.copy(self.pipeline)
        vtk_graph.run_many_pipelines([((0,0), p1), ((1,0), p2)], (2,1))

    def testNoCrash(self):
        p1 = copy.copy(self.pipeline)
        vtk_graph.run_many_pipelines([((0,0), p1)], (1,1))

    def testParameterStudy2(self):
        p = ParameterStudy()
        specs = [InterpolateDiscreteParam(2,'GenerateValues',
                                          [(2, 0, 1.2),
                                           (5, 0, 1.2),
                                           (10, 0, 1.2),
                                           (20, 0, 1.2)]),
                 InterpolateFloatParam(8,'SetOpacity', (1.0, 0.2), 5)]
        result, dims = p.parameterStudy(self.pipeline2, specs)
        vtk_graph.run_many_pipelines(result, dims)

if __name__ == '__main__':
    import sys
    opt = sys.argv[1]
    tests = TestPipelineAnalyzer()
    tests.setUp()
    getattr(tests, opt)()
