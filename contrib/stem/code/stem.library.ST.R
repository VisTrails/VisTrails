


# ------------------------------------------------------------------
# 10.8.08
#  Adding 
#	Point in ploygon Function
# (This is a more basic/generic version of the 
# the point.in.polygon.contours() function in 
# rel.abundance.mapping.functions3.r. 
#
#
# 10.6.08
# Adding Functions: 
#	Point in ShapeFile Function
# 		NOTE: This function is based on the NCEAS function XXXXXX
# 		except that I needed to fix the donut hole problem with 
# 		the shape files. I need to finish documenting this and 
# 		send it back to those guys!
# Initialize Map Gridding
# Needed ==> a more generic regional.cluster.cloropleth.map()
# 	
# ------------------------------------------------------------------


#------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------
# SBT: Better ST Maps
# -------------------------------------
# 9.9.08 
#
# Produce maps and save them to disk.  
# Based on "st.bdt.surface.maps.9.9.R"
#
# 10.20.08 Modifications
# -----------------------------------------
# 1) Added code include the leading zeros on the map.filename 
# 	This produces files that will be sequentially ordered in file browsers!
# 	Small but important "convenience" modification. 
# 2) Also added call to the function initizalize.map.grid() in 
# 	st.clustering.functions.2.R format maps automatically
# 3) Assumed additional parameters 
# 	begin.seq
# 	end.seq
#
# 10/24/08
# -------------------
# * Added code & switch to deal with sqrt transform
# 	# Response Transformation code: resp.transformation.code <- "sqrt"
# * Excluded the extraneous spatial density contours
#
# 11/19/08
# -------------
# google earth maps - transparent & no margin plots. 
# 
#	
# REQUIRES 
# ------------------------
#"eBird taxonomy file.csv",
#"yelwar.East.travel.spatial.density.contours.RData",se
	#~ # ------------------------
	#~ # control.data
	#~ # ------------------------
	#~ # (spp.code, spatial.extent, exp.tag, ST.group)
	#~ # ST groups
	#~ # 	A - 156 - 1 per week 2004-06
	#~ # 	B - 36 - 1 per month 2004 -2006
	#~ # 	C -26 - 1per 2 weeks 2006
	#~ # ------------------------
	#~ "amekes", US, stbdt.8.19., B
	#~ "buffle",US, stbdt.8.19., C
	#~ "buwwar",East, stbdt.8.19., B	
	#~ "barswa", US, stbdt.9.3.,C
	#~ "cavswa", SoTX, stbdt.9.3.,C	
	#~ "cliswa", US, stbdt.9.3.,C
#------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------



## KFW
require(fields)







# These are legacy code for spatial contours
# They will need to be intergrated with current functions
# if this functions stays!
# -------------------------------------------------------------------
# Poisson Predictive Performance Measures
# -------------------------------------------------------------------
# yyy = observations
# ppp = predicted value - response scale 
#
# Verified - replicated GAM deviance calcuatlions for poisson
poisson.deviance <- function(yyy,ppp){
      # if predictions (ppp) equal zero we will get underflow 
      # problems from log function. 
      # -------------
      # break deviance into two pieces - where obs == 0 
      ttt.zero <- (yyy == 0)
      ttt.pos <- (yyy > 0)
      dev1 <- sum( (yyy[ttt.zero] - ppp[ttt.zero]) )
      dev2 <- sum( yyy[ttt.pos]*(log(yyy[ttt.pos])-log(ppp[ttt.pos])) - 
                  (yyy[ttt.pos] - ppp[ttt.pos]))
      dev <- 2*(dev2 - dev1)
      return(dev)
      } 

deviance.explained <- function(yyy,ppp){
      null.deviance <- poisson.deviance(yyy, rep(mean(yyy),length(yyy) ))
      obs.deviance <- poisson.deviance(yyy,ppp)
      deviance.explained <- (null.deviance - obs.deviance)/null.deviance
      de <- list(deviance.explained=deviance.explained, 
                obs.deviance=obs.deviance, 
                null.deviance=null.deviance)
      return(de) 
      }
           
poisson.pearson <- function(yyy,ppp){
      p <- sum( ((yyy - ppp)^2)/(ppp) )
      return(p)
      }    
      
  # Accuracy of 0-1 Classification for Poisson Regression 
  # ---------------------------------------------------------
  poisson.accuracy <-  function(yyy, ppp, threshold=0.5){
      y.binary <- as.numeric(yyy > threshold)
      p.binary <- as.numeric(ppp > threshold)
      acc <- 1-sum(abs(y.binary - p.binary))/length(y.binary)  
      return(acc)
      }    
# -------------------------------------------------------------------
# -------------------------------------------------------------------





# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Measure Predictive performance as a function of Spatial Scale
# -----------------------------------------------------------------------------
# Daniel Fink 
# 1.9.08
# 2.7.08 modifications 
#
# Description
# -----------------
# This function Measures the predictive performance as a function of
# Spatial Scale. It takes the bs.model object from a single test/training
# split and bins/grids this data across a range of scales. Performance 
# is computed and recorded at each scale and passed back to the user. 
# Predictive performance is computed on the test set. 
# Predictive performance may also be plotted as a function of scale.  
# 
# Currently, the function will take the entire spatial extent analyzed/
# in the data set, p.data. 
#
# Input
# ----------
#		p.data, 
#		dtm.obj,
#		grid.size.seq,
#		grid.size.units = "cells",
#		file.name=NULL,
#		plot.it=FALSE,
#		plot.height=600 
#		plot.width=800
#
# Output 
# ----------
#	pred.performance[iii,1] <- perf.ttt$deviance.explained
#	pred.performance[iii,2] <- perf.ttt$obs.deviance
#	pred.performance[iii,3] <- poisson.pearson(zzz.size[ttt.ind],ppp.size[ttt.ind] )
#	# Total number of grid cells that have test-set observations 
#	pred.performance[iii,4] <- NROW(image.pred$ind)
#	# Median # of observations/grid cell, in grid cells with observations 
#	pred.performance[iii,5] <- median(image.pred$weights[image.pred$ind])
#	# Grid Size in units of cells
#	pred.performance[iii,6] <- grid.size[iii]
#	# Grid Size in units of (approximate) km^2
#	pred.performance[iii,7] <- grid.size[iii]
# 
#
# Notes: 
# ---------
#
# Further Development: 
# ----------------------------
# * include km2 as units 
# 	Check out the web page at
# 	 http://www.movable-type.co.uk/scripts/latlong.html
#	 for the Haversine formula 
# * inlcude control over spatial.extent 
# -----------------------------------------------------------------------------
spatial.performance.plot <- function(
		xxx,
    yyy,
    ppp, # predicted
    zzz, #obs 
    spatial.extent=NULL, 
		#dtm.obj,
		grid.size.seq,
		grid.size.ratio = 2,
		grid.size.units = "cells",
		# ----------------------------
		file.name=NULL,
		plot.it=NULL,
		span=0.3,
		plot.height=600, 
		plot.width=800){
# ------------------------------------------
#  Dummy Values
# ------------------------------------------
#   xxx = test.data$X$x[subset.index]
#   yyy = test.data$X$y[subset.index]
#   ppp = test.pred$mean[subset.index]  predicted
#   zzz = test.data$y[subset.index]   observed	
#   spatial.extent = spatial.extent 	
#   grid.size.seq = grid.size.seq
#   grid.size.ratio = 1.0
#   file.name=NULL
#   plot.it=TRUE 
#	 
#         spatial.extent <- list(   
#		   				#  NE Region
#					       	lat.max = 50.0,
#					      	lat.min = 25.0,	
#					      	lon.min= -100.0,
#					      	lon.max = -67.0  )
#         file.name <- FALSE
#         plot.it <- TRUE
#         n.sizes <- 50
#        grid.size.seq <- round(seq(from=5, to=120, length=n.sizes))
         # -----------------------------------         	 
         # verification
         #length(xxx)
         #length(yyy)
         #length(ppp)
         #length(zzz) 	        
         #  image.pred <- as.image(ppp, x= data.frame(xxx,yyy),
	       #        nrow=40, 
	       #        ncol=40, na.rm=TRUE)
         #  image.plot(image.pred)
         #         map('state',add=TRUE, lwd=1, col="grey")        

# ------------------------------------------
#  Initial Values
# ------------------------------------------
 	n.sizes <- length(grid.size.seq)
 	pred.performance <- matrix(0, n.sizes, 20)
	# Covert grid sizes to both units
	# -----------------------------------------	
# ------------------------------------------
#  Compute Baseline-Point Performance
# ------------------------------------------
       epsilon <- 1e-8
       #ppp <- ddd$pred.Xp
       #obs <- p.data$yp
       obs <- zzz
           ttt.index <- ppp == 0      
           ppp[ttt.index] <- epsilon
           ttt.ind <- !is.na(ppp)      
        test.dev <- deviance.explained(obs[ttt.ind],ppp[ttt.ind])$deviance.explained
        test.pearson <- poisson.pearson(obs[ttt.ind],  ppp[ttt.ind])

# ------------------------------------------
#  Compute Performance across scales
# ------------------------------------------
 for (iii in 1:n.sizes){
# -------------------------
#      if (!is.null(spatial.extent)){     
#          # Add two points based on spatial extent
#          # Idea is to set spatial extent manually
#          # I should rewrite the binning myself!
#          # small bias caused in perf. metrics  
#          ppp.ip <- c(ppp,0,0)
#          zzz.ip <- c(zzz,0,0)
#          xxx.ip <- c(xxx,spatial.extent$lon.min,spatial.extent$lon.max)
#          yyy.ip <- c(yyy,spatial.extent$lat.min,spatial.extent$lat.max)  
#    	   image.pred <- as.image(ppp.ip, x= data.frame(xxx.ip,yyy.ip),
#    	               nrow=grid.size.seq[iii]*grid.size.ratio, 
#    	               ncol=grid.size.seq[iii] , na.rm=TRUE)
#    	   image.obs <- as.image(zzz.ip, x= data.frame(xxx.ip,yyy.ip),
#    	               nrow=grid.size.seq[iii]*grid.size.ratio, 
#    	               ncol=grid.size.seq[iii], na.rm=TRUE)
#     } 
# -----------------------
      #if (is.null(spatial.extent)){       
    	   image.pred <- as.image(ppp, x= data.frame(xxx,yyy),
    	               nrow=grid.size.seq[iii]*grid.size.ratio, 
    	               ncol=grid.size.seq[iii] , na.rm=TRUE)
    	   image.obs <- as.image(zzz, x= data.frame(xxx,yyy),
    	               nrow=grid.size.seq[iii]*grid.size.ratio, 
    	               ncol=grid.size.seq[iii]) #, na.rm=TRUE)
    # Form a common na index
    # ---------------------------
     ddd.na.ind <- !is.na(image.pred$weights)
     d2.na.ind <- ddd.na.ind & !is.na(image.obs$weights)    
  
	   ppp.size <- image.pred$z[d2.na.ind ]
	   zzz.size <- image.obs$z[d2.na.ind ]
	   length(ppp.size)
	   length(zzz.size)
	   
       # -------------------------------------
       # Clean Predictions for Dev. Calcs
       # -------------------------------------
       # Substitute predicted zero's with small values
       ttt.index <- ppp.size == 0
       ppp.size[ttt.index] <- epsilon
       # Remove any NA's - several occurr with GAM models
       ttt.ind <- !is.na(ppp.size)
       # -------------------------------------
    	perf.ttt <- deviance.explained(zzz.size[ttt.ind], ppp.size[ttt.ind])
    	pred.performance[iii,1] <- perf.ttt$deviance.explained
    	pred.performance[iii,2] <- perf.ttt$obs.deviance
    	pred.performance[iii,3] <- poisson.pearson(zzz.size[ttt.ind],ppp.size[ttt.ind] )
    	# Total number of grid cells that have test-set observations
      # This is the sample size at this scale 
    	ip.ind <- !is.na(image.pred$weight)
      pred.performance[iii,4] <- sum(ip.ind)
      # Mean Squared error and scaled RMSE
      pred.performance[iii,5] <- sqrt(
              mean((zzz.size[ttt.ind]-ppp.size[ttt.ind])^2))
        pred.performance[iii,6] <- sqrt(
              mean(((zzz.size[ttt.ind]-ppp.size[ttt.ind])/
                    ppp.size[ttt.ind]) )) 
	# -----------------------------	    
	 # Add more 
	 # -------------------------        
	#MSE 
	pred.performance[iii,11] <- mean((ppp.size - zzz.size)^2)
	
	#R2 
	pred.performance[iii,12] <- 1 - mean((ppp.size - zzz.size)^2)/
	mean((mean(zzz.size) - zzz.size)^2)
	#MSE.sqrt 
	pred.performance[iii,13] <- mean((sqrt(ppp.size) - sqrt(zzz.size))^2)
	#R2.sqrt 
	pred.performance[iii,14] <- 1 - mean((sqrt(ppp.size) - sqrt(zzz.size))^2)/
				mean((mean(sqrt(zzz.size)) - sqrt(zzz.size))^2)
	#MAD 
	pred.performance[iii,15]<- mean(abs(ppp.size - zzz.size))
	#rho 
	pred.performance[iii,16]<- cor(zzz.size,ppp.size)
	#rho.sqrt 
	pred.performance[iii,17]<- cor(sqrt(zzz.size),sqrt(ppp.size))
	         
 # --------------------------------              
 
    	# Median # of observations/grid cell, in grid cells with observations 
    	pred.performance[iii,7] <- median(image.pred$weights[ip.ind])
    	pred.performance[iii,8] <- sd(image.pred$weights[ip.ind])
      # Grid Size in units of cells
    	pred.performance[iii,9] <- grid.size.seq[iii]
    	# Grid Size in units of (approximate) km^2
    	# --------------------------------------------------
      #  Great Circle Distance Formula using decimal degrees:
          # Where r is the radius of the earth in whatever units you desire.
          #r <-3437.74677 (nautical miles)
          r <- 6378.7 #(kilometers)
          #r<-3963.0 (statute miles)
          # Assume we are at centered at 40 Lat and 100 lon
          lat1 <- 40
          lon1 <- -100
          # Step size from image grid
          lat2 <- lat1 + (image.pred$y[2]- image.pred$y[1])
          lon2 <- lon1 #+ (image.pred$x[2]- image.pred$x[1])
          cell.height.km <- r * acos(sin(lat1/57.2958) * sin(lat2/57.2958) + 
                      cos(lat1/57.2958) * cos(lat2/57.2958) *  
                      cos(lon2/57.2958 -lon1/57.2958))
          lat2 <- lat1 #+ (image.pred$y[2]- image.pred$y[1])
          lon2 <- lon1 + (image.pred$x[2]- image.pred$x[1])
          cell.width.km <- r * acos(sin(lat1/57.2958) * sin(lat2/57.2958) + 
                      cos(lat1/57.2958) * cos(lat2/57.2958) *  
                      cos(lon2/57.2958 -lon1/57.2958))                      	
    	pred.performance[iii,10] <- cell.width.km*cell.height.km  
 } # end for loop
 # ----------------------------------------------------------
# pred.performance

# ------------------------------------------
# Plot Performance vs Spatial Scale
# ------------------------------------------
	 if  (!is.null(file.name)){
	    	png(file=file.name, 
	    			bg="white",
	    			width = plot.width, 
	    			height = plot.height)
	    			}      
  	if  (!is.null(file.name) | !is.null(plot.it)){
	 	# --------------------------------------
	 	# ** dual x-labels for # cells and km2 would be cool
	 	# ** draw Base-Line at point-level predictive performance
	 	# ** adaptively set maximum y-axis value?  
	 	# ** plot smoothed performance trajectory?? 
	 	# --------------------------------------
		 ymin <- min(c( 0.9*min(pred.performance[,1]),  0.9*test.dev)  )
		 ymax <- max( c( 1.1*max(pred.performance[,1]), 1.1*test.dev) )
		 plot(pred.performance[,9],
		     pred.performance[,1],
		     ylim=c(ymin,ymax),
		     type="p",
		     lwd=2.0,
		     col="red",
		     xlab=" #  latitude cells ", 
		     ylab=" Percent Deviance Explained",
		     main="Performance vs Scale" )
		 # Smoothed Performance 

		 # Smoothed Performance 
		 lines(lowess(pred.performance[,9], pred.performance[,1],
		 		f=span), 
		 		lwd=2.0, 
		 		col="red")
		 # baseline performance
		 lines(range(pred.performance[,9]), 
		            c(test.dev, test.dev),
		            lwd=2.0,
		            col="black")
		            
     		}
	if  (!is.null(file.name)) dev.off() 
	
# ------------------------------------------
# Return Values
# ------------------------------------------    			
return.list <- list(pred.performance=pred.performance,
                    test.dev=test.dev, 
                    test.pearson=test.pearson)    			
return(return.list)    			    
# --------------------------------------------------------------------------
} # end function
# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
# --------------------------------------------------------------------------




# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Generate Contours for Spatial Density of Given Locations
# -----------------------------------------------------------------------------
# Daniel Fink 
# 2.7.08
#
# Description
# -----------------
# Objectives are to 
#   ** estimate 2D KDE over lat & Lon
#       ** second: estimate the SD of prediction error
#   ** exclude/white out lowest level of density surface     
#   ** estimate quantiles of density surface estimates

# ----------------------------------------------------------------------
#
#
# Input
# ----------
#     xxx, yyy - locations 
#     contours - vector of numbers
#     density.cutoff
#
# Output 
# ----------
#   ** draw contours
#   ** return zzz quantile hieghts that define the contours. 
#      This will be a numeric vector with same length as contours 
#
# Notes: 
# ---------
#
# Further Development: 
# ----------------------------
# ** return density estimate
# ** pass through to access options on density estimator
# -----------------------------------------------------------------------------
spatial.density.contours <- function(
		xxx, yyy, 
		contours,
		density.cutoff = 0.1,
		xgridsize = 40, 
		ygridsize = 40,
		# ----------------------------
		file.name =NULL,
		plot.it =FALSE,
		plot.height=600, 
		plot.width=800){
# ------------------------------------------
#  Dummy Values/Calls
# ------------------------------------------

# ------------------------------------------
#  Inits
# ------------------------------------------
    require(GenKern)
    require(maps)
    require(fields)
# -------------------------------------
# GenKern: Estimate 2D KDE over lat & Lon
# ----------------------------------
    # calculate and plot a surface with zero correlation
    # Notes that KernSur 2D KDE can change dramatically by 
    # changing the bandwidths and correlation.
    # The selection of grid size determines spatial resoluation
    # of the contours. Which we want regional. 
    # ------------------------------------------ 
    op <- KernSur(xxx,yyy, 
            xgridsize=xgridsize, 
            ygridsize=ygridsize) 
            #correlation=0, 
            #xbandwidth=1, 
            #ybandwidth=1, 
    # Plot level plot of the Density estimate
      #density.cutoff <- 0.1 # "Zero" Density cutoff
    # cleans up map and calculations
    #par(mfrow=c(1,2))
    image.plot(op$xords, op$yords, 
          log(op$zden+1), 
          zlim = c(density.cutoff, 7),
          col=terrain.colors(100),
          #col=heat.colors(100), 
          axes=TRUE,
          xlab="Longitude",
          ylab="Latitude", 
          main=" eBird Spatial Log Density " )
  # Compute quantiles of the Density estimate. 
  # Note however, that this includes all the zeros that are 
  # in the boundary area. 
  # ---------------------------------------------------------
    # Quantiles for 2004 - 2007 Unique Locations (12008)
    zzz.quant <- quantile( op$zden[op$zden > density.cutoff],  
                  probs = contours) # Defines lower bound for data quality 
    # Quantiles for 2004 - 2007 Unique Locations (12008)
    #zzz.quant <- quantile( op$zden[op$zden > density.cutoff],  
    #                  probs =c(0.983, 0.88, 0.65))   
    # Quantiles for 2006 Unique Locations (~6000) #c(0.85, 0.605))
    # Plot Contours at these levels
    # ------------------------------
    #contour(op$xords, op$yords, op$zden, add=TRUE, 
    #    levels=zzz.quant, 
    #    col=c(1:length(contours))+1,
    #    lwd=2.0)
    box()
    # Add political Boundaries
    map('state',add=TRUE, lwd=2, col="yellow")
    map('state',add=TRUE, lwd=1, col="black")
    #points(xxx,yyy,         cex=0.25)

    # Calculate All Contour Polygons using contourLines
    # contour.poly is a list where each element describes
    #     one ploygon. Elements are 
    #     $level (this is one of the z.quantiles) 
    #     $x 
    #     $y (vectors defining boundary of polygon)
    # -------------------------------------------------
    contour.polygons <- contourLines(op$xords, op$yords, op$zden, 
                                levels=zzz.quant) 
# Return contours as polygons too!!! 
results.list <- list(
        contours = contours,
        xxx = xxx,
        yyy = yyy, 
        log.density.quantiles = zzz.quant,
        contour.polygons = contour.polygons,
        density.KernSur.obj = op) 
 return(results.list)
}#---------------------------------------------------------------------
#-----------------------------------------------------------------------
#-----------------------------------------------------------------------






# --------------------------------------------------------------------------
# Plot Halloween Maps
# -----------------------------
#
#
# -------------------------------------
#   There may be a problem with the halloween.maps()
#	code when there are NO missing values and
# 	this parameter is used: NA.col="grey20")
# ------------------------------------- 
#
#
# jdate.seq
# year.seq
# save.name 
# spp.name <- "Yellow Warbler" 	
# z.min  <- 
# z.max <- 
# If you use the mapping function for a single map, and 
# turn the add=TRUE parameter, then you can add 
# more stuff to the plot. You will need to end it with a call to 
# dev.off()
#
#	# ----------------------------------------------------------------------
#	# Calculate Indices for Point.in.polygon for Contours
#	# ----------------------------------------------------------------------   
#		# Do not filter locations
#		# ------------------------
#		contour.index <- rep(TRUE, length(st.pred$xxx))
#		# Filter locations using archived polygon
#		# --------------------------------
#		sdc.name <- paste(control.dir,
#				"yelwar.East.travel.spatial.density.contours.RData",sep="")
#		load( file=sdc.name) # sd.cont 
#		pip.cont <- point.in.polygon.contours( st.pred$xxx, st.pred$yyy, 
#			                   				sd.cont$contour.polygons)
#		#contour.index <- pip.cont$contour.index[,1]
#	#
##
#
#	#~ # Eg.1. extract individual States
#	#~ #--------------------------------------------------------------
#		#~ sites <- data.frame(lon=st.pred$xxx, lat=st.pred$yyy)
#		#~ shape.dir <-"/mnt/data2/ST.BDT/BDT.shapefiles/" 
#		#~ shape.filename <- "STATES.shp"
#		#~ selected.shape.names <- c("New York", "Georgia")
#		#~ att.selection.column.name <- "STATE_NAME"
#	#~ # --------------------------------------------------------------
#	#~ # Eg.2 extract individual BCRs
#	#~ #--------------------------------------------------------------
#		#~ sites <- data.frame(lon=st.pred$xxx, lat=st.pred$yyy)
#		#~ shape.dir <-"/mnt/data2/ST.BDT/BDT.shapefiles/" 
#		#~ shape.filename <- "bcr.shp"		  # watch capitalization!
#		#~ att.selection.column.name <- "BCR"
##	#~ # --------------------------------------------------------------		#~ selected.shape.names <- c(13, 27)   # class must match att.selection.column
##
#
# --------------------------------------------------------------------------
# DMF 3.19.10 modified from halloween.maps in stem.library.ST.R 
# 					dated 3.16.10
# 
# I am going to add formal parameters so that 
# we can can specify separate input directories for st.matrix files
# and separate directories for map sequence outputs
# --------------------------------------------------------------------------
st.matrix.maps <- function(
			st.matrix.directory, 
			map.directory,
			# --------------
			#save.dir, 
			#save.name, 
			## KFW resp.transformation.code = NULL, 
			# ---------------
			jdate.seq,
			year.seq,
			begin.seq,
			end.seq=length(jdate.seq),
			# ------------------
		# output
			pred.grid.size=NULL,
			map.plot.width = 1000,
			spatial.extent.list = NULL,  
			z.max = NULL,
			z.min = NULL,
			map.tag = NULL,
			google.maps=FALSE, 
			add=FALSE,
			NA.col=NULL,
			halloween.colors=NULL,
			title.text = NULL,
			date.bar = TRUE,
			# -------------------------------------------
			# map args
			# -------------------------------------------
			county.map = FALSE, 
			state.map=TRUE,
			world.map=FALSE,
			state.map.lwd = NULL,
			state.map.col = NULL,
			county.map.lwd = NULL,
			county.map.col = NULL,
			world.map.lwd = NULL,
			world.map.col = NULL,
			# -------------------------
			print.date=FALSE,
			# -------------------------
			...) {
# ------------------------------------------------

			if (is.null(state.map.lwd))	state.map.lwd <- 1.5
			if (is.null(state.map.col))		state.map.col <- "grey"
			if (is.null(county.map.lwd))	county.map.lwd <- 0.5
			if (is.null(county.map.col))	county.map.col <- "grey"
			if (is.null(world.map.lwd))	world.map.lwd <- 2.0
			if (is.null(world.map.col))	world.map.col <- "white"	
#---------------------------------------------

   if ("/" != substring(map.directory, nchar(map.directory), nchar(map.directory))) {
      map.directory <- paste(map.directory, "/", sep="")
   }

   if ("/" != substring(st.matrix.directory, nchar(st.matrix.directory), nchar(st.matrix.directory))) {
      st.matrix.directory <- paste(st.matrix.directory, "/", sep="")
   }

	system(paste("mkdir ", map.directory,sep=""), intern=TRUE)
	# Initialization Info Space-Time Predictions From file
	# ---------------------------------------------- 
	stp.name <- paste(st.matrix.directory,"st.matrix..1.RData",sep="")
	load(stp.name) 
	# ----------------------------------------------------------------------
	# Limit Spatial Extent by Point in Polygon or ShapeFile
	# ----------------------------------------------------------------------   
	contour.index <- rep(TRUE, length(st.pred$xxx))
	if (!is.null(spatial.extent.list)){
		if (spatial.extent.list$type == "rectangle"){
			ttt.index <- ( st.pred$yyy > spatial.extent.list$lat.min & 
						st.pred$yyy < spatial.extent.list$lat.max &
						st.pred$xxx > spatial.extent.list$lon.min & 
						st.pred$xxx < spatial.extent.list$lon.max )
			contour.index <- (ttt.index & contour.index)			  
			}
		  if (spatial.extent.list$type == "polygon"){
			ttt.index <- point.in.polygon(
					    xxx = st.pred$xxx, 
					    yyy = st.pred$yyy,
					    polygon.vertices = 
				      spatial.extent.list$polygon.vertices)
			contour.index <- (ttt.index & contour.index)			  
			  }
		  if (spatial.extent.list$type == "shapefile"){
			  ttt.index <- point.in.shapefile(
				sites = data.frame(lon=st.pred$xxx, lat=st.pred$yyy), 
				shape.dir=spatial.extent.list$shape.dir, 
				shape.filename=spatial.extent.list$shape.filename, 
				att.selection.column.name=
				       spatial.extent.list$att.selection.column.name,
				selected.shape.names=
				    spatial.extent.list$selected.shape.names) 
			  contour.index <- (ttt.index & contour.index)			  
			}				 		
	} 	# if (!is.null(spatial.extent.list)){    	    
	# -------------------------------------------------------------------
	# initizalize.map.grid() formats maps automatically	
	# -------------------------------------------------------------------		
	mapping.spatial.extent <- list(
			lat.max = max( st.pred$yyy[contour.index]),
						  lat.min = min( st.pred$yyy[contour.index]),	
						  lon.min = min( st.pred$xxx[contour.index]),
						  lon.max = max( st.pred$xxx[contour.index]) )	   
	map.inits <- initizalize.map.grid(
						spatial.extent = mapping.spatial.extent,
						map.plot.width = map.plot.width, 
						pred.grid.size = pred.grid.size)
	# ----------------------------------------------------------------------   	
	# Compute Surface Summaries 
	# ----------------------------------------------------------------------   
		st.summary <- matrix(0,(end.seq-begin.seq+1), 7)
		for (iii in begin.seq:end.seq){	
			stp.name <- paste(st.matrix.directory,"st.matrix..",iii,".RData",sep="")
			load(stp.name) 
				# ---------------------------------------------------------------------------
				# Un-tranform Responses
				# ---------------------------------------------------------------------------		
					## KFW if ( resp.transformation.code == "sqrt") {  
					## KFW 		st.pred$pred <- (st.pred$pred) ^2
                                        ## KFW } 
				# ---------------------------------------------------------------------------	
				st.summary[(iii-begin.seq +1),] <- quantile(st.pred$pred[contour.index], 
									probs=c(0, .1,.25,.5,.75,.9,1),
									na.rm = TRUE)
				}
		# Set minium as min of 10th quantiles
		if (is.null(z.min))	z.min <- min(st.summary[,2])
		# Take max as max of 90th quantiles
		if (is.null(z.max))	z.max <- max(st.summary[,6])
	# ---------------------------------------------------------  
	# Convert Temporal Sequence times to POSIX
	# ---------------------------------------------------------
		p.time <- strptime( x=paste(round(jdate.seq),year.seq), "%j %Y")
		# Nice function to convert DateTime Classes 
		month.text <- months(p.time, abbreviate = FALSE)
		date.names <- paste(month.text, " ",p.time$mday,",", year.seq,sep="") 
	# --------------------------------------------------------------
	# Lookup Common Name in eBird Taxonomy File
	# --------------------------------------------------------------
		#	datafile <- paste(control.dir,"eBird taxonomy file.csv",sep="")
		#	eBird.taxonomy <- read.csv(file=datafile) 
		#	#names(eBird.taxonomy)
		#	spp.name <- eBird.taxonomy$PRIMARY_COM_NAME[          
		#				as.character(eBird.taxonomy$SPECIES_CODE) == spp.code ] 
	# --------------------------------------------------------------
	# Will's Halloween Pallete 
	# --------------------------------------------------------------				
	if (is.null(halloween.colors)){	
		n.red <- 100   
		red.colors <- colorRampPalette(
			#-----------------------------------------------------------------------------------------
			# Traditional Halloweeen Map (black under 0.20)
			# -----------------------------------------------------------------------------------------
			#	c("black","black","#FF7100","white"),
			#	bias=1.9)
			# -----------------------------------------------------------------------------------------
			# Low Probability Halloween
			# -----------------------------------------------------------------------------------------
			#	c("black","grey","#FF7100","yellow","white"),
			#	bias=1.0)
			# -----------------------------------------------------------------------------------------
			# Low Probability Halloween 2
			# -----------------------------------------------------------------------------------------
				c("black","grey20","#FF7100","white"),
				bias=2.0)			
			# -----------------------------------------------------------------------------------------
			# Green Halloween
			# -----------------------------------------------------------------------------------------
			#c("black","black","DarkGreen","Green4","Green"),
			#space = "rgb",
	}
	else { 
           n.red <- 100   
           red.colors <- halloween.colors
	}
	
	# --------------------------------------------------------------
	# Loop over Dates
	# --------------------------------------------------------------
	for (iii in begin.seq:end.seq){
		#---------------------------------------------
		# Load Space-Time Predictions From file
		# ---------------------------------------------- 
		#stp.name <- paste(save.dir,save.name,".",iii,".RData",sep="")
		stp.name <- paste(st.matrix.directory,"st.matrix..",iii,".RData",sep="")
		load(stp.name) 
		# ---------------------------------------------------------------------------
		# Un-tranform Responses
		# ---------------------------------------------------------------------------		
			## KFW if ( resp.transformation.code== "sqrt")  
			## KFW 		st.pred$pred <- (st.pred$pred) ^2 
		# ---------------------------------------------------------------------------	
		#----------------------------
		# Surface Height Limits
		# ----------------------------
		st.pred$pred[st.pred$pred < z.min] <- z.min
		st.pred$pred[st.pred$pred > z.max] <- z.max  	
		# --------------
		# --------------
		num.txt <- formatC(iii,format="fg", width=5)
		num.txt <- chartr(" ","0",num.txt)
		map.file.name <- paste(map.directory,map.tag,
						num.txt,".",jdate.seq[iii],
						".",year.seq[iii],".png" ,sep="") 			
		
		# --------------------------------------------------------------
		# "Google".maps == Transparent PNG's
		# --------------------------------------------------------------
		# if TRUE then background = Transparent
		# PNG margins are ajusted. 
		# spatial.extent needs to be communicated to 
		# Google.Earth so that it knows how to overlay image
		# --------------------------------------------------------------						
			if (!google.maps) { 
				png(file=map.file.name, bg="white", 
				    width=map.plot.width, 
				    height=map.inits$map.plot.height) 
				par(mar = c(2,4,4,2), bg="black",fg="grey")  
			}
			if (google.maps) {	
				png(file=map.file.name, bg="transparent", 
				    width=map.plot.width, 
				    height=map.inits$map.plot.height) 
				par(mar=c(0,0,0,0),bg="black",fg="grey",
					xpd=TRUE)
			}			
		# --------------------------------------------------------------
		# Include Date Bar
		# --------------------------------------------------------------	
		if (date.bar) { 
			par(plt = c(0.10, 0.883, 0.25, 0.85) )
			# --------------------------------------------------------				
			# Do not add NA's filled in with given color
			# --------------------------------------------------------
			if ( is.null(NA.col) ) { 
				bs.rpart.maps(			
						xxx = st.pred$xxx[contour.index],
						yyy = st.pred$yyy[contour.index],
						zzz = st.pred$pred[contour.index],
						zlim = c(z.min,z.max),  
						pred.grid.size = map.inits$pred.grid.size , 
						grid.size.ratio = map.inits$grid.size.ratio,  
						axis.args=list(fg="grey", col.axis="grey"),
						# Less than 1 reduces height, 
						# greater than 1 increase height 
						#for given width
						col.palette = red.colors(n.red),  
						axes = FALSE,
						...)
			}
			# --------------------------------------------------------				
			# Add image plot with NA's filled in with given color
			# --------------------------------------------------------
			if ( !is.null(NA.col) ) {
				ttt.st.pred <- rep(NA,length(st.pred$pred))
				ttt.st.pred[is.na(st.pred$pred)] <- 1
				ttt.image <- as.image(
					ttt.st.pred[contour.index],
					x= data.frame(	st.pred$xxx[contour.index],
									st.pred$yyy[contour.index]),
					nrow=round(map.inits$pred.grid.size*
								map.inits$grid.size.ratio),  	# nrow=X direction
					ncol=map.inits$pred.grid.size,     		# ncol=Y direction
					na.rm=TRUE)
				image(ttt.image, 
						col=NA.col, 
						#	 add=TRUE, 	
						axes = FALSE,...)
				if (!is.null(title.text)) {
					title(main=paste(title.text), col="white",line=0)
					}
				bs.rpart.maps(			
					xxx = st.pred$xxx[contour.index],
					yyy = st.pred$yyy[contour.index],
					zzz = st.pred$pred[contour.index],
					zlim = c(z.min,z.max),  
					pred.grid.size = map.inits$pred.grid.size , 
					grid.size.ratio = map.inits$grid.size.ratio,  
					axis.args=list(fg="grey", col.axis="grey"),
					# Less than 1 reduces height, 
					# greater than 1 increase height 
					#for given width
					col.palette = red.colors(n.red),  
					axes = FALSE,
					add=TRUE,
					...)
			}	# !is.null(NA.col)
		# -------------------------------------------------------------
		# Add Date Text
		# -------------------------------------------------------------  		
			if (print.date)  {
				#mtext( paste(date.names[iii]), side=3, col="white")
				text( x= min(st.pred$xxx[contour.index]), 
					y= min(st.pred$yyy[contour.index]), 
					pos=4, #plot to the right
					labels= date.names[iii])
					}
		# -------------------------------------------------------------
		# Add Political Boundaries
		# -------------------------------------------------------------  		
			if (county.map)  map('county',add=TRUE, lwd=county.map.lwd,  col=county.map.col)		
			if (state.map)  map('state',add=TRUE, lwd=state.map.lwd,  col=state.map.col)
			if (world.map)  map('world',add=TRUE, lwd=world.map.lwd,  col=world.map.col)
		# -------------------------------------------------------------		
		# Bottom Date Legend Rectangle
		# -------------------------------------------------------------
			# Find the coordinate for the right boundary of
			# image.plot's "bigplot"
			right.corner <- image.plot.plt()$bigplot[2]
			par(plt = c(0.10, right.corner, 0.15, 0.22) )
			# Set user coordinates for this region
			par(usr=c(-1,366,0,1))
			box(lwd=2, col="grey")
			rect(xleft= (jdate.seq[iii]-2), ybottom=0, xright=(jdate.seq[iii]+2), ytop=2,
			      col=red.colors(n.red)[n.red],
			      border=NA )
			axis(1, at = c(5, 90, 180, 270, 360),
			       labels = c("Jan", "Apr", "Jun", "Sep", "Dec"),
			       cex=1.5,
			       col="grey",
			       col.axis="grey",
			       font=1)
		# -------------------------------------------------------------			
		} # end date.bar == TRUE
		# -------------------------------------------------------------
		
		
		# --------------------------------------------------------------
		# Exclude Date Bar
		# --------------------------------------------------------------	
		if (!date.bar) { 
			# --------------------------------------------------------				
			# Do not add NA's filled in with given color
			# --------------------------------------------------------
			if ( is.null(NA.col) ) { 
				bs.rpart.maps(			
						xxx = st.pred$xxx[contour.index],
						yyy = st.pred$yyy[contour.index],
						zzz = st.pred$pred[contour.index],
						zlim = c(z.min,z.max),  
						pred.grid.size = map.inits$pred.grid.size , 
						grid.size.ratio = map.inits$grid.size.ratio,  
						axis.args=list(fg="grey", col.axis="grey"),
						# Less than 1 reduces height, 
						# greater than 1 increase height 
						#for given width
						col.palette = red.colors(n.red),  
						axes = FALSE,
						...)
			}
			# --------------------------------------------------------				
			# Add image plot with NA's filled in with given color
			# --------------------------------------------------------
			if ( !is.null(NA.col) ) {
				ttt.st.pred <- rep(NA,length(st.pred$pred))
				ttt.st.pred[is.na(st.pred$pred)] <- 1
				ttt.image <- as.image(
					ttt.st.pred[contour.index],
					x= data.frame(	st.pred$xxx[contour.index],
									st.pred$yyy[contour.index]),
					nrow=round(map.inits$pred.grid.size*
								map.inits$grid.size.ratio),  	# nrow=X direction
					ncol=map.inits$pred.grid.size,     		# ncol=Y direction
					na.rm=TRUE)
				image(ttt.image, 
						col=NA.col, 
						#	 add=TRUE, 	
						axes = FALSE,...)
				if (!is.null(title.text)) {
					title(main=paste(title.text), col="white",line=0)
					}
				bs.rpart.maps(			
					xxx = st.pred$xxx[contour.index],
					yyy = st.pred$yyy[contour.index],
					zzz = st.pred$pred[contour.index],
					zlim = c(z.min,z.max),  
					pred.grid.size = map.inits$pred.grid.size , 
					grid.size.ratio = map.inits$grid.size.ratio,  
					axis.args=list(fg="grey", col.axis="grey"),
					# Less than 1 reduces height, 
					# greater than 1 increase height 
					#for given width
					col.palette = red.colors(n.red),  
					axes = FALSE,
					add=TRUE,
					...)
			}	# !is.null(NA.col)
		# -------------------------------------------------------------
		# Add Date Text
		# -------------------------------------------------------------  		
			if (print.date)  {
				#mtext( paste(date.names[iii]), side=3, col="white")
				text( x= min(st.pred$xxx[contour.index]), 
					y= min(st.pred$yyy[contour.index]), 
					pos=4, #plot to the right
					labels= date.names[iii])
					}
		# -------------------------------------------------------------
		# Add Political Boundaries
		# -------------------------------------------------------------  		
			if (county.map)  map('county',add=TRUE, lwd=county.map.lwd,  col=county.map.col)		
			if (state.map)  map('state',add=TRUE, lwd=state.map.lwd,  col=state.map.col)
			if (world.map)  map('world',add=TRUE, lwd=world.map.lwd,  col=world.map.col)
		# -------------------------------------------------------------
		} # end plotting w/o date bar
		# -------------------------------------------------------------  			
		if (add==FALSE) dev.off()			
	# ---------------------------------------------------------------------------		
	} # iii - loop over dates
# -----------------------------------------------------------------------------------	
}# end function
#------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------



# --------------------------------------------------------------------------
# Plot  Base Surface Maps
# -----------------------------
#
#
# Results:  
#
#
# jdate.seq
# year.seq
# save.name 
# spp.name <- "Yellow Warbler" 	
# z.min  <- 
# z.max <- 
		#----------------------------
		# google.maps 
		# ---------------------
		# if TRUE then background = Transparent
		# PNG margins are ajusted. 
		# spatial.extent needs to be communicated to 
		# Google.Earth so that it knows how to overlay image
		# ----------------------------						
# --------------------------------------------------------------------------
surface.maps <- function(
			save.dir, 
			save.name, 
			jdate.seq,
			year.seq,
			begin.seq,
			end.seq=length(jdate.seq),
			## KFW resp.transformation.code = NULL, 
		# output
			pred.grid.size=NULL,
			z.max = NULL,
			z.min = NULL,
			map.tag,
			google.maps=FALSE,
			add=FALSE)  		
{
# ------------------------------------------
	# call to the function initizalize.map.grid() in 
	# st.clustering.functions.2.R format maps automatically	
	# ---------------------------------------------------------------------------------------------------
		map.inits <- initizalize.map.grid(spatial.extent=spatial.extent,
							map.plot.width=map.plot.width, 
							pred.grid.size= pred.grid.size)
		# Reset this for slightly larger grid cells 
	# Response Transformation code 	
		#resp.transformation.code <- "sqrt"
	# Map surface filename tag 
		#map.tag <- paste(exp.name,"st.map.",sep="")
	#---------------------------------------------
	# Initialization Info Space-Time Predictions From file
	# ---------------------------------------------- 
		stp.name <- paste(save.dir, 
				save.name,".",1,".RData",sep="")
		load(stp.name) 
	# ----------------------------------------------------------------------
	# Calculate Indices for Point.in.polygon for Contours
	# ----------------------------------------------------------------------   
		# Do not filter locations
		# ------------------------
		contour.index <- rep(TRUE, length(st.pred$xxx))
		# Filter locations using archived polygon
		# --------------------------------
		sdc.name <- paste(control.dir,
				"yelwar.East.travel.spatial.density.contours.RData",sep="")
		load( file=sdc.name) # sd.cont 
		pip.cont <- point.in.polygon.contours( st.pred$xxx, st.pred$yyy, 
			                   				sd.cont$contour.polygons)
		#contour.index <- pip.cont$contour.index[,1]
	# ----------------------------------------------------------------------   	
	# Compute Surface Summaries 
	# ----------------------------------------------------------------------   
		st.summary <- matrix(0,(end.seq-begin.seq+1), 7)
		for (iii in begin.seq:end.seq){	
			stp.name <- paste(save.dir, 
				save.name,".",iii,".RData",sep="")
			load(stp.name) 
			# ---------------------------------------------------------------------------
			# Un-tranform Responses
			# ---------------------------------------------------------------------------		
				## KFW if ( resp.transformation.code== "sqrt")  
				## KFW 		st.pred$pred <- (st.pred$pred) ^2 
			# ---------------------------------------------------------------------------	
			st.summary[iii,] <- quantile(st.pred$pred[contour.index], 
								probs=c(0, .1,.25,.5,.75,.9,1))
			}
		# Set minium as min of 10th quantiles
		if (is.null(z.min)) z.min <- min(st.summary[,2])
		# Take max as max of 90th quantiles
		if (is.null(z.max))	z.max <- max(st.summary[,6])

			# Compute Slice Quantiles
			#pred.ecdf <- ecdf(st.pred$pred)+
			#qqq <- pred.ecdf(st.pred$pred) 
	# ---------------------------------------------------------  
	# Convert Temporal Sequence times to POSIX
	# ---------------------------------------------------------
		p.time <- strptime( x=paste(round(jdate.seq),year.seq), "%j %Y")
		# Nice function to convert DateTime Classes 
		month.text <- months(p.time, abbreviate = FALSE)
		date.names <- paste(month.text, " ",p.time$mday,",", year.seq,sep="") 
	# --------------------------------------------------------------
	# Lookup Common Name in eBird Taxonomy File
	# --------------------------------------------------------------
		datafile <- paste(control.dir,"eBird taxonomy file.csv",sep="")
		eBird.taxonomy <- read.csv(file=datafile) 
		#names(eBird.taxonomy)
		spp.name <- eBird.taxonomy$PRIMARY_COM_NAME[          
					as.character(eBird.taxonomy$SPECIES_CODE) == spp.code ] 
	# ------------------------------------
	# My "Red" Pallete 
	# ------------------------------------				
		n.red <- 100   
		red.colors <- colorRampPalette(
			c("white","red","#7F0000"), 
			space = "rgb",
			bias=0.5)		  		
	# --------------------------------------- 
	for (iii in begin.seq:end.seq){
		#---------------------------------------------
		# Load Space-Time Predictions From file
		# ---------------------------------------------- 
		stp.name <- paste(save.dir, 
			save.name,".",iii,".RData",sep="")
		load(stp.name) 
		# ---------------------------------------------------------------------------
		# Un-tranform Responses
		# ---------------------------------------------------------------------------		
			## KFW if ( resp.transformation.code== "sqrt")  
			## KFW 		st.pred$pred <- (st.pred$pred) ^2 
		# ---------------------------------------------------------------------------	
		#----------------------------
		# Surface Height Limits
		# ----------------------------
		st.pred$pred[st.pred$pred < z.min] <- z.min
		st.pred$pred[st.pred$pred > z.max] <- z.max  	
		# --------------
		# --------------
		num.txt <- formatC(iii,format="fg", width=5)
		num.txt <- chartr(" ","0",num.txt)
		map.file.name <- paste(save.dir,map.tag,
						num.txt,".",jdate.seq[iii],
						".",year.seq[iii],".png" ,sep="") 			
		
		#----------------------------
		# google.maps 
		# ---------------------
		# if TRUE then background = Transparent
		# PNG margins are ajusted. 
		# spatial.extent needs to be communicated to 
		# Google.Earth so that it knows how to overlay image
		# ----------------------------						
		if (!google.maps) { 
			png(file=map.file.name, bg="white", 
		            width=map.plot.width, 
		            height=map.inits$map.plot.height) 
			par(mfrow=c(1,1), cex=2.0, mar=c(5,4,4,5))  
		}
		if (google.maps) {	
			png(file=map.file.name, bg="transparent", 
		            width=map.plot.width, 
		            height=map.inits$map.plot.height) 
			par(mfrow=c(1,1), 
				cex=2.0, 
				mar=c(0,0,0,0),
				xpd=TRUE)
		}			
		# ---------------
		# Plot Surface 
		# ---------------	
		contour.index <- pip.cont$contour.index[,1]
		bs.rpart.maps(			
				xxx = st.pred$xxx[contour.index],
				yyy = st.pred$yyy[contour.index],
				zzz = st.pred$pred[contour.index],
				zlim = c(z.min,z.max),  
				pred.grid.size = map.inits$pred.grid.size , 
				grid.size.ratio = map.inits$grid.size.ratio,  
				# Less than 1 reduces height, 
				# greater than 1 increase height 
				#for given width
				col.palette = red.colors(n.red),  
				#spatial.extent =  spatial.extent.map  ,
				xlab= "Longitude",
				ylab= "Latitude")
		title(main = paste(spp.name, "  ", date.names[iii]) , 
			font.main=4, line=1, cex.main=3.0 )
		# -------------------------------------------------------------
		# Add Polygon Boundaries
		# -------------------------------------------------------------           
		kk <- 1 # first (lower) quantile
		hd.index <- pip.cont$contour.level.index ==
				sd.cont$log.density.quantiles[kk]
		hd.set <- (1:length(pip.cont$contour.level.index))[hd.index]
		# There are 9 polygons in this set, but only the first and fourth 
		# are the big important regions
		for (kkk in c(1,4)){
			polygon(sd.cont$contour.polygons[[kkk]])  #$x,
			#sd.cont$contour.polygons[[jjj]]$y,
			# col=  "black",  #c.col[kk],
			#border=TRUE)             
			}                                             		
		# -------------------------------------------------------------
		# Add Political Boundaries
		# -------------------------------------------------------------  
			require(maps)
      map('county',add=TRUE, lwd=2, col="grey") 
			map('state',add=TRUE, lwd=3, col="yellow")
			map('state',add=TRUE, lwd=2, col="black") 
		# -----------------------------------------------------
		# -------------------------------------------------------------
		if (add==FALSE) dev.off()
		} # iii - st.pred index
}# end fuction  		
#------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------



# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------
# Initialize Map Gridding 
# ------------------------------------------------------------
# 10.7.08
#
# This needs to be cleaned up a bit
# 
# Input:
# -------------
#			
# Output:
# ----------
#
# Examples: 
# ------------------
# --------------------------------------------------
	#~ spatial.extent  <- list( lat.max = 45.0,
						 #~ lat.min = 39.0,	
						 #~ lon.min= -82.5,
						 #~ lon.max = -67.0  )	
	#~ # ----------------------------------------
	#~ if (spatial.extent.code == "US") {
		#~ spatial.extent <- spatial.extent.US
		#~ map.plot.width <- 1800  
		#~ #pred.grid.size <- 100 #height == lat
		#~ }
# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------


initizalize.map.grid <- function(
    	spatial.extent=NULL,
    	lat=NULL,
    	lon=NULL,
    	map.plot.width,
    	pred.grid.size=NULL	){
# Needs either spatial.extent or lat & lon	
# -----------------------------------------------------------------------------
# ST Surface Plots Inits
# ----------------------------------------------------------------------------- 
#~ Latitude and longitude can be used very simply for plotting 
#~ by setting up a rectangular grid (e.g. like a Simple Cylindrical Projection) 
#~ The question is how to scale the length:width of the rectangles. 
#~ At the equator a degree of latitude is roughly the same length 
#~ in miles as a degree of longitude - ignoring the asphericity of the 
#~ Earth's globe. Thus, at the equator, a square grid would be satisfactory 
#~ for a small map. 
#	
#~ As we move further away from the equator, e.g. where the continental US lies, 
#~ a degree of longitude is shorter in miles, though a degree of latitude 
#~ is much the same. Thus, a square lat-lon grid in the continental US distorts 
# distances, the map being stretched E-W. Using a rectangular lat-lon grid
# gives a truer picture of everyday miles. 
#
#~ The ratio of lengths for a degree latitude:longitude approximately corresponds 
#~ to the inverse of the cosine of the latitude. For example, at 40 degrees 
#~ latitude,  the ratio of lat:lon is appriximately 1/cos(40 degrees) = 1.31. 
#~ This is the ratio for latitude of Denver,CO Springfield, IL, or Harrisburg, PA. 
#
#~ This ratio of latitude:longitude is used to determine an appropriate 
#~ ratio of map image size (length & width in pixes) as well to determine 
# grid size ratio so that 
#~ grid cells plotted in the map surface have approximately equal length width & height in miles. 
#~ For simplicity, I use a fixed grid size for mapping.  The ratio of 
#~ the length latitude:longitude length of the pixels is adjusted to 
#~ the inverse of the cosine of the latitude from the middle of the spatial 
#~ extent being plotted. 
# -----------------------------------------------------------------------------------------------------
	# user specified: Width of image (png file) in pixels
	#map.plot.width <- 1500  
	middle.lat <- mean(spatial.extent$lat.max,spatial.extent$lat.min)
	pixels.per.degree.lon <- map.plot.width/
			(spatial.extent$lon.max - spatial.extent$lon.min)
	length.lat.to.length.lon.ratio <- 1/cos(middle.lat/360*2*pi)
	pixels.per.degree.lat <- length.lat.to.length.lon.ratio  * 
						pixels.per.degree.lon
	map.plot.height <- round(pixels.per.degree.lat * 
			(spatial.extent$lat.max-spatial.extent$lat.min))

# ------------------------------------------------------------------------
  # Discretization size
  # ------------------------------------------------------------------------
  # Calculate the maximum number of grid cells (minimum grid cell area)
  # to achieve the 10 random locations per cell from the prediction
  # grid design.
  #
  # NOTE: It appears that with these setting there are FAR more than 
  # 			10 random locs per cell!!!!
  #
  # The minimum Longitude grid side = . .14436 deg long
  # At 40 degrees Lat, a change of  .14436 lon is 12km in length. 
  # This number comes from the stratified design used to sample the 
  # random locations based on extent and 400 equally spaced lon cells: 
  #                          .14436 deg long =   (-124.72839 - -66.98426)/400
  #
  # The minimum Latitude grid side = ..12210 deg lat
  # At 40 degrees Lat, a change of .12210 lat is 14 km in length. 
  # This number comes from the stratified design used to sample the 
  # random locations based on extent and 200 equally spaced lat cells: 
  #				.12210 deg lat= (48.97630 - 24.55572)/200
  #------------------------------------------------------------------------
	if (is.null(pred.grid.size)) {
		  # Calculate Maximum pred.grid.size for this region
		  pred.grid.size.max.xxx <- 
			floor( (spatial.extent$lon.max - spatial.extent$lon.min)/.145)
		  pred.grid.size.max.yyy <- 
			floor( (spatial.extent$lat.max - spatial.extent$lat.min)/.123 )
		  if (pred.grid.size.max.xxx < pred.grid.size.max.yyy)
		        pred.grid.size <- floor(pred.grid.size.max.xxx)
		  if (pred.grid.size.max.xxx > pred.grid.size.max.yyy)
		        pred.grid.size <- floor(pred.grid.size.max.yyy)
		  #pred.grid.size
		  }
	# -------------------------------------------------------------------
	# User specified: number of latitude cells across spatial.extent
	#pred.grid.size <- 100 
	# --------------------------------------------------------------------------
	# longitude cells = pred.grid.size * grid.size.ratio 
	# Note that this ratio really takes into account two 
	# quantities, the ratio of the lat:lon distances on the 
	# surface of the Earth as well as the lat:lon ratio of 
	# the spatial extent.
	# -------------------------------------------------------------------------
	cells.per.degree.lat <- pred.grid.size/
			(spatial.extent$lat.max - spatial.extent$lat.min)
	cells.per.degree.lon <-  cells.per.degree.lat /  
						length.lat.to.length.lon.ratio  						
	grid.cell.plot.width <- cells.per.degree.lon * 
			(spatial.extent$lon.max-spatial.extent$lon.min)	
	grid.size.ratio  <-   grid.cell.plot.width/pred.grid.size    		
		#grid.size.ratio
		#pred.grid.size
		#grid.cell.plot.width
		
	# ---------------------------------------------------------------------------------
	# How long are the sides of a grid cell? 
	# ----------------------------------------------------------------------------------
	# Assume a grid cell centered at 40 degrees lat
	# ----------------------------------------------------------------------------------
	# Formula for distance between two points on a great circle
	# Each point needs to be expressed in radians
	# ---------------------------------------------------------------------------------------------
	lat1<- (40)*pi/180
	lon1 <- 70*pi/180
	lat2 <- (40 + 1/cells.per.degree.lat)*pi/180
	lon2 <- lon1
	d <- 2*asin(sqrt((sin((lat1-lat2)/2))^2 + 
                 cos(lat1)*cos(lat2)*(sin((lon1-lon2)/2))^2))	
	radius.km <- 6371.0 
	lat.distance.km <- radius.km * d
	# ---------------------------------------------------------------------------------------------
	lat1<- (40)*pi/180
	lon1 <- 70*pi/180
	lon2 <- (70 + 1/cells.per.degree.lon)*pi/180
	lat2 <- lat1
	d <- 2*asin(sqrt((sin((lat1-lat2)/2))^2 + 
                 cos(lat1)*cos(lat2)*(sin((lon1-lon2)/2))^2))	
	radius.km <- 6371.0 
	lon.distance.km <- radius.km * d
 	# ----------------------------	

return(list(
		pixels.per.degree.lon=pixels.per.degree.lon,
		pixels.per.degree.lat=pixels.per.degree.lat,
		map.plot.height=map.plot.height,
		length.lat.to.length.lon.ratio=length.lat.to.length.lon.ratio,
		cells.per.degree.lat =cells.per.degree.lat ,
		cells.per.degree.lon=cells.per.degree.lon,
		grid.cell.plot.width=grid.cell.plot.width,
		grid.size.ratio =grid.size.ratio,
		pred.grid.size=pred.grid.size,
		lon.distance.km=lon.distance.km,
		lat.distance.km=lat.distance.km))
} # end function
# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------
# Point in Shapefile Polygon Operation
# ------------------------------------------------------------
# 6.3.08
# 10.6.08
#
# This function performs the "Point in shapefile" operation 
# for BCRs and Statenames for a specific set of shapefiles.
# Because each shape file has its own attr data frame, there are two 
# steps to select shapes:
# 	1) find the att.selection.column of the att.data data.frame 
# 	2) search for selected.shape.names in the att.selection.column
#
# NOTE: This function is based on the NCEAS function XXXXXX
# except that I needed to fix the donut hole problem with 
# the shape files. I need to finish documenting this and 
# send it back to those guys!
#
# NOTE: 1.9.09
# ---------------
# I changed the way that I access attributes - 
# I ran into problems not having S4 objects
#
# Input:
# -------------
#     shape.dir
#     shape.filename
#     sites = data.frame with lat & lon vectors for spatial extent/universe 
#	att.selection.column.name = the name of the att.data column
# 	selected.shape.names = vector of region/shape names from shape file
#			
# Output:
# ----------
#     location.pip - T/F vector the length of the sites
#
# Examples: 
# ------------------
	#~ # --------------------------------------------------------------
	#~ # Eg.1. extract individual States
	#~ #--------------------------------------------------------------
		#~ sites <- data.frame(lon=st.pred$xxx, lat=st.pred$yyy)
		#~ shape.dir <-"/mnt/data2/ST.BDT/BDT.shapefiles/" 
		#~ shape.filename <- "STATES.shp"
		#~ selected.shape.names <- c("New York", "Georgia")
		#~ att.selection.column.name <- "STATE_NAME"
	#~ # --------------------------------------------------------------
	#~ # Eg.2 extract individual BCRs
	#~ #--------------------------------------------------------------
		#~ sites <- data.frame(lon=st.pred$xxx, lat=st.pred$yyy)
		#~ shape.dir <-"/mnt/data2/ST.BDT/BDT.shapefiles/" 
		#~ shape.filename <- "bcr.shp"		  # watch capitalization!
		#~ att.selection.column.name <- "BCR"
		#~ selected.shape.names <- c(13, 27)   # class must match att.selection.column

		#~ # ------------------------------------------------------------
	#~ location.pip <- point.in.shapefile(
			#~ sites, 
			#~ shape.dir, 
			#~ shape.filename, 
			#~ att.selection.column.name,
			#~ selected.shape.names) 
	#~ plot(sites)
	#~ points(sites[location.pip,], col="red",cex=0.25)		
# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------
point.in.shapefile <- function(
		sites, 
		shape.dir, 
		shape.filename, 
		att.selection.column.name,
		selected.shape.names
		 ) {
# ------------------------------------------------------------------------------------------------------
	require(maptools)
	require(splancs)
	#require(maps)
	# --------------------------------------------------------------
	# Read Shape File & Create Map object (using Maptools package)
	#--------------------------------------------------------------
		#shape.dir <-"c:\\users\\Research.AKN\\BDT\\Data\\point.in.polygon\\"
		#shape.dir <- data.dir
		#shape.filename <- "STATES.shp"
		#shape.data <- read.shape(paste(shape.dir,shape.filename,sep=""))
		
		# 2.24.10 Theo Damoulas 
		# The map tools library was "updated"
		# !!!!!!! function read.shape deprecated use internal ::: to find
		shape.data <- maptools:::read.shape(paste(shape.dir,shape.filename,sep=""))
		#maptools:::getinfo.shape(paste(shape.dir,shape.filename,sep=""))		
		
		# --------------------------------------------------------------------------------
		# Because each shape file has its own attr data frame, 
		# 	1) find the att.selection.column.name of the att.data data.frame 
		# 	2) search for selected.shape.names in the att.selection.column
		# --------------------------------------------------------------------------------
		att.col.index <-( names(shape.data$att.data) %in% 
                      att.selection.column.name )
		#selected.regions <- subset(Map2poly(shape.data),
		#		shape.data$att.data[, att.col.index] %in% selected.shape.names  )
		selected.regions <- subset(maptools:::Map2poly(shape.data),
				shape.data$att.data[, att.col.index] %in% selected.shape.names  )
				
	# ----------------------------------------------
	# PIP function
	# ----------------------------------------------
		selected.sites <- NULL           
		nnn.regions <- length(selected.regions[])
		point.in.poly.ind <- NULL
		for (iii in 1:nnn.regions){
			# --------------------------------------------------
			temp.region <- selected.regions[[iii]]               
			# cycle through individual parts within each polygon region
			# performing the PinP operation one part at a time
			# instead of one region at a time
			# ------------------------------------------------
			attr.temp <- attributes(temp.region)
      #nParts <-  temp.region@nParts
			nParts <- attr.temp$nParts
      for (jjj in 1:nParts) {
				#begin.ttt <- temp.region@pstart$from[jjj]
				#end.ttt <- temp.region@pstart$to[jjj]
				begin.ttt <- attr.temp$pstart$from[jjj]
				end.ttt <- attr.temp$pstart$to[jjj]
				ttt <- temp.region[begin.ttt:end.ttt,]                   
				res <- try(inpip(sites[c("lon","lat")], ttt))
				# If no errors, collect indices of sites that
				# are within the set of polygons.
				if (class(res)=="integer")
					point.in.poly.ind <- c(point.in.poly.ind,res)
			} # end for jjj
		} #end for iii
	# --------------------------------------------------------	
	# Collect all point in Polygon set
	# --------------------------------------------------------
	location.pip <- rep(FALSE, NROW(sites))
	location.pip[point.in.poly.ind] <- TRUE
	return(location.pip)
} # end function
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Point-in-Polygon Function
# -----------------------------------------------------------------------------
# Daniel Fink 
# 10.08.08
# 03.17.10
#
# Description
# -----------------
# For a given set of locations determine if they fall into 
# a sinlge Polygon. Return one index (length of locations).  
#
# Input
# ----------
#     xxx, yyy - locations 
#     polygon.vertices - data.frame with named vertices x and y 
# 							corresponding to xxx and yyy coordinates, resp.
# 
# Output 
# ----------
# 		 index vector the length of locations
#
# Notes: 
# ---------
#
# Examples: 
# ----------
#nnn <- 1000
#xxx <- rnorm(nnn, mean=0, sd=1)
#yyy <- rnorm(nnn, mean=0, sd=1)
#unit.sq.polygon <- data.frame( x=c(0,0,1,1),y=c(0,1,1,0))
#pip.index <- point.in.polygon(
#								xxx = xxx, 
#								yyy = yyy,
#								polygon.vertices = unit.sq.polygon)
#plot(xxx, yyy, type="n")
#polygon(unit.sq.polygon, col="blue")
#points(xxx,yyy)
#points(xxx[pip.index], yyy[pip.index], pch=19, col="yellow")					
#	
# -----------------------------------------------------------------------------
point.in.polygon <- function(
		xxx, yyy, 
		polygon.vertices){
# ------------------------------------------
    require(splancs)
 		ttt.index <- inpip(cbind(xxx,yyy),
                              cbind(polygon.vertices$x, 
                                    polygon.vertices$y))
		data.index <- rep(FALSE, length(xxx))
		data.index[ttt.index] <- TRUE   
 return(data.index)
}#---------------------------------------------------------------------
#-----------------------------------------------------------------------
# Drew, Kevin, and the Point in Polygon requires a lot 
# DF: is very general - allows very flexible spatial partions
# Drew: is computationally intensive
# Kevin: is easily replaced 
# 
# I have changed the name because point.in.polygon is 
# used LEGITIMATELY used in many other routines. 
# This new function expedites the logic that selects 
# stixels (ST ensemble extents/subsets)
# 	 predict.ST.ensemble
# 	 sample.ST.ensemble
# 	and create.ST.ensemble
#
#
# ------------------------------------------
# ------------------------------------------
## For North America
##
## min(x), max(y)
##       -----------------------
##       |                     |
##       |                     |    		
##       |                     | 
##       |                     |           
##       |                     |
##       |                     |            
##       -----------------------
##                       max(x), min(y)
##
## This means that even if the base model extents 
## were indeed non-rectangular polgons, then 
## this logic will simply cover each polygon with 
## the smallest covering retangle. 
## This is an interesting idea. 
##
##
## Here is another way to do it: 
# The order of the vertices written by create.ST.ensemble is:
# 1)	Lower Left corner
# 2) 	Upper Left
# 3) 	Upper Right
# 4) 	Lower Right
#	ttt.index <- rep(FALSE, length(xxx))
#	ttt.index <- xxx >= polygon.vertices$x[1] &
#				xxx <= polygon.vertices$x[4] & 
#				yyy >= polygon.vertices$y[1] &
#				xxx <= polygon.vertices$y[2] 
#
#-----------------------------------------------------------------------
# -----------------------------------------------------------------------------
point.in.rectangle <- function(
		xxx, yyy, 
		polygon.vertices){
# ------------------------------------------
    maxX <- max(polygon.vertices$x)
    minX <- min(polygon.vertices$x)
    maxY <- max(polygon.vertices$y)
    minY <- min(polygon.vertices$y)
    newDataIndex <- rep(FALSE, length(xxx))
    locationMask <- xxx <= maxX & xxx >= minX & yyy <= maxY & yyy >= minY   
    newDataIndex[locationMask] <- TRUE
####    if (isTRUE(all.equal(data.index,newDataIndex)) == FALSE) {
####       print("~~~~~ point.in.polygon FALSE")
####    }
   return(newDataIndex)
}#---------------------------------------------------------------------
#-----------------------------------------------------------------------
#-----------------------------------------------------------------------


# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
# BS.RPART Mapping Plot Function   
# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
# 1.2.08
#
# Description:
# ----------------
# This function produces a single map image using fields. 
# No smoothing. 
# Primitive (i.e. rectangular) control of spatial extent  
#
# INPUT
# ------------			
#   xxx
#   yyy
#   zzz
#
# OUTPUT
# ------------
#
# To do: 
# ---------
#
# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
bs.rpart.maps <- function(
		# Data			
			xxx, 
			yyy,
			zzz,
			pred.grid.size = NULL, 
      			grid.size.ratio = 2, 	
			spatial.extent = NULL,
	        # Save File
     			save.name = NULL,
			plot.width = 800,
			plot.height = 600,
			main.text = NULL,
		# Pass in other plotting parameters 
			col.palette=NULL,
			... )
{  #begin function

# ------------------------------------------------------
# Inits
# ------------------------------------------------------
	call <- match.call()
    	require(maps)
    	require(fields)  
    	
    	if (is.null(col.palette)){
    	# Color scheme stolen from sp library	
	 col.palette<- c(   	
	  "#000033FF", "#00003CFF", "#000046FF", "#00004FFF", "#000058FF", "#000061FF",
	  "#00006BFF", "#000074FF", "#00007DFF", "#000086FF", "#000090FF", "#000099FF",
	  "#0000A2FF", "#0000ACFF", "#0000B5FF", "#0000BEFF", "#0000C7FF", "#0000D1FF",
	  "#0000DAFF", "#0000E3FF", "#0000ECFF", "#0000F6FF", "#0000FFFF", "#0700FFFF",
	  "#0E00FFFF", "#1600FFFF", "#1D00FFFF", "#2400FFFF", "#2B00FFFF", "#3300FFFF",
	  "#3A00FFFF", "#4100FFFF", "#4800FFFF", "#5000FFFF", "#5700FFFF", "#5E00FFFF",
	  "#6500FFFF", "#6D00FFFF", "#7400FFFF", "#7B00FFFF", "#8200FFFF", "#8A01FEFF",
	  "#9106F9FF", "#980BF4FF", "#9F0FF0FF", "#A714EBFF", "#AE19E6FF", "#B51DE2FF",
	  "#BC22DDFF", "#C426D9FF", "#CB2BD4FF", "#D230CFFF", "#D934CBFF", "#E139C6FF",
	  "#E83EC1FF", "#EF42BDFF", "#F647B8FF", "#FE4CB3FF", "#FF50AFFF", "#FF55AAFF",
	  "#FF59A6FF", "#FF5EA1FF", "#FF639CFF", "#FF6798FF", "#FF6C93FF", "#FF718EFF",
	  "#FF758AFF", "#FF7A85FF", "#FF7F80FF", "#FF837CFF", "#FF8877FF", "#FF8C73FF",
	  "#FF916EFF", "#FF9669FF", "#FF9A65FF", "#FF9F60FF", "#FFA45BFF", "#FFA857FF",
	  "#FFAD52FF", "#FFB24DFF", "#FFB649FF", "#FFBB44FF", "#FFBF40FF", "#FFC43BFF",
	  "#FFC936FF", "#FFCD32FF", "#FFD22DFF", "#FFD728FF", "#FFDB24FF", "#FFE01FFF",
	  "#FFE51AFF", "#FFE916FF", "#FFEE11FF", "#FFF20DFF", "#FFF708FF", "#FFFC03FF",
	  "#FFFF09FF", "#FFFF26FF", "#FFFF43FF", "#FFFF60FF")}

# ----------------------------------------------
# Set Spatial Extent
# ----------------------------------------------
    	if  (!is.null(spatial.extent)) { 
	     	if (is.null(spatial.extent$lat.max))   spatial.extent$lat.max <- max(yyy)
	     	if (is.null(spatial.extent$lat.min))   spatial.extent$lat.min <- min(yyy)
	     	if (is.null(spatial.extent$lon.min))   spatial.extent$lon.min <- min(xxx)
	     	if (is.null(spatial.extent$lon.max))   spatial.extent$lon.max <- max(xxx)
	      	x.zoom.ind <- (xxx < spatial.extent$lon.max & xxx > spatial.extent$lon.min)
	      	y.zoom.ind <- (yyy < spatial.extent$lat.max & yyy > spatial.extent$lat.min)
	      	zoom.ind <- as.logical( x.zoom.ind & y.zoom.ind)
	      	#sum(zoom.ind)
	      	zzz <- zzz[zoom.ind]
	      	xxx <- xxx[zoom.ind] 
	      	yyy <- yyy[zoom.ind] 
     	}   

  # ------------------------------------------------------------------------
  # Discretization size
  # ------------------------------------------------------------------------
  # Calculate the maximum number of grid cells(minimum grid cell area)
  # to achieve the 10 random locations per cell from the prediction
  # grid design.
  #
  # The minimum Longitude grid side = .28872 deg long
  # This number comes from the stratified design used to sample the 
  # random locations based on extent and 200 equally spaced lon cells: 
  #                          .28872 deg long =   (-124.72839 - -66.98426)/200
  #
  # The minimum Latitude grid side = .24421 deg lat
  # This number comes from the stratified design used to sample the 
  # random locations based on extent and 100 equally spaced lat cells: 
  #				.24421 deg lat= (48.97630 - 24.55572)/100
  #------------------------------------------------------------------------
	if (is.null(pred.grid.size)) {
		  # Calculate Maximum pred.grid.size for this region
		  pred.grid.size.max.xxx <- floor( (max(xxx) - min(xxx))/.28872 )
		  pred.grid.size.max.yyy <- floor( (max(yyy) - min(yyy))/.24421 )
		  if (pred.grid.size.max.xxx/2 < pred.grid.size.max.yyy)
		        pred.grid.size <- floor(pred.grid.size.max.xxx/2)
		  if (pred.grid.size.max.xxx > pred.grid.size.max.yyy*2)
		        pred.grid.size <- floor(pred.grid.size.max.yyy)
		  #pred.grid.size
		  }

  # ----------------------------------------------
  # Create Prediction Grid with as.image
  # ----------------------------------------------   
      ttt.image <- as.image(zzz,
                x= data.frame(xxx,yyy),
                nrow=round(pred.grid.size*grid.size.ratio),  	# nrow=X direction
                ncol=pred.grid.size,     		# ncol=Y direction
		na.rm=TRUE)

    if  (!is.null(save.name)){
    	png(file=save.name, 
    			bg="white",
    			width = plot.width, 
    			height = plot.height)
    			}      
      image.plot(ttt.image, 
      		col = col.palette, ...) 
          #      			zlim=c(0,5))
       	if  (!is.null(main.text)){
     		title(main = main.text , font.main=4, line=2) 
		    title(main = paste("Spatial Grid:",pred.grid.size,"x",
	            pred.grid.size*2), font.main=4, line=1, cex.main=0.75)}
      
      # Add political Boundaries
      # ----------------------------
      #map('state',add=TRUE, lwd=2, col="yellow")
      #map('state',add=TRUE, lwd=1.5, col="black")

if  (!is.null(save.name)){
    	dev.off()
    			}
    
# --------------------------------------------------------------------------
} # end function
# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
# --------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Point-in-Polygon Contours
# -----------------------------------------------------------------------------
# Daniel Fink 
# 2.7.08
#
# Description
# -----------------
# For a given set of locations determine if they fall into 
# a set of Polygon contours. Return one index (lenght of locations)
# for each unique level of polygon contours. 
#
# Also compute quantiles for locations and make a pretty picture. 
#
# Input
# ----------
#     xxx, yyy - locations 
#     contour.polygons - list of polygon contours from contourLines 
#                         function
#
# Output 
# ----------
# Return one index (lenght of locations)
# for each unique level of polygon contours.
#
# Notes: 
# ---------
#
# Further Development: 
# ----------------------------
# -----------------------------------------------------------------------------
point.in.polygon.contours <- function(
		xxx, yyy, 
		contour.polygons){
# ------------------------------------------
#  Dummy Values/Calls
# ------------------------------------------
 #contour.polygons <- sd.cont$contour.polygons
# ------------------------------------------
#  Inits
# ------------------------------------------
    require(splancs)

# ------------------------------------------
#  Identify unique polygon levels 
# ------------------------------------------
   level.index <- rep(0,length(contour.polygons)) 
   for (iii in 1:length(contour.polygons)) 
       level.index[iii] <- contour.polygons[[iii]]$level
   unique.levels <- sort(unique(level.index))
   # Matrix of Contour indices
   contour.index <- matrix(FALSE,length(xxx),length(unique.levels))   
               
    # Cycle through all Polygons in order  
    # ** Do point-in-polygon operations 
    # ** store indices according to polygon level 
    # ----------------------------------------------------------
        #sum.points <- 0
        for (jjj in 1:length(contour.polygons)) {
            ttt.ind <- inpip(cbind(yyy,xxx),
                              cbind(contour.polygons[[jjj]]$y, 
                                    contour.polygons[[jjj]]$x))
            # Construct/store contour indices
            col.index <- (contour.polygons[[jjj]]$level == unique.levels)
            contour.index[ ttt.ind, col.index] <- TRUE
            }        
        # -----------------------
        # Empirical Quantiles
        empirical.quant <- apply(contour.index, 2, mean)

    # ---------------------------------------------------------
    # Construct Indices into nonoverlapping contours
    # ---------------------------------------------------------
       non.olap.index <- matrix(FALSE, NROW(contour.index), 
                           NCOL(contour.index)) 
       # Begin with smallest contour
       non.olap.index[,NCOL(contour.index)] <-
              contour.index[,NCOL(contour.index)]  
       # Sequentially subtract
       for (iii in NCOL(contour.index):2){    
              non.olap.index[,(iii-1)] <- (contour.index[,(iii-1)] & 
                                            !contour.index[,iii])
            }         
       # % of data in each contour
       n.contour <- apply(non.olap.index, 2, sum)
    # ---------------------------------------------------------
            
# Return contours as polygons too!!! 
results.list <- list(
        xxx = xxx,
        yyy = yyy, 
        empirical.quant = empirical.quant,
        contour.polygons = contour.polygons,
        contour.index = contour.index,
        contour.level.index = level.index, 
        non.olap.index = non.olap.index, 
        n.contour = n.contour) 
 return(results.list)
}#---------------------------------------------------------------------
#-----------------------------------------------------------------------


#-----------------------------------------------------------------------
# -------------------------------------------------------------------------------
# Smooth ST Predictions 
#  
# -------------------------------------------------------------------------------
smooth.st.predictions <- function(
		kkk, # Single Time slice
		pred.grid.size, # roughly twice desired plotting resolution
		gam.smoothing.knots=25, 
		st.rough.dir,
    		st.rough.name ,
		st.smooth.dir ,
		st.smooth.name){
		# ----------------
		#shape.dir, # <- "C:\\users\\Research.STBDT\\Data\\BDT.shapefiles\\"
    		#shape.filename, # <- "STATES.shp"
    		#selected.state.names = NULL) {
  # -----------------------------------------------
    stp.name <- paste(st.rough.dir,st.rough.name,".",kkk,".RData",sep="")
		load(stp.name) #st.pred   
    require(mgcv)
    # -----------------------------------------------
    xxx <- st.pred$xxx
    yyy <- st.pred$yyy
    #xxx.name <- "Lon"
    #yyy.name <- "Lat"
    zzz <- st.pred$pred
    # -----------------------------------------------
    require(mgcv)
    d.gam <- gam( zzz ~ s(xxx,yyy, k=gam.smoothing.knots))
    nnn.xxx <- pred.grid.size
    nnn.yyy <- pred.grid.size
    xxx.pred <- seq(from=min(xxx),to=max(xxx),length=nnn.xxx)
    yyy.pred <- seq(from=min(yyy),to=max(yyy),length=nnn.yyy)
    pred.design <- expand.grid(xxx=xxx.pred, yyy=yyy.pred)
    # "Fuzz up" Prediction Grid to better fill in image.plot
    pred.design$xxx <- pred.design$xxx + runif(NROW(pred.design), 
                min = -(abs(xxx.pred[2] - xxx.pred[1]))/2.,
                max =  (abs(xxx.pred[2] - xxx.pred[1]))/2.)
    pred.design$yyy <- pred.design$yyy + runif(NROW(pred.design), 
                min = -(abs(yyy.pred[2] - yyy.pred[1]))/2.,
                max =  (abs(yyy.pred[2] - yyy.pred[1]))/2.)
#  # -------------------------------------------------------
#  # Cutout US States to reduce prediction time! 
#	# --------------------------------------------------------------
#	if (!is.null(selected.state.names)){
#		sites <- data.frame(lon=pred.design$xxx, lat=pred.design$yyy)
#		#shape.dir <- "C:\\users\\Research.STBDT\\Data\\BDT.shapefiles\\"
#    		#shape.filename <- "STATES.shp"
#    		#selected.shape.names <- 
#        #      c("New York", "Pennsylvania", "New Jersey", 
#        #        "Ohio", "West Virginia", "Delaware", "Connecticut",
#        #        "Rhode Island", "Massachusetts", 
#        #        "Vermont", "New Hampshire", "Maine", 
#        #        "Maryland", "Virginia")
#	  att.selection.column.name <- "STATE_NAME"
#    	  location.pip <- point.in.shapefile(
#    			sites, 
#    			shape.dir, 
#    			shape.filename, 
#    			att.selection.column.name,
#    			selected.shape.names=selected.state.names) 
#    	   #plot(sites)
#    	   #points(sites[location.pip,], col="red",cex=0.25)	    
#        pred.design <- pred.design[ location.pip, ]
#    }            
#    # -------------------------------
    pred.gam <- predict(d.gam, 
                newdata=pred.design,
                se.fit=FALSE, type="response")
    st.pred <- data.frame(pred.design, pred=pred.gam)
    names(st.pred)
    dim(st.pred)
    # -----------------------------------------------
    smooth.filename <- paste(st.smooth.dir,st.smooth.name,".",kkk,".RData",sep="")
    save(st.pred, file=smooth.filename)
    # For initialization in Halloween.maps()
    #smooth.filename <- paste(st.smooth.dir,st.smooth.name,".",1,".RData",sep="")
    #save(st.pred, file=smooth.filename)
    # -----------------------------------------------  
  # ------------------------------------------------------------
  # Return Values
  # ------------------------------------------------------------
} # end function
# --------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------


# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
# Load & Process SPAT_COVAR Data for Spatial Prediction
# --------------------------------------------------------------------------
# This function will load, subsample, and process the Spatial
# prediction data.
#
# Like the other functions I am writing, I will begin by keeping
# this as simple as possible. KISS!!
#
# INPUT
# ------------
# INPUT
# ------------
# 	pred.data.file <- character string for file location including directory
#       	pred.dir <-  "~/norcar.temp/USA Prediction Grid/"
#        	pred.data.file <- paste(pred.dir,"Random.locations.NE.10.31.07.csv",sep="")
#
#
#   		This file is assumed to contain the following fields/information
#
#		what happens if a field is missing?
#		Should these fields be compared/match to the p.data$X fields used to
# 			develop the model?
#
#
# 	NNN.pred <- (sub)sample size of prediction data file. Defalult = NULL
#				(defaults to whole data set)
#	NNN <- 5000
# 	spatial.extent <- list( # NE Region
#				      lat.max <- 45.0,
#				      lat.min <- 39.0,
#				      lon.min <- -82.5,
#				      lon.max <- -67.0  )
#
# OUTPUT
# ------------
# 	D.pred  - prediction data frame
# 	locs - 	locations corresponding to D.pred
#
# To do:
# ---------
# I need to describe the format of D.pred in detail so that I can
# generate new sets. Part of this will be to point to/describe the
# process that Roger and I went through to generate this data.
#
# Currently, I have hard coded the list of predictor variables that
# to be added to D.pred. I would like to add logic to match and
# keep only those predictors that match a list of predictor names
# 		target.var <- names(p.data$X)
# possibly matching the classes of the variables too. That would
# be very useful.
#
# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
make.SPAT.COVAR.pred.data <- function(
			pred.data.file,
			NNN.pred = NULL,
			spatial.extent = NULL)  {
# ---------------------------------------------------
	call <- match.call()
# ----------------------------------------------
# Load Data
# ----------------------------------------------
        D.pred <- read.csv(file=pred.data.file)
        #dim(D.pred) #27933   67
# ----------------------------------------------
# Set Spatial Extent
# ----------------------------------------------
    	if  (!is.null(spatial.extent)) {
	     	xxx <- D.pred$DECIMAL_LONGITUDE
	     	yyy <- D.pred$DECIMAL_LATITUDE
	     	if (is.null(spatial.extent$lat.max))   spatial.extent$lat.max <- max(yyy)
	     	if (is.null(spatial.extent$lat.min))   spatial.extent$lat.min <- min(yyy)
	     	if (is.null(spatial.extent$lon.min))   spatial.extent$lon.min <- min(xxx)
	     	if (is.null(spatial.extent$lon.max))   spatial.extent$lon.max <- max(xxx)
	      	x.zoom.ind <- (xxx < spatial.extent$lon.max & xxx > spatial.extent$lon.min)
	      	y.zoom.ind <- (yyy < spatial.extent$lat.max & yyy > spatial.extent$lat.min)
	      	zoom.ind <- as.logical( x.zoom.ind & y.zoom.ind)
	      	#sum(zoom.ind)
	      	D.pred <- D.pred[zoom.ind, ]
	      	rm(xxx,yyy)
     	}

# ---------------------------------------------------------------------
# Convert regional NCLD classes counts to proportions
# ---------------------------------------------------------------------
	  # Currently, Rogers NLCD neighborhood variables in SPATCOVAR
	  # contain the counts of each landcover class within the given neighborhood.
	  #   i.e percentages x 100
	  # # of cells = (a*r)^2
	  #
	  # This was only for earlier version ==>
	  # It should be a non-issue with the "new" version of
	  # "ebird.data.processing.12.03.07.R"
	  # ----------------------------------------------------
	  #  NLCD01_CMN"   "NLCD01_IMN", are already stored as %'s
	  # However, I am going to include them so that these
	  # predictors are 100% compatible with the ebird predictors.
	  # I need to fix the ebird data!!!
	  # ------------------------------------------------------------
	  nbhd.size <- c("A10R15", "A10R5", "A100R5")
	  nbhd.cell.size <- c(22500,2500,250000)
	  nlcd.vars <- c(
	          "NLCD01_N11",           "NLCD01_N12",
	          "NLCD01_N21",           "NLCD01_N22",
	          "NLCD01_N23",           "NLCD01_N24",
	          "NLCD01_N31",           "NLCD01_N41",
	          "NLCD01_N42",           "NLCD01_N43",
	          "NLCD01_N52",           "NLCD01_N71",
	          "NLCD01_N81",           "NLCD01_N82",
	          "NLCD01_N90",           "NLCD01_N95")
	  for (iii in 1:3) {
		    regional.nlcd.vars <- paste(nlcd.vars, nbhd.size[iii] ,sep="")
		    D.pred[,names(D.pred) %in% regional.nlcd.vars] <-
		          D.pred[,names(D.pred) %in%
		          	regional.nlcd.vars]/nbhd.cell.size[iii]*100
	  }
# ------------------------------------------------------------
# Subsampling
# ------------------------------------------------------------
  subsample.index <- NULL
  if (!is.null(NNN.pred)) {
        	if (NNN.pred < NROW(D.pred)){
        		subsample.index <- sample(1:NROW(D.pred), NNN.pred)
        		D.pred <- D.pred[subsample.index, ]
        }}

# ------------------------------------------------------------
# Predictor Processing
# ------------------------------------------------------------
	        y <- D.pred$DECIMAL_LATITUDE
	        x <- D.pred$DECIMAL_LONGITUDE
	        # List of D.NE predictors that need to be removed
	        remove.var <- c( "X", "DECIMAL_LATITUDE_CS", "DECIMAL_LONGITUDE_CS",
	                      "NED48_ELEVATION",  "BLOCKGROUP_FIPS_ESRI04" ,
	                      "DECIMAL_LATITUDE",  "DECIMAL_LONGITUDE")
	                      # "NLCD01_IMPERV" , "NLCD01_LANDCOVER" )
	        D.pred <-  D.pred[ , !(names(D.pred) %in% remove.var) ]
    	# BCR Processing: BCR == 0 occurs at coastline locations
    	# ---------------------------------------------------------------------
	          #points( loc.x[ D.pred$BCR == 0],
	          #      loc.y[ D.pred$BCR == 0],
	          #      col=4,
	          #      cex=3.0,
	          #      pch=5)
	          D.pred$BCR[ D.pred$BCR == 0] <- NA
	          D.pred$BCR <- as.factor(D.pred$BCR)
            	  D.pred$NLCD01_LANDCOVER <- as.factor(D.pred$NLCD01_LANDCOVER)
    	# Append Lat & lon
    	# ------------------------------------------
        	D.pred <- cbind(D.pred, x, y)
# ------------------------------------------------------------
# Return Values
# ------------------------------------------------------------
	locs <- data.frame(x = x, y=y)
	data.list <- list(
		call = call,
		locs = locs,
		D.pred = D.pred,
		subsample.index=subsample.index)
	return(data.list)
} # end function

# --------------------------------------------------------------------------
# --------------------------------------------------------------------------





# -----------------------------------------------------------------------------------------------------------
# Plot Monthly Training Data Map
# -----------------------------------------------------------------------------------------------------------		
monthly.maps <- function(	
		    xxx,
		    yyy,
		    jdates,
		    zzz, # same length as (xxx, yyy, jdates)
		    zzz.index.1,  #red   obs > pred  ===> Predictions too BIG
		    zzz.index.2)
{# ----------------------------------------
		mo.txt <- c("Jan","Feb","Mar","Apr","May","Jun",
				"Jul","Aug","Sep","Oct","Nov","Dec")	
		require(maps)  
	     par(mfrow=c(3,4),mar=c(0,0,1,0),cex=1.0)
		n.period <- 12
		for (iii in 1:n.period) {
			#Subseting Criterion
			# -------------------------------------
			#ll <- min(jdates)
			#ul <- max(jdates)
			#ttt.index <- jdates >= ll & jdates <= ul 
			ll <- (365/n.period)*(iii-1)
			ul <- (365/n.period)*(iii)
			ttt.index <- jdates > ll & jdates < ul 
			# --------------------------------------
			plot(	xxx[ttt.index], 
				yyy[ttt.index], 
					#type="n",
					cex=0.25,
					pch=19,
					col="grey",
					axes = FALSE,
					main=paste( mo.txt[iii], " ", format(ll, digits=3),":", 
							format(ul, digits=3),"   + propor = ",
							format(sum(zzz[ttt.index] > 0)/ sum(ttt.index),
							digits=3)))
			box()
			# ---------------------------------------
			# Add negative residuals in blue 
			# RED, neg res ==> ppp> yyy ==> almost all occur when yyy == 0)
			# ----------------------------------------
			ttt.index <- jdates > ll & jdates < ul & zzz.index.1
			points(	xxx[ttt.index], 
					yyy[ttt.index], 
					cex=sqrt(abs(zzz[ttt.index])),
					col="red",
					#cex=0.25,
					pch=1)	
			# BLUE ==> ppp < yyy
			ttt.index <- jdates > ll & jdates < ul  & zzz.index.2
			points(	xxx[ttt.index], 
					yyy[ttt.index], 
					cex=sqrt(abs(zzz[ttt.index])),
					col="blue",
					#cex=0.25,
					pch=4)					
			# Add political Boundaries
			# ----------------------------
			map('state',add=TRUE, lwd=2, col="yellow")
			map('state',add=TRUE, lwd=1.5, col="black")   
		} # end iii = months

  # ------------------------------------------------------------
  # Return Values
  # ------------------------------------------------------------
	return()
} # end function
# --------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------


# ------------------------------------------------------------------
#  FOR LOOP over time slices (within season)
#   * Load Predicted Surface
#   * Pixelate it
#   * Stack pixelated surface into Clustering design
#        row = pixel/locations, cols= times
#        ==> group trajectories
#        Q: rows come from stack/unstack(ttt.image) ??
#   * END FOR
#
#  Then cluster the Clustering design
#  Output: each row, i.e. pixel/location will get a cluster
#          label and a silhoullette number
#
#  Plot these on a map, perhaps one color at a time.
#
#
# Inputs: 
# ---------
#   		stp.save.name,  #bs.stp.save.name
#         temporal.index,
#         pred.grid.size,
#         grid.size.ratio,
#         spatial.index=NULL  This is an index on the prediction vector, 
# 								usually used to select regions (BCR's or states) 
# Outputs: 
# ---------
#return.list <- list(call=call,
#                    X=X.cluster,
#                    X.image = ttt.image)
# ------------------------------------------------------------------
make.functional.data.design.matrix <- function(
         stp.save.dir,	#bs.stp.save.dir 
	    stp.save.name,  #bs.stp.save.name
         temporal.index,
         pred.grid.size,
         grid.size.ratio,
         spatial.index=NULL){
 # ----------------------------------
	call <- match.call()
    # ------------------------------------------------------------
    X.cluster <- NULL
    # ------------------------------------------------
    for (iii in (temporal.index)){
      # ----------------------------------------------
      # Load Space-Time Predictions From file
      # ----------------------------------------------
          stp.name <- paste(stp.save.dir,stp.save.name,".",iii,".RData",sep="")
    			load(stp.name) # st.pred
      # ----------------------------------------------
      # Spatial Index
      # ----------------------------------------------      
          if (is.null(spatial.index))  
                spatial.index <- rep(TRUE, length(st.pred$xxx))
      # ----------------------------------------------
      # Create Prediction Grid with as.image
      # ----------------------------------------------
          xxx <- st.pred$xxx[spatial.index]
          yyy <- st.pred$yyy[spatial.index]
          zzz <- st.pred$pred[spatial.index]
      # ----------------------------------------------
      # Stack/Unstack using as.image
      # ----------------------------------------------
          ttt.image <- as.image(zzz,
                    x= data.frame(xxx,yyy),
                    nrow=round(pred.grid.size*grid.size.ratio), # nrow=X direction
                    ncol=pred.grid.size,
				na.rm=TRUE)     		                # ncol=Y direction
           #names(ttt.image)
           # ---------------------
           zzz.vector <- rep(0, length( ttt.image$ind[,1] ))
           for (jjj in 1:length( ttt.image$ind[,1] ))
                  zzz.vector[jjj] <- ttt.image$z[ ttt.image$ind[jjj,1],
                                                  ttt.image$ind[jjj,2]]
           #zzz.loc.x <- ttt.image$x[ttt.image$ind[,1]]
           #zzz.loc.y <- ttt.image$y[ttt.image$ind[,2]]
           # ---------------------
           #hist(zzz.vector)
           #image.plot(ttt.image)
           #points(ttt.image$x[ttt.image$ind[,1]],
           #       ttt.image$y[ttt.image$ind[,2]],
           #       cex=0.5*zzz.vector ,
           #       col="yellow")
           # ---------------------
      # ----------------------------------------------
      # Add to cluster design
      # ----------------------------------------------
      X.cluster <- cbind(X.cluster, zzz.vector)
  } # end iii
# ------------------------------------------
# Return Values
# ------------------------------------------
return.list <- list(call=call,
                    X=X.cluster,
                    X.image = ttt.image)
return(return.list)
# --------------------------------------------------------------------------
} # end function
# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
# --------------------------------------------------------------------------

