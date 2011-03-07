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

Debug=F    # set to F for command line pluggability
if(Debug==T){
     output.dir <- "F:/code for Jeff and Roger/jeffs paper/filtered_rs/"  # a set of ouput files will be created in this directory.
    ma.dir <- "F:/code for Jeff and Roger/jeffs paper/filtered_rs/train/"
    test.dir <- "F:/code for Jeff and Roger/jeffs paper/filtered_rs/test/"
    ma.names <- paste(ma.dir,sort(list.files(path=ma.dir)),sep="")
    test.names <- paste(test.dir,sort(list.files(path=test.dir)),sep="")
    
    tif.dir <- "F:/yerc/RRSC/YELL/" # directory containing geotiff files
     test.name <- NULL  # if this is supplied, it will be read for use as test data. 
    
    #setwd('F:/code for Jeff and Roger/jeffs paper/data')
    library(tools)
    debug.mode=T  # if true, prints output and status updates to the console. Otherwise all of this goes to a log file and only the XML output is printed to console.
    batch.mode=F
     output.dir <- "c:/temp/"  # a set of ouput files will be created in this directory.
    fnames <- list.files(pattern=".csv")
    ma.names <- fnames[-grep("_test.csv",fnames)]
    test.names <- rep(fnames[grep("_test.csv",fnames)],rep(7,7))
    test.resp.col <- "pres_abs"
    response.col <- "^response.binary"
    tif.dir <- "j:/SAHM/YELL/" # directory containing geotiff files
    ma.name <- "j:/SAHM/07_YELL_Dalmatiantoadflax_train_clean_filt_mod.csv" # model array to use.
    #ma.name <- "GSENM_cheat_pres_abs_2001_factor.mds" # model array to use.
    test.name <- NULL
    debug.mode=F  # if true, prints output and status updates to the console. Otherwise all of this goes to a log file and only the XML output is printed to console.
    batch.mode=F
    make.p.tif=F # make a geotiff of probability surface?
    make.binary.tif=F  # make a binary response surface geotiff?
    output.dir <- "c:/temp"  # a set of ouput files will be created in this directory.
    ma.names <- c("a","b","c")
    test.resp.col <- "pres_abs"
    response.col <- "^response.binary"
    simp.method="BIC"
    library(tools) 
    script.name="glm.r"                        
    out.table <- as.data.frame(matrix(NA,nrow=21,ncol=length(ma.names),dimnames=list(c("ncov.final","nrow_train","ncol_train",
              "dev_exp_train","auc_train","auc.sd_train","thresh_train","pcc_train","sens_train","spec_train","kappa_train",
              "nrow_test","ncol_test","dev_exp_test","auc_test","auc.sd_test","thresh_test","pcc_test","sens_test","spec_test",
              "kappa_test"),file_path_sans_ext(basename(ma.names)))))
    #out.table <- as.data.frame(matrix(NA,nrow=21,ncol=length(ma.names),dimnames=list(c("ncov.final","nrow_train","ncol_train",
#              "dev_exp_train","auc_train","auc.sd_train","thresh_train","pcc_train","sens_train","spec_train","kappa_train",
#              "nrow_test","ncol_test","dev_exp_test","auc_test","auc.sd_test","thresh_test","pcc_test","sens_test","spec_test",
#              "kappa_test"),file_path_sans_ext(basename(ma.names)))))
}
    
# source("F:/code for Jeff and Roger/FIT_RF_pluggable_040609.r")    
    
fit.rf.fct <- function(ma.name,tif.dir=NULL,output.dir=NULL,response.col="^response.binary",test.resp.col="response",make.p.tif=T,make.binary.tif=T,
      debug.mode=F,n.trees=1000,ma.test=NULL,make.r.curves=T,script.name="rf.r"){    
    # This function fits a boosted regression tree model to presence-absence data.
    # written by Alan Swanson, Jan-March 2009
    # uses code modified from that published in Elith et al 2008
    #
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
                 ma.test=ma.test,
                 tif.dir=tif.dir,
                 output.dir=output.dir,
                 response.col=response.col,
                 test.resp.col=test.resp.col,
                 make.p.tif=make.p.tif,
                 make.binary.tif=make.binary.tif,
                 model.type="random forest regression tree",
                 model.source.file=script.name,
                 model.fitting.subset=c(n.pres=50,n.abs=50),#subset used for response curves
                 run.time=paste(c(format(Sys.time(),"%Y-%m-%d"),format(Sys.time(),"%H:%M:%S")),collapse="T"),
                 sig.test="mean decrease in accuracy"),
      dat = list(missing.libs=NULL,
                 output.dir=list(dname=NULL,exist=F,readable=F,writable=F),
                 tif.dir=list(dname=NULL,exist=F,readable=F,writable=F),
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
                          ma.subset=NULL),
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
    
       
    #if(simplify.brt==T) out$input$simp.method<-"cross-validation" else out$input$simp.method<-">1% rel. influence"
    # load libaries #
    out <- check.libs(list("randomForest","PresenceAbsence","rgdal","XML","sp","raster"),out)
    
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
    options(warn=-1)
    
    # check tif dir #
    out$dat$tif.dir <- check.dir(tif.dir) 
    if(out$dat$tif.dir$readable==F & (out$input$make.binary.tif | out$input$make.p.tif)) {
              out$ec<-out$ec+1
              out$error.mssg[[out$ec]] <- paste("ERROR: tif directory",tif.dir,"is not readable")
              if(!debug.mode) {sink();on.exit();unlink(paste(bname,"_log.txt",sep=""))}
            cat(saveXML(mars.to.xml(out),indent=T),'\n')
            return()
            }
    
    # find .tif files in tif dir #
    if(out$dat$tif.dir$readable)  out$dat$tif.names <- list.files(out$dat$tif.dir$dname,pattern=".tif",recursive=T)
    
    # check for model array #
    out$input$ma.name <- check.dir(out$input$ma.name)$dname
    out <- read.ma(out)
        
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
    mtry <- try(tuneRF(x=out$dat$ma$ma[,-1],y=factor(out$dat$ma$ma[,1]),mtryStart=3,importance=TRUE,ntreeTry=100,
        replace=FALSE, doBest=F, plot=F),silent=T)
    if(class(mtry)=="try-error"){
              if(!debug.mode) {sink();on.exit();unlink(paste(bname,"_log.txt",sep=""))}
              out$ec<-out$ec+1
              out$error.mssg[[out$ec]] <- paste("Error tuning mtry parameter:",mtry)
              cat(saveXML(rf.to.xml(out),indent=T),'\n')
              return()
              }
    
    mtry <- try(mtry[mtry[,2]==min(mtry[,2]),1][1])
    t2 <- unclass(Sys.time())
    if(!debug.mode) {sink();cat("Progress:30%\n");flush.console();sink(logname,append=T)} else {cat("\n");cat("30%\n")}
    
    cat("\ndone tuning random forest parameters, t=",round(t2-t1,1),"sec\n")
    cat("\nnow fitting full random forest model using mtry=",mtry,"\n")  
    if(debug.mode) flush.console() 
    
    rf.full <- try(randomForest(x=out$dat$ma$ma[,-1],y=factor(out$dat$ma$ma[,1]),importance=TRUE,
        ntree=out$mods$parms$n.tree, replace=FALSE, mtry=mtry))
    
    if(class(rf.full)=="try-error"){
              if(!debug.mode) {sink();on.exit();unlink(paste(bname,"_log.txt",sep=""))}
              out$ec<-out$ec+1
              out$error.mssg[[out$ec]] <- paste("Error fitting full random forest model:",rf.full)
              cat(saveXML(rf.to.xml(out),indent=T),'\n')
              return()
              } else {
              out$mods$parms$mtry<-mtry
              out$mods$final.mod <- rf.full
              }
    t3 <- unclass(Sys.time())
    if(!debug.mode) {sink();cat("Progress:40%\n");flush.console();sink(logname,append=T)} else {cat("\n");cat("40%\n")}  ### print time
    
    cat("\nfinished fitting full model, t=",round(t2-t1,1),"sec\nnow computing output stats...\n")
    if(debug.mode) flush.console()
        
    ##############################################################################################################
    #  Begin model output #
    ##############################################################################################################
           
    # ROC plot #                            
    auc.output <- try(make.auc.plot.jpg(out$dat$ma$ma,pred=tweak.p(as.vector(predict(out$mods$final.mod,type="prob")[,2])),plotname=paste(bname,"_auc_plot.jpg",sep=""),modelname="RF"),
            silent=T)
   
    if(class(auc.output)=="try-error"){
          out$ec<-out$ec+1
          out$error.mssg[[out$ec]] <- paste("Error making ROC plot:",auc.output)
    } else { out$mods$auc.output<-auc.output}
        
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
    #assign("out",out,envir=.GlobalEnv)   
    
    # Text summary #
    txt0 <- paste("Random Forest Modeling Results\n",out$input$run.time,"\n\n","Data:\n",ma.name,"\n","n(pres)=",
        out$dat$ma$n.pres[2],", n(abs)=",out$dat$ma$n.abs[2],", n covariates considered=",length(out$dat$ma$used.covs),
        "\n\n","Settings:\n","n covariates considered at each split =",out$mods$parms$mtry,", n trees=",out$mods$parms$n.tree,
        "\n\n","Results:\n","AUC=",round(out$mods$auc.output$auc,4),
        ", pct deviance explained=",round(out$mods$auc.output$pct_dev_exp,1),"%\n",
        "total time for model fitting=",round((unclass(Sys.time())-t0)/60,2),"min\n",sep="")
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
      
    if(!debug.mode) {sink();cat("Progress:70%\n");flush.console();sink(logname,append=T)} else {cat("\n");cat("60%\n")}  ### print time
    
    if(debug.mode) flush.console()
    
    # Response curves #
    t4 <- unclass(Sys.time())
    if(make.r.curves){
            r.curves <- list(names=row.names(out$mods$summary),preds=list(),resp=list())
            inc <- 10/length(r.curves$names)
            assign("r.curves",r.curves,envir=.GlobalEnv)   
            if(debug.mode){
                nvar <- nrow(out$mods$summary)
                pcol <- min(ceiling(sqrt(nvar)),4)
                prow <- min(ceiling(nvar/pcol),3)
                pdf(paste(bname,"_response_curves.pdf",sep=""),width=11,height=8.5,onefile=T)
                par(oma=c(2,2,4,2),mfrow=c(prow,pcol))
                }
            for(i in 1:length(r.curves$names)){
                    assign("i",i,envir=.GlobalEnv)
                    if(debug.mode){
                            x<-try(partialPlot(out$mods$final.mod,out$dat$ma$ma.subset,r.curves$names[i],n.pt=50,plot=T,main="",
                                    xlab=r.curves$names[i]))
                            #cat("response curve generated for",r.curves$names[i],"\n");flush.console()
                        } else {
                            x<-try(partialPlot(out$mods$final.mod,out$dat$ma$ma.subset,r.curves$names[i],n.pt=50,plot=F))
                        }
                        
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
    if(out$input$make.p.tif==T | out$input$make.binary.tif==T){
        cat("\nproducing prediction maps...","\n","\n");flush.console()
        mssg <- try(proc.tiff(model=out$mods$final.mod,vnames=as.character(row.names(out$mods$summary)),
            tif.dir=out$dat$tif.dir$dname,pred.fct=rf.predict,factor.levels=out$dat$ma$factor.levels,make.binary.tif=make.binary.tif,
            thresh=out$mods$auc.output$thresh,make.p.tif=make.p.tif,outfile.p=paste(out$dat$bname,"_prob_map.tif",sep=""),
            outfile.bin=paste(out$dat$bname,"_bin_map.tif",sep=""),tsize=50.0,NAval=-3000,fnames=out$dat$tif.names,logname=logname),silent=T)     #"brt.prob.map.tif"

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
    
    
    # read in test data #
    if(!is.null(out$input$ma.test)) out <- read.ma(out,T)
    
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



make.auc.plot.jpg<-function(ma.reduced,pred,plotname,modelname){
    auc.data <- data.frame(ID=1:nrow(ma.reduced),pres_abs=ma.reduced[,1],pred=pred)
    p_bar <- mean(auc.data$pres_abs); n_pres <- sum(auc.data$pres_abs); n_abs <- nrow(auc.data)-n_pres
    null_dev <- -2*(n_pres*log(p_bar)+n_abs*log(1-p_bar))
    dev_fit <- -2*(sum(log(auc.data$pred[auc.data$pres_abs==1]))+sum(log(1-auc.data$pred[auc.data$pres_abs==0])))
    dev_exp <- null_dev - dev_fit
    pct_dev_exp <- dev_exp/null_dev*100
    thresh <- as.numeric(optimal.thresholds(auc.data,opt.methods=2))[2] 
    auc.fit <- auc(auc.data,st.dev=T)
    jpeg(file=plotname)
    auc.roc.plot(auc.data,model.names=modelname,opt.thresholds=thresh)
    graphics.off()
    cmx <- cmx(auc.data,threshold=thresh)
    PCC <- pcc(cmx,st.dev=F)
    SENS <- sensitivity(cmx,st.dev=F)
    SPEC <- specificity(cmx,st.dev=F)
    KAPPA <- Kappa(cmx,st.dev=F)
    return(list(thresh=thresh,null_dev=null_dev,dev_fit=dev_fit,dev_exp=dev_exp,pct_dev_exp=pct_dev_exp,auc=auc.fit[1,1],auc.sd=auc.fit[1,2],
        plotname=plotname,pcc=PCC,sens=SENS,spec=SPEC,kappa=KAPPA))
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


read.ma <- function(out,test.dat=F){
      if(test.dat==F){
          ma.name <- out$input$ma.name
          } else ma.name <- out$input$ma.test
      tif.dir <- out$dat$tif.dir$dname
      out.list <- out$dat$ma
      out.list$status[1] <- file.access(ma.name,mode=0)==0
      ma <- try(read.csv(ma.name, header=TRUE),silent=T)
      if(class(ma)=="try-error"){
          out$ec <- out$ec+1
          out$error.mssg[[out$ec]] <- paste("ERROR: model array",ma.name,"is not readable")
          return(out)
          } else {
          out.list$status[2]<-T
          }
      if(test.dat==F){
          r.name <- out$input$response.col
          } else r.name <- out$input$test.resp.col 
      
      # remove x and y columns #
      xy.cols <- c(match("x",tolower(names(ma))),match("y",tolower(names(ma))))
      xy.cols <- xy.cols[!is.na(xy.cols)]
      if(length(xy.cols)>0) ma <- ma[,-xy.cols]
      
      # check to make sure that response column exists in the model array #
      r.col <- grep(r.name,names(ma))
      if(length(r.col)==0){
          out$ec <- out$ec+1
          out$error.mssg[[out$ec]] <- paste("ERROR: response column (",r.name,") not found in ",ma.name,sep="")
          return(out)
          }
      if(length(r.col)>1){
          out$ec <- out$ec+1
          out$error.mssg[[out$ec]] <- paste("ERROR: multiple columns in ",ma.name," match:",r.name,sep="")
          return(out)
          }
      # check that response column contains only 1's and 0's, but not all 1's or all 0's
      if(any(ma[,r.col]!=1 & ma[,r.col]!=0) | sum(ma[,r.col]==1)==nrow(ma) | sum(ma[,r.col]==0)==nrow(ma)){
          out$ec <- out$ec+1
          out$error.mssg[[out$ec]] <- paste("ERROR: response column (#",r.col,") in ",ma.name," is not binary 0/1",sep="")
          return(out)
          }
      out$dat$ma$resp.name <- names(ma)[r.col]<-"response"
      out.list$n.pres[1] <- sum(ma[,r.col])
      out.list$n.abs[1] <- nrow(ma)-sum(ma[,r.col])
      out.list$resp.name <- names(ma)[r.col]
      ma.names <- names(ma)
      
      # identify factors (this will eventually be derived from image metadata) #
      factor.cols <- grep("categorical",names(ma))
      factor.cols <- factor.cols[!is.na(factor.cols)]
      if(length(factor.cols)==0){
          out.list$factor.levels <- NA
          } else {
          names(ma) <- ma.names <-  sub("categorical.","",ma.names)
          factor.names <- ma.names[factor.cols]
          if(test.dat==F) factor.levels <- list() 
          for (i in 1:length(factor.cols)){
              f.col <- factor.cols[i]
              if(test.dat==F){
                  x <- table(ma[,f.col],ma[,1])
                  if(nrow(x)<2){
                        out$dat$bad.factor.cols <- c(out$dat$bad.factor.cols,factor.names[i])
                        }
                  lc.levs <-  as.numeric(row.names(x))[x[,2]>0] # make sure there is at least one "available" observation at each level
                  lc.levs <- data.frame(number=lc.levs,class=lc.levs)
                  factor.levels[[i]] <- lc.levs
                  } else {
                      f.index <- match(factor.names[i],names(out$dat$ma$factor.levels))
                      lc.levs <- out$dat$ma$factor.levels[[f.index]]
                  }
              ma[,f.col] <- factor(ma[,f.col],levels=lc.levs$number,labels=lc.levs$class)
              }
          if(test.dat==F) {
              names(factor.levels)<-factor.names
              out.list$factor.levels <- factor.levels
              }
          }
      
      #out.list$ma <- ma[,c(r.col,c(1:ncol(ma))[-r.col])]
      
      # if producing geotiff output, check to make sure geotiffs are available for each column of the model array #
      if(out$input$make.binary.tif==T | out$input$make.p.tif==T){ 
          tif.names <- out$dat$tif.names
          ma.cols <- match(ma.names[-r.col],sub(".tif","",basename(tif.names)))
          if(any(is.na(ma.cols))){
              out$ec <- out$ec+1
              out$error.mssg[[out$ec]] <- paste("ERROR: the following geotiff(s) are missing in ",
                        tif.dir,":  ",paste(ma.names[-r.col][is.na(ma.cols)],collapse=" ,"),sep="")
              return(out)
              }
          out$dat$tif.names <- tif.names[ma.cols]
          } else out$dat$tif.names <- ma.names[-1]

      out.list$ma <- ma[complete.cases(ma),c(r.col,c(1:ncol(ma))[-r.col])]
      if(!test.dat & !is.null(out$dat$bad.factor.cols)) out.list$ma <- out.list$ma[,-match(out$dat$bad.factor.cols,names(out.list$ma))]
      if(test.dat & any(ss<-is.na(match(names(ma),names(out$dat$ma$ma))))) {
           out$ec <- out$ec+1
           out$error.mssg[[out$ec]] <- paste("ERROR: missing columns in test model array:  ",paste(names(ma)[ss],collapse=" ,"),sep="")
           return(out)
           }  
            
      
      out.list$dims <- dim(out.list$ma)
      out.list$ratio <- min(sum(out$input$model.fitting.subset)/out.list$dims[1],1)
      out.list$n.pres[2] <- sum(out.list$ma[,1])
      out.list$n.abs[2] <- nrow(out.list$ma)-sum(out.list$ma[,1])
      out.list$used.covs <- names(out.list$ma)[-1]
      if(!is.null(out$input$model.fitting.subset)){
            pres.sample <- sample(c(1:nrow(out.list$ma))[out.list$ma[,1]==1],min(out.list$n.pres[2],out$input$model.fitting.subset[1]))
            abs.sample <- sample(c(1:nrow(out.list$ma))[out.list$ma[,1]==0],min(out.list$n.abs[2],out$input$model.fitting.subset[2]))
            out.list$ma.subset <- out.list$ma[c(pres.sample,abs.sample),]
            out.list$n.pres[3] <- length(pres.sample)
            out.list$n.abs[3] <- length(abs.sample)
            } else {
            out.list$ma.subset <- NULL
            out.list$n.pres[3] <- NA
            out.list$n.abs[3] <- NA }
      
      if(test.dat==F){
          out$dat$ma <- out.list
          } else out$dat$ma.test <- out.list
      return(out)
      }
      
lc.names <- data.frame(number=c(0:16,254,255),class=c('water',  'evergreen_forest', 'evergreen_b_forest',   'decid_n_forest',   'decid_forest',
    'mixed_forest', 'closed_shrubs',    'open_shrubs',  'woody_savannas',   'savannas', 'grasslands',
    'perm_wetlands',    'croplands',    'urban',    'crop_nat_mosaic',  'snow_and_ice', 'barren',
    'unclassified', 'fill'))

check.libs <- function(libs,out){
      lib.mssg <- unlist(suppressMessages(suppressWarnings(lapply(libs,require,quietly = T, warn.conflicts=F,character.only=T))))
      if(any(!lib.mssg)){
            out$ec <- out$ec+1
            out$dat$missing.libs <-  paste(unlist(libs)[!lib.mssg],collapse="; ")
            out$error.mssg[[out$ec]] <- paste("ERROR: the following package(s) could not be loaded:",out$dat$missing.libs)
            }
      return(out)
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

proc.tiff <- function(model,vnames,tif.dir,pred.fct,factor.levels=NA,make.binary.tif=F,make.p.tif=T,binary.thresh=NA,
    thresh=0.5,outfile.p="brt.prob.map.tif",outfile.bin="brt.bin.map.tif",tsize=2.0,NAval=-3000,fnames=NULL,logname=NULL){
    # vnames,fpath,myfun,make.binary.tif=F,outfile=NA,outfile.bin=NA,output.dir=NA,tsize=10.0,NAval=NA,fnames=NA
    # Written by Alan Swanson, YERC, 6-11-08
    # Description:
    # This function is used to make predictions using a number of .tiff image inputs
    # in cases where memory limitations don't allow the full images to be read in.
    #
    # Arguments:
    # vname: names of variables used for prediction.  must be same as filenames and variables
    #   in model used for prediction. do not include a .tif extension as this is added in code.
    # fpath: path to .tif files for predictors. use forward slashes and end with a forward slash ('/').
    # myfun: prediction function.  must generate a vector of predictions using only a
    #   dataframe as input.
    # outfile:  name of output file.  placed in same directory as input .tif files.  should
    #   have .tif extension in name.
    # tsize: size of dataframe used for prediction in MB.  this controls the size of tiles
    #   extracted from the input files, and the memory usage of this function.
    # NAval: this is the NAvalue used in the input files.
    # fnames: if the filenames of input files are different from the variable names used in the
    #   prediction model.
    #
    # Modification history:
    # NA
    #
    # Description:
    # This function reads in a limited number of lines of each image (specified in terms of the
    # size of the temporary predictor dataframe), applies a user-specified
    # prediction function, and stores the results as matrix.  Alternatively, if an
    # output file is specified, a file is written directly to that file in .tif format to
    # the same directory as the input files.  Geographic information from the input images
    # is retained.
    #
    # Example:
    # tdata <- read.csv("D:/yerc/LISN biodiversity/resource selection/split/05_GYA_Leafyspurge_reduced_250m_train.csv")
    # tdata$gya_250m_evi_16landcovermap_4ag05<-factor(tdata$gya_250m_evi_16landcovermap_4ag05)
    # f.levels <- levels(tdata$gya_250m_evi_16landcovermap_4ag05)
    # m0 <- glm(pres_abs~gya_250m_evi_01greenup_4ag05+gya_250m_evi_02browndown_4ag05+gya_250m_evi_03seasonlength_4ag05+
    #          gya_250m_evi_04baselevel_4ag05+gya_250m_evi_05peakdate_4ag05+gya_250m_evi_16landcovermap_4ag05,data=tdata,family=binomial())#
    # glm.predict <- function(x) {
    #   x$gya_250m_evi_16landcovermap_4ag05<-factor(x$gya_250m_evi_16landcovermap_4ag05,levels=f.levels)
    #   y <- as.vector(predict(m0,x,type="response"))
    #   y[is.na(y)]<- -1
    #   return(y)
    # }
    # x<-glm.predict(temp)
    # fnames <- names(tdata)[c(10:14,25)]
    # vnames <- fnames
    # fpath <- 'D:/yerc/LISN biodiversity/GYA data/gya_250m_tif_feb08_2/'
    # x <- proc.tiff(vnames,fpath,glm.predict)
    # proc.tiff(vnames,fpath,glm.predict,"test11.tif")

    # Start of function #
    require(rgdal)

    if(is.na(NAval)) NAval<- -3000
    if(is.null(fnames)) fnames <- paste(vnames,"tif",sep=".")
    nvars<-length(vnames)

    # check availability of image files #
    fnames <- fnames[match(vnames,basename(sub(".tif","",fnames)))]
    fullnames <- paste(tif.dir,fnames,sep="/")
    goodfiles <- file.access(fullnames)==0
    if(!all(goodfiles)){
        cat('\n',paste("ERROR: the following image files are missing:",paste(fullnames[!goodfiles],collapse=", ")),'\n','\n')
        flush.console()
        return(paste("ERROR: the following image files are missing:",paste(fullnames[!goodfiles],collapse=", ")))
        }
# settup up output raster to match input raster
RasterInfo=raster(fullnames[1])


    # get spatial reference info from existing image file
    gi <- GDALinfo(fullnames[1])
    dims <- as.vector(gi)[1:2]
    ps <- as.vector(gi)[6:7]
    ll <- as.vector(gi)[4:5]
    pref<-attr(gi,"projection")

RasterInfo=raster(fullnames[1])

if(!is.na(match("AREA_OR_POINT=Point",attr(gi,"mdata")))){
   xx<-RasterInfo  #this shifts by a half pixel
nrow(xx) <- nrow(xx) - 1
ncol(xx) <- ncol(xx) - 1
rs <- res(xx)
xmin(RasterInfo) <- xmin(RasterInfo) - 0.5 * rs[1]
xmax(RasterInfo) <- xmax(RasterInfo) - 0.5 * rs[1]
ymin(RasterInfo) <- ymin(RasterInfo) + 0.5 * rs[2]
ymax(RasterInfo) <- ymax(RasterInfo) + 0.5 * rs[2]
 }
    # calculate position of upper left corner and get geotransform ala http://www.gdal.org/gdal_datamodel.html
    #ul <- c(ll[1]-ps[1]/2,ll[2]+(dims[1]+.5)*ps[2])
    ul <- c(ll[1],ll[2]+(dims[1])*ps[2])
    gt<-c(ul[1],ps[1],0,ul[2],0,ps[2])

    # setting tile size
    MB.per.row<-dims[2]*nvars*32/8/1000/1024

    nrows<-min(round(tsize/MB.per.row),dims[1])
    bs<-c(nrows,dims[2])
    nbs <- ceiling(dims[1]/nrows)
    inc<-round(10/nbs,1)

    chunksize<-bs[1]*bs[2]
    tr<-blockSize(RasterInfo,chunksize=chunksize)

  continuousRaster<-raster(RasterInfo)
  NAvalue(continuousRaster)<-NAval
  continuousRaster <- writeStart(continuousRaster, filename=outfile.p, overwrite=TRUE)
    if(make.binary.tif) {
     binaryRaster<-raster(RasterInfo)
      NAvalue(binaryRaster)<-NAval
      binaryRaster <- writeStart(binaryRaster, filename=outfile.bin, overwrite=TRUE)
      }
temp <- data.frame(matrix(ncol=nvars,nrow=tr$size*ncol(RasterInfo))) # temp data.frame.
names(temp) <- vnames


  for (i in 1:tr$n) {
    strt <- c((i-1)*nrows,0)
     region.dims <- c(min(dims[1]-strt[1],nrows),dims[2])
        if (i==tr$n) {
        temp <- temp[1:(tr$nrows[i]*dims[2]),] # for the last tile...
        }
      for(k in 1:nvars) { # fill temp data frame
            temp[,k]<- getValuesBlock(raster(fullnames[k]), row=tr$row[i], nrows=tr$size)
            }
    temp[temp==NAval] <- NA # replace missing values #
        if(!is.na(factor.levels)){
            factor.cols <- match(names(factor.levels),names(temp))
            for(j in 1:length(factor.cols)){
                if(!is.na(factor.cols[j])){
                    temp[,factor.cols[j]] <- factor(temp[,factor.cols[j]],levels=factor.levels[[j]]$number,labels=factor.levels[[j]]$class)
                }
            }
        }
    ifelse(sum(!is.na(temp))==0,  # does not calculate predictions if all predictors in the region are na
        preds<-matrix(data=NaN,nrow=region.dims[1],ncol=region.dims[2]),
        preds <- t(matrix(pred.fct(model,temp),ncol=dims[2],byrow=T)))

    ## Writing to the rasters u
      if(make.binary.tif) binaryRaster<-writeValues(binaryRaster,(preds>thresh),tr$row[i])
   continuousRaster <- writeValues(continuousRaster,preds, tr$row[i])

  #NAvalue(continuousRaster) <-NAval
        rm(preds);gc() #why is gc not working on the last call
}
  continuousRaster <- writeStop(continuousRaster)
  if(make.binary.tif) writeStop(binaryRaster)
   return(0)
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


# Interpret command line argurments #
# Make Function Call #
if(Debug==F){
    Args     <- commandArgs(F)
    script.name <- strsplit(Args[grep("file",Args)],"=")[[1]][2]
    dashArgs <- Args[(grep("args",Args)+1):length(Args)]
    args <- substr(dashArgs,2,nchar(dashArgs))

    fit.rf.fct(ma.name=args[1],tif.dir=args[2],output.dir=args[3],script.name=script.name)
} 
if(Debug==T) {
    if(batch.mode==T){
        for(g in 1:length(ma.names)){
            out <- fit.rf.fct(ma.names[g],tif.dir,output.dir=output.dir,make.p.tif=make.p.tif,test.resp.col=test.resp.col,make.binary.tif=make.binary.tif,
                  debug.mode=debug.mode,response.col=response.col,ma.test=test.names[g],make.r.curves=F)
            if(!is.null(test.names)){
                auc.output <- try(make.auc.plot.jpg(out$dat$ma.test$ma[complete.cases(out$dat$ma.test$ma),],pred=tweak.p(as.vector(predict(out$mods$final.mod,newdata=out$dat$ma.test$ma[complete.cases(out$dat$ma.test$ma),],type="prob")[,2])),plotname="rf_auc_plot.jpg",modelname="RF"),
                          silent=T)
      
                #out$dat$ma.test$ma$seki_250m_evi_16landcovermap_4ag05 <- factor(out$dat$ma.test$ma$seki_250m_evi_16landcovermap_4ag05,levels=c(1,5,6,7,8,10,16))
                #out$dat$ma.test$ma$seki_250m_ndvi_16landcovermap_4ag05 <- factor(out$dat$ma.test$ma$seki_250m_ndvi_16landcovermap_4ag05,levels=c(1,5,6,7,8,10,16))
                 
                print(basename(ma.names[g]))
                print(out.table[,g]<-c(length(coef(out$mods$final.mod)),out$dat$ma$dims,out$mods$auc.output$pct_dev_exp/100,out$mods$auc.output$auc,
                          out$mods$auc.output$auc.sd,out$mods$auc.output$thresh,out$mods$auc.output$pcc,out$mods$auc.output$sens,out$mods$auc.output$spec,
                          out$mods$auc.output$kappa,out$dat$ma.test$dims,auc.output$pct_dev_exp/100,auc.output$auc,auc.output$auc.sd,auc.output$thresh,auc.output$pcc,auc.output$sens,
                          auc.output$spec,auc.output$kappa))
                flush.console()
                #assign(basename(out$dat$bname),out)
                }
            }
      write.csv(out.table,"./reanalysis/rf_test_results_tweak_p.csv")
      } else {
         out <- fit.rf.fct(ma.name,tif.dir,output.dir=output.dir,make.p.tif=make.p.tif,test.resp.col=test.resp.col,make.binary.tif=make.binary.tif,
                  debug.mode=debug.mode,response.col=response.col,ma.test=test.name)
         if(!is.null(test.name)){
              auc.output <- try(make.auc.plot.jpg(out$dat$ma.test$ma,pred=predict(out$mods$final.mod,newdata=out$dat$ma.test$ma,type='response'),
                  plotname=paste(out$dat$bname,"_test_auc_plot.jpg",sep=""),modelname="RF"),silent=T)
              }
         }
    #write.csv(data.frame(pres_abs=out$dat$ma.test$ma[,1],pred=predict.gbm(out$mods$final.mod,out$dat$ma.test$ma,
    #    out$mods$final.mod$target.trees,type="response")),"auc test data.csv",row.names=F)
    #
    }    
    
    
 