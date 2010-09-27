#------------------------------------------------------------------------------
# I envision ERD data creation this way 
# * STEM_erd.data.creation - processes data from CSV files
# * STEM_erd.data.subsetting - load and further subset data
# 
#  * Consider SRD & ERD data together as a single functional step 
# 		because they rely on the same parameters
#  ==> subsetting should also be done together
# 
# Kevin, we will need to talk about how to incorporate
# your work on ERD & NDVI data creation.  
# In general we want this to extend to other SRD with 
# temporally varying covariates.  
# 
# Kevin, I dont know where this fits
#------------------------------------------------------------------------------
# Load NDVI Data
#-----------------------------------------------------------------------------
## KFW
## vegetationIndexData <- read.csv(file="ebird_reference_data/processed_VI_Data_SRD.csv", na.strings = c("NA", "?"))
#vegetationIndexData  <- matrix(scan("ebird_reference_data/custom_vi.txt"), 18880842, 6, byrow=TRUE)
#print(class(vegetationIndexData))
#print(nrow(vegetationIndexData))
#print(ncol(vegetationIndexData))

testRpyCall <- function(object) {
   print(class(object))
   print(object)
}



#------------------------------------------------------------------------------
erd.srd.data.subsetting <- function(
			erd.data.filename,    #erd.data.tag,
			srd.pred.design.filename,
			spatial.extent.list, 
			temporal.extent.list, 
			## KFW speciesList,
			species.name,
			predictor.names, 
			response.family,
			srd.max.sample.size,
			split.par.list,
			response.truncation.cutoff=20){
 	#---------------------------------------------------------------------------
 	# Load SRD Data	#------------------------------------------------------------------------------------------------------------
  print(srd.pred.design.filename)
	load(file=srd.pred.design.filename)  # pred.data
		#dim(pred.data$D.pred)
		#dim(pred.data$locs)
	# ----------------------------------------------------------------------
	# Limit Spatial Extent by Point in Rectangle, Polygon, or ShapeFile
	# ----------------------------------------------------------------------   
	xxx <- pred.data$locs$x
	yyy <- pred.data$locs$y
	region.index <- rep(TRUE, nrow(pred.data$D.pred) )
	if (!is.null(spatial.extent.list)){
		## KFW if (spatial.extent.list$type == "rectangle"){
		if (spatial.extent.list[['type']] == "rectangle"){
			ttt.index <- ( 
						yyy > spatial.extent.list$lat.min & 
						yyy < spatial.extent.list$lat.max &
						xxx > spatial.extent.list$lon.min & 
						xxx < spatial.extent.list$lon.max )
			region.index <- (ttt.index & region.index)			  
			}
		  ## KFW if (spatial.extent.list$type == "polygon"){
		  if (spatial.extent.list[['type']] == "polygon"){
			ttt.index <- point.in.polygon(
					    xxx = xxx, 
					    yyy = yyy,
					    polygon.vertices = 
			spatial.extent.list$polygon.vertices)
			region.index <- (ttt.index & region.index)			  
			  }
		  ## KFW if (spatial.extent.list$type == "shapefile"){
		  if (spatial.extent.list[['type']] == "shapefile"){

			  ttt.index <- point.in.shapefile(
				sites = data.frame(lon=xxx, lat=yyy), 
				shape.dir=spatial.extent.list$shape.dir, 
				shape.filename=spatial.extent.list$shape.filename, 
				att.selection.column.name=
				       spatial.extent.list$att.selection.column.name,
				selected.shape.names=
				    spatial.extent.list$selected.shape.names) 
			  region.index <- (ttt.index & region.index)		  
			}				 		
	} 	# if (!is.null(spatial.extent.list)){    	    
	# ------------------
	# Subset SRD
	# ------------------
	srd.data <-NULL
	srd.data$D.pred <- pred.data$D.pred[region.index, ]
	srd.data$locs <- pred.data$locs[region.index, ]
		#dim(pred.data$D.pred)
		#dim(pred.data$locs)		
	rm(pred.data)
	## KFW gc()	
	# ------------------
	# Subset SRD
	# DMF 3.17.10
	# ------------------	
	if (!is.null(srd.max.sample.size)) {
		if (nrow(srd.data$D.pred) > srd.max.sample.size){
			ttt.index <- sample(x=c(1:nrow(srd.data$D.pred)), 
							size=srd.max.sample.size)
			srd.data$D.pred <- srd.data$D.pred[ttt.index, ]
			srd.data$locs <- srd.data$locs[ttt.index, ]
		}
	}
	# --------------------------


	#-----------------------------------------------------------------------------
	# Load ERD parameter data & Data	
        #	
        # Wish List for erd.data.creation 	
        # ** combine data & parameters into a single list object
	# ** save only index to identify train & test sets. There is no need to 	
        # 	save entire thing twice. 	
        #------------------------------------------------------------------------------
	#erdParameterListFile <- paste(data.dir, erd.data.tag, "erd.data.par.list.RData", sep="")
	#load(file=erdParameterListFile) #return.list
	#D.erd.data.par.list <- return.list
	
	#erdDataFile <- paste(data.dir, D.erd.data.par.list$erd.data.tag, "erd.data.RData", sep="")
	load(file=erd.data.filename) #    erdDataFile) #D
	# ----------------------------------------------------------------------
	# Limit Spatial Extent by Point in Rectangle, Polygon, or ShapeFile
	# ----------------------------------------------------------------------
	xxx <- D$LONGITUDE
	yyy <- D$LATITUDE
	region.index <- rep(TRUE, nrow(D) )
	if (!is.null(spatial.extent.list)){
		## KFW if (spatial.extent.list$type == "rectangle"){
		if (spatial.extent.list[['type']] == "rectangle"){
			ttt.index <- ( 
						yyy > spatial.extent.list$lat.min & 
						yyy < spatial.extent.list$lat.max &
						xxx > spatial.extent.list$lon.min & 
						xxx < spatial.extent.list$lon.max )
			region.index <- (ttt.index & region.index)			  
			}
		  ## KFW if (spatial.extent.list$type == "polygon"){
		  if (spatial.extent.list[['type']] == "polygon"){
			ttt.index <- point.in.polygon(
					    xxx = xxx, 
					    yyy = yyy,
					    polygon.vertices = 
			spatial.extent.list$polygon.vertices)
			region.index <- (ttt.index & region.index)			  
			  }
		  ## KFW if (spatial.extent.list$type == "shapefile"){
		  if (spatial.extent.list[['type']] == "shapefile"){
			  ttt.index <- point.in.shapefile(
				sites = data.frame(lon=xxx, lat=yyy), 
				shape.dir=spatial.extent.list$shape.dir, 
				shape.filename=spatial.extent.list$shape.filename, 
				att.selection.column.name=
				       spatial.extent.list$att.selection.column.name,
				selected.shape.names=
				    spatial.extent.list$selected.shape.names) 
			  region.index <- (ttt.index & region.index)		  
			}				 		
	} 	# if (!is.null(spatial.extent.list)){    	    
	# -------------------------------------------------------------------
	# -------------------------------------------------------------------
	# Limit Temporal Extent
	# -------------------------------------------------------------------	
	season.index <- rep(TRUE, nrow(D) )
	if (!is.null(temporal.extent.list)){ 
		# Convert JDATE + YEAR to single temporal index
		begin.tindex <- temporal.extent.list$begin.year + 
						temporal.extent.list$begin.jdate/366 
		end.tindex <- temporal.extent.list$end.year + 
						temporal.extent.list$end.jdate/366
		D.tindex <- D$YEAR + D$DAY/366 
		season.index <- D.tindex >= begin.tindex & 
						D.tindex <= end.tindex
	}
	# -------------------------------------------------------------------
	# ST extent
	# -------------------------------------------------------------------	
	regional.seasonal.index <- region.index & season.index
	sum(regional.seasonal.index)
	ebirdReferenceDataFrame <- D[regional.seasonal.index, ]
	rm(D)
	## KFW gc(D)
	#------------------------------------------------------------------------------------------------------------	
        # Train:Test Set Split :   maximum coverage, eq wt train-test split	
        #------------------------------------------------------------------------------------------------------------	
        D.split <- maximum.coverage.selection(locs=data.frame(x=ebirdReferenceDataFrame$LONGITUDE ,
                                                              y=ebirdReferenceDataFrame$LATITUDE),
                                              jdates=ebirdReferenceDataFrame$DAY,	
                                              #  vector length n
                                              grid.cell.min.lat = split.par.list$grid.cell.min.lat,	
                                              grid.cell.min.lon = split.par.list$grid.cell.min.lon, 
                                              min.val.cell.locs = split.par.list$min.val.cell.locs,
                                              fraction.training.data = split.par.list$fraction.training.data,
                                              mfrac = split.par.list$mfrac,	
                                              plot.it=split.par.list$plot.it)
	# -----------------------------------------------
			train.index <- D.split$train.index
	 		test.index <- D.split$test.index
	 		rm(D.split)
			## KFW response.index <-  names(ebirdReferenceDataFrame) %in% speciesList[[1]][1]
			response.index <- names(ebirdReferenceDataFrame) %in% species.name
			predictors.index <- names(ebirdReferenceDataFrame) %in% predictor.names
	 		train.data <- NULL
	 		test.data <- NULL
	 		# ---------------------
	 		train.data$X <- ebirdReferenceDataFrame[train.index, predictors.index]
	 		ttt.y <-  ebirdReferenceDataFrame[, response.index]
			train.data$y <- ttt.y[train.index]
			rm(ttt.y)
	 		train.data$locs$x <- ebirdReferenceDataFrame$LONGITUDE[train.index]
	 		train.data$locs$y <- ebirdReferenceDataFrame$LATITUDE[train.index]
	 		train.data$jdates <- ebirdReferenceDataFrame$DAY[train.index]
	 		# ------------------------------------
	 		test.data$X <- ebirdReferenceDataFrame[test.index,predictors.index]
	 		ttt.y <-  ebirdReferenceDataFrame[, response.index]
			test.data$y <- ttt.y[test.index]
			rm(ttt.y)
	 		test.data$locs$x <- ebirdReferenceDataFrame$LONGITUDE[test.index]
	 		test.data$locs$y <- ebirdReferenceDataFrame$LATITUDE[test.index]
	 		test.data$jdates <- ebirdReferenceDataFrame$DAY[test.index]
	 		# --------------------------------------------
	 		rm(ebirdReferenceDataFrame)
	# ----------------------------------------------------------------------
	#  ERD parameters
	# ----------------------------------------------------------------------
		#protocol.tag <- D.erd.data.par.list$protocol.tag  
			#c("traveling","stationary") #,"casual.obs")
		#if (D.erd.data.par.list$response.type == "occurrence") {
		#	resp.family <- "bernoulli"  # "gaussian" or "bernoulli"
		#	}
		#if (D.erd.data.par.list$response.type == "abundance"){
		#	resp.family <- "gaussian"  # "gaussian" or "bernoulli"
		#	}
	# --------------------------------
	if ( response.family =="bernoulli") {
		# ------------------------------------
		# Logical - where the predicted response is the 
		# probability of a positive/True class
		# -------------------------------------
		train.data$y <- as.factor( train.data$y > 0) # TRUE if positive
		test.data$y <- as.factor( test.data$y > 0) # TRUE if positive
		} 
	# Create Truncated Gaussian Response
	if ( response.family == "gaussian"){ 
		#
		# truncate responses @ 10 
		#sum(train.data$y > response.truncation.cutoff)
		train.data$y[train.data$y > response.truncation.cutoff] <- response.truncation.cutoff
		test.data$y[test.data$y >response.truncation.cutoff] <- response.truncation.cutoff
		}     
# --------------------------------------------------------------------------
	return.list <- list(
	 		train.index = train.index,
	 		test.index = test.index,
	 		#protocol.tag=protocol.tag,
	 		response.family=response.family,
	 		train.data = train.data, 
	 		test.data = test.data,
	 		srd.data = srd.data) 
# --------------------------------------------------------------------------
	return(return.list)
	}
# --------------------------------------------------------------------------


