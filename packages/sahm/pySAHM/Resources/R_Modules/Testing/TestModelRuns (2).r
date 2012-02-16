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
source("PairsExplore.r")

# Currently testing to see if models work with
#  * new test train split
#  * separation of model fit from prediction
#  * working with count data
#  * producing correct evaluation metrics
#Future testing will include testing that factor columns are handled correctly


#################################################################
## Current test files
input.file<-vector()
input.file[1]="C:/VisTrails/mtalbert_20110504T132851/MergedDataSetNullModelTest.csv"
input.file[2]="C:/VisTrails/mtalbert_20110504T132851/MergedDataSetNullSplit.csv"
input.file[3]="C:/VisTrails/mtalbert_20110504T132851/MergedDataSetIncludeTest.csv"
input.file[4]="C:/VisTrails/mtalbert_20110504T132851/MergedDataSetIncludeSplit.csv"
input.file[5]="C:/VisTrails/mtalbert_20110504T132851/MergedDataSet_1.csv"
input.file[6]="C:/VisTrails/mtalbert_20110504T132851/MergedDataSplitTest.csv"
input.file[7]="C:/VisTrails/mtalbert_20110504T132851/MergedDataSetNullModelTest2.csv"
output.file<-sub("851/","851/TestOutput/",input.file)
output.file<-sub(".csv",".jpg",output.file)

#######################################################
Debug=FALSE
rc="ResponseBinary"
output.dir="C:/VisTrails/mtalbert_20110504T132851/TestOutput"

#BRT TEST LIST
      brt.list<-list()
      #this is the default scenario
      brt.list[[1]]<-list(make.p.tif=TRUE,
       			make.binary.tif=TRUE,
            tc=NULL,
       			n.folds=3,
       			alpha=1,
            learning.rate=NULL,
       			bag.fraction=.5,
       			model.family="\"bernoulli\"",
       			prev.stratify=TRUE,
       			max.trees=10000,
       			opt.methods=2,
       			seed=NULL,
       		  tolerance.method="\"auto\"",
       		  tolerance=.001,
             debug.mode=FALSE)
      #setting up some alternative scenarios
      brt.list[[2]]<-brt.list[[1]]
      brt.list[[2]]$learning.rate=.002

      brt.list[[3]]<-brt.list[[1]]
      brt.list[[3]]$bag.fraction=1
      brt.list[[3]]$opt.methods=4

      #which datasets to test with the given set of parameters
      brt.use.list<-list()
      brt.use.list[[1]]<-c(3,4,5)
      brt.use.list[[2]]<-c(5,6,7)
      brt.use.list[[3]]<-c(3)

#MARS TEST LIST
  mars.list<-list()
      #this is the default scenario
      mars.list[[1]]<-list(make.p.tif=T,
            make.binary.tif=T,
            mars.degree=1,
            mars.penalty=2,
            model.family="\"binomial\"",
            script.name="\"mars.r\"",
            opt.methods=2,
            save.model=TRUE,
             debug.mode=FALSE)
      #setting up some alternative scenarios
      mars.list[[2]]<-mars.list[[1]]
      mars.list[[2]]$mars.degree=2

      mars.list[[3]]<-mars.list[[1]]
      mars.list[[3]]$mars.penalty=3
      mars.list[[3]]$opt.methods=4

      #which datasets to test with the given set of parameters
      mars.use.list<-list()
      mars.use.list[[1]]<-c(3)
      mars.use.list[[2]]<-c(2,5,6,7)
      mars.use.list[[3]]<-c(3,4)

#GLM TEST LIST
  glm.list<-list()
      #this is the default scenario
      glm.list[[1]]<-list(make.p.tif=TRUE,
          make.binary.tif=TRUE,
          simp.method="\"AIC\"",
          model.family="\"binomial\"",
          opt.methods=2,
          save.model=FALSE,
          debug.mode=FALSE)
      #setting up some alternative scenarios
      glm.list[[2]]<-glm.list[[1]]
      glm.list[[2]]$simp.method="\"BIC\""

      glm.list[[3]]<-glm.list[[1]]
      glm.list[[3]]$opt.methods=4

      #which datasets to test with the given set of parameters
      glm.use.list<-list()
      glm.use.list[[1]]<-c(1,3)
      glm.use.list[[2]]<-c(2,5,6,7)
      glm.use.list[[3]]<-c(1,2,3,4)

#RF TEST LIST
  rf.list<-list()
      #this is the default scenario
      rf.list[[1]]<-list(make.p.tif=TRUE,
          make.binary.tif=TRUE,
          simp.method="\"AIC\"",
          model.family="\"binomial\"",
          opt.methods=2,
          save.model=FALSE,
          debug.mode=FALSE)
      #setting up some alternative scenarios
      rf.list[[2]]<-rf.list[[1]]
      rf.list[[2]]$simp.method="\"BIC\""

      rf.list[[3]]<-rf.list[[1]]
      rf.list[[3]]$opt.methods=4

      #which datasets to test with the given set of parameters
      rf.use.list<-list()
      rf.use.list[[1]]<-c(1,3)
      rf.use.list[[2]]<-c(2,5,6,7)
      rf.use.list[[3]]<-c(1,2,3,4)
      
parameter.list<-list(brt.list=brt.list,brt.use.list=brt.use.list,mars.list=mars.list,mars.use.list=mars.use.list,
    glm.list=glm.list,glm.use.list=glm.use.list,rf.list=rf.list,rf.use.list=rf.use.list)

Out<-TestFunction(input.file,parameter.list,Debug,rc,output.dir)


