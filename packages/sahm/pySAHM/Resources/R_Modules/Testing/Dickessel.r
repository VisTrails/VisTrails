 setwd("I:\\VisTrails\\Central_VisTrailsInstall_debug\\vistrails\\packages\\sahm\\pySAHM\\Resources\\R_Modules")
source("FIT_BRT_pluggable.r")
source("FIT_MARS_pluggable.r")
source("FIT_RF_pluggable.r")
source("FIT_GLM_pluggable.r")

source("EvaluationStats.r")
source("TestTrainRocPlot.r")
source("read.ma.r")
source("proc.tiff.r")
source("PredictModel.r")

# Currently testing to see if models work with
#  * new test train split
#  * separation of model fit from prediction
#  * working with count data
#  * producing correct evaluation metrics
#Future testing will include testing that factor columns are handled correctly
#trace(proc.tiff,browser)
#options(error=expression(if(interactive()) recover() else dump.calls()))
#options(error=NULL)
#trace(proc.tiff,browser)
#################################################################################
## Testing the code with some dickessel data

 ## EAME
 input.file="I:\\NPS_NPMP_data\\ModelingSession_June\\EAME_MDS.csv"
    rc="responseCount"
 output.dir="C:\\VisTrails\\EAMENoTestTrain"

## DICK
 input.file="I:\\NPS_NPMP_data\\ModelingSession_June\\DICK_MDS.csv"
    rc="responseCount"
 output.dir="C:\\VisTrails\\DICKNoTestTrain"
 
## HESP
 input.file="I:\\NPS_NPMP_data\\ModelingSession_June\\HESP_MDS.csv"
    rc="responseCount"
 output.dir="C:\\VisTrails\\HESPNoTestTrain"
 
 ## GRSP
 input.file="I:\\NPS_NPMP_data\\ModelingSession_June\\GRSP_MDS.csv"
    rc="responseCount"
 output.dir="C:\\VisTrails\\GRSPNoTestTrain"

input.file="I:\\VisTrails\\WorkingFiles\\workspace\\talbertc_20110623T104642\\SelectPredictorsLayers_second_1.csv"
fit.brt.fct(ma.name=input.file,
      tif.dir=NULL,output.dir=output.dir,
      response.col=rc,test.resp.col="response",make.p.tif=F,make.binary.tif=F,
      simp.method="cross-validation",debug.mode=T,responseCurveForm="pdf",tc=NULL,n.folds=3,alpha=.3,script.name="brt.r",
      learning.rate =NULL, bag.fraction = 0.5,prev.stratify = TRUE, model.family = "binomial", opt.methods=1,seed=1,save.model=FALSE)

#  No Predictions here
#  PredictModel(workspace=paste("C:\\VisTrails\\EAMENoTestTrain","modelWorkspace",sep="\\"),out.dir="C:\\VisTrails")

fit.glm.fct(ma.name=input.file,
      tif.dir=NULL,
      output.dir=output.dir,
      response.col=rc,make.p.tif=F,make.binary.tif=F,
      simp.method="AIC",debug.mode=T,responseCurveForm="pdf",script.name="glm.r",model.family="binomial",save.model=FALSE)

  #PredictModel(workspace=paste("C:\\VisTrails\\EAMENoTestTrain","modelWorkspace",sep="\\"),out.dir="C:\\VisTrails")
  
      fit.mars.fct(ma.name=input.file,
        tif.dir=NULL,output.dir=output.dir,
        response.col=rc,make.p.tif=F,make.binary.tif=F,
        mars.degree=1,mars.penalty=2,debug.mode=T,responseCurveForm="pdf",model.family="poisson",script.name="mars.r",save.model=FALSE)

    #PredictModel(workspace=paste("C:\\VisTrails\\EAMENoTestTrain","modelWorkspace",sep="\\"),out.dir="C:\\VisTrails")
    

 
#######################################################
### Now with a test/train split
#################################################
## GRSP
input.file="C:\\VisTrails\\GRSP_TestTrain.csv"
    rc="responseCount"
 output.dir="C:\\VisTrails\\GRSPTest"
 
 
input.file="C:\\VisTrails\\HESP_TestTrain.csv"
    rc="responseCount"
 output.dir="C:\\VisTrails\\HESPTest"
 
input.file="C:\\VisTrails\\EAME_TestTrain.csv"
    rc="responseCount"
 output.dir="C:\\VisTrails\\EAMETest"
input.file="N:\\Active\\FORT_RAM\\VisTrails\\workspace\\talbertc_20110622T083717\\TestTrainingSplit_1"
    rc="responseCount"
 output.dir="N:\\Active\\FORT_RAM\\VisTrails\\workspace\\talbertc_20110622T083717"
 
############################################################
### Testing with binary data

  ## EAME
 input.file="I:\\NPS_NPMP_data\\ModelingSession_June\\EAME_MDS_binary.csv"
    rc="responseBinary"
 output.dir="C:\\VisTrails\\EAMEBin"

## DICK
 input.file="I:\\NPS_NPMP_data\\ModelingSession_June\\DICK_MDS_binary.csv"
    rc="responseBinary"
 output.dir="C:\\VisTrails\\DICKBin"

## HESP
 input.file="I:\\NPS_NPMP_data\\ModelingSession_June\\HESP_MDS_binary.csv"
    rc="responseBinary"
 output.dir="C:\\VisTrails\\HESPBin"

 ## GRSP
 input.file="I:\\NPS_NPMP_data\\ModelingSession_June\\GRSP_MDS_binary.csv"
    rc="responseBinary"
 output.dir="C:\\VisTrails\\GRSPBin"

input.file="N:\\Active\\FORT_RAM\\VisTrails\\workspace\\talbertc_20110622T083717\\TestTrainingSplit_1.csv"
    rc="responseCount"
 output.dir="N:\\Active\\FORT_RAM\\VisTrails\\workspace\\talbertc_20110622T083717"
input.file="N:\\Active\\FORT_RAM\\VisTrails\\workspace\\talbertc_20110622T113117\\TestTrainingSplit_1.csv"
input.file="N:\\Active\\FORT_RAM\\VisTrails\\workspace\\talbertc_20110622T113117\\MergedDataset_2.csv"
fit.brt.fct(ma.name=input.file,
      tif.dir=NULL,output.dir=output.dir,
      response.col=rc,test.resp.col="response",make.p.tif=F,make.binary.tif=F,
      simp.method="cross-validation",debug.mode=T,responseCurveForm="pdf",tc=NULL,n.folds=3,alpha=1,script.name="brt.r",
      learning.rate =NULL, bag.fraction = 0.5,prev.stratify = TRUE, model.family = "binomial", opt.methods=1,seed=1,save.model=FALSE)

#  No Predictions here
#  PredictModel(workspace=paste("C:\\VisTrails\\EAMENoTestTrain","modelWorkspace",sep="\\"),out.dir="C:\\VisTrails")

fit.glm.fct(ma.name=input.file,
      tif.dir=NULL,
      output.dir=output.dir,
      response.col=rc,make.p.tif=F,make.binary.tif=F,
      simp.method="AIC",debug.mode=T,responseCurveForm="pdf",script.name="glm.r",model.family="binomial",save.model=FALSE)

  #PredictModel(workspace=paste("C:\\VisTrails\\EAMENoTestTrain","modelWorkspace",sep="\\"),out.dir="C:\\VisTrails")

      fit.mars.fct(ma.name=input.file,
        tif.dir=NULL,output.dir=output.dir,
        response.col=rc,make.p.tif=F,make.binary.tif=F,
        mars.degree=1,mars.penalty=2,debug.mode=T,responseCurveForm="pdf",model.family="binomial",script.name="mars.r",save.model=FALSE)

    #PredictModel(workspace=paste("C:\\VisTrails\\EAMENoTestTrain","modelWorkspace",sep="\\"),out.dir="C:\\VisTrails")

fit.rf.fct(ma.name=input.file,
  tif.dir=NULL,
  output.dir=output.dir,
  response.col=rc,make.p.tif=F,make.binary.tif=F,
      debug.mode=T,n.trees=1000,save.model=FALSE)


###################################################################################
## testing  with binary with a test train split
  ## EAME
 input.file="C:\\VisTrails\\EAMEBinTT.csv"
    rc="responseBinary"
 output.dir="C:\\VisTrails\\EAMEBinTT"

## DICK
 input.file="C:\\VisTrails\\DICKBinTT.csv"
    rc="responseBinary"
 output.dir="C:\\VisTrails\\DICKBinTT"

## HESP
 input.file="C:\\VisTrails\\HESPBinTT.csv"
    rc="responseBinary"
 output.dir="C:\\VisTrails\\HESPBinTT"

 ## GRSP
 input.file="C:\\VisTrails\\GRSPBinTT.csv"
    rc=r"responseBinary"
 output.dir="C:\\VisTrails\\GRSPBinTT"

fit.brt.fct(ma.name=input.file,
      tif.dir=NULL,output.dir=output.dir,
      response.col=rc,test.resp.col="response",make.p.tif=F,make.binary.tif=F,
      simp.method="cross-validation",debug.mode=T,responseCurveForm="pdf",tc=NULL,n.folds=3,alpha=1,script.name="brt.r",
      learning.rate =NULL, bag.fraction = 0.5,prev.stratify = TRUE, model.family = "binomial", opt.methods=1,seed=1,save.model=FALSE)

#  No Predictions here
#  PredictModel(workspace=paste("C:\\VisTrails\\EAMENoTestTrain","modelWorkspace",sep="\\"),out.dir="C:\\VisTrails")

fit.glm.fct(ma.name=input.file,
      tif.dir=NULL,
      output.dir=output.dir,
      response.col=rc,make.p.tif=F,make.binary.tif=F,
      simp.method="AIC",debug.mode=T,responseCurveForm="pdf",script.name="glm.r",model.family="binomial",save.model=FALSE)

  #PredictModel(workspace=paste("C:\\VisTrails\\EAMENoTestTrain","modelWorkspace",sep="\\"),out.dir="C:\\VisTrails")

      fit.mars.fct(ma.name=input.file,
        tif.dir=NULL,output.dir=output.dir,
        response.col=rc,make.p.tif=F,make.binary.tif=F,
        mars.degree=1,mars.penalty=2,debug.mode=T,responseCurveForm="pdf",model.family="binomial",script.name="mars.r",save.model=FALSE)

    #PredictModel(workspace=paste("C:\\VisTrails\\EAMENoTestTrain","modelWorkspace",sep="\\"),out.dir="C:\\VisTrails")

fit.rf.fct(ma.name=input.file,
  tif.dir=NULL,
  output.dir=output.dir,
  response.col=rc,make.p.tif=F,make.binary.tif=F,
      debug.mode=T,n.trees=1000,save.model=FALSE)

input.file="N:\\Active\\FORT_RAM\\VisTrails\\workspace\\talbertc_20110621T083827\\MergedDataset_1.csv"
input.file="N:\\Active\\FORT_RAM\\VisTrails\\workspace\\talbertc_20110621T112620\\TestTrainingSplit_1.csv"

input.file="N:\\Active\\FORT_RAM\\VisTrails\\workspace\\talbertc_20110621T114212\\MergedDataset_1.csv"

input.file="N:\\Active\\FORT_RAM\\VisTrails\\workspace\\talbertc_20110621T115847\\TestTrainingSplit_2.csv"
   rc="responseBinary"
output.dir="C:\\VisTrails"

input.file="N:\\Active\\FORT_RAM\\VisTrails\\workspace\\talbertc_20110621T134656\\TestTrainingSplit_1.csv"
rc="responseCount"
fit.glm.fct(ma.name=input.file,
      tif.dir=NULL,
      output.dir=output.dir,
      response.col=rc,make.p.tif=T,make.binary.tif=T,
      simp.method="AIC",debug.mode=T,responseCurveForm="pdf",script.name="glm.r",model.family="binomial",save.model=FALSE)

input.file="N:\\Active\\FORT_RAM\\VisTrails\\workspace\\talbertc_20110621T114212\\MergedDataset_1.csv"
fit.brt.fct(ma.name=input.file,
      tif.dir=NULL,output.dir=output.dir,
      response.col=rc,test.resp.col="response",make.p.tif=F,make.binary.tif=F,
      simp.method="cross-validation",debug.mode=T,responseCurveForm="pdf",tc=NULL,n.folds=3,alpha=1,script.name="brt.r",
      learning.rate =NULL, bag.fraction = 0.5,prev.stratify = TRUE, model.family = "binomial", opt.methods=1,seed=1,save.model=FALSE)
 
 
C:\R-2.12.1\bin\i386\Rterm.exe --vanilla -f I:\VisTrails\Central_VisTrailsInstall_debug\vistrails\packages\sahm\pySAHM\Resources\R_Modules\FIT_RF_pluggable.r --args  mbt=FALSE mpt=FALSE c=N:\Active\FORT_RAM\VisTrails\workspace\dignizio_20110616T162343\TestTrainingSplit_4.csv o=N:\Active\FORT_RAM\VisTrails\workspace\dignizio_20110616T162343\rfoutput_7 rc=responseBinary
C:\R-2.12.1\bin\i386\Rterm.exe --vanilla -f I:\VisTrails\Central_VisTrailsInstall_debug\vistrails\packages\sahm\pySAHM\Resources\R_Modules\PairsExplore.r --args i=N:\Active\FORT_RAM\VisTrails\workspace\talbertc_20110621T083827\MergedDataset_1.csv o=N:\Active\FORT_RAM\VisTrails\workspace\talbertc_20110621T083827\PredictorCorrelation_second_1.jpg m=0.7 rc=responseBinary pres=TRUE absn=TRUE bgd=TRUE
C:\R-2.12.1\bin\i386\Rterm.exe --vanilla -f I:\VisTrails\Central_VisTrailsInstall_debug\vistrails\packages\sahm\pySAHM\Resources\R_Modules\FIT_BRT_pluggable.r --args  c=N:\Active\FORT_RAM\VisTrails\workspace\talbertc_20110621T105356\TestTrainingSplit_1.csv o=N:\Active\FORT_RAM\VisTrails\workspace\talbertc_20110621T105356\brtoutput_1 rc=responseBinary