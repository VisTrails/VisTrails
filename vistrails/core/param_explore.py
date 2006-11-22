"""
This module handles Parameter Exploration in VisTrails
"""
from core.vistrail.module_function import ModuleFunction
from core.vistrail.module_param import ModuleParam
################################################################################

class ParameterExploration(object):
    """
    ParameterExploration is a class that will take a pipeline and a
    set of parameter values and executes all of them

    """
    
    def __init__(self, stepCounts, specs):
        """ ParameterExploration(specs: list) -> ParameterExploration
        Takes a list of interpolator list. The number of items in the
        list is also the number of dimensions this parameter
        exploration is going to explore on
        
        """
        self.stepCounts = stepCounts
        self.specs = specs

    def explore(self, pipeline):
        """ explore(pipeline: VisPipeline) -> list[VisPipeline]        
        Apply parameter exploration on multiple dimensions using the
        values in self.specs and the number of steps in
        self.stepCounts per each dimension
        
        """
        pipelineList = [pipeline]
        for i in range(len(self.specs)):
            pipelineList = interpolateList(pipelineList, self.specs[i])
        return pipelineList

    def interpolateList(self, pipelineList, interpList):
        """ interpolateList(pipeline: list[VisPipeLine],
                            interpList: InterpolateDiscreteParam)
                            -> list[VisPipeline]                            
        Returns a list of interpolated pipelines, by applying the
        interpolators in a multiplication manner
        
        """
        if len(interpList)<1: return pipelineList
        stepCount = interpList[0].stepCount
        result = []
        for step in range(stepCount):
            for pipeline in pipelineList:
                newp = copy.copy(pipeline)
                for interp in interpList:
                    interp.perform(newp, step)
                result.append(newp)
        return result
    
class InterpolateDiscreteParam(object):
    """
    InterpolateDiscreteParam takes in ranges and a number of
    steps. Then given a pipeline, it will interpolate and generate a
    number of steps pipelines with values interpolated between the
    ranges
    
    """

    def __init__(self, module, function, ranges, stepCount):
        """ InterpolateDiscreteParam(module: int,
                                     function: str,
                                     ranges: list(tuple),
                                     stepCount: int)
                                     -> InterpolateDiscreteParam
                                     
        Initialize the interpolator with a specific module function
        given a list of parameter ranges

        Keyword arguments:
        module    --- module id in a pipeline        
        function  --- a string express the function name that belongs
                      to module
                      
        ranges    --- [tupe(min,max) or tuple(s1,s2..,s{stepCount}],
                      ranges specified for each argument of function
                      where s{i} is of type 'str'
                      
        stepCount --- the number of step for the interpolation
                                     
        """
        self.module = module
        self.function = function
        self.stepCount = stepCount
        self.values = self.interpolate(ranges, stepCount)

    def interpolate(self, ranges, stepCount):
        """ interpolate(ranges: tuple, stepCount: int) -> list
        
        This function takes a number of (min,max) or (s1,...sn) to
        interpolate exact stepCount number of step. The output will be
        a list of stepCount elements where each of them is (a1,...,an).
        a{i} is either int or string and n is the number of arguments.
        
        """
        params = []
        for r in ranges:
            interpolatedValues = []
            argumentType = type(r[0])
            if argumentType in [int, float]:
                for i in range(stepCount):
                    if stepCount>1: t = i/float(stepCount-1)
                    else: t = 0
                    interpolatedValues.append(argumentType(r[0]+t*(r[1]-r[0])))
            elif argumentType==str:
                interpolatedValues = list(r)
            else:
                print 'Cannot interpolate non-cardinal types'
                assert False
            params.append(interpolatedValues)
        return zip(*params)
        
        
    def perform(self, pipeline, step):
        """ perform(pipeline: VisPipeline, step: int) -> None        
        This will takes a pipeline and apply the interpolated values
        at step 'step' to the pipeline. Then return the updated
        pipeline

        """
        m = pipeline.modules[self.module]
        f = ModuleFunction()
        f.name = self.function
        f.returnType = 'void'
        value = self.values[step]
        for v in value:
            p = ModuleParam()
            convert = {'int':'Integer', 'str':'String',
                       'float':'Float', 'double':'Float'}
            p.type = convert[type(v).__name__]
            p.strValue = str(v)
            f.params.append(p)
        m.functions.append(f)

################################################################################
        
import unittest

class TestParameterExploration(unittest.TestCase):
    """
    Test if ParameterExploration is executing correctly. For now it is a very
    simple test to test more of the interpolated values
    
    """
    def testInterpolator(self):
        interpolator = InterpolateDiscreteParam(0, 'testing',
                                                [(0,10),
                                                 (0.0,10.0),
                                                 ('one', 'two', 'three')],
                                                3)
        self.assertEqual(interpolator.values,
                         [(0, 0.0, 'one'),
                          (5, 5.0, 'two'),
                          (10, 10.0, 'three')])

if __name__ == '__main__':
    unittest.main()
