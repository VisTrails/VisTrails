
# STEM LIBRARY INDEX
# ---------------------------------------------------------
# FUNCTION: Create Simple ST Ensemble, 5.1.09
#    * cleaned
#
# sample.ST.ensemble <- function(    5.1.09
#    * cleaned, consistent use of locs
#    * STEM ensemble requires ensemble.locs & ensemble.jdates
#      WTIHOUT requiring predictors ($x, $y, & $JDATE)
#    * These predictors are required if basis rotation used!
#
# rotate.ST.basis.sample - added ensemble.locs
# 	this means that you can split by location within DT
#    without having layt & lon predictors!
#
# FUNCTION: Plot STEM Spatial Design
#
# FUNCTION: predict.ST.ensemble -
# 		explicit locs & jdate incices 
# 		better handling of null predictions
# 		verified
#
# FUNCTION: predict.ST.matrix
# FUNCTION: STEM.partial.dependence
# 	** NOT yet working for lat,lon effects!!!
# 
# 
# plot ST design Function
# ---------------------------------------------------------
# STEM Specific functionality that is Needed:
# --------------
# Histogram of ensemble sample sizes
# Support Map at a point
# Support Depth Map
# -------------------------------------------








# ---------------------------------------------------------
# FUNCTION: Create Simple ST Ensemble
# D Fink
# 5.1.09
# ---------------------------------------------------------
#
# Becuase the spatial regions are generated randomly, I want
# to incorporate as much of this variation as possible in
# the sample. We use a different spatial
# regionalization for each time interval.
#
# Note with spatial design.
# if locations are only unique locations, then min.data.size
# if applied to unique locations. Otherwise min.data.size
# is applied to total number of data pts w/in STEM cell.
#
#
# -----------------------------------------------------------
# Temporal Design - Seasonal Tiles
# -----------------------------------------------------------
# 1) jdate.seq are centers of symmetric temporal window
# 	Evenly spaced slices throughout year
#  ** begin.window = vector of jdates for beginning of window
# 					 centered at jdate.seq
#  ** end.window = same
#  ** begin.pred.window = is the beginning of the prediction
# 							window. This controls how the
# 							averaging of the ensemble is done.
#		Eg. If prediction.window.width <
# 		season.window.width. This can be used to remove bias
# 		often encountered when predicting at end of time series.
# 		If prediction.window.width > season.window.width
# 		then this allows forecasting, predictions beyond the
# 		time horizon of the data. This should give a more
# 		realistic errors if goal is forecasting.
# ------------------------------------------------------------
#
# INPUT:
# -----------
#     y = (n x 1) full response vector
#         (Should I remove this or make it optional??)
#     X = (n x p) full design matrix
#
# sampling.par.list=NULL
# split.by.location==TRUE
#   X.loc = data.frame used to split data.
#           note - the NROWS(X.loc) must equal NROWS(X) the
#           training design!!!
#   p.train = proportion data sampled for training
#                  # Default ==> Use all available data for
#                  # test & training sets by including all replicate locations.
#                  m.frac <- 1.0
# OUTPUT:
# -------------
#   Regional.polygons = data.frame with components
#       x = vertices of polygons
#       y = vertices of polygons
#       region.code = sequential number code,
#
#   Cluster.codes = (rows = NROW(ensemble.data$X)
#                     cols =  n.mc.regions)
#                 contains the clusterings for each mc realization
# regional.polygons = data.frame that defines the regional polygons
#                     the partition the global region.
#                     Here, regions are defined by clustering algorithm
#                     number of polygons = n.region
#                     (longitude, latitude, region.number)
# design.summary <- Center of region mass
#            (good for Knot locations & text titles)
# ----------------------------------------------------------------------
# Future Development -
# ** add logic to cycle through limited
# 	number of n.mc.regions for all btrial x n.interval combinations.
# ------------------------------------------------------------
create.simple.STEM.ensemble <- function(
		# Data
		# ------------------------
			ensemble.data.locs, # <- data.frame(x=ensemble.data$X$x, y=ensemble.data$X$y)
			ensemble.data.jdates, 	# "JDATE" = Julian date from 0 to 365
		# ------------------------
		# Spatial Design
		# ------------------------
			spatial.region.par.list, # All Random Rectangle Inits
		# Temporal Design
		# ------------------------
			n.intervals, 		# Slice year into n.intervals prediction points
			begin.jdate = 0,       #
			end.jdate = 365,
			season.window.width,     # Fitting/Training window width in days
			prediction.window.width, # Prediction window width in days
		# Sampling parameters (pass through only)
		# ------------------------------------
			sample.ensemble.function,
			sampling.par.list,
			predict.ensemble.function,
			spatial.extent.list=NULL)
{# ---------------------------------------------------------
#	# ----------------------------------------------------------------------
#	# Formal parameter Test Values
#	# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
# Temporal Design - Seasonal Tiles
# ----------------------------------------------------------------------
	jdate.seq <- seq(from=begin.jdate, to=end.jdate, length=(n.intervals+1))
	jdate.seq <- round((jdate.seq[2:(n.intervals+1)] + jdate.seq[1:(n.intervals)])/2)
	begin.window <- jdate.seq - round(season.window.width/2)
	begin.window[  begin.window < 0 ] <- begin.window[  begin.window < 0 ] + 365
	end.window <- jdate.seq + round(season.window.width/2)
	end.window[  end.window > 365 ] <- end.window[ end.window > 365 ] - 365
	# ----------------------
	begin.pred.window <- jdate.seq - round(prediction.window.width/2)
	begin.pred.window[  begin.pred.window < 0 ] <-
			begin.pred.window[  begin.pred.window < 0 ] +365
	end.pred.window <- jdate.seq + round(prediction.window.width/2)
	end.pred.window[  end.pred.window > 365 ] <-
			end.pred.window[ end.pred.window > 365 ] -365

# ----------------------------------------------------------------------
# Spatial Design - Random Rectangular Regional Tiles
# ----------------------------------------------------------------------
	# --------------------------------------------------------------------------------------------
	# Inits
	# --------------------------------------------------------------------------------------------
		n.mc.regions <- spatial.region.par.list$n.mc.regions
		# Underlying Coverage Grid
		grid.cell.min.lat <- spatial.region.par.list$grid.cell.min.lat
		grid.cell.min.lon <- spatial.region.par.list$grid.cell.min.lon
		# Randomized Rectangular Regions
		n.centers.per.region <- spatial.region.par.list$n.centers.per.region
		regional.cell.min.lat <- spatial.region.par.list$regional.cell.min.lat
		regional.cell.min.lon <- spatial.region.par.list$regional.cell.min.lon
		min.data.size <- spatial.region.par.list$min.data.size
		# Unpack location info
		# ----------------------
		xxx <- ensemble.data.locs$x # Longitude
		yyy <- ensemble.data.locs$y # Longitude
		lat.min <- min(yyy)
		lat.max <- max(yyy)
		lon.min <- min(xxx)
		lon.max <- max(xxx)
		iii.count <- 0
# --------------------------------------------------------------------------------------------
# Loop MC Regions - one SET of regions for each MC x Time Interval Combination
# --------------------------------------------------------------------------------------------
regional.polygons <- NULL
design.summary <- NULL
for (iii.interval in 1:n.intervals){
for (iii.mc.region in 1:(n.mc.regions)){  #  1){ #
	# ----------------------------------------------------------------------
	# Define "Coverage" Grid
	# ----------------------------------------------------------------------
	# Store grid as x-vector of grid vertices
	# and y-vector of grid vectices. Both of these are bookended
	# with their min & max values.
	# 0) Initialize with x-min,
	# 1) randomize position of first vertex
	# 2) lay down equally spaced grid until x.max reached
	# ** Repeate for y-axis
	# --------------------------------------------------
  	# --------------------------------------------------
   	# Randomize Coordinate for first grid cell boundary
   	# --------------------------------------------------
	r.lat <- runif(1,min=0, max=grid.cell.min.lat)
	r.lon <- runif(1,min=0, max=grid.cell.min.lon)
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
	   # -------------------------
	   # Test Plot of Grid
	   # -------------------------
	   #plot(xxx,yyy, cex=0.25)
	   #require(maps)
	   #map("state", add=TRUE)
	   #for (jjj in 1:length(grid.yyy)){
	   #        lines(c(lon.min,lon.max),rep(grid.yyy[jjj],2))
	   #        }
	   #for (jjj in 1:length(grid.xxx)){
	   #        lines(rep(grid.xxx[jjj],2),c(lat.min,lat.max))
	   #        }
   # --------------------------------------------------------------
   # -------------------------------------------------------
   # Cycle over Columns(xxx_iii) within Given Row (yyy_jjj)
   # Sample Random Centers within Grid Cells
   # -------------------------------------------------------
   grid.centers.x <- NULL
   grid.centers.y <- NULL
   for (jjj in 1:(length(grid.yyy)-1)){
   for (iii in 1:(length(grid.xxx)-1)){
	   ttt.index <- xxx >= grid.xxx[iii] & xxx < grid.xxx[iii+1] &
	                yyy >= grid.yyy[jjj] & yyy < grid.yyy[jjj+1]
	   ttt.df <- data.frame(xxx=xxx[ttt.index], yyy=yyy[ttt.index])
	   #ttt.u <- unique(ttt.df)
	   # Check for at least 1 data point in the coverage cell.
	   # If so, then Sample Random Centers
	   # ----------------------------------------
	   if (NROW(ttt.df) > 0 ){
		  n.centers <- n.centers.per.region
   	  	  grid.centers.x <-c(grid.centers.x,
		   	   			   runif(n.centers,
								min=grid.xxx[iii],
								max=grid.xxx[iii+1]))
   	  	  grid.centers.y <-c(grid.centers.y,
			   			   runif(n.centers,
								min=grid.yyy[jjj],
								max=grid.yyy[jjj+1]))
	   } # endif
   # ---------------
   } #iii
   } #jjj
   grid.centers <- data.frame(x=grid.centers.x,
                              y=grid.centers.y)
   rm(grid.centers.x)
   rm(grid.centers.y)
	   #dim(grid.centers)
	   # plot
	   #points(grid.centers, cex=1.5, pch=19, col=2)
   # --------------------------------------------------
   # Filter Grid Centers to lie within Target Boundary
   # --------------------------------------------------
	  ttt.index <- c(1:NROW(grid.centers))
	  if (!is.null(spatial.extent.list)){
	   	 if (spatial.extent.list$type == "shapefile"){
			  ttt.index <- point.in.shapefile(
				sites = data.frame(lon=grid.centers$x,
	                                  lat=grid.centers$y),
				shape.dir=spatial.extent.list$shape.dir,
				shape.filename=spatial.extent.list$shape.filename,
				att.selection.column.name=
			               spatial.extent.list$att.selection.column.name,
				selected.shape.names=
			            spatial.extent.list$selected.shape.names)
			  }
	    	  } 	# if (!is.null(spatial.extent.list)){
	   # Use Convex Hull around ensemble.data to get approximate boundary
	   # ------------------------------------------------------------
	   if (!is.null(spatial.extent.list)){
		if (spatial.extent.list$type == "convexhull"){
		 chull.index <- chull(ensemble.data.locs )
	   	 ttt.index <- point.in.polygon(
		  			    xxx = grid.centers$x,
		  			    yyy = grid.centers$y,
		  			    polygon.vertices = ensemble.data.locs[chull.index,])
	   }}
   # -----------------------------------------
   grid.centers <- grid.centers[ttt.index,]
	   # -----------------------------------------
	   # plot check
	   # -----------------------------------------
	   #points(grid.centers, cex=1.0, pch=19, col=3)
	   #cat(dim(grid.centers), "\n")
	   #for (jjj in 1:length(grid.yyy)){
	   #        lines(c(lon.min,lon.max),rep(grid.yyy[jjj],2))
	   #        }
	   #for (jjj in 1:length(grid.xxx)){
	   #        lines(rep(grid.xxx[jjj],2),c(lat.min,lat.max))
	   #        }
	   # --------------
# --------------------------------------------------------------------------------------------
# Cycle over Regions - Check for minimum data & area requirements
# Grow Rectanges as necessary
# --------------------------------------------------------------------------------------------
  	for (iii in 1:NROW(grid.centers)) {
      # Make Intial Rectangle
      # ----------------------
           center.lon <- grid.centers$x[iii]
	      center.lat <- grid.centers$y[iii]
	      r.lat <- regional.cell.min.lat/2
       	 r.lon <- regional.cell.min.lon/2
		 regional.rectangle <- data.frame(
		 x= c((center.lon-r.lon), (center.lon-r.lon),
	           (center.lon+r.lon), (center.lon+r.lon), (center.lon- r.lon)),
		 y= c((center.lat-r.lat), (center.lat+r.lat),
	           (center.lat+r.lat), (center.lat-r.lat), (center.lat-r.lat)) )
		 # Clip X & Y coordinates: maximum is
		 # the rectangle bounding the data PLUS
		 # an essential small (epsilon) boundary. This is essential 
		 # to include "boundary points" with the point in polygon 
		 # routines that I am using. They points that lie 
		 # on the lower polygon boundaries. 
		 # --------------------------------------------------
		 epsilon <- 1e-10
		 regional.rectangle$x[ regional.rectangle$x > max(xxx)] <- max(xxx)+epsilon
		 regional.rectangle$x[ regional.rectangle$x < min(xxx)] <- min(xxx)-epsilon
		 regional.rectangle$y[ regional.rectangle$y > max(yyy)] <- max(yyy)+epsilon
		 regional.rectangle$y[ regional.rectangle$y < min(yyy)] <- min(yyy)-epsilon
	# --------------------------
	# Loop over all ST windows/extents/regions
	# Record vector of Regional-seasonal sample sizes
	# Test for minimum sample size requirements
	# --------------------------
          # Spatial Region Index
		rr.index <- point.in.rectangle(
		  			    xxx = ensemble.data.locs$x,
		  			    yyy = ensemble.data.locs$y,
		  			    polygon.vertices = regional.rectangle )
	     # Seasonal Index
		if ((begin.window[iii.interval] < end.window[iii.interval])) # non-Winter
		   season.index <- ensemble.data.jdates >= begin.window[iii.interval] &
 			 ensemble.data.jdates <= end.window[iii.interval]
		if ((begin.window[iii.interval] > end.window[iii.interval])) # Winter
		   season.index <-ensemble.data.jdates >= begin.window[iii.interval] |
                ensemble.data.jdates <= end.window[iii.interval]
	          # regional & Seasonal indices
   		ttt.index <- rr.index & season.index
   		# Now see how many unique locations there
   		# are among the selected/identified points
   		# ------------------------------------------
   		u.locs <- unique(data.frame(ensemble.data.locs$x[ttt.index],
	                            ensemble.data.locs$y[ttt.index]))
		   # number of unique locs
 		temp.samp.sizes <- NROW(u.locs) #sum(ttt.index)
 	# -------------------------------
	# If minium data size is met for
	# ALL Temporal Windows in that region
	# Then we record its name in the book of
	# regional names. Otherwise, we ignore that region.
	# -------------------------------
	# 4) Summarize Regions
	# -------------------------------
	if (temp.samp.sizes > min.data.size) {
	   iii.count <- iii.count + 1
		regional.polygons <- rbind(regional.polygons,
		   data.frame(
		     	    regional.rectangle,
	           	    region.number=rep(iii.count, NROW(regional.rectangle)),
	          	    region.mc = iii.mc.region,
	          	    time.intervals=iii.interval))
		design.summary <- rbind(design.summary,
		   data.frame(
		   		    x.center=center.lon,
		   		    y.center=center.lat,
			  	    region.number=iii.count,
				    region.mc=iii.mc.region,
	    			    time.intervals=iii.interval,
                        unique.locs = temp.samp.sizes))
    }
   	# -------------------------------
    # 5) plot final region
    # -------------------------------
 	#polygon(regional.rectangle, border=iii+3)
    #points(center.lon, center.lat, col=iii+3, pch=19)
    #cat("Region ",iii," :",sum(rr.index),"\n")
# ------------------------------------------------
} # end loop over regions iii
# ------------------------------------------------
iii.count <- 0
# ------------------------------------------------
}} # end loop over MC x Time Interval Combinations
# --------------------------------------------------------------------------------------------
    #names(design.summary)
    #dim(design.summary)
    #names(regional.polygons)
    #dim(regional.polygons)
    # -----------------------------------------------------------------
    # -------------------------------------------------
    # Cleanup & Return
    # -------------------------------------------------
    return.list <- list(
        ensemble.data.locs=ensemble.data.locs, # <- data.frame(x=ensemble.data$X$x, y=ensemble.data$X$y)
        ensemble.data.jdates=ensemble.data.jdates, 	# "JDATE" = Julian date from 0 to 365
        # Spatial
        # --------
            n.ensemble.models = NROW(design.summary),
            regional.polygons=regional.polygons,
            design.summary = design.summary,
            spatial.region.par.list = spatial.region.par.list,
        # Temporal
        # ---------
			n.intervals=n.intervals, 		# Slice year into n.intervals prediction points
			begin.jdate = begin.jdate,       #
			end.jdate = end.jdate,
			season.window.width=season.window.width,     # Fitting/Training window width in days
			prediction.window.width=prediction.window.width, # Prediction window width in days
            begin.window=begin.window,
            end.window=end.window,
            begin.pred.window=begin.pred.window,
            end.pred.window=end.pred.window,
        # Sampling
        # -----------------------
            sample.ensemble.function = sample.ensemble.function,
            sampling.par.list = sampling.par.list,
        	predict.ensemble.function = predict.ensemble.function)
# ---------------------------------------- -----------------
    return(return.list)
# ---------------------------------------- -----------------
}# end Create STEM ensemble Function
# ---------------------------------------------------------



# ---------------------------------------------------------
# sample.ST.ensemble
# ---------------------------------------------------------
# Generate a Sample from a SINGLE ST.ensemble model
# 4.13.09 - modifications
# ** if there are no data in stem cell, skip that cell.
# ---------------------------------------------------------
sample.ST.ensemble <- function(
                          ensemble.model.number,
                          ensemble.data,
                          ensemble.par.list,
                          diagnostic.plot = FALSE)
{# -----------------------------------------------------------
# -----------------------------------------------------------
# Formal Parameter TEST Values
# -----------------------------------------------------------
	#ensemble.model.number <- 100
	#ensemble.data <- train.data
# -----------------------------------------------------------
# Inits
# -----------------------------------------------------------
	return.list <- NULL
	# -----------------
	n.ensemble.models <- ensemble.par.list$n.ensemble.models
	# Check ensemble.model.number
	if (ensemble.model.number > n.ensemble.models)
		stop(paste("Error: There are only ", n.ensemble.models,
			" ensemble models. "))
	# --------
	ensemble.data.locs <- ensemble.par.list$ensemble.data.locs
	ensemble.data.jdates <- ensemble.par.list$ensemble.data.jdates
# -----------------------------------------------------------
# Select Temporal Window
# -----------------------------------------------------------
	iii.interval <- 
		ensemble.par.list$design.summary$time.intervals[ensemble.model.number]
	sw.obj <- seasonal.window(
			begin.window = ensemble.par.list$begin.window[iii.interval],
			end.window = ensemble.par.list$end.window[iii.interval],
			p.data= ensemble.data)
			
#cat("   iii.iterval=",iii.interval,	
#	ensemble.par.list$begin.window[iii.interval],
#	ensemble.par.list$end.window[iii.interval],"\n")
#readline()	
#print(
#	cbind(ensemble.par.list$begin.window, ensemble.par.list$end.window)	)
	
			
# -----------------------------------------------------------
# Check that there are data!!!
# -----------------------------------------------------------
	if (sum(sw.obj$season.index) > 0){
# -----------------------------------------------------------
# Select Region
# -----------------------------------------------------------
	# Index into regional polygons
	region.number <- ensemble.par.list$design.summary$region.number[ensemble.model.number]
	region.mc <- ensemble.par.list$design.summary$region.mc[ensemble.model.number]
	#**** Requires temporal index
	# *** 4.13 Added temporal interval
	r.index <- (ensemble.par.list$regional.polygons$region.mc == region.mc &
		ensemble.par.list$regional.polygons$region.number == region.number &
		ensemble.par.list$regional.polygons$time.intervals == iii.interval )
	# Index into p.data Training set
	region.given.season.index <- point.in.rectangle(
		# = ttt.data$X$x
		xxx = ensemble.data.locs$x[sw.obj$season.index],
		# = ttt.data$X$y
		yyy = ensemble.data.locs$y[sw.obj$season.index],
		polygon.vertices = ensemble.par.list$regional.polygons[r.index,1:2])
# -----------------------------------------------------------
# Check that there are data!!!
# -----------------------------------------------------------
	if (sum(region.given.season.index) > 0){
	# -----------------------------------------------------------
	# Indexing Verification
	# -----------------------------------------------------------
	# 	dim(ensemble.data$X)        # size training data
	#    # Seasonal index = logical index into training data
	#    length(sw.obj$season.index)
	#    sum( sw.obj$season.index)
	#    # region.given.season.index = logical index into seasonal subset
	#    length(region.given.season.index)
	#    sum(region.given.season.index)
	#    # sample.data$row.index = numeric index into regional-seasonal subset
	#    length(sample.data$row.index)
	# -------------------------------------
	# numerical index from training data to
	# regional-seasonal OOB/IB samples
	# -------------------------------------
	seasonal.num.ind <- c(1:length(sw.obj$season.index))[sw.obj$season.index]
	#length(seasonal.num.ind)
	reg.sea.num.ind <- seasonal.num.ind[region.given.season.index]
# -----------------------------------------------------------
# Sampling and Data Transformations
# -----------------------------------------------------------
	# Sample with rotate.ST.basis.sample()
	sample.data <- rotate.ST.basis.sample(
		train.data = list(
			X = ensemble.data$X[reg.sea.num.ind,],
			y = ensemble.data$y[reg.sea.num.ind]) ,
		train.locs =ensemble.data.locs[reg.sea.num.ind , ] ,
		train.jdates = ensemble.data.jdates[reg.sea.num.ind  ],
		sampling.par.list = ensemble.par.list$sampling.par.list)

# -----------------------------------------------------------
# Check that there are data!!!
if (length(sample.data$row.index) > 0){
# ----------------------------------------------
	# ----------------------------------
	# Final Indexing Information
	# ----------------------------------
	#length(reg.sea.num.ind)
	ib.reg.sea.num.ind <- reg.sea.num.ind[sample.data$row.index]
	#length(oob.reg.sea.num.ind)
	# -----------------------
	oob.reg.sea.num.ind <- setdiff(reg.sea.num.ind,ib.reg.sea.num.ind)
	#length(ib.reg.sea.num.ind)
	#length(oob.reg.sea.num.ind)+ length(ib.reg.sea.num.ind)

# -----------------------------------------
# Visual Verification Plot
#   Illustrating some fancy sampling!
# -----------------------------------------
	if (diagnostic.plot == TRUE) {
		#windows()
		# All training points
		plot( ensemble.data.locs$x, ensemble.data.locs$y, pch=19, cex=0.5)
		map('state',add=TRUE, lwd=2, col="yellow")
		map('state',add=TRUE, lwd=1, col="black")
		# -----------------------------------------------
		# Seasonal Points
		points(ensemble.data.locs$x[seasonal.num.ind],
			ensemble.data.locs$y[seasonal.num.ind],
			col="red", cex=1.0)
		# -----------------------------------------------
		# Regional-Seasonal Points
		points(ensemble.data.locs$x[reg.sea.num.ind],
			ensemble.data.locs$y[reg.sea.num.ind],
			col="blue", cex=1.5)
		polygon(ensemble.par.list$regional.polygons[r.index,1:2],
			border="blue")
		# ----------------------------------------------
		# IB/OOB points
		points(ensemble.data.locs$x[oob.reg.sea.num.ind],
			ensemble.data.locs$y[oob.reg.sea.num.ind],
			col="green", cex=2.0, lwd=2)
		points(ensemble.data.locs$x[ib.reg.sea.num.ind],
			ensemble.data.locs$y[ib.reg.sea.num.ind],
			col="purple", cex=2.0, lwd=2)
	}
	# -------------------------------------------------
	# Cleanup & Return
	# -------------------------------------------------
	return.list <- list(
		# These are the sampled ("in bag") data
		X = sample.data$X,
		y = sample.data$y,
		# Numerical IB & OOB Indices into formal parameter ensemble.data
		oob.num.ind = oob.reg.sea.num.ind,
		ib.num.ind = ib.reg.sea.num.ind,
		#unique.locs.split = sample.data$dsplit,
		realized.par =  sample.data$realized.par)
} # seasonal window check end ifs checking for data in stem cell
}  # #sw.obj$season.index
} # bs - subsampling sampled
	return(return.list)
# ---------------------------------------------------------
}# end Function sample.ST.ensemble
# ---------------------------------------------------------



# ---------------------------------------------------------
# Sample with ST Basis Rotation
# ---------------------------------------------------------
# This function is identical to simple.sample,
# except for the rotation and the sister function
#     rotate.ST.basis.pred()
# Note: I am going to start with hard coded
# rotation code.
#
#
# ---------------------------------------------------------
rotate.ST.basis.sample <- function(
				   train.data,
				   train.locs,
				   train.jdates,
				   sampling.par.list=NULL){
    # ------------------------------------------------
    # Inits
    # ------------------------------------------------
    n <- NROW(train.data$X)
    realized.par <- NULL
    dsplit <- NULL
    # ------------------------------------------------
    # Check sampling.par.list for "RND.seed"
    # ------------------------------------------------
    if (!is.null(sampling.par.list)) {
      if (sum(names(sampling.par.list)=="RNG.seed") > 0)
          set.seed(sampling.par.list$RNG.seed)
          }
    # -----------------------------------------------------------
    # Check for Sampling with ST Basis Rotation
    # ----------------------------------
    # requires variables named
    #  "x" - lon coordinate
    #  "y" - lat coordinate
    #  "JDATE" - julian date
    # --------------
    #  ==> this is a way of introducing Data Transformations
    #  or randomization into the model. perhaps this may be
    #  a nice way of icncorporating latent structure???
    # -----------------------------------------------------------
    if (sampling.par.list$ST.basis.rotation == TRUE){
	    # ------------------------------------------------
	    # Random Rotation of "Cartesian" Lat-Lon Plane
	    #   and Random cutting of the Julian Date Circle
	    # ------------------------------------------------
	    theta.prime <- runif(1, min=0, max=2*pi)
	    train.data$X$x <- train.data$X$x*cos(theta.prime) - train.data$X$y*sin(theta.prime)
	    train.data$X$y <- train.data$X$x*sin(theta.prime) + train.data$X$y*cos(theta.prime)
	    # ------------------------------------------
	    # Random rotation of Julian Date line
	    theta2.prime <- round(runif(1, min=0, max=365))
	    train.data$X$JDATE <-  train.data$X$JDATE + theta2.prime
	    train.data$X$JDATE[train.data$X$JDATE > 365] <- train.data$X$JDATE[train.data$X$JDATE > 365] - 365
	    realized.par <- c(theta.prime, theta2.prime)
	    }

    # -------------------------------------------------
    # Split Data into Train:Test sets with Unique Locations
    # -------------------------------------------------
    if (!is.null(sampling.par.list$split.by.location)){
      if (sampling.par.list$split.by.location==TRUE){
		 # ------------------------------------
		 # train.locs = data.frame( x, y)
           # -----
           # m.frac
           if (is.null(sampling.par.list$m.frac))
                  # Default ==> Use all available data for
                  # test & training sets by including all replicate locations.
                  m.frac <- 1.0
           if (!is.null(sampling.par.list$m.frac))
                  m.frac <- sampling.par.list$m.frac
           # -------
           # p.train
           p.train <- NULL
            if (!is.null(sampling.par.list$p.train))
                p.train <- sampling.par.list$p.train
            if (is.null(sampling.par.list$p.train))
                # Bootstrap proportion as default
                p.train <-  0.63
           # --------
		       dsplit <- unique.locs.splitting(
                              locs=train.locs,
                              p.train=p.train,
                              m.frac=m.frac)
		       bindex <- dsplit$train.locs.multiple
	         # default is to pass back train.locs.multiple
	     }}

    # -------------------------------------------------
    # Split Data Randomly - w/o respect to anything else
    # -------------------------------------------------
    if (is.null(sampling.par.list$split.by.location) |
      (!is.null(sampling.par.list$split.by.location) &
       sampling.par.list$split.by.location==FALSE)) {
        # ------------------------------------------------
         # -------------------------------------------------
        # Random Sampling
        # -------------------------------------------------
    		if (!is.null(sampling.par.list$p.train)){
  		 	bindex <- sample( c(1:n), 
			   	  round(n*sampling.par.list$p.train) , 
					replace=FALSE)
          }
        # Default is to sample with replacement
    		if (is.null(sampling.par.list$p.train))
		    bindex <- round(1 + (n-1)*runif(n))
    } # end random split
     # -------------------------------------------------

    # -------------------------------------------------
    # Cleanup & Return
    # -------------------------------------------------
    return.list <- list(
        X = train.data$X[bindex,],
        y = train.data$y[bindex],
        row.index = bindex,
        unique.locs.split = dsplit,
        realized.par = realized.par)
    return(return.list)
# ---------------------------------------------------------
}# end Function
# ---------------------------------------------------------

# ---------------------------------------------------------
# Predict with ST Basis Rotation
# ---------------------------------------------------------
# The prediction-sampling functions need to
# apply the same design transformations that were
# used on the training data to subsequent prediction
# designs. Here the "Cartesian" latxlon and Julian date
# transformation are performed.
#
# INPUT:
#     X = (n x p) full design matrix (unrotated)
#     realized.par = c(theta.prime, theta2.prime)
#                     rotation parameters
#
# OUTPUT:
#     X = (nnn x ppp) newly rotated prediction matrix
#
# NOTE
# -----------
# response could be made optional parameter,
# This might be a nice way to deal with
# response transformations??? Like
# box-cox parameterization??
# ----------------------------------------------


# ---------------------------------------------------------
rotate.ST.basis.pred <- function(X, realized.par){
			# ----------------------------------------------------------------------
			# Randomize(Rotate) the predictor.data
			# 7.17.08
			# ----------------------------------------------------------------------
				# Random rotation of "Cartesian" lat-lon plane
				theta.prime <-realized.par[1]
				# Random rotation of Julian Date line, Jan 1
				theta2.prime <- realized.par[2]
				# ---------------------------------
    		X$x <- X$x*cos(theta.prime) - X$y*sin(theta.prime)
    		X$y <- X$x*sin(theta.prime) + X$y*cos(theta.prime)
    		# ------------------------------------------
    		X$JDATE <-  X$JDATE + theta2.prime
    		ttt.ind <- (X$JDATE > 365)
        X$JDATE[ttt.ind] <- X$JDATE[ttt.ind] - 365
    # -------------------------------------------------
    # Cleanup & Return
    # -------------------------------------------------
    return(list(X = X))
# ---------------------------------------------------------
}# end Function
# ---------------------------------------------------------





# --------------------------------------------------------
pop.rpart <- function(filename, ensemble.model.number,ttt.rpart){
   f.rpart <- ttt.rpart
   num.txt <- formatC(ensemble.model.number,format="fg", width=6)
   num.txt <- chartr(" ","0",num.txt)
   temp.filename <- paste(filename,".",num.txt,".RData",sep="")
   load( file=temp.filename)  #rpart.parts
   # ----------------------------
   # Reassemble f.rpart from ttt.rpart stub
   # ----------------------------
   f.rpart$frame  <- rpart.parts$frame
   f.rpart$where  <- rpart.parts$where
   f.rpart$splits  <- rpart.parts$splits
   f.rpart$cptable <- rpart.parts$cptable
   if (sum(names(rpart.parts) == "csplit") > 0)
      f.rpart$csplit <- rpart.parts$csplit

   return(f.rpart)
}# end function


# ---------------------------------------------------------
# ---------------------------------------------------------
#  Notes: I need to check the resp.family
#         multiclass has not been added - I have not
#         how to handle the MATRIX of class probablities
#
# ** ensemble.pred.matrix - could be a VERY large
# matrix. There are other strategies for dealing with
# large data sets. This project is geared towards
# "mid-sized" data sets.
#
#
# 	# 3.18.09
# ----------------------------
# This the first revision to cut down on memory requirements
# required when (naively) storing ALL ensmble predictions.
# Here - store only the first two moments - mean & variance's
# for baggged/ensemble predictions. There is a formal parameter
# that can be set to store all predictions, if desired
# 			matrix.flag = FALSE
#
#
# ensemble.index = (not implemented yet)
# 		optional ordered index of ensemble modelsto use for predictions)
#
# -----------------------------------------------------------
# rpart.object$ frame
# -----------------------------------------------------------
# frame = data frame with one row for each node in the tree.
# row.names of frame contain the (unique) node numbers that
# follow a binary ordering indexed by node depth.
# Elements of frame include
# -----------------
#	* var = factor giving the variable used in the split at each node
#  	(leaf nodes are denoted by the string <leaf>),
#	* n = size of each node,
#	* wt = sum of case weights for the node,
#	* dev = deviance of each node,
#	* yval = the fitted value of the response at each node, and
#	* splits = two column matrix of left and right split labels for each node.
#Also included in the frame are
#	* complexity = complexity parameter at which this split will collapse,
#	* ncompete = number of competitor splits retained, and
#	* nsurrogate, the number of surrogate splits retained.
#	* yval2 = contains the number of events at the node (poisson),
#  		or a matrix containing the fitted class, the class counts for
#		each node and the class probabilities (classification).
# -----------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------
predict.ST.ensemble <- function(
	filename, # filename of ensemble & index file
	ensemble.par.list,
	prediction.design,
	prediction.design.locs,    # required for STEM
	prediction.design.jdates,  # required for STEM
	matrix.flag = FALSE)
	#ensemble.index=NULL)
	#...)   # pass through model.specific/predict.rpart parameters
{ 

   # ---------------------------------------------------------
   # Formal Parameter Test Values
   # ---------------------------------------------------------
   #	filename <-  ensemble.model.filename
   #	ensemble.index <- NULL
   #	prediction.design <- train.data$X
   #	matrix.flag <- FALSE
   # ---------------------------------------------------------
   # Inits
   # ---------------------------------------------------------
   function.call <- match.call()
   # ---------------------------
   # Load Ensemble Information
   # ---------------------------
   # * Number of models in ensemble
   # * ensemble resp.family
   # * realized.sample.par
   # ----------------------------
   n.ensemble.models <- ensemble.par.list$n.ensemble.models
   ensemble.index <- 1:n.ensemble.models
   ensemble.index <- sort(ensemble.index)
   # ------------------
   temp.filename <- paste(filename,".ensemble.index.RData",sep="")
   load(file=temp.filename) #return.list
   ens.realized.par <- return.list$realized.sample.par
   resp.family <- return.list$resp.family
   rm(return.list)
   ## KFW gc()
# -------------------------
# Extract Time Intervals
# DMF - 3.17.10
# 	added logic
# -------------------------
	time.intervals <- sort(unique(ensemble.par.list$design.summary$time.intervals))
	time.interval.vect <- ensemble.par.list$design.summary$time.intervals
	# These two parametes define the time intervals 
	# for each unique time interval in the ST ensemble
	# ==> vector of length(time.intervals)
	# ---------------------
	begin.pred.window <-  ensemble.par.list$begin.pred.window
	end.pred.window <-  ensemble.par.list$end.pred.window
	# -----------------------------------------------------------
	# 3.13.10 
	# Instead of looping over all temporal intervals
	# I want to identify the subset of temporal intervals 
	# that contain any of the prediction design!!!!
	# 
	# This should result in speed ups for many predicitons 
	# where the prediction design covers a relatively 
	# small interval of times. Eg. ST matrix and ST PD predictions. 
	# -----------------------------------------------------------
		ttt.intervals <- rep(FALSE, length(time.intervals))
		for (iii.time in time.intervals){
	     	winter <- begin.pred.window[iii.time] > end.pred.window[iii.time]
	        if (!winter) {
	            pd.season.index <-  begin.pred.window[iii.time] <= 
	            	prediction.design.jdates &
					prediction.design.jdates <= end.pred.window[iii.time]
	         	}
		  	else {
	            pd.season.index <-  begin.pred.window[iii.time] <= 
	            	prediction.design.jdates |
					prediction.design.jdates <= end.pred.window[iii.time]
	         	}
			if (sum(pd.season.index) > 0) ttt.intervals[iii.time] <- TRUE
		}
		# Select only the time intervals needed to cover pred.design
		time.intervals <- time.intervals[ttt.intervals]  
   # ----------------------------------------
   # Initialize Results/Prediction Vectors
   # ----------------------------------------
   ens.count <- rep(0, nrow(prediction.design))
   ens.moment1<- rep(0, nrow(prediction.design))
   ens.moment2<- rep(0, nrow(prediction.design))
   if (matrix.flag==TRUE){
      ensemble.pred.matrix <- matrix(NA, NROW(prediction.design), NROW(ensemble.par.list$design.summary))
   }

   # ----------------------------------------------------------
   # Init: Load First Ensemble Model
   # -----------------------------------------------------------
   iii <- 1
   num.txt <- formatC(iii,format="fg", width=6)
   num.txt <- chartr(" ","0",num.txt)
   temp.filename <- paste(filename,".",num.txt,".RData",sep="")
   load( file=temp.filename)

   # Save ensemble rpart.object stub
   ## f.rpart is coming from loaded(RData) objects 
   ttt.rpart <- f.rpart

   # ----------------------------------------------------------
   # A) Loop Over All Seasons & ID Models within Given Season
   # -----------------------------------------------------------
   for (iii.time in time.intervals){
      seasonal.model.index <- c(1:length(time.interval.vect))[time.interval.vect == iii.time]
      # ----------------------------------------------------------
      # B) Loop over all MODELS in Specified Season &
      #     Search for Subset of Data within Prediction Season
      # -----------------------------------------------------------
      for (ensemble.model.number in seasonal.model.index){
         winter <- begin.pred.window[iii.time] > end.pred.window[iii.time]
         if (!winter) {
            pd.season.index <-  begin.pred.window[iii.time] <= prediction.design.jdates &
				prediction.design.jdates <= end.pred.window[iii.time]
         }
	 else {
            pd.season.index <-  begin.pred.window[iii.time] <= prediction.design.jdates |
				prediction.design.jdates <= end.pred.window[iii.time]
         }
         # --------------------------------------------------------
         # 1) Point in Polygon: Are seasonal data in Model Region?
         # --------------------------------------------------------
	 if (sum(pd.season.index) > 0){
	    # -----------------------------------------------------------
	    # Select Region
	    # -----------------------------------------------------------
            region.number <- ensemble.par.list$design.summary$region.number[ensemble.model.number]
	    region.mc <- ensemble.par.list$design.summary$region.mc[ensemble.model.number]
            t.interval <- ensemble.par.list$design.summary$time.intervals[ensemble.model.number]
            r.index <- (ensemble.par.list$regional.polygons$region.mc == region.mc &
			ensemble.par.list$regional.polygons$region.number == region.number &
			ensemble.par.list$regional.polygons$time.intervals == t.interval	)
            # Index into Prediction Design set
            region.given.season.index <- point.in.rectangle(xxx = prediction.design.locs$x[pd.season.index],
			                                  yyy = prediction.design.locs$y[pd.season.index],
			                                  polygon.vertices = ensemble.par.list$regional.polygons[r.index,1:2])
            # -------------------------------------------------------- 
            # 2) Are there data in ensemble.model.number's REGION-SEASON ?
            # -----------------------------------------------------------
	    if (sum(region.given.season.index) > 0){
		# -------------------------------------------------
		# Numeric Indices:
		#    superset/parent: Prediction.design
		#    subset/child   : Regional-Seaonal data set
		# -------------------------------------------------
		seasonal.num.ind <- c(1:length(pd.season.index))[pd.season.index]
		reg.sea.num.ind <- seasonal.num.ind[region.given.season.index]
		# -------------------------------
		# Regional-seasonal design
		# ------------------------------
                X.pred  <-  prediction.design[ reg.sea.num.ind, ]
		# -------------------------------------------------
		# check for Design Transformations, e.g. for basis rotation
		# -------------------------------------------------
		if (ensemble.par.list$sampling.par.list$ST.basis.rotation == TRUE){
	           ttt <- rotate.ST.basis.pred(X = X.pred, realized.par=ens.realized.par[,ensemble.model.number])
		   X.pred <- ttt$X
		   rm(ttt)
                   ## KFW gc()
		}
		# ----------------------------------------------------------
		# Load/Construct rpart.object
		# -----------------------------------------------------------

		if  (ensemble.model.number != 1){
			# ---------------------------------
			# 5.20.09 
			# Adding Error Trapping code 
			# to deal with the following mysterious message
			# Error in f.rpart$frame <- rpart.parts$frame :  
			# value of 'SET_ATTRIB' must be a pairlist or NULL, not a 'character' 
			# ---------------------------------
			f.rpart <- try( pop.rpart(filename, ensemble.model.number, ttt.rpart) )
			# If there is an error, try it again
			if (class(f.rpart) == "try-error") {
			   cat("rpart file read error \n")
			   f.rpart <- try( pop.rpart(filename, ensemble.model.number, ttt.rpart) )
			}
		} # end ensemble.model.number != 1
                else {
		   f.rpart <- ttt.rpart
                }

		# -------------------------------------------------
		# rpart Predict
		# ------------------
		# Note: the predict method for rpart will
		# not make a prediction on a root node only.
		# That is, if the rpart model is only a root node
		# then I need to skip the call to predict - will generate an error
		# and manually assign all pts the same prediction.
		# --------------------
		# 4.9.09
		# Separate out case when bernoulli because
		# it requires slightly different call to deal with two classes.
		# -------------------------------------------------
		#NROW(f.rpart$frame)
		if (NROW(f.rpart$frame) == 1) {
			if (resp.family == "bernoulli"){
			   # yval is the predicted response
			   # In the two class problem, the assumed coding is
			   # a factor with levels "FALSE" and "TRUE".
			   # rpart orders these alphabetically, so
			   # 	The first class: FALSE
			   # 	The second class: TRUE
			   # So, if yval are predicted prob for the first class
			   # i.e. FALSE, then I want to use 1-yval as the predicted value
			   #  -------------------------------------------------------------
			   ttt.rpart.pred <- rep((1-f.rpart$frame$yval), NROW(X.pred))
			 }
			 if (resp.family =="gaussian"){
			    ttt.rpart.pred <- rep(f.rpart$frame$yval, NROW(X.pred))
			 }# end gaussian
		} #end stump predictions section
		# ------------------------------------------
  		# If there is more than just the root node
    		# ------------------------------------------
		if (NROW(f.rpart$frame) > 1) {
			if (resp.family=="gaussian"){
				ttt.rpart.pred <- predict(f.rpart,newdata=X.pred) # ...)
			}
			if (resp.family=="bernoulli"){
				## ttt.rpart.pred.bern <- predict(f.rpart,newdata=X.pred, type="prob")

				tryCatch ({
                                   x.pred.attributes <- attributes(X.pred)
                                   f.rpart.attributes <- attributes(f.rpart)

                                   ## print("start of X.pred attributes")
                                   ## print(x.pred.attributes)
                                   ## print("end of X.pred attributes")

                                   if (is.null(x.pred.attributes)) {
                                      print("**** NULL X.pred attributes ***")
                                   }

                                   if (is.null(f.rpart.attributes)) {
                                      print("**** NULL X.pred attributes ***")
                                   }


                                   ## print("start of f.rpart attributes")
                                   ## print(f.rpart.attributes)
                                   ## print("end of f.rpart attributes")
                                   ## print(f.rpart)
                                   ## print("======= before predict() ==================================================")

                                   ttt.rpart.pred.bern <- predict(f.rpart,newdata=X.pred, type="prob");

                                   ## print("after predict()")
                                },
                                error = function(ex) {
                                   print("***** KFW start of catch block")

                                   x.pred.attributes <- attributes(X.pred)
                                   f.rpart.attributes <- attributes(f.rpart)

                                   print("start of X.pred attributes")
                                   print(x.pred.attributes)
                                   print("end of X.pred attributes")
                                   print("start of f.rpart attributes")
                                   print(f.rpart.attributes)
                                   print("end of f.rpart attributes")
                                   print(f.rpart)
                                   print("=========================================================")

                                ##
                                ##   print("---- prediction.design ---")
                                ##
                                ##   print(nrow(prediction.design))
                                ##   print(ncol(prediction.design))
                                ##
                                ##   for (colIndex in 1:ncol(prediction.design)) {
                                ##      message <- paste(colIndex, class(prediction.design[,colIndex]), sep="  ")
                                ##      print(message)
                                ##   }
                                ##
                                ##
                                   stop("ERROR - bailing out!")
                                },
                                finally = {
                                })

	   			ttt.rpart.pred <- ttt.rpart.pred.bern[,2]
	   		}
			if (resp.family=="poisson") {
				ttt.rpart.pred <- predict(f.rpart,newdata=X.pred,type="vector") #,...)
			}
		}

                #---------------------------------------------------------------
                # 3. Accumulate Predictions
                # --------------------------------------------------------------
	        ens.count[reg.sea.num.ind] <- ens.count[reg.sea.num.ind] + 1
	        ens.moment1[reg.sea.num.ind] <- ens.moment1[reg.sea.num.ind] + ttt.rpart.pred
	        ens.moment2[reg.sea.num.ind] <- ens.moment2[reg.sea.num.ind] + ttt.rpart.pred^2
	        # ----------------------------
	        #   nrow = NROW(prediction.design)
	        #   ncol = number models in ensemble models
	        # ----------------------------
	        if (matrix.flag == TRUE){
	           ensemble.pred.matrix[reg.sea.num.ind,ensemble.model.number] <- ttt.rpart.pred
	        }

                rm(X.pred)
	    } # End REGION-SEASON Prediction
         } # if data in REGION-SEASON subset

         ## KFW gc()
      } # end loop over Seasonal ensemble models
   } # end time interval loop

   # ----------------------------------------------------------
   # Return Prediction Matrix
   # -----------------------------------------------------------
   # 3.18.09 Modifications
   # -----------------------------------
   ens.mean <-  rep(NA, NROW(prediction.design))
   ens.var <-  rep(NA, NROW(prediction.design))
   na.ind <- (ens.count > 0)
   ens.mean[na.ind] <- ens.moment1[na.ind]/ens.count[na.ind]
   na.ind2 <- (ens.count >= 2)
   ens.var[na.ind2] <- ens.moment2[na.ind2]/ (ens.count[na.ind2] -1) -
			(ens.mean[na.ind2]^2)*(ens.count[na.ind2])/(ens.count[na.ind2] -1)

   if (matrix.flag == TRUE) {
      return.list <- list(
      	mean = ens.mean, 
      	sd = sqrt(ens.var), 
      	count = ens.count, 
      	matrix = ensemble.pred.matrix, 
      	function.call = function.call)
   }
   else {
      return.list <- list(
      	mean = ens.mean, 
      	sd = sqrt(ens.var), 
      	count = ens.count, 
      	function.call = function.call)
   }

   if (matrix.flag==TRUE){
      rm(ensemble.pred.matrix)
   }

   ## kfw gc()

   return(return.list)
}# End FUNCTION
# --------------------------------------------------------------------------
# --------------------------------------------------------------------------





# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
# BS.RPART Random Space-Time Prediction Function
# --------------------------------------------------------------------------
# 1.15.07
# 7.16.08 - quick & dirty modifications to take into
# 					account basis rotations performed in the function
#						ST.BDT.test (located in this file)
# 1.8.09 - reorganization
#
# This function performs two related tasks:
#
# 	1) Predictor Conditioning
# 	2) Time-Slice Predictions
#
# Predictor Conditioning:
# -----------------------------
# For many prediction tasks it is necessary to assign constant
# values to certain predictors. E.g. constructing a prediction
# design to control for observation effort - by seting effort constant.
# The conditioning variables and corresponding values are defined
#  in the conditioning.vars list.  If the conditioning variable is not
# present in the predictor.design data frame, it will be added.
#
# Time-Slice predictions.
# ----------------------------
# We loop though all time slices (defined by julian date AND year)
# and make the full set of (spatial) predictions. This simple looping
# proceedure was designed to handle large prediction vectors.
# For this reason, we decided to cycle throught each ensemble model
# for EACH time slice. This takes more time to load and reload all
# of the models, but requires less memory to hold the predictions
# for ALL time slices simultaneously.
#
# The results, i.e. the prediction vectors, are saved into sequentially
#  numbered  files, in the same order as the temporal sequence.
#
# Like the other functions I am writing, I will begin by keeping
# this as simple as possible. KISS!!
#
# INPUT
# ------------
# 	predictor.design  <- data frame of predictors. Including YEAR, JDATE,
#					and the conditioning variables, this should have
# 					the same number of predictors are the
# 					predictors used in the models.
#   --------------
# 	information about the ensemble models
#   ------------------------------------
#		model.predictor.names,
# 		bs.rpart.name,
#		bs.rpart.dir,
#		btrials,
#  Save Results to directory and name
#			# --------------
#			save.name,
#			save.dir,
# Define Temporal Sequence
# ** jdate.seq and year.seq must be of the same length
#     the code cycles through all pairs of values.
#			jdate.seq,
#			year.seq,
# Conditioning Variable List - This is how we control for the Observation
# 							process.
#			conditioning.vars = NULL
#
# OUTPUT
# ------------
#		call = call,
#		# Saved predictions
#			save.name=save.name,
#			save.dir=save.dir,
#		# Temporal Sequence
#			jdate.seq=jdate.seq,
#			year.seq = year.seq)
#
# To do:
# ---------
# I need to describe the format of D.pred in detail so that I can
# generate new sets. Part of this will be to point to/describe the
# process that Roger and I went through to generate this data.
#
# A simple way to do this is to pass the dtm object which
# should include the names of the predictors!
# It will also include the bs.trial, and the bs.path and file
# name information!!!
#
# ERROR occurs when there is a predictor.name in "model.predictor.names"
# but that predictor does not occurr in predictor.design or the
# conditioning variables. should this happen?
# If so, I should pass a more intelligible error message to the user.
#
# NOTE:
# When model predicts an NA (e.g. STEM does this when location
# has no support , i.e. an extrapolation) then this function
#will just pass NA's through $mean & $sd
#
# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
predict.st.matrix <- function(
              prediction.design,
		    prediction.design.locs,   
		    #prediction.design.jdates = NULL,  # required for STEM
			#--------------
			model.predictor.names,
			model.filename,
			ensemble.par.list,
			# --------------
			save.name,
		# Temporal Sequence
			jdate.seq,
			year.seq,
		# Conditioning Vars - Observation Process Design
			conditioning.vars = NULL){
# ---------------------------------------------------
#			prediction.design = pred.data$D.pred
#			prediction.design.locs = pred.data$locs
#			#--------------
#			model.predictor.names = names(train.data$X)
#			model.filename = ensemble.model.filename
#			ensemble.par.list = ensemble.par.list
#			# --------------
#			save.name = st.pred.filename
#			# Temporal Sequence
#			jdate.seq =jdate.seq
#			year.seq =year.seq
#			# Conditioning Vars - Observation Process Design
#			conditioning.vars = conditioning.vars
# ---------------------------------------------------------
# Inits
# ---------------------------------------------------------
	  function.call <- match.call()	  
## ------------------------------------------------------------------------
# Assign and/or Add  Conditioning variables as necessary
#		Verified for class numeric
#		Check to make sure that this works with factors -
#     especially if the conditioning value is a level
#     that has NOT been used for training!!!
# ------------------------------------------------------------------------
	for (iii in 1:length(conditioning.vars)) {
		# When conditioning predictor is already in predictor.design
		if (names(conditioning.vars)[iii] %in% names(prediction.design) ) {
			pred.index <- names(prediction.design)  %in% names(conditioning.vars)[iii]
			prediction.design[ , pred.index] <- conditioning.vars[[iii]]
			}
		# When conditioning predictor is NOT in predictor.design
		if (!(names(conditioning.vars)[iii] %in% names(prediction.design) )) {
			ttt.names <- names(prediction.design)
			ttt <- matrix(conditioning.vars[[iii]], NROW(prediction.design),1)
		 	prediction.design <- data.frame(prediction.design,  ttt)
		 	names(prediction.design) <- c(ttt.names,
				names(conditioning.vars)[iii])
			}
		} # end iii

# ------------------------------------------------------------------------
# Check to see if any model.predictor.names are missing from predictor.design
# ------------------------------------------------------------------------
		# ID predictors in the predictor.design but not in the model.predictors
		#setdiff(names(prediction.design), model.predictor.names)
			# These are OK, just extraneous
		# and the other way around
		#setdiff(model.predictor.names,names(prediction.design))
			# year and jdate are OK here, but anything else needs to be flagged

# --------------------------------------------------------------------------
# Loop over dates in design & make predicitons
# --------------------------------------------------------------------------
   for (iii in 1:length(jdate.seq)){
  	    # Set prediction design jdate
  	    prediction.design.jdates <- rep(jdate.seq[iii],NROW(prediction.design))
	    # Check for predictors called JDATES & YEARS
	    # If so, then impute prediction design values
	    # ----------------------------------------------
	    if ( c("JDATE") %in% model.predictor.names  ) 
	    	 prediction.design$JDATE <- rep(jdate.seq[iii],NROW(prediction.design))
	    if ( c("YEAR") %in% model.predictor.names ) 	 
		 prediction.design$YEAR <- rep(year.seq[iii],NROW(prediction.design))
         # -----------------------------------------------
		# Ensemble predictions
	     # -----------------------------------------------
		#pred.Xp <- ensemble.par.list$predict.ensemble.function(
		#	filename = model.filename,
		#	ensemble.par.list =ensemble.par.list,
		#	prediction.design=predictor.design)
		# --------------------------------------
		pred.Xp <- predict.ST.ensemble(
			filename = model.filename,
			ensemble.par.list,
			prediction.design=prediction.design,
			prediction.design.locs=prediction.design.locs,    # required for STEM
			prediction.design.jdates=prediction.design.jdates,  # required for STEM
			matrix.flag = FALSE)
    	# --------------------------------------------------------------------------
    	# Save predictions to files
    	# --------------------------------------------------------------------------
    	save.filename <- paste(save.name,".",iii,".RData",sep="")
    	st.pred <- data.frame(
					xxx = prediction.design.locs$x,
					yyy = prediction.design.locs$y,
					pred = pred.Xp$mean,
					sd = pred.Xp$sd)
    	save(st.pred,  file=save.filename) # st.pred
    	# Compare to dput or other methods to see if
    	# there is a size advantage
	# ----------------------------------------------------
  }    # end iii loop

  # ------------------------------------------------------------
  # Return Values
  # ------------------------------------------------------------
	return(function.call)
} # end function
# --------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------


# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
# Modify predict.st.matrix from stem.library.8.18.09.R
# by 
# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
predict.st.matrix.ebird.ref.data <- function(
		prediction.design,
		prediction.design.locs,   
		#prediction.design.jdates = NULL,  # required for STEM
			#--------------
			model.predictor.names,
			model.filename,
			ensemble.par.list,
			# --------------
			save.name,
		# Temporal Sequence
			jdate.seq,
			year.seq,
		# Conditioning Vars - Observation Process Design
			conditioning.vars = NULL){
# ---------------------------------------------------
#			prediction.design = pred.data$D.pred
#			prediction.design.locs = pred.data$locs
#			#--------------
#			model.predictor.names = names(train.data$X)
#			model.filename = ensemble.model.filename
#			ensemble.par.list = ensemble.par.list
#			# --------------
#			save.name = st.pred.filename
#			# Temporal Sequence
#			jdate.seq =jdate.seq
#			year.seq =year.seq
#			# Conditioning Vars - Observation Process Design
#			conditioning.vars = conditioning.vars
# ---------------------------------------------------------
# Inits
# ---------------------------------------------------------
	  function.call <- match.call()	  
# ------------------------------------------------------------------------
# Assign and/or Add  Conditioning variables as necessary
#		Verified for class numeric
#		Check to make sure that this works with factors -
#     especially if the conditioning value is a level
#     that has NOT been used for training!!!
# ------------------------------------------------------------------------
	for (iii in 1:length(conditioning.vars)) {
		# When conditioning predictor is already in predictor.design
		if (names(conditioning.vars)[iii] %in% names(prediction.design) ) {
			pred.index <- names(prediction.design)  %in% names(conditioning.vars)[iii]
			prediction.design[ , pred.index] <- conditioning.vars[[iii]]
			}
		# When conditioning predictor is NOT in predictor.design
		if (!(names(conditioning.vars)[iii] %in% names(prediction.design) )) {
			ttt.names <- names(prediction.design)
			ttt <- matrix(conditioning.vars[[iii]], NROW(prediction.design),1)
		 	prediction.design <- data.frame(prediction.design,  ttt)
		 	names(prediction.design) <- c(ttt.names,
				names(conditioning.vars)[iii])
			}
		} # end iii

# ------------------------------------------------------------------------
# Check to see if any model.predictor.names are missing from predictor.design
# ------------------------------------------------------------------------
		# ID predictors in the predictor.design but not in the model.predictors
		#setdiff(names(prediction.design), model.predictor.names)
			# These are OK, just extraneous
		# and the other way around
		#setdiff(model.predictor.names,names(prediction.design))
			# year and jdate are OK here, but anything else needs to be flagged

		## KFW 
                ## vegetationIndexData <- read.csv(file="ebird_reference_data/processed_VI_Data_SRD.csv", na.strings = c("NA", "?"))
		## KFW 

# --------------------------------------------------------------------------
# Loop over dates in design & make predicitons
# --------------------------------------------------------------------------
   for (iii in 1:length(jdate.seq)){
	    # Set prediction design jdate
  	    prediction.design.jdates <- rep(jdate.seq[iii],NROW(prediction.design))
	    # Check for predictors called JDATES & YEARS
	    # If so, then impute prediction design values
	    # ----------------------------------------------
	    if ( c("DAY") %in% model.predictor.names  ) 
	    	 prediction.design$DAY <- rep(jdate.seq[iii],NROW(prediction.design))
	    if ( c("YEAR") %in% model.predictor.names ) 	 
		 prediction.design$YEAR <- rep(year.seq[iii],NROW(prediction.design))
		 
		# ----------------------------------------------------------------------------------------------------------------------
		# 8.18.09 
		# -----------------
		# check for special ebird reference data predictors called 
		# "caus_temp_avg"              "caus_temp_min"             
		#[15] "caus_temp_max"              "caus_prec"                 
		#[17] "caus_snow"     
		#each of these records the climate variable value  ( e.g. snow depth ) 
		# for month in which observation was made. so, here i 
		# will assume that the requisite us climate are available and then 
		# select the approtiate month for the 
		# corresponding prediction design "observation". 
		# ----------------------------------------------		 
		if ( "CAUS_TEMP_AVG"  %in% model.predictor.names  ) {
			month.index <- floor(jdate.seq[iii] / (366/12))+1 
			num.txt <- formatC(month.index, format="fg",width=2)
			num.txt <- chartr(" ","0",num.txt)
			ttt.pred.name <- paste("CAUS_TEMP_AVG", num.txt,sep="")
			## KFW prediction.design$CAUS_TEMP_AVG <- 
			## KFW	prediction.design[ , names(prediction.design) %in% ttt.pred.name]

			prediction.design$CAUS_TEMP_AVG <- 
				as.numeric(prediction.design[ , names(prediction.design) %in% ttt.pred.name])
			} # end if
		if ( "CAUS_TEMP_MIN"  %in% model.predictor.names  ) {
			month.index <- floor(jdate.seq[iii] / (366/12))+1 
			num.txt <- formatC(month.index, format="fg",width=2)
			num.txt <- chartr(" ","0",num.txt)
			ttt.pred.name <- paste("CAUS_TEMP_MIN", num.txt,sep="")
			## KFW prediction.design$CAUS_TEMP_MIN <- 
			## KFW	prediction.design[ , names(prediction.design) %in% ttt.pred.name]

			prediction.design$CAUS_TEMP_MIN <- 
				as.numeric(prediction.design[ , names(prediction.design) %in% ttt.pred.name])
			} # end if
		if ( "CAUS_TEMP_MAX"  %in% model.predictor.names  ) {
			month.index <- floor(jdate.seq[iii] / (366/12))+1 
			num.txt <- formatC(month.index, format="fg",width=2)
			num.txt <- chartr(" ","0",num.txt)
			ttt.pred.name <- paste("CAUS_TEMP_MAX", num.txt,sep="")
			## KFW prediction.design$CAUS_TEMP_MAX <- 
			## KFW	prediction.design[ , names(prediction.design) %in% ttt.pred.name]

			prediction.design$CAUS_TEMP_MAX <- 
				as.numeric(prediction.design[ , names(prediction.design) %in% ttt.pred.name])
			} # end if			
		if ( "CAUS_PREC"  %in% model.predictor.names  ) {
			month.index <- floor(jdate.seq[iii] / (366/12))+1 
			num.txt <- formatC(month.index, format="fg",width=2)
			num.txt <- chartr(" ","0",num.txt)
			ttt.pred.name <- paste("CAUS_PREC", num.txt,sep="")
			## KFW prediction.design$CAUS_PREC <- 
			## KFW	prediction.design[ , names(prediction.design) %in% ttt.pred.name]

			prediction.design$CAUS_PREC <- 
				as.numeric(prediction.design[ , names(prediction.design) %in% ttt.pred.name])
			} # end if						
		if ( "CAUS_SNOW"  %in% model.predictor.names  ) {
			month.index <- floor(jdate.seq[iii] / (366/12))+1 
			num.txt <- formatC(month.index, format="fg",width=2)
			num.txt <- chartr(" ","0",num.txt)
			ttt.pred.name <- paste("CAUS_SNOW", num.txt,sep="")
			# Check for Mean snow depth May - Sept 
			snow.check <- month.index >=5 & month.index <=9
			if (snow.check) 	ttt.pred <- rep(0,NROW(prediction.design)) 
			if (!snow.check) 	ttt.pred <- 
					prediction.design[ , names(prediction.design) %in% ttt.pred.name]						
			## KFW prediction.design$CAUS_SNOW <- ttt.pred

			prediction.design$CAUS_SNOW <- as.numeric(ttt.pred)
			} # end if


                ## KFW
		if ( "NDVI"  %in% model.predictor.names  ) {
                   ## viDataRecordMask <- vegetationIndexData$YEAR == year.seq[iii] &
                   ##                     vegetationIndexData$DAY == jdate.seq[iii]  
                
                   ## prediction.design$NDVI <- as.numeric(vegetationIndexData$NDVI[viDataRecordMask])

                   viDataRecordMask <- vegetationIndexData[,3] == year.seq[iii] &
                                       vegetationIndexData[,4] == jdate.seq[iii]  
                
                   prediction.design$NDVI <- as.numeric(vegetationIndexData[viDataRecordMask, 5])


                   ## print(year.seq[iii])
                   ## print(jdate.seq[iii])
                   ## print(prediction.design$NDVI)

                   rm(viDataRecordMask)
                }

	        if ( "EVI"  %in% model.predictor.names  ) {
                   viDataRecordMask <- vegetationIndexData$YEAR == year.seq[iii] &
                                       vegetationIndexData$DAY == jdate.seq[iii]  

	           prediction.design$EVI <- as.numeric(vegetationIndexData$EVI[viDataRecordMask])

                   rm(viDataRecordMask)
                }
                ## KFW


         # -----------------------------------------------
		# Ensemble predictions
	     # -----------------------------------------------
		#pred.Xp <- ensemble.par.list$predict.ensemble.function(
		#	filename = model.filename,
		#	ensemble.par.list =ensemble.par.list,
		#	prediction.design=predictor.design)
		# --------------------------------------


                ## print("predict.st.matrix.ebird.ref.data() calling predict.ST.ensemble()")

		pred.Xp <- predict.ST.ensemble(
			filename = model.filename,
			ensemble.par.list,
			prediction.design=prediction.design,
			prediction.design.locs=prediction.design.locs,    # required for STEM
			prediction.design.jdates=prediction.design.jdates,  # required for STEM
			matrix.flag = FALSE)
    	# --------------------------------------------------------------------------
    	# Save predictions to files
    	# --------------------------------------------------------------------------
    	save.filename <- paste(save.name,".",iii,".RData",sep="")
    	st.pred <- data.frame(
					xxx = prediction.design.locs$x,
					yyy = prediction.design.locs$y,
					pred = pred.Xp$mean,
					sd = pred.Xp$sd)
    	save(st.pred,  file=save.filename) # st.pred
    	# Compare to dput or other methods to see if
    	# there is a size advantage
	# ----------------------------------------------------
  }    # end iii loop

  # ------------------------------------------------------------
  # Return Values
  # ------------------------------------------------------------
	return(st.pred)
} # end function
# --------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------



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
# 5.4.09 
# --------------------------------
#  ** Got rid of "matrix" object - only using mean 
#  ** STEM additions
# 		construct updated prediction.design.locs & prediction.design.jdate 
#  ** break appart & sum over nn.sample
#  ** added logic to deal with PD of JDATE and (x,y) locs 
#
# TO DO: 
# --------------------------------
# ** collect PD sd estimates!
# **	Need to Recode Categorical predictors
# 	eg. if BCR was a predictor we would need to recode it 
# 	to its proper level labels !!!!!
# 	Currently, BCR is coded as the number of the LEVEL
# 	xxx.grid[,2] <- levels(train.data$X$BCR)[xxx.grid[,2]]
# ** 2.26.10
#	I need to take a single random sample 
# 	of size nn.sample from an index of length == nrows(prediction.design)
# 	then add to it over the batch "samples".
#	This instead of the multiple samples taken one batch at a time. 
# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------
STEM.partial.dependence <- function(
	filename,
	ensemble.par.list,
	prediction.design,   	#XX,
	prediction.design.locs,    # required for STEM
	prediction.design.jdates,  # required for STEM	
	partial.dependence.list,
	continuous.resolution = 15,
	nn.sample = 200,
	batch.size =50 )
{ # ----------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------
# Test Formal Parameters
# ------------------------------------------------------------------------------------------------------
#	pd.list <- list( 
#     		"NLCD01_N90A100R5", "JDATE", 
#        # 2D Partials
#     		c("x", "y"),         # lat x lon interaction
#     		c("JDATE", "NLCD01_N90A100R5"))  # can we pick up change in time of sunrise? 
#		filename = ensemble.model.filename
#		ensemble.par.list = ensemble.par.list
#		#XX = train.data$X,
#		prediction.design=train.data$X   	#XX,
#		prediction.design.locs=ensemble.par.list$ensemble.data.locs    # required for STEM
#		prediction.design.jdates=ensemble.par.list$ensemble.data.jdates  # required for STEM
#		partial.dependence.list=pd.list
#		continuous.resolution = 30
#		nn.sample = 500
#		batch.size = 50	
# ------------------------------------------------------------------------------------------------------
# Inits Formal Parameters
# ------------------------------------------------------------------------------------------------------
	#temp.filename <- paste(filename,".ensemble.index.RData",sep="")
	#load(file=temp.filename) #return.list
	#bs.trials <- NCOL(return.list$ib.sample.index)
	# Results
   	XX <- prediction.design
 	pd.means <- vector(mode="list", length=length(partial.dependence.list))
 	pd.matrices <- vector(mode="list", length=length(partial.dependence.list))
# ------------------------------------------------------------------------------------------------------
# Compute Partial Dependence Quantile Grids
# ------------------------------------------------------------------------------------------------------
	pd.quant.grids <- create.pd.grid(
				XX=XX,
				i.var.list=partial.dependence.list,
				continuous.resolution = continuous.resolution)
# ------------------------------------------------------------------------------------------------------
# Find factors in XX
# 	Note : I can not use apply b/c XX is class data.frame
# ------------------------------------------------------------------------------------------------------
	XX.factor.ind <- rep(FALSE, NCOL(XX))
	ttt <- XX[1,] # it is much faster to search a 1D data.frame!
	for (ii in 1:NCOL(XX)) XX.factor.ind[ii] <- is.factor(ttt[,ii])
	# Extract an index of column positions for factors (wo zeros!)
 	factor.index <-	as.numeric(XX.factor.ind)*seq(1,NCOL(XX))
 	factor.index <- factor.index[factor.index > 0 ]
# ------------------------------------------------------------------------------------------------------
# Loop Over PD list elements
# ------------------------------------------------------------------------------------------------------
for (iii in 1:length(pd.quant.grids)){
	# Initialize Batch Result Vectors
	ppp.batch <- 0
	ppp.batch.count <- 0
	# Calculate # of Batch Loops	 
	nnn.batch <- floor(nn.sample/batch.size) + 
	                 as.numeric(ceiling(nn.sample/batch.size) > 
                          floor(nn.sample/batch.size))	  
# Begin Batch loop Here
# -------------------------------
for ( iii.batch in 1:nnn.batch){
# -------------------------------
     batch.sample.size <- min(batch.size, (nn.sample - (iii.batch-1)*batch.size)) 
	# ------------------------------------------------------------------------------------------------------
	# Random Sample of Data Rows (same sample for all PD elements)
	# ------------------------------------------------------------------------------------------------------
	    # Sample without replacement from data rows
	    if (batch.sample.size  >= NROW(XX))	
	    	  sample.index <- sample(1:NROW(XX), batch.sample.size, replace = TRUE)
	    if (batch.sample.size < NROW(XX))
	    	sample.index <- sample(1:NROW(XX), batch.sample.size, replace = FALSE)
	    #dim(XX.sample)
	# ------------------------------------
	# 1. Expand Quantile Grid into PD Prediction Design
	# 2. BDT Predictions
	# 3. Assemble Results
	# ------------------------------------
	i.var <- match( names(pd.quant.grids[[iii]]), names(XX))
	XX.sample <- XX[sample.index, setdiff(names(XX), names(XX)[i.var]) ]
	pd.grid <- pd.quant.grids[[iii]]
	 # ----------------------------
	 # NOTE** PD design can get big = batch.sample.size * length(pd.grid)
	# ------------------------------------------------------------------------------------------------------
	# Construct Partial Dependence Prediction Data Frame
	# 	NOTE: the use of data.matrix converts factors to numerics
	# ------------------------------------------------------------------------------------------------------
	# Stack Randomly Sampled Data Rows
	XX.stack <- kronecker( matrix(1, NROW(pd.grid), 1),
    						data.matrix(XX.sample))
	XX.stack <- as.data.frame(XX.stack)
	names(XX.stack) <- names(XX.sample)
	# Stack Partial Dependence Grids
	pd.stack <- kronecker( data.matrix(pd.grid), matrix(1, batch.sample.size, 1))
	pd.stack <- as.data.frame(pd.stack)
	names(pd.stack) <- names(pd.grid)
	PD.prediction.frame <- cbind(pd.stack,XX.stack)
	# -------------------------------------------
	# Stack Location & JDATE indices
	# Stack Randomly Sampled Data Rows
	XX.locs.sample <- prediction.design.locs[sample.index,]
	XX.locs.stack <- kronecker( matrix(1, NROW(pd.grid), 1),
    						data.matrix(XX.locs.sample))
	XX.locs.stack <- as.data.frame(XX.locs.stack)
	names(XX.locs.stack) <- names(XX.locs.sample)	
	# -----------
	XX.jdates.sample <- prediction.design.jdates[sample.index]
	XX.jdates.stack <- kronecker( matrix(1, NROW(pd.grid), 1),
    						data.matrix(XX.jdates.sample))
	# -------------------------------------------
	# **** Check to see if i.var is an index variable. 
	# Currently the ST index variable names are hardcoded to " x, y, or JDATE "
	#
	# modified 10.20.09
	#
	# If so, then modify parameter indices accordingly 
	# ** Check out the flexible logic - this will work 
	# 	for any pd.list! 
	# -------------------------------------------    						
	#    	if ("DAY" %in% names(XX)[i.var]) XX.jdates.stack <- pd.stack$DAY
	#    	if ("x" %in% names(XX)[i.var]) XX.locs.stack[,1] <- pd.stack$x
	#    	if ("y" %in% names(XX)[i.var]) XX.locs.stack[,2] <- pd.stack$y
	# modified 02.17.10
	# -------------------
	# With the separate index variables, there is no need to 
	# treat them specially, whether or not the same index 
	# variables are used as predictors. 
	# Therefore, I removed the lines above. 	
	
				   					   					     	     							
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
			PD.prediction.frame[,i] <-
			factor(levels(XX[,i])[PD.prediction.frame[,i]],
				levels=levels(XX[,i]))
				}
	# ------------------------------------------------------------------------------------------------------
	# Ensemble PD Predictions
	# ------------------------------------------------------------------------------------------------------
	ttt.pred <- predict.ST.ensemble(
		filename= filename, # filename of ensemble & index file
		ensemble.par.list = ensemble.par.list,
		prediction.design= PD.prediction.frame,
		prediction.design.locs=XX.locs.stack,    # required for STEM
		prediction.design.jdates=XX.jdates.stack,  # required for STEM
		matrix.flag = FALSE)
	pred.X <- ttt.pred$mean	
	# --------------------------------------------
	# Average to get Ensemble average PD estimates
	# --------------------------------------------
		pred.index <- (rep(c(1:NROW(pd.grid)),each=batch.sample.size))
	 	ppp <- tapply(pred.X, pred.index, sum, na.rm=T)
	 	ppp.count <-  tapply(!is.na(pred.X), pred.index, sum, na.rm=T)
	# ---------------------------------
	# Collect the mean (first moment + count) 
	# across batch of partial prediction jobs
	# ---------------------------------	
	 	ppp.batch <- ppp.batch + ppp
	 	ppp.batch.count <- ppp.batch.count + ppp.count
	# ---------------------------------
	# 2.26.10 Cleanup
	# 	(incomplete)
	# ---------------------------------	
	rm(ttt.pred, XX.stack,pd.stack,PD.prediction.frame, 
		XX.locs.stack, XX.jdates.stack)
	## KFW gc()

# end Batch loop Here
# -------------------------
} # end iii.batch
# ------------------------- 	
 	if (sum(ppp.batch.count==0) > 0) 
 	   warning(paste("STEM.partial.dependence: unsupported",
	     "partial predictions, ppp.batch.count==0 ")) 
	 # Calculate Mean Value and Final Count(support)
	ppp <- ppp.batch/ppp.batch.count
 	# -------------------------------	
 	# recode pd.grid factors
	f.factor <- rep(FALSE, NCOL(pd.grid))
	for (i in 1:NCOL(pd.grid)) {
		col.index <- match( names(pd.grid)[i], names(XX))
		if (!is.numeric( XX[,col.index] )) {
			f.factor[i] <- TRUE
		#if (names(pd.grid[i]) %in% names(XX)[factor.index])
			pd.grid[,i] <-
				factor(levels(XX[,col.index])[pd.grid[,i]],
					levels=levels(XX[,col.index]))}
	} #end for i - search for factors
	# Reassociate pd.grid with predictions
	pdf.grid <- data.frame(pd.grid, pred=ppp)
	# -----------------------------------
	# Store results in PD.list
	# -----------------------------------
	# pd.means = the Partial Dependence Estimate averaged over bags
	# pd.matrices = the PD estimates, one col per bag/model
  	pd.means[[iii]] <- pdf.grid
  	#pd.matrices[[iii]] <- pdf.grid.matrix
	#names(pdf.grid)
	#dim(pdf.grid)
} # end iii
# -----------------
return(list(
      pd.quant.grids=pd.quant.grids,
      pd.means=pd.means))
      #pd.matrices=pd.matrices))
} # end function
# -------------------------------------------------------------------
# ---------------------------------------------------------------------




# ---------------------------------------------------------------------------------------------------------------------
# Plot STEM Temporal Design
# ---------------------------------------------------------------------------------------------------------------------
plot.STEM.temporal.design<- function(
      ensemble.par.list)
      #ensemble.data,
      #mc.region.x.time.index=1, # value of nnn.spatial.mc)
      #...) # pass through plotting parameters?
{# ---------------------------------------------------------
		#ensemble.par.list
		p.min <- -1.5
		p.max <- 1.5
	# -----------------------------------------------------
	# Central Julian Calendar Circle
	# ------------------------------------------------------
		nnn <- 1000
		radian.seq <- seq(from=0, to=2*pi, length=nnn)
		plot( cos(radian.seq),
			sin(radian.seq),
				type="l",
				lwd=3.0,
				xlab=" ",
				ylab=" ",
				xlim = c(p.min,p.max),
				ylim = c(p.min, p.max),
				axes = FALSE)
	# ---------------------------------------------------------
	# Convert Temporal Sequence times to POSIX
	# ---------------------------------------------------------
		#text( -.25, .75,
		#		pos=4, # text is to the left of location
		#		cex = 1.5,
		#		labels=c("Dec/Jan") )
		# Add notches at 3,6,9, & 12 o'clock
		n.notches <- 12
		radian.seq <- seq(from=pi/2, to=5*pi/2, length=(n.notches+1))
		jdate.ttt <- 365 - radian.seq/2/pi *365 +  radian.seq[1]/2/pi *365 + 1
		jdate.ttt[jdate.ttt > 365]  <- jdate.ttt[jdate.ttt > 365] -365
		jdate.ttt <- jdate.ttt[1:n.notches]
		p.time <- strptime( x=paste(round(jdate.ttt)), "%j")
		# Nice function to convert DateTime Classes
		month.text <- months(p.time, abbreviate = TRUE)
		date.names <- paste(month.text, " ",p.time$mday,sep="")
		#p.time
		#month.text
		#date.names
		ttt.min <- 1.0
		ttt.max <- 1.1
		inside.scale <- 0.9
		for (iii in 1:n.notches){
			lines(  c(ttt.min*cos(radian.seq[iii]), ttt.max*cos(radian.seq[iii])),
					c(ttt.min*sin(radian.seq[iii]), ttt.max*sin(radian.seq[iii])),
					lwd=2.0)
			text( inside.scale* cos(radian.seq[iii]) ,
				 inside.scale*sin(radian.seq[iii]),
		#		pos=4, # text is to the left of location
		#		cex = 1.5,
				labels=c(month.text[iii]) )
					}
	# ---------------------------------------------------------
	# Add Shingles
	# ---------------------------------------------------------
	nnn <- length(ensemble.par.list$begin.window)
	#nnn <- 1
	inner.radius <- 1.0
	outer.radius <- 1.5
	training.window.color <- "blue"
		inner.pred.radius <- inner.radius + 0.1
		outer.pred.radius <- outer.radius - 0.1
	pred.window.color <- "red"
	# Convert Julian dates into positions on Julian Calendar
	begin.window.radians <- ensemble.par.list$end.window/365*2*pi + pi/2
	end.window.radians <- ensemble.par.list$begin.window/365*2*pi + pi/2
	begin.pred.window.radians <- ensemble.par.list$begin.pred.window/365*2*pi + pi/2
	end.pred.window.radians <- ensemble.par.list$end.pred.window/365*2*pi + pi/2
	for (iii in 1:nnn){
		lines(  c( inner.radius*cos(begin.window.radians [iii]),
					outer.radius*cos(end.window.radians [iii])),
				c( inner.radius*sin(begin.window.radians [iii]),
					outer.radius*sin(end.window.radians [iii])),
					lwd=2.0,
					col=training.window.color)
		#lines(  c( inner.pred.radius*cos(begin.pred.window.radians [iii]),
		#			outer.pred.radius*cos(end.pred.window.radians [iii])),
		#		c( inner.pred.radius*sin(begin.pred.window.radians [iii]),
		#			outer.pred.radius*sin(end.pred.window.radians [iii])),
		#			lwd=2.0,
		#			col=pred.window.color)
		}
	title(main = paste("STEM Temporal Design"),
		font.main=4, line=2, cex.main=2.0 )


 # ---------------------------------------------------------
    return()
# ---------------------------------------------------------------------------------------------------------------------
}# end plot ST ensemble Function
# ---------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------




# ---------------------------------------------------------------------------
# FUNCTION: Plot STEM Spatial Design
# --------------------------------------
# Plots a sinlge realization of the STEM Spatial design
# identified & indexed by its mc.region and time.interval values.
#
#	# -------------------------------
#	regional.polygons <- rbind(regional.polygons,
#	   data.frame(
#	     	    regional.rectangle,
#           	    region.number=rep(iii, NROW(regional.rectangle)),
#          	    region.mc = iii.mc.region,
#          	    time.intervals=iii.interval))
# ----------------------------------------------------------------------------
plot.ST.ensemble <- function(
      ensemble.par.list,
      # Like JDATE-YEAR.SEQ's These two vectors
      # define an index PAIR into the ensemble
      # This means that these have to be the same length!!!!
      # ----------------------------------------------------
	 mc.regions,
	 time.intervals,
      ...) # pass through plotting parameters?
{# ---------------------------------------------------------
    # mc.regions = c(1)
    # time.intervals = c(2)
# -------------------------
# Inits
# ------------------------
      require(maps)
      regional.polygons <- ensemble.par.list$regional.polygons
      xxx <- regional.polygons$x
      yyy <- regional.polygons$y
      # -------------------------
      # Plot clusters
      # ------------------------
	 # Divergent Colors from RColorBrewer
	 col.names <- c( "#E41A1C", "#377EB8", "#4DAF4A",
  					 "#984EA3", "#FF7F00", #"#FFFF33", Remove yellow!!
  					 "#A65628", "#F781BF", "#999999",
  					 "#66C2A5", "#FC8D62", "#8DA0CB",
  					 "#E78AC3", "#A6D854", "#FFD92F",
  					 "#E5C494", "#B3B3B3")
	 # Repeat colors for large sets of polygons
	 col.names <- rep( col.names, times=1000)
       # Intialize Plotting Region
      plot(xxx, yyy, type="n", ...)
 	map('state',add=TRUE, lwd=2, col="yellow")
	map('state',add=TRUE, lwd=1, col="black")
	# ------------------------------------------------
	for (jjj in length(time.intervals)){
	     ttt.index <- regional.polygons$region.mc == mc.regions[jjj] &
		         	  regional.polygons$time.intervals == time.intervals[jjj]
		ttt.poly <- regional.polygons[ttt.index,]
		n.region <- max(ttt.poly$region.number)
		for (iii in 1:n.region){
		    polygon(ttt.poly[ttt.poly$region.number == iii,],
		        			 border = col.names[iii],
					      lwd=2.0,
						 density=NULL)
		    #cat("polygon=",iii," Enter to continue","\n") # prompt
		    #ttt.scan <-scan(n=1,what="character")
		} # end iii
	} # end jjj
	# ------------------------------------------------
	#points(region.centers, col="white", cex=1.5)
	#points(ensemble.data$X$x,ensemble.data$X$y, col="black", cex=.25)
	#points(ensemble.data$X$x,ensemble.data$X$y, col="white", cex=.25)
# ---------------------------------------------------------
    return()
# ---------------------------------------------------------
}# end plot ST ensemble Function
# ---------------------------------------------------------


                 
