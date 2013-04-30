

# --------------------------------------------------------------------#  
#  ==> This function is just a CV wrapper to 
#		predict.st.matrix.ebird.ref.data!!! 
#  ==> Also new is the creation of an "index" file
# 		to hold all of the parameters needed to describe
# 		the st.matrix (file sequence)
# 
#
# The ST Matrix: 
# ------------------
# Basis for predictive experiments or ST analysis 
# is predictions across a region in space and across. 
# Often we want to know how spatial distrivution changed shrought time. 
# 
# Conceptually the ST Matrix as a data object is a set of 
# prediction across a lattice in space and time.  
# The st.matrix data object is a sequence of files
# Each one contains the predictions across a set of locations
# during a single time step.
# Each file in the sequence contains the predictions across
# the same set of locations evaluated at each of times
# in the temporal sequence.
#
# One set of ST.matrix files is written for each CV-fold 
# model in cv.list
#
# The ST matrix can be thougth of as a source of psuedo-data
# with 3 added benefits: 
# 1) Cleaned
# 2) Filled In
# 3) Uncertainty Estimates 
#
# 
# File Namining Conventions
# ---------------------------
#
#
# Naming Standards are being hardcoded for convenience/simplicity
# For example, one stem analysis per directory means that the
# STEM objects are uniquely identified by the directory name. 
# So, I fixed the model names by hardcoding 
# 		stem.model.tag <- "stem." 
# 
# st.matrix Names = paste(results.dir,st.matrix.file.tag,"st.matrix.",
#							[sequence number], ".RData",sep="")
# These are kept in the CV result directories 
# because they are CV specific. 
# 
# --------------------------------------------------------------------# --------------------------------------------------------------------
# DMF 3.19.10 VT modifications
# 	* change formal parameter st.matrix.name,	# st.matrix project name
predict.erd.st.matrix <- function(
	stem.directory, # equivalent to stem.object
	pred.data, 		#= srd.data,
  	cv.list, 		# subset of cv's
  	stem.predictor.names, 		   
	# --------------
	st.matrix.name,	# st.matrix project name
	#st.matrix.directory,
	jdate.seq,
	year.seq,
	conditioning.vars){ #= conditioning.vars)				   
# -------------------------------------------------------------------- 
   stem.model.tag <- "stem."  #hardcoded for convenience

   print("**********")
   print(stem.directory)


   if ("/" == substring(stem.directory, nchar(stem.directory), nchar(stem.directory))) {
      st.matrix.directory <- paste(stem.directory, st.matrix.name, "/", sep="")
      stem.model.directory <- paste(stem.directory, "model", "/", sep = "")
   }
   else {
      st.matrix.directory <- paste(stem.directory, "/", st.matrix.name, "/", sep="")
      stem.model.directory <- paste(stem.directory, "/", "model", "/", sep="")
   }

   system(paste("mkdir ",st.matrix.directory, sep=""), intern=TRUE)

# ---------------------------
for (iii.cv in cv.list){
	results.dir <- paste(st.matrix.directory, "st.matrix.", 
		as.character(iii.cv), sep = "")
	system(paste("mkdir ",results.dir,sep=""), intern=TRUE)
	# ------	
	model.dir <- paste(stem.model.directory, "stem.models.", 
		as.character(iii.cv), "/", sep="")
	stem.ST.matrix.file.tag <- 
	    paste(results.dir,"/", "st.matrix.",sep="")
	## Load nfold specific parameter list
	load(file = paste(model.dir, 
				"stem.model.par.list.", iii.cv, ".RData" , sep = "")) # D.stem      
    # ----------------------------
    # Write ST.Matrix object to stem.results directories
    # ----------------------------

   print(names(pred.data$D.pred))
   print(nrow(pred.data$D.pred))


    predict.st.matrix.ebird.ref.data(
	    	prediction.design = pred.data$D.pred,
		   	prediction.design.locs = pred.data$locs,
	  	# prediction.design.jdates,  #not needed here
	  	#--------------
	  		model.predictor.names = stem.predictor.names,
	  		model.filename = #stem.model$ensemble.model.filename,
				paste(model.dir, stem.model.tag,sep=""),
	  		ensemble.par.list = D.stem, #stem.model, #ensemble.par.list,
	  	# --------------
	  		save.name = stem.ST.matrix.file.tag,
	  	# Temporal Sequence
	  		jdate.seq =jdate.seq,
	  		year.seq =year.seq,
	  	# Conditioning Vars - Observation Process Design
	  		conditioning.vars = conditioning.vars)
	# ---------------------- 
	# Save Index File 
	# ----------------------    
	st.matrix.list <- list(
		stem.directory = stem.directory, 
		pred.data.locs = pred.data$locs, 		
		cv.number=iii.cv, 		# subset of cv's
		stem.predictor.names=stem.predictor.names, 		   
		# --------------
		st.matrix.name = st.matrix.name,
		jdate.seq = jdate.seq,
		year.seq = year.seq,
		conditioning.vars=conditioning.vars)
	filename.tag <- 
        paste(results.dir,"st.matrix.list.",iii.cv,".RData",sep="")    
    save(st.matrix.list, file=filename.tag)
    # ------------------       
    ## KFW DF
    ## Local memory recovery block
    rm(D.stem,st.matrix.list)
    ## KFW gc()
} # end iii.cv - data folds    
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
## Clear the deck
rm(list = c("bs.rpart.maps", "conditioning.vars", "create.pd.grid", 
	"create.simple.STEM.ensemble", "D", "data.filename", 
	"D.erd.data.par.list", "D.erd.test.data.par.list", 
	"D.erd.train.data.par.list", "deviance.explained", 
	"ebirdReferenceDataFrame", "ensemble.partial.dependence", 
	"equal.wt.max.coverage.selection", "erdDataFile", "erdParameterListFile", 
	"exp.name", "fit.ensemble", "fit.stem", "halloween.maps", "iii.cv",
	"iii.year", "initizalize.map.grid", "jdate.seq", "make.erd.data", 
	"make.functional.data.design.matrix", "make.SPAT.COVAR.pred.data", 
	"make.spatial.erd.prediction.design", "map.tag", 
	"maximum.coverage.selection", "model.dir", "monthly.maps", "n.intervals", 
	"n.intervals.per.year", "n.red", "plot.diagnostics", 
	"plot.STEM.temporal.design", "plot.ST.ensemble", "plot.vi.bdt", 
	"point.in.polygon", "point.in.polygon.contours", "point.in.shapefile", 
	"poisson.accuracy", "poisson.deviance", "poisson.pearson", "pop.rpart", 
	"pred.data", "predictive.performance", "predictors.index", 
	"predict.stem.ST.matrix", "predict.ST.ensemble", "predict.st.matrix", 
	"predict.st.matrix.ebird.ref.data", "protocol.tag", "resp.family", 
	"response.index", "response.truncation.cutoff", "results.dir", "return.list", 
	"rotate.ST.basis.pred", "rotate.ST.basis.sample", 
	"rpart.ensemble.diagnostics", "sample.ST.ensemble", "seasonal.window", 
	"smooth.st.predictions", "spatial.density.contours", 
	"spatial.performance.plot", "spp.common.name", "spp.dir", "spp.list", 
	"stateMapEnv", "stem.map.inference.split", "STEM.partial.dependence", 
	"stem.ST.matrix.file.tag", "st.ttt.pred", "summarize.ensemble", 
	"summary.1D.PD.ensemble", "surface.maps", "test.set.prediction.filename", 
	"ttsplit", "ttt.statement", "unique.locs.splitting", 
	"year.seq", "zzz.max"))
if (debugOutput == TRUE) {
   rm(list = c("mem", "memoryMsg"))
}
## KFW gc()
# --------------------------------------------------------------------------
} #end function
# --------------------------------------------------------------------------




















