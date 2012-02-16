# A set of R functions for automated model fitting of random forest models to presence/absence data #
#
# Modified 12-2-09 to:  remove categorical covariates from consideration if they only contain one level
#                       ID factor variables based on "categorical" prefix and look for tifs in subdir
#                       Give progress reports
#                       write large output tif files in blocks to alleviate memory issues
#                       various bug fixes
#
# Adapted from existing pluggable BRT and GLM modules in April 2009 by Alan Swanson


# Libraries required to run this program #
#   PresenceAbsence - for ROC plots
#   XML - for XML i/o
#   rgdal - for geotiff i/o
#   RandomForest - duh
#   sp - used by rdgal library

options(error=NULL)

fit.rf.fct <- function(ma.name,tif.dir=NULL,output.dir=NULL,response.col="^response.binary",make.p.tif=T,make.binary.tif=T,
      debug.mode=F,responseCurveForm="pdf",xtest=NULL,ytest=NULL,n.trees=1000,mtry=NULL, samp.replace=FALSE, sampsize=NULL,nodesize=NULL,maxnodes=NULL,importance=FALSE,
      localImp=FALSE,nPerm=1,proximity=NULL,oob.prox=proximity,norm.votes=TRUE,do.trace=FALSE,keep.forest=NULL,keep.inbag=FALSE, make.r.curves=T,
      seed=NULL,script.name="rf.r",opt.methods=2,save.model=TRUE,UnitTest=FALSE,MESS=FALSE){
    # This function fits a boosted regression tree model to presence-absence data.
    # written by Alan Swanson, Jan-March 2009
    # uses code modified from that published in Elith et al 2008
    # # Maintained and edited by Marian Talbert September 2010-
    # Arguements.
    # ma.name: is the name of a .csv file with a model array.  full path must be included unless it is in the current
    #  R working directory #
    # tif.dir: is the directory containing geotiffs for each covariate.  only required if geotiffs output of the 
    #   response surface is requested #    # cov.list.name: is the name of a text file with the names of covariates to be included in models (one per line).
    # output.dir: is the directory that output files will be stored in.  if not given, files will go to the current working directory. 
    # response.col: column number of the model array containing a binary 0/1 response.  all other columns will be considered explanatory variables.
    # make.p.tif: T if a geotiff of the response surface is desired.
    # make.binary.tif: T if a geotiff of the response surface is desired.
    # simp.method: model simplification method.  valid methods include: "cross-validation", "rel-inf", and "none".  "cross-validation" uses the
    #   methods of Elith et al, 2008 for removing covariates that don't contribute to the model.  "rel-inf" simply removes covariates that contribute 
    #  less than 1%.  cross-validation is very slow - it can add up to 10min to a run. 
    # debug.mode: if T, output is directed to the console during the run.  also, a pdf is generated which contains response curve plots and perspective plots
    #    showing the effects of interactions deemed important.  if F, output is diverted to a text file and the console is kept clear 
    #    except for final output of an xml file.  in either case, a set of standard output files are created in the output directory.
    # tc:  tree-complexity for brt fits.  if specified, this sets the tree-complexity of the final model fit.  A lower tree-complexity will be used for
    #    model selection steps.  if not set, this will be estimated loosely following the guidelines given by Elith et al, 2008.
    # 

    # Value:
    # returns nothing but generates a number of output files in the directory
    # "output.dir" named above.  These output files consist of:
    #
    # brt_output.txt:  a text file with fairly detailed results of the final model.
    # brt_output.xml:  an xml-formatted text file with results from the final model.
    # brt_response_curves.xml:  an xml-formatted text file with response curves for
    #   each covariate in the final model.
    # brt_prob_map.tif:  a geotiff of the response surface
    # brt_bin_map.tif:  a geotiff of the binary response surface.  threhold is based on the roc curve at the point where sensitivity=specificity.
    # brt_log.txt:   a file containing text output diverted from the console when debug.mode=F
    # brt_auc_plot.jpg:  a jpg file of a ROC plot.
    # brt_response_curves.pdf:  an pdf file with response curves for
    #   each covariate in the final model and perspective plots showing the effect of interactions deemed significant.
    #   only produced when debug.mode=T
    #  seed=NULL                                 # sets a seed for the algorithm, any inegeger is acceptable
    #  opt.methods=2                             # sets the method used for threshold optimization used in the
    #                                            # the evaluation statistics module
    #  save.model=FALSE                          # whether the model will be used to later produce tifs
    #
    # when debug.mode is true, these filenames will include a number in them so that they will not overwrite preexisting files. eg brt_1_output.txt.
    #
    times <- as.data.frame(matrix(NA,nrow=8,ncol=1,dimnames=list(c("start","read data","model tuning","model fit",
            "model summary","response curves","tif output","done"),c("time"))))
    times[1,1] <- unclass(Sys.time())
    t0 <- unclass(Sys.time())
    #simp.method <- match.arg(simp.method)
    out <- list(
      input=list(ma.name=ma.name,
                 tif.dir=tif.dir,
                 output.dir=output.dir,
                 response.col=response.col,
                 save.model=save.model,
                 xtest=xtest,
                 ytest=ytest,
                 n.trees=n.trees,
                 mtry=mtry,
                 samp.replace=samp.replace,
                 sampsize=sampsize,
                 nodesize=nodesize,
                 maxnodes=maxnodes,
                 importance=importance,
                 localImp=localImp,
                 nPerm=nPerm,
                 proximity=proximity,
                 oob.prox=oob.prox,
                 norm.votes=norm.votes,
                 do.trace=do.trace,
                 keep.forest=keep.forest,
                 keep.inbag=keep.inbag,
                 make.p.tif=make.p.tif,
                 make.binary.tif=make.binary.tif,
                 model.type="random forest regression tree",
                 model.source.file=script.name,
                 model.fitting.subset=c(n.pres=50,n.abs=50),#subset used for response curves
                 run.time=paste(c(format(Sys.time(),"%Y-%m-%d"),format(Sys.time(),"%H:%M:%S")),collapse="T"),
                 sig.test="mean decrease in accuracy",
                 MESS=MESS),
      dat = list(missing.libs=NULL,
                 output.dir=list(dname=NULL,exist=F,readable=F,writable=F),
                 tif.dir=list(dname=NULL,exist=F,readable=F,writable=F),
                 tif.ind=NULL,
                 tif.names=NULL,
                 bname=NULL,
                 bad.factor.covs=NULL, # factorchange
                 ma=list( status=c(exists=F,readable=F),
                          dims=c(NA,NA),
                          n.pres=c(all=NA,complete=NA,subset=NA),
                          n.abs=c(all=NA,complete=NA,subset=NA),
                          ratio=NA,
                          resp.name=NULL,
                          factor.levels=NULL,
                          used.covs=NULL,
                          ma=NULL,
                          ma.subset=NULL,
                          train.xy=NULL,
                          test.xy=NULL,
                          site.weights=NULL),
                 ma.test=NULL),
      mods=list(parms=list(n.trees=n.trees,mtry=NULL),
                full.mod=NULL,
                simp.mod=NULL,
                final.mod=NULL,
                r.curves=NULL,
                tif.output=list(prob=NULL,bin=NULL),
                auc.output=NULL,
                interactions=NULL,
                summary=NULL),
      time=list(strt=unclass(Sys.time()),end=NULL),
      error.mssg=list(NULL),
      ec=0
      )

   if(!is.null(seed)) set.seed(seed)
    #if(simplify.brt==T) out$input$simp.method<-"cross-validation" else out$input$simp.method<-">1% rel. influence"
    # load libaries #
    out <- check.libs(list("randomForest","PresenceAbsence","rgdal","XML","sp","raster","tcltk2","foreign","ade4"),out)
    
    # exit program now if there are missing libraries #
    if(!is.null(out$error.mssg[[1]])){
          cat(saveXML(rf.to.xml(out),indent=T),'\n')
          return()
          }
                
    # check output dir #
    out$dat$output.dir <- check.dir(output.dir)    
    if(out$dat$output.dir$writable==F) {out$ec<-out$ec+1
              out$error.mssg[[out$ec]] <- paste("ERROR: output directory",output.dir,"is not writable")
              out$dat$output.dir$dname <- getwd()
              
            }
    
    # generate a filename for output #
    if(debug.mode==T){
            outfile <- paste(bname<-paste(out$dat$output.dir$dname,"/rf_",n<-1,sep=""),"_output.txt",sep="")
            while(file.access(outfile)==0) outfile<-paste(bname<-paste(out$dat$output.dir$dname,"/rf_",n<-n+1,sep=""),"_output.txt",sep="")
            capture.output(cat("temp"),file=outfile) # reserve the new basename #
    } else bname <- paste(out$dat$output.dir$dname,"/rf",sep="")
    out$dat$bname <- bname    
    
    # sink console output to log file #
    if(!debug.mode) {sink(logname <- paste(bname,"_log.txt",sep=""));on.exit(sink)} else logname<-NULL
    #options(warn=1)
    
    # check tif dir #
        # check tif dir #
    if(!is.null(tif.dir)){
      out$dat$tif.dir <- check.dir(tif.dir)
      if(out$dat$tif.dir$readable==F & (out$input$make.binary.tif | out$input$make.p.tif)) {
                out$ec<-out$ec+1
                out$error.mssg[[out$ec]] <- paste("ERROR: tif directory",tif.dir,"is not readable")
                if(!debug.mode) {sink();on.exit();unlink(paste(bname,"_log.txt",sep=""))}
              cat(saveXML(brt.to.xml(out),indent=T),'\n')
              return()
              }
            }

    
    # find .tif files in tif dir #
    if(out$dat$tif.dir$readable)  out$dat$tif.names <- list.files(out$dat$tif.dir$dname,pattern=".tif",recursive=T)
    
    # check for model array #
    out$input$ma.name <- check.dir(out$input$ma.name)$dname
    if(UnitTest!=FALSE) options(warn=2)
    out <- read.ma(out)
    if(UnitTest==1) return(out)
    # exit program now if there are errors in the input data #
    if(!is.null(out$error.mssg[[1]])){
          if(!debug.mode) {sink();on.exit();unlink(paste(bname,"_log.txt",sep=""))}
          cat(saveXML(rf.to.xml(out),indent=T),'\n')
          return()
          }
    t1 <- unclass(Sys.time()) 
    cat("\ndone processing data, t=",round(t1-t0,1),"sec\n")  
    cat("\nbegin processing of model array:",out$input$ma.name,"\n")
    cat("\nfile basename set to:",out$dat$bname,"\n")
    if(debug.mode) flush.console()
    
    if(!debug.mode) {sink();cat("Progress:20%\n");flush.console();sink(logname,append=T)} else {cat("\n");cat("20%\n")}  ### print time
    
    ##############################################################################################################
    #  Begin model fitting #
    ##############################################################################################################


    # tune the mtry parameter - this controls the number of covariates randomly subset for each split #
    cat("\ntuning mtry parameter\n")

  x=out$dat$ma$ma[,-1]
  y=factor(out$dat$ma$ma[,1])
      if(is.null(mtry)){
     mtry <- try(tuneRF(x=out$dat$ma$ma[,-1],y=factor(out$dat$ma$ma[,1]),mtryStart=3,importance=TRUE,ntreeTry=100,
        replace=FALSE, doBest=F, plot=F),silent=T)
          mtry <- try(mtry[mtry[,2]==min(mtry[,2]),1][1])
          t2 <- unclass(Sys.time())
          if(!debug.mode) {sink();cat("Progress:30%\n");flush.console();sink(logname,append=T)} else {cat("\n");cat("30%\n")}
    
          cat("\ndone tuning random forest parameters, t=",round(t2-t1,1),"sec\n")
        }
    
    cat("\nnow fitting full random forest model using mtry=",mtry,"\n")  
    if(debug.mode) flush.console() 

     rf.full <- randomForest(x=out$dat$ma$ma[,-1],y=factor(out$dat$ma$ma[,1]),xtest=xtest,ytest=ytest,importance=TRUE, ntree=n.trees,
        mtry=mtry,replace=samp.replace,sampsize=ifelse(is.null(sampsize),(ifelse(samp.replace,nrow(x),ceiling(.632*nrow(x)))),sampsize),
        nodesize=ifelse(is.null(nodesize),(if (!is.null(y) && !is.factor(y)) 5 else 1),nodesize),maxnodes=maxnodes,
        localImp=localImp, nPerm=nPerm, keep.forest=ifelse(is.null(keep.forest),!is.null(y) && is.null(xtest),keep.forest),
        corr.bias=corr.bias, keep.inbag=keep.inbag)

              out$mods$parms$mtry<-mtry
              out$mods$final.mod <- rf.full

    t3 <- unclass(Sys.time())
    if(!debug.mode) {sink();cat("Progress:40%\n");flush.console();sink(logname,append=T)} else {cat("\n");cat("40%\n")}  ### print time
    
    cat("\nfinished fitting full model, t=",round(t2-t1,1),"sec\nnow computing output stats...\n")
    if(debug.mode) flush.console()
        
    ##############################################################################################################
    #  Begin model output #
    ##############################################################################################################
           
    # ROC plot #

      model.summary <- try(importance(out$mods$final.mod),silent=T)
    if(class(model.summary)=="try-error"){
        if(!debug.mode) {sink();on.exit();unlink(paste(bname,"_log.txt",sep=""))}
        out$ec<-out$ec+1
        out$error.mssg[[out$ec]] <- paste("ERROR: can't generate summary of final model:",model.summary)
        cat(saveXML(rf.to.xml(out),indent=T),'\n')
        return()
    } else {
        model.summary<-model.summary[order(model.summary[,3],decreasing=T),]
        out$mods$summary <- model.summary
        }
        
   txt0 <- paste("Random Forest Modeling Results\n",out$input$run.time,"\n\n",
          "Data:\n\t",ma.name,
          "\n\tn(pres)=",out$dat$ma$n.pres[2],
          "\n\tn(abs)=",out$dat$ma$n.abs[2],
          "\n\tn covariates considered=",length(out$dat$ma$used.covs),
        "\n\n","Settings:",
        "\n\tn covariates considered at each split =",out$mods$parms$mtry,
        "\n\tn trees=",out$mods$parms$n.tree,
        "\n\ttotal time for model fitting=",round((unclass(Sys.time())-t0)/60,2),"min\n",sep="")
    txt1 <- "\nRelative performance of predictors in final model:\n\n"
    txt2 <- "\nDefault summary of random forest fit:\n"
    capture.output(cat(txt0),cat(txt1),print(round(model.summary,4)),cat(txt2),print(out$mods$final.mod),file=paste(bname,"_output.txt",sep=""))
    cat(txt0);cat(txt1);print(round(model.summary,4));cat(txt2);print(out$mods$final.mod);cat("\n\n")
    if(!is.null(out$dat$bad.factor.cols)){
        capture.output(cat("\nWarning: the following categorical response variables were removed from consideration\n",
            "because they had only one level:",paste(out$dat$bad.factor.cols,collapse=","),"\n"),
            file=paste(bname,"_output.txt",sep=""),append=T)
        cat("\nWarning: the following categorical response variables were removed from consideration\n",
            "because they had only one level:",paste(out$dat$bad.factor.cols,collapse=","),"\n\n")
        }
        
    auc.output <- make.auc.plot.jpg(out$dat$ma$ma,pred=tweak.p(as.vector(predict(out$mods$final.mod,type="prob")[,2])),
            plotname=paste(bname,"_auc_plot.jpg",sep=""),modelname="RF",opt.methods=opt.methods,weight=rep(1,times=dim(out$dat$ma$ma)[1]),out=out)
   
    if(class(auc.output)=="try-error"){
          out$ec<-out$ec+1
          out$error.mssg[[out$ec]] <- paste("Error making ROC plot:",auc.output)
    } else { out$mods$auc.output<-auc.output}
        

    #assign("out",out,envir=.GlobalEnv)   
    
    # Text summary #

      
    if(!debug.mode) {sink();cat("Progress:70%\n");flush.console();sink(logname,append=T)} else {cat("\n");cat("60%\n")}  ### print time
    
    if(debug.mode) flush.console()

    # Response curves #
    t4 <- unclass(Sys.time())
    if(make.r.curves){

            r.curves <- list(names=row.names(out$mods$summary),preds=list(),resp=list())
            inc <- 10/length(r.curves$names)
            assign("r.curves",r.curves,envir=.GlobalEnv)   

        if(is.null(responseCurveForm)){
          responseCurveForm<-0}

    if(debug.mode | responseCurveForm=="pdf"){
                nvar <- nrow(out$mods$summary)
                pcol <- min(ceiling(sqrt(nvar)),4)
                prow <- min(ceiling(nvar/pcol),3)
                pdf(paste(bname,"_response_curves.pdf",sep=""),width=11,height=8.5,onefile=T)
                par(oma=c(2,2,4,2),mfrow=c(prow,pcol))
                }
            for(i in 1:length(r.curves$names)){
                    assign("i",i,envir=.GlobalEnv)

                            x<-try(partialPlot(out$mods$final.mod,out$dat$ma$ma.subset,r.curves$names[i],n.pt=50,plot=T,main="",
                                    xlab=r.curves$names[i]))
                    if(class(x)=="try-error"){
                        if(!debug.mode) {sink();on.exit();unlink(paste(bname,"_log.txt",sep=""))} else graphics.off()
                        out$ec<-out$ec+1
                        out$error.mssg[[out$ec]] <- paste("ERROR: can't generate response curves:",x)
                        cat(saveXML(rf.to.xml(out),indent=T),'\n')
                        return()
                    } else {
                        r.curves$preds[[i]] <- x$x
                        r.curves$resp[[i]] <- x$y
                        }
                     if(!debug.mode) {sink();cat(paste("Progress:",round(70+i*inc,1),"%\n",sep=""));flush.console();sink(logname,append=T)} else {cat("\n");cat(paste(round(70+i*inc,1),"%\n",sep=""))}  ### print time
                    }
            if(debug.mode) graphics.off()
            out$mods$r.curves <- r.curves
        }
       
    t5 <- unclass(Sys.time())
    #if(!debug.mode) {sink();cat("80%\n");flush.console();sink(logname,append=T)} else {cat("\n");cat("80%\n")}  ### print time
    cat("\nfinished with response curves, t=",round(t5-t4,2),"sec\n")
    if(debug.mode) flush.console()
    
    # Make .tif of predictions #
    out$mods$final.mod$contributions$var<-as.character(row.names(out$mods$summary))
    
    assign("out",out,envir=.GlobalEnv)
     save.image(paste(output.dir,"modelWorkspace",sep="\\"))
    if(out$input$make.p.tif==T | out$input$make.binary.tif==T){
        cat("\nproducing prediction maps...","\n","\n");flush.console()
        mssg <- try(proc.tiff(model=out$mods$final.mod,vnames=as.character(row.names(out$mods$summary)),
            tif.dir=out$dat$tif.dir$dname,filenames=out$dat$tif.ind,pred.fct=rf.predict,factor.levels=out$dat$ma$factor.levels,make.binary.tif=make.binary.tif,
            thresh=out$mods$auc.output$thresh,make.p.tif=make.p.tif,outfile.p=paste(out$dat$bname,"_prob_map.tif",sep=""),
            outfile.bin=paste(out$dat$bname,"_bin_map.tif",sep=""),tsize=50.0,NAval=-3000,fnames=out$dat$tif.names,logname=logname,out=out),silent=T)     #"brt.prob.map.tif"

        if(class(mssg)=="try-error" | mssg!=0){
          if(!debug.mode) {sink();on.exit();unlink(paste(bname,"_log.txt",sep=""))}
          out$ec<-out$ec+1
          out$error.mssg[[out$ec]] <- paste("Error producing prediction maps:",mssg)
          cat(saveXML(rf.to.xml(out),indent=T),'\n')
          return()
        }  else {
            if(make.p.tif) out$mods$tif.output$prob <- paste(out$dat$bname,"_prob_map.tif",sep="")
            if(make.binary.tif) out$mods$tif.output$bin <- paste(out$dat$bname,"_bin_map.tif",sep="")
            t5 <- unclass(Sys.time())
            cat("\nfinished with prediction maps, t=",round(t5-t4,2),"sec\n");flush.console()
          }
        }
    if(!debug.mode) {sink();cat("Progress:90%\n");flush.console();sink(logname,append=T)} else {cat("\n");cat("90%\n")}  ### print time

  # Evaluation Statistics on Test Data#

    if(!is.null(out$dat$ma$ma.test)) Eval.Stat<-EvaluationStats(out,thresh=auc.output$thresh,train=out$dat$ma$ma,
        train.pred=tweak.p(as.vector(predict(out$mods$final.mod,type="prob")[,2])),opt.methods)

    

    
    # Write summaries to xml #
    assign("out",out,envir=.GlobalEnv)
    doc <- rf.to.xml(out)
    
    cat(paste("\ntotal time=",round((unclass(Sys.time())-t0)/60,2),"min\n\n\n",sep=""))
    if(!debug.mode) {
        sink();on.exit();unlink(paste(bname,"_log.txt",sep=""))
        cat("Progress:100%\n");flush.console()
        cat(saveXML(doc,indent=T),'\n')
        }
    capture.output(cat(saveXML(doc,indent=T)),file=paste(out$dat$bname,"_output.xml",sep=""))
    assign("fit",out$mods$final.mod,envir=.GlobalEnv)
    invisible(out)
}

rf.predict <- function(model,x) {
    # retrieve key items from the global environment #
    # make predictions from complete data only #
    y <- rep(NA,nrow(x))
    y[complete.cases(x)] <- as.vector(predict(model,newdata=x[complete.cases(x),],type="prob")[,2])
    
    # make predictions from full data #
    
    # encode missing values as -1.
    y[is.na(y)]<- NaN
    
    # return predictions.
    return(y)
    }

logit <- function(x) 1/(1+exp(-x))

file_path_as_absolute <- function (x){
    if (!file.exists(epath <- path.expand(x))) 
        stop(gettextf("file '%s' does not exist", x), domain = NA)
    cwd <- getwd()
    on.exit(setwd(cwd))
    if (file_test("-d", epath)) {
        setwd(epath)
        getwd()
    }
    else {
        setwd(dirname(epath))
        file.path(getwd(), basename(epath))
    }
}
#file_path_as_absolute(".")

rf.to.xml <- function(out){
    require(XML)
    schema.http="http://www.w3.org/2001/XMLSchema-instance"
    schema.fname="file:/Users/isfs2/Desktop/Source/2008-04-09/src/gov/nasa/gsfc/quickmap/ModelBuilder/modelRun_output_v2.xsd"
    xml.out <- newXMLDoc()
    mr <- newXMLNode("modelRunOutput",doc=xml.out,namespaceDefinitions=c(xsi=schema.http,noNamespaceSchemaLocation=schema.fname))#,parent=xml.out
    sm <- newXMLNode("singleModel",parent=mr)
    bg <- newXMLNode("background",parent=sm)
        newXMLNode("mdsName",out$input$ma.name,parent=bg)
        newXMLNode("runDate",out$input$run.time,parent=bg)
        lc <- newXMLNode("layersConsidered",parent=bg)#, parent = xml.out)
        kids <- lapply(paste(out$dat$tif.dir$dname,"/",out$dat$tif.names,sep=""),function(x) newXMLNode("layer", x))
        addChildren(lc, kids)
    mo <- newXMLNode("modelOutput",parent=sm)
        newXMLNode("modelType",out$input$model.type,parent=mo)
        newXMLNode("modelSourceFile",out$input$model.source.file,parent=mo)
        newXMLNode("devianceExplained",out$mods$auc.output$pct_dev_exp,parent=mo,attrs=list(type="percentage"))
        newXMLNode("nativeOutput",paste(out$dat$bname,"_output.txt",sep=""),parent=mo)
        newXMLNode("binaryOutputFile",out$mods$tif.output[[2]],parent=mo)
        newXMLNode("probOutputFile",out$mods$tif.output[[1]],parent=mo)
        newXMLNode("auc",out$mods$auc.output$auc,parent=mo)
        newXMLNode("rocGraphic",out$mods$auc.output$plotname,parent=mo)
        newXMLNode("rocThresh",out$mods$auc.output$thresh,parent=mo)
        newXMLNode("modelDeviance",out$mods$auc.output$dev_fit,parent=mo)
        newXMLNode("nullDeviance",out$mods$auc.output$null_dev,parent=mo)
        if(is.null(out$mods$r.curves)) rc.name <- NULL else rc.name <- paste(out$dat$bname,"_response_curves.xml",sep="")
        newXMLNode("responsePlotsFile",rc.name,parent=mo)
        newXMLNode("significanceDescription",out$input$sig.test,parent=mo)
        mfp <- newXMLNode("modelFitParmas",parent=mo)
            newXMLNode("nTrees",out$mods$parms$n.tree,parent=mfp)
            newXMLNode("mTry",out$mods$parms$mtry,parent=mfp)
        
        sv <- newXMLNode("significantVariables",parent=mo)
        if(!is.null(out$mods$summary)) {
            t.table <- data.frame(significanceMeasurement=out$mods$summary[,3],row.names=row.names(out$mods$summary))
            for(i in 1:nrow(t.table)){
                x <- newXMLNode("sigVar",parent=sv)
                newXMLNode(name="name", row.names(t.table)[i],parent=x)
                kids <- lapply(1:ncol(t.table),function(j) newXMLNode(name=names(t.table)[j], t.table[i,j]))
                addChildren(x, kids)
                }
            }
    if(!is.null(out$mods$r.curves)){
        r.curves <-  out$mods$r.curves
        rc.out <- newXMLDoc()
        root <- newXMLNode("responseCurves",doc=rc.out,namespaceDefinitions=c(xsi=schema.http,noNamespaceSchemaLocation=schema.fname))
        for(i in 1:length(r.curves$names)){
            vartype <- ifelse(class(r.curves$preds[[i]])=="character","factor","continuous")
            x <- newXMLNode("responseCurve",attrs=list(covariate=r.curves$names[i],type=vartype),parent=root)
            kids <- lapply(1:length(r.curves$preds[[i]]),function(j){
                newXMLNode(name="responsePt",parent=x,.children=list(
                    newXMLNode(name="explanatory",r.curves$preds[[i]][j]),
                    newXMLNode(name="response",r.curves$resp[[i]][j])))})
            addChildren(x, kids)
            }
        saveXML(rc.out,rc.name,indent=T)
        } 
    if(!is.null(out$error.mssg[[1]])) {
        kids <- lapply(out$error.mssg,function(j) newXMLNode(name="error",j))
        addChildren(mo,kids)
        }
    return(xml.out)
    }


get.cov.names <- function(model){
    return(attr(terms(formula(model)),"term.labels"))
    }

check.dir <- function(dname){
    if(is.null(dname)) dname <- getwd()
    dname <- gsub("[\\]","/",dname)
    end.char <- substr(dname,nchar(dname),nchar(dname))
    if(end.char == "/") dname <- substr(dname,1,nchar(dname)-1)
    exist <- suppressWarnings(as.numeric(file.access(dname,mode=0))==0) # -1 if bad, 0 if ok #
    if(exist) dname <- file_path_as_absolute(dname)
    readable <- suppressWarnings(as.numeric(file.access(dname,mode=4))==0) # -1 if bad, 0 if ok #
    writable <- suppressWarnings(as.numeric(file.access(dname,mode=2))==0) # -1 if bad, 0 if ok #
    return(list(dname=dname,exist=exist,readable=readable,writable=writable))
    }


get.image.info <- function(image.names){
    # this function creates a data.frame with summary image info for a set of images #
    require(rgdal)
    n.images <- length(image.names)

    full.names <- image.names
    out <- data.frame(image=full.names,available=rep(F,n.images),size=rep(NA,n.images),
        type=factor(rep("unk",n.images),levels=c("asc","envi","tif","unk")))
    out$type[grep(".tif",image.names)]<-"tif"
    out$type[grep(".asc",image.names)]<-"asc"
    for(i in 1:n.images){
        if(out$type[i]=="tif"){
            x <-try(GDAL.open(full.names[1],read.only=T),silent=T)
            suppressMessages(try(GDAL.close(x),silent=T))
            if(class(x)!="try-error") out$available[i]<-T
            x<-try(file.info(full.names[i]))
        } else {
            x<-try(file.info(full.names[i]))
            if(!is.na(x$size)) out$available[i]<-T
        }
        if(out$available[i]==T){
            out$size[i]<-x$size
            if(out$type[i]=="unk"){
                # if extension not known, look for envi .hdr file in same directory #
                if(file.access(paste(file_path_sans_ext(full.names[i]),".hdr",sep=""))==0) 
                    out$type[i]<-"envi"
                }
        }
    }
    return(out)
}

tweak.p <- function(p){
	p[p==1]<-max(p[p<1])
	p[p==0]<-min(p[p>0])
	return(p)
	}


#

 # Interpret command line argurments #
# Make Function Call #
#Set defaults for optional commands
make.p.tif=T
make.binary.tif=T
responseCurveForm="pdf"
xtest=NULL
ytest=NULL
n.trees=1000
mtry=NULL
samp.replace=FALSE
sampsize=NULL
nodesize=NULL
maxnodes=NULL
importance=FALSE
localImp=FALSE
nPerm=1
proximity=NULL
oob.prox=proximity
norm.votes=TRUE
do.trace=FALSE
keep.forest=NULL
keep.inbag=FALSE
make.r.curves=T
seed=NULL
opt.methods=2
save.model=TRUE
seed=NULL
MESS=FALSE

Args <- commandArgs(trailingOnly=FALSE)

    for (i in 1:length(Args)){
     if(Args[i]=="-f") ScriptPath<-Args[i+1]
     }

    for (arg in Args) {
    	argSplit <- strsplit(arg, "=")
    	argSplit[[1]][1]
    	argSplit[[1]][2]
    	if(argSplit[[1]][1]=="c") csv <- argSplit[[1]][2]
    	if(argSplit[[1]][1]=="o") output <- argSplit[[1]][2]
    	if(argSplit[[1]][1]=="rc") responseCol <- argSplit[[1]][2]
    	if(argSplit[[1]][1]=="mpt") make.p.tif <- argSplit[[1]][2]
 			if(argSplit[[1]][1]=="mbt")  make.binary.tif <- argSplit[[1]][2]
      if(argSplit[[1]][1]=="xtst")  xtest <- argSplit[[1]][2]
 			if(argSplit[[1]][1]=="ytst")  ytest <- argSplit[[1]][2]
 			if(argSplit[[1]][1]=="ntree")  n.trees <- argSplit[[1]][2]
      if(argSplit[[1]][1]=="mtry")  mtry <- argSplit[[1]][2]
 			if(argSplit[[1]][1]=="sampR")  samp.replace <- argSplit[[1]][2]
 			if(argSplit[[1]][1]=="sampS")  sampsize <- argSplit[[1]][2]
 			if(argSplit[[1]][1]=="nodeS")  nodesize <- argSplit[[1]][2]
 			if(argSplit[[1]][1]=="maxN")  maxnodes <- argSplit[[1]][2]
 			if(argSplit[[1]][1]=="impt")  importance <- argSplit[[1]][2]
 			if(argSplit[[1]][1]=="locImp")  localImp <- argSplit[[1]][2]
 		  if(argSplit[[1]][1]=="nPerm")  nPerm <- argSplit[[1]][2]
 		  if(argSplit[[1]][1]=="prox")  proximity <- argSplit[[1]][2]
 			if(argSplit[[1]][1]=="oopp")  oop.prox <- argSplit[[1]][2]
 			if(argSplit[[1]][1]=="NVot")  norm.votes <- argSplit[[1]][2]
 			if(argSplit[[1]][1]=="Trce")  do.trace <- argSplit[[1]][2]
 			if(argSplit[[1]][1]=="kf")  keep.forest <- argSplit[[1]][2]
 			if(argSplit[[1]][1]=="Kbag")  keep.inbag <- argSplit[[1]][2]
 		  if(argSplit[[1]][1]=="curves")  make.r.curves <- argSplit[[1]][2]
 		  if(argSplit[[1]][1]=="om")  opt.methods <- argSplit[[1]][2]
      if(argSplit[[1]][1]=="savm")  save.model <- argSplit[[1]][2]
      if(argSplit[[1]][1]=="mes")  MESS <- argSplit[[1]][2]
 		  
    }
	print(csv)
	print(output)
	print(responseCol)
	
make.p.tif<-as.logical(make.p.tif)
make.binary.tif<-as.logical(make.binary.tif)
samp.replace<-as.logical(samp.replace)
importance<-as.logical(importance)
localImp<-as.logical(localImp)
norm.votes<-as.logical(norm.votes)
do.trace<-as.logical(do.trace)
keep.inbag<-as.logical(keep.inbag)
make.r.curves<-as.logical(make.r.curves)
save.model<-make.p.tif | make.binary.tif
n.trees<-as.numeric(n.trees)
opt.methods<-as.numeric(opt.methods)
ScriptPath<-dirname(ScriptPath)
MESS<-as.logical(MESS)

source(paste(ScriptPath,"LoadRequiredCode.r",sep="\\"))

fit.rf.fct(ma.name=csv,tif.dir=NULL,output.dir=output,response.col=responseCol,make.p.tif=make.p.tif,make.binary.tif=make.binary.tif,
      debug.mode=F,responseCurveForm="pdf",xtest=xtest,ytest=ytest,n.trees=n.trees,mtry=mtry,samp.replace=samp.replace, sampsize=sampsize,
      nodesize=nodesize,maxnodes=maxnodes,importance=importance,
      localImp=localImp,nPerm=nPerm,proximity=proximity,oob.prox=oob.prox,norm.votes=norm.votes,do.trace=do.trace,keep.forest=keep.forest,
      keep.inbag=keep.inbag,make.r.curves=make.r.curves,
      seed=seed,script.name="rf.r",opt.methods=opt.methods,save.model=save.model,MESS=MESS)

 