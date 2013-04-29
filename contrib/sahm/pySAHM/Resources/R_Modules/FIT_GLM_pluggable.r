# A set of "pluggable" R functions for automated model fitting of glm models to presence/absence data #
#
# Modified 12-2-09 to:  remove categorical covariates from consideration if they only contain one level
#                       ID factor variables based on "categorical" prefix and look for tifs in subdir
#                       Give progress reports
#                       write large output tif files in blocks to alleviate memory issues
#                       various bug fixes
#
#
# Modified 3-4-09 to use a list object for passing of arguements and data
#


# Libraries required to run this program #
#   PresenceAbsence - for ROC plots
#   XML - for XML i/o
#   rgdal - for geotiff i/o
#   sp - used by rdgal library
#   raster for geotiff o
options(error=NULL)

fit.glm.fct <- function(ma.name,tif.dir=NULL,output.dir=NULL,response.col="^response.binary",make.p.tif=T,make.binary.tif=T,
      simp.method="AIC",responseCurveForm=NULL,debug.mode=F,model.family="binomial",script.name="glm.r",opt.methods=2,save.model=TRUE,UnitTest=FALSE,MESS=FALSE){
    # This function fits a stepwise GLM model to presence-absence data.
    # written by Alan Swanson, 2008-2009
    ## Maintained and edited by Marian Talbert September 2010-
    # Arguements.
    # ma.name: is the name of a .csv file with a model array.  full path must be included unless it is in the current
    #  R working directory #
    # tif.dir: is the directory containing geotiffs for each covariate.  only required if geotiffs output of the 
    #   response surface is requested #    # cov.list.name: is the name of a text file with the names of covariates to be included in models (one per line).
    # output.dir: is the directory that output files will be stored in.  if not given, files will go to the current working directory. 
    # response.col: column number of the model array containing a binary 0/1 response.  all other columns will be considered explanatory variables.
    # make.p.tif: T if a geotiff of the response surface is desired.
    # make.binary.tif: T if a geotiff of the response surface is desired.
    # simp.method: model simplification method.  valid methods include: "AIC" and "BIC". 
    # debug.mode: if T, output is directed to the console during the run.  also, a pdf is generated which contains response curve plots and perspective plots
    #    showing the effects of interactions deemed important.  if F, output is diverted to a text file and the console is kept clear 
    #    except for final output of an xml file.  in either case, a set of standard output files are created in the output directory.
    # 

    # Value:
    # returns nothing but generates a number of output files in the directory
    # "output.dir" named above.  These output files consist of:
    #
    # glm_output.txt:  a text file with fairly detailed results of the final model.
    # glm_output.xml:  an xml-formatted text file with results from the final model.
    # glm_response_curves.xml:  an xml-formatted text file with response curves for
    #   each covariate in the final model.
    # glm_prob_map.tif:  a geotiff of the response surface
    # glm_bin_map.tif:  a geotiff of the binary response surface.  threhold is based on the roc curve at the point where sensitivity=specificity.
    # glm_log.txt:   a file containing text output diverted from the console when debug.mode=F
    # glm_auc_plot.jpg:  a jpg file of a ROC plot.
    # glm_response_curves.pdf:  an pdf file with response curves for
    #   each covariate in the final model and perspective plots showing the effect of interactions deemed significant.
    #   only produced when debug.mode=T
    #  seed=NULL                                 # sets a seed for the algorithm, any inegeger is acceptable
    #  opt.methods=2                             # sets the method used for threshold optimization used in the
    #                                            # the evaluation statistics module
    #  save.model=FALSE                          # whether the model will be used to later produce tifs
    #
    # when debug.mode is true, these filenames will include a number in them so that they will not overwrite preexisting files. eg brt_1_output.txt.
    #
    times <- as.data.frame(matrix(NA,nrow=7,ncol=1,dimnames=list(c("start","read data","model fit",
            "model summary","response curves","tif output","done"),c("time"))))
    times[1,1] <- unclass(Sys.time())
    t0 <- unclass(Sys.time())
    #simp.method <- match.arg(simp.method)
    out <- list(
      input=list(ma.name=ma.name,
                 tif.dir=tif.dir,
                 output.dir=output.dir,
                 response.col=response.col,
                 make.p.tif=make.p.tif,
                 model.family=model.family,
                 make.binary.tif=make.binary.tif,
                 simp.method=simp.method,
                 model.type="stepwise glm",
                 model.source.file=script.name,
                 model.fitting.subset=NULL,
                 save.model=save.model,
                 run.time=paste(c(format(Sys.time(),"%Y-%m-%d"),format(Sys.time(),"%H:%M:%S")),collapse="T"),
                 sig.test="t-test p-value",
                 MESS=MESS),
      dat = list(missing.libs=NULL,
                 output.dir=list(dname=NULL,exist=F,readable=F,writable=F),
                 tif.dir=list(dname=NULL,exist=F,readable=F,writable=F),
                 tiff.ind=NULL,
                 tif.names=NULL,
                 bname=NULL,
                 bad.factor.covs=NULL, # factorchange
                 ma=list( status=c(exists=F,readable=F),
                          dims=c(NA,NA),
                          resp.name=NULL,
                          factor.levels=NA,
                          used.covs=NULL,
                          ma=NULL,
                          train.weights=NULL,
                          test.weights=NULL,
                          train.xy=NULL,
                          test.xy=NULL,
                          ma.subset=NULL
                          ),
                 ma.test=NULL),
      mods=list(final.mod=NULL,
                r.curves=NULL,
                tif.output=list(prob=NULL,bin=NULL),
                auc.output=NULL,
                interactions=NULL,  # not used #
                summary=NULL),
      time=list(strt=unclass(Sys.time()),end=NULL),
      error.mssg=list(NULL),
      ec=0    # error count #
      )
    # load libaries #
    out <- check.libs(list("PresenceAbsence","rgdal","XML","sp","survival","tools","raster","tcltk2","foreign","ade4"),out)
    
    # exit program now if there are missing libraries #
    if(!is.null(out$error.mssg[[1]])){
          cat(saveXML(glm.to.xml(out),indent=T),'\n')
          return()
          }
          
    if(is.na(match(simp.method,c("AIC","BIC")))){
        return()
        }
        
    # check output dir #
    
    out$dat$output.dir <- check.dir(output.dir)    
    if(out$dat$output.dir$writable==F) {out$ec<-out$ec+1
              out$error.mssg[[out$ec]] <- paste("ERROR: output directory",output.dir,"is not writable")
              out$dat$output.dir$dname <- getwd()
              }
    
    # generate a filename for output #
    if(debug.mode==T){  #paste(bname,"_summary.txt",sep="")
            outfile <- paste(bname<-paste(out$dat$output.dir$dname,"/glm_",n<-1,sep=""),"_output.txt",sep="")
            while(file.access(outfile)==0) outfile<-paste(bname<-paste(out$dat$output.dir$dname,"/glm_",n<-n+1,sep=""),"_output.txt",sep="")
            capture.output(cat("temp"),file=outfile) # reserve the new basename #
    } else bname <- paste(out$dat$output.dir$dname,"/glm",sep="")
    out$dat$bname <- bname    
    
    # sink console output to log file #
    if(!debug.mode) {sink(logname <- paste(bname,"_log.txt",sep=""));on.exit(sink)} else logname<-NULL
    options(warn=1)

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
    
    if(!is.null(out$error.mssg[[1]])){
          if(!debug.mode) {sink();on.exit();unlink(logname)}
          cat(saveXML(glm.to.xml(out),indent=T),'\n')
          return()
          }
      #allowing site weights    

    times[2,1] <- unclass(Sys.time())
    if(!debug.mode) {sink();cat("Progress:20%\n");flush.console();sink(logname,append=T)} else {cat("\n");cat("20%\n")}  ### print time
    cat("\nbegin processing of model array:",out$input$ma.name,"\n")
    cat("\nfile basename set to:",out$dat$bname,"\n")
    if(debug.mode) assign("out",out,envir=.GlobalEnv)
    
       
    
           
    ##############################################################################################################
    #  Begin model fitting #
    ##############################################################################################################

    # Fit null GLM and run stepwise, then print results #
    cat("\n","Fitting stepwise GLM","\n")
    flush.console()
    penalty <- if(out$input$simp.method=="AIC") 2 else log(nrow(out$dat$ma$ma))
    scope.glm <- list(lower=as.formula(paste(out$dat$ma$resp.name,"~1")),
        upper=as.formula(paste(out$dat$ma$resp.name,"~",paste(out$dat$ma$used.covs,collapse='+'))))

    mymodel.glm.step <- step(glm(as.formula(paste(out$dat$ma$resp.name,"~1")),family=out$input$model.family,data=out$dat$ma$ma,weights=out$dat$ma$train.weights,na.action="na.exclude"),
          direction='both',scope=scope.glm,trace=0,k=penalty)
    
    out$mods$final.mod <- mymodel.glm.step

    out$dat$ma$used.covs <- attr(terms(formula(out$mods$final.mod)),"term.labels")
    #assign("out",out,envir=.GlobalEnv)
    t3 <- unclass(Sys.time())
    cat("\n","Finished with stepwise GLM","\n")
    cat("Summary of Model:","\n")
    print(out$mods$summary <- summary(mymodel.glm.step))
    if(!is.null(out$dat$bad.factor.cols)){
        cat("\nWarning: the following categorical response variables were removed from consideration\n",
            "because they had only one level:",paste(out$dat$bad.factor.cols,collapse=","),"\n\n")
        }
    flush.console()

    flush.console()
    times[3,1] <- unclass(Sys.time())
    if(!debug.mode) {sink();cat("Progress:40%\n");flush.console();sink(logname,append=T)} else cat("40%\n")

     #r<-residuals(out$mods$final.mod, "deviance")

    if(length(coef(out$mods$final.mod))==1) stop("Null model was selected.  \nEvaluation metrics and plots will not be produced")

    ##############################################################################################################
    #  Begin model output #
    ##############################################################################################################
           
    # Store .jpg ROC plot #
     txt0 <- paste("Generalized Linear Results\n",out$input$run.time,"\n\n","Data:\n\t ",ma.name,"\n\t ","n(pres)=",
        out$dat$ma$n.pres[2],"\n\t n(abs)=",out$dat$ma$n.abs[2],"\n\t number of covariates considered=",(length(names(out$dat$ma$ma))-1),
        "\n\n","Settings:\n","\n\t model family=",out$input$model.family,
        "\n\n","Results:\n\t ","number covariates in final model=",length(out$dat$ma$used.covs),
        "\n\t total time for model fitting=",round((unclass(Sys.time())-t0)/60,2),"min\n",sep="")

    capture.output(cat(txt0),file=paste(bname,"_output.txt",sep=""))

        capture.output(out$mods$summary,file=paste(bname,"_output.txt",sep=""),append=TRUE)
    if(!is.null(out$dat$bad.factor.cols)){
        capture.output(cat("\nWarning: the following categorical response variables were removed from consideration\n",
            "because they had only one level:",paste(out$dat$bad.factor.cols,collapse=","),"\n"),
            file=paste(bname,"_output.txt",sep=""),append=T)
        }


      auc.output <- make.auc.plot.jpg(out$dat$ma$ma,pred=predict(mymodel.glm.step,type='response'),plotname=paste(bname,"_auc_plot.jpg",sep=""),modelname="GLM",opt.methods=opt.methods,
            weight=out$dat$ma$train.weights,out=out)

      out$mods$auc.output<-auc.output

 # if(out$input$model.family=="poisson"){
 #     auc.output <- make.poisson.jpg(out$dat$ma$ma,pred=predict(mymodel.glm.step,type='response'),
 #     plotname=paste(bname,"_auc_plot.jpg",sep=""),modelname="BRT",
 #           weight=out$dat$ma$train.weights,out=out)

  #    out$mods$auc.output<-auc.output
   #   }

  #  out$mods$auc.output<-auc.output




    times[4,1] <- unclass(Sys.time())
    if(!debug.mode) {sink();cat("Progress:70%\n");flush.console();sink(logname,append=T)} else cat("70%\n")
    
    # Response curves #
    
if(is.null(responseCurveForm)){
responseCurveForm<-0}  
  
if(debug.mode | responseCurveForm=="pdf"){
        nvar <- length(coef(out$mods$final.mod))-1
        pcol <- min(ceiling(sqrt(nvar)),4)
        prow <- min(ceiling(nvar/pcol),3)
        
        pdf(paste(bname,"_response_curves.pdf",sep=""),width=11,height=8.5,onefile=T)
            par(oma=c(2,2,4,2),mfrow=c(prow,pcol))
            r.curves <-my.termplot(out$mods$final.mod,plot.it=T)
            mtext(paste("GLM response curves for",basename(ma.name)),outer=T,side=3,cex=1.3)
            par(mfrow=c(1,1))
            graphics.off()
        } else r.curves<-try(my.termplot(out$mods$final.mod,plot.it=F))
            
    
        if(class(r.curves)!="try-error") {
            out$mods$r.curves <- r.curves
                } else {
            out$ec<-out$ec+1
            out$error.mssg[[out$ec]] <- paste("ERROR: problem fitting response curves",r.curves)
            }
        
    
    t4 <- unclass(Sys.time())
    cat("\nfinished with final model summarization, t=",round(t4-t3,2),"sec\n");flush.console()
    times[5,1] <- unclass(Sys.time())
    if(!debug.mode) {sink();cat("Progress:80%\n");flush.console();sink(logname,append=T)} else cat("80%\n")
    
   
    ##############################################################################################################
    # Make .tif of predictions #
    ##############################################################################################################
        out$mods$final.mod$contributions$var<-attr(terms(formula(out$mods$final.mod)),"term.labels")
         assign("out",out,envir=.GlobalEnv)

 save.image(paste(output.dir,"modelWorkspace",sep="\\"))
    if(out$input$make.p.tif==T | out$input$make.binary.tif==T){
        if((n.var <- length(coef(out$mods$final.mod)))<2){
            mssg <- "Error producing geotiff output:  null model selected by stepwise procedure - pointless to make maps"
            class(mssg)<-"try-error"
            } else {
            cat("\nproducing prediction maps...","\n","\n");flush.console()
            mssg <- proc.tiff(model=out$mods$final.mod,vnames=attr(terms(formula(out$mods$final.mod)),"term.labels"),
                tif.dir=out$dat$tif.dir$dname,filenames=out$dat$tif.ind,pred.fct=glm.predict,factor.levels=out$dat$ma$factor.levels,make.binary.tif=make.binary.tif,
                thresh=out$mods$auc.output$thresh,make.p.tif=make.p.tif,outfile.p=paste(out$dat$bname,"_prob_map.tif",sep=""),
                outfile.bin=paste(out$dat$bname,"_bin_map.tif",sep=""),tsize=50,NAval=-3000,fnames=out$dat$tif.names,logname=logname,out=out)     #"brt.prob.map.tif"
            }
      #  model=out$mods$final.mod;vnames=attr(terms(formula(out$mods$final.mod)),"term.labels");
#                tif.dir=out$dat$tif.dir$dname;pred.fct=glm.predict;factor.levels=out$dat$ma$factor.levels;make.binary.tif=make.binary.tif;
#                thresh=out$mods$auc.output$thresh;make.p.tif=make.p.tif;outfile.p=paste(out$dat$bname,"_prob_map.tif",sep="");
#                outfile.bin=paste(out$dat$bname,"_bin_map.tif",sep="");tsize=50;NAval=-3000;fnames=out$dat$tif.names
        if(class(mssg)=="try-error"){
          if(!debug.mode) {sink();on.exit();unlink(logname)}
          out$ec<-out$ec+1
          out$error.mssg[[out$ec]] <- paste("Error producing prediction maps:",mssg)
          cat(saveXML(glm.to.xml(out),indent=T),'\n')
          return()
        }  else {
            if(make.p.tif) out$mods$tif.output$prob <- paste(out$dat$bname,"_prob_map.tif",sep="")
            if(make.binary.tif) out$mods$tif.output$bin <- paste(out$dat$bname,"_bin_map.tif",sep="")
            t5 <- unclass(Sys.time())
            cat("\nfinished with prediction maps, t=",round(t5-t4,2),"sec\n");flush.console()
          }
        }
    times[6,1] <- unclass(Sys.time())
    if(!debug.mode) {sink();cat("Progress:90%\n");flush.console();sink(logname,append=T)} else cat("90%\n")
    
     # Evaluation Statistics on Test Data#

    if(!is.null(out$dat$ma$ma.test)) Eval.Stat<-EvaluationStats(out,thresh=auc.output$thresh,train=out$dat$ma$ma,
    train.pred=predict(mymodel.glm.step,type="response"),opt.methods)

    
    # Write summaries to xml #
    assign("out",out,envir=.GlobalEnv)
    doc <- glm.to.xml(out)
    
    #cat(paste("\ntotal time=",round((unclass(Sys.time())-t0)/60,2),"min\n\n\n",sep=""))
    if(!debug.mode) {
        sink();on.exit();unlink(logname)
        cat("Progress:100%\n");flush.console()
        cat(saveXML(doc,indent=T),'\n')
        flush.console()
        } else {cat("100%\n")}
    capture.output(cat(saveXML(doc,indent=T)),file=paste(out$dat$bname,"_output.xml",sep=""))
    assign("fit",out$mods$final.mod,envir=.GlobalEnv)
    times[7,1] <- unclass(Sys.time())
    
    times$net <- times$time - times$time[1]
    times$pct <- round(times$net/times$net[7]*100,2)
    times$process <- c(0,times$time[-1]-times$time[-7])
    times$ppcnt <- round(times$process/times$net[7]*100,2)
    write.csv(times,paste(bname,"times.csv",sep="_"))
    invisible(out)
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

glm.to.xml <- function(out){
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
            newXMLNode("simpMethod",out$input$model.type,parent=mfp)
            newXMLNode("simpCriteria",out$input$simp.method,parent=mfp)
                  
        sv <- newXMLNode("significantVariables",parent=mo)
        if(!is.null(out$mods$summary)) {
            t.table <- out$mods$summary$coefficients
            t.table <- t.table[order(t.table[,4]),]
            dimnames(t.table)[[2]] <- c("coefficient","standardError","testStatistic","significanceMeasurement")
            t.table <- as.data.frame(t.table)
            for(i in 1:nrow(t.table)){
                x <- newXMLNode("sigVar",parent=sv)
                newXMLNode(name="name", row.names(t.table)[i],parent=x)
                kids <- lapply(1:ncol(t.table),function(j) newXMLNode(name=names(t.table)[j], t.table[i,j]))
                addChildren(x, kids)
                }
            }
        
    if(!is.null(out$mods$r.curves)){
        r.curves <-  out$mods$r.curves
        factor.levels <- out$dat$ma$factor.levels
        rc.out <- newXMLDoc()
        root <- newXMLNode("responseCurves",doc=rc.out,namespaceDefinitions=c(xsi=schema.http,noNamespaceSchemaLocation=schema.fname))
        for(i in 1:length(r.curves$names)){
            if(!is.na(f.index<-match(r.curves$names[i],names(factor.levels)))){
                  vartype <- "factor"} else vartype="continuous"
            x <- newXMLNode("responseCurve",attrs=list(covariate=r.curves$names[i],type=vartype),parent=root)
            kids <- lapply(1:length(r.curves$preds[[i]]),function(j){
                    newXMLNode(name="responsePt",parent=x,.children=list(
                        newXMLNode(name="explanatory",as.character(r.curves$preds[[i]])[j]),
                        newXMLNode(name="response",r.curves$resp[[i]][j])))})
            addChildren(x,kids)
            }
        saveXML(rc.out,rc.name,indent=T)
        
        } else { rc.name<-NULL }
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
    require(tools)
    n.images <- length(image.names)

    full.names <- image.names
    out <- data.frame(image=full.names,available=rep(F,n.images),size=rep(NA,n.images),
        type=factor(rep("unk",n.images),levels=c("asc","envi","tif","unk")))
    out$type[grep(".tif",image.names)]<-"tif"
    out$type[grep(".asc",image.names)]<-"asc"
    for(i in 1:n.images){
        if(out$type[i]=="tif"){
            x <-try(GDAL.open(full.names[1],read.only=T))
            suppressMessages(try(GDAL.close(x)))
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

#make.r.curves.glm <- function(model){
#    tms <- as.matrix(predict(model,type="terms"))
#    mf <- model.frame(model)
#    preds <- list()
#    response <- list()
#    p.names <- colnames(tms)
#    is.fac <- sapply(p.names, function(i) is.factor(mf[, i]))
#    for(i in 1:length(p.names)){
#        if(is.fac[i]){
#            ff <- mf[, p.names[i]]
#            if (!is.null(model$na.action)) ff <- naresid(model$na.action,ff)
#            xx <- as.numeric(ff)
#            ll <- levels(ff)
#            out <- rep(NA,length(ll))
#            for (j in seq_along(ll)) {
#                    ww <- which(ff == ll[j])[1]
#                    out[j]<-tms[ww,i]
#                    #out[j]<-tms[ff==ll[j],i][1]
#                    }
#            
#            }
#    
#        
#    
#data = NULL; envir = environment(formula(model));
#    partial.resid = FALSE; rug = FALSE; terms = NULL; se = FALSE;
#    xlabs = NULL; ylabs = NULL; main = NULL; col.term = 2; lwd.term = 1.5;
#    col.se = "orange"; lty.se = 2; lwd.se = 1; col.res = "gray";
#    cex = 1; pch = par("pch"); col.smth = "darkred"; lty.smth = 2;
#    span.smth = 2/3; ask = dev.interactive() && nb.fig < n.tms;
#    use.factor.levels = TRUE; smooth = NULL; ylim = "common";plot.it=F;
#terms="yell_250m_evi_16landcovermap_4ag05"
my.termplot <- function (model, data = NULL, envir = environment(formula(model)),
    partial.resid = FALSE, rug = FALSE, terms = NULL, se = FALSE,
    xlabs = NULL, ylabs = NULL, main = NULL, col.term = 2, lwd.term = 1.5,
    col.se = "orange", lty.se = 2, lwd.se = 1, col.res = "gray",
    cex = 1, pch = 1, col.smth = "darkred", lty.smth = 2,
    span.smth = 2/3, ask = dev.interactive() && nb.fig < n.tms,
    use.factor.levels = TRUE, smooth = NULL, ylim = "common",plot.it=F,
    ...)
{   # this function is borrowed from the stats library #

    which.terms <- terms
    terms <- if (is.null(terms))
        predict(model, type = "terms", se.fit = se)
    else predict(model, type = "terms", se.fit = se, terms = terms)
    n.tms <- ncol(tms <- as.matrix(if (se)
        terms$fit
    else terms))
    mf <- model.frame(model)
    if (is.null(data))
        data <- eval(model$call$data, envir)
    if (is.null(data))
        data <- mf
    if (NROW(tms) < NROW(data)) {
        use.rows <- match(rownames(tms), rownames(data))
    }
    else use.rows <- NULL
    nmt <- colnames(tms)
    cn <- parse(text = nmt)
    if (!is.null(smooth))
        smooth <- match.fun(smooth)
    if (is.null(ylabs))
        ylabs <- paste("Partial for", nmt)
    if (is.null(main))
        main <- ""
    else if (is.logical(main))
        main <- if (main)
            deparse(model$call, 500)
        else ""
    else if (!is.character(main))
        stop("'main' must be TRUE, FALSE, NULL or character (vector).")
    main <- rep(main, length.out = n.tms)
    pf <- envir
    carrier <- function(term) {
        if (length(term) > 1)
            carrier(term[[2]])
        else eval(term, data, enclos = pf)
    }
    carrier.name <- function(term) {
        if (length(term) > 1)
            carrier.name(term[[2]])
        else as.character(term)
    }
    if (is.null(xlabs))
        xlabs <- unlist(lapply(cn, carrier.name))
    if (partial.resid || !is.null(smooth)) {
        pres <- residuals(model, "partial")
        if (!is.null(which.terms))
            pres <- pres[, which.terms, drop = FALSE]
    }
    is.fac <- sapply(nmt, function(i) is.factor(mf[, i]))
    se.lines <- function(x, iy, i, ff = 2) {
        tt <- ff * terms$se.fit[iy, i]
        lines(x, tms[iy, i] + tt, lty = lty.se, lwd = lwd.se,
            col = col.se)
        lines(x, tms[iy, i] - tt, lty = lty.se, lwd = lwd.se,
            col = col.se)
    }
    if(plot.it) nb.fig <- prod(par("mfcol"))
    if (ask & plot.it) {
        oask <- devAskNewPage(TRUE)
        on.exit(devAskNewPage(oask))
    }
    ylims <- ylim
    if (identical(ylims, "common")) {
        ylims <- if (!se)
            range(tms, na.rm = TRUE)
        else range(tms + 1.05 * 2 * terms$se.fit, tms - 1.05 *
            2 * terms$se.fit, na.rm = TRUE)
        if (partial.resid)
            ylims <- range(ylims, pres, na.rm = TRUE)
        if (rug)
            ylims[1] <- ylims[1] - 0.07 * diff(ylims)
    }
    preds <- list()
    response <- list()
    p.names <- xlabs
    for (i in 1:n.tms) {
        if (identical(ylim, "free")) {
            ylims <- range(tms[, i], na.rm = TRUE)
            if (se)
                ylims <- range(ylims, tms[, i] + 1.05 * 2 * terms$se.fit[,
                  i], tms[, i] - 1.05 * 2 * terms$se.fit[, i],
                  na.rm = TRUE)
            if (partial.resid)
                ylims <- range(ylims, pres[, i], na.rm = TRUE)
            if (rug)
                ylims[1] <- ylims[1] - 0.07 * diff(ylims)
        }
        if (is.fac[i]) {
            ff <- mf[, nmt[i]]
            if (!is.null(model$na.action))
                ff <- naresid(model$na.action, ff)
            preds[[i]] <- ll <- levels(ff)
            xlims <- range(seq_along(ll)) + c(-0.5, 0.5)
            xx <- as.numeric(ff)
            response[[i]]<-rep(NA,length(ll))
            if (rug) {
                xlims[1] <- xlims[1] - 0.07 * diff(xlims)
                xlims[2] <- xlims[2] + 0.03 * diff(xlims)
            }

            if(plot.it){
                plot(1, 0, type = "n", xlab = xlabs[i], ylab = ylabs[i],
                    xlim = xlims, ylim = ylims, main = main[i], xaxt = "n",
                    ...)
                if (use.factor.levels)
                    axis(1, at = seq_along(ll), labels = ll, ...)
                else axis(1)
                for (j in seq_along(ll)) {
                    ww <- which(ff == ll[j])[c(1, 1)]
                    jf <- j + c(-0.4, 0.4)
                    lines(jf, response[[i]][j]<-tms[ww, i], col = col.term, lwd = lwd.term,...)
                    if (se) se.lines(jf, iy = ww, i = i)
                    }
            } else {
            for (j in seq_along(ll)) {
                    ww <- which(ff == ll[j])[c(1, 1)]
                    response[[i]][j]<-tms[ww, i]
                    }
                }
        }
        else {
            xx <- carrier(cn[[i]])
            if (!is.null(use.rows))
                xx <- xx[use.rows]
            xlims <- range(xx, na.rm = TRUE)
            if (rug)
                xlims[1] <- xlims[1] - 0.07 * diff(xlims)
           
            response[[i]]<-  logit(seq(min(tms[,i]),max(tms[,i]),length=100))  #aks
            preds[[i]]<-seq(min(xx),max(xx),length=100) #aks
            if(plot.it){
                 oo <- order(xx)
                 plot(xx[oo], logit(tms[oo, i]), type = "l", xlab = xlabs[i],
                    ylab = ylabs[i], xlim = xlims, ylim = logit(ylims),
                    main = main[i], col = col.term, lwd = lwd.term,
                    ...)
                if (se)
                    se.lines(xx[oo], iy = oo, i = i)
                }
        }
        if(plot.it){
            if (partial.resid) {
                if (!is.fac[i] && !is.null(smooth)) {
                    smooth(xx, pres[, i], lty = lty.smth, cex = cex,
                      pch = pch, col = col.res, col.smooth = col.smth,
                      span = span.smth)
                }
                else points(xx, pres[, i], cex = cex, pch = pch,
                    col = col.res)
            }
            if (rug) {
                n <- length(xx)
                lines(rep.int(jitter(xx), rep.int(3, n)), rep.int(ylims[1] +
                    c(0, 0.05, NA) * diff(ylims), n))
                if (partial.resid)
                    lines(rep.int(xlims[1] + c(0, 0.05, NA) * diff(xlims),
                      n), rep.int(pres[, i], rep.int(3, n)))
            }
        }
    }
    invisible(list(names=p.names,preds=preds,resp=response))
}


# Interpret command line argurments #
# Make Function Call #
 # Interpret command line argurments #
# Make Function Call #
make.p.tif=T
make.binary.tif=T
simp.method="AIC"
opt.methods=2
save.model=FALSE
MESS=FALSE

Args <- commandArgs(trailingOnly=FALSE)

    for (i in 1:length(Args)){
     if(Args[i]=="-f") ScriptPath<-Args[i+1]
     }

    print(Args)
    for (arg in Args) {
    	argSplit <- strsplit(arg, "=")
    	argSplit[[1]][1]
    	argSplit[[1]][2]
    	if(argSplit[[1]][1]=="c") csv <- argSplit[[1]][2]
    	if(argSplit[[1]][1]=="o") output <- argSplit[[1]][2]
    	if(argSplit[[1]][1]=="rc") responseCol <- argSplit[[1]][2]
    	if(argSplit[[1]][1]=="mpt") make.p.tif <- argSplit[[1]][2]
 			if(argSplit[[1]][1]=="mbt")  make.binary.tif <- argSplit[[1]][2]
 			if(argSplit[[1]][1]=="om")  opt.methods <- argSplit[[1]][2]
 			if(argSplit[[1]][1]=="savm")  save.model <- argSplit[[1]][2]
 			if(argSplit[[1]][1]=="sm")  simp.method <- argSplit[[1]][2]
 			if(argSplit[[1]][1]=="mes")  MESS <- argSplit[[1]][2]
    }
	print(csv)
	print(output)
	print(responseCol)

ScriptPath<-dirname(ScriptPath)
source(paste(ScriptPath,"LoadRequiredCode.r",sep="\\"))

make.p.tif<-as.logical(make.p.tif)
make.binary.tif<-as.logical(make.binary.tif)
save.model<-make.p.tif | make.binary.tif
opt.methods<-as.numeric(opt.methods)
MESS<-as.logical(MESS)

 fit.glm.fct(ma.name=csv,
      tif.dir=NULL,output.dir=output,
      response.col=responseCol,make.p.tif=make.p.tif,make.binary.tif=make.binary.tif,
      simp.method=simp.method,debug.mode=F,responseCurveForm="pdf",script.name="glm.r",opt.methods=opt.methods,save.model=save.model,MESS=MESS)
