
#--------------------------------------------------------------------------------
# Predictive.Ensemble.Modeling.Library
# 1.22.09
# DMF
#
#
#--------------------------------------------------------------------------------
#
# One Stop Shopping for BDT's
# Bigger vision - this is a flexible bootstrap CV wrapper
# for predictive modeling.
#
#
# 3.11.09 - Added New STEM Spatial Design 
# 	Tested standalone
# 
#	Tested with Demo - performed favorably on NE Norcar data 
# 	compared with BDT!!! Bernoulli - 
# 	spatial design - no temporal segmentation.  
#
#New Strategy for saving smaller rpart objects. 
# ----------------------------------------------------
#Sucess = saving minimal structure for making predicitons 
#        & CALCULATING diagnostics (VI's)
#Test: 
#Pass data frame to predict function. 
#How big are the terms? 
#Can they be left out and still make preds & VI's?
#--------------------------------------
#      ans <- list(frame = frame, where = where, call = call, 
#            terms = Terms, cptable = t(rp$cptable), splits = splits, 
#            method = method, parms = init$parms, control = controls, 
#            functions = functions)
#      class(ans) <- "rpart"
#
#
# 4/15
# -------
# ** sample.ST.ensemble - fixed temporal index problem
# ** predict.ST.ensemble - fixed temporal index problem
# 					** fixed response factor input
# ==> This means that the ST ensemble is finally doing 
# what I THOUGHT it was doing all the time. 
# ** reduced memory footprint & speed up run times
# ==> Run very many more small models - improving 
# ensemble depth. 
#
# 4.15 TO DO LIST: 
# -------------------------
# ** Batch processing for Partial Calculations
# ** I need to figure out some logic to deal with possibilites
# 	of region-seasons that do not contain any data, or 
# 	perhaps do not contain any sampled training data. 
# 		this will affect sample.ST.ensemble 
# 		create.ST.ensemble - one option may be to simply exclude them
# 		and fit.ST.ensemble & predict.ST.ensemble
# ** Need to make location information names and parameters 
# 	consistent across all ST.ensmble functions
# 		This means do not assume that train.data$X$x & $X$y are there!!
# ** sample.ST.ensemble
# 		** missing logic for sampling options
# 		** currently writing $X.loc to the GLOBAL instance 
# 			of ensemble.par.list. This is BAD - and unnecessary
# 			need to clean logic. 
#
#
#
# predict.ST.ensemble - Assumes existance of 
# 	prediction.design$x,  $y,  & $JDATE
# 
#
#--------------------------------------------------------------------------------



# ---------------------------------------------------------------------
# ---------------------------------------------------------------------
# FUNCTION: Fit and Save BDT Ensemble
# ---------------------------------------------------------------------
# ---------------------------------------------------------------------
# D.Fink
# Cornell Lab of Ornithology
# Department of Statistical Science
# 7.14.08
#
# Description
# -------------
#
# Usage:
# --------
#
# Arguments:
# -----------
# y 		response vector
# X			matrix/data.frame of predictors only!!!
#       		one predictor per column. Describe how predictors enter model
#       		as main effects and interactions of smooth & nonsmooth funcitional
#       		forms. Invariant to Monotone transformations.etc.
# ensemble.weights = from ben's experience rpart likes variances (as 
# opposed to sd or reciprocals of ...)
# it looks like gam likes st.dev. 
#
# Value
# --------
#  ib.sample.index = logical matrix dimension (n x bs.trials)
#                  indicates training samples for each ensemble
#
# Details
# --------
#
# TO DO List
# -------------
#
# 3.25.09 Added code to pass weights to rpart
#
# 4.14.09
# -------------
# Modified code to save oob. & ib.sample.index's 
# 	** in batches
# 	** to separate file sets
# This in order to reduce the memory overhead. 
# Both of these matrices were being stored as 
# size = N x (# of ensemble model). 
# Moreover, I almost never use this information for predictions. 
# So, I am going to write it to disk , just in case. 
# Meanwhile - The index file has been modified to hold:
#	# * Number of models in ensemble 
#	# * ensemble resp.family
#	# * realized.sample.par
# and I might add the ensemble.par.list for good measure. 
#
#
# **** I NEED LOGIC TO CHECK FOR "NULL" SAMPLES!!!
#
#
# ---------------------------------------------------------------------
# ---------------------------------------------------------
# Design Notes:
#
# * Individual-Model Paramters will pass through, since cant anticipate
#           how to handle parameters from other models!!!
# * Ensemble Parameters will be passed with a dedicated list name
#   since this is something that I CAN control
# ---------------------------------------------------------
fit.ensemble <- function(
    train.data,
    resp.family,
    RNG.seed = NULL,
    #sample.ensemble.function,
    ensemble.par.list=NULL,
    filename,
    ensemble.weights=NULL,
    block.save.size=100,  # (training sample size x block.save.size ) 
    # Model Parameter Pass Through
    ...){
    # ---------------------------------------------------------
    # Inits
    # ---------------------------------------------------------
    function.call <- match.call()
    ib.sample.index <- NULL
    oob.sample.index <- NULL
    realized.sample.par <- NULL
    n <- length(train.data$y)
    ensemble.trials <- ensemble.par.list$n.ensemble.models
    # -----------------------------------------------
    if (resp.family=="gaussian") bs.method <- "anova"
    if (resp.family=="bernoulli") bs.method <- "class"
    if (resp.family=="multiclass") bs.method <- "class"
    if (resp.family=="poisson") bs.method <- "poisson"
    # ---------------------------------------------------------
    # Bootstrap Samples
    # ---------------------------------------------------------
    block.number <- 1
    for (iii in 1:ensemble.trials) {
	# -------------------------------------
	# RNG.seed parameter
	# ------------------------------------------------
	if (iii==1 & !is.null(RNG.seed)) set.seed(RNG.seed)
	# --------------------------

	sample.data <- ensemble.par.list$sample.ensemble.function(
					ensemble.model.number = iii,
				    ensemble.data = train.data, 
				    ensemble.par.list = ensemble.par.list,
				    diagnostic.plot = FALSE) 
	
			#cat("fe: iii,",iii, " length(yyy)=", length(sample.data$y),
			#	sum(is.na(sample.data$y)) "\n")
			#cat("fit.ensemble: iii,",iii, " sum(is.na(yyy))=", sum(is.na(sample.data$y)), "\n")
			#if (length(sample.data$y) == sum(is.na(sample.data$y)) ){
			#	print(sample.data$y)
			#}	
	# ---------------------------------------------
	# Fit Ensemble Member with sampled data
	# ---------------------------------------
        # First check for weights
	if (is.null(ensemble.weights)) {
	   f.rpart <- try(rpart( yyy ~ .,
                 data= data.frame(yyy=sample.data$y,sample.data$X),
				 method=bs.method,
				 ...))	
	   # If there is an error, try it again
	   if (class(f.rpart) == "try-error") {
	      cat("fit.ensemble: rpart error \n")
	      f.rpart <- try(rpart( yyy ~ .,
				    data= data.frame(yyy=sample.data$y,sample.data$X),
				    method=bs.method,
				    ...))	
	   }				
	}
        else { 
	     f.rpart <- try(rpart( yyy ~ .,
				data= data.frame(yyy=sample.data$y,sample.data$X),
				weights= ensemble.weights[sample.data$ib.num.ind],
				method=bs.method,
				...))
	     # If there is an error, try it again
	     if (class(f.rpart) == "try-error") {
	     	cat("fit.ensemble: rpart error \n")
		f.rpart <- try(rpart( yyy ~ .,
				      data= data.frame(yyy=sample.data$y,sample.data$X),
				      weights= ensemble.weights[sample.data$ib.num.ind],
				      method=bs.method,
				      ...))	
	     }			
        }
	# ----------------------
	# Save Ensemble Model
	#-----------------------
	num.txt <- formatC(iii, format="fg", width=6)
	num.txt <- chartr(" ","0",num.txt)
	temp.filename <- paste(filename,".",num.txt,".RData",sep="")
	if (iii == 1) save(f.rpart,  file=temp.filename)
	if (iii > 1) {
		rpart.parts <-
		list( frame = f.rpart$frame,
			where = f.rpart$where, # - vector
			splits= f.rpart$splits, #- numeric matrix
			cptable = f.rpart$cptable)
		if (sum(names(f.rpart) == "csplit") > 0)
			rpart.parts$csplit <- f.rpart$csplit
		save(rpart.parts,  file=temp.filename)
	}
	# --------------------------------
	# Save sampled data information
	# --------------------------------
	ttt.logical <- rep(FALSE, n)
	ttt.logical[sample.data$oob.num.ind] <- TRUE
	oob.sample.index <- cbind(oob.sample.index, ttt.logical)
	ttt.logical <- rep(FALSE, n)
	ttt.logical[sample.data$ib.num.ind] <- TRUE
	ib.sample.index <- cbind(ib.sample.index, ttt.logical)
	# ---------------- 
	realized.sample.par <- cbind(realized.sample.par, sample.data$realized.par)

    	# ----------------------------------------------------
    	# Block Save of Sampling Index Information 
    	# ----------------------------------------------------
    	if ( round(iii/block.save.size) == (iii/block.save.size)) { 
	    return.list <- list(oob.sample.index = oob.sample.index,
	                        ib.sample.index = ib.sample.index,
	                        realized.sample.par = realized.sample.par,
	                        function.call = function.call)
	    temp.filename <- paste(filename,".bs.sampling.index.", block.number,".RData",sep="")
	    save(return.list, file=temp.filename)
	    # -------------------------------
	    # Reinitialize Results 
	    # -------------------------------
	    ib.sample.index <- NULL
	    oob.sample.index <- NULL
	    # Next block number
	    block.number <- block.number + 1
	}                                                         
    }# End for(iii) :Bootstrap

    # ---------------------------------------------------------
    # ----------------------------------------------------
    # Final Block Save of Sampling Index Information 
    # ----------------------------------------------------
    if (!is.null(oob.sample.index)){
	    return.list <- list(oob.sample.index = oob.sample.index,
	        ib.sample.index = ib.sample.index,
	        realized.sample.par = realized.sample.par,
	        function.call = function.call)
	    temp.filename <- paste(filename,".bs.sampling.index.",
	    			   block.number,".RData",sep="")
	    save(return.list, file=temp.filename)
            rm(ib.sample.index) 
    	    rm(oob.sample.index)
	    ## KFW gc()
    }                                       
    # ---------------------------------------------------------
    # Return Value
    # ** I need to return enough information to act as a
    #    handle to the ensemble for prediction, diagnostics, etc.
    # ** Save all this information as a header/providence
    #    index file with the ensemble itself
    # ---------------------------------------------------------
    rm(rpart.parts)
    rm(num.txt)
    return.list <- list(realized.sample.par = realized.sample.par,
		   			    resp.family=resp.family,
					    RNG.seed = RNG.seed,
					    block.save.size=block.save.size,
					    function.call = function.call)
    temp.filename <- paste(filename,".ensemble.index.RData",sep="")
    save(return.list, file=temp.filename)

    return(return.list)
}# End FUNCTION
# ---------------------------------------------------------





# ---------------------------------------------------------------------
# This is a simple function to compute
# OOB Predictions,
# SD,
# OOB Matrix,
# * Handle NA's for samples that have not been predited
# OOB. This is more of a concern when the number of
# bootstraps is small.
#
#
# OUTPUT:
#        count = (n x 1) vector count of BS reps for each obs
#        mean =  (n x 1) vector count of BS reps for each obs
#        sd = OOB.sd,
#        matrix = OOB.pred.index)
#
#      predict.oob.bdt
# ---------------------------------------------------------------------
#predict.oob.bdt <- function(filename, X.train){
## ---------------------------------------------------------------------
#  # ---------------------------------------------------------
#  # Inits
#  # ---------------------------------------------------------
#    temp.filename <- paste(filename,".ensemble.index.RData",sep="")
#    load(file=temp.filename) #return.list
#  # ---------------------------------------------------------
#  # OOB Predictions - Means & SD's
#  # ---------------------------------------------------------
#      #KISS-Predict entire training set, then extract OOB preds
#      training.pred <- predict.bdt(
#                      filename = filename,  #model specific stuff stored here
#                      prediction.design=X.train)
#      OOB.pred.index <- training.pred$matrix
#      OOB.pred.index[return.list$ib.sample.index==TRUE] <- NA
#      # -------------------
#      OOB.count <- apply(!return.list$ib.sample.index, 1, sum)
#      OOB.pred <- apply(OOB.pred.index, 1, mean, na.rm = TRUE)
#      OOB.sd <-  apply(OOB.pred.index, 1, sd, na.rm = TRUE)
#  # ---------------------------------------------------------
#  # Return Value
#  # ---------------------------------------------------------
#    return.list <- list(
#        count = OOB.count,
#        mean = OOB.pred,
#        sd = OOB.sd,
#        matrix = OOB.pred.index)
#    return(return.list)
## ---------------------------------------------------------
#}# END OOB FUNCTION
## ---------------------------------------------------------------------
## ---------------------------------------------------------------------
#

# -------------------------------------------------------------------
# -------------------------------------------------------------------
# Variable Importances & Summaries
# DT-rpart Specific Diagnostics
# -------------------------------------------------------------------
# -------------------------------------------------------------------
# 	var.imp[ ,1]
#		a vector of all the variable importances measured as the empirical
#		improvement in the splitting criterion. Importances are in the
#		same order as the columns in X (design matrix).
#		See above notes for more info.
# 	var.imp[ ,2]
#		variable importance weighted by height in tree
# 	var.imp[ ,3]
#		variable importance weighted by support - number of data pts affected by
#          split. I need to look at code
#
#	leaf.count = # of terminal leafs
# 	ave.leaf.obs = average number of observations per leaf
# 	min.leaf.obs = minimum number of observation in leaf
# 					(this value is controled by min.bucket too!)
#
# -------------------------------------------------------------------
rpart.ensemble.diagnostics <- function(
        filename, 
	ensemble.par.list,
        X,
        ensemble.index=NULL){
# -------------------------------------------------------------------

   # ---------------------------------------------------------
   # Inits
   # ---------------------------------------------------------

   bs.trials <- ensemble.par.list$n.ensemble.models
   # -------------------------------------------------------------------
   #    ** I can pull out the number of predictors
   #    used in the rpart ensemble from the files that
   #    are saved. Then I can remove X.train from the parameter list
   # -------------------------------------------------------------------
    # Results
    # ----------
    var.imp1 <- matrix(0,NCOL(X), bs.trials)
    var.imp2 <- matrix(0,NCOL(X), bs.trials)
    var.imp3 <- matrix(0,NCOL(X), bs.trials)
    leaf.count <- rep(0,bs.trials)
    ave.leaf.obs  <- rep(0,bs.trials)
    min.leaf.obs  <- rep(0,bs.trials)
    # ----------------------------------------------------------
    # Load First Ensemble Model
    # -----------------------------------------------------------
    iii <- 1
    num.txt <- formatC(iii,format="fg", width=6)
    num.txt <- chartr(" ","0",num.txt)
    temp.filename <- paste(filename,".",num.txt,".RData",sep="")
    load( file=temp.filename)
    # Save ensemble rpart.object stub
    ttt.rpart <- f.rpart
    if (is.null(ensemble.index)) ensemble.index <- 1:bs.trials
    # ----------------------------------------------------------
    # Loop over Ensemble.Index
    #       KISS - but not the most efficient programming
    # -----------------------------------------------------------
    for (iii in 1:length(ensemble.index)){
        # ----------------------------------------------------------
        # Load/Construct rpart.object
        # -----------------------------------------------------------
        f.rpart <- ttt.rpart
        if (ensemble.index[iii]!=1){
            num.txt <- formatC(ensemble.index[iii],format="fg", width=6)
      	    num.txt <- chartr(" ","0",num.txt)
            temp.filename <- paste(filename,".",num.txt,".RData",sep="")
            load( file=temp.filename)  #rpart.parts
            # Reassemble f.rpart from ttt.rpart stub
            # ----------------------------
            f.rpart$frame   <- rpart.parts$frame
            f.rpart$where   <- rpart.parts$where
            f.rpart$splits  <- rpart.parts$splits
            f.rpart$cptable <- rpart.parts$cptable
            if (sum(names(rpart.parts) == "csplit") > 0)
              f.rpart$csplit <- rpart.parts$csplit
        }
	# -------------------------------------------------------------------
 	# DT-rpart Specific Variable Importance Measures
	# -------------------------------------------------------------------
	# Split Variables = row.names(d.rpart$split)
	# Empirical Improvement = Change in Deviance= d.rpart$split[,3]
	# var.imp is a vector of all the variable importances in the
	# same order as the columns in X (design matrix)
	# -------------------------------------------------------------------
	# sort out info about leaf nodes (I just want splits!)
	dnodes <- f.rpart$frame[ f.rpart$frame[ ,1] != "<leaf>", ]
	ncompete <- dnodes[,7]
	nsurrogate <- dnodes[,8]
	nsupport <- dnodes[, 2]  # no. of pts affected by split
	nheight <- as.numeric(row.names(dnodes)) # height in pascal's triange
	nheight <- floor(log2(nheight)) + 1
	split.index <- 1 # initialize split index
	# variable look-up table
	var.table <- data.frame(pos=seq(1:NCOL(X)), varname=names(X))
	# add "<leaf>" level to var.table$varname so that var.index works
	levels(var.table$varname) <- c(levels(var.table$varname),"<leaf>")
	if (!is.null(f.rpart$split)){
  	   # Loop through all splits (rows)
  	   for (ii in 1:NROW(dnodes)){
  	       # ID split predictor
               # --------------------------------------------------
               # Summer & Fall 2007
               # Generating error number of levels in the factor is different
               # But I not understand exactly when this error is generated
               # so I dont  know why it occurrs!
               # ---------------------------------------------------
  		
  		var.index <- var.table[as.character(dnodes[ii,1]) == as.character(var.table$varname) , 1]
  		# extract & store improvement in empirical purity from split frame
  		# Use twice emprical improvement to get actual deviance for entropy splitting rule
  		var.imp1[var.index,iii] <- var.imp1[var.index,1] + 2*f.rpart$split[split.index,3]
  		# update current row index in d.rpart$split
  		split.index <- split.index + ncompete[ii] + nsurrogate[ii]+1
  		# variable importance weighted by height in tree
  		var.imp2[var.index,iii] <- var.imp2[var.index,2] + nheight[ii]
  		# variable importance weighted by support
  		var.imp3[var.index,iii] <- var.imp3[var.index,3] + nsupport[ii]
  	     } #endfor ii
       } #end if is.null
	

       # ----------------------------------------------------------
       # 10.2.07
       # I need information on ensemble trees to understand laplacian
       # smoothing.
       #	leaf.count = # of terminal leafs
       # 	ave.leaf.obs = average number of observations per leaf
       # 	min.leaf.obs = minimum number of observation in leaf
       # 					(this value is controled by min.bucket too!)
       # ----------------------------------------------------------
       is.leaf.ind <- (f.rpart$frame$var == "<leaf>")
       leaf.count[iii] <- sum(is.leaf.ind)
       ave.leaf.obs[iii] <- mean(f.rpart$frame$n[is.leaf.ind])
       min.leaf.obs[iii] <- min(f.rpart$frame$n[is.leaf.ind])
       # -------------------------------------------------------------------
    } #end ensemble.index

    # ----------------------------------------------------------
    # Return Prediction Matrix
    # -----------------------------------------------------------
    return.list <- list(var.imp1 = var.imp1,
            	   	var.imp2 = var.imp2,
            		var.imp3 = var.imp3,
            		leaf.count = leaf.count,
            		ave.leaf.obs = ave.leaf.obs,
            		min.leaf.obs=min.leaf.obs)
    return(return.list)
# ---------------------------------------------------------
}# End FUNCTION
# ---------------------------------------------------------


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Variable Importance Barplot
# -----------------------------------------------------------------------------
# Daniel Fink
#
#
# Description
# -----------------
# This function ....
# I need to describe what the measure of relative variable importance
# is and how it is aggregated over the ensemble.
# * key assumptions
# * uses, strengths & weaknesses
#
#
# Input
# ----------
#	 vi = (n x 1) numeric vector of VI point estimates
#       where n is the number of Variables
#       barplot
#  vi.mat = ( n x bs.trials) numeric matrix of VI estimates
#           one set of estimates per column.
#           Variabliltiy in estimates plotted with boxplot
# 	 plot.it=FALSE
#
# Output
# ----------
# A plot may be produced or the predictive performances for train & test
# returned.
#
# Notes:
# ---------
#
# Further Development:
# ----------------------------
# ** common parameter names and calling proceedures for
# 	all functions
# ** return variable importances and names as data.frame
# -----------------------------------------------------------------------------
plot.vi.bdt <- function(
	vi=NULL,
        vi.mat=NULL,
        predictor.names,
	max.vars = 25,
	file.name = NULL,
        plot.width = 600,
        plot.height = 800 ){
	# --------------------------------------------------------------
	# VI Point Estimate Plot
	# --------------------------------------------------------------
	if (!is.null(vi)) {
    	   # --------------------------------------------------------------
    	   # Assemble Scaled VI & Names
    	   # ---------------------------------------------------------------
    	   ttt <- data.frame(Predictor = predictor.names, Deviance = vi/sum(vi)*100)
    	   # Re-order ttt in terms of descending Deviance
    	   ttt.ind <- order(ttt[,2],decreasing=TRUE)
    	   ttt <- ttt[ttt.ind, ]
    	   ttt$Predictor <- as.character(ttt$Predictor)
    	   # ---------------------------------------------------
    	   # Save image to disk
    	   # ---------------------------------------------------
    	   if (!is.null(file.name)) {
      	      png(file=file.name, 
              	  bg="white",
            	  width=plot.width,
    	    	  height=plot.height) 
    	   }
    
	  # ---------------------------------------------------
    	  # Barplot
    	  # ---------------------------------------------------
    	  xmax <- max(ttt$Deviance)	# scale max bar length
    	  x.stretch <- 1.4		# scale max bar length
    	  nbars <- max.vars		# number of bars to plot
    	  bar.length <- ttt$Deviance
    	  bar.names <- ttt$Predictor
    	  tcol <- rainbow(nbars, start = 3/6, end = 4/6)
    	  tcol <- tcol[nbars:1]   # reorder from dark to light colors
    	  barplot(bar.length[1:nbars],
		  horiz=TRUE,
    		  xlim=c(0,(xmax*x.stretch)),
    		  xlab="Relative Importance",
   		  col = tcol,
    		  axes=F)
    	  axis(1)
    	  for (ii in 1:nbars) {
    	      text( bar.length[ii] + 1, 
              	    1.2*(ii-1) + .75,
    	      	    as.character(bar.names[ii]), 
	      	    cex=0.75, 
	      	    pos=4)
    	  }
    	  title(main="Ensemble Averages")
    	  # ---------------------------------------------------
    	  # Save image to disk
    	  # ---------------------------------------------------
    	  if (!is.null(file.name)) dev.off()
      }

      # --------------------------------------------------------------
      # VI Estimates BoxPlot
      # --------------------------------------------------------------
      if (!is.null(vi.mat)) {
      	 mean.vi <- apply(vi.mat, 1, mean)
  	 mean.index <- order(mean.vi, decreasing=TRUE)
  	 mean.vi <- mean.vi[mean.index]
  	 vi.mat <- vi.mat[mean.index,]/sum(mean.vi)*100
  	 mean.vi <- mean.vi/sum(mean.vi)*100
  	 predictor.names <- predictor.names[mean.index]
  	 # --------------------
  	 nbars <- max.vars
  	 mean.vi <- mean.vi[c(1:nbars)]
  	 predictor.names <- predictor.names[c(1:nbars)]
  	 vi.mat <- vi.mat[c(1:nbars), ]
  	 ttt.stack <- stack(data.frame(vi.mat))
  	 ttt.stack <- data.frame(ttt.stack, var=c(1:nbars))
  	 # --------------------
 	 xmax <- max(ttt.stack[,1])		# scale max bar length
	 x.stretch <- 1.3				# scale max bar length
	 bar.length <- mean.vi
	 bar.names <- predictor.names
	 tcol <- rainbow(nbars, start = 3/6, end = 4/6)
	 tcol <- tcol[nbars:1]   # reorder from dark to light colors
	 # ---------------------------------------------------
	 # Save image to disk
	 # ---------------------------------------------------
	 if (!is.null(file.name)) {
		png(file=file.name, bg="white",
			width=plot.width,
			height=plot.height) 
	 }

	 # --------------

	 boxplot(-values ~ as.factor(var),
			data = ttt.stack,
			horizontal=TRUE,
			outline=FALSE,
			#xlim=c(0,(nbars)),
			ylim=c(-(xmax*x.stretch),(.5*xmax)),
			xlab="Relative Importance",
			col = tcol,
			axes=F)
	 axis(1)
	 for (ii in 1:nbars) {  #bar.length[ii]
			#text( ttt.stack$values[ii] + 1, 1.2*(ii-1) + .75,
			text( 0.5 , 1.*(ii-1) + 1,
			       as.character(bar.names[ii]), cex=1.0, pos=4)
	 }
	 title(main="Ensemble BoxPlot")
         # ------------
    	 # ---------------------------------------------------
    	 # Save image to disk
    	 # ---------------------------------------------------
      	 if (!is.null(file.name)) dev.off()
      } # end vi.mat
} # end function


# -------------------------------------------------------------------
# create.pd.grid - Function to Create List of Prediction Grid(s)
# -------------------------------------------------------------------
# based on plot.gbm!
# Input
# 	XX - DTM Design matrix
#		arguments that are lists
#		# --------------------------
#	i.var.list = list of i.var vectors
# 		for now- these two arguments must be scalars
#	continuous.resolution = list/vector of cont.resolutions
#
# Output
#  	for each of member of the list, the following objects will be
# 	produced:
#	pd.grids
#
# Notes:
# -------
# There may be times when we actually want to see what the
# predictions are for NA's - I have left this out, as an extra item.
# I need to document how I am handling NA's.
# -------------------------------------------------------------------
# ---------------------------------------------------------------------
create.pd.grid <- function(XX,
			   i.var.list,
			   continuous.resolution,
			   na.flag=NULL) {
   # Cycle through elements of list
   # --------------------------------
   pd.grids <- vector(mode="list", length=length(i.var.list))
   for (iii in 1:length(i.var.list)){
	i.var <- i.var.list[[iii]]

 	# --------------------------------------------
 	# Check User Input
 	# --------------------------------------------
 	 if (all(is.character(i.var))) {
        i <- match(i.var, names(XX))
        if (any(is.na(i))) {
            stop("i.var.list contains variables that are not used in model",
                i.var[is.na(i)])
        }
        else {
            i.var <- i
        }
   }

   if ((min(i.var) < 1) || (max(i.var) > length(names(XX)))) {
        warning("i.var must be between 1 and ", length(names(XX)))
   }


   # --------------------------------------------
   # Create Prediction Grid
   # --------------------------------------------
   # vector produces a vector of the given length and mode.
   grid.levels <- vector(mode="list", length=length(i.var))
   for (i in 1:length(i.var)) {
       X.vars <- XX[ ,i.var[i]]
       # Check for missing values flag other than "NA"
       # (for ex. I do not want RF 9e30 flag to affect the
       # quantile calculations below
       # ----------------------------------------------
       if (!is.null(na.flag)){
       	  na.ind <- (X.vars == na.flag)
	  # replace with NA's
	  X.vars[na.ind] <- NA
       }

       # ----------------------
       # Integer Predictors
       # ----------------------
       # continuous resolution - use minimum of either
       #  	the range of integers or continuous.resolution
       if (is.integer(X.vars)) {
       	  cont.res <- min((max(X.vars,na.rm=TRUE) - min(X.vars,na.rm=TRUE) + 1), continuous.resolution)
	  grid.levels[[i]] <- seq(min(X.vars,na.rm=TRUE), max(X.vars,na.rm=TRUE), length = cont.res)
	  grid.levels[[i]] <- sort(unique(grid.levels[[i]]))
       }
       # ----------------------
       # Double Predictors
       # ----------------------
       if (is.double(X.vars)) {
            # Sequential Grid
	    # grid.levels[[i]] <- seq(min(XX[ ,i.var[i]],na.rm=TRUE),
            #    					max(XX[ ,i.var[i]],na.rm=TRUE),
            #   						length = continuous.resolution)
	    # Grid at Equi-spaced Quantiles
	    prob.seq <- seq(from=0, to=1, length= (continuous.resolution+2))
	    # Remove the endpoints of this sequence
	    prob.seq <- prob.seq[2:(continuous.resolution+1)]
	    grid.levels[[i]] <- quantile(X.vars, probs = prob.seq, na.rm = TRUE)
	    grid.levels[[i]] <- sort(unique(grid.levels[[i]]))
    	} #end double
        # ----------------------
	# Factors: code levels numerically
	# ----------------------
 	if (is.factor(X.vars)) {
	   # What happens with missing values here?
           grid.levels[[i]] <- sort(unique(as.numeric(X.vars) ))
       	} # end factor
     } #end for i: Making grid.levels
     # ----------------------
     pd.grid <- expand.grid(grid.levels)
     names(pd.grid) <- names(XX)[i.var]
     # ----------------------------------------
     pd.grids[[iii]] <- pd.grid
   } # end for i.var.lists

   return(pd.grids)
} # end function



# -------------------------------------------------------------------
# Predict.pd.grid - Function to make Predictions over PD.grids
# -------------------------------------------------------------------
# Input
# 	XX = DTM Design matrix
#	pd.quant.grids = create.pd.grid obejct
# 	nn.sample = # of randomly selected samples from XX
# Output
#  	list of predictions for each member of the create.pd.grid.object
#
#
#
# TO DO: 
# --------------------------------
# 1) 	Add key parameters to output object!!!
#		partial.dependence.list,
#		continuous.resolution = 15,
#		nn.sample = 500
#
# 2)	Need to Recode Categorical predictors
# eg. if BCR was a predictor we would need to recode it 
# to its proper level labels !!!!!
# Currently, BCR is coded as the number of the LEVEL
# xxx.grid[,2] <- levels(train.data$X$BCR)[xxx.grid[,2]]
#
#
# HPM Use:
# 	HPM will need to store and accululate these predictions or
# 	lists of predictions for plotting.
# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------
ensemble.partial.dependence <- function(filename,
	                                ensemble.par.list,
	                                XX,
	                                partial.dependence.list,
	                                continuous.resolution = 15,
	                                nn.sample = 500) { 
   # ------------------------------------------------------------------------------------------------------
   # Inits Formal Parameters
   # ------------------------------------------------------------------------------------------------------
   # Results
   pd.means <- vector(mode="list", length=length(partial.dependence.list))
   pd.matrices <- vector(mode="list", length=length(partial.dependence.list))
   # ------------------------------------------------------------------------------------------------------
   # Compute Partial Dependence Quantile Grids
   # ------------------------------------------------------------------------------------------------------
   pd.quant.grids <- create.pd.grid(XX=XX,
				    i.var.list=partial.dependence.list,
				    continuous.resolution = continuous.resolution)
   # ------------------------------------------------------------------------------------------------------
   # Check Function input
   # ------------------------------------------------------------------------------------------------------
   if (nn.sample > NROW(XX)) {
      nn.sample <- NROW(XX)
   }
   # ------------------------------------------------------------------------------------------------------
   # Random Sample of Data Rows (same sample for all PD elements)
   # ------------------------------------------------------------------------------------------------------
   # Sample without replacement from data rows
   if (nn.sample == NROW(XX)) sample.index <- c(1:NROW(XX))
   if (nn.sample < NROW(XX)) sample.index <- sample(1:NROW(XX), nn.sample, replace = FALSE)

   # ------------------------------------------------------------------------------------------------------
   # Find factors in XX
   # 	Note : I can not use apply b/c XX is class data.frame
   # ------------------------------------------------------------------------------------------------------
   XX.factor.ind <- rep(FALSE, NCOL(XX))
   ttt <- XX[1,] # it is much faster to search a 1D data.frame!
   for (ii in 1:NCOL(XX)) XX.factor.ind[ii] <- is.factor(ttt[,ii])
	
   # Extract an index of column positions for factors (wo zeros!)
   factor.index <- as.numeric(XX.factor.ind)*seq(1,NCOL(XX))
   factor.index <- factor.index[factor.index > 0 ]
   # ------------------------------------------------------------------------------------------------------
   # Loop Over PD list elements
   # ------------------------------------------------------------------------------------------------------
   for (iii in 1:length(pd.quant.grids)){
	# ------------------------------------
	# 1. Expand Quantile Grid into PD Prediction Design
	# 2. BDT Predictions
	# 3. Assemble Results
	# ------------------------------------
	i.var <- match( names(pd.quant.grids[[iii]]), names(XX))
	XX.sample <- XX[sample.index, setdiff(names(XX), names(XX)[i.var]) ]
	pd.grid <- pd.quant.grids[[iii]]
	# ----------------------------
	# NOTE** The size of the PD design = nn.sample * length(pd.grid)
	# If this too large, there should be a loop here that can
	# break this computation into pieces by breaking up
	# nn.sample
	# ----------------------------
	# ------------------------------------------------------------------------------------------------------
	# Construct Partial Dependence Prediction Data Frame
	# 	NOTE: the use of data.matrix converts factors to numerics
	# ------------------------------------------------------------------------------------------------------
	# Stack Randomly Sampled Data Rows
	XX.stack <- kronecker( matrix(1, NROW(pd.grid), 1), data.matrix(XX.sample))
	XX.stack <- as.data.frame(XX.stack)
	names(XX.stack) <- names(XX.sample)
	# Stack Partial Dependence Grids
	pd.stack <- kronecker( data.matrix(pd.grid), matrix(1, nn.sample, 1))
	pd.stack <- as.data.frame(pd.stack)
	names(pd.stack) <- names(pd.grid)
	PD.prediction.frame <- cbind(pd.stack,XX.stack)
	# ------------------------------------------------------------------------------------------------------
	# Reconstruct Factor structure for data.frame
	# ------------------------------------------------------------------------------------------------------
	# XX = original data frame that may include factors
	# PD.prediction.frame = the data.frame currently with numeric
	#	values for all predictors. The prediction data.frame needs
	#	to have the same column/predictor structure as XX
	# ------------------------------------------------
	# 1) Reorder PD.prediction.frame to match XX
	col.order <- match( names(XX), names(PD.prediction.frame))
	PD.prediction.frame <- PD.prediction.frame[,col.order]
	# 2) Convert PD.prediction.frame cols to factors
	for (i in factor.index) {
	    PD.prediction.frame[,i] <- factor(levels(XX[,i])[PD.prediction.frame[,i]], levels=levels(XX[,i]))
	}
	# ------------------------------------------------------------------------------------------------------
	# Ensemble PD Predictions
	# ------------------------------------------------------------------------------------------------------

	ttt.pred <- ensemble.par.list$predict.ensemble.function(
		filename = filename,
		ensemble.par.list = ensemble.par.list, 
		prediction.design= PD.prediction.frame) 		    
		# BDT ensemble mean predictions
	pred.X <- ttt.pred$mean
	pred.X.matrix <- ttt.pred$matrix
	rm(ttt.pred)
	# -----------------------------
	# PD Design Loop would (somewhere?) end here, I think, hmmm
	# -----------------------------
	# --------------------------------------------
	# Ensemble Matrix PD estimates
	# --------------------------------------------
	pdf.grid.matrix <- NULL
	pred.index <- (rep(c(1:NROW(pd.grid)),each=nn.sample))
	for (jjj in 1:NCOL(pred.X.matrix)){
		pdf.grid.matrix <- cbind(pdf.grid.matrix, tapply(pred.X.matrix[,jjj], pred.index, mean,na.rm=T))
	}
	rm(pred.X.matrix)
	# --------------------------------------------
	# Average to get Ensemble average PD estimates
	# --------------------------------------------
	pred.index <- (rep(c(1:NROW(pd.grid)), each=nn.sample))
 	ppp <- tapply(pred.X, pred.index, mean,na.rm=T)
 	# recode pd.grid factors
	f.factor <- rep(FALSE, NCOL(pd.grid))
	for (i in 1:NCOL(pd.grid)) {
		col.index <- match( names(pd.grid)[i], names(XX))
		if (!is.numeric( XX[,col.index] )) {
		   f.factor[i] <- TRUE
		   pd.grid[,i] <- factor(levels(XX[,col.index])[pd.grid[,i]], levels=levels(XX[,col.index]))
		}
	} #end for i 
	# Reassociate pd.grid with predictions
	pdf.grid <- data.frame(pd.grid, pred=ppp)

	# -----------------------------------
	# Store results in PD.list
	# -----------------------------------
	# pd.means = the Partial Dependence Estimate averaged over bags
	# pd.matrices = the PD estimates, one col per bag/model
  	pd.means[[iii]] <- pdf.grid
  	pd.matrices[[iii]] <- pdf.grid.matrix
	#names(pdf.grid)
	#dim(pdf.grid)
   } # end iii

   return(list(pd.quant.grids=pd.quant.grids, pd.means=pd.means, pd.matrices=pd.matrices))
} # end function

# ---------------------------------------------------------
# Summary (TEXT) Function
# ---------------------------------------------------------
summarize.ensemble <- function(model.filename,
              ensemble.par.list,
              train.data,
              test.data=NULL,
              diag.bdt = NULL,
              oob.pred = NULL,
              train.pred = NULL,
              test.pred = NULL){
   # ---------------------------------------------------------
   # Inits
   # ---------------------------------------------------------
   temp.filename <- paste(model.filename,".ensemble.index.RData",sep="")
   load(file=temp.filename) #return.list
   bs.trials <- ensemble.par.list$n.ensemble.models
   resp.family <-  return.list$resp.family
   # ---------------------------------------------------------
   cat(" -------------------------------------\n")
   cat(" Bagged Decision Trees \n")
   cat(" -------------------------------------\n")
   cat("   Model Name: ", model.filename , "\n")
   cat("   Response type = ", resp.family , "\n")
   cat("   Number of Predictors = ", NCOL(train.data$X) , "\n")
   cat("   Training sample size = ", NROW(train.data$X) , "\n")
   cat(" -------------------------------------\n")
   cat(" Ensemble   \n")
   cat(" -------------------------------------\n")
   cat("   ensemble size  = ", bs.trials,"\n")
   cat("   Ensemble parameters: \n")
   for (iii in 2:length(ensemble.par.list)){
      cat( "      ",names(ensemble.par.list)[iii],"\n")
   }
   # ----------------------------------------------------
   # Ensemble size stats
   # ----------------------------------------------------
   if (!is.null(diag.bdt)) {
        cat("   Average # leaves per tree =",
              mean(diag.bdt$leaf.count) ,"\n")
        cat("   Average # obs per leaf =",
              mean(diag.bdt$ave.leaf.obs) ,"\n")
        cat("   Minimum # obs per leaf =",
              mean(diag.bdt$min.leaf.obs) ,"\n")
   }
   # -----------------------------------------
   pp <- NULL
   pp.names <- NULL
   # -----------------------------------------
   if (resp.family == "gaussian" | resp.family == "poisson"){
      if (!is.null(train.pred)) {
      # -------------------
      ttt.ind <- (!is.na(train.pred$mean)) 
      ttt <- predictive.performance(
            obs=train.data$y[ttt.ind],
            ppp=train.pred$mean[ttt.ind],
            resp.family=resp.family )
      pp  <- cbind(pp, ttt)
      pp.names <- rbind(pp.names, "Training")
      }
      # -----------------
      if (!is.null(oob.pred)) {
      ttt.ind <- (oob.pred$count > 0 & !is.na(oob.pred$mean)) 
      ttt <- predictive.performance(
            obs=train.data$y[ttt.ind],
            ppp=oob.pred$mean[ttt.ind],
            resp.family=resp.family)
      pp  <- cbind(pp, ttt)
      pp.names <- rbind(pp.names, "OOB")
      }
      # ----------------
      if (!is.null(test.pred)){
	 ttt.ind <- (!is.na(test.pred$mean)) 
          ttt <- predictive.performance(
                      obs=test.data$y[ttt.ind],
                      ppp=test.pred$mean[ttt.ind],
                      resp.family=resp.family)
      pp  <- cbind(pp, ttt)
      pp.names <- rbind(pp.names, "Test")
      }
      if (!is.null(pp)) pp <- data.frame(pp)
      # -----------------
   } # end if gaussian or poisson
   # ----------------------------------------
   if (resp.family == "bernoulli"){
      if (!is.null(train.pred)) {
      # -------------------
      ttt.ind <- (!is.na(train.pred$mean)) 
      ttt <- predictive.performance(
            obs=train.data$y[ttt.ind],
            ppp=train.pred$mean[ttt.ind],
            resp.family=resp.family )
      pp  <- cbind(pp, c(ttt$acc, ttt$rmse, ttt$auc))
      pp.names <- rbind(pp.names, "Training")
      }
      # -----------------
      if (!is.null(oob.pred)) {
      ttt.ind <- (oob.pred$count > 0 & !is.na(oob.pred$mean)) 
      ttt <- predictive.performance(
            obs=train.data$y[ttt.ind],
            ppp=oob.pred$mean[ttt.ind],
            resp.family=resp.family)
     pp  <- cbind(pp, c(ttt$acc, ttt$rmse, ttt$auc))
      pp.names <- rbind(pp.names, "OOB")
      }
      # ----------------
      if (!is.null(test.pred)){
	 ttt.ind <- (!is.na(test.pred$mean)) 
          ttt <- predictive.performance(
                      obs=test.data$y[ttt.ind],
                      ppp=test.pred$mean[ttt.ind],
                      resp.family=resp.family)
        pp  <- cbind(pp, c(ttt$acc, ttt$rmse, ttt$auc))
      pp.names <- rbind(pp.names, "Test")
      }
      if (!is.null(pp)) pp <- data.frame(pp)
      # -----------------
      rownames(pp) <- c("Accuracy", "RMSE", "AUC")
   } # end if bernoulli 
  
   cat(" -------------------------------------\n")
   cat(" Predictive Performance   \n")
   cat(" -------------------------------------\n")
   n.row <- NROW(pp)
   n.col <- NCOL(pp)
   for (ii in 1:n.col){
      cat( "      ",pp.names[ii]," ")
   }
   cat("\n")
     
   for (ii in 1:n.row){
       cat("   ", rownames(pp)[ii], "  ")
       for (jj in 1:n.col) {
       	   cat( as.character(format(pp[ii,jj], digits=5)),"   ")
       }
       cat("\n")
   }
   # ----------------------------------------------------
   # Relative Variable Importance -
   # ----------------------------------------------------
   if (!is.null(diag.bdt)) {
      cat(" ---------------------------------------------------------------------\n")
      cat("  Relative Variable Importance - Top 10    \n")
      cat(" ---------------------------------------------------------------------\n")
      # Re-order ttt in terms of descending Deviance
      ttt <- data.frame(Predictor = c(names(train.data$X)), Deviance = diag.bdt$var.imp1/sum(diag.bdt$var.imp1)*100 )
      ttt.ind <- order(ttt[,2],decreasing=TRUE)
      ttt <- ttt[ttt.ind, ]
      ttt$Predictor <- as.character(ttt$Predictor)
      for (iii in 1:10) cat("    ", iii, "  ",ttt[iii, 2],"   ", ttt[iii, 1], "\n")
      cat(" ---------------------------------------------------------------------\n")
      cat("\n")
      cat("\n")
   }
}# end summary function


# -----------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------
# Predictive Performance Functions
# 10.23.08
#
# Compute predictive Performance measures. The basic idea is to
# measure the average distance between observation & prediction.
#  		ave (distance(obs - pred))
# Methods vary according to the family of the response, how the
# averaging is performed and how distance is measured.
#
# ** Assumed that there are no NA's in either obs or predicted.
#
# Input:
# ---------
# 	obs = observed response
# 	ppp = corresponding predicted response (on response scale!)
# 	family = family or name of response type
#
# Output:
# ---------
# 	Family = "bernoulli" == binary (numerical? logical?)
# 	------------------------------------------------
# 	Family = "gaussian" == numerical
# 	------------------------------------------------
# 	Family = "poisson" == counts
# 	------------------------------------------------
#	**  I am no longer computing Pearson's Chi-Squared measure
# 	because the predictions in the denominator make is very
# 	unstable when there are lots of small predictions.
#	(for the relative abundance analyses)
#	          p <- sum( ((yyy - ppp)^2)/(ppp) )
# 	** Deviance Calculations
#
# Demo Code:
# -----------
#	yyy <- p.data$yp
#	ppp <- (d.dtm$pred.Xp)^2  #Untransformed
#	res <- residuals.dtm(obs = yyy,
#					ppp = ppp,
#					family="poisson")
#
# Needed:
# --------------------
# * More documentation
# * Example showing ROC curve using pred.obj (ROCR library help(performance))
# * Add gaussian & binary deviance functions & measures
# * erorr checking for different types of binary obs & pred
#
# -----------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------
predictive.performance <- function(obs, ppp, resp.family) {
	if (resp.family=="poisson"){
		# ----------------------------------
		MSE <- mean((ppp - obs)^2)
		R2 <- 1 - mean((ppp - obs)^2)/mean((mean(obs) - obs)^2)
		MSE.sqrt <- mean((sqrt(ppp) - sqrt(obs))^2)
		R2.sqrt <- 1 - mean((sqrt(ppp) - sqrt(obs))^2)/
					mean((mean(sqrt(obs)) - sqrt(obs))^2)
		MAD <- mean(abs(ppp - obs))
		rho <- cor(obs,ppp)
		rho.sqrt <- cor(sqrt(obs),sqrt(ppp))
		# ----------------------------
		# Poisson Deviance can not have zero predictions
		# Substitute predicted zero's with small values
		# ------------------------------------
			epsilon <- 1e-8
			ppp[ppp == 0] <- epsilon
		# ---------------------------------------------------------
		null.deviance <- poisson.deviance(
						yyy=obs,
						ppp=rep(mean(obs),length(obs) ))
		obs.deviance <- poisson.deviance(
						yyy=obs,
						ppp=ppp)
		deviance.explained <- (null.deviance - obs.deviance)/null.deviance
		# ----------------------------------
		return(list(
			MSE = MSE,
			R2=R2,
			MSE.sqrt = MSE.sqrt,
			R2.sqrt=R2.sqrt,
			MAD=MAD,
			rho=rho,
			rho.sqrt=rho.sqrt,
			deviance.explained=deviance.explained,
			obs.deviance=obs.deviance,
			null.deviance=null.deviance))
		}

	if (resp.family=="bernoulli"){
		acc <- 1 - sum(abs(obs-ppp))/length(ppp)
		require(ROCR)
		pred.obj <- prediction(prediction=ppp, labels=as.numeric(obs))
		perf <- performance(pred.obj, "auc")
		auc <- perf@y.values[[1]][1]
		perf <- performance(pred.obj, "rmse")
		rmse <- perf@y.values[[1]][1]
		return(list(
			acc=acc,
			rmse = rmse,
			auc = auc,
			pred.obj = pred.obj))
		}
	if (resp.family=="gaussian"){
		# ----------------------------------
		MSE <- mean((ppp - obs)^2)
		R2 <- 1 - mean((ppp - obs)^2)/mean((mean(obs) - obs)^2)
		MAD <- mean(abs(ppp - obs))
		rho <- cor(obs,ppp)
		# ----------------------------
		return(list(
			MSE = MSE,
			R2=R2,
			MAD=MAD,
			rho=rho))
		}
}
# -----------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------------------------------
# Poisson Predictive Performance Measures
# -----------------------------------------------------------------------------------------------------------
# yyy = observations
# ppp = predicted value - response scale
#
# Verified - replicated GAM deviance calcuatlions for poisson
# -----------------------------------------------------------------------------------------------------------
poisson.deviance <- function(yyy,ppp){
      # if predictions (ppp) equal zero we will get underflow
      # problems from log function.
      # -------------
      # break deviance into two pieces - where obs == 0
      ttt.zero <- (yyy == 0)
      ttt.pos <- (yyy > 0)
      dev1 <- sum( (yyy[ttt.zero] - ppp[ttt.zero]) )
      dev2 <- sum( yyy[ttt.pos]*log(yyy[ttt.pos]/ppp[ttt.pos]) -
                  (yyy[ttt.pos] - ppp[ttt.pos]))
      dev <- 2*(dev2 - dev1)
      return(dev)
}
# -----------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------


# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# Random Train/Test Split
# ------------------------
# n = length of index
# p.train = percentage for training
#
# This function simply returns two indices that partition
# a set of n iterms into two mutually exclusive sets.
#
# Demo
#ttt <- ttsplit(n=100, p.train=0.5)
#length(ttt$train.index)
#length(ttt$test.index)
# ---------------------------------------------------
ttsplit <- function(n, p.train){
  train.index <- NULL
  val.index <- NULL 
  ttt.index <- 1:n
  nnn.train <- round(n * p.train)
  nnn.val <- n - nnn.train
  if (nnn.train <= n)
      train.index <- sample((1:n), nnn.train)
  if (nnn.val > 0 ) {
  	full.index <- c(1:n)
  	val.index <- setdiff(full.index, train.index)
  	val.index <- sample( val.index, min(nnn.val, length(val.index)))
  	}
  return(list(train.index=train.index, test.index=val.index))
} # end function

# ------------------------------------------------------------------------
# ------------------------------------------------------------------------

# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# Simple Unique Location Train/Test Splitting
# 11.3.07
#
# Randomly select a unique set of locations for the train and
# test sets. This function will collect all records for a given
# location and assign them according to the train/test split.
# This sampling design does NOT preserve the relative sampling
# density across locations because there are no repeat locations
# sampled.
#
# Input:
# ---------
#     locs - location data frame/matrix
#     p.train - proportion of locations for training
#     m.frac - fraction of multiple observations to include for
#               each location
#
# Output:
# ---------
#   unique.index= unique loc index ( I believe that the
#                 first instance for each repeated loc is indicated here)
#   train.index.single & test.locs.single
#                 index to one observation from a unique set of locations.
#                 Train & test sets form a random partition of the locations
#                 in the unique.index.
#   train.locs.index & test.locs.index
#                 Collect a fraction of available observations at each of
#                 the randomly selected training locations. If there are repeat observations at
#                 a unique location, then all of these observations will
#                 be included in this set. Same for the test set.
#
# Demo Code:
# -----------
#  # Create Data with Repeat Obs at specific locations
#  #nnn <- 10000
#  #locs <- data.frame(x=rnorm(nnn), y=rnorm(nnn))
#  locs <- cc.data$loc
#  ddd <- unique.locs.splitting(locs, p.train=0.75, m.frac=0.5)
#  length(ddd$train.locs.single)
#  length(ddd$train.locs.multiple)
#  length(ddd$test.locs.single)
#  length(ddd$test.locs.multiple)
#  # ----------------------------
#  # Plot Map of Train/Test Sets
#  # ----------------------------
#  plot(locs$x[ddd$train.locs.single],
#      locs$y[ddd$train.locs.single],
#      xlab ="lon", ylab="lon",
#      pch=24,
#      col="red",
#      cex=.5)
#  points(locs$x[ddd$test.locs.single],
#      locs$y[ddd$test.locs.single],
#      col="blue",
#      pch=25,
#      cex=0.5)
#  title(main="eBird Northern Cardinal Summer 2006", font.main = 4 )
#  box(lwd=3.0)
#  require(maps)
#  require(mapdata)
#  map('state',add=TRUE)
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
unique.locs.splitting <- function(locs, p.train, m.frac=1.0){
  # Extract unique locs as ttt
  ttt <- unique(locs)
  # 1) Randomly select proportion of unique locations
  split.ind <- ttsplit(n=NROW(ttt), p.train=p.train)
  train.index <- split.ind$train.index
  test.index <- split.ind$test.index
  # ----------------------
  # 2) Process Test Set
   test.locs.single <- NULL
   test.locs.multiple <- NULL
   for (iii in 1:length(test.index)){
      temp.ind <- (locs$x == ttt$x[test.index[iii]]  &
                   locs$y == ttt$y[test.index[iii]])
      #Convert to index into locs for matches
      temp.ind <- as.numeric(temp.ind) * c(1:NROW(locs))
      temp.ind <- temp.ind[temp.ind > 0]
      # Random Selection Single
      temp.ind.single <-temp.ind[
            sample(1:length(temp.ind), size=1, replace=FALSE) ]
      test.locs.single<- c(test.locs.single, temp.ind.single)
      # Random Selection Multiple
      m.size <- max(1,round(m.frac*length(temp.ind)))
      temp.ind.multiple <- temp.ind[
            sample(1:length(temp.ind), size=m.size, replace=FALSE)]
      test.locs.multiple <- c(test.locs.multiple, temp.ind.multiple)
      }
  # -------------------------
  # 3) Process Train Set
    train.locs.single <- NULL
    train.locs.multiple <- NULL
    for (iii in 1:length(train.index)){
      temp.ind <- (locs$x == ttt$x[train.index[iii]]  &
                   locs$y == ttt$y[train.index[iii]])
      #Convert to index into locs for matches
      temp.ind <- as.numeric(temp.ind) * c(1:NROW(locs))
      temp.ind <- temp.ind[temp.ind > 0]
      # Random Selection Single
      temp.ind.single <-temp.ind[
            sample(1:length(temp.ind), size=1, replace=FALSE) ]
      train.locs.single<- c(train.locs.single, temp.ind.single)
      # Random Selection Multiple
      m.size <- max(1,round(m.frac*length(temp.ind)))
      temp.ind.multiple <- temp.ind[
            sample(1:length(temp.ind), size=m.size, replace=FALSE)]
      train.locs.multiple <- c(train.locs.multiple, temp.ind.multiple)
      }
  # -------------------------
  return(list(train.locs.single = train.locs.single,
              train.locs.multiple = train.locs.multiple,
              test.locs.single = test.locs.single,
              test.locs.multiple = test.locs.multiple,
              unique.index=as.numeric(rownames(ttt))
              ))
} # end function
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------



# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# Loop Over 1 Grid Realization - Compute & Store Distribution 
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# Create Train:Test sets with Unique Locations 
# ----------------------------------------------------------------------
#	dsplit <- unique.locs.splitting(locs=cc.data$loc,
#			p.train=fraction.training.data,
#			m.frac=1.0)
#	train.index <- dsplit$train.locs.multiple
#	test.index <- dsplit$test.locs.multiple
# ---------------------------
# Maximum Coverage Selection
# for Train:Test Set
# ---------------------------
maximum.coverage.selection <- function(
               locs, # data.frame(x , y) length n
               jdates, # vector length n
			#grid.parameters,
	              grid.cell.min.lat,
		  	    grid.cell.min.lon,
			min.val.cell.locs,
			fraction.training.data,
			mfrac=1.0,
			plot.it =FALSE ){
# ----------------------------------------------------------------
#		 RETURN:
#			train.index <- 
#			test.index <- 
# -------------------------------------------------------------------
# Formal test values
#               locs=cc.data$locs  data.frame(x , y) length n
#               jdates=cc.data$X$JDATE  vector length n
#			grid.parameters,
#	              grid.cell.min.lat=1.0
#		  	    grid.cell.min.lon=1.5
#			min.val.cell.locs=5
#			fraction.training.data=0.8
#			mfrac=1.0
# ----------------------				
	lon.min <- min(locs$x)
	lon.max <- max(locs$x)
	lat.min <- min(locs$y)
	lat.max <- max(locs$y)

	#for (iii.loop in 1:nnn.grids) { 
	iii.loop <- 1
	# 1) Randomize Coordinate for first grid cell boundary
		r.lat <- runif(1,min=0, max=grid.cell.min.lat)
		r.lon <- runif(1,min=0, max=grid.cell.min.lon)
		# 2) lay down equally spaced grid until x.max reached
		grid.ttt <- seq(from=(lon.min+r.lon),
		               to=lon.max,
			           by=grid.cell.min.lon)
		grid.xxx <- c(lon.min, grid.ttt, lon.max)
		grid.ttt <- seq(from=(lat.min+r.lat),
		               to=lat.max,
			           by=grid.cell.min.lat)
		grid.yyy <- c(lat.min, grid.ttt, lat.max)
		# incase of any duplicates!
		grid.xxx <- sort(unique(grid.xxx))
		grid.yyy <- sort(unique(grid.yyy))
		# ---------------------------
		# Sample Maximal Coverage Validation Data
		# Then use the rest for Training
		# ** Take up to the first min.val.cell.locs
		# ** Then randomly select the rest, by unique loc
		# ---------------------------
		kkk <- 0 # counter for grid cell regions
		nnn.grid.cells <- (length(grid.xxx)-1)*(length(grid.yyy)-1)
		u.test.locs <- NULL 
		# -----------------------------------------------------------------
		# Cycle over Columns(xxx_iii) within Given Row (yyy_jjj)
		# -----------------------------------------------------------------
		for (jjj in 1:(length(grid.yyy)-1)){
		for (iii in 1:(length(grid.xxx)-1)){
			#iii <- 10
			#jjj <- 20
			
			kkk <- kkk + 1
			# --------------------------------
			xxx <- locs$x
			yyy <- locs$y
			cell.index <- xxx >= grid.xxx[iii] & xxx < grid.xxx[iii+1] &
					yyy >= grid.yyy[jjj] & yyy < grid.yyy[jjj+1]
			# Check for minimum Prediction Cell Locations
			# ---------------------------------------------
			u.locs <- unique(data.frame(x=locs$x[cell.index],
				  		y=locs$y[cell.index]))
 			sum(cell.index)
 			dim(u.locs)
			 
			 if (NROW(u.locs) <= min.val.cell.locs) {
			   # Randomly Select first min.val.cell.locs
			   u.test.locs <- rbind(u.test.locs,u.locs)
			   }		
			if (NROW(u.locs) > min.val.cell.locs) {
			   # Randomly Select first min.val.cell.locs
			   # Then Randomly split the rest
			   # ---------------------------------
			   ttt.ind <- sample(1:NROW(u.locs), size=min.val.cell.locs)
			   u.test.locs <- rbind(u.test.locs,u.locs[ttt.ind,])
			   u.locs <- u.locs[ (setdiff(1:NROW(u.locs),ttt.ind)) , ] 
			   dsplit <- unique.locs.splitting(locs=u.locs,
							p.train=fraction.training.data,
							m.frac=1.0)
			   u.test.locs <- rbind(u.test.locs, 
			   			     u.locs[dsplit$test.locs.multiple,])
			   }						  		
		}}# end grid loop
		# -----------------------------------------	
		#  
		# -----------------------------------------			
		# Should be locs DF with all unique locs for valiation set
		# Now, I need to divide data accordingly 
		# ------------------------------	
		test.index <- (locs$x %in% u.test.locs$x) & (locs$y %in% u.test.locs$y)
		train.index <- !test.index		
		# -------------------------
		# Test Plot of Grid
		# -------------------------
		if ( plot.it == TRUE){
			plot(1,1, 
				xlim=c(lon.min,lon.max), 
				ylim=c(lat.min, lat.max),
				type="n",
				cex=0.25, 
				main =paste("Train=Blue(",sum(train.index),
					")    Test=Red(",sum(test.index),")"))
			require(maps)
			map("state", add=TRUE, col="black", lwd=2)
			for (jjj in 1:length(grid.yyy)){
			      lines(c(lon.min,lon.max),rep(grid.yyy[jjj],2),col="grey")
			      }
			for (jjj in 1:length(grid.xxx)){
			      lines(rep(grid.xxx[jjj],2),c(lat.min,lat.max),col="grey")
			      }			
			#dim(u.test.locs) 
			points(locs[train.index,], col="blue", cex=0.5, pch=19)
			points(u.test.locs, cex=0.5, col=2,pch=19)
			}
# ------------------		
return(list( test.index = test.index, 
    train.index = train.index))		
# ---------------------------------------------------------------------------------
} #end FUNCTION
# ---------------------------------------------------------------------------------	

# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# equal.wt.max.coverage.selection
# max.uniform.coverage.split
# DFink 
# 3.22.10
#
# This function splits a set of locations into "test" and "training" 
# set with with the goal that the test set meet two objectives:
# 	1) The test set covers the broadest extent possible, and 
# 	2) The test set is approximately uniform over the extent.
# 
# The first goal is met by constructing a randomly located rectangular
# grid over the extent of the data and then preferentially select 
# test locations that populate as many cells as possible. Within
# grid cell density is controlled, i.e. made more uniform, by 
# setting the maximum number of unique locations included in cell. 
# Small value of the maximum cell sample size parameter help 
# to produce more uniformly distributed test set samples.
#
# Note, if locations are repeated, all the repeats for each location 
# are all assigned to either the test or training sets.  
#
# Inputs:
# ---------  
#	locs - data frame or list with elements x & y.  
#	grid.cell.min.lat - height of grid cells
#	grid.cell.min.lon - width of grid cells
#	max.cell.locs - integer giving maximum number of unique locations 
# 					per cell
#	plot.it =FALSE - flag for diagnostic plot
# 
# Outputs: 
# --------- 
# 	test.index = boolean index of length = nrows(locs)
# 	train.index = same. 
#   
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# Equal Weight with Maximum Coverage Splitting
# for Train:Test Set
# ---------------------------
equal.wt.max.coverage.selection <- function(
	locs, 
	grid.cell.min.lat,
	grid.cell.min.lon,
	max.cell.locs=1,
	plot.it =FALSE ){
# ----------------------------------------------------------------
# Formal test values
#           locs=cc.data$locs  data.frame(x , y) length n
#	        grid.cell.min.lat=1.0
#		  	grid.cell.min.lon=1.5
#			max.cell.locs=5
# ----------------------				
	lon.min <- min(locs$x)
	lon.max <- max(locs$x)
	lat.min <- min(locs$y)
	lat.max <- max(locs$y)
	iii.loop <- 1
	# 1) Randomize Coordinate for first grid cell boundary
	r.lat <- runif(1,min=0, max=grid.cell.min.lat)
	r.lon <- runif(1,min=0, max=grid.cell.min.lon)
	# 2) lay down equally spaced grids from min to max
	grid.ttt <- seq(from=(lon.min+r.lon),
	               to=lon.max,
		           by=grid.cell.min.lon)
	grid.xxx <- c(lon.min, grid.ttt, lon.max)
	grid.ttt <- seq(from=(lat.min+r.lat),
	               to=lat.max,
		           by=grid.cell.min.lat)
	grid.yyy <- c(lat.min, grid.ttt, lat.max)
	# incase of any duplicates!
	grid.xxx <- sort(unique(grid.xxx))
	grid.yyy <- sort(unique(grid.yyy))
	# ---------------------------------------------------
	# Sample Maximal Coverage Test Set 
	# Then use the rest for Training
	# ** Take up to the first max.cell.locs
	# ** Then randomly select the rest, by unique loc
	# ---------------------------------------------------
	kkk <- 0 # counter for grid cell regions
	nnn.grid.cells <- (length(grid.xxx)-1)*(length(grid.yyy)-1)
	u.test.locs <- NULL 
	# -----------------------------------------------------------------
	# Cycle over Columns(xxx_iii) within Given Row (yyy_jjj)
	# -----------------------------------------------------------------
	for (jjj in 1:(length(grid.yyy)-1)){
	for (iii in 1:(length(grid.xxx)-1)){
		kkk <- kkk + 1
		xxx <- locs$x
		yyy <- locs$y
		cell.index <- xxx >= grid.xxx[iii] & xxx < grid.xxx[iii+1] &
				yyy >= grid.yyy[jjj] & yyy < grid.yyy[jjj+1]
		# Check for minimum Prediction Cell Locations
		# ---------------------------------------------
		u.locs <- unique(data.frame(x=locs$x[cell.index],
			  						y=locs$y[cell.index]))
		#sum(cell.index)
		#dim(u.locs)
		#cat(NROW(u.locs),"\n")
		#cat( max.cell.locs, "\n")
		if (NROW(u.locs) <= max.cell.locs) {
			# Randomly Select first max.cell.locs
		   	u.test.locs <- rbind(u.test.locs,u.locs)
		   	}		
		if (NROW(u.locs) > max.cell.locs) {
		   	# Randomly Select first max.cell.locs
		   	# Then Randomly split the rest
		   	# ---------------------------------
		   	ttt.ind <- sample(1:NROW(u.locs), size=max.cell.locs)
		   	u.test.locs <- rbind(u.test.locs,u.locs[ttt.ind,])
		   }						  		
	}}# end grid loops
	# -----------------------------------------			
	# Build index into all locations.  
	# ------------------------------	
	test.index <- (locs$x %in% u.test.locs$x) & (locs$y %in% u.test.locs$y)
	train.index <- !test.index		
	# -------------------------
	# Test Plot of Grid
	# -------------------------
	if ( plot.it == TRUE){
		plot(1,1, 
			xlim=c(lon.min,lon.max), 
			ylim=c(lat.min, lat.max),
			type="n",
			cex=0.25, 
			main =paste("Train=Blue(",sum(train.index),
				")    Test=Red(",sum(test.index),")"))
		require(maps)
		map("state", add=TRUE, col="black", lwd=2)
		for (jjj in 1:length(grid.yyy)){
		      lines(c(lon.min,lon.max),rep(grid.yyy[jjj],2),col="grey")
		      }
		for (jjj in 1:length(grid.xxx)){
		      lines(rep(grid.xxx[jjj],2),c(lat.min,lat.max),col="grey")
		      }			
		#dim(u.test.locs) 
		points(locs$x, locs$y, col="blue", cex=0.25, pch=1)
		points(u.test.locs, cex=0.25, col=2,pch=1)
	} # plot.it
# ------------------		
return(list(test.index = test.index, 
    		train.index = train.index))		
# ---------------------------------------------------------------------------------
} #end FUNCTION
# ---------------------------------------------------------------------------------	





# ---------------------------------------------------------------------
# ---------------------------------------------------------------------
# OOB Diagnositic Plots
# ---------------------------------------------------------------------
plot.diagnostics <- function(pred, ensemble.data, resp.family) {
   # ---------------------------------------------------------------------
   # ---------------------------------------------------------------------
   #
   #  pred = test.pred
   #          oob <-  FALSE
   #          ensemble.data = test.data
   # ---------------------------------------------------------------------        
   require(mgcv)
   par(mfrow=c(3,2))
   # Plot Residuals
   # --------------      
   ttt.ind <- !is.na(pred$mean) 
   res <- (ensemble.data$y[ttt.ind] - pred$mean[ttt.ind])
   hist(res,
	xlab = "Observation - Prediction",
	main = "Residuals")
   lines(c(0,0), c(-9e9,9e9), col="blue")
   # ------------------------------------
   # How many models support In-Bag Predicitons
   # and Out Of Bag/Sample Predictions
   # --------------------------------------------
   hist(apply(!is.na(pred$matrix), 1, sum, na.rm=T),
   main="Ensemble Support",
   xlab="Number of Models per Prediction")
   # Note: Zero column is the number of training points
   # that were never predicted OOB
   # Plot predictions vs Obs.
   # ---------------------------
   ttt.ind <- !is.na(pred$mean) 
   xxx <- pred$mean[ttt.ind]
   yyy <- ensemble.data$y[ttt.ind]
   plot(xxx, 
   	yyy,
	xlab="Prediction",
	ylab="Observation")
   abline(0,1, col="blue")
   require(mgcv)
   d.gam <- gam(yyy ~ s(xxx), data=data.frame(yyy,xxx), gamma=1.2)
   ttt <- seq(from=min(xxx), to=max(xxx), length=15)
   p.ttt <- predict(d.gam, newdata=data.frame(xxx=ttt))
   lines(ttt,p.ttt, col=2)
   # Mean - Var Scaling 
   # -------------------
   ttt.ind <- ( !is.na(pred$sd) & !is.na(pred$mean) )       
   xxx <- pred$mean[ttt.ind]
   yyy <- pred$sd[ttt.ind]
   plot(xxx, 
        yyy,
	xlab="Ensemble Pointwise Mean",
	ylab="Ensemble Pointwise SD")
   abline(0,1, col="blue")
   d.gam <- gam(yyy ~ s(xxx), data=data.frame(yyy,xxx), gamma=1.2)
   ttt <- seq(from=min(xxx), to=max(xxx), length=15)
   p.ttt <- predict(d.gam, newdata=data.frame(xxx=ttt))
   lines(ttt,p.ttt, col=2)  
   # ------------------------------
   # -------------------------------------------------------------
   # Add Bootstrap Trajectory for MSE(oob.pred, training.obs)
   # -------------------------------------------------------------
   if (resp.family=="gaussian" | resp.family=="poisson") {	
      ppp <- pred$matrix  # continous.res x btrials
      j.length <- 25
      j.ind <- seq(from=1, to=NCOL(ppp), length=j.length)
      MSE <- rep(0,  j.length)
      for (jjj in 1:j.length){
      	  if (jjj == 1) ttt.pred <- ppp[,1]
          if (jjj > 1) ttt.pred <- apply(ppp[,c(1:j.ind[jjj])],1,
                                         mean,
                                         na.rm=TRUE)
	  MSE[jjj] <- predictive.performance(obs=ensemble.data$y[!is.na(ttt.pred)],
						ppp=ttt.pred[!is.na(ttt.pred)],
	                			resp.family=resp.family)$MSE             
          }
          plot(j.ind,
                MSE,
                xlab="Ensemble Size",
                main=" MSE vs Ensemble Size ",
                type="l", lwd=2)
       } # 
       # -------------------------------------------------
       # -------------------------------------------------------------
       # Add Bootstrap Trajectory for MSE(oob.pred, training.obs)
       # -------------------------------------------------------------
       if (resp.family=="bernoulli") {
		ppp <- pred$matrix  # continous.res x btrials
          j.length <- 25
          j.ind <- seq(from=1, to=NCOL(ppp), length=j.length)
          MSE <- rep(0,  j.length)
          for (jjj in 1:j.length){
            if (jjj == 1) ttt.pred <- ppp[,1]
            if (jjj > 1) ttt.pred <- apply(ppp[,c(1:j.ind[jjj])],1,
                                    mean,
                                    na.rm=TRUE)
		  # ---------------------------------------------------------------
		  # This is a hack to accomodate 
		  # an error from the ROCR prediction() function 
		  # encountered when all the observations are of a 
		  # single class! 
		  # "Error in prediction(prediction = ppp, labels = as.numeric(obs)) : 
  		  # "Number of classes is not equal to 2.
		  # ---------------------------------------------------------------
		  if (length((unique(ensemble.data$y[!is.na(ttt.pred)]))) ==2)
		  	MSE[jjj] <- predictive.performance(
                	    obs=ensemble.data$y[!is.na(ttt.pred)],
                	    ppp=ttt.pred[!is.na(ttt.pred)],
                	    resp.family=resp.family)$auc     	    
          }
          plot(j.ind,
                MSE,
                ylim=c(0.5, 1.0),
                xlab="Ensemble Size",
                ylab="AUC",
                main=" AUC vs Ensemble Size ",
                type="l", lwd=2)
       } # 
       # -------------------------------------------------
# -------------------------------------------------------------
} # end function
# ---------------------------------------------------------------------
# ---------------------------------------------------------------------

# ---------------------------------------------------------
# Simple Plot for 1D PD plots
# 
# This needs to really be cleaned up 
# ---------------------------------------------------------
summary.1D.PD.ensemble<- function(filename=NULL,
					ensemble.par.list,
					pd.data,
    					pd.bdt.object.name = NULL, 
    					continuous.resolution = 15,
    					nn.sample = 100,
    					# ----------------------
    					partial.datafile = NULL, 
    					diag.bdt=NULL,
    					n.pd = 4,
    					pd.filename,
    					# ----------------------
    					plot.it = TRUE,
    					plot.range = "common",
    					n.row = 2,
    					n.col =2) {
	# ---------pd.data------------------------------------------------
	    X.names <- names(pd.data$X)
	    X.factor.ind <-  rep(FALSE, NCOL(pd.data$X))
		  ttt <- pd.data$X[1,] # it is much faster to search a 1D data.frame!
	    for (ii in 1:NCOL(pd.data$X))
		X.factor.ind[ii] <- is.factor(ttt[,ii])
	    # ------------------------------
	    ttt.ind <- order(apply(diag.bdt$var.imp1,1,median), decreasing=TRUE)
	    pd.names <- X.names[ttt.ind]
	    pd.names <- pd.names[1:n.pd]
	    pd.factor.ind <- X.factor.ind[ttt.ind]
	    pd.factor.ind <- pd.factor.ind[1:n.pd]
	    pd.list <- as.list(pd.names)
    
	if (is.null(pd.bdt.object.name) ){
	# ------------------------------------------------
	pd.bdt <- ensemble.partial.dependence(
                  filename = filename,
		  	   ensemble.par.list = ensemble.par.list,
                  XX = pd.data$X,
                  partial.dependence.list = pd.list,
                  continuous.resolution = continuous.resolution,
                  nn.sample = nn.sample)
	save(pd.bdt, file=paste(pd.filename,sep=""))
	} 

	if (!is.null(pd.bdt.object.name) ){
	# ------------------------------------------------
	load(pd.bdt.object.name) # Assumed name is pd.bdt
	} 

    # ---------------------------
    if (plot.it == TRUE) {
      # Calc Centered PD means &
      # Find y-limits for these plots
      # --------------------------------
      y.min <- 0.0
      y.max <- 0.0
      for (iii in 1:n.pd) {
          # Calculate Centered Mean
          ppp <- pd.bdt$pd.matrices[[iii]]
          ppp.mean <- apply(ppp, 1, mean, na.rm=T)
          ppp.mean <- ppp.mean - mean(ppp.mean)
          y.min <- min(c(y.min,min(ppp.mean)))
          y.max <- max(c(y.max,max(ppp.mean)))
        }
      y.range <- NULL
      if (plot.range=="common") y.range <- c(y.min, y.max)
	      
      # -------------------------------------------------------------------------------------------------------
      par(mfrow=c(n.row,n.col), mar=c(2,2,4,2))
      # mar = c(bottom, left, top, right)
      for (iii in 1:n.pd) {
      # --------------------------
          # Continuous Plot
          # ----------------------------------
	if (pd.factor.ind[iii] == FALSE) { 
              xxx <- pd.bdt$pd.quant.grids[[iii]] #
              ppp <- pd.bdt$pd.matrices[[iii]]  # matrix: continous.res x btrials
             # Change ppp to data.frame
              ppp <- data.frame(ppp)
              # Calculate Centered Mean
              ppp.mean <- apply(ppp, 1, mean, na.rm=T)
              ppp.center <- mean(ppp.mean)
              ppp.mean <- ppp.mean - ppp.center
              #names(ppp) <- as.character(c(1:NCOL(ppp)))
              #yyy.stacked <- stack(ppp)
              #yyy.stacked <- as.numeric(yyy.stacked[,1])- ppp.center
              #xxx.stacked <- rep(as.numeric(xxx[,1]), times=NCOL(ppp))
              #----		
			plot(xxx[,1],
					ppp.mean,
					ylim=y.range ,
					type = "p",
					col="black",
					pch = 19,
					cex=.75,
					xlab = " ",
					main = names(xxx),
					ylab = " ")
			abline(0,0) 
			
		# -----------------------------------------------
		# Plot when there enough unique levels to smooth 
		# ----------------------------------------------
		if (length(sort(unique(xxx[,1]))) >= 10) { 	      
		# ----------------------------------------------------
			yyy.stacked <- ppp.mean
			xxx.stacked <- xxx[,1]
			# ---------------
			require(mgcv)
			d.gam <- gam( yyy.stacked ~ s(xxx.stacked),
					gamma=1.2)
			xxx.pred <- seq(from=min(xxx.stacked),
						to=max(xxx.stacked),
						length=25)
			pred.gam <- predict(d.gam,
				  newdata=data.frame(xxx.stacked=xxx.pred),
				  se.fit=TRUE, type="response")
			lines(xxx.pred,pred.gam$fit,col="blue", lwd=2.0)
		}}
          # ----------------------------------
          # Factor Plot
          # ----------------------------------
          if (pd.factor.ind[iii] == TRUE){
              xxx <- pd.bdt$pd.quant.grids[[iii]] #
              ppp <- pd.bdt$pd.matrices[[iii]]  # continous.res x btrials
              # Calculate Centered Mean
              ppp.mean <- apply(ppp, 1, mean, na.rm=T)
              ppp.center <- mean(ppp.mean)
              ppp.mean <- ppp.mean - ppp.center
              # -----------------------------------------------
              # Change xxx to class factor for plot
              # -----------------------------------------------
              factor.levels <-
                levels(pd.data$X[, names(pd.data$X) == names(xxx)])
              xxx.recoded <- factor.levels[ xxx[,1]]
              plot(as.factor(xxx.recoded),
                   ppp.mean,
                   ylim= y.range,
                   xlab = " ",
                   main = names(xxx),
                   ylab = " ")
              abline(0,0)
            }
       }# end plotting
    } # end plot.it
} # end function
# -------------------------------------------------------------------
# ---------------------------------------------------------------------


 
#------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------
# Extract Seasonal p.data
# function st.gam relies on this function. 
#
# 1.13.08 
# Modified to only do a single "training/test" data set
# and to return only the index (logical index). 
#
#
#Demo:
# -----------
# ttt.data <- seasonal.window(
# 					begin.window=30, 
# 					end.window=80,
# 					p.data=p.data)
# 		names(ttt.data$X)
# 		dim(ttt.data$X)
# 		dim(ttt.data$Xp)
# 		sort(unique(ttt.data$X$JDATE))	
#
#
# Tree Swallow Notes: 
# ---------------------------------
	# -----------------------------------------
	# Define Seasons
	# -----------------------------------------
	#ttt<- c( 	320, 45, 		#winter
	#		45, 110, 		#spring
	#		110, 200, 	#Breeding
	#		200, 320)		# Fall 
	#season.boundaries <- matrix(ttt,4,2, byrow=TRUE)
#------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------
seasonal.window <- function(
					begin.window, 
					end.window,
					p.data){
		season.boundaries <- matrix(c(begin.window, end.window), 
									1,2, byrow=TRUE)
		jjj <- 1					
		winter <- (begin.window > end.window)
		# -----------------------------------------
		# Training p.data 
		# -----------------------------------------
		season.index <- p.data$jdates >= season.boundaries[jjj,1]  & 
						p.data$jdates <= season.boundaries[jjj,2]	
		if (winter) { # Winter
			season.index <- p.data$jdates >= season.boundaries[jjj,1] | 
						p.data$jdates <= season.boundaries[jjj,2]
                }
		return(
			list(
      #p.data=p.data,
			season.index = season.index))
			#season.p.index = season.p.index))
	} #end function
# -------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------


## Clear the deck of all local variables
## rm(list = c("arrival.dates", "begin.date", "bs.rpart.maps", "by.tic", "color.palette", "create.pd.grid", "create.simple.STEM.ensemble", "D.erd.data.par.list", "deviance.explained", "end.date", "ensemble.partial.dependence", "equal.wt.max.coverage.selection", "fit.ensemble", "halloween.colors", "halloween.maps", "iii", "initizalize.map.grid", "jdate.index", "jdate.seq", "jdate.tic.names", "jdate.tics", "j.index", "make.functional.data.design.matrix", "make.SPAT.COVAR.pred.data", "map.inits", "map.plot.pixel.width", "maximum.coverage.selection", "monthly.maps", "month.text", "n.intervals", "ns.rows", "old.directories", "plot.diagnostics", "plot.file.name", "plot.main", "plot.STEM.temporal.design", "plot.ST.ensemble", "plot.vi.bdt", "point.in.polygon", "point.in.polygon.contours", "point.in.shapefile", "poisson.accuracy", "poisson.deviance", "poisson.pearson", "pop.rpart", "pred.grid.size", "prediction.threshold", "predictive.performance", "predict.ST.ensemble", "predict.st.matrix", "predict.st.matrix.ebird.ref.data", "p.time", "results.dir", "return.list", "rotate.ST.basis.pred", "rotate.ST.basis.sample", "rpart.ensemble.diagnostics", "sample.ST.ensemble", "save.plot", "seasonal.window", "season.tag", "smoothing.dir", "smoothing.dir.tag", "smoothing.tag", "smooth.st.predictions", "spatial.density.contours", "spatial.extent.list", "spatial.performance.plot", "spp.common.name", "spp.dir", "spring.migration", "st.arrival.dates", "st.arrival.dates.filename", "STEM.partial.dependence", "st.pred", "summarize.ensemble", "summary.1D.PD.ensemble", "surface.maps", "t.smooth.file.tag", "t.smooth.tag", "ttsplit", "ttt.filename", "ttt.index", "unique.locs.splitting", "usaMapEnv", "year.seq", "ylab.text", "z.range"))
## KFW gc()