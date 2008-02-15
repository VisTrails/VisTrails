import core.modules
import core.modules.module_registry
from core.modules.vistrails_module import Module, ModuleError

# Numpy package imports
from Array import *
from ArrayAccess import *
from ArrayOperations import *
from ArrayConvert import *

# Scipy package imports
from Matrix import *
from MatrixUtilities import *
from DSP import *
from Filters import *

version = '0.1.3'
name = 'Num-SciPy'
identifier = 'edu.utah.sci.vistrails.numpyscipy'

def initialize(*args, **keywords):
    reg = core.modules.module_registry
    basic = core.modules.basic_modules

    #########################################################################################
    #  Numpy Registry
    reg.add_module(NDArray, name="Numpy Array", namespace=NDArray.my_namespace)
    
    #########################################################################################
    #  Array Access registry
    accessclass = [GetShape,
                   GetReals,
                   GetImaginaries,
                   GetMax,
                   GetMean,
                   GetMin,
                   GetDiagonal,
                   GetArrayAsType,
                   GetConjugate,
                   GetFlattenedArray,
                   GetField,
                   ToScalar,
                   GetMemoryFootprint,
                   GetArrayRank,
                   GetNonZeroEntries,
                   GetArraySize,
                   GetTranspose,
                   GetRowRange,
                   GetColumnRange]

    for cls in accessclass:
        cls.register(reg, basic)


    #########################################################################################
    #  Array Operations registry
    opclasses = [ArrayReshape,
                 ArrayCumulativeSum,
                 ArraySort,
                 ArrayCumulativeProduct,
                 ArrayFill,
                 ArrayResize,
                 ArrayRavel,
                 ArrayRound,
                 ArrayGetSigma,
                 ArraySum,
                 ArrayElementMultiply,
                 ArraySetElement,
                 ArrayVariance,
                 ArrayTrace,
                 ArraySwapAxes,
                 ArraySqueeze]

    for cls in opclasses:
        cls.register(reg, basic)
                 

    #########################################################################################
    #  Array Convert registry
    convertclasses = [ArrayDumpToFile,
                     ArrayDumpToString,
                     ArrayToFile,
                     ArrayToString]
    
    for cls in convertclasses:
        cls.register(reg, basic)

    #########################################################################################
    #  Scipy Registry
    reg.add_module(Matrix, name="Scipy Matrix", namespace=Matrix.my_namespace)
    
    matrixclasses = [MatrixMultiply,
                     MatrixConjugate,
                     MatrixToArray]

    for cls in matrixclasses:
        cls.register(reg,basic)

    #########################################################################################
    #  Scipy Matrix Utilities Registry
    matrixutils = [MatlabReader]

    for cls in matrixutils:
        cls.register(reg, basic)

    #########################################################################################
    #  Scipy DSP Registry
    dspclasses = [FFT,
                  FFTN,
                  ShortTimeFourierTransform]

    for cls in dspclasses:
        cls.register(reg, basic)

    #########################################################################################
    #  Scipy Windows Registry
    winclasses = [HanningWindow,
                  TriangularWindow,
                  BlackmanWindow,
                  BlackmanHarrisWindow,
                  ParzenWindow,
                  HammingWindow,
                  KaiserWindow,
                  BartlettHannWindow,
                  GaussianWindow,
                  BoxcarWindow,
                  BohmanWindow,
                  BartlettWindow,
                  NuttallBlackmanHarrisWindow]

    for cls in winclasses:
        cls.register(reg, basic)
