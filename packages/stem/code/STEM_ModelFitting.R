

# --------------------------------------------------------------------
# --------------------------------------------------------------------
#
# cv.folds = 0 : fit complete training data, no splitting
# cv.folds >= 1: fit nfold data
#
# ---------------------------------------------------------------------
# Fit & Save The bagged rpart Ensemble
# ------------------------------------------------
# Note: Ensemble Model information is autmatically stored 
# with the tag ".ensemble.index.RData" in the model directory. 
# This is essential information along with the 
# ensemble parameter list. So we save that too.
# ----------------------
# Brieman rpart parameters
#control=rpart.control(cp=0,xval=0,minsplit=2))
# Limit infludence of any one point. 
# And for node-level predictions, it means that a
# single positive value may have a maximum of 
# 1/minbucket. Which was one 
#parms=list(split="information")) # bernoulli deviance 
# Its huge and all the information is in the index file          
# ---------------------------------------------------------------------
#
#
# TO DO: 
# ** Add functionality for 		
#		keep.data = TRUE,#		verbose = TRUE,
# and check functionality for RNG.seed in the fit.ensemble() 
# routine. 
# --------------------------------------------------------------------
# --------------------------------------------------------------------
# DMF 3.19.10 VT Changes
# 	* remove creation of stem.results.directories
stem <- function(train.data,
                 stem.directory,		
                 weights = NULL,
                 offset = NULL,
                 response.family = "bernoulli",	
                 cv.folds=0,
                 cv.folds.par.list=NULL,
                 stem.init.par.list,
                 base.model.par.list = NULL,
                 keep.data = TRUE,
                 verbose = TRUE, 
		 RNG.seed= 12345, 
		 block.save.size=100) # (training sample size x block.save.size ) 
{# begin function
# --------------------------------------------------------------------
# use constant tag value to simplify inputs
stem.model.tag <- "stem."
for (iii.cv in 1:cv.folds){
  print(paste("iii.cv", iii.cv))
	# -------------------------------------------------------------
	# Create Directories
	# -------------------------------------------------------------
		if (iii.cv == 1) {
			system(paste("mkdir ",stem.directory,sep=""), intern=TRUE)

                        if( "/" != substring(stem.directory, nchar(stem.directory), nchar(stem.directory))) {
			   stem.model.directory <- paste(stem.directory,"/model/",sep="")                          
                        } 
                        else {
			   stem.model.directory <- paste(stem.directory,"model/",sep="")
                        }

			system(paste("mkdir ",stem.model.directory,sep=""), intern=TRUE)
		}
		model.dir <- paste(stem.model.directory, 
						"stem.models.", as.character(iii.cv), "/",sep="")
		ttt.statement <- paste("mkdir ",model.dir,sep="")
		#print(ttt.statement)
		system(ttt.statement, intern=TRUE)
		#results.dir <- paste(stem.directory, 
		#				"stem.results.", as.character(iii.cv), "/",sep="")
		#ttt.statement <- paste("mkdir ",results.dir,sep="")
		#print(ttt.statement)
		#system(ttt.statement, intern=TRUE)
	# -------------------------------------------------------------
	# Split-Fold Training Data
	# -------------------------------------------------------------
  print(paste("cv.folds", cv.folds))
		if (cv.folds<=0) {
				cv.train.data <- list(
					X = train.data$X,
					y = train.data$y,
					locs = train.data$loc,
					jdates = train.data$jdates)
                       }
		if (cv.folds>0) {
			D.split <- maximum.coverage.selection(
						locs=data.frame(
							x=train.data$locs$x ,
							y=train.data$locs$y),
						jdates=train.data$jdates,	
						grid.cell.min.lat = cv.folds.par.list$grid.cell.min.lat,						grid.cell.min.lon = cv.folds.par.list$grid.cell.min.lon,						min.val.cell.locs = cv.folds.par.list$min.val.cell.locs,						fraction.training.data = cv.folds.par.list$fraction.training.data,						mfrac = cv.folds.par.list$mfrac,						plot.it=cv.folds.par.list$plot.it)							
			cv.train.data <- list(
					X = train.data$X[ D.split$train.index, ],
					y = train.data$y[ D.split$train.index ],
					locs = 
						list(x=train.data$loc$x[ D.split$train.index ],
							y=train.data$loc$y[ D.split$train.index ]),
					jdates = train.data$jdates[ D.split$train.index ])

		}
	# -------------------------------------------------------------
	# Create Ensemble based on Training Data
	# -------------------------------------------------------------

  print("creating ensemble")
	stem.par.list <- create.simple.STEM.ensemble(
		ensemble.data.locs = cv.train.data$locs,
		ensemble.data.jdates = cv.train.data$jdates,
		#ensemble.model.filename = stem.model.tag,
		# --------------------------------------------------
		# Spatial Design
		# --------------------------------------------------
		spatial.extent.list = stem.init.par.list$spatial.extent.list ,  #default to train data convex hull 
		spatial.region.par.list = stem.init.par.list$spatial.region.par.list, 
			#~ # Number of MC regionalizations for each time interval
			#~ n.mc.regions=1, 
			#~ # Underlying Coverage Grid
			#~ grid.cell.min.lat = 1.5*(iii.scale^0.5), #5 degrees
			#~ grid.cell.min.lon = 2*(iii.scale^0.5), # 10 degrees
			#~ n.centers.per.region = 1, # Density Dependent!!!
			#~ # Maximum Rectangular Region Growth Factor
			#~ #max.random.scale.factor = 0.25,
			#~ # define minimum area & sample size of rectangles
			#~ regional.cell.min.lat = 3.00*iii.scale,
			#~ regional.cell.min.lon = 4.00*iii.scale,
			#~ min.data.size = 25),
		# --------------------------------------------------
		# Temporal Design: 
		#		Slice year into n.intervals prediction points
		# --------------------------------------------------
			n.intervals = stem.init.par.list$n.intervals,  #add 1!    # 81 for migration
			begin.jdate= stem.init.par.list$begin.jdate,
			end.jdate = stem.init.par.list$end.jdate,
			season.window.width= stem.init.par.list$season.window.width,  #40       # Fitting window
			prediction.window.width=stem.init.par.list$prediction.window.width,  #36
		# --------------------------------------------------
		# Sampling
		# --------------------------------------------------
			sample.ensemble.function = sample.ST.ensemble,
			sampling.par.list = stem.init.par.list$sampling.par.list, 
				    #~ split.by.location = FALSE,
				    #~ # if TRUE uses locs == ensemble.data.locs
				    #~ ST.basis.rotation = FALSE,
				    #~ # if TRUE assumes {lat,lon} ={$y, $ x} 
				    #~ # and julian date == $JDATES 
				    #~ p.train=0.63),
		# --------------------------------------------------
		# Prediction
		# --------------------------------------------------
			predict.ensemble.function = predict.ST.ensemble)
# ---------------------------------------------------------------------

	# -------------------------------------------------------------
	# STEM Fit
	# -------------------------------------------------------------
  print("running fit")
		D.ttt <- fit.ensemble(
			train.data = cv.train.data, 
			resp.family= response.family,
			filename = paste(model.dir,stem.model.tag,sep=""),
			RNG.seed = RNG.seed, 
			ensemble.par.list = stem.par.list,
			ensemble.weights = weights,
			block.save.size=block.save.size,
			control=base.model.par.list)
	# -------------------------------------------------------------	# Pack additional info into stem.par.list	# -------------------------------------------------------------
	stem.par.list$cv.fold.train.index <- D.split$train.index
	stem.par.list$realized.sample.par <- D.ttt$realized.sample.par
	stem.par.list$RNG.seed <- D.ttt$RNG.seed
	stem.par.list$function.call <- D.ttt$function.call
	D.stem <- stem.par.list
	save(D.stem, 
		file = paste(model.dir, "stem.model.par.list.", 
					iii.cv,".RData" , sep = ""))
	rm(D.stem, D.split, stem.par.list, D.ttt)
	## KFW gc()
	# -------------------------------------------------------------	# Debug output	# -------------------------------------------------------------
         if (debugOutput == TRUE) {
       	     print("----- Memory usage before system() call gc() -----")
             memoryMsg <- paste("Memory info =", gc(verbose=TRUE), sep=" ")
             print(memoryMsg)
             print("----- Memory usage before system() call object.size()-----")
             mem <- sapply(ls(), function(x) object.size(get(x)))
             print(mem)
             print("----- Sum of object.size()-----")
             print(sum(mem))
          }
} ## End for (iii.cv in 1:nnn.cv)
# -----------------------------------------------------------------------------
# No Return Value Object
} # end function
# --------------------------------------------------------------------

        
