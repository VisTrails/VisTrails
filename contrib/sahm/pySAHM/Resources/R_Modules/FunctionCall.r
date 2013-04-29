setwd("I:\\VisTrails\\Central_VisTrailsInstall_debug\\vistrails\\packages\\sahm\\pySAHM\\Resources\\R_Modules")
source("FIT_BRT_pluggable.r")
source("FIT_MARS_pluggable.r")
source("FIT_RF_pluggable.r")
source("FIT_GLM_pluggable.r")

source("EvaluationStats.r")
source("TestTrainRocPlot.r")
source("PredictModel.r")
source("read.ma.r")
source("proc.tiff.r")

# Curr
#trace(proc.tiff,browser)
#options(error=expression(if(interactive()) recover() else dump.calls()))
#options(error=NULL)

output.dir="C:\\VisTrails\\mtalbert_20110504T132851"
    rc="ResponseBinary"
    input.file="C:\\VisTrails\\mtalbert_20110504T132851\\MergedDataSet_1.csv"
      fit.brt.fct(ma.name=input.file,
      tif.dir=NULL,output.dir=output.dir,
      response.col="ResponseBinary",test.resp.col="response",make.p.tif=F,make.binary.tif=F,
            simp.method="cross-validation",debug.mode=T,responseCurveForm="pdf",tc=NULL,n.folds=3,alpha=1,script.name="brt.r",
           learning.rate =NULL, bag.fraction = 0.5,prev.stratify = TRUE, model.family = "bernoulli", max.trees = NULL,opt.methods=1,seed=1,save.model=TRUE)

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
  