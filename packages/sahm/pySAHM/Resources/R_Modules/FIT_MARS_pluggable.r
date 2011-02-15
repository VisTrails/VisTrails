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

Debug=F   # set to F for command line pluggability
if(Debug==T){
    tif.dir <- "F:/yerc/RRSC/YELL/" # directory containing geotiff files
    simp.method="AIC" # use cross-validation model simplification methods of Elith '08.
    ma.dir <- "F:/code for Jeff and Roger/jeffs paper/filtered_rs/train/"
    test.dir <- "F:/code for Jeff and Roger/jeffs paper/filtered_rs/test/"
    tif.dir <- "j:/SAHM/YELL/" # directory containing geotiff files
    ma.name <- "j:/SAHM/07_YELL_Dalmatiantoadflax_train_clean_filt_mod2.csv" # model array to use.
    ma.name <- "GSENM_cheat_pres_abs_2001_factor.mds" # model array to use.
    test.name <- NULL  # if this is supplied, it will be read for use as test data. 
    mars.degree=1
    mars.penalty=2
    ma.test=NULL
    #setwd('F:/code for Jeff and Roger/jeffs paper/data')
    library(tools)
    debug.mode=F  # if true, prints output and status updates to the console. Otherwise all of this goes to a log file and only the XML output is printed to console.
    batch.mode=F
    make.p.tif=F # make a geotiff of probability surface?
    make.binary.tif=F  # make a binary response surface geotiff?
    output.dir <- "c:/temp/"  # a set of ouput files will be created in this directory.
    ma.names <- c("a","b","c")
    test.resp.col <- "pres_abs"
    response.col <- "^response.binary"
    out.table <- as.data.frame(matrix(NA,nrow=21,ncol=length(ma.names),dimnames=list(c("ncov.final","nrow_train","ncol_train",
              "dev_exp_train","auc_train","auc.sd_train","thresh_train","pcc_train","sens_train","spec_train","kappa_train",
              "nrow_test","ncol_test","dev_exp_test","auc_test","auc.sd_test","thresh_test","pcc_test","sens_test","spec_test",
              "kappa_test"),file_path_sans_ext(basename(ma.names)))))
    }
fit.mars.fct <- function(ma.name,tif.dir=NULL,output.dir=NULL,response.col="^response.binary",test.resp.col="response",make.p.tif=T,make.binary.tif=T,
      mars.degree=1,mars.penalty=2,debug.mode=F,ma.test=NULL,script.name="mars.r"){    
    # This function fits a stepwise GLM model to presence-absence data.
    # written by Alan Swanson, 2008-2009
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
                 ma.test=ma.test,
                 tif.dir=tif.dir,
                 output.dir=output.dir,
                 response.col=response.col,
                 test.resp.col=test.resp.col,
                 make.p.tif=make.p.tif,
                 make.binary.tif=make.binary.tif,
                 mars.degree=mars.degree,
                 mars.penalty=mars.penalty,
                 model.type="stepwise with pruning",
                 model.source.file=script.name,
                 model.fitting.subset=NULL, # not used.
                 run.time=paste(c(format(Sys.time(),"%Y-%m-%d"),format(Sys.time(),"%H:%M:%S")),collapse="T"),
                 sig.test="chi-squared anova p-value"),
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
                          factor.levels=NA,
                          used.covs=NULL,
                          ma=NULL,
                          ma.subset=NULL),
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
      out <- check.libs(list("PresenceAbsence","rgdal","XML","sp","survival","mda","raster"),out)
      
      # exit program now if there are missing libraries #
      if(!is.null(out$error.mssg[[1]])){
          cat(saveXML(mars.to.xml(out),indent=T),'\n')
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
            outfile <- paste(bname<-paste(out$dat$output.dir$dname,"/mars_",n<-1,sep=""),"_output.txt",sep="")
            while(file.access(outfile)==0) outfile<-paste(bname<-paste(out$dat$output.dir$dname,"/mars_",n<-n+1,sep=""),"_output.txt",sep="")
            capture.output(cat("temp"),file=outfile) # reserve the new basename #
    } else bname <- paste(out$dat$output.dir$dname,"/mars",sep="")
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
          cat(saveXML(mars.to.xml(out),indent=T),'\n')
          return()
          }
        
    cat("\nbegin processing of model array:",out$input$ma.name,"\n")
    cat("\nfile basename set to:",out$dat$bname,"\n")
    if(debug.mode) assign("out",out,envir=.GlobalEnv)
    if(!debug.mode) {sink();cat("Progress:20%\n");flush.console();sink(logname,append=T)} else {cat("\n");cat("20%\n")}  ### print time
    ##############################################################################################################
    #  Begin model fitting #
    ##############################################################################################################

    # Fit null GLM and run stepwise, then print results #
    cat("\n","Fitting MARS model","\n")
    flush.console()
    fit <- try(mars.glm(data=out$dat$ma$ma, mars.x=c(2:ncol(out$dat$ma$ma)), mars.y=1, mars.degree=out$input$mars.degree, family="binomial", penalty=out$input$mars.penalty),silent=T)
     
    if(class(fit)=="try-error"){
          if(!debug.mode) {sink();on.exit();unlink(paste(bname,"_log.txt",sep=""))}
          out$ec<-out$ec+1
          out$error.mssg[[out$ec]]<- paste("Error fitting MARS model:",fit)
          cat(saveXML(mars.to.xml(out),indent=T),'\n')
          return()
          } else out$mods$final.mod <- fit  
    
    assign("out",out,envir=.GlobalEnv)
    t3 <- unclass(Sys.time())
    fit_contribs <- try(mars.contribs(fit),silent=T)
    if(class(fit_contribs)=="try-error"){
          if(!debug.mode) {sink();on.exit();unlink(paste(bname,"_log.txt",sep=""))}
          out$ec<-out$ec+1
          out$error.mssg[[out$ec]]<- paste("Error summarizing MARS model:",fit_contribs)
          cat(saveXML(mars.to.xml(out),indent=T),'\n')
          return()
          } 
       
    x<-fit_contribs$deviance.table
    x <- x[x[,2]!=0,]
    x <- x[order(x[,4]),]
    row.names(x) <- x[,1]
    x$df <- -1*x$df
    x <- x[,-1]
    cat("\n","Finished with MARS","\n")
    cat("Summary of Model:","\n")
    print(out$mods$summary <- x)
    if(!is.null(out$dat$bad.factor.cols)){
        cat("\nWarning: the following categorical response variables were removed from consideration\n",
            "because they had only one level:",paste(out$dat$bad.factor.cols,collapse=","),"\n\n")
        }
    cat("\n","Storing output...","\n","\n")
    flush.console()
    capture.output(print(out$mods$summary),file=paste(bname,"_output.txt",sep=""))
    if(!is.null(out$dat$bad.factor.cols)){
        capture.output(cat("\nWarning: the following categorical response variables were removed from consideration\n",
            "because they had only one level:",paste(out$dat$bad.factor.cols,collapse=","),"\n"),
            file=paste(bname,"_output.txt",sep=""),append=T)
        }
    
    if(!debug.mode) {sink();cat("Progress:40%\n");flush.console();sink(logname,append=T)} else cat("40%\n")
    
    
    ##############################################################################################################
    #  Begin model output #
    ##############################################################################################################
           
    # Store .jpg ROC plot #    
    pred<-try(mars.predict(fit,out$dat$ma$ma)$prediction[,1],silent=T)
    if(class(pred)=="try-error"){
          if(!debug.mode) {sink();on.exit();unlink(paste(bname,"_log.txt",sep=""))}
          out$ec<-out$ec+1
          out$error.mssg[[out$ec]]<- paste("Error producing ROC predictions:",pred)
          cat(saveXML(mars.to.xml(out),indent=T),'\n')
          return()
          } 
                          
    auc.output <- try(make.auc.plot.jpg(out$dat$ma$ma,pred=pred,plotname=paste(bname,"_auc_plot.jpg",sep=""),modelname="MARS"),
            silent=T)
   
    if(class(auc.output)=="try-error"){
          out$ec<-out$ec+1
          out$error.mssg[[out$ec]] <- paste("Error making ROC plot:",auc.output)
    } else { out$mods$auc.output<-auc.output}
    if(!debug.mode) {sink();cat("Progress:70%\n");flush.console();sink(logname,append=T)} else cat("70%\n")
    
    # Response curves #
    if(debug.mode){
        nvar <- nrow(out$mods$summary)
        pcol <- min(ceiling(sqrt(nvar)),4)
        prow <- min(ceiling(nvar/pcol),3)
        r.curves <- try(mars.plot(fit,plot.layout=c(prow,pcol),file.name=paste(bname,"_response_curves.pdf",sep="")),silent=T)
        
        } else r.curves<-try(mars.plot(fit,plot.it=F),silent=T)
        
        if(class(r.curves)!="try-error") {
            out$mods$r.curves <- r.curves
                } else {
            out$ec<-out$ec+1
            out$error.mssg[[out$ec]] <- paste("ERROR: problem fitting response curves",r.curves)
            }
        
    
    t4 <- unclass(Sys.time())
    cat("\nfinished with final model summarization, t=",round(t4-t3,2),"sec\n");flush.console()
    if(!debug.mode) {sink();cat("Progress:80%\n");flush.console();sink(logname,append=T)} else cat("70%\n")   
    # Make .tif of predictions #
    if(out$input$make.p.tif==T | out$input$make.binary.tif==T){
        if((n.var <- nrow(out$mods$summary))<1){
            mssg <- "Error producing geotiff output:  null model selected by stepwise procedure - pointless to make maps"
            class(mssg)<-"try-error"
            } else {
            cat("\nproducing prediction maps...","\n","\n");flush.console()
            mssg <- try(proc.tiff(model=out$mods$final.mod,vnames=names(out$dat$ma$ma)[-1],
                tif.dir=out$dat$tif.dir$dname,pred.fct=pred.mars,factor.levels=out$dat$ma$factor.levels,make.binary.tif=make.binary.tif,
                thresh=out$mods$auc.output$thresh,make.p.tif=make.p.tif,outfile.p=paste(out$dat$bname,"_prob_map.tif",sep=""),
                outfile.bin=paste(out$dat$bname,"_bin_map.tif",sep=""),tsize=50.0,NAval=-3000,
                fnames=out$dat$tif.names,logname=logname),silent=T)
            }

        if(class(mssg)=="try-error"){
          if(!debug.mode) {sink();on.exit();unlink(paste(bname,"_log.txt",sep=""))}
          out$ec<-out$ec+1
          out$error.mssg[[out$ec]] <- paste("Error producing prediction maps:",mssg)
          cat(saveXML(mars.to.xml(out),indent=T),'\n')
          return()
        }  else {
            if(make.p.tif) out$mods$tif.output$prob <- paste(out$dat$bname,"_prob_map.tif",sep="")
            if(make.binary.tif) out$mods$tif.output$bin <- paste(out$dat$bname,"_bin_map.tif",sep="")
            t5 <- unclass(Sys.time())
            cat("\nfinished with prediction maps, t=",round(t5-t4,2),"sec\n");flush.console()
          }
        }
    if(!debug.mode) {sink();cat("Progress:90%\n");flush.console();sink(logname,append=T)} else cat("90%\n")
    # read in test data #
    if(!is.null(out$input$ma.test)) out <- read.ma(out,T)
    
    # Write summaries to xml #
    if(debug.mode) assign("out",out,envir=.GlobalEnv)
    doc <- mars.to.xml(out)
    
    cat(paste("\ntotal time=",round((unclass(Sys.time())-t0)/60,2),"min\n\n\n",sep=""))
    if(!debug.mode) {
        sink();on.exit();unlink(paste(bname,"_log.txt",sep=""))
        cat("Progress:100%\n");flush.console()
        cat(saveXML(doc,indent=T),'\n')
        } else #unlink(outfile)
    capture.output(cat(saveXML(doc,indent=T)),file=paste(out$dat$bname,"_output.xml",sep=""))
    if(debug.mode) assign("fit",out$mods$final.mod,envir=.GlobalEnv)
    invisible(out)
}

pred.mars <- function(model,x) {
    # retrieve key items from the global environment #
    # make predictionss.
    y <- rep(NA,nrow(x))
    y[complete.cases(x)] <- as.vector(mars.predict(model,x[complete.cases(x),])$prediction[,1])
    
    # encode missing values as -1.
    y[is.na(y)]<- NaN
    
    # return predictions.
    return(y)
    }

logit <- function(x) 1/(1+exp(-x))


make.auc.plot.jpg<-function(ma.reduced,pred,plotname,modelname){
    auc.data <- data.frame(ID=1:nrow(ma.reduced),pres_abs=ma.reduced[,1],pred=pred)
    auc.data <- auc.data[complete.cases(auc.data),]
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

mars.to.xml <- function(out){
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
            newXMLNode("marsDegree",out$input$mars.degree,parent=mfp)
            newXMLNode("marsPenalty",out$input$mars.penalty,parent=mfp)
        
        sv <- newXMLNode("significantVariables",parent=mo)
        if(!is.null(out$mods$summary)) {
            t.table <- out$mods$summary#$coefficients
            names(t.table)[3]<-"significanceMeasurement"
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

#model=out$mods$final.mod;vnames=names(out$dat$ma$ma)[-1] #out$mods$summary[,1];
#fnames=NULL;tif.dir=out$dat$tif.dir$dname;pred.fct=mars.predict;factor.levels=out$dat$ma$factor.levels;make.binary.tif=make.binary.tif;
#thresh=out$mods$auc.output$thresh;make.p.tif=make.p.tif;outfile.p=paste(out$dat$bname,"_prob_map.tif",sep="");
#outfile.bin=paste(out$dat$bname,"_bin_map.tif",sep="");tsize=50/nrow(out$mods$summary);NAval=-3000
#

#model<-fit;vnames<-names(ma.reduced)[out$good.cols]
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
        temp <- temp[1:(tr$nrows[i]*dims[2]),]} # for the last tile...
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

###########################################################################################
#  The following functions are from Elith et al. 
###########################################################################################

"calc.deviance" <-
function(obs.values, fitted.values, weights = rep(1,length(obs.values)), family="binomial", calc.mean = TRUE)
{
# j. leathwick/j. elith
#
# version 2.1 - 5th Sept 2005
#
# function to calculate deviance given two vectors of raw and fitted values
# requires a family argument which is set to binomial by default
#
#

if (length(obs.values) != length(fitted.values)) 
   stop("observations and predictions must be of equal length")

y_i <- obs.values

u_i <- fitted.values
 
if (family == "binomial" | family == "bernoulli") {
 
   deviance.contribs <- (y_i * log(u_i)) + ((1-y_i) * log(1 - u_i))
   deviance <- -2 * sum(deviance.contribs * weights)

}

if (family == "poisson" | family == "Poisson") {

    deviance.contribs <- ifelse(y_i == 0, 0, (y_i * log(y_i/u_i))) - (y_i - u_i)
    deviance <- 2 * sum(deviance.contribs * weights)

}

if (family == "laplace") {
    deviance <- sum(abs(y_i - u_i))
    }

if (family == "gaussian") {
    deviance <- sum((y_i - u_i) * (y_i - u_i))
    }
    


if (calc.mean) deviance <- deviance/length(obs.values)

return(deviance)

}

"calibration" <-
function(obs, preds, family = "binomial")
{
#
# j elith/j leathwick 17th March 2005
# calculates calibration statistics for either binomial or count data
# but the family argument must be specified for the latter 
# a conditional test for the latter will catch most failures to specify
# the family
#

if (family == "bernoulli") family <- "binomial"
pred.range <- max(preds) - min(preds)
if(pred.range > 1.2 & family == "binomial") {
print(paste("range of response variable is ", round(pred.range, 2)), sep = "", quote = F)
print("check family specification", quote = F)
return()
}
if(family == "binomial") {
pred <- preds + 1e-005
pred[pred >= 1] <- 0.99999
mod <- glm(obs ~ log((pred)/(1 - (pred))), family = binomial)
lp <- log((pred)/(1 - (pred)))
a0b1 <- glm(obs ~ offset(lp) - 1, family = binomial)
miller1 <- 1 - pchisq(a0b1$deviance - mod$deviance, 2)
ab1 <- glm(obs ~ offset(lp), family = binomial)
miller2 <- 1 - pchisq(a0b1$deviance - ab1$deviance, 1)
miller3 <- 1 - pchisq(ab1$deviance - mod$deviance, 1)
}
if(family == "poisson") {
mod <- glm(obs ~ log(preds), family = poisson)
lp <- log(preds)
a0b1 <- glm(obs ~ offset(lp) - 1, family = poisson)
miller1 <- 1 - pchisq(a0b1$deviance - mod$deviance, 2)
ab1 <- glm(obs ~ offset(lp), family = poisson)
miller2 <- 1 - pchisq(a0b1$deviance - ab1$deviance, 1)
miller3 <- 1 - pchisq(ab1$deviance - mod$deviance, 1)
}
calibration.result <- c(mod$coef, miller1, miller2, miller3)
names(calibration.result) <- c("intercept", "slope", "testa0b1", "testa0|b1", "testb1|a")
return(calibration.result)
}

"mars.contribs" <-
function (mars.glm.object,sp.no = 1, verbose = TRUE) 
{

# j leathwick/j elith August 2006
#
# version 3.1 - developed in R 2.3.1 using mda 0.3-1
#
# takes a mars/glm model and uses the updated mars export table
# stored as the second list item from mars.binomial
# assessing the contribution of the fitted functions, 
# amalgamating terms for variables as required
#
# amended 29/9/04 to pass original mars model details
# and to return f-statistics
#
# amended 7th January to accommodate any glm model family
#
# modified 050609 by aks to output a numeric deviance table #

  mars.detail <- mars.glm.object$mars.call
  pred.names <- mars.detail$predictor.base.names #get the names from the original data
  n.preds <- length(pred.names)

  spp.names <- mars.detail$y.names
  family <- mars.detail$family

  m.table <- mars.glm.object$mars.table[-1,]
  m.table$names1 <- as.character(m.table$names1)   #convert from a factor

  x.data <- as.data.frame(eval(mars.glm.object$basis.functions))
  y.data <- as.data.frame(eval(mars.glm.object$y.values))

  assign("x.data", x.data, pos = 1)
  assign("y.data", y.data, pos = 1)
  assign("sp.no", sp.no, pos = 1)

  glm.model <- glm(y.data[,sp.no] ~ .,data = x.data,family = family)

  print(paste("performing backwards drops for mars/glm model for",
       spp.names[sp.no]),quote=F)

  n.bfs <- length(m.table[,1])
 
  delta.deviance <- rep(0,n.preds)
  df <- rep(0,n.preds)
  signif <- rep(0,n.preds)

  for (i in 1:n.preds) {   #start at two because first line is the constant
    # look for variable names in the table matching those in the var list

    var.nos <- grep(as.character(pred.names[i]),m.table$names1)

    #drop.list stores numbers of basis functions to be dropped
    if (length(var.nos) > 0) {
      drop.list <- 0 - var.nos
      x.data.new <- x.data[,drop.list]
      assign("x.data.new",x.data.new,pos=1)

      if (verbose) {
 	  print(paste("Dropping ",pred.names[i],"...",sep=""),
	             quote=FALSE)
      }

      new.model <- glm(y.data[,sp.no] ~ ., data=x.data.new, family = family)
      comparison <- anova(glm.model,new.model,test="Chisq")

      df[i] <- comparison[2,3]
      delta.deviance[i] <- zapsmall(comparison[2,4],4)
      signif[i] <- zapsmall(comparison[2,5],6)
    }
  }

  rm(x.data,y.data,sp.no,pos=1)  # tidy up temporary files    

  #deviance.table <- as.data.frame(cbind(pred.names,delta.deviance,df,signif))
  #names(deviance.table) <- c("variable","delta_dev","deg. free.","p-value")
  deviance.table <- data.frame(variable=pred.names,delta_dev=delta.deviance,df=df,p_value=signif)#aks
  return(list(mars.call=mars.detail,deviance.table=deviance.table))
}

"mars.cv" <-
function (mars.glm.object, nk = 10, sp.no = 1, prev.stratify = F) 
{
#
# j. leathwick/j. elith - August 2006
#
# version 3.1 - developed in R 2.3.1 using mda 0.3-1
#
# function to perform k-fold cross validation 
# with full model perturbation for each subset
#
# requires mda library from Cran
# requires functions mw and calibration
#
# takes a mars/glm object produced by mars.glm
# and first assesses the full model, and then 
# randomly subsets the dataset into nk folds and drops 
# each subset in turn, fitting on remaining data 
# and predicting for withheld data
#
# caters for both single species and community models via the argument sp.no
# for the first, sp.no can be left on its default of 1
# for community models, sp.no can be varied from 1 to n.spp
#
# modified 29/9/04 to 
#   1. return mars analysis details for audit trail
#   2. calculate roc and calibration on subsets as well as full data
#      returning the mean and se of the ROC scores 
#      and the mean calibration statistics
#
# modified 8/10/04 to add prevalence stratification
# modified 7th January to test for binomial family and return if not
# 
# updated 15th March to cater for both binomial and poisson families
#
# updated 16th June 2005 to calculate residual deviance
#

  data <- mars.glm.object$mars.call$dataframe    #get the dataframe name
  dataframe.name <- deparse(substitute(data))   
    
  data <- as.data.frame(eval(parse(text=data)))   #and now the data
  n.cases <- nrow(data)

  mars.call <- mars.glm.object$mars.call          #and the mars call details
  mars.x <- mars.call$mars.x    
  mars.y <- mars.call$mars.y
  mars.degree <- mars.call$degree
  mars.penalty <- mars.call$penalty
  family <- mars.call$family
  site.weights <- eval(mars.glm.object$weights$site.weights)

  n.spp <- length(mars.y)

  if (sp.no > n.spp) {
    print(paste("the value specified for sp.no of",sp.no),quote=F)
    print(paste("exceeds the total number of species, which is ",n.spp),quote=F)
    return()
  }
  
  xdat <- as.data.frame(data[,mars.x])
  xdat <- mars.new.dataframe(xdat)[[1]]
  ydat <- mars.glm.object$y.values[,sp.no]
  target.sp <- names(data)[mars.y[sp.no]]

  if (prev.stratify) {
    presence.mask <- ydat == 1
    absence.mask <- ydat == 0
    n.pres <- sum(presence.mask)
    n.abs <- sum(absence.mask)
  }

  print(paste("Calculating ROC and calibration from full model for",target.sp),quote=F)

  u_i <- mars.glm.object$fitted.values[,sp.no]
  y_i <- ydat

  if (family == "binomial") {
    full.resid.deviance <- calc.deviance(y_i,u_i, weights = site.weights, family="binomial") 
    full.test <- roc(y_i, u_i)
    full.calib <- calibration(y_i, u_i)
  }

  if (family=="poisson") {
    full.resid.deviance <- calc.deviance(y_i,u_i, weights = site.weights, family="poisson")
    full.test <- cor(y_i, u_i) 
    full.calib <- calibration(y_i, u_i, family = "poisson")
  }

# set up for results storage
  
  subset.test <- rep(0,nk)
  subset.calib <- as.data.frame(matrix(0,ncol=5,nrow=nk))
  names(subset.calib) <- c("intercept","slope","test1","test2","test3")
  subset.resid.deviance <- rep(0,nk)

# now setup for withholding random subsets
    
  pred.values <- rep(0, n.cases)
  fitted.values <- rep(0, n.cases)

  if (prev.stratify) {

    selector <- rep(0,n.cases)

#create a vector of randomised numbers and feed into presences

    temp <- rep(seq(1, nk, by = 1), length = n.pres)
    temp <- temp[order(runif(n.pres, 1, 100))]
    selector[presence.mask] <- temp

# and then do the same for absences

    temp <- rep(seq(1, nk, by = 1), length = n.abs)
    temp <- temp[order(runif(n.abs, 1, 100))]
    selector[absence.mask] <- temp

  }
  else {  #otherwise make them random with respect to presence/absence

    selector <- rep(seq(1, nk, by = 1), length = n.cases)
    selector <- selector[order(runif(n.cases, 1, 100))]
  }
 
  print("", quote = FALSE)
  print("Creating predictions for subsets...", quote = F)

  for (i in 1:nk) {
    cat(i," ")
    model.mask <- selector != i  #used to fit model on majority of data
    pred.mask <- selector == i   #used to identify the with-held subset
    assign("species.subset", ydat[model.mask], pos = 1)
    assign("predictor.subset", xdat[model.mask, ], pos = 1)

    # fit new mars model

    mars.object <- mars(y = species.subset, x = predictor.subset, 
      degree = mars.degree, penalty = mars.penalty)

    # and extract basis functions

    n.bfs <- length(mars.object$selected.terms)
    bf.data <- as.data.frame(mars.object$x)
    names(bf.data) <- paste("bf",1:n.bfs,sep="")
    assign("bf.data", bf.data, pos=1)

    # then fit a binomial model to them

    mars.binomial <- glm(species.subset ~ .,data=bf.data[,-1], family= family, maxit = 100)

    pred.basis.functions <- as.data.frame(mda:::model.matrix.mars(mars.object, 
      xdat[pred.mask, ]))

    #now name the bfs to match the approach used in mars.binomial

    names(pred.basis.functions) <- paste("bf",1:n.bfs,sep="")

    # and form predictions for them and evaluate performance

    fitted.values[pred.mask] <- predict(mars.binomial, 
      pred.basis.functions, type = "response")

    y_i <- ydat[pred.mask]
    u_i <- fitted.values[pred.mask]  
    weights.subset <- site.weights[pred.mask]

    if (family == "binomial") {
      subset.resid.deviance[i] <- calc.deviance(y_i,u_i,weights = weights.subset, family="binomial") 
      subset.test[i] <- roc(y_i,u_i)
      subset.calib[i,] <- calibration(y_i, u_i)
    }

    if (family=="poisson"){
      subset.resid.deviance[i] <- calc.deviance(y_i,u_i,weights = weights.subset, family="poisson") 
      subset.test[i] <- cor(y_i, u_i) 
      subset.calib[i,] <- calibration(y_i, u_i, family = family)
    }
  }
 
  cat("","\n")

# tidy up temporary files

  rm(species.subset,predictor.subset,bf.data,pos=1) 

# and assemble results for return

#  mars.detail <- list(dataframe = dataframe.name,
#    x = mars.x, x.names = names(xdat), 
#    y = mars.y, y.names = names(data)[mars.y], 
#    target.sp = target.sp, degree=mars.degree, penalty = mars.penalty, family = family)

  y_i <- ydat
  u_i <- fitted.values

  if (family=="binomial") {
    cv.resid.deviance <- calc.deviance(y_i,u_i,weights = site.weights, family="binomial") 
    cv.test <- roc(y_i, u_i)
    cv.calib <- calibration(y_i, u_i)
  }

  if (family=="poisson"){
    cv.resid.deviance <- calc.deviance(y_i,u_i,weights = site.weights, family="poisson") 
    cv.test <- cor(y_i, u_i) 
    cv.calib <- calibration(y_i, u_i, family = "poisson")
  }

  subset.test.mean <- mean(subset.test)
  subset.test.se <- sqrt(var(subset.test))/sqrt(nk)

  subset.test <- list(test.scores = subset.test, subset.test.mean = subset.test.mean, 
    subset.test.se = subset.test.se)

  subset.calib.mean <- apply(subset.calib[,c(1:2)],2,mean)
  names(subset.calib.mean) <- names(subset.calib)[c(1:2)] #mean only of parameters

  subset.calib <- list(subset.calib = subset.calib, 
    subset.calib.mean = subset.calib.mean)
    
  subset.deviance.mean <- mean(subset.resid.deviance)
  subset.deviance.se <- sqrt(var(subset.resid.deviance))/sqrt(nk)

  subset.deviance <- list(subset.deviances = subset.resid.deviance, subset.deviance.mean = subset.deviance.mean,
    subset.deviance.se = subset.deviance.se)

  return(list(mars.call = mars.call, full.resid.deviance = full.resid.deviance,
    full.test = full.test, full.calib = full.calib, pooled.deviance = cv.resid.deviance, pooled.test = cv.test, 
    pooled.calib = cv.calib,subset.deviance = subset.deviance, subset.test = subset.test, subset.calib = subset.calib))
}

"mars.export" <-
function (object,lineage) 
{
#
# j leathwick/j elith August 2006
#
# takes a mars model fitted using library mda
# and extracts the basis functions and their 
# coefficients, returning them as a table
# caters for models with degree up to 2
#
# version 3.1 - developed in R 2.3.1 using mda 0.3-1

  which <- object$selected.terms
  nterms <- length(which)
  nspp <- ncol(eval(object$call$y))
  dir <- object$factor
  cut <- object$cuts
  var.names <- dimnames(object$factor)[[2]]
  p <- length(var.names)
  coefs <- as.data.frame(object$coefficients)
  names(coefs) <- names(eval(object$call$y))

# setup storage for results

  names1 <- rep("null", length = nterms)
  types1 <- rep("null", length = nterms)
  levels1 <- rep("null", length = nterms)
  signs1 <- rep(0, length = nterms)
  cuts1 <- rep(0, length = nterms)

  names2 <- rep("null", length = nterms)
  types2 <- rep("null", length = nterms)
  levels2 <- rep("null", length = nterms)
  signs2 <- rep(0, length = nterms)
  cuts2 <- rep(0, length = nterms)
  names1[1] <- "constant"
  signs1[1] <- 1
 
# now cycle through the terms

  for (i in seq(2, nterms)) {
 
    j <- which[i]
      term.count = 1
      for (k in 1:p) {
        if (dir[j, k] != 0) {
          if (term.count == 1) {
            n <- match(var.names[k],lineage$full.name)
            names1[i] <- lineage$base.name[n] #var.names[k]
            types1[i] <- lineage$type[n]
            levels1[i] <- lineage$level[n]
            signs1[i] <- dir[j, k]
            cuts1[i] <- cut[j, k]
            term.count <- term.count + 1
          }
          else {
            names2[i] <- var.names[k]
            n <- match(var.names[k],lineage$full.name)
            names2[i] <- lineage$base.name[n] #var.names[k]
            types2[i] <- lineage$type[n]
            levels2[i] <- lineage$level[n]
            signs2[i] <- dir[j, k]
            cuts2[i] <- cut[j, k]
          }
        }
      }
    }

  mars.export.table <- data.frame(names1, types1, levels1, signs1, cuts1, 
       names2, types2, levels2, signs2, cuts2, coefs)

  return(mars.export.table)
}

"mars.glm" <-
function (data,                         # the input data frame
  mars.x,                               # column numbers of the predictors
  mars.y,                               # column number(s) of the response variable(s)
  mars.degree = 1,                      # level of interactions - 1 = zero, 2 = 1st order, etc
  site.weights = rep(1, nrow(data)),    # one weight per site
  spp.weights = rep(1,length(mars.y)),  # one wieght per species
  penalty = 2,                          # the default penaly for a mars model
  family = "binomial")                  # the family for the glm model
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
# requires mda and leathwick/elith's mars.export
#
# modified 3/11/04 to store information on glm phase convergence
# and with number of iterations raised to 100 to encourage convergence for low prevalence species
# modified 4/11/04 to accommodate observation weights in both mars and glm steps
# modified 12/04 to accommodate non-binomial families
# modified 11/05 to accommodate factor variables
# these are done as 0/1 dummy variables in a new dataframe
# created using mars.new.dataframe

  require(mda)
 
  n.spp <- length(mars.y)

# setup input data and assign to position one

  dataframe.name <- deparse(substitute(data))  # get the dataframe name

  xdat <- as.data.frame(eval(data[, mars.x]))                 #form the temporary datasets
  predictor.base.names <- names(xdat)

# create the new dataframe with dummy vars for factor predictors
  xdat <- mars.new.dataframe(xdat)
  lineage <- xdat[[2]]   # tracks which variables have had dummy's created
  xdat <- xdat[[1]]
  predictor.dummy.names <- names(xdat)

  ydat <- as.data.frame(eval(data[, mars.y]))
  names(ydat) <- names(data)[mars.y]

  assign("xdat", xdat, pos = 1)               #and assign them for later use
  assign("ydat", ydat, pos = 1)

# create storage space for glm model results

  n.cases <- nrow(xdat)

  fitted.values <- matrix(0,ncol = n.spp, nrow = n.cases)
  model.residuals <- matrix(0,ncol = n.spp, nrow = n.cases)
  null.deviances <- rep(0,n.spp)
  residual.deviances <- rep(0,n.spp)
  null.dfs <- rep(0,n.spp)
  residual.dfs <- rep(0,n.spp)
  converged <- rep(TRUE,n.spp)

# fit the mars model and extract the basis functions

  cat("fitting initial mars model for",n.spp,"responses","\n")
  cat("followed by a glm model with a family of",family,"\n")

  mars.object <- mars(x = xdat, y = ydat, degree = mars.degree, w = site.weights, 
       wp = spp.weights, penalty = penalty)

  bf.data <- as.data.frame(eval(mars.object$x))
  n.bfs <- ncol(bf.data)
  bf.names <- paste("bf", 1:n.bfs, sep = "")
  names(bf.data) <- bf.names
  bf.data <- as.data.frame(bf.data[,-1])

  m.table <- as.data.frame(mars.export(mars.object,lineage))
  names(m.table)[(10 + 1):(10 + n.spp)] <- names(ydat)

  p.values <- matrix(0, ncol = n.spp, nrow = n.bfs)
  rownames(p.values) <- paste("bf", 1:n.bfs, sep = "")
  colnames(p.values) <- names(ydat)

# now cycle through the species fitting glm models 

  cat("fitting glms for individual responses","\n")

  for (i in 1:n.spp) {

    cat(names(ydat)[i],"\n")
    model.glm <- glm(ydat[, i] ~ ., data = bf.data, weights = site.weights, 
  	  family = family, maxit = 100)

# update the coefficients and other results

    # then match names and insert as appropriate
    m.table[ , i + 10] <- 0   					# set all values to zero
    m.table[ , i + 10] <- model.glm$coefficients  	      # update all the constant
    sum.table <- summary(model.glm)$coefficients
    p.values[,i] <- sum.table[,4]
    fitted.values[,i] <- model.glm$fitted
    model.residuals[,i] <- resid(model.glm)
    null.deviances[i] <- model.glm$null.deviance
    residual.deviances[i] <- model.glm$deviance
    null.dfs[i] <- model.glm$df.null
    residual.dfs[i] <- model.glm$df.residual
    converged[i] <- model.glm$converged
  }

# now assemble data to be returned

  fitted.values <- as.data.frame(fitted.values)
  names(fitted.values) <- names(ydat)

  model.residuals <- as.data.frame(model.residuals)
  names(model.residuals) <- names(ydat)

  deviances <- data.frame(names(ydat),null.deviances,null.dfs,residual.deviances,residual.dfs,converged)
  names(deviances) <- c("species","null.dev","null.df","resid.dev","resid.df","converged")

  weights = list(site.weights = site.weights, spp.weights = spp.weights)

  mars.detail <- list(dataframe = dataframe.name, mars.x = mars.x, 
    predictor.base.names = predictor.base.names, predictor.dummy.names = predictor.dummy.names, 
    mars.y = mars.y, y.names = names(ydat), degree=mars.degree, penalty = penalty, 
    family = family)

  rm(xdat,ydat,pos=1)           #finally, clean up the temporary dataframes

  return(list(mars.table = m.table, basis.functions = bf.data, y.values = ydat,
    fitted.values = fitted.values, residuals = model.residuals, weights = weights, deviances = deviances,
    p.values = p.values, mars.call = mars.detail,mars.object=mars.object))
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

"mars.plot" <-
function (mars.glm.object,  #the input mars object
   sp.no = 0,               # the species number for multi-response models
   plot.rug=T,              # plot a rug of deciles
   plot.layout = c(3,4),    # the plot layout to use
   file.name = NA,          # giving a file name will send results to a pdf
   plot.it=T)               # option for making curves but no plots (aks)
{

# j leathwick/j elith August 2006
#
# version 3.1 - developed in R 2.3.1 using mda 0.3-1
#
# requires mars.export of leathwick/elith
# 
# takes a mars or mars/glm model and either 
# creates a mars export table (vanilla mars object)
# and works from this or uses the updated mars export table
# stored as the first list item from mars.binomial
# plotting out the fitted functions, amalgamating terms
# for variables and naming the pages as required
#
# caters for multispecies mars models by successively plotting
# all species unless a value other than zero is given for sp.no
#
# modified by aks 050609 to only open one plot window and use the record=T option.

  max.plots <- plot.layout[1] * plot.layout[2]
  if(plot.it){ #aks
      if (is.na(file.name)) {
        use.windows = TRUE 
        windows(width = 11, height = 8, record=T) #AKS
        par(mfrow = plot.layout) #AKS
               }
      else {
        use.windows = FALSE
        pdf(file=file.name,width = 11, height=8)
        par(mfrow = plot.layout) #AKS
      }
  } else use.windows = FALSE

  if (class(mars.glm.object) == "mars") {  #then we have a mars object
    mars.binomial = FALSE
    model <- mars.glm.object
    xdat <- eval(model$call$x)
    Y <- as.data.frame(eval(model$call$y))
    n.env <- ncol(xdat)
    m.table <- mars.export(mars.glm.object)
  }
  else {
    mars.binomial = TRUE

    dat <- mars.glm.object$mars.call$dataframe
    mars.x <- mars.glm.object$mars.call$mars.x
    xdat <- as.data.frame(eval(parse(text=dat)))
    xdat <- xdat[,mars.x]

    m.table <- mars.glm.object[[1]]

  }

  n.bfs <- length(m.table[,1])
  n.spp <- length(m.table[1,]) - 10
  r.curves <- list(names=NULL,preds=list(),resp=list()) #aks
  spp.names <- names(m.table)[(10+1):(10+n.spp)]

  if (sp.no == 0) {
    wanted.species <- seq(1:n.spp) 
  }
  else {
    wanted.species <- sp.no
  }

  xrange <- matrix(0,nrow = 2,ncol = ncol(xdat))
  factor.filter <- rep(FALSE,ncol(xdat))
  for (i in 1:ncol(xdat)) factor.filter[i] <- is.vector(xdat[,i])
  xrange[,factor.filter] <- sapply(xdat[,factor.filter], range)
  for (i in wanted.species) {
    n.pages <- 1
    plotit <- rep(TRUE, n.bfs)
    print(paste("plotting responses for ",spp.names[i]),quote=F)
    nplots <- 0
    cntr <- 1 #aks
    for (j in 2:n.bfs) {
      if (m.table$names2[j] == "null") {
        if (plotit[j]) {
          varno <- pmatch(as.character(m.table$names1[j]), 
          names(xdat))
          if (factor.filter[varno]) {
            Xi <- seq(xrange[1, varno], xrange[2, varno], 
               length = 100)
            bf <- pmax(0, m.table$signs1[j] * (Xi - m.table$cuts1[j]))
            bf <- bf * m.table[j, i + 10]
            bf <- bf - mean(bf)
          }
          else {
            factor.table <- as.data.frame(table(xdat[,varno]))
            names(factor.table) <- c("levels","coefficients")
            factor.table$coefficients <- 0
            level.no <- match(m.table$levels1[j],factor.table$levels)
            factor.table$coefficients[level.no] <- m.table[j, i + 10]
          }
          if (j < n.bfs) {
            for (k in ((j + 1):n.bfs)) {
              if (m.table$names1[j] == m.table$names1[k] & m.table$names2[k] == "null") {
                    if (factor.filter[varno]) {
                      bf.add <- pmax(0, m.table$signs1[k] * 
                          (Xi - m.table$cuts1[k]))
                      bf.add <- bf.add * m.table[k, i + 10]
                      bf <- bf + bf.add
                    }
                    else {
                      level.no <- match(m.table$levels1[k],factor.table$levels)
                      factor.table$coefficients[level.no] <- m.table[k, i + 10]
                    }
                    plotit[k] <- FALSE
              }
            }
          }
          #if (nplots == 0) { #AKS
#            if (use.windows) windows(width = 11, height = 8)
#              par(mfrow = plot.layout)
#            }
            if (factor.filter[varno]) {
              if(plot.it) plot(Xi, bf, type = "l", xlab = names(xdat)[varno], ylab = "response") #aks
              if (plot.rug & plot.it) rug(quantile(xdat[,varno], probs = seq(0, 1, 0.1), na.rm = FALSE))
              r.curves$preds[[cntr]] <- Xi #aks
              r.curves$resp[[cntr]] <- bf #aks
            }
            else {
              if(plot.it) plot(factor.table$levels, factor.table$coefficients, xlab = names(xdat)[varno]) #aks
              r.curves$preds[[cntr]] <- factor.table$levels #aks
              r.curves$resp[[cntr]] <- factor.table$coefficients #aks
              
            }
            r.curves$names <- c(r.curves$names,names(xdat)[varno])  #aks
            cntr <- cntr + 1  #aks
            nplots = nplots + 1
            plotit[j] <- FALSE
          }
        }
        else {  # case where there is an interaction #
          if (plotit[j]) {
            varno1 <- pmatch(as.character(m.table$names1[j]), names(xdat))
            X1 <- seq(xrange[1, varno1], xrange[2, varno1], length = 20)
            bf1 <- pmax(0, m.table$signs1[j] * (X1 - m.table$cuts1[j]))
            varno2 <- pmatch(as.character(m.table$names2[j]), names(xdat))
            X2 <- seq(xrange[1, varno2], xrange[2, varno2], length = 20)
            bf2 <- pmax(0, m.table$signs2[j] * (X2 - m.table$cuts2[j]))
            if(factor.filter[varno1] & factor.filter[varno2]){ #aks
                zmat <- bf1 %o% bf2
                zmat <- zmat * m.table[j, i + 10]
                if (j < n.bfs) {
                  for (k in ((j + 1):n.bfs)) {
                    if (m.table$names1[j] == m.table$names1[k] & m.table$names2[j] == m.table$names2[k]) {
                      bf1 <- pmax(0, m.table$signs1[k] * (X1 - m.table$cuts1[k]))
                      bf2 <- pmax(0, m.table$signs2[j] * (X2 - m.table$cuts2[j]))
                      zmat2 <- bf1 %o% bf2
                      zmat2 <- zmat2 * m.table[j, i + 10]
                      zmat = zmat + zmat2
                      plotit[k] <- FALSE
                    }
                  }
                }
              #if (nplots == 0) {  #AKS
    #            if (use.windows) windows(width = 11, height = 8)
    #            par(mfrow = plot.layout)
    #          }
                if(plot.it){
                    persp(x = X1, y = X2, z = zmat, xlab = names(xdat)[varno1], 
                              ylab = names(xdat)[varno2], theta = 45, phi = 25) }
                r.curves$preds[[cntr]] <- X1 #aks
                r.curves$resp[[cntr]] <- apply(zmat,1,mean,na.rm=T) #aks
                nplots = nplots + 1
                } else {
                    r.curves$preds[[cntr]] <- NA #aks
                    r.curves$resp[[cntr]] <- NA #aks
                    
                }
        r.curves$names <- c(r.curves$names,names(xdat)[varno]) #aks
        cntr <- cntr + 1 #aks
        }
      }
      if (nplots == 1 & plot.it) {
        title(paste(spp.names[i], " - page ", n.pages, sep = ""))
      }
      if (nplots == max.plots) {
        nplots = 0
        n.pages <- n.pages + 1
      }
    }
  }
  if (!use.windows & plot.it) dev.off()
  invisible(r.curves) #aks
}

"mars.plot.fits" <-
function(mars.glm.object,    # the input mars object
   sp.no = 0,                # allows selection of individual spp for multiresponse models
   mask.presence = FALSE,    # plots out just presence records
   use.factor = FALSE,       # draws plots as factors for faster printing
   plot.layout = c(4,2),     # the default plot layout
   file.name = NA)           # allows plotting to a pdf file
{
#
# j leathwick, j elith - August 2006
#
# version 3.1 - developed in R 2.3.1 using mda 0.3-1
#
# to plot distribution of fitted values in relation to ydat from mars or other p/a models
# allows masking out of absences to enable focus on sites with high predicted values
# fitted values = those from model; raw.values = original y values
# label = text species name; ydat = predictor dataset
# mask.presence forces function to only plot fitted values for presences
# use.factor forces to use quicker printing box and whisker plot
# file.name routes to a pdf file of this name
#

  max.plots <- plot.layout[1] * plot.layout[2]

  if (is.na(file.name)) {    #setup for windows or file output
    use.windows = TRUE 
  }
  else {
    pdf(file.name, width=8, height = 11)
    par(mfrow = plot.layout)
    par(cex = 0.5)
    use.windows = FALSE
  }

  dat <- mars.glm.object$mars.call$dataframe    #get the dataframe name
  dat <- as.data.frame(eval(parse(text=dat)))   #and now the data

  n.cases <- nrow(dat)

  mars.call <- mars.glm.object$mars.call	#and the mars call details
  mars.x <- mars.call$mars.x    
  mars.y <- mars.call$mars.y
  family <- mars.call$family

  xdat <- as.data.frame(dat[,mars.x])
  ydat <- as.data.frame(dat[,mars.y])

  n.spp <- ncol(ydat)
  n.preds <- ncol(xdat)

  fitted.values <- mars.glm.object$fitted.values

  pred.names <- names(dat)[mars.x]
  spp.names <- names(dat)[mars.y]

  if (sp.no == 0) {
    wanted.species <- seq(1:n.spp) 
    }
  else {
    wanted.species <- sp.no
    }

  for (i in wanted.species) {

    if (mask.presence) {
	mask <- ydat[,i] == 1 }
    else {
      mask <- rep(TRUE, length = n.cases) 
    }

    robust.max.fit <- approx(ppoints(fitted.values[mask,i]), sort(fitted.values[mask,i]), 0.99) #find 99%ile value
    nplots <- 0

    for (j in 1:n.preds) {
      if (use.windows & nplots == 0) {
        windows(width = 8, height = 11)
        par(mfrow = plot.layout)
        par(cex = 0.5)
      }
	nplots <- nplots + 1    
      if (is.vector(xdat[,j])) wt.mean <- mean((xdat[mask, j] * fitted.values[mask, i]^5)/mean(fitted.values[mask, i]^5))
        else wt.mean <- 0
	if (use.factor) {
	temp <- factor(cut(xdat[mask, j], breaks = 12))
	if (family == "binomial") {
	  plot(temp, fitted.values[mask,i], xlab = pred.names[j], ylab = "fitted values", ylim = c(0, 1))
      }
	else {
	  plot(temp, fitted.values[mask,i], xlab = pred.names[j], ylab = "fitted values")}
	}
	else {
	  if (family == "binomial") {
	    plot(xdat[mask, j], fitted.values[mask,i], xlab = pred.names[j], ylab = "fitted values", 
					ylim = c(0, 1))
        }
	  else {
          plot(xdat[mask, j], fitted.values[mask,i], xlab = pred.names[j], ylab = "fitted values")
        }
	}
	abline(h = (0.333 * robust.max.fit$y), lty = 2.)
	if (nplots == 1) { 
  	  title(paste(spp.names[i], ", wtm = ", zapsmall(wt.mean, 4.)))}
	else {
	  title(paste("wtm = ", zapsmall(wt.mean, 4.)))}
	  nplots <- ifelse(nplots == max.plots, 0, nplots)
	}
    }
  if (!use.windows) dev.off()
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

  base.data <- as.data.frame(eval.parent(parse(text = dataframe.name))) #aks

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

"roc" <-
function (obsdat, preddat) 
{
# code adapted from Ferrier, Pearce and Watson's code, by J.Elith
#
# see:
# Hanley, J.A. & McNeil, B.J. (1982) The meaning and use of the area
# under a Receiver Operating Characteristic (ROC) curve.
# Radiology, 143, 29-36
#
# Pearce, J. & Ferrier, S. (2000) Evaluating the predictive performance
# of habitat models developed using logistic regression.
# Ecological Modelling, 133, 225-245.
# this is the non-parametric calculation for area under the ROC curve, 
# using the fact that a MannWhitney U statistic is closely related to
# the area
#
    if (length(obsdat) != length(preddat)) 
        stop("obs and preds must be equal lengths")
    n.x <- length(obsdat[obsdat == 0])
    n.y <- length(obsdat[obsdat == 1])
    xy <- c(preddat[obsdat == 0], preddat[obsdat == 1])
    rnk <- rank(xy)
    wilc <- ((n.x * n.y) + ((n.x * (n.x + 1))/2) - sum(rnk[1:n.x]))/(n.x * 
        n.y)
    return(round(wilc, 4))
}



# Interpret command line argurments #
# Make Function Call #
if(Debug==F){
   Args     <- commandArgs(F)
    script.name <- strsplit(Args[grep("file",Args)],"=")[[1]][2]
    dashArgs <- Args[(grep("args",Args)+1):length(Args)]
    args <- substr(dashArgs,2,nchar(dashArgs))

    fit.mars.fct(ma.name=args[1],tif.dir=args[2],output.dir=args[3],script.name=script.name)
} 


if(Debug==T) {
    if(batch.mode==T){
        for(g in 1:length(ma.names)){
            out <- fit.mars.fct(ma.names[g],tif.dir,output.dir=output.dir,make.p.tif=make.p.tif,test.resp.col=test.resp.col,make.binary.tif=make.binary.tif,
                  mars.degree=mars.degree,mars.penalty=mars.penalty,debug.mode=debug.mode,response.col=response.col,ma.test=test.names[g])
            if(!is.null(test.names)){
                auc.output <- try(make.auc.plot.jpg(out$dat$ma.test$ma[complete.cases(out$dat$ma.test$ma),],pred=as.vector(mars.predict(out$mods$final.mod,out$dat$ma.test$ma[complete.cases(out$dat$ma.test$ma),])$prediction[,1]),plotname=paste(out$dat$bname,"_auc_plot.jpg",sep=""),modelname="MARS"),
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
      } else {
         out <- fit.mars.fct(ma.name,tif.dir,output.dir=output.dir,make.p.tif=make.p.tif,test.resp.col=test.resp.col,make.binary.tif=make.binary.tif,
                  mars.degree=mars.degree,mars.penalty=mars.penalty,debug.mode=debug.mode,response.col=response.col,ma.test=test.name)
         if(!is.null(test.name)){
              auc.output <- try(make.auc.plot.jpg(out$dat$ma.test$ma,pred=predict(out$mods$final.mod,newdata=out$dat$ma.test$ma,type='response'),
                  plotname=paste(out$dat$bname,"_test_auc_plot.jpg",sep=""),modelname="GLM"),silent=T)
              }
         }
    #write.csv(data.frame(pres_abs=out$dat$ma.test$ma[,1],pred=predict.gbm(out$mods$final.mod,out$dat$ma.test$ma,
    #    out$mods$final.mod$target.trees,type="response")),"auc test data.csv",row.names=F)
    #write.csv(out.table[,1:49],"./reanalysis/mars_test_results_penalty8.csv")
    }    
    
