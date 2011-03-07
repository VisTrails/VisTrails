# A set of "pluggable" R functions for automated model fitting of boosted regression trees models to presence/absence data #
#
# Modified 12-2-09 to:  remove categorical covariates from consideration if they only contain one level
#                       ID factor variables based on "categorical" prefix and look for tifs in subdir
#                       Give progress reports
#                       write large output tif files in blocks to alleviate memory issues
#                       various bug fixes
#
# Modified 3-4-09 to use a list object for passing of arguements and data
#
# Modified in early 2009 to incorporate new tools and methods as described in
# Elith et al, 2008.  The new algorithm:
#  1.  Subsets the data to a maximum of 500 used and 500 available to pick settings and
#     perform model selection.
#  2.  Fits a models using a range of learning rates to find a rate which produces an optimal number of ~1000 trees.
#  3.
# Modified 12-30-08 to use directories that don't end with a forward slash
#
# Modified 8-19-08 to include the creation of a image info table.
# Modified 8-8-8 to modularize the model array input, and to include and xml output summary.
#  also added "debug.mode" to make debugging easier on my end.
# Modified on 6-30-08 to avoid writing to directories other the 'output.dir' spec'd in the
#  command line arguements.  If this arguement is not defined, output may still be written
#  to the input directories.
# Modified on 6-27-08 to take in additional arguements for a file directory (containing
#  the .tif files used for prediction) and an output directory.  Command line args are now
#  (note: ma=model array): 1. ma.name, 2. cov.list.name, 3. factor.list.name, 4. ma.dir,
#   5. tif.dir, 6. output.dir.  Also note that directories need to use forward slashes and end
#   with a forward slash.
# modified on 6-24-08 to be 'pluggable'.  The last 20 lines of code interpret command line
#   arguements and run the glm model.
# modified on 6-23-08 to handle factor variables.
# modified on 6-18-08 to remove MARS code.
# modified on 6-18-08 to include new function to return covariate names from a model.
# modified on 5/15/08 to fit both Logistic and MARS models


# Libraries required to run this program #
#   PresenceAbsence - for ROC plots
#   XML - for XML i/o
#   rgdal - for geotiff i/o
#   gbm
#   gbmplus - not on CRAN, see elith et al or contact me.
#   survival - used by gbm library
#   splines -  used by gbm library
#   lattice -  used by gbm library
#   sp - used by rdgal library

Debug=F   # set to F for command line pluggability
if(Debug==T){
    # if Debug=T, the variables set in the next few lines will control a model run when this file is sourced.  See the last
      # few lines of this script for the context in which these variables are used.

    # general settings #
      debug.mode=T  # if true, prints output and status updates to the console. Otherwise all of this goes to a log file and only the XML output is printed to console.
      simp.method="cross-validation" # use cross-validation model simplification methods of Elith '08.
      tc=NULL # tree complexity - setting to NULL allows tc to be set by the model, based on the number of observations, following Elith '08.
      n.folds=3 # number of folds used for cross-validation.

    # input:output settings #
      tif.dir <- "F:/yerc/RRSC/YELL/" # directory containing geotiff files
      make.p.tif=F # make a geotiff of probability surface?
      make.binary.tif=F  # make a binary response surface geotiff?
      output.dir <- "F:/code for Jeff and Roger/jeffs paper/filtered_rs/" # a set of ouput files will be created in this directory.
      ma.name <- "F:/code for Jeff and Roger/jeffs paper/data/07_YELL_Dalmatiantoadflax_train_clean_filt.csv" # model array to use.
      response.col <- "^response.binary"  # the name of the response column

    # this can be used to run the fitted model on a test dataset #
      test.name <- NULL  # if this is non-NULL, it will be read for use as test data.
      test.resp.col <- "response"

    # the following lines only apply if you wish to run a batch of model arrays #
    #setwd('F:/code for Jeff and Roger/jeffs paper/data')
    tif.dir <- "j:/SAHM/YELL/" # directory containing geotiff files
    ma.name <- "j:/SAHM/07_YELL_Dalmatiantoadflax_train_clean_filt_mod2.csv" # model array to use.
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
    library(tools)
    script.name="glm.r"
    out.table <- as.data.frame(matrix(NA,nrow=21,ncol=length(ma.names),dimnames=list(c("ncov.final","nrow_train","ncol_train",
              "dev_exp_train","auc_train","auc.sd_train","thresh_train","pcc_train","sens_train","spec_train","kappa_train",
              "nrow_test","ncol_test","dev_exp_test","auc_test","auc.sd_test","thresh_test","pcc_test","sens_test","spec_test",
              "kappa_test"),file_path_sans_ext(basename(ma.names)))))
    }



fit.brt.fct <- function(ma.name,tif.dir=NULL,output.dir=NULL,response.col="^response.binary",test.resp.col="response",make.p.tif=T,make.binary.tif=T,
      simp.method="cross-validation",debug.mode=F,responseCurveForm="jpg",tc=NULL,n.folds=3,ma.test=NULL,alpha=1,script.name="brt.r",
     learning.rate = NULL, bag.fraction = 0.5,
 prev.stratify = TRUE, model.family = "bernoulli",max.trees = 10000,tolerance.method = "auto",
  tolerance = 0.001){

# Possibly to add later
# offset = NULL, fold.vector = NULL, var.monotone = rep(0,length(gbm.x))

#  offset = NULL,                            # allows an offset to be specified
#  fold.vector = NULL,                       # allows a fold vector to be read in for CV with offsets,
#  tree.complexity = 1,                      # sets the complexity of individual trees
#  learning.rate = 0.01,                     # sets the weight applied to inidivudal trees
#  bag.fraction = 0.75,                      # sets the proportion of observations used in selecting variables
#  site.weights = rep(1, nrow(dat)),        # allows varying weighting for sites
#  var.monotone = rep(0, length(gbm.x)),     # restricts responses to individual predictors to monotone
#  n.folds = 10,                             # number of folds
#  prev.stratify = TRUE,                     # prevalence stratify the folds - only for p/a data
#  family = "bernoulli",                     # family - bernoulli (=binomial), poisson, laplace or gaussian
#  n.trees = 50,                             # number of initial trees to fit
#  step.size = n.trees,                      # numbers of trees to add at each cycle
#  max.trees = 10000,                        # max number of trees to fit before stopping
#  tolerance.method = "auto",                # method to use in deciding to stop - "fixed" or "auto"
#  tolerance = 0.001,                        # tolerance value to use - if method == fixed is absolute,
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
                 tc=tc,
                 learning.rate=learning.rate,
                 n.folds=n.folds,
                 bag.fraction=bag.fraction,
                 prev.stratify=prev.stratify,
                 model.family=model.family,
                 max.trees=max.trees,
                 tolerance.method=tolerance.method,
                 tolerance=tolerance,
                 simp.method=simp.method,
                 alpha=alpha,
                 model.type="boosted regression tree",
                 model.source.file=script.name,
                 model.fitting.subset=c(n.pres=500,n.abs=500),
                 run.time=paste(c(format(Sys.time(),"%Y-%m-%d"),format(Sys.time(),"%H:%M:%S")),collapse="T"),
                 sig.test="relative influence"),
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
                          factor.levels=NA,
                          used.covs=NULL,
                          ma=NULL,
                          site.weights=NULL,
                          ma.subset=NULL,
                          weight.subset=NULL),
                 ma.test=NULL),
      mods=list(parms=list(n.target.trees=1000,tc.full=tc,tc.sub=tc),
                lr.mod=NULL,
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
    # load libaries #
    out <- check.libs(list("PresenceAbsence","rgdal","XML","sp","survival","lattice","raster"),out)

    # exit program now if there are missing libraries #
      if(!is.null(out$error.mssg[[1]])){
          cat(saveXML(brt.to.xml(out),indent=T),'\n')
          return()
          }

    if(is.na(match(simp.method,c("cross-validation","rel-inf","none")))){
        out$ec <- out$ec+1
        out$error.mssg[[out$ec]] <- "ERROR: arguement simp.method must be either cross-validation, rel-inf, or none"
        cat(saveXML(brt.to.xml(out),indent=T),'\n')
        return()
        }

    #if(simplify.brt==T) out$input$simp.method<-"cross-validation" else out$input$simp.method<-">1% rel. influence"

    # check output dir #
    out$dat$output.dir <- check.dir(output.dir)
    if(out$dat$output.dir$writable==F) {out$ec<-out$ec+1
              out$error.mssg[[out$ec]] <- paste("ERROR: output directory",output.dir,"is not writable")
              out$dat$output.dir$dname <- getwd()
              }

    # generate a filename for output #
    if(debug.mode==T){
            outfile <- paste(bname<-paste(out$dat$output.dir$dname,"/brt_",n<-1,sep=""),"_output.txt",sep="")
            while(file.access(outfile)==0) outfile<-paste(bname<-paste(out$dat$output.dir$dname,"/brt_",n<-n+1,sep=""),"_output.txt",sep="")
            capture.output(cat("temp"),file=outfile) # reserve the new basename #
    } else bname <- paste(out$dat$output.dir$dname,"/brt",sep="")
    out$dat$bname <- bname

    # sink console output to log file #
    if(!debug.mode) {sink(logname <- paste(bname,"_log.txt",sep=""));on.exit(sink)} else logname<-NULL
    options(warn=-1)
    out <- check.libs(list("gbm"),out)

    # check that only one of tif.dir and tif.file is supplied #
#     if(sum(is.null(tif.file),is.null(tif.dir))!=1){
#              out$ec<-out$ec+1
#             out$error.mssg[[out$ec]] <- paste("ERROR: Exactly one of tif.dir and tif.file must be supplied at the function call")
#              if(!debug.mode) {sink();on.exit();unlink(paste(bname,"_log.txt",sep=""))}
#            cat(saveXML(brt.to.xml(out),indent=T),'\n')
#            return()
#            }
     
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
    out <- read.ma(out)

    # exit program now if there are errors in the input data #
    if(!is.null(out$error.mssg[[1]])){
          if(!debug.mode) {sink();on.exit();unlink(paste(bname,"_log.txt",sep=""))}
          cat(saveXML(brt.to.xml(out),indent=T),'\n')
          return()
          }

    cat("\nbegin processing of model array:",out$input$ma.name,"\n")
    cat("\nfile basename set to:",out$dat$bname,"\n")
    if(debug.mode) assign("out",out,envir=.GlobalEnv)
    if(!debug.mode) {sink();cat("Progress:20%\n");flush.console();sink(logname,append=T)} else {cat("\n");cat("20%\n")}  ### print time
    ##############################################################################################################
    #  Begin model fitting #
    ##############################################################################################################

    # estimate optimal learning rate and tc #
    out <-est.lr(out)
    if(debug.mode) assign("out",out,envir=.GlobalEnv)

    # exit program now if lr estimation fails #
    if(!is.null(out$error.mssg[[1]])){
          if(!debug.mode) {sink();on.exit();unlink(paste(bname,"_log.txt",sep=""))}
          cat(saveXML(brt.to.xml(out),indent=T),'\n')
          return()}

    cat("\nfinished with learning rate estimation, lr=",out$mods$lr.mod$lr0,", t=",try(round(out$mods$lr.mod$t.elapsed,2),silent=T),"sec\n")
    cat("\nfor final fit, lr=",out$mods$lr.mod$lr,"and tc=",out$mods$parms$tc.full,"\n");flush.console()
    if(!debug.mode) {sink();cat("Progress:30%\n");flush.console();sink(logname,append=T)} else {cat("\n");cat("30%\n")}

    if(out$input$simp.method=="cross-validation"){
        # remove variables with <1% relative influence and re-fit model #

        t1 <- unclass(Sys.time())
        m0 <- try(gbm.step.fast(dat=out$dat$ma$ma.subset,gbm.x=out$mods$lr.mod$good.cols,gbm.y=1,family=out$input$model.family,
              n.trees = c(300,600,800,1000,1200,1500,1800),step.size=out$input$step.size,max.trees=out$input$max.trees,
              tolerance.method=out$input$tolerance.method,tolerance=out$input$tolerance, n.folds=out$input$n.folds,tree.complexity=out$mods$parms$tc.sub,
              learning.rate=out$mods$lr.mod$lr0,bag.fraction=out$input$bag.fraction,site.weights=out$dat$ma$weight.subset,autostop=T,debug.mode=F,silent=T,
              plot.main=F,superfast=F))
        if(debug.mode) assign("m0",m0,envir=.GlobalEnv)
        if(class(m0)=="try-error"){
              if(!debug.mode) {sink();on.exit();unlink(paste(bname,"_log.txt",sep=""))}
              out$ec<-out$ec+1
              out$error.mssg[[out$ec]] <- paste("Error fitting reduced BRT model:",m0)
              cat(saveXML(brt.to.xml(out),indent=T),'\n')
              return()
              }
        t1b <- unclass(Sys.time())
        if(!debug.mode) {sink();cat("Progress:40%\n");flush.console();sink(logname,append=T)} else {cat("\n");cat("40%\n")}
        cat("\nfinished with trimmed model fitting, n.trees=",m0$target.trees,", t=",round(t1b-t1,2),"sec\n");flush.console()
        cat("\nbeginning model simplification - very slow...\n");flush.console()
        out$mods$simp.mod <- try(gbm.simplify(m0,n.folds=out$input$n.folds,plot=F,verbose=F,alpha=out$input$alpha),silent=T) # this step is very slow #
        if(debug.mode) assign("out",out,envir=.GlobalEnv)
        if(class(out$mods$simp.mod)=="try-error"){
            if(!debug.mode) {sink();on.exit();unlink(paste(bname,"_log.txt",sep=""))}
            out$error.mssg[[out$ec<-out$ec+1]] <- paste("Error simplifying BRT model:",out$mods$simp.mod)
            cat(saveXML(brt.to.xml(out),indent=T),'\n')
            return()
            }
        out$mods$simp.mod$good.cols <- out$mods$simp.mod$pred.list[[length(out$mods$simp.mod$pred.list)]]
        out$mods$simp.mod$good.vars <- names(out$dat$ma$ma)[out$mods$simp.mod$good.cols]
        cat("\nfinished with model simplification, t=",round((unclass(Sys.time())-t1b)/60,2),"min\n");flush.console()
        if(!debug.mode) {sink();cat("Progress:50%\n");flush.console();sink(logname,append=T)} else {cat("\n");cat("50%\n")}
        }

    # fit final model #
    t2 <- unclass(Sys.time())

  out$mods$final.mod <- try(gbm.step.fast(dat=out$dat$ma$ma,gbm.x=out$mods$simp.mod$good.cols,gbm.y = 1,family=out$input$model.family,
                  n.trees = c(300,600,700,800,900,1000,1200,1500,1800,2200,2600,3000,3500,4000,4500,5000),n.folds=out$input$n.folds,
                  tree.complexity=out$mods$parms$tc.full,learning.rate=out$mods$lr.mod$lr,bag.fraction=out$input$bag.fraction,site.weights=out$dat$ma$site.weights,
                  autostop=T,debug.mode=F,silent=T,plot.main=F,superfast=F))



    if(debug.mode) assign("out",out,envir=.GlobalEnv)
    if(class(out$mods$final.mod)=="try-error"){
          if(!debug.mode) {sink();on.exit();unlink(paste(bname,"_log.txt",sep=""))}
          out$ec<-out$ec+1
          out$error.mssg[[out$ec]]<- paste("Error fitting final BRT model:",out$mods$final.mod)
          cat(saveXML(brt.to.xml(out),indent=T),'\n')
          return()
          }
    t3 <- unclass(Sys.time())
    cat("\nfinished with final model fitting, n.trees=",out$mods$final.mod$target.trees,", t=",round(t3-t2,2),"sec\n\n\n");flush.console()
    if(!debug.mode) {sink();cat("Progress:60%\n");flush.console();sink(logname,append=T)} else {cat("\n");cat("60%\n")}

    ##############################################################################################################
    #  Begin model output #
    ##############################################################################################################

    # Store .jpg ROC plot #
    auc.output <- try(make.auc.plot.jpg(out$dat$ma$ma,pred=predict.gbm(out$mods$final.mod,out$dat$ma$ma,
            out$mods$final.mod$target.trees,type="response"),plotname=paste(bname,"_auc_plot.jpg",sep=""),modelname="BRT"),
            silent=T)

    if(class(auc.output)=="try-error"){
          out$ec<-out$ec+1
          out$error.mssg[[out$ec]] <- paste("Error making ROC plot:",auc.output)
    } else { out$mods$auc.output<-auc.output}

    # Generate and store text summary #
    #source('F:/code for Jeff and Roger/boosted regression trees/brt.functions.aks.021709.r')
    y <- try(gbm.interactions(out$mods$final.mod),silent=T)
    if(debug.mode) assign("out",out,envir=.GlobalEnv)
    if(class(y)!="try-error"){
        int <- y$rank.list;
        int<-int[int$p<.05,]
        int <- int[order(int$p),]
        int$p <- round(int$p,4)
        names(int) <- c("v1","name1","v2","name2","int.size","p-value")
        row.names(int)<-NULL
        if(nrow(int)>0) out$mods$interactions <- int else out$mods$interactions <- NULL
        } else {
        out$ec <-out$ec+1
        out$error.mssg[[out$ec]] <- paste("ERROR: problem assessing interactions:",y)
        }

    model.summary <- try(summary(out$mods$final.mod,plotit=F),silent=T)
    if(class(model.summary)=="try-error"){
        if(!debug.mode) {sink();on.exit();unlink(paste(bname,"_log.txt",sep=""))}
        out$ec<-out$ec+1
        out$error.mssg[[out$ec]] <- paste("ERROR: can't generate summary of final model:",model.summary)
        cat(saveXML(brt.to.xml(out),indent=T),'\n')
        return()
    } else {
        out$mods$summary <- model.summary
        }
    if(debug.mode) assign("out",out,envir=.GlobalEnv)
    txt0 <- paste("Boosted Regression Tree Modeling Results\n",out$input$run.time,"\n\n","Data:\n",ma.name,"\n","n(pres)=",
        out$dat$ma$n.pres[2],", n(abs)=",out$dat$ma$n.abs[2],", n covariates considered=",length(out$dat$ma$used.covs),
        "\n\n","Settings:\n","tree complexity=",out$mods$parms$tc.full,", learning rate=",round(out$mods$lr.mod$lr,4),
        ", n(trees)=",out$mods$final.mod$target.trees,",\n","model simplification=",out$input$simp.method,", n folds=",out$input$n.folds,
        "\n\n","Results:\n","AUC=",round(out$mods$auc.output$auc,4),", n covariates in final model=",nrow(out$mods$final.mod$contributions),
        ", pct deviance explained=",round(out$mods$auc.output$pct_dev_exp,1),"%\n",
        "total time for model fitting=",round((unclass(Sys.time())-t0)/60,2),"min\n",sep="")
    txt1 <- "\nRelative influence of predictors in final model:\n\n"
    txt2 <- "\nImportant interactions in final model:\n\n"
    capture.output(cat(txt0),cat(txt1),print(out$mods$final.mod$contributions),cat(txt2),print(out$mods$interactions,row.names=F),file=paste(bname,"_output.txt",sep=""))
    cat(txt0);cat(txt1);print(out$mods$final.mod$contributions);cat(txt2);print(out$mods$interactions,row.names=F)
    if(!is.null(out$dat$bad.factor.cols)){
        capture.output(cat("\nWarning: the following categorical response variables were removed from consideration\n",
            "because they had only one level:",paste(out$dat$bad.factor.cols,collapse=","),"\n"),
            file=paste(bname,"_output.txt",sep=""),append=T)
        cat("\nWarning: the following categorical response variables were removed from consideration\n",
            "because they had only one level:",paste(out$dat$bad.factor.cols,collapse=","),"\n\n")
        }



    if(!debug.mode) {sink();cat("Progress:70%\n");flush.console();sink(logname,append=T)} else {cat("\n");cat("70%\n")}

    # Response curves #
    if(is.null(responseCurveForm)){
    responseCurveForm<-0}

    if(debug.mode | responseCurveForm=="pdf"){
        nvar <- nrow(out$mods$final.mod$contributions)
        pcol <- min(ceiling(sqrt(nvar)),4)
        prow <- min(ceiling(nvar/pcol),3)

        pdf(paste(bname,"_response_curves.pdf",sep=""),width=11,height=8.5,onefile=T)
            par(oma=c(2,2,4,2))
            r.curves <- try(gbm.plot(out$mods$final.mod,plotit=T,plot.layout=c(prow,pcol)),silent=T)
            if(class(r.curves)!="try-error") {out$mods$r.curves <- r.curves
            mtext(paste("BRT response curves for",basename(ma.name)),outer=T,side=3,cex=1.3)}
            par(mfrow=c(1,1))
            #for(i in 1:min(nrow(int),2)) gbm.perspec(fit,int$var1.index[i],int$var2.index[i])
            if(!is.null(out$mods$interactions)){
                for(i in 1:nrow(out$mods$interactions)) {gbm.perspec(out$mods$final.mod,out$mods$interactions$v1[i],out$mods$interactions$v2[i])
                mtext(paste("BRT interaction plots for",basename(ma.name)),outer=T,side=3,cex=1.5) }
                }
        graphics.off()
        } else {
            r.curves <- try(gbm.plot(out$mods$final.mod,plotit=F),silent=T)
            if(class(r.curves)!="try-error") {out$mods$r.curves <- r.curves
              } else {
              out$ec<-out$ec+1
              out$error.mssg[[out$ec]] <- paste("ERROR: problem fitting response curves",r.curves)
              }
        }
    t4 <- unclass(Sys.time())
    cat("\nfinished with final model summarization, t=",round(t4-t3,2),"sec\n");flush.console()
    if(!debug.mode) {sink();cat("Progress:80%\n");flush.console();sink(logname,append=T)} else {cat("\n");cat("80%\n")}

    # Make .tif of predictions #
    if(out$input$make.p.tif==T | out$input$make.binary.tif==T){
        cat("\nproducing prediction maps...","\n","\n");flush.console()
        mssg <- proc.tiff(model=out$mods$final.mod,vnames=as.character(out$mods$final.mod$contributions$var),
            tif.dir=out$dat$tif.dir$dname,filenames=out$dat$tif.ind,pred.fct=brt.predict,factor.levels=out$dat$ma$factor.levels,make.binary.tif=make.binary.tif,
            thresh=out$mods$auc.output$thresh,make.p.tif=make.p.tif,outfile.p=paste(out$dat$bname,"_prob_map.tif",sep=""),
            outfile.bin=paste(out$dat$bname,"_bin_map.tif",sep=""),tsize=50.0,NAval=-3000,logname=logname)     #"brt.prob.map.tif"

        if(class(mssg)=="try-error" | mssg!=0){
          if(!debug.mode) {sink();on.exit();unlink(paste(bname,"_log.txt",sep=""))}
          out$ec<-out$ec+1
          out$error.mssg[[out$ec]] <- paste("Error producing prediction maps:",mssg)
          cat(saveXML(brt.to.xml(out),indent=T),'\n')
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
    if(debug.mode) assign("out",out,envir=.GlobalEnv)
    doc <- brt.to.xml(out)

    cat(paste("\ntotal time=",round((unclass(Sys.time())-t0)/60,2),"min\n\n\n",sep=""))
    if(!debug.mode) {
        sink();on.exit();unlink(paste(bname,"_log.txt",sep=""))
        cat("Progress:100%\n");flush.console() ### print time

        cat(saveXML(doc,indent=T),'\n')
        }
    capture.output(cat(saveXML(doc,indent=T)),file=paste(out$dat$bname,"_output.xml",sep=""))
    if(debug.mode) assign("fit",out$mods$final.mod,envir=.GlobalEnv)
    invisible(out)
}

brt.predict <- function(model,x) {
    # retrieve key items from the global environment #
    # make predictions from complete data only #
    #y <- rep(NA,nrow(x))
    #y[complete.cases(x)] <- predict.gbm(model, x[complete.cases(x),],model$target.trees,type="response")

    # make predictions from full data #
    y <- predict.gbm(model,x,model$target.trees,type="response")
    # encode missing values as -1.
    a<-apply(x,1,sum)
    y[is.na(a)]<- NaN

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

brt.to.xml <- function(out){
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
        kids <- lapply(paste(out$dat$tif.dir$dname,"/",out$dat$ma$used.covs,".tif",sep=""),function(x) newXMLNode("layer", x))
        addChildren(lc, kids)
    mo <- newXMLNode("modelOutput",parent=sm)
        newXMLNode("modelType",out$input$model.type,parent=mo)
        newXMLNode("modelSourceFile",out$input$model.source.file,parent=mo)
        newXMLNode("devianceExplained",out$mods$auc.output$pct_dev_exp,parent=mo,attrs=list(type="percentage"))
        if(!is.null(out$mods$summary)){
              newXMLNode("nativeOutput",paste(out$dat$bname,"_output.txt",sep=""),parent=mo)
              } else {
              newXMLNode("nativeOutput",NULL,parent=mo)
              }
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
            newXMLNode("treeComplexity",out$input$tc,parent=mfp)
            newXMLNode("bagFraction",out$input$bag.fraction,parent=mfp)
            newXMLNode("simpMethod",out$input$simp.method,parent=mfp)
            newXMLNode("alpha",out$input$alpha,parent=mfp)

        sv <- newXMLNode("significantVariables",parent=mo)
        if(!is.null(out$mods$summary)) {
            t.table <- data.frame(significanceMeasurement=out$mods$summary$rel.inf,row.names=out$mods$summary$var)
            if(!is.null(out$mods$interactions)){
                int1 <- int2 <- out$mods$interactions
                int2$name1 <- int1$name2
                int2$name2 <- int1$name1
                int <- rbind(int1,int2)
                }

            for(i in 1:nrow(t.table)){
                x <- newXMLNode("sigVar",parent=sv)
                newXMLNode(name="name", row.names(t.table)[i],parent=x)
                kids <- lapply(1:ncol(t.table),function(j) newXMLNode(name=names(t.table)[j], t.table[i,j]))
                addChildren(x, kids)
                if(!is.null(out$mods$interactions)){
                    ints <-  c(1:nrow(int))[int$name1 %in% row.names(t.table)[i]]
                    if(length(ints)>0){
                        kids <- lapply(ints,function(j) newXMLNode(name="sigInteraction",attrs=list(name=as.character(int$name2)[j],size=int$int.size[j],p=int$"p-value"[j])))
                        addChildren(x,kids)
                        }

                    }
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



est.lr <- function(out){
    # this function estimates optimal number of trees at a variety of learning rates #
    # the learning rate that produces closest to 1000 trees is selected #
    # in addition, variables with >1% influence are identified by column number in
    # the original dataframe
    # written by AKS early 2009
    suppressMessages(require(gbm))


    t0 <- unclass(Sys.time())

    # set tree complexity for full-data run #
    a<-2.69; b<-0.0012174
    if(is.null(out$mods$parms$tc.full)) out$mods$parms$tc.full<-min(round(a+b*out$dat$ma$dims[1]),15) # this gives 3 for n=250
    if(is.null(out$mods$parms$tc.sub)){
        n <- out$dat$ma$n.abs[3]+out$dat$ma$n.pres[3]  # this gives 3 for n=250
       if(is.na(n)) (n=length(out$input$site.weights))
        out$mods$parms$tc.sub <- round(a+b*n)
    }

    cat("\n");cat("tree complexity set to",out$mods$parms$tc.sub,"\n")

    n.trees <- c(100,200,400,800,900,1000,1100,1200,1500,1800,2400)
    lrs <- c(.1,.06,.05,.04,.03,.02,.01,.005,.0025,.001)
    lr.out <- data.frame(lrs=lrs,max.trees=0)
    dat <- out$dat$ma$ma.subset
    gbm.y <- 1
    gbm.x <- 2:ncol(dat)

    max.trees <- 0
    i=1

    while(max.trees<800 & i<=nrow(lr.out)){

       tryCatch(gbm.fit <- gbm.step.fast(dat=dat,
          gbm.x = gbm.x,
          gbm.y = gbm.y,
          family = out$input$model.family,
          n.trees = n.trees,
          n.folds=out$input$n.folds,
          tree.complexity = out$mods$parms$tc.sub,
          learning.rate = lrs[i],
          bag.fraction = out$input$bag.fraction,
          site.weights=out$dat$ma$weight.subset,
          autostop=T,verbose=F,silent=T,plot.main=F),error=function(ex){cat("Error: learning rate estimation failed.\n");
          print(ex);
          stop();})
          
       if(class(gbm.fit)=="try-error"){
            out$ec <- out$ec+1
            out$error.mssg[[out$ec]] <- paste("ERROR: learning rate estimation failed:",gbm.fit)
            return(out)
            }
       lr.out$max.trees[i] <- max.trees <- gbm.fit$target.trees
       assign(paste("gbm.fit",i,sep="_"),gbm.fit)
       cat("lr =",lrs[i],"  optimal n trees =",max.trees,"\n");flush.console()
       i<-i+1 #ifelse(max.trees<=200,i+2,i+1)
       }
    # pick lr that gives closest to 1000 trees #
    lr.out$i <- 1:nrow(lr.out)
    lr.out <- lr.out[lr.out$max.trees!=0,]
    ab<-coef(lm(max.trees~log(lrs),data=lr.out))
    tt <- out$dat$ma$ratio*800
    lr.full <- round(as.numeric(exp((tt-ab[1])/ab[2])),4)
    lr <- round(as.numeric(exp((1000-ab[1])/ab[2])),4)
    lr.out$abs <- abs(lr.out$max.trees-1000)
    lr.out$d.lr <- abs(lr.out$lrs-lr)
    lr.out <- lr.out[order(lr.out$abs,lr.out$d.lr),]
    lr0 <- lr.out$lrs[1]
    i <- lr.out$i[1]
    gbm.fit <- get(paste("gbm.fit",i,sep="_"))
    gbm.fit$gbm.call$dataframe <- as.character(substitute(dat))
    good.vars <- summary(gbm.fit,plotit=F)
    good.vars <- good.vars$var[good.vars$rel.inf>ifelse(out$input$simp.method!="none",1,0)]
    good.cols <- c(1:ncol(dat))[names(dat)  %in%  good.vars]
    out$mods$simp.mod <- list(good.cols=good.cols,good.vars=good.vars)
    out$mods$lr.mod <- list(tc=out$mods$parms$tc.sub,lr=lr.full,lr0=lr0,lr.out=lr.out,ab=ab,gbm.fit=gbm.fit,good.cols=good.cols,t.elapsed=c(unclass(Sys.time())-t0))
    if(!is.null(out$input$learning.rate)) out$mods$lr.mod$lr0=out$input$learning.rate

    return(out)
    }

 read.ma <- function(out,test.dat=F){

      if(test.dat==F){
          ma.name <- out$input$ma.name
          } else ma.name <- out$input$ma.test
      tif.dir <- out$dat$tif.dir$dname
      out.list <- out$dat$ma
      out.list$status[1] <- file.access(ma.name,mode=0)==0
      if(!is.null(out$input$tif.dir)){
          ma <- try(read.csv(ma.name, header=TRUE),silent=T)}

      if(is.null(out$input$tif.dir)){
          try(ma<-read.csv(ma.name,skip=3),silent=T)
          hl<-readLines(ma.name,1)
          hl=strsplit(hl,',')
          colnames(ma) = hl[[1]]
          
          tif.info<-readLines(ma.name,3)
          tif.info<-strsplit(tif.info,',')
          include<-(as.numeric(tif.info[[2]]))
          paths<-as.character(tif.info[[3]])
          #paths<-paths[!is.na(include)]
          #include[is.na(include)]<-0

            }
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
      if(length(xy.cols)>0){ ma <- ma[,-xy.cols]
          if(is.null(out$input$tif.dir)){
           include<-include[-xy.cols]
           paths<-paths[-xy.cols]
      }}
       # remove weights column
       site.weights<-match("site.weights",tolower(names(ma)))
       ifelse(!is.na(site.weights),{
          out$input$site.weights<-ma[,site.weights]
          ma <- ma[,-site.weights]
           if(is.null(out$input$tif.dir)){
           include<-include[-site.weights]
           paths<-paths[-site.weights]
            }
          },
          out$input$site.weights<-rep(1,times=dim(ma)[1]))

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
      # check that response column contains only 1's and 0's, but not all 1's or all 0's if GLMFamily==binomial

      if(tolower(out$input$model.family)=="bernoulli"){
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
          }
     #check that response column contains at least two unique values for counts

      if(tolower(out$input$model.family)=="poisson"){
      if(length(table(unique(ma[,r.col])))==1){
          out$ec <- out$ec+1
          out$error.mssg[[out$ec]] <- paste("ERROR: response column (#",r.col,") in ",ma.name," does not have at least two unique values",sep="")
          return(out)
          }
          out$dat$ma$resp.name <- names(ma)[r.col]<-"response"
          out.list$n.pres[1] <- sum(ma[,r.col])
          out.list$n.abs[1] <- nrow(ma)-sum(ma[,r.col])
          out.list$resp.name <- names(ma)[r.col]
          ma.names <- names(ma)
          }

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
                  x <- table(ma[,f.col])
                  if(nrow(x)<2){
                        out$dat$bad.factor.cols <- c(out$dat$bad.factor.cols,factor.names[i])
                        }
                  lc.levs <-  as.numeric(row.names(x))[x>0] # make sure there is at least one "available" observation at each level
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
               # test that geotiffs match ma.columns
          if(is.null(out$input$tif.dir)){
              ma.cols <- match(ma.names[-r.col],sub(".tif","",basename(paths[-r.col])))
                if(any(is.na(ma.cols))){
                  out$ec <- out$ec+1
                  out$error.mssg[[out$ec]] <- paste("ERROR: the following geotiff(s) are missing in ",
                        tif.dir,":  ",paste(ma.names[-r.col][is.na(ma.cols)],collapse=" ,"),sep="")
                  return(out)
                }
                 #remove columns that shouldn't be used from tiff based on the indicator
                include<-include[-r.col]
                paths<-paths[-r.col]
                paths<-paths[include==1]
                 #creates a list of predictors from tif.ind and response column
               ma.use <- c(r.col,match(sub(".tif","",basename(paths)),ma.names))
                ma<-ma[,ma.use]
                ma.names<-names(ma)
                #Now check that tiffs to be used exist
              #out$dat$tif.names <- tif.names[ma.cols]

              if(sum(file.access(paths),mode=0)!=0){
                  out$ec <- out$ec+1
                  out$error.mssg[[out$ec]] <- paste("ERROR: the following geotiff(s) are missing : ",
                        paths[(file.access(paths)!=0),][1],sep="")
                return(out)
                }
                out$dat$tif.ind<-paths
                }
          if(!is.null(out$input$tif.dir)){
              tif.names <- out$dat$tif.names
              ma.cols <- match(ma.names[-r.col],sub(".tif","",basename(tif.names)))
              if(any(is.na(ma.cols))){
                  out$ec <- out$ec+1
                  out$error.mssg[[out$ec]] <- paste("ERROR: the following geotiff(s) are missing in ",
                        tif.dir,":  ",paste(ma.names[-r.col][is.na(ma.cols)],collapse=" ,"),sep="")
                return(out)
                }
            out$dat$tif.names <- tif.names[ma.cols]
            }} else out$dat$tif.names <- ma.names[-1]

      out.list$ma <- ma[complete.cases(ma),c(r.col,c(1:ncol(ma))[-r.col])]
      out.list$site.weights <- out$input$site.weights[complete.cases(ma)]
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
            out.list$weight.subset<-out.list$site.weights[c(pres.sample,abs.sample)]
            out.list$n.pres[3] <- length(pres.sample)
            out.list$n.abs[3] <- length(abs.sample)
            } else {
            out.list$ma.subset <- NULL
            out.list$weight.subset<-NULL
            out.list$n.pres[3] <- NA
            out.list$n.abs[3] <- NA }

if(tolower(out$input$model.family)=="poisson"){
out.list$ma.subset<-out.list$ma
}

      if(test.dat==F){
          out$dat$ma <- out.list
          } else out$dat$ma.test <- out.list
      return(out)
      }

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

proc.tiff <- function(model,vnames,tif.dir=NULL,filenames=NULL,pred.fct,factor.levels=NA,make.binary.tif=F,make.p.tif=T,binary.thresh=NA,
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
   if(!is.null(tif.dir)){
      fnames <- fnames[match(vnames,basename(sub(".tif","",fnames)))]
      fullnames <- paste(tif.dir,fnames,sep="/")
      goodfiles <- file.access(fullnames)==0
      if(!all(goodfiles)){
          cat('\n',paste("ERROR: the following image files are missing:",paste(fullnames[!goodfiles],collapse=", ")),'\n','\n')
         flush.console()
          return(paste("ERROR: the following image files are missing:",paste(fullnames[!goodfiles],collapse=", ")))
          }}
# settup up output raster to match input raster
       if(!is.null(filenames)){
          fullnames <- as.character(filenames[match(vnames,basename(sub(".tif","",filenames)))])
          goodfiles <- file.access(fullnames)==0
        if(!all(goodfiles)){
          cat('\n',paste("ERROR: the following image files are missing:",paste(fullnames[!goodfiles],collapse=", ")),'\n','\n')
         flush.console()
          return(paste("ERROR: the following image files are missing:",paste(fullnames[!goodfiles],collapse=", ")))
          }}
  
  
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
        if (i==tr$n) temp <- temp[1:(tr$nrows[i]*dims[2]),] # for the last tile...
      for(k in 1:nvars) { # fill temp data frame
            temp[,k]<- getValuesBlock(raster(fullnames[k]), row=tr$row[i], nrows=tr$size)
            }
    temp[temp==NAval] <- NA # replace missing values #
    temp[is.na(temp)]<-NA #this seemingly worthless line switches NaNs to NA so they aren't predicted
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
print(i)
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

gbm.step.fast <- function(
  dat,                             # the input dataframe
  gbm.x,                                    # the predictors
  gbm.y,                                    # and response
  offset = NULL,                            # allows an offset to be specified
  fold.vector = NULL,                       # allows a fold vector to be read in for CV with offsets,
  tree.complexity = 1,                      # sets the complexity of individual trees
  learning.rate = 0.01,                     # sets the weight applied to inidivudal trees
  bag.fraction = 0.75,                      # sets the proportion of observations used in selecting variables
  site.weights = rep(1, nrow(dat)),        # allows varying weighting for sites
  var.monotone = rep(0, length(gbm.x)),     # restricts responses to individual predictors to monotone
  n.folds = 10,                             # number of folds
  prev.stratify = TRUE,                     # prevalence stratify the folds - only for p/a data
  family = "bernoulli",                     # family - bernoulli (=binomial), poisson, laplace or gaussian
  n.trees = 50,                             # number of initial trees to fit
  step.size = n.trees,                      # numbers of trees to add at each cycle
  max.trees = 10000,                        # max number of trees to fit before stopping
  tolerance.method = "auto",                # method to use in deciding to stop - "fixed" or "auto"
  tolerance = 0.001,                        # tolerance value to use - if method == fixed is absolute,
                                            # if auto is multiplier * total mean deviance
  keep.data = FALSE,                        # keep raw data in final model
  plot.main = TRUE,                         # plot hold-out deviance curve
  plot.folds = FALSE,                       # plot the individual folds as well
  verbose = TRUE,                           # control amount of screen reporting
  silent = FALSE,                           # to allow running with no output for simplifying model)
  keep.fold.models = FALSE,                 # keep the fold models from cross valiation
  keep.fold.vector = FALSE,                 # allows the vector defining fold membership to be kept
  keep.fold.fit = FALSE,                    # allows the predicted values for observations from CV to be kept
  autostop = FALSE,                       # setting autostop to T causes the tree fitting while loop to terminate
                                            #   if the cv.loss value increases twice in a row (AKS).

  superfast=FALSE,                          # controls whether or not to compute final model when optimal n.trees differs from 1000 (AKS)
  ...)                                      # allows for any additional plotting parameters
{
#
# j. leathwick/j. elith - 19th September 2005
#
# version 2.9
#
# function to assess optimal no of boosting trees using k-fold cross validation
#
# implements the cross-validation procedure described on page 215 of
# Hastie T, Tibshirani R, Friedman JH (2001) The Elements of Statistical Learning:
# Data Mining, Inference, and Prediction Springer-Verlag, New York.
#
# divides the data into 10 subsets, with stratification by prevalence if required for pa data
# then fits a gbm model of increasing complexity along the sequence from n.trees to n.trees + (n.steps * step.size)
# calculating the residual deviance at each step along the way
# after each fold processed, calculates the average holdout residual deviance and its standard error
# then identifies the optimal number of trees as that at which the holdout deviance is minimised
# and fits a model with this number of trees, returning it as a gbm model along with additional information
# from the cv selection process
#
# updated 13/6/05 to accommodate weighting of sites
#
# updated 19/8/05 to increment all folds simultaneously, allowing the stopping rule
# for the maxinum number of trees to be fitted to be imposed by the data,
# rather than being fixed in advance
#
# updated 29/8/05 to return cv test statistics, and deviance as mean
# time for analysis also returned via unclass(Sys.time())
#
# updated 5/9/05 to use external function calc.deviance
# and to return cv test stats via predictions formed from fold models
# with n.trees = target.trees
#
# updated 15/5/06 to calculate variance of fitted and predicted values across folds
# these can be expected to approximate the variance of fitted values
# as would be estimated for example by bootstrapping
# as these will underestimate the true variance
# they are corrected by multiplying by (n-1)2/n
# where n is the number of folds
#
# updated 25/3/07 tp allow varying of bag fraction
#
# requires gbm library from Cran
# requires roc and calibration scripts of J Elith
# requires calc.deviance script of J Elith/J Leathwick
#
# updated 1/2/09 by aks:
# now takes a vector arguement for n.trees:  if n.trees is given as a (should be montonically
#   increasing) vector, then models with those # of trees are fit.  if n.trees is a single number,
#   then the program works as default
# there is also a provision for stopping the fitting of successive models IF the cv.loss.value increases
#   over two successive steps.

  require(gbm)

  if (silent) verbose <- FALSE

# initiate timing call

  z1 <- unclass(Sys.time())

# setup input data and assign to position one

  dataframe.name <- deparse(substitute(dat))   # get the dataframe name

  dat <- eval(dat)
  x.data <- eval(dat[, gbm.x])                 #form the temporary datasets
  names(x.data) <- names(dat)[gbm.x]
  y.data <- eval(dat[, gbm.y])
  sp.name <- names(dat)[gbm.y]
  if (family == "bernoulli") prevalence <- mean(y.data)

  assign("x.data", x.data, env = globalenv())               #and assign them for later use
  assign("y.data", y.data, env = globalenv())

  offset.name <- deparse(substitute(offset))   # get the dataframe name
  offset = eval(offset)
  #print(summary(offset))

  n.cases <- nrow(dat)
  n.preds <- length(gbm.x)

  if (!silent) {
    cat("\n","\n");cat("GBM STEP - version 2.9","\n","\n") #AKS
    cat("Performing cross-validation optimization of a boosted regression tree model \n")#AKS
    cat("for",sp.name,"with dataframe",dataframe.name,"and using a family of",family,"\n\n")
    cat("Using",n.cases,"observations and",n.preds,"predictors \n\n")
    flush.console() #AKS
  }

# set up the selector variable either with or without prevalence stratification

  if (is.null(fold.vector)) {

    if (prev.stratify & family == "bernoulli") {
      presence.mask <- dat[,gbm.y] == 1
      absence.mask <- dat[,gbm.y] == 0
      n.pres <- sum(presence.mask)
      n.abs <- sum(absence.mask)

# create a vector of randomised numbers and feed into presences
      selector <- rep(0,n.cases)
      temp <- rep(seq(1, n.folds, by = 1), length = n.pres)
      temp <- temp[order(runif(n.pres, 1, 100))]
      selector[presence.mask] <- temp

# and then do the same for absences
      temp <- rep(seq(1, n.folds, by = 1), length = n.abs)
      temp <- temp[order(runif(n.abs, 1, 100))]
      selector[absence.mask] <- temp
      }

    else {  #otherwise make them random with respect to presence/absence
      selector <- rep(seq(1, n.folds, by = 1), length = n.cases)
      selector <- selector[order(runif(n.cases, 1, 100))]
      }
    }
  else {
    if (length(fold.vector) != n.cases) stop("supplied fold vector is of wrong length")
    cat("loading user-supplied fold vector \n\n")
    selector <- eval(fold.vector)
    }

# set up the storage space for results

  pred.values <- rep(0, n.cases)

  cv.loss.matrix <- matrix(0, nrow = n.folds, ncol = 1)
  training.loss.matrix <- matrix(0, nrow = n.folds, ncol = 1)
  trees.fitted <- n.trees[1]

  model.list <- list(paste("model",c(1:n.folds),sep=""))     # dummy list for the tree models

# set up the initial call to gbm

  if (is.null(offset)) {  #AKS (n.trees arg)
    gbm.call <- paste("gbm(y.subset~.,data=x.subset,n.trees=n.trees[1],interaction.depth=tree.complexity,shrinkage=learning.rate,bag.fraction=bag.fraction,weights=weight.subset,distribution=as.character(family),var.monotone=var.monotone,verbose=FALSE)",sep="")
    }
  else {       #AKS (n.trees arg)
    gbm.call <- paste("gbm(y.subset~.+offset(offset.subset),data=x.subset,n.trees=n.trees[1],interaction.depth=tree.complexity,shrinkage=learning.rate,bag.fraction=bag.fraction,weights=weight.subset,distribution=as.character(family),var.monotone=var.monotone,verbose=FALSE)",sep="")
    }


  n.fitted <- n.trees[1] # AKS

# calculate the total deviance

  y_i <- y.data

  u_i <- sum(y.data * site.weights) / sum(site.weights)
  u_i <- rep(u_i,length(y_i))

  total.deviance <- calc.deviance(y_i, u_i, weights = site.weights, family = family, calc.mean = FALSE)

  mean.total.deviance <- total.deviance/n.cases

  tolerance.test <- tolerance

  if (tolerance.method == "auto") {
     tolerance.test <- mean.total.deviance * tolerance
  }

# now step through the folds setting up the initial call

  if (!silent){

    cat("creating",n.folds,"initial models of",n.trees,"trees","\n")

    if (prev.stratify & family == "bernoulli") {cat("\n");cat("folds are stratified by prevalence","\n","\n")#AKS
      } else {cat("\n","folds are unstratified","\n","\n")}

    cat ("total mean deviance = ",round(mean.total.deviance,4),"\n","\n")

    cat("tolerance is fixed at ",round(tolerance.test,4),"\n","\n")
    flush.console()#AKS

    if (tolerance.method != "fixed" & tolerance.method != "auto") {
      cat("invalid argument for tolerance method - should be auto or fixed","\n")
      return()}
  }

  if (verbose) cat("fitting initial model...","\n");flush.console()#AKS

  for (i in 1:n.folds) {

    model.mask <- selector != i  #used to fit model on majority of data
    pred.mask <- selector == i   #used to identify the with-held subset

    y.subset <- y.data[model.mask]
    x.subset <- x.data[model.mask,]
    weight.subset <- site.weights[model.mask]

    if (!is.null(offset)) {
      offset.subset <- offset[model.mask]
    }
    else {
      offset.subset <- NULL
    }

    model.list[[i]] <- eval(parse(text = gbm.call))

    fitted.values <- model.list[[i]]$fit  #predict.gbm(model.list[[i]], x.subset, type = "response", n.trees = n.trees)
    if (!is.null(offset)) fitted.values <- fitted.values + offset[model.mask]
    if (family == "bernoulli") fitted.values <- exp(fitted.values)/(1 + exp(fitted.values))
    if (family == "poisson") fitted.values <- exp(fitted.values)

    pred.values[pred.mask] <- predict.gbm(model.list[[i]], x.data[pred.mask, ], n.trees = n.trees[1])
    if (!is.null(offset)) pred.values[pred.mask] <- pred.values[pred.mask] + offset[pred.mask]
    if (family == "bernoulli") pred.values[pred.mask] <- exp(pred.values[pred.mask])/(1 + exp(pred.values[pred.mask]))
    if (family == "poisson") pred.values[pred.mask] <- exp(pred.values[pred.mask])

# calc training deviance

    y_i <- y.subset
    u_i <- fitted.values
    weight.fitted <- site.weights[model.mask]
    training.loss.matrix[i,1] <- calc.deviance(y_i, u_i, weight.fitted, family = family)

# calc holdout deviance

    y_i <- y.data[pred.mask]
    u_i <- pred.values[pred.mask]
    weight.preds <- site.weights[pred.mask]
    cv.loss.matrix[i,1] <- calc.deviance(y_i, u_i, weight.preds, family = family)

  } # end of first loop

# now process until the change in mean deviance is =< tolerance or max.trees is exceeded

  delta.deviance <- 1

  cv.loss.values <- apply(cv.loss.matrix,2,mean)
  if (verbose) cat("ntrees resid. dev.","\n")#AKS
  if (verbose) cat(n.fitted,"  ",round(cv.loss.values,4),"\n","\n")

  if (!silent) cat("")
  if (!silent) cat("now adding trees...","\n");flush.console()#AKS

  j <- 1
  k <- 2 #AKS
  stop.loop <- F #AKS
  if(length(n.trees>1)) max.trees <- n.trees[length(n.trees)] #AKS

  while (delta.deviance > tolerance.test & n.fitted < max.trees & stop.loop==F) {  # beginning of inner loop

        # add a new column to the results matrice..

        training.loss.matrix <- cbind(training.loss.matrix,rep(0,n.folds))
        cv.loss.matrix <- cbind(cv.loss.matrix,rep(0,n.folds))

        if(length(n.trees>1)){ #AKS
          n.fitted <- n.trees[k] #AKS
          step.size <- n.trees[k]-n.trees[k-1]
          k <- k+1 #AKS
              } else {  #AKS
          n.fitted <- n.fitted + step.size
          }  #AKS

        trees.fitted <- c(trees.fitted,n.fitted)

        j <- j + 1

        for (i in 1:n.folds) {

          model.mask <- selector != i  #used to fit model on majority of data
          pred.mask <- selector == i   #used to identify the with-held subset

          y.subset <- y.data[model.mask]
          x.subset <- x.data[model.mask,]
          weight.subset <- site.weights[model.mask]
          if (!is.null(offset)) {
            offset.subset <- offset[model.mask]
          }

          model.list[[i]] <- gbm.more(model.list[[i]], weights = weight.subset, step.size)

          fitted.values <- model.list[[i]]$fit # predict.gbm(model.list[[i]],x.subset, type = "response", n.trees = n.fitted)
          if (!is.null(offset)) fitted.values <- fitted.values + offset[model.mask]
          if (family == "bernoulli") fitted.values <- exp(fitted.values)/(1 + exp(fitted.values))
          if (family == "poisson") fitted.values <- exp(fitted.values)

          pred.values[pred.mask] <- predict.gbm(model.list[[i]], x.data[pred.mask, ], n.trees = n.fitted)
          if (!is.null(offset)) pred.values[pred.mask] <- pred.values[pred.mask] + offset[pred.mask]
          if (family == "bernoulli") pred.values[pred.mask] <- exp(pred.values[pred.mask])/(1 + exp(pred.values[pred.mask]))
          if (family == "poisson") pred.values[pred.mask] <- exp(pred.values[pred.mask])

    # calculate training deviance

          y_i <- y.subset
          u_i <- fitted.values
          weight.fitted <- site.weights[model.mask]
          training.loss.matrix[i,j] <- calc.deviance(y_i, u_i, weight.fitted, family = family)

    # calc holdout deviance

          u_i <- pred.values[pred.mask]
          y_i <- y.data[pred.mask]
          weight.preds <- site.weights[pred.mask]
          cv.loss.matrix[i,j] <- calc.deviance(y_i, u_i, weight.preds, family = family)

        }  # end of inner loop

        cv.loss.values <- apply(cv.loss.matrix,2,mean)

        if (j < 5 & autostop==F) {   #AKS
          if (cv.loss.values[j] > cv.loss.values[j-1]) {
            if (!silent) cat("restart model with a smaller learning rate or smaller step size...")
            return()
          }
        }

          if (j >= 20) {   #calculate stopping rule value
            test1 <- mean(cv.loss.values[(j-9):j])
            test2 <- mean(cv.loss.values[(j-19):(j-9)])
            delta.deviance <- test2 - test1
          }

          if (verbose) cat(n.fitted," ",round(cv.loss.values[j],4),"\n");flush.console()#AKS
          if(autostop==T & j>2){ # this if statement added by AKS
              if((cv.loss.values[j]>cv.loss.values[j-1])){# & (cv.loss.values[j-1]>cv.loss.values[j-2])){ # if deviance increases twice in a row
                  stop.loop=T#n.fitted <- max.trees # by setting n.fitted to max.trees, the while loop will terminate.
                  }
              }



  } # end of while loop

# now begin process of calculating optimal number of trees

  training.loss.values <- apply(training.loss.matrix,2,mean)

  cv.loss.ses <- rep(0,length(cv.loss.values))
  cv.loss.ses <- sqrt(apply(cv.loss.matrix,2,var)) / sqrt(n.folds)

# find the target holdout deviance

  y.bar <- min(cv.loss.values)

# plot out the resulting curve of holdout deviance

  if (plot.main) {

    y.min <- min(cv.loss.values - cv.loss.ses)  #je added multiplier 10/8/05
    y.max <- max(cv.loss.values + cv.loss.ses)  #je added multiplier 10/8/05 }

    if (plot.folds) {
      y.min <- min(cv.loss.matrix)
      y.max <- max(cv.loss.matrix) }

      plot(trees.fitted, cv.loss.values, type = 'l', ylab = "holdout deviance",
          xlab = "no. of trees", ylim = c(y.min,y.max), ...)
      abline(h = y.bar, col = 2)

      lines(trees.fitted, cv.loss.values + cv.loss.ses, lty=2)
      lines(trees.fitted, cv.loss.values - cv.loss.ses, lty=2)

      if (plot.folds) {
        for (i in 1:n.folds) {
          lines(trees.fitted, cv.loss.matrix[i,],lty = 3)
      }
    }
  }

# identify the optimal number of trees

  target.trees <- trees.fitted[match(TRUE,cv.loss.values == y.bar)]
  #cat("\n");cat("optimal n trees =",target.trees,"\n")    #AKS

  if(plot.main) {
    abline(v = target.trees, col=3)
    title(paste(sp.name,", d - ",tree.complexity,", lr - ",learning.rate, sep=""))
  }

# skip additional details on final model unless target.trees is close to 1000 (AKS)#
if(abs(target.trees-1000) >= 600 & superfast==T){         # AKS
    return(list(target.trees=target.trees)) # AKS
    } else {      # AKS


# estimate the cv deviance and test statistics
# includes estimates of the standard error of the fitted values added 2nd may 2005

  cv.deviance.stats <- rep(0, n.folds)
  cv.roc.stats <- rep(0, n.folds)
  cv.cor.stats <- rep(0, n.folds)
  cv.calibration.stats <- matrix(0, ncol=5, nrow = n.folds)
  if (family == "bernoulli") threshold.stats <- rep(0, n.folds)

  fitted.matrix <- matrix(NA, nrow = n.cases, ncol = n.folds)   #used to calculate se's
  fold.fit <- rep(0,n.cases)

  for (i in 1:n.folds) {

    pred.mask <- selector == i   #used to identify the with-held subset
    model.mask <- selector != i  #used to fit model on majority of data

    fits <- predict.gbm(model.list[[i]], x.data[model.mask, ], n.trees = target.trees)
    if (!is.null(offset)) fits <- fits + offset[model.mask]
    if (family == "bernoulli") fits <- exp(fits)/(1 + exp(fits))
    if (family == "poisson") fits <- exp(fits)
    fitted.matrix[model.mask,i] <- fits

    fits <- predict.gbm(model.list[[i]], x.data[pred.mask, ], n.trees = target.trees)
    if (!is.null(offset)) fits <- fits + offset[pred.mask]
    fold.fit[pred.mask] <- fits  # store the linear predictor values
    if (family == "bernoulli") fits <- exp(fits)/(1 + exp(fits))
    if (family == "poisson") fits <- exp(fits)
    fitted.matrix[pred.mask,i] <- fits

    y_i <- y.data[pred.mask]
    u_i <- fitted.matrix[pred.mask,i]  #pred.values[pred.mask]      ####
    weight.preds <- site.weights[pred.mask]

    cv.deviance.stats[i] <- calc.deviance(y_i, u_i, weight.preds, family = family)

    cv.cor.stats[i] <- cor(y_i,u_i)

    if (family == "bernoulli") {
      cv.roc.stats[i] <- roc(y_i,u_i)
      cv.calibration.stats[i,] <- calibration(y_i,u_i,"binomial")
      threshold.stats[i] <- approx(ppoints(u_i), sort(u_i,decreasing = T), prevalence)$y
    }

    if (family == "poisson") {
      cv.calibration.stats[i,] <- calibration(y_i,u_i,"poisson")
    }
  }

  fitted.vars <- apply(fitted.matrix,1, var, na.rm = TRUE)

 #now calculate the mean and se's for the folds

  cv.dev <- mean(cv.deviance.stats, na.rm = TRUE)
  cv.dev.se <- sqrt(var(cv.deviance.stats)) / sqrt(n.folds)

  cv.cor <- mean(cv.cor.stats, na.rm = TRUE)
  cv.cor.se <- sqrt(var(cv.cor.stats, use = "complete.obs")) / sqrt(n.folds)

  cv.roc <- 0.0
  cv.roc.se <- 0.0

  if (family == "bernoulli") {
    cv.roc <- mean(cv.roc.stats,na.rm=TRUE)
    cv.roc.se <- sqrt(var(cv.roc.stats, use = "complete.obs")) / sqrt(n.folds)
    cv.threshold <- mean(threshold.stats, na.rm = T)
    cv.threshold.se <- sqrt(var(threshold.stats, use = "complete.obs")) / sqrt(n.folds)
  }

  cv.calibration <- 0.0
  cv.calibration.se <- 0.0

  if (family == "poisson" | family == "bernoulli") {
    cv.calibration <- apply(cv.calibration.stats,2,mean)
    cv.calibration.se <- apply(cv.calibration.stats,2,var)
    cv.calibration.se <- sqrt(cv.calibration.se) / sqrt(n.folds) }

 #fit the final model

  if (is.null(offset)) {
    gbm.call <- paste("gbm(y.data~.,data=x.data,n.trees=target.trees,interaction.depth=tree.complexity,shrinkage=learning.rate,bag.fraction=bag.fraction,weights=site.weights,distribution=as.character(family),var.monotone=var.monotone,verbose=FALSE)",sep="")
    }
  else {
    gbm.call <- paste("gbm(y.data~.+ offset(offset),data=x.data,n.trees=target.trees,interaction.depth=tree.complexity,shrinkage=learning.rate,bag.fraction=bag.fraction,weights=site.weights,distribution=as.character(family),var.monotone=var.monotone,verbose=FALSE)",sep="")
    }

  if (!silent) cat("fitting final gbm model with a fixed number of ",target.trees," trees for ",sp.name,"\n")

  gbm.object <- eval(parse(text = gbm.call))  # AKS

  best.trees <- target.trees

#extract fitted values and summary table

  gbm.summary <- summary(gbm.object,n.trees = target.trees, plotit = FALSE)

  fits <- predict.gbm(gbm.object,x.data,n.trees = target.trees)
  if (!is.null(offset)) fits <- fits + offset
  if (family == "bernoulli") fits <- exp(fits)/(1 + exp(fits))
  if (family == "poisson") fits <- exp(fits)
  fitted.values <- fits

  y_i <- y.data
  u_i <- fitted.values
  resid.deviance <- calc.deviance(y_i, u_i, weights = site.weights, family = family, calc.mean = FALSE)

  self.cor <- cor(y_i,u_i)
  self.calibration <- 0.0
  self.roc <- 0.0

  if (family == "bernoulli") {   #do this manually as we need the residuals
    deviance.contribs <- (y_i * log(u_i)) + ((1-y_i) * log(1 - u_i))
    residuals <- sqrt(abs(deviance.contribs * 2))
    residuals <- ifelse((y_i - u_i) < 0, 0 - residuals, residuals)
    self.roc <- roc(y_i,u_i)
    self.calibration <- calibration(y_i,u_i,"binomial")
  }

  if (family == "poisson") {    #do this manually as we need the residuals
    deviance.contribs <- ifelse(y_i == 0, 0, (y_i * log(y_i/u_i))) - (y_i - u_i)
    residuals <- sqrt(abs(deviance.contribs * 2))
    residuals <- ifelse((y_i - u_i) < 0, 0 - residuals, residuals)
    self.calibration <- calibration(y_i,u_i,"poisson")
  }

  if (family == "gaussian" | family == "laplace") {
    residuals <- y_i - u_i
  }

  mean.resid.deviance <- resid.deviance/n.cases

  z2 <- unclass(Sys.time())
  elapsed.time.minutes <- round((z2 - z1)/ 60,2)  # calculate the total elapsed time

  if (verbose) {
    cat("\n")
    cat("mean total deviance =", round(mean.total.deviance,3),"\n")
    cat("mean residual deviance =", round(mean.resid.deviance,3),"\n","\n")
    cat("estimated cv deviance =", round(cv.dev,3),"; se =",
      round(cv.dev.se,3),"\n","\n")
    cat("training data correlation =",round(self.cor,3),"\n")
    cat("cv correlation = ",round(cv.cor,3),"; se =",round(cv.cor.se,3),"\n","\n")
    if (family == "bernoulli") {
      cat("training data ROC score =",round(self.roc,3),"\n")
      cat("cv ROC score =",round(cv.roc,3),"; se =",round(cv.roc.se,3),"\n","\n")
    }
    cat("elapsed time - ",round(elapsed.time.minutes,2),"minutes","\n")
  }

  if (n.fitted == max.trees & !silent) {
    cat("\n"," warning ","\n","\n")
    cat("maximum tree limit reached - results may not be optimal","\n")
    cat("  - refit with faster learning rate or increase maximum number of trees","\n")


  }

 # now assemble data to be returned

  gbm.detail <- list(dataframe = dataframe.name, gbm.x = gbm.x, predictor.names = names(x.data),
    gbm.y = gbm.y, response.name = sp.name, offset = offset.name, family = family, tree.complexity = tree.complexity,
    learning.rate = learning.rate, bag.fraction = bag.fraction, cv.folds = n.folds,
    prev.stratification = prev.stratify, max.fitted = n.fitted, n.trees = target.trees,
    best.trees = target.trees, train.fraction = 1.0, tolerance.method = tolerance.method,
    tolerance = tolerance, var.monotone = var.monotone, date = date(),
    elapsed.time.minutes = elapsed.time.minutes)

  training.stats <- list(null = total.deviance, mean.null = mean.total.deviance,
    resid = resid.deviance, mean.resid = mean.resid.deviance, correlation = self.cor,
    discrimination = self.roc, calibration = self.calibration)

  cv.stats <- list(deviance.mean = cv.dev, deviance.se = cv.dev.se,
    correlation.mean = cv.cor, correlation.se = cv.cor.se,
    discrimination.mean = cv.roc, discrimination.se = cv.roc.se,
    calibration.mean = cv.calibration, calibration.se = cv.calibration.se)

  if (family == "bernoulli") {
    cv.stats$cv.threshold <- cv.threshold
    cv.stats$cv.threshold.se <- cv.threshold.se
  }

  rm(x.data,y.data, envir = globalenv())          # finally, clean up the temporary dataframes

 # and assemble results for return

  gbm.object$gbm.call <- gbm.detail
  gbm.object$fitted <- fitted.values
  gbm.object$fitted.vars <- fitted.vars
  gbm.object$residuals <- residuals
  gbm.object$contributions <- gbm.summary
  gbm.object$self.statistics <- training.stats
  gbm.object$cv.statistics <- cv.stats
  gbm.object$weights <- site.weights
  gbm.object$trees.fitted <- trees.fitted
  gbm.object$training.loss.values <- training.loss.values
  gbm.object$cv.values <- cv.loss.values
  gbm.object$cv.loss.ses <- cv.loss.ses
  gbm.object$cv.loss.matrix <- cv.loss.matrix
  gbm.object$cv.roc.matrix <- cv.roc.stats
  gbm.object$target.trees <- target.trees

  if (keep.fold.models) gbm.object$fold.models <- model.list
  else gbm.object$fold.models <- NULL

  if (keep.fold.vector) gbm.object$fold.vector <- selector
  else gbm.object$fold.vector <- NULL

  if (keep.fold.fit) gbm.object$fold.fit <- fold.fit
  else gbm.object$fold.fit <- NULL

  return(gbm.object)
  } #end if statement
}

"gbm.plot" <-
function(gbm.object,                # a gbm object - could be one from gbm.step
     variable.no = 0,               # the var to plot - if zero then plots all
     nt = gbm.object$n.trees,       # how many trees to use
     smooth = FALSE,                # should we add a smoothed version of the fitted function
     rug = T,                       # plot a rug of deciles
     n.plots = length(pred.names),  # plot the first n most important preds
     common.scale = T,              # use a common scale on the y axis
     write.title = T,               # plot a title above the plot
     y.label = "fitted function",   # the default y-axis label
     x.label = NULL,                # the default x-axis label
     show.contrib = T,              # show the contribution on the x axis
     plot.layout = c(3,4),          # define the default layout for graphs on the page
     rug.side = 3,                  # which axis for rug plot? default (3) is top; bottom=1
     rug.lwd = 1,                   # line width for rug plots
     rug.tick = 0.03,               # tick length for rug plots
     plotit=T,                      # AKS
     prob.scale=T,                       # AKS
     ...                            # other arguments to pass to the plotting
                                    # useful options include cex.axis, cex.lab, etc.
     )
{
# function to plot gbm response variables, with the option
# of adding a smooth representation of the response if requested
# additional options in this version allow for plotting on a common scale
# note too that fitted functions are now centered by subtracting their mean
#
# version 2.9
#
# j. leathwick/j. elith - March 2007
#

require(gbm)


gbm.call <- gbm.object$gbm.call
gbm.x <- gbm.call$gbm.x
pred.names <- gbm.call$predictor.names
out.names <- rep("",length(pred.names))
response.name <- gbm.call$response.name
dataframe.name <- gbm.call$dataframe
data <- eval.parent(parse(text = dataframe.name))

max.plots <- plot.layout[1] * plot.layout[2]
plot.count <- 0
n.pages <- 1

if (length(variable.no) > 1) {stop("only one response variable can be plotted at a time")}

if (variable.no > 0) {   #we are plotting all vars in rank order of contribution
  n.plots <- 1
  }

max.vars <- length(gbm.object$contributions$var)
if (n.plots > max.vars) {
  n.plots <- max.vars
  cat("warning - reducing no of plotted predictors to maximum available (",max.vars,")\n",sep="")
  }

predictors <- list(rep(NA,n.plots)) # matrix(0,ncol=n.plots,nrow=100)
responses <- list(rep(NA,n.plots)) # matrix(0,ncol=n.plots,nrow=100)

for (j in c(1:n.plots)) {  #cycle through the first time and get the range of the functions
  if (n.plots == 1) {
    k <- variable.no
  }
  else k <- match(gbm.object$contributions$var[j],pred.names)

  if (is.null(x.label)) var.name <- gbm.call$predictor.names[k]
    else var.name <- x.label

  pred.data <- data[,gbm.call$gbm.x[k]]
  out.names[j] <- names(data)[gbm.call$gbm.x[k]]

  response.matrix <- plot.gbm(gbm.object, i.var = k, n.trees = nt, return.grid = TRUE,...)

  predictors[[j]] <- response.matrix[,1]
  if (is.factor(data[,gbm.call$gbm.x[k]])) {
    predictors[[j]] <- factor(predictors[[j]],levels = levels(data[,gbm.call$gbm.x[k]]))
    }
  responses[[j]] <- response.matrix[,2] - mean(response.matrix[,2])
  if(prob.scale) responses[[j]] <- logit(responses[[j]])

  if(j == 1) {
    ymin = min(responses[[j]])
    ymax = max(responses[[j]])
    }
  else {
    ymin = min(ymin,min(responses[[j]]))
    ymax = max(ymax,max(responses[[j]]))
    }
  }

# now do the actual plots
  if(plotit==T){
      for (j in c(1:n.plots)) {

       if (plot.count == max.plots) {
         plot.count = 0
         n.pages <- n.pages + 1
       }

       if (plot.count == 0) {
         #windows(width = 11, height = 8)  #aks
         par(mfrow = plot.layout)
       }

        plot.count <- plot.count + 1

        if (n.plots == 1) {
          k <- match(pred.names[variable.no],gbm.object$contributions$var)
          if (show.contrib) {
             x.label <- paste(var.name,"  (",round(gbm.object$contributions[k,2],1),"%)",sep="")
          }
        }
        else {
          k <- match(gbm.object$contributions$var[j],pred.names)
          var.name <- gbm.call$predictor.names[k]
          if (show.contrib) {
             x.label <- paste(var.name,"  (",round(gbm.object$contributions[j,2],1),"%)",sep="")
          }
          else x.label <- var.name
        }

        if (common.scale) {
          plot(predictors[[j]],responses[[j]],ylim=c(ymin,ymax), type='l',
            xlab = x.label, ylab = y.label, ...)
        }
        else {
          plot(predictors[[j]],responses[[j]], type='l',
            xlab = x.label, ylab = y.label, ...)
        }
        if (smooth & is.vector(predictors[[j]])) {
          temp.lo <- loess(responses[[j]] ~ predictors[[j]], span = 0.3)
          lines(predictors[[j]],fitted(temp.lo), lty = 2, col = 2)
        }
        if (plot.count == 1) {
          if (write.title) {
            title(paste(response.name," - page ",n.pages,sep=""))
          }
          if (rug & is.vector(data[,gbm.call$gbm.x[k]])) {
            rug(quantile(data[,gbm.call$gbm.x[k]], probs = seq(0, 1, 0.1), na.rm = TRUE), side = rug.side, lwd = rug.lwd, ticksize = rug.tick)
          }
        }
        else {
          if (write.title & j == 1) {
            title(response.name)
          }
          if (rug & is.vector(data[,gbm.call$gbm.x[k]])) {
            rug(quantile(data[,gbm.call$gbm.x[k]], probs = seq(0, 1, 0.1), na.rm = TRUE), side = rug.side, lwd = rug.lwd, ticksize = rug.tick)
          }
        }
      }
    }
  return(invisible(list(names=out.names,preds=predictors,resp=responses)))
}


"gbm.perspec" <-
function(gbm.object,
     x = 1,                # the first variable to be plotted
     y = 2,                # the second variable to be plotted
     pred.means = NULL,    # allows specification of values for other variables
     x.label = NULL,       # allows manual specification of the x label
     x.range = NULL,       # manual range specification for the x variable
     y.label = NULL,       # and y label
     y.range = NULL,       # and the y
     z.range = NULL,       # allows control of the vertical axis
     ticktype = "detailed",# specifiy detailed types - otherwise "simple"
     theta = 55,           # rotation
     phi=40,               # and elevation
     smooth = "none",      # controls smoothing of the predicted surface
     mask = FALSE,         # controls masking using a sample intensity model
     perspective = TRUE,   # controls whether a contour or perspective plot is drawn
     verbose=F,            # AKS
     ...)                  # allows the passing of additional arguments to plotting routine
                           # useful options include shade, ltheta, lphi for controlling illumination
                           # and cex for controlling text size - cex.axis and cex.lab have no effect
{
#
# gbm.perspec version 2.9 April 2007
# J Leathwick/J Elith
#
# takes a gbm boosted regression tree object produced by gbm.step and
# plots a perspective plot showing predicted values for two predictors
# as specified by number using x and y
# values for all other variables are set at their mean by default
# but values can be specified by giving a list consisting of the variable name
# and its desired value, e.g., c(name1 = 12.2, name2 = 57.6)

  require(gbm)


#get the boosting model details

  gbm.call <- gbm.object$gbm.call
  gbm.x <- gbm.call$gbm.x
  n.preds <- length(gbm.x)
  gbm.y <- gbm.call$gbm.y
  pred.names <- gbm.call$predictor.names
  family = gbm.call$family

  x.name <- gbm.call$predictor.names[x]

  if (is.null(x.label)) {
    x.label <- gbm.call$predictor.names[x]}

  y.name <- gbm.call$predictor.names[y]

  if (is.null(y.label)) {
    y.label <- gbm.call$predictor.names[y]}

  data <- eval.parent(parse(text=gbm.call$dataframe))[,gbm.x]   #AKS
  n.trees <- gbm.call$best.trees

  if (is.null(x.range)) {
    x.var <- seq(min(data[,x],na.rm=T),max(data[,x],na.rm=T),length = 50)
  }
  else {x.var <- seq(x.range[1],x.range[2],length = 50)}

  if (is.null(y.range)) {
    y.var <- seq(min(data[,y],na.rm=T),max(data[,y],na.rm=T),length = 50)
  }
  else {y.var <- seq(y.range[1],y.range[2],length = 50)}

  pred.frame <- expand.grid(list(x.var,y.var))
  names(pred.frame) <- c(x.name,y.name)

  j <- 3
  for (i in 1:n.preds) {
    if (i != x & i != y) {
      if (is.vector(data[,i])) {
        m <- match(pred.names[i],names(pred.means))
        if (is.na(m)) {
          pred.frame[,j] <- mean(data[,i],na.rm=T)
        }
        else pred.frame[,j] <- pred.means[m]
      }
      if (is.factor(data[,i])) {
        m <- match(pred.names[i],names(pred.means))
        temp.table <- table(data[,i])
        if (is.na(m)) {
          pred.frame[,j] <- rep(names(temp.table)[2],2500)
        }
        else pred.frame[,j] <- pred.means[m]
        pred.frame[,j] <- factor(pred.frame[,j],levels=names(temp.table))
      }
      names(pred.frame)[j] <- pred.names[i]
      j <- j + 1
     }
  }
#
# form the prediction
#
  prediction <- predict.gbm(gbm.object,pred.frame,n.trees = n.trees, type="response")

# model smooth if required

  if (smooth == "model") {
    require(splines)
    pred.glm <- glm(prediction ~ ns(pred.frame[,1], df = 8) * ns(pred.frame[,2], df = 8), data=pred.frame,family=poisson)
    prediction <- fitted(pred.glm)
  }

# report the maximum value and set up realistic ranges for z

  max.pred <- max(prediction)
  if(verbose) cat("maximum value = ",round(max.pred,2),"\n")    #AKS

  if (is.null(z.range)) {
    if (family == "bernoulli") {
      z.range <- c(0,1)
    }
    else if (family == "poisson") {
      z.range <- c(0,max.pred * 1.1)
    }
    else {
      z.min <- min(data[,y],na.rm=T)
      z.max <- max(data[,y],na.rm=T)
      z.delta <- z.max - z.min
      z.range <- c(z.min - (1.1 * z.delta), z.max + (1.1 * z.delta))
    }
  }
# form the matrix

  pred.matrix <- matrix(prediction,ncol=50,nrow=50)

# kernel smooth if required

  if (smooth == "average") {  #apply a 3 x 3 smoothing average
     pred.matrix.smooth <- pred.matrix
     for (i in 2:49) {
       for (j in 2:49) {
         pred.matrix.smooth[i,j] <- mean(pred.matrix[c((i-1):(i+1)),c((j-1):(j+1))])
       }
     }
  pred.matrix <- pred.matrix.smooth
  }

# mask out values inside hyper-rectangle but outside of sample space

  if (mask) {
    mask.trees <- mask.object$gbm.call$best.trees
    point.prob <- predict.gbm(mask.object[[1]],pred.frame, n.trees = mask.trees, type="response")
    point.prob <- matrix(point.prob,ncol=50,nrow=50)
    pred.matrix[point.prob < 0.5] <- 0.0
  }
#
# and finally plot the result
#
  if (!perspective) {
    image(x = x.var, y = y.var, z = pred.matrix, zlim = z.range)
  }
  else {
    persp(x=x.var, y=y.var, z=pred.matrix, zlim= z.range,      # input vars
      xlab = x.label, ylab = y.label, zlab = "fitted value",   # labels
      theta=theta, phi=phi, r = sqrt(10), d = 3,               # viewing pars
      ticktype = ticktype, mgp = c(4,1,0), ...) #
  }
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

"gbm.interactions" <-
function(gbm.object,
   use.weights = FALSE,     # use weights for samples
   mask.object)             # a gbm object describing sample intensity
{
#
# gbm.interactions version 2.9
#
# j. leathwick, j. elith - May 2007
#
# functions assesses the magnitude of 2nd order interaction effects
# in gbm models fitted with interaction depths greater than 1
# this is achieved by:
#   1. forming predictions on the linear scale for each predictor pair;
#   2. fitting a linear model that relates these predictions to the predictor
#        pair, with the the predictors fitted as factors;
#   3. calculating the mean value of the residuals, the magnitude of which
#        increases with the strength of any interaction effect;
#   4. results are stored in an array;
#   5. finally, the n most important interactions are identified,
#        where n is 25% of the number of interaction pairs;

  require(gbm)

  gbm.call <- gbm.object$gbm.call
  n.trees <- gbm.call$best.trees
  depth <- gbm.call$interaction.depth
  gbm.x <- gbm.call$gbm.x
  n.preds <- length(gbm.x)
  pred.names <- gbm.object$gbm.call$predictor.names
  cross.tab <- matrix(0,ncol=n.preds,nrow=n.preds)
  dimnames(cross.tab) <- list(pred.names,pred.names)
  int.p.table <- matrix(NA,ncol=n.preds,nrow=n.preds,dimnames=list(pred.names,pred.names))#AKS

  if (use.weights) mask.trees <- mask.object$gbm.call$best.trees

  #cat("gbm.interactions - version 2.9 \n")  #aks
  #cat("Cross tabulating interactions for gbm model with ",n.preds," predictors","\n",sep="") #aks

  data <- eval.parent(parse(text=gbm.call$dataframe),n=1)[,gbm.x]    #aks

  for (i in 1:(n.preds - 1)) {  # step through the predictor set
    x.fac<-F
    if (is.vector(data[,i])) {  # create a sequence through the range
       x.var <- seq(min(data[,i],na.rm=T),max(data[,i],na.rm=T),length = 20)
       x2 <-  as.vector(tapply(x.var,rep(1:10,rep(2,10)),mean))
       }  else {                      # otherwise set up simple factor variable
       x.var <- factor(names(table(data[,i])),levels = levels(data[,i]))
       x.fac<-T
       }
    x.length <- length(x.var)

    #cat(i,"\n")  #aks

    for (j in (i+1):n.preds) { #create vector or factor data for second variable
      y.fac<-F
      if (is.vector(data[,j])) {
        y.var <- seq(min(data[,j],na.rm=T),max(data[,j],na.rm=T),length = 20)
        y2 <-  as.vector(tapply(y.var,rep(1:10,rep(2,10)),mean))

      }    else {
        y.var <- factor(names(table(data[,j])),levels = levels(data[,j]))
        y.fac<-T
      }
      y.length <- length(y.var)

# and now make a temporary data frame

      pred.frame <- expand.grid(list(x.var,y.var))
      names(pred.frame) <- c(pred.names[i],pred.names[j])

      n <- 3 # and add the balance of the variables to it

      for (k in 1:n.preds) {
        if (k != i & k != j) {
          if (is.vector(data[,k])) {  # either with the mean
            pred.frame[,n] <- mean(data[,k],na.rm=T)
          } else {   # or the most common factor level
            temp.table <- sort(table(data[,k]),decreasing = TRUE)
            pred.frame[,n] <- rep(names(temp.table)[1],x.length * y.length)
            pred.frame[,n] <- as.factor(pred.frame[,n])
          }
          names(pred.frame)[n] <- pred.names[k]
          n <- n + 1
        }
      }
#
# form the prediction
#
      prediction <- predict.gbm(gbm.object,pred.frame,n.trees = n.trees, type="link")

      if (use.weights) {
        point.prob <- predict.gbm(mask.object[[1]],pred.frame, n.trees = mask.trees, type="response")
        interaction.test.model <- lm(prediction ~ as.factor(pred.frame[,1]) + as.factor(pred.frame[,2]),
          weights = point.prob)
      }

      else {

        interaction.test.model <- lm(prediction ~ as.factor(pred.frame[,1]) + as.factor(pred.frame[,2]))
      }
      #cat("\n",i,names(data)[i],x.length,length(unique(data[,i])),"  ",
      #      j,names(data)[j],y.length,length(unique(data[,j])),dim(pred.frame));flush.console()
      #print(summary(data[,i]));print(summary(data[,j]))
      # check significance of interaction term in model that pools every 4 grid points #
      pred.frame<<-pred.frame

      if(x.fac==F | y.fac==F){ # case where at least one cov is not a factor
          if(x.fac==T) {x3 <- pred.frame[,1]
          } else { x3 <- rep(rep(x2,rep(2,10)),y.length) }
          if(y.fac==T) {y3 <- pred.frame[,1]
          } else { y3 <- rep(y2,rep(x.length*2,length(y2)))}
          int.p.table[i,j] <- anova(lm(prediction~as.factor(x3)*as.factor(y3)))[3,5] #aks
          }


      interaction.flag <- round(mean(resid(interaction.test.model)^2)*1000,2)

      cross.tab[i,j] <- interaction.flag
      }   # end of j loop
  }  # end of i loop

# create an index of the values in descending order

  search.index <- ((n.preds^2) + 1) - rank(cross.tab, ties.method = "first")

  n.important <- max(2,round(0.1 * ((n.preds^2)/2),0))
  var1.names <- rep(" ",n.important)
  var1.index <- rep(0,n.important)
  var2.names <- rep(" ",n.important)
  var2.index <- rep(0,n.important)
  int.size <- rep(0,n.important)
  int.p <- rep(NA,n.important) #aks

  for (i in 1:n.important) {

    index.match <- match(i,search.index)

    j <- trunc(index.match/n.preds) + 1
    var1.index[i] <- j
    var1.names[i] <- pred.names[j]

    k <- index.match%%n.preds
    if (k > 0) {   #only do this if k > 0 - otherwise we have all zeros from here on
      var2.index[i] <- k
      var2.names[i] <- pred.names[k]

      int.size[i] <- cross.tab[k,j]
      int.p[i] <- int.p.table[k,j] #aks
    }

  }
  rank.list <- data.frame(var1.index,var1.names,var2.index,var2.names,int.size,p=int.p)
  rank.list <- rank.list[complete.cases(rank.list),]
  return(list(rank.list = rank.list, interactions = cross.tab, gbm.call = gbm.object$gbm.call))
}

"gbm.simplify" <-
function(gbm.object,          # a gbm object describing sample intensity
  n.folds = 10,               # number of times to repeat the analysis
  n.drops = "auto",           # can be automatic or an integer specifying the number of drops to check
  alpha = 1,                  # controls stopping when n.drops = "auto"
  prev.stratify = TRUE,       # use prevalence stratification in selecting evaluation data
  eval.data = NULL,           # an independent evaluation data set - leave here for now
  plot = TRUE,                # plot results
  verbose=F)                  # to suppress text output.
{
# function to simplify a brt model fitted using gbm.step
#
# version 2.9 - J. Leathwick/J. Elith - June 2007
#
# starts with an inital cross-validated model as produced by gbm.step
# and then assesses the potential to remove predictors using k-fold cv
# does this for each fold, removing the lowest contributing predictor,
# and repeating this process for a set number of steps
# after the removal of each predictor, the change in predictive deviance
# is computed relative to that obtained when using all predictors
# it returns a list containing the mean change in deviance and its se
# as a function of the number of variables removed
# having completed the cross validation, it then identifies the sequence
# of variable to remove when using the full data set, testing this
# up to the number of steps used in the cross-validation phase of the analysis
# with results reported to the screen - it then returns
# a table containing the order in which variables are to be removed
# and a list of vectors, each of which specifies the predictor col numbers
# in the original dataframe  - the latter can be used as an argument to gbm.step
# e.g., gbm.step(data = data, gbm.x = simplify.object$pred.list[[4]]...
# would implement a new analysis with the original predictor set, minus its
# four lowest contributing predictors
#

require(gbm)

# first get the original analysis details..

  gbm.call <- gbm.object$gbm.call
  data <- eval.parent(parse(text=gbm.call$dataframe))
  n.cases <- nrow(data)
  gbm.x <- gbm.call$gbm.x
  gbm.y <- gbm.call$gbm.y
  family <- gbm.call$family
  lr <- gbm.call$learning.rate
  tc <- gbm.call$tree.complexity
  start.preds <- length(gbm.x)
  max.drops <- start.preds - 2
  response.name <- gbm.call$response.name
  predictor.names <- gbm.call$predictor.names
  n.trees <- gbm.call$best.trees
  pred.list <- list(initial = gbm.x)
  weights <- gbm.object$weights

  if (n.drops == "auto") auto.stop <- TRUE

  else auto.stop <- FALSE

# take a copy of the original data and starting predictors

  orig.data <- data
  orig.gbm.x <- gbm.x

#  if (!is.null(eval.data)) independent.test <- TRUE
#    else independent.test <- FALSE

# extract original performance statistics...

  original.deviance <- round(gbm.object$cv.statistics$deviance.mean,4)
  original.deviance.se <- round(gbm.object$cv.statistics$deviance.se,4)

  if(verbose){ #aks
    cat("\n");cat("gbm.simplify - version 2.9","\n\n")#AKS
    cat("simplifying gbm.step model for ",response.name," with ",start.preds," predictors",sep="")
    cat(" and ",n.cases," observations \n",sep="")
    cat("original deviance = ",original.deviance,"(",original.deviance.se,")\n\n",sep="")
    }

# check that n.drops is less than n.preds - 2 and update if required

  if (auto.stop) {
    if(verbose) cat("variable removal will proceed until average change exceeds the original se\n\n") #aks
    n.drops <- 1 } else{
    if (n.drops > start.preds - 2) {
      if(verbose) cat("value of n.drops (",n.drops,") is greater than permitted","\n", #aks
        "resetting value to ",start.preds - 2,"\n\n",sep="")
      n.drops <- start.preds - 2
    } else {
      if(verbose) cat("a fixed number of",n.drops,"drops will be tested\n\n") #aks
    }
  }
  flush.console()#AKS


# set up storage for results

  dev.results <- matrix(0, nrow = n.drops, ncol = n.folds)
  dimnames(dev.results) <- list(paste("drop.",1:n.drops,sep=""),
   paste("rep.",1:n.folds,sep=""))

  drop.count <- matrix(NA, nrow = start.preds, ncol = n.folds)
  dimnames(drop.count) <- list(predictor.names,paste("rep.",1:n.folds,sep=""))

  original.deviances <- rep(0,n.folds)

  model.list <- list(paste("model",c(1:n.folds),sep=""))     # dummy list for the tree models

# create gbm.fixed function call

  gbm.call.string <- paste("try(gbm.fixed(data=train.data,gbm.x=gbm.new.x,gbm.y=gbm.y,",sep="")
  gbm.call.string <- paste(gbm.call.string,"family=family,learning.rate=lr,tree.complexity=tc,",sep="")
  gbm.call.string <- paste(gbm.call.string,"n.trees = ",n.trees,", site.weights = weights.subset,verbose=FALSE))",sep="")

# now set up the fold structure

  if (prev.stratify & family == "bernoulli") {
    presence.mask <- data[,gbm.y] == 1
    absence.mask <- data[,gbm.y] == 0
    n.pres <- sum(presence.mask)
    n.abs <- sum(absence.mask)

# create a vector of randomised numbers and feed into presences
    selector <- rep(0,n.cases)
    temp <- rep(seq(1, n.folds, by = 1), length = n.pres)
    temp <- temp[order(runif(n.pres, 1, 100))]
    selector[presence.mask] <- temp

# and then do the same for absences
    temp <- rep(seq(1, n.folds, by = 1), length = n.abs)
    temp <- temp[order(runif(n.abs, 1, 100))]
    selector[absence.mask] <- temp
    }

  else {  #otherwise make them random with respect to presence/absence
    selector <- rep(seq(1, n.folds, by = 1), length = n.cases)
    selector <- selector[order(runif(n.cases, 1, 100))]
    }

# now start by creating the intial models for each fold

  if(verbose) cat("creating initial models");flush.console()#AKS

  gbm.new.x <- orig.gbm.x

  for (i in 1:n.folds) {

# create the training and prediction folds

    train.data <- orig.data[selector!=i,]
    weights.subset <- weights[selector != i]
    eval.data <- orig.data[selector==i,]

    model.list[[i]] <- eval(parse(text=gbm.call.string))  # create a fixed size object

# now make predictions to the withheld fold

    u_i <- eval.data[,gbm.y]
    y_i <- predict.gbm(model.list[[i]], eval.data, n.trees, "response")

    original.deviances[i] <- round(calc.deviance(u_i,y_i, family = family, calc.mean = TRUE),4)
    if(verbose) cat(".");flush.console()#AKS
  } # end of creating initial models
  if(verbose) {cat("\n");cat("done \n\n")}  #aks
  n.steps <- 1

  while (n.steps <= n.drops & n.steps <= max.drops) {

    if(verbose) cat("dropping predictor",n.steps,"\n");flush.console()#AKS

    for (i in 1:n.folds) {

# get the right data

    train.data <- orig.data[selector!=i,]
    eval.data <- orig.data[selector==i,]
    weights.subset <- weights[selector != i]

# get the current model details

    gbm.x <- model.list[[i]]$gbm.call$gbm.x
    n.preds <- length(gbm.x)
    these.pred.names <- model.list[[i]]$gbm.call$predictor.names
    contributions <- model.list[[i]]$contributions

# get the index number in pred.names of the last variable in the contribution table

    last.variable <- match(as.character(contributions[n.preds,1]),these.pred.names)
    gbm.new.x <- gbm.x[-last.variable]

# and keep a record of what has been dropped

    last.variable <- match(as.character(contributions[n.preds,1]),predictor.names)
    drop.count[last.variable,i] <- n.steps

    model.list[[i]] <- eval(parse(text=gbm.call.string))  # create a fixed size object

    u_i <- eval.data[,gbm.y]
    y_i <- predict.gbm(model.list[[i]],eval.data,n.trees,"response")

    deviance <- round(calc.deviance(u_i,y_i, family = family, calc.mean = TRUE),4)

# calculate difference between intial and new model by subtracting new from old because we want to minimise deviance

    dev.results[n.steps,i] <- round(deviance - original.deviances[i] ,4)

    }

  if (auto.stop){ # check to see if delta mean is less than original deviance error estimate

    delta.mean <- mean(dev.results[n.steps,])

    if (delta.mean < (alpha * original.deviance.se)) {
      n.drops <- n.drops + 1
      dev.results <- rbind(dev.results, rep(0,n.folds))
      }
    }
  n.steps <- n.steps + 1
  }

# now label the deviance matrix

  dimnames(dev.results) <- list(paste("drop.",1:n.drops,sep=""),
   paste("rep.",1:n.folds,sep=""))

# calculate mean changes in deviance and their se

  mean.delta <- apply(dev.results,1,mean)
  se.delta <- sqrt(apply(dev.results,1,var))/sqrt(n.folds)

###########################

  if (plot) {
    y.max <- 1.5 * max(mean.delta + se.delta)
    y.min <- 1.5 * min(mean.delta - se.delta)
    plot(seq(0,n.drops),c(0,mean.delta),xlab="variables removed",
      ylab = "change in predictive deviance",type='l',ylim=c(y.min,y.max))
    lines(seq(0,n.drops),c(0,mean.delta) + c(0,se.delta),lty = 2)
    lines(seq(0,n.drops),c(0,mean.delta) - c(0,se.delta),lty = 2)
    abline(h = 0 , lty = 2, col = 3)
    min.y <- min(c(0,mean.delta))
    min.pos <- match(min.y,c(0,mean.delta)) - 1 # subtract one because now zero base
    abline(v = min.pos, lty = 3, col = 2)
    abline(h = original.deviance.se, lty = 2, col = 2)
    title(paste("RFE deviance - ",response.name," - folds = ",n.folds,sep=""))
  }

# and do a final backwards drop sequence from the original model

  if(verbose) cat("\nnow processing final dropping of variables with full data \n\n") #aks

  gbm.call.string <- paste("try(gbm.fixed(data=orig.data,gbm.x=gbm.new.x,gbm.y=gbm.y,",sep="")
  gbm.call.string <- paste(gbm.call.string,"family=family,learning.rate=lr,tree.complexity=tc,",sep="")
  gbm.call.string <- paste(gbm.call.string,"n.trees = ",n.trees,", site.weights = weights,verbose=FALSE))",sep="")

  n.steps <- n.steps - 1 #decrement by one to reverse last increment in prev loop

  final.model <- gbm.object  # restore the original model and data
  train.data <- orig.data

# and set up storage

  final.drops <- matrix(NA, nrow = start.preds, ncol = 1)
  dimnames(final.drops) <- list(predictor.names,"step")

  for (i in 1:n.steps) {

# get the current model details

    gbm.x <- final.model$gbm.call$gbm.x
    n.preds <- length(gbm.x)
    these.pred.names <- final.model$gbm.call$predictor.names
    contributions <- final.model$contributions

    if(verbose) cat(i,"-",as.character(contributions[n.preds,1]),"\n");flush.console()#AKS

# get the index number in pred.names of the last variable in the contribution table

    last.variable <- match(as.character(contributions[n.preds,1]),these.pred.names)
    gbm.new.x <- gbm.x[-last.variable]

# and keep a record of what has been dropped

    last.variable <- match(as.character(contributions[n.preds,1]),predictor.names)
    final.drops[last.variable] <- i

    final.model <- eval(parse(text=gbm.call.string))  # create a fixed size object

  }

#and then the corresponding numbers

  removal.list <- dimnames(final.drops)[[1]]
  removal.list <- removal.list[order(final.drops)]
  removal.list <- removal.list[1:n.drops]

  removal.numbers <- rep(0,n.steps)

# construct predictor lists to faciliate final model fitting

  for (i in 1:n.steps) {
    removal.numbers[i] <- match(removal.list[i],predictor.names)
    pred.list[[i]] <- orig.gbm.x[0-removal.numbers[1:i]]
    names(pred.list)[i] <- paste("preds.",i,sep="")
  }

  deviance.summary <- data.frame(mean = round(mean.delta,4), se = round(se.delta,4))

  final.drops <- data.frame("preds" = dimnames(final.drops)[[1]][order(final.drops)],
     "order" = final.drops[order(final.drops)])

  return(list(deviance.summary = deviance.summary,
    deviance.matrix = dev.results, drop.count = drop.count,
    final.drops = final.drops, pred.list = pred.list,
    gbm.call = gbm.call))

}

"gbm.fixed" <-
function (data,                        # the input dataframe
  gbm.x,                               # indices of the predictors in the input dataframe
  gbm.y,                               # index of the response in the input dataframe
  tree.complexity = 1,                 # the tree depth - sometimes referred to as interaction depth
  site.weights = rep(1, nrow(data)),   # by default set equal
  verbose = TRUE,                      # to control reporting
  learning.rate = 0.001,               # controls speed of the gradient descent
  n.trees = 2000,                      # default number of trees
  train.fraction = 1,
  bag.fraction = 0.5,                  # varies random sample size for each new tree
  family = "bernoulli",                # can be any of bernoulli, poisson, gaussian, laplace - note quotes
  keep.data = FALSE,                   # keep original data
  var.monotone = rep(0, length(gbm.x)) # constrain to positive (1) or negative monontone (-1)
  )
{
#
# j leathwick, j elith - 6th May 2007
#
# version 2.9 - developed in R 2.0
#
# calculates a gradient boosting (gbm)object with a fixed number of trees
# with the number of trees identified using gbm.step or some other procedure
#
# mostly used as a utility function, e.g., when being called by gbm.simplify
#
# takes as input a dataset and args selecting x and y variables, learning rate and tree complexity
#
# updated 13/6/05 to accommodate weighting of sites when calculating total and residual deviance
#
# updated 10/8/05 to correct how site.weights are returned
#
# requires gbm
#
#
  require(gbm)

# setup input data and assign to position one

  dataframe.name <- deparse(substitute(data))   # get the dataframe name

  x.data <- eval(data[, gbm.x])                 #form the temporary datasets
  names(x.data) <- names(data)[gbm.x]
  y.data <- eval(data[, gbm.y])
  sp.name <- names(data)[gbm.y]


  assign("x.data", x.data, pos = 1)             #and assign them for later use
  assign("y.data", y.data, pos = 1)

# fit the gbm model

  z1 <- unclass(Sys.time())

  gbm.call <- paste("gbm(y.data ~ .,n.trees = n.trees, data=x.data, verbose = F, interaction.depth = tree.complexity,
    weights = site.weights, shrinkage = learning.rate, distribution = as.character(family),
    var.monotone = var.monotone, bag.fraction = bag.fraction, keep.data = keep.data)", sep="")

  if (verbose) {
    print(paste("fitting gbm model with a fixed number of ",n.trees," trees for ",sp.name,sep=""),quote=FALSE) }

  gbm.object <- eval(parse(text = gbm.call))

  best.trees <- n.trees

#extract fitted values and summary table

  fitted.values <- predict.gbm(gbm.object,x.data,n.trees = n.trees,type="response")
  gbm.summary <- summary(gbm.object,n.trees = n.trees, plotit = FALSE)

  y_i <- y.data
  u_i <- fitted.values

  if (family == "poisson") {
    deviance.contribs <- ifelse(y_i == 0, 0, (y_i * log(y_i/u_i))) - (y_i - u_i)
    resid.deviance <- 2 * sum(deviance.contribs * site.weights)
    residuals <- sqrt(abs(deviance.contribs * 2))
    residuals <- ifelse((y_i - u_i) < 0, 0 - residuals, residuals)

    u_i <- sum(y.data * site.weights) / sum(site.weights)
    deviance.contribs <- ifelse(y_i == 0, 0, (y_i * log(y_i/u_i))) - (y_i - u_i)
    total.deviance <- 2 * sum(deviance.contribs * site.weights)
  }

  if (family == "bernoulli") {
    deviance.contribs <- (y_i * log(u_i)) + ((1-y_i) * log(1 - u_i))
    resid.deviance <- -2 * sum(deviance.contribs * site.weights)
    residuals <- sqrt(abs(deviance.contribs * 2))
    residuals <- ifelse((y_i - u_i) < 0, 0 - residuals, residuals)

    u_i <- sum(y.data * site.weights) / sum(site.weights)
    deviance.contribs <- (y_i * log(u_i)) + ((1-y_i) * log(1 - u_i))
    total.deviance <- -2 * sum(deviance.contribs * site.weights)
  }

  if (family == "laplace") {
    resid.deviance <- sum(abs(y_i - u_i))
    residuals <- y_i - u_i
    u_i <- mean(y.data)
    total.deviance <- sum(abs(y_i - u_i))
  }

  if (family == "gaussian") {
    resid.deviance <- sum((y_i - u_i) * (y_i - u_i))
    residuals <- y_i - u_i
    u_i <- mean(y.data)
    total.deviance <- sum((y_i - u_i) * (y_i - u_i))
  }

  if (verbose) {
    print(paste("total deviance = ",round(total.deviance,2),sep=""),quote=F)
    print(paste("residual deviance = ",round(resid.deviance,2),sep=""),quote=F)}

# now assemble data to be returned

  z2 <- unclass(Sys.time())
  elapsed.time.minutes <- round((z2 - z1)/ 60,2)  #calculate the total elapsed time

  gbm.detail <- list(dataframe = dataframe.name, gbm.x = gbm.x, predictor.names = names(x.data),
    gbm.y = gbm.y, reponse.name = names(y.data), family = family, tree.complexity = tree.complexity,
    learning.rate = learning.rate, bag.fraction = bag.fraction, cv.folds = 0, n.trees = n.trees, best.trees = best.trees,
    train.fraction = train.fraction, var.monotone = var.monotone, date = date(), elapsed.time.minutes = elapsed.time.minutes)

  gbm.object$gbm.call <- gbm.detail
  gbm.object$fitted <- fitted.values
  gbm.object$residuals <- residuals
  gbm.object$contributions <- gbm.summary
  gbm.object$self.statistics <- list(null.deviance = total.deviance, resid.deviance = resid.deviance)
  gbm.object$weights <- site.weights

  rm(x.data,y.data, pos=1)           #finally, clean up the temporary dataframes

  return(gbm.object)
}


# Interpret command line argurments #
# Make Function Call #
if(Debug==F){
    Args     <- commandArgs(T)
    print(Args)
    for (arg in Args) {
    	print(arg)
    	argSplit <- strsplit(arg, "=")
    	argSplit[[1]][1]
    	argSplit[[1]][2]
    	"hello"
    	if(argSplit[[1]][1]=="c") csv <- argSplit[[1]][2]; "hello"
    	if(argSplit[[1]][1]=="o") output <- argSplit[[1]][2]
    	if(argSplit[[1]][1]=="rc") responseCol <- argSplit[[1]][2]
    }
	print(csv)
	print(output)
	print(responseCol)
	
    fit.brt.fct(ma.name=csv,
		tif.dir=NULL,
		output.dir=output,
		response.col=responseCol,
		test.resp.col="response",make.p.tif=T,make.binary.tif=T,
		simp.method="cross-validation",debug.mode=T,responseCurveForm="pdf",tc=NULL,n.folds=3,ma.test=NULL,alpha=1,script.name="brt.r",
		learning.rate =NULL, bag.fraction = 0.5,prev.stratify = TRUE, model.family = "bernoulli", max.trees = NULL)
}
if(Debug==T){
    if(batch.mode==T){
        for(g in 1:length(ma.names)){
            out <- fit.brt.fct(ma.names[g],tif.dir,output.dir=output.dir,make.p.tif=make.p.tif,test.resp.col=test.resp.col,make.binary.tif=make.binary.tif,
              simp.method=simp.method,debug.mode=debug.mode,tc=tc,response.col=response.col,n.folds=n.folds,ma.test=test.names[g],alpha=2)
            if(!is.null(test.names)){
                auc.output <- try(make.auc.plot.jpg(out$dat$ma.test$ma,pred=predict.gbm(out$mods$final.mod,out$dat$ma.test$ma,
                      out$mods$final.mod$target.trees,type="response"),plotname=paste(out$dat$bname,"_test_auc_plot.jpg",sep=""),
                      modelname="BRT"),silent=T)

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
         out <- fit.brt.fct(ma.name,tif.dir,output.dir=output.dir,make.p.tif=make.p.tif,test.resp.col=test.resp.col,make.binary.tif=make.binary.tif,
              simp.method=simp.method,debug.mode=debug.mode,tc=tc,response.col=response.col,n.folds=n.folds,ma.test=test.name)
         if(!is.null(test.name)){
              auc.output <- try(make.auc.plot.jpg(out$dat$ma.test$ma,pred=predict(out$mods$final.mod,newdata=out$dat$ma.test$ma,type='response'),
                  plotname=paste(out$dat$bname,"_test_auc_plot.jpg",sep=""),modelname="BRT"),silent=T)
              }
         }
    #write.csv(data.frame(pres_abs=out$dat$ma.test$ma[,1],pred=predict.gbm(out$mods$final.mod,out$dat$ma.test$ma,
    #    out$mods$final.mod$target.trees,type="response")),"auc test data.csv",row.names=F)
    #write.csv(out.table,"./reanalysis/brt_test_results_alpha2b.csv")
    }


