# -----------------------------------------------------------------------------
# ----------------------------------------------------------------------------- 
# Compute ST Matrix fold-average
# # DMF 3.19.10 
# 
# The fold-average st.mat predictions produces
# a single ST matrix object and stores it in the output dir.
# 
# The idea here is the ST matrix handle is the directory name
# So, different ST matrices need to live in different directories
# because each directory will have the same file names. 
#
# Remember, we are assuming that the loc list is identical for 
# all cv.folds. 
#
#
#
# Inputs
# 	stem.dir
# 	st.matrix.input.name
# 	jdate.seq
# 	year.seq
# Outputs:
# 	ST.matrix 
#
#
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------		
st.matrix.cv.average <- function(
		stem.directory, #=stem.directory
		st.matrix.input.directory,	# st.matrix project name #st.matrix.file.tag, # = "demo." 
	  	cv.list, # = c(1:cv.folds) 
		jdate.seq = jdate.seq,
		year.seq = year.seq,			   
		st.matrix.output.directory){
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------					    

   if ("/" == substring(st.matrix.input.directory, nchar(st.matrix.input.directory), nchar(st.matrix.input.directory))) {
      st.matrix.directory <- st.matrix.input.directory
   }
   else {
      st.matrix.directory <- paste(st.matrix.input.directory, "/", sep="")
   }

   if ("/" == substring(st.matrix.output.directory, nchar(st.matrix.output.directory), nchar(st.matrix.output.directory))) {
      st.matrix.output.directory <- st.matrix.output.directory
   }
   else {
      st.matrix.output.directory <- paste(st.matrix.output.directory, "/", sep="")
   }

   system(paste("mkdir ", st.matrix.output.directory,sep=""), intern=TRUE)
# -----------------
for (iii in 1:length(jdate.seq)){	
	cv.pred <- NULL
	for (iii.cv in cv.list){
		# --------------------------------------------------------------------
		# Load data into (location, time) matrix
		# --------------------------------------------------------------------
		#results.dir <- paste(stem.directory,"stem.results.",iii.cv, "/",sep="")
		#stem.ST.matrix.file.tag <- 
		#	paste(results.dir,st.matrix.file.tag,"st.matrix.",sep="")
		results.dir <- paste(st.matrix.directory, "st.matrix.", 
				as.character(iii.cv), "/",sep="")	
		stem.ST.matrix.file.tag <- 
	    		paste(results.dir,"st.matrix.",sep="")
		stp.name <- paste(stem.ST.matrix.file.tag,".",iii,".RData",sep="")
		load(stp.name) # st.pred
		#names(st.pred) #xxx      yyy      pred        sd
		if (iii.cv == cv.list[1]) cv.pred <- st.pred$pred
		if (iii.cv != cv.list[1]) cv.pred <- cv.pred + st.pred$pred
	} # iii.cv 
	st.pred$pred <- cv.pred/length(cv.list)
	# -----------------------
	# Save st.pred
	# -----------------------
	# map.dir 
	cv.ave.st.pred.filename <- paste(st.matrix.output.directory,
					"st.matrix..",iii,".RData",sep="")

	save(st.pred, file = cv.ave.st.pred.filename) # st.pred
} # end iii - intervals
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
} # end function 
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------






        
