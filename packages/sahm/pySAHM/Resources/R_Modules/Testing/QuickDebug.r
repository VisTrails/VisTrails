setwd("I:\\VisTrails\\Central_VisTrailsInstall_debug\\vistrails\\packages\\sahm\\pySAHM\\Resources\\R_Modules")
setwd("I:\\VisTrails\\Central_VisTrailsInstall\\vistrails\\packages\\sahm\\pySAHM\\Resources\\R_Modules")
source("FIT_BRT_pluggable.r")
source("FIT_MARS_pluggable.r")
source("FIT_RF_pluggable.r")
source("FIT_GLM_pluggable.r")

source("EvaluationStats.r")
source("TestTrainRocPlot.r")
source("read.maNew.r")
source("proc.tiff.r")
source("PredictModel.r")
source("PredictModel.r")
source("modalDialog.R")
source("check.libs.r")
options(error=expression(if(interactive()) recover() else dump.calls()))
options(error=NULL)
trace(proc.tiff,browser)

list.files()
#Testing Compile Output on data with no test train and with a test train


input.file="N:/Active/FORT_RAM/VisTrails/workspace/mtalbert_20110817T104421/MergedDataset_1.csv"
#input.file="N:/Active/FORT_RAM/VisTrails/workspace/mtalbert_20110817T104421/MergedDatasetTestTrain_1.csv"

#No test training split

#this one has a test training split

output.dir="C:\\temp\\SAHMDebugJunk\\BRTOut1"
rc="responseBinary"
input.file="I:\\VisTrails\\WorkingFiles\\workspace\\talbertc_20110824T133049\\CovariateCorrelationOutputMDS_anothertry.csv"
input.file="I:\\VisTrails\\WorkingFiles\\workspace\\talbertc_20110825T130119\\CovariateCorrelationOutputMDS_anothertry2.csv"
#input.file="I:\\VisTrails\\WorkingFiles\\workspace\\talbertc_20110824T133049\\CovariateCorrelationOutputMDS_anothertry2.csv"

##RF
    fit.rf.fct(ma.name=input.file,
      tif.dir=NULL,
      output.dir=output.dir,
      response.col=rc,make.p.tif=F,make.binary.tif=F,
          debug.mode=T,n.trees=1000,opt.methods=5)

    PredictModel(workspace=paste(output.dir,"modelWorkspace",sep="\\"),out.dir=output.dir)

##BRT
    fit.brt.fct(ma.name=input.file,
          tif.dir=NULL,output.dir=output.dir,
          response.col=rc,make.p.tif=F,make.binary.tif=F,
          simp.method="cross-validation",debug.mode=T,responseCurveForm="pdf",tc=NULL,n.folds=3,alpha=.3,script.name="brt.r",
          learning.rate =NULL, bag.fraction = 0.5,prev.stratify = TRUE, max.trees = NULL,opt.methods=2,seed=1,save.model=TRUE)
          
    PredictModel(workspace=paste("C:\\VisTrails\\mtalbert_20110504T132851","modelWorkspace",sep="\\"),out.dir="C:\\VisTrails")

##MARS
    fit.mars.fct(ma.name=input.file,
            tif.dir=NULL,output.dir=output.dir,
            response.col=rc,make.p.tif=F,make.binary.tif=F,
            mars.degree=1,mars.penalty=2,debug.mode=F,responseCurveForm="pdf",script.name="mars.r")

    PredictModel(workspace=paste("C:\\VisTrails\\mtalbert_20110504T132851","modelWorkspace",sep="\\"),out.dir="C:\\VisTrails")

##GLM
    fit.glm.fct(ma.name=input.file,
          tif.dir=NULL,
          output.dir=output.dir,
          response.col=rc,make.p.tif=F,make.binary.tif=F,
          simp.method="AIC",debug.mode=T,responseCurveForm="pdf",script.name="glm.r")

    PredictModel(workspace=paste("C:\\VisTrails\\mtalbert_20110504T132851","modelWorkspace",sep="\\"),out.dir="C:\\VisTrails")


## Command line
C:\R-2.12.1\bin\i386\Rterm.exe --vanilla -f I:\VisTrails\Central_VisTrailsInstall_debug\vistrails\packages\sahm\pySAHM\Resources\R_Modules\FIT_MARS_pluggable.r --args c=I:\VisTrails\WorkingFiles\workspace\talbertc_20110824T133049\CovariateCorrelationOutputMDS_anothertry2.csv o=I:\VisTrails\WorkingFiles\workspace\talbertc_20110824T133049\marsoutput_4 rc=responseBinary
C:\R-2.12.1\bin\i386\Rterm.exe --vanilla -f I:\VisTrails\Central_VisTrailsInstall\vistrails\packages\sahm\pySAHM\Resources\R_Modules\FIT_RF_pluggable.r --args c=I:\VisTrails\WorkingFiles\workspace\talbertc_20110825T130119\CovariateCorrelationOutputMDS_anothertry2.csv o=I:\VisTrails\WorkingFiles\workspace\talbertc_20110825T130119\rfoutput_1 rc=responseBinary
