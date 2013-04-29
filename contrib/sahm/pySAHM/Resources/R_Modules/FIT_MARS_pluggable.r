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

fit.mars.fct <- function(ma.name,tif.dir=NULL,output.dir=NULL,response.col="^response.binary",make.p.tif=T,make.binary.tif=T,
      mars.degree=1,mars.penalty=2,responseCurveForm=NULL,debug.mode=T,script.name="mars.r",opt.methods=2,save.model=TRUE,UnitTest=FALSE,MESS=FALSE){
    # This function fits a stepwise GLM model to presence-absence data.
    # written by Alan Swanson, 2008-2009
    # # Maintained and edited by Marian Talbert September 2010-
    # Arguements.
    # ma.name: is the name of a .csv file with a model array.  full path must be included unless it is in the current
    #  R working directory # THIS FILE CAN NOW INCLUDE AN OPTIONAL COLUMN OF SITE WEIGHTS WHICH MUST BE LABELED "site.weights"
    # tif.dir: is the directory containing geotiffs for each covariate.  only required if geotiffs output of the 
    #   response surface is requested #    # cov.list.name: is the name of a text file with the names of covariates to be included in models (one per line).
    # output.dir: is the directory that output files will be stored in.  if not given, files will go to the current working directory. 
    # response.col: column number of the model array containing a binary 0/1 response.  all other columns will be considered explanatory variables.
    # make.p.tif: T if a geotiff of the response surface is desired.
    # make.binary.tif: T if a geotiff of the response surface is desired.
    # simp.method: model simplification method.  valid methods include: "AIC" and "BIC". NOT CURRENTLY FUNCTIONAL 
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
    # #  seed=NULL                                 # sets a seed for the algorithm, any inegeger is acceptable
    #  opt.methods=2                             # sets the method used for threshold optimization used in the
    #                                            # the evaluation statistics module
    #  save.model=FALSE                          # whether the model will be used to later produce tifs
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
                 make.binary.tif=make.binary.tif,
                 site.weights=NULL,
                 save.model=save.model,
                 mars.degree=mars.degree,
                 mars.penalty=mars.penalty,
                 model.type="stepwise with pruning",
                 model.source.file=script.name,
                 model.fitting.subset=NULL, # not used.
                 model.family="binomial",
                 run.time=paste(c(format(Sys.time(),"%Y-%m-%d"),format(Sys.time(),"%H:%M:%S")),collapse="T"),
                 sig.test="chi-squared anova p-value",
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
                          train.weights=NULL,
                          test.weights=NULL,
                          train.xy=NULL,
                          test.xy=NULL,
                          factor.levels=NA,
                          used.covs=NULL,
                          ma=NULL,
                          ma.subset=NULL,
                          ma.test=NULL)),
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
      out <- check.libs(list("PresenceAbsence","rgdal","XML","sp","survival","mda","raster","tcltk2","foreign","ade4"),out)
      
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
          if(debug.mode==T){
            outfile <- paste(bname<-paste(out$dat$output.dir$dname,"/mars_",n<-1,sep=""),"_output.txt",sep="")
            while(file.access(outfile)==0) outfile<-paste(bname<-paste(out$dat$output.dir$dname,"/mars_",n<-n+1,sep=""),"_output.txt",sep="")
            capture.output(cat("temp"),file=outfile) # reserve the new basename #
            } else bname<-paste(out$dat$output.dir$dname,"/mars",sep="")
            out$dat$bname <- bname
            
    # sink console output to log file #
    if(!debug.mode) {sink(logname <- paste(bname,"_log.txt",sep=""));on.exit(sink)} else logname<-NULL
    options(warn=1)
    
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
          cat(saveXML(mars.to.xml(out),indent=T),'\n')
          return()
          }
        
    cat("\nbegin processing of model array:",out$input$ma.name,"\n")
    cat("\nfile basename set to:",out$dat$bname,"\n")
    assign("out",out,envir=.GlobalEnv)
    if(!debug.mode) {sink();cat("Progress:20%\n");flush.console();sink(logname,append=T)} else {cat("\n");cat("20%\n")}  ### print time
    ##############################################################################################################
    #  Begin model fitting #
    ##############################################################################################################

    # Fit null GLM and run stepwise, then print results #
    cat("\n","Fitting MARS model","\n")
    flush.console()

    fit <- mars.glm(data=out$dat$ma$ma, mars.x=c(2:ncol(out$dat$ma$ma)), mars.y=1, mars.degree=out$input$mars.degree, family=out$input$model.family,
          site.weights=out$dat$ma$train.weights, penalty=out$input$mars.penalty)
      
    out$mods$final.mod <- fit

  out$mods$final.mod$contributions$var<-names(out$dat$ma$ma)[-1]

    assign("out",out,envir=.GlobalEnv)
    t3 <- unclass(Sys.time())
    fit_contribs <- try(mars.contribs(fit))
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
    
     txt0 <- paste("\nMARS Model Results\n","\n","Data:\n",ma.name,"\n","\n\t n(pres)=",
        out$dat$ma$n.pres[2],"\n\t n(abs)=",out$dat$ma$n.abs[2],"\n\t n covariates considered=",length(out$dat$ma$used.covs),
        "\n",
        "\n   total time for model fitting=",round((unclass(Sys.time())-t0)/60,2),"min\n",sep="")

    capture.output(cat(txt0),file=paste(bname,"_output.txt",sep=""))
    
    cat("\n","Finished with MARS","\n")
    cat("Summary of Model:","\n")
    print(out$mods$summary <- x)
    if(!is.null(out$dat$bad.factor.cols)){
        cat("\nWarning: the following categorical response variables were removed from consideration\n",
            "because they had only one level:",paste(out$dat$bad.factor.cols,collapse=","),"\n\n")
        }
    cat("\n","Storing output...","\n","\n")
    #flush.console()
    capture.output(cat("\n\nSummary of Model:\n"),file=paste(bname,"_output.txt",sep=""),append=TRUE)
    capture.output(print(out$mods$summary),file=paste(bname,"_output.txt",sep=""),append=TRUE)
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
      auc.output <- make.auc.plot.jpg(out$dat$ma$ma,pred=mars.predict(fit,out$dat$ma$ma)$prediction[,1],
      plotname=paste(bname,"_auc_plot.jpg",sep=""),modelname="MARS",opt.methods=opt.methods,
            weight=out$dat$ma$train.weights,out=out)
      out$mods$auc.output<-auc.output

    if(!debug.mode) {sink();cat("Progress:70%\n");flush.console();sink(logname,append=T)} else cat("70%\n")
    
    # Response curves #
    
    if(is.null(responseCurveForm)){
    responseCurveForm<-0}    
    
    if(debug.mode | responseCurveForm=="pdf"){
        nvar <- nrow(out$mods$summary)
        pcol <- min(ceiling(sqrt(nvar)),4)
        prow <- min(ceiling(nvar/pcol),3)
        r.curves <- try(mars.plot(fit,plot.layout=c(prow,pcol),file.name=paste(bname,"_response_curves.pdf",sep="")))

        } else r.curves<-try(mars.plot(fit,plot.it=F))
        
        if(class(r.curves)!="try-error") {
            out$mods$r.curves <- r.curves
                } else {
            out$ec<-out$ec+1
            out$error.mssg[[out$ec]] <- paste("ERROR: problem fitting response curves",r.curves)
            }

        pred.fct<-pred.mars

     assign("out",out,envir=.GlobalEnv)

 save.image(paste(output.dir,"modelWorkspace",sep="\\"))
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
                tif.dir=out$dat$tif.dir$dname,filenames=out$dat$tif.ind,pred.fct=pred.mars,factor.levels=out$dat$ma$factor.levels,make.binary.tif=make.binary.tif,
                thresh=out$mods$auc.output$thresh,make.p.tif=make.p.tif,outfile.p=paste(out$dat$bname,"_prob_map.tif",sep=""),
                outfile.bin=paste(out$dat$bname,"_bin_map.tif",sep=""),tsize=50.0,NAval=-3000,
                fnames=out$dat$tif.names,logname=logname,out=out))     #"brt.prob.map.tif"
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

     # Evaluation Statistics on Test Data#

    if(!is.null(out$dat$ma$ma.test)) Eval.Stat<-EvaluationStats(out,thresh=auc.output$thresh,train=out$dat$ma$ma,
          train.pred=mars.predict(fit,out$dat$ma$ma)$prediction[,1],opt.methods)


    
    # Write summaries to xml #
    if(debug.mode) assign("out",out,envir=.GlobalEnv)
    doc <- mars.to.xml(out)
    
    cat(paste("\ntotal time=",round((unclass(Sys.time())-t0)/60,2),"min\n\n\n",sep=""))
    if(!debug.mode) {
        sink();on.exit();unlink(paste(bname,"_log.txt",sep=""))
        cat("Progress:100%\n");flush.console()
        #cat(saveXML(doc,indent=T),'\n')
        } else #unlink(outfile)
    capture.output(cat(saveXML(doc,indent=T)),file=paste(out$dat$bname,"_output.xml",sep=""))
    if(debug.mode) assign("fit",out$mods$final.mod,envir=.GlobalEnv)
    invisible(out)
    }
################################################################################
###########          End fit.mars.fct       ####################################

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

###########################################################################################
#  The following functions are from Elith et al. 
###########################################################################################

"calc.deviance" <-
function(obs.values, fitted.values, weights = rep(1,length(obs.values)), family=family, calc.mean = TRUE)
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
function(obs, preds, family = family)
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
      x.data.new<-as.data.frame(x.data.new)
      if(dim(x.data.new)[2]==0){
           new.model <- glm(y.data[,sp.no] ~ 1, family = family)
           }else new.model <- glm(y.data[,sp.no] ~ ., data=x.data.new, family = family)
           
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
if(nterms>1){
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
  family =family)                  # the family for the glm model
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
  if(length(mars.object$coefficients)==1) stop("MARS has fit the null model (intercept only) \n new predictors are required")
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

  if(sum(factor.filter>1)) {
  xrange[,factor.filter] <- sapply(xdat[,factor.filter], range)
  } else  xrange[,factor.filter]<-range(xdat[,factor.filter])
  
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



#set defaults
make.p.tif=T
make.binary.tif=T
mars.degree=1
mars.penalty=2
script.name="mars.r"
opt.methods=2
save.model=TRUE
MESS=FALSE

# Interpret command line argurments #
# Make Function Call #
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
    	if(argSplit[[1]][1]=="deg") mars.degree <- argSplit[[1]][2]
    	if(argSplit[[1]][1]=="pen") mars.penalty <- argSplit[[1]][2]
    	if(argSplit[[1]][1]=="om")  opt.methods <- argSplit[[1]][2]
    	if(argSplit[[1]][1]=="savm")  save.model <- argSplit[[1]][2]
    	if(argSplit[[1]][1]=="mes")  MESS <- argSplit[[1]][2]
    }
	print(csv)
	print(output)
	print(responseCol)

ScriptPath<-dirname(ScriptPath)
source(paste(ScriptPath,"LoadRequiredCode.r",sep="\\"))
print(ScriptPath)

make.p.tif<-as.logical(make.p.tif)
make.binary.tif<-as.logical(make.binary.tif)
save.model<-make.p.tif | make.binary.tif
opt.methods<-as.numeric(opt.methods)
MESS<-as.logical(MESS)

fit.mars.fct(ma.name=csv,
        tif.dir=NULL,output.dir=output,
        response.col=responseCol,make.p.tif=make.p.tif,make.binary.tif=make.binary.tif,
            mars.degree=mars.degree,mars.penalty=mars.penalty,debug.mode=F,responseCurveForm="pdf",
            script.name="mars.r",save.model=save.model,opt.methods=as.numeric(opt.methods),MESS=MESS)
