import core.modules
import core.modules.module_registry
from core.modules.vistrails_module import Module, ModuleError
import scipy
import scipy.interpolate

# Numpy package imports
import Array
import ArrayAccess
import ArrayOperations
import ArrayUtilities
import ArrayConvert
import ArrayIO
import Imaging

# Scipy package imports
import Matrix
import MatrixUtilities
import DSP
import Filters
import EnsembleOrdering

version = '0.2.0'
name = 'Num-SciPy'
identifier = 'edu.utah.sci.vistrails.numpyscipy'

def initialize(*args, **keywords):
    reg = core.modules.module_registry
    basic = core.modules.basic_modules

    clslst = []
    
    #########################################################################################
    #  Numpy Registry
    reg.add_module(Array.NDArray, name="Numpy Array", namespace=Array.NDArray.my_namespace)
    reg.add_output_port(Array.NDArray, "self", (Array.NDArray, 'self'))
    reg.add_module(Matrix.Matrix, name="Scipy Matrix", namespace=Matrix.Matrix.my_namespace)
    
    
    #########################################################################################
    #  Array Access registry
    accessclass = [ArrayAccess.GetShape,
                   ArrayAccess.GetReals,
                   ArrayAccess.GetImaginaries,
                   ArrayAccess.GetMax,
                   ArrayAccess.GetMean,
                   ArrayAccess.GetMin,
                   ArrayAccess.GetDiagonal,
                   ArrayAccess.GetArrayAsType,
                   ArrayAccess.GetConjugate,
                   ArrayAccess.GetFlattenedArray,
                   ArrayAccess.GetField,
                   ArrayAccess.ToScalar,
                   ArrayAccess.GetMemoryFootprint,
                   ArrayAccess.GetArrayRank,
                   ArrayAccess.GetNonZeroEntries,
                   ArrayAccess.GetArraySize,
                   ArrayAccess.GetTranspose,
                   ArrayAccess.GetRowRange,
                   ArrayAccess.GetColumnRange,
                   ArrayAccess.GetRows]

    for cls in accessclass:
        cls.register(reg, basic)


    #########################################################################################
    #  Array Operations registry
    opclasses = [ArrayOperations.ArrayReshape,
                 ArrayOperations.ArrayCumulativeSum,
                 ArrayOperations.ArraySort,
                 ArrayOperations.ArrayCumulativeProduct,
                 ArrayOperations.ArrayFill,
                 ArrayOperations.ArrayResize,
                 ArrayOperations.ArrayExtractRegion,
                 ArrayOperations.ArrayRavel,
                 ArrayOperations.ArrayRound,
                 ArrayOperations.ArrayGetSigma,
                 ArrayOperations.ArraySum,
                 ArrayOperations.ArrayElementMultiply,
                 ArrayOperations.ArraySetElement,
                 ArrayOperations.ArrayVariance,
                 ArrayOperations.ArrayTrace,
                 ArrayOperations.ArraySwapAxes,
                 ArrayOperations.ArraySqueeze,
                 ArrayOperations.ArrayScalarMultiply,
                 ArrayOperations.ArrayAdd,
                 ArrayOperations.ArrayScalarAdd,
                 ArrayOperations.ArrayLog10,
                 ArrayOperations.ArrayAtan2,
                 ArrayOperations.ArraySqrt,
                 ArrayOperations.ArrayThreshold,
                 ArrayOperations.ArrayWindow,
                 ArrayOperations.ArrayNormalize]

    for cls in opclasses:
        cls.register(reg, basic)
                 

    #########################################################################################
    #  Array Convert registry
    convertclasses = [ArrayConvert.ArrayDumpToFile,
                      ArrayConvert.ArrayDumpToString,
                      ArrayConvert.ArrayToFile,
                      ArrayConvert.ArrayToString,
                      ArrayConvert.ArrayToMatrix,
                      ArrayConvert.ArrayToVTKImageData]
    
    for cls in convertclasses:
        cls.register(reg, basic)

    #########################################################################################
    #  Array IO registry
    ioclasses = [ArrayIO.ReadRAW,
                 ArrayIO.ReadNHDR,
                 ArrayIO.WriteRAW,
                 ArrayIO.WriteNHDR,
                 ArrayIO.ReadStatisticalSummary]

    try:
        import pylab
        ioclasses.append(ArrayIO.ReadPNG)
        ioclasses.append(ArrayIO.WritePNG)
    except:
        pass
    
    for cls in ioclasses:
        cls.register(reg, basic)

    #########################################################################################
    #  Array Imaging registry
    ar_util = [ArrayUtilities.ArrayToVTKScalars,
               ArrayUtilities.ArrayToTimeVaryingVTKScalars,
               ArrayUtilities.ArrayToTimeVaryingVTKVectors,
               ArrayUtilities.ArrayToVTKVectors,
               ArrayUtilities.VTKDataSetToPointArray]

    clslst.extend(ar_util)
    
    for cls in ar_util:
        cls.register(reg, basic)        

    #########################################################################################
    #  Array Imaging registry
    imclasses = [Imaging.ExtractRGBAChannel,
                 Imaging.GaussianGradientMagnitude,
                 Imaging.JointHistogram,
                 Imaging.GaussianSmooth,
                 Imaging.MedianFilter,
                 Imaging.ImageDifference,
                 Imaging.ImageNormalize,
                 Imaging.SobelGradientMagnitude]

    for cls in imclasses:
        cls.register(reg, basic)
        
    #########################################################################################
    #  Scipy Registry
    matrixclasses = [Matrix.MatrixMultiply,
                     Matrix.MatrixConjugate,
                     Matrix.MatrixToArray]

    for cls in matrixclasses:
        cls.register(reg,basic)

    #########################################################################################
    #  Scipy Matrix Utilities Registry
    matrixutils = [MatrixUtilities.MatlabReader,
                   MatrixUtilities.MatlabWriter]

    for cls in matrixutils:
        cls.register(reg, basic)

    #########################################################################################
    #  Scipy DSP Registry
    dspclasses = [DSP.FFT,
                  DSP.FFTN,
                  DSP.SignalSmoothing,
                  DSP.ShortTimeFourierTransform,
                  DSP.SignalGenerator]
#                  DSP.FrequencyPhaseLocking,
#                  DSP.SingleTrialPhaseLocking

    try:
        import smt
        import Stockwell
        dspclasses.append(Stockwell.StockwellTransform)
        dspclasses.append(Stockwell.MultiTaperStockwellTransform)
        dspclasses.append(Stockwell.FastStockwell3D)
        dspclasses.append(Stockwell.Stockwell2D)
        dspclasses.append(Stockwell.PyStockwellTransform)
        dspclasses.append(Stockwell.PointBasedStockwell)
        dspclasses.append(Stockwell.ScaleSpaceHistogram)
        dspclasses.append(Stockwell.PyScaleSpaceHistogram)
        dspclasses.append(Stockwell.MaximalScaleVolume)
        dspclasses.append(Stockwell.ScaleVolumes)
        dspclasses.append(Stockwell.IsotropicScaleVolumes)
        dspclasses.append(Stockwell.FrequencyPhaseLocking)
    except:
        pass

    for cls in dspclasses:
        cls.register(reg, basic)

    #########################################################################################
    #  Scipy Interpolation Registry
    interpclasses = []
    try:
        import ArrayInterpolate
        interpclasses.append(ArrayInterpolate.RBFInterpolate)
        interpclasses.append(ArrayInterpolate.BSplineInterpolate)
    except:
        pass

    interpclasses.append(ArrayInterpolate.BSplineResample)
    for cls in interpclasses:
        cls.register(reg, basic)

    #########################################################################################
    #  Scipy Windows Registry
    winclasses = [Filters.HanningWindow,
                  Filters.TriangularWindow,
                  Filters.BlackmanWindow,
                  Filters.BlackmanHarrisWindow,
                  Filters.ParzenWindow,
                  Filters.HammingWindow,
                  Filters.KaiserWindow,
                  Filters.BartlettHannWindow,
                  Filters.GaussianWindow,
                  Filters.BoxcarWindow,
                  Filters.BohmanWindow,
                  Filters.BartlettWindow,
                  Filters.NuttallBlackmanHarrisWindow]    

    for cls in winclasses:
        cls.register(reg, basic)

    #########################################################################################
    #  Scipy Signal Ensembles Registry
    ensembles = [EnsembleOrdering.OrderByIndexes,
                 EnsembleOrdering.OrderByCorrelation,
                 EnsembleOrdering.OrderByProgressiveCorrelation,
                 EnsembleOrdering.ComputeDistance]

    for cls in ensembles:
        cls.register(reg, basic)

    for cls in clslst:
        cls.register_ports(reg, basic)

    #########################################################################################    

def package_dependencies():
    import core.packagemanager
    manager = core.packagemanager.get_package_manager()
    if manager.has_package('edu.utah.sci.vistrails.vtk'):
        return ['edu.utah.sci.vistrails.vtk']
    else:
        return []
