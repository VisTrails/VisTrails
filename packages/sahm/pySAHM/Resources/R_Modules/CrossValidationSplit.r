CrossValidationSplit<-function(input.file,output.file,response.col="ResponseBinary",n.folds=10,stratify=FALSE){

#Description:
#this code takes as input an mds file with the first line being the predictor or
#response name, the second line an indicator of predictors to include and the
#third line being paths where tif files can be found.   An output file and a
#response column must also be specified.  Given a number of folds, a new
#column is created indicating which fold each observation will be assigned to
#if a Split Column is also found (test/train split) then only the train portion
#will be assigned a fold.  Optional stratification by response is also available
#Background points are ignored
#by this module (they are read in, written out, but not assigned to cv folds.
#Output is written to a csv that can be used by the
#SAHM R modules.

#Written by Marian Talbert 9/29/2011

     if(n.folds<=1 | n.folds%%1!=0) stop("n.folds must be an integer greater than 1")
      browser()

   #Read input data and remove any columns to be excluded
          dat.in<-read.csv(input.file,header=FALSE,as.is=TRUE)
          dat<-as.data.frame(dat.in[4:dim(dat.in)[1],])
          names(dat)<-dat.in[1,]

        response<-dat[,match(tolower(response.col),tolower(names(dat)))]

          if(sum(as.numeric(response)==0)==0 && !is.null(stratify)) stop("The ratio of presence to absence cannot be set with only presence data")

      #Ignoring background data that might be present in the mds

          bg.dat<-dat[response==-9999,]

          if(dim(bg.dat)[1]!=0){
            dat<-dat[-c(which(response==-9999,arr.ind=TRUE)),]
            dat.in<-dat.in[-c(which(response==-9999,arr.ind=TRUE)+3),]
            response<-response[-c(which(response==-9999,arr.ind=TRUE))]
            bg.dat$TrainSplit=""
            }

            #this splits the training set
             split.mask<-dat[,match(tolower("split"),tolower(names(dat)))]=="train"
             index<-seq(1:nrow(dat))[split.mask]
             if(stratify==TRUE){
               dat[,ncol(dat)+1]<-NA
                for(i in 1:names(table(response))){
                  index.i<-index[response[split.mask]==names(table(response))[i]]
                  index.i<-index.i[order(runif(length(index.i)))]
                  dat[index.i,ncol(dat)]<-c(rep(seq(1:n.folds),each=floor(length(index.i)/n.folds)),sample(seq(1:n.folds),size=length(index.i)%%n.folds,replace=FALSE))
                }
             } else{
                index<-index[order(runif(length(index)))]
                dat[index,ncol(dat)+1]<-c(rep(seq(1:n.folds),each=floor(length(index)/n.folds)),sample(seq(1:n.folds),size=length(index)%%n.folds,replace=FALSE))
             }

         #inserting data must be done in 3 steps because dat.in isn't a proper dataframe in that
         #not all elements in a column are of the same type
          dat.in<-dat.in[c(1:3,rownames(dat)),] #removing rows that weren't selected for the test train split
          dat.in[4:(dim(dat.in)[1]),(dim(dat.in)[2]+1)]<-dat$TrainSplit
          dat.in[c(1,3),(dim(dat.in)[2])]<-c("Split","")
          dat.in[2,(dim(dat.in)[2])]<-1

              if(dim(bg.dat)[1]!=0) {
                names(bg.dat)<-names(dat.in)
                dat.in<-rbind(dat.in,bg.dat)}

              #write output files for R modules
             write.table(dat.in,file=output.file,row.names=FALSE,col.names=FALSE,sep=",",quote=FALSE)


    }


 #Reading in command line arguments
 Args <- commandArgs(T)
    print(Args)
    #assign default values

    responseCol <- "responseBinary"
    trainProp=.7
    RatioPresAbs=NULL
    #replace the defaults with passed values
    for (arg in Args) {
    	argSplit <- strsplit(arg, "=")
    	argSplit[[1]][1]
    	argSplit[[1]][2]
    	if(argSplit[[1]][1]=="p") trainProp <- argSplit[[1]][2]
    	if(argSplit[[1]][1]=="m") RatioPresAbs <- argSplit[[1]][2]
    	if(argSplit[[1]][1]=="o") output.file <- argSplit[[1]][2]
    	if(argSplit[[1]][1]=="i") infil <- argSplit[[1]][2]
    	if(argSplit[[1]][1]=="rc") responseCol <- argSplit[[1]][2]
    }

    RatioResAbs<-as.numeric(RatioPresAbs)
    trainProp<-as.numeric(trainProp)

	#Run the Test training split with these parameters
	CrossValidationSplit(input.file=infil,output.file=output.file,response.col=responseCol,
  trainProp=trainProp,RatioPresAbs=RatioPresAbs)
