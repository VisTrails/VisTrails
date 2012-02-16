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
input.file="I:\\VisTrails\\WorkingFiles\\workspace\\talbertc_20110519T121044\\TestTrainingSplit_1.csv"
output.dir="I:\\VisTrails\\WorkingFiles\\workspace\\talbertc_20110519T121044\\brtoutput_1"
rc="responseBinary"
PredictModel(workspace="I:\\VisTrails\\WorkingFiles\\workspace\\talbertc_20110519T130214\\brtoutput_1\\modelWorkspace",out.dir="C:\\VisTrails")
PredictModel(workspace="I:\\VisTrails\\WorkingFiles\\workspace\\talbertc_20110519T130214\\brtoutput_1\\modelWorkspace",out.dir="C:\\VisTrails\\mtalbert_20110505T161105",make.btif=TRUE,make.ptif=TRUE)
#######################################################
## BRT TESTING

output.dir="C:\\VisTrails\\mtalbert_20110504T132851"
    rc="ResponseBinary"
    input.file="C:\\VisTrails\\mtalbert_20110504T132851\\MergedDataSet_1.csv"

#this file does have a test training split
input.file="N:\\Active\\FORT_RAM\\VisTrails\\workspace\\mtalbert_20110602T155823\\MergedDataset_1.csv"
    rc="responseCount"
input.file="I:\\VisTrails\\WorkingFiles\\workspace\\morisettej_20110721T095017\\MergedDataset_2.csv"
output.dir="I:\\VisTrails\\WorkingFiles\\workspace\\morisettej_20110721T095017\\brtoutput_1"
rc="responseBinary"

input.file="I:\\VisTrails\\WorkingFiles\\workspace\\morisettej_20110721T134303\\TestTrainingSplit_1.csv"
output.dir="I:\\VisTrails\\WorkingFiles\\workspace\\morisettej_20110721T134303\\marsoutput_3"
rc="responseBinary"

fit.mars.fct(ma.name=input.file,
        tif.dir=NULL,output.dir=output.dir,
        response.col=rc,make.p.tif=F,make.binary.tif=F,
        mars.degree=1,mars.penalty=2,debug.mode=T,responseCurveForm="pdf",model.family="binomial",script.name="mars.r")

fit.brt.fct(ma.name=input.file,
      tif.dir=NULL,output.dir=output.dir,
      response.col=rc,test.resp.col="response",make.p.tif=F,make.binary.tif=F,
      simp.method="cross-validation",debug.mode=T,responseCurveForm="pdf",tc=NULL,n.folds=3,alpha=.3,script.name="brt.r",
      learning.rate =NULL, bag.fraction = 0.5,prev.stratify = TRUE, max.trees = NULL,opt.methods=1,seed=1,save.model=TRUE)

source("FIT_MARS_pluggable.r")
PredictModel(workspace=paste("C:\\VisTrails\\mtalbert_20110504T132851","modelWorkspace",sep="\\"),out.dir="C:\\VisTrails")
           
#########################################################
## MARS TESTING
output.dir="C:\\VisTrails\\mtalbert_20110504T132851"

    #this input file does not have a test training split
    input.file="C:\\VisTrails\\mtalbert_20110504T132851\\MergedDataSet_1.csv"
    rc="ResponseBinary"
    
    #this file does have a test training split
    input.file<-"I:\\VisTrails\\WorkingFiles\\workspace\\talbertc_20110519T121044\\TestTrainingSplit_1.csv"
    rc="responseBinary"
    
fit.mars.fct(ma.name=input.file,
        tif.dir=NULL,output.dir=output.dir,
        response.col=rc,make.p.tif=F,make.binary.tif=F,
        mars.degree=1,mars.penalty=2,debug.mode=F,responseCurveForm="pdf",model.family="binomial",script.name="mars.r")

PredictModel(workspace=paste("C:\\VisTrails\\mtalbert_20110504T132851","modelWorkspace",sep="\\"),out.dir="C:\\VisTrails")

#########################################################
## GLM TESTING
output.dir="C:\\VisTrails\\mtalbert_20110504T132851"
    rc="ResponseBinary"
    input.file="C:\\VisTrails\\mtalbert_20110504T132851\\MergedDataSet_1.csv"

#this file does have a test training split
    input.file<-"I:\\VisTrails\\WorkingFiles\\workspace\\talbertc_20110519T121044\\TestTrainingSplit_1.csv"
    rc="responseBinary"
    
fit.glm.fct(ma.name=input.file,
      tif.dir=NULL,
      output.dir=output.dir,
      response.col=rc,make.p.tif=F,make.binary.tif=F,
      simp.method="AIC",debug.mode=T,responseCurveForm="pdf",script.name="glm.r")

PredictModel(workspace=paste("C:\\VisTrails\\mtalbert_20110504T132851","modelWorkspace",sep="\\"),out.dir="C:\\VisTrails")

########################################################
## RANDOM FOREST TESTING
output.dir="C:\\VisTrails\\mtalbert_20110504T132851"
    rc="ResponseBinary"
    input.file="C:\\VisTrails\\mtalbert_20110504T132851\\MergedDataSet_1.csv"

#this file does have a test training split
    input.file<-"I:\\VisTrails\\WorkingFiles\\workspace\\talbertc_20110519T121044\\TestTrainingSplit_1.csv"
    rc="responseBinary"
    
fit.rf.fct(ma.name=input.file,
  tif.dir=NULL,
  output.dir=output.dir,
  response.col=rc,make.p.tif=F,make.binary.tif=F,
      debug.mode=T,n.trees=1000)

PredictModel(workspace=paste("C:\\VisTrails\\mtalbert_20110504T132851","modelWorkspace",sep="\\"),out.dir="C:\\VisTrails")
      
      
#Now testing to make sure this code works with no test training split
ma.name<-"H:\\Desktop\\SAHM\\Rcode\\ExposingModelParameters\\ModelOutputCheck\\NewInput.csv"
ma.name="C:\\VisTrails\\mtalbert_20110406T093111\\sahm4h5b1t.mds"

ma.name="I:\\VisTrails\\WorkingFiles\\workspace\\GYA_demo\\test.csv"
fit.brt.fct(ma.name=ma.name,
      tif.dir=NULL,output.dir="H:\\Desktop\\SAHM\\Rcode\\ExposingModelParameters\\PDFCheck",
      response.col="ResponseBinary",test.resp.col="response",make.p.tif=T,make.binary.tif=T,
            simp.method="cross-validation",debug.mode=T,responseCurveForm="pdf",tc=NULL,n.folds=3,alpha=1,script.name="brt.r",
           learning.rate =NULL, bag.fraction = 0.5,prev.stratify = TRUE, model.family = "bernoulli", max.trees = NULL)


#this is the GLM_pluggable1.r under NewMDSBuilder (Works with new vistrails format)
input.file="I:\\VisTrails\\WorkingFiles\\workspace\\talbertc_20110510T100421\\TestTrainingSplit_1.csv"
output.dir="C:\\VisTrails\\mtalbert_20110504T132851"
rc="responseCount"

      fit.glm.fct(ma.name=input.file,
      tif.dir=NULL,output.dir="H:\\Desktop\\SAHM\\Rcode\\ExposingModelParameters\\PDFCheck",
      response.col=rc,make.p.tif=T,make.binary.tif=T,
      simp.method="AIC",debug.mode=T,responseCurveForm="pdf",script.name="glm.r")


#Mars check Works with new vistrails format
      fit.mars.fct(ma.name=ma.name,
        tif.dir=NULL,output.dir="H:\\Desktop\\SAHM\\Rcode\\ExposingModelParameters\\PDFCheck",
        response.col="ResponseBinary",test.resp.col="response",make.p.tif=T,make.binary.tif=T,
            mars.degree=1,mars.penalty=2,debug.mode=T,responseCurveForm="pdf",ma.test=NULL,model.family="binomial",script.name="mars.r")


fit.rf.fct(ma.name="I:\\VisTrails\\WorkingFiles\\workspace\\GYA_demo\\test.csv",
  tif.dir=NULL,
  output.dir="H:\\Desktop\\SAHM\\Rcode\\ExposingModelParameters\\PDFCheck",
  response.col="ResponseBinary",test.resp.col="response",make.p.tif=T,make.binary.tif=T,
      debug.mode=T,n.trees=1000,ma.test=NULL,make.r.curves=T,script.name="glm.r")



#this one does not subset paths set up in the old way works with old sahm as well as for
fit.brt.fct(ma.name="H:\\Desktop\\SAHM\\Data\\CanadaThistle\\canadathistle_gcs_grp_r_mds_train.mds",
tif.dir="H:\\Desktop\\SAHM\\Data\\CanadaThistle\\layers",output.dir="H:\\Desktop\\SAHM\\Rcode\\ExposingModelParameters\\PDFCheck",
response.col="response.binary",test.resp.col="response",make.p.tif=T,make.binary.tif=T,
      simp.method="cross-validation",debug.mode=T,responseCurveForm="pdf",tc=NULL,n.folds=3,ma.test=NULL,alpha=1,script.name="brt.r",
     learning.rate =NULL, bag.fraction = 0.5,prev.stratify = TRUE, model.family = "bernoulli", max.trees = NULL)
     

fit.mars.fct(ma.name="H:\\Desktop\\SAHM\\Data\\CanadaThistle\\canadathistle_gcs_grp_r_mds_train.mds",
  tif.dir="H:\\Desktop\\SAHM\\Data\\CanadaThistle\\layers",
  output.dir="H:\\Desktop\\SAHM\\Rcode\\ExposingModelParameters\\PDFCheck",
  response.col="response.binary",test.resp.col="response",make.p.tif=T,make.binary.tif=T,
      mars.degree=1,mars.penalty=2,debug.mode=T,responseCurveForm="pdf",ma.test=NULL,model.family="binomial",script.name="mars.r")

fit.glm.fct(ma.name="H:\\Desktop\\SAHM\\Data\\CanadaThistle\\canadathistle_gcs_grp_r_mds_train.mds",
  tif.dir="H:\\Desktop\\SAHM\\Data\\CanadaThistle\\layers",
  output.dir="H:\\Desktop\\SAHM\\Rcode\\ExposingModelParameters\\PDFCheck",
  response.col="response.binary",test.resp.col="response",make.p.tif=T,make.binary.tif=T,
      simp.method="AIC",debug.mode=T,responseCurveForm="pdf",ma.test=NULL,script.name="glm.r")
  