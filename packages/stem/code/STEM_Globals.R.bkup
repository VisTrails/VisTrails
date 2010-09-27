
debugOutput <- FALSE
# Slash direction for directory creation
platform = "linux"
# Possibly Spp names info
	
# Required Packages
require(rpart)
require(mgcv)
require(gbm)
require(fields)
require(splancs)
require(maps)
require(maptools)
	
# Source STEM Libraries
source(paste(code.directory,"stem.library.A.R",sep=""))	
source(paste(code.directory,"stem.library.B.R",sep=""))  
source(paste(code.directory,"stem.library.ST.R",sep=""))
	
# Source MORE STEM Functions 
#source(paste(code.directory,"STEM_erd.data.creation.R",sep=""))
source(paste(code.directory,"STEM_erd.srd.data.subsetting.R",sep=""))	
source(paste(code.directory,"STEM_ModelFitting.R",sep="") )	
source(paste(code.directory,"predict.eBird.ST.matrix.R",sep=""))	
source(paste(code.directory,"STEM_st.matrix.cv.average.R",sep=""))


## Name of space time matrix sub-directory
st.matrix.name <- "stm"

## Name of space time matrix ave map sub-directory
st.matrix.ave.maps <- "stm.ave.maps"



# ------------------------
# Select One Species
# speciesList - a list of vectors. vector[1] = scientificName & vector[2] = commonName 
# ------------------------
speciesList <- list(
c("Hylocichla_mustelina", "Wood_Thrush"))
#c("Cyanocitta_cristata", "Blue_Jay"))
#c("Euphagus_carolinus", "Rusty_Blackbird"))
#c("Turdus_migratorius", "American_Robin"))
#c("Seiurus_aurocapilla", "Ovenbird"), 
#c("Vireo_olivaceus", "Red-eyed_Vireo")) 
#c("Cardinalis_cardinalis", "Northern_Cardinal"))
#c("Junco_hyemalis", "Dark-eyed_Junco"), 
#c("Piranga_olivacea", "Scarlet_Tanager"))
#c("Carduelis_pinus", "Pine_Siskin"))
#c("Hylocichla_mustelina", "Wood_Thrush"))
#c("Colinus_virginianus", "Northern_Bobwhite"))

# -----------------------------------------------------
# SRD maximum sample size - this further restricts SRD
# in addition to ERD spatial restrictions above)
# -----------------------------------------------------
srd.max.sample.size <- 5000

## response.family = "bernoulli" or "gaussian"
response.family <- "bernoulli"
	
# ----------------------------------------------------------------------
# Spatial Extent by Point in Rectangle, Polygon, or ShapeFile
# ----------------------------------------------------------------------   
#spatial.extent.list <- NULL # Full US
# -----------
#spatial.extent.list <- list(type = "rectangle",
#				lat.min = 25.0,  
#				lat.max = 50.0,
#				lon.min = -130.0,
#				lon.max = -65.0)
# -----------
spatial.extent.list <- list(type = "polygon",
			# data.frame with named vertices x and y
			polygon.vertices = 
				data.frame(x = c(-85,-85,-70,-70), 
						   y = c(35, 50, 50, 35)) )
# -----------
#spatial.extent.list <- list(type="shapefile",
#			shape.dir = data.dir.shapefiles,
#			att.selection.column.name = "BCR",
#			# watch capitalization!
#			shape.filename =  "bcr.shp",  
#			selected.shape.names = c(13))
# -----------	
#spatial.extent.list <- list(type="shapefile",
#			shape.dir = data.dir.shapefiles, 
#			att.selection.column.name = "STATE_NAME",
#			shape.filename = "STATES.shp",
#			selected.shape.names = c("New York")) 

	
# -------------------------------------------------------------------
# Temporal Extent
# -------------------------------------------------------------------	
temporal.extent.list <- list(begin.jdate = 1, 
			begin.year = 2006, 
			end.jdate = 366, 
			end.year = 2008)
iii.year <- 2008
n.intervals.per.year <-52
n.intervals <- n.intervals.per.year  + 1
jdate.seq <- seq(from = temporal.extent.list[['begin.jdate']], to = temporal.extent.list[['end.jdate']], length = (n.intervals))
if (n.intervals > 1) {
   jdate.seq <- round((jdate.seq[2:n.intervals] + jdate.seq[1:(n.intervals-1)])/2)
}
year.seq <- rep(iii.year, length(jdate.seq))
begin.seq <- 1
end.seq <- length(jdate.seq)



# ------------------------
# Select predictors - must be a subset of what is in erd…..
# ------------------------
predictor.names <- c("YEAR", "TIME", "DAY",
		     "EFFORT_HRS", "EFFORT_DISTANCE_KM",
		     "NUMBER_OBSERVERS", "HOUSING_DENSITY",
		     "ELEV_NED",    	
		     "CAUS_TEMP_AVG",
		     "CAUS_TEMP_MIN", "CAUS_TEMP_MAX",
		     "CAUS_PREC", "CAUS_SNOW",
		     "NLCD2001_FS_C11_750_PLAND", "NLCD2001_FS_C12_750_PLAND",
		     "NLCD2001_FS_C21_750_PLAND", "NLCD2001_FS_C22_750_PLAND",
		     "NLCD2001_FS_C23_750_PLAND", "NLCD2001_FS_C24_750_PLAND",
		     "NLCD2001_FS_C31_750_PLAND", "NLCD2001_FS_C41_750_PLAND",
		     "NLCD2001_FS_C42_750_PLAND", "NLCD2001_FS_C43_750_PLAND",
		     "NLCD2001_FS_C52_750_PLAND", "NLCD2001_FS_C71_750_PLAND",
		     "NLCD2001_FS_C81_750_PLAND", "NLCD2001_FS_C82_750_PLAND",
		     "NLCD2001_FS_C90_750_PLAND", "NLCD2001_FS_C95_750_PLAND")	

# -------------------------------------------------------------------
# Data Splitting Parameters 
# -------------------------------------------------------------------	
split.par.list <- list(grid.cell.min.lat = 0.75,
                       grid.cell.min.lon = 0.75,
                       min.val.cell.locs = 2,
                       fraction.training.data=0.8,
                       mfrac=1.0,
                       plot.it=FALSE)	

# -------------------------------------------------------------------
# CV Fold Splitting Parameters 
# -------------------------------------------------------------------	
cv.folds <- 1
cv.list <- c(1:cv.folds)	
cv.folds.par.list <- list(grid.cell.min.lat = 0.75,
                          grid.cell.min.lon = 0.75,
                          min.val.cell.locs = 2,
                          fraction.training.data = 0.8,
                          mfrac = 1.0,
                          plot.it = FALSE)						

# ---------------------------------------------------------------------
# STEM Ensemble Design
# ---------------------------------------------------------------------
iii.scale <- 2  # largest scale in STEM MS ==> current magic value
stem.init.par.list <- list(  
	# --------------------------------------------------
	# Spatial Design
	# --------------------------------------------------
	spatial.extent.list = NULL,
	spatial.region.par.list = list(	
		# Number of MC regionalizations for each time interval
		n.mc.regions=1, 
		# define minimum area & sample size of rectangles
		regional.cell.min.lat = 3.00*iii.scale,
		regional.cell.min.lon = 4.00*iii.scale,
		# Underlying Coverage Grid
			# Older declarations
			# grid.cell.min.lat = 1*(iii.scale^0.5), #5 degrees
			# grid.cell.min.lon = 1.75*(iii.scale^0.5), # 10 degrees
		# Simplified
		grid.cell.min.lat = 3.00*iii.scale/3, #5 degrees
		grid.cell.min.lon = 4.00*iii.scale/3, # 10 degrees
		n.centers.per.region = 1, # Density Dependent!!!
		min.data.size = 10),
	# --------------------------------------------------
	# Temporal Design: 
	# Slice year into n.intervals prediction points
	# --------------------------------------------------
	n.intervals=60,  #add 1!    # 81 for migration
	begin.jdate=1 ,
	end.jdate = 366,
	season.window.width=40,  #40       # Fitting window
	prediction.window.width=36,  #36
	# --------------------------------------------------
	# Sampling
	# --------------------------------------------------
	sampling.par.list = list(
		split.by.location = FALSE,
	    # if TRUE uses locs == ensemble.data.locs
	    ST.basis.rotation = FALSE,
	    # if TRUE assumes {lat,lon} ={$y, $ x} 
	    # and julian date == $JDATES 
	    p.train=0.75))				

base.model.par.list <- rpart.control(cp = 0.01, xval = 0, minbucket = 10)

# ---------------------------------------------------------------------
# conditioning variables
# ---------------------------------------------------------------------

conditioning.vars <- list(EFFORT_HRS = 1.0,
			  EFFORT_DISTANCE_KM = 1.0,
			  TIME = 7.0,
			  NUMBER_OBSERVERS = 1.0,
			  I.STATIONARY = 0)

# -----------------------------------------------------------------------------
# ----------------------------------------------------------------------------- 
# ST Matrix Maps 
# (AKA Halloween Maps) 
# -----------------------------------------------------------------------------
# ----------------------------------------------------------------------------- 

ns.rows <- 40
map.plot.pixel.width <- 1000
z.max <- 0.50
z.min <- 0.0
map.filename.tag <- "demo."
state.map <- TRUE   	
state.map.lwd <- 1.0
county.map <- TRUE                                                                                   
county.map.lwd <- 0.5
pred.grid.size <- ns.rows
## map.plot.width <- map.plot.pixel.width
map.plot.width <- 1000
## This is duplicated in stem.init.par.list
spatial.extent.list <- NULL
map.tag <- map.filename.tag
date.bar <- TRUE
print.date <- TRUE
## KFW resp.transformation.code <- NULL
