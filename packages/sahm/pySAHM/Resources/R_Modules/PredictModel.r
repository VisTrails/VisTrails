PredictModel<-function(workspace=NULL,new.tifs=NULL,out.dir=NULL,thresh=NULL,make.btif=NULL,make.ptif=NULL){

#This functions separates the step of model fit from producing probability or binary surfaces
#the default is to read in a workspace and make predictions using the original tiffs supplied
#but if an mds with new tiff directories are supplied, the function will instead use these
#options are available for setting the threshold
#and true and false for whether to make binary or prob.tif

#my stuff to delete
#workspace=paste("C:\\VisTrails\\mtalbert_20110504T132851","modelWorkspace",sep="\\")
#new.tifs<-out$input$ma.name
#end delete

    load(workspace)

    if(!is.null(new.tifs)){

              ma.name <- new.tifs
                  #get the paths off of the new mds file
                      tif.info<-readLines(ma.name,3)
                      tif.info<-strsplit(tif.info,',')
                      include<-(as.numeric(tif.info[[2]]))
                      paths<-as.character(tif.info[[3]])

              paths<-paths[paths!=""]
            #this line needs to be changed eventually to deal with locations of model fit covaries from different models
            if(out$input$model.source.file=="brt.r") {model.covs<-levels(summary(out$mods$final.mod,plotit=FALSE)[,1])
            pred.fct=brt.predict
            }

            ma.cols <- match(model.covs,sub(".tif","",basename(paths)))
            paths<-paths[ma.cols]
            #checking that all tifs are present
            if(any(is.na(ma.cols))){

                              stop("ERROR: the following geotiff(s) are missing in ",
                                    tif.dir,":  ",paste(ma.names[-r.col][is.na(ma.cols)],collapse=" ,"),sep="")
                            }
            #checking that we have read access to all tiffs
             if(sum(file.access(paths),mode=0)!=0){
                              stop("ERROR: the following geotiff(s) are missing : ",
                                    paths[(file.access(paths)!=0),][1],sep="")

                            }
                            out$dat$tif.ind<-paths
      }

    if(out$input$model.source.file=="rf.r")   {
        pred.fct=rf.predict
        library(randomForest)
        }
    if(out$input$model.source.file=="mars.r") {
        pred.fct=pred.mars
        library(mda)
        }
    if(out$input$model.source.file=="glm.r")  pred.fct=glm.predict
    if(out$input$model.source.file=="brt.r")  {
        pred.fct=brt.predict
        library(gbm)
    }
    
    if(!is.null(thresh))out$mods$auc.output$thresh<-thresh
    if(!is.null(make.btif)) make.binary.tif<-make.btif
    if(!is.null(make.ptif)) make.p.tif<-make.ptif


       assign("Pred.Surface",Pred.Surface,envir=.GlobalEnv)
      mssg <- proc.tiff(model=out$mods$final.mod,vnames=as.character(out$mods$final.mod$contributions$var),
                  tif.dir=out$dat$tif.dir$dname,filenames=out$dat$tif.ind,pred.fct=pred.fct,factor.levels=out$dat$ma$factor.levels,make.binary.tif=make.binary.tif,
                  thresh=out$mods$auc.output$thresh,make.p.tif=make.p.tif,outfile.p=paste(out.dir,"prob_map.tif",sep="\\"),
                  outfile.bin=paste(out.dir,"bin_map.tif",sep="\\"),tsize=50.0,NAval=-3000,logname=logname,out=out)


}

brt.predict <- function(model,x) {
    # retrieve key items from the global environment #
    # make predictions from complete data only #
    #y <- rep(NA,nrow(x))
    #y[complete.cases(x)] <- predict.gbm(model, x[complete.cases(x),],model$target.trees,type="response")

    # make predictions from full data #
    y <- predict.gbm(model,x,model$target.trees,type="response")
    # encode missing values as -1.
     a<-complete.cases(x)
    y[!(a)]<- NaN

    # return predictions.
    return(y)
    }

pred.mars <- function(model,x) {
    # retrieve key items from the global environment #
    # make predictionss.
    y <- rep(NA,nrow(x))
    y[complete.cases(x)] <- as.vector(mars.predict(model,x[complete.cases(x),])$prediction[,1])

#if(sum(is.na(x))/dim(x)[2]!=sum(is.na(y)))
#h<-is.na(x)
#h<-apply(h,1,sum)
#h=h/35
#f<-is.na(y)
#which((h-f)!=0,arr.ind=TRUE)
#b<-cbind(x[which((h-f)!=0,arr.ind=TRUE),],y[which((h-f)!=0,arr.ind=TRUE)])

#which(is.na(y)
    # encode missing values as -1.
    y[is.na(y)]<- NaN

    # return predictions.
    return(y)
    }

glm.predict <- function(model,x) {
    # retrieve key items from the global environment #
    # make predictionss.

    y <- as.vector(predict(model,x,type="response"))

    # encode missing values as -1.
    y[is.na(y)]<- NaN

    # return predictions.
    return(y)
    }

"mars.predict" <-
function (mars.glm.object,new.data)
{
#
# j leathwick, j elith - August 2006
#
# version 3.1 - developed in R 2.3.1 using mda 0.3-1
#
# calculates a mars/glm object in which basis functions are calculated
# using an initial mars model with single or multiple responses
# data for individual species are then fitted as glms using the
# common set of mars basis functions with results returned as a list
#
# takes as input a dataset and args selecting x and y variables, and degree of interaction
# along with site and species weights, the CV penalty, and the glm family argument
# the latter would normally be one of "binomial" or "poisson" - "gaussian" could be used
# but in this case the model shouldn't differ from that fitted using mars on its own
#
# naming problem for dataframes fixed - je - 15/12/06
#
# requires mda and leathwick/elith's mars.export
#
  require(mda)

# first recreate both the original mars model and the glm model

# setup input data and create original temporary data

  dataframe.name <- mars.glm.object$mars.call$dataframe  # get the dataframe name
  mars.x <- mars.glm.object$mars.call$mars.x
  mars.y <- mars.glm.object$mars.call$mars.y
  n.spp <- length(mars.y)
  family <- mars.glm.object$mars.call$family
  mars.degree <- mars.glm.object$mars.call$degree
  penalty <- mars.glm.object$mars.call$penalty
  site.weights <- mars.glm.object$weights[[1]]
  spp.weights <- mars.glm.object$weights[[2]]

  print("creating original data frame...",quote=FALSE)

  base.data <- as.data.frame(eval.parent(parse(text = dataframe.name),n=3)) #aks

  x.temp <- eval(base.data[, mars.x])                 #form the temporary datasets
  base.names <- names(x.temp)

  xdat <- mars.new.dataframe(x.temp)[[1]]

  ydat <- as.data.frame(base.data[, mars.y])
  names(ydat) <- names(base.data)[mars.y]

  assign("xdat", xdat, pos = 1)               #and assign them for later use
  assign("ydat", ydat, pos = 1)

# now create the temporary dataframe for the new data

  print("checking variable matching with new data",quote = FALSE)

  new.names <- names(new.data)

  for (i in 1:length(base.names)) {

    name <- base.names[i]

    if (!(name %in% new.names)) {
      print(paste("Variable ",name," missing from new data",sep=""),quote = FALSE)  #aks
      return()
    }
  }

  print("and creating temporary dataframe for new data...",quote=FALSE)

  selector <- match(names(x.temp),names(new.data))

  pred.dat <- mars.new.dataframe(new.data[,selector])[[1]]

  assign("pred.dat", pred.dat, pos = 1)               #and assign them for later use

# fit the mars model and extract the basis functions

  print(paste("re-fitting initial mars model for",n.spp,"responses"),quote = FALSE)
  print(paste("using glm family of",family),quote = FALSE)

  #mars.fit <- mars(x = xdat, y = ydat, degree = mars.degree, w = site.weights,
  #  wp = spp.weights, penalty = penalty)

  mars.fit <- mars.glm.object$mars.object  #AKS

  old.bf.data <- as.data.frame(eval(mars.fit$x))
  n.bfs <- ncol(old.bf.data)
  bf.names <- paste("bf", 1:n.bfs, sep = "")
  old.bf.data <- as.data.frame(old.bf.data[,-1])
  names(old.bf.data) <- bf.names[-1]

  new.bf.data <- as.data.frame(mda:::model.matrix.mars(mars.fit,pred.dat))
  new.bf.data <- as.data.frame(new.bf.data[,-1])
  names(new.bf.data) <- bf.names[-1]

# now cycle through the species fitting glm models

  print("fitting glms for individual responses", quote = F)

  prediction <- as.data.frame(matrix(0, ncol = n.spp, nrow = nrow(pred.dat)))
  names(prediction) <- names(ydat)
  standard.errors <- as.data.frame(matrix(0, ncol = n.spp, nrow = nrow(pred.dat)))
  names(standard.errors) <- names(ydat)

  for (i in 1:n.spp) {

    print(names(ydat)[i], quote = FALSE)
    model.glm <- glm(ydat[, i] ~ ., data = old.bf.data, weights = site.weights,
      family = family, maxit = 100)
    temp <- predict.glm(model.glm,new.bf.data,type="response",se.fit=TRUE)
    prediction[,i] <- temp[[1]]
    standard.errors[,i] <- temp[[2]]

    }

  return(list("prediction"=prediction,"ses"=standard.errors))
}

"mars.new.dataframe" <-
function (input.data)
{
#
# j leathwick, j elith - August 2006
#
# version 3.1 - developed in R 2.3.1 using mda 0.3-1
#
# takes an input data frame and checks for factor variables
# converting these to dummy variables, one each for each factor level
# returning it for use with mars.glm so that factor vars can be included
# in a mars analysis
#

  if (!is.data.frame(input.data)) {
    print("input data must be a dataframe..",quote = FALSE)
    return()
  }

  n <- 1
  for (i in 1:ncol(input.data)) {  #first transfer the vector variables
    if (is.vector(input.data[,i])) {
      if (n == 1) {
        output.data <- as.data.frame(input.data[,i])
        names.list <- names(input.data)[i]
        var.type <- "vector"
        factor.level <- "na"
      }
      else {
        output.data[,n] <- input.data[,i]
        names.list <- c(names.list,names(input.data)[i])
        var.type <- c(var.type,"vector")
        factor.level <- c(factor.level,"na")
      }
      names(output.data)[n] <- names(input.data)[i]
      n <- n + 1
    }
  }

  for (i in 1:ncol(input.data)) {  # and then the factor variables
    if (is.factor(input.data[,i])) {
      temp.table <- summary(input.data[,i])
      for (j in 1:length(temp.table)) {
        names.list <- c(names.list,names(input.data)[i])
        var.type <- c(var.type,"factor")
        factor.level <- c(factor.level,names(temp.table)[j])
        output.data[,n] <- ifelse(input.data[,i] == names(temp.table)[j],1,0)
        names(output.data)[n] <- paste(names(input.data)[i],".",names(temp.table)[j],sep="")
        n <- n + 1
      }
    }
  }

  lineage <- data.frame(names(output.data),names.list,var.type,factor.level)
  for (i in 1:4) lineage[,i] <- as.character(lineage[,i])
  names(lineage) <- c("full.name","base.name","type","level")

  return(list(dataframe = output.data, lineage = lineage))
}





new.tifs=NULL
# Interpret command line argurments #
# Make Function Call #
Args <- commandArgs(trailingOnly=FALSE)

    for (i in 1:length(Args)){
     if(Args[i]=="-f") ScriptPath<-Args[i+1]
     }

    for (arg in Args) {
    	argSplit <- strsplit(arg, "=")
    	argSplit[[1]][1]
    	argSplit[[1]][2]
    	if(argSplit[[1]][1]=="ws") ws <- argSplit[[1]][2]
    	if(argSplit[[1]][1]=="new.tifs") new.tifs <- argSplit[[1]][2]
    	if(argSplit[[1]][1]=="o") out.dir <- argSplit[[1]][2]
    }

PredictModel(workspace=ws,new.tifs=new.tifs,out.dir=out.dir)


