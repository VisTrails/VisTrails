import core.modules
import core.modules.module_registry
from core.modules.vistrails_module import Module, ModuleError

# Numpy package imports
from Array import *
from ArrayAccess import *
from ArrayOperations import *
from ArrayConvert import *
from ArrayIO import *
from Imaging import *

# Scipy package imports
from Matrix import *
from MatrixUtilities import *
from DSP import *
from Filters import *
from EnsembleOrdering import *

version = '0.1.3'
name = 'Num-SciPy'
identifier = 'edu.utah.sci.vistrails.numpyscipy'

def initialize(*args, **keywords):
    reg = core.modules.module_registry
    basic = core.modules.basic_modules

    #########################################################################################
    #  Numpy Registry
    reg.add_module(NDArray, name="Numpy Array", namespace=NDArray.my_namespace)
    reg.add_output_port(NDArray, "self", (NDArray, 'self'))
    
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
                 ArrayExtractRegion,
                 ArrayRavel,
                 ArrayRound,
                 ArrayGetSigma,
                 ArraySum,
                 ArrayElementMultiply,
                 ArraySetElement,
                 ArrayVariance,
                 ArrayTrace,
                 ArraySwapAxes,
                 ArraySqueeze,
                 ArrayScalarMultiply,
                 ArrayAdd,
                 ArrayScalarAdd,
                 ArrayLog10]

    for cls in opclasses:
        cls.register(reg, basic)
                 

    #########################################################################################
    #  Array Convert registry
    convertclasses = [ArrayDumpToFile,
                      ArrayDumpToString,
                      ArrayToFile,
                      ArrayToString,
                      ArrayToMatrix,
                      ArrayToVTKImageData]
    
    for cls in convertclasses:
        cls.register(reg, basic)

    #########################################################################################
    #  Array IO registry
    ioclasses = [ReadRAW,
                 ReadNHDR]
    try:
        import pylab
        ioclasses.append(ReadPNG)
    except:
        pass
    
    for cls in ioclasses:
        cls.register(reg, basic)

    #########################################################################################
    #  Array Imaging registry
    imclasses = [ExtractRGBAChannel,
                 GaussianGradientMagnitude,
                 JointHistogram,
                 GaussianSmooth,
                 MedianFilter,
                 ImageDifference,
                 ImageNormalize]

    for cls in imclasses:
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
    matrixutils = [MatlabReader,
                   MatlabWriter]

    for cls in matrixutils:
        cls.register(reg, basic)

    #########################################################################################
    #  Scipy DSP Registry
    dspclasses = [FFT,
                  FFTN,
                  ShortTimeFourierTransform,
                  StockwellTransform]

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

    #########################################################################################
    #  Scipy Signal Ensembles Registry
    ensembles = [OrderByIndexes,
                 OrderByCorrelation]

    for cls in ensembles:
        cls.register(reg, basic)

def package_dependencies():
    import core.packagemanager
    manager = core.packagemanager.get_package_manager()
    if manager.has_package('edu.utah.sci.vistrails.vtk'):
        return ['edu.utah.sci.vistrails.vtk']
    else:
        return []
