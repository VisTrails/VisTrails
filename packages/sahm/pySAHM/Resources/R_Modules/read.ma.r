 read.ma <- function(out){

          ma.name <- out$input$ma.name

      tif.dir <- out$dat$tif.dir$dname
      out.list <- out$dat$ma
      out.list$status[1] <- file.access(ma.name,mode=0)==0

          try(ma<-read.csv(ma.name,skip=2))
          hl<-readLines(ma.name,1)
          hl=strsplit(hl,',')
          colnames(ma) = hl[[1]]

          tif.info<-readLines(ma.name,3)
          tif.info<-strsplit(tif.info,',')
          temp<-tif.info[[2]]
          temp[1:3]<-0
          include<-as.numeric(temp)

          paths<-as.character(tif.info[[3]])

      if(class(ma)=="try-error") stop("Error reading MDS")
          else out.list$status[2]<-T

              temp<-strsplit(tif.info[[2]][1],split="\\\\")[[1]]
            out.list$input$FieldDataTemp<-temp[length(temp)]

                temp<-strsplit(tif.info[[2]][2],split="\\\\")[[1]]
            out.list$input$OrigFieldData<-temp[length(temp)]

               temp<-strsplit(tif.info[[2]][3],split="\\\\")[[1]]
            out.list$input$CovSelectName<-temp[length(temp)]

                temp<-strsplit(tif.info[[3]][1],split="\\\\")[[1]]
            out.list$input$ParcTemplate<-temp[length(temp)]

            temp<-strsplit(tif.info[[3]][2],split="\\\\")[[1]]
            out.list$input$ParcOutputFolder<-temp[length(temp)]

            temp<-strsplit(tif.info[[2]][2],split="\\\\")[[1]]
            out.list$input$OrigFieldData<-temp[length(temp)]

          r.name <- out$input$response.col
          if(r.name=="responseCount") out$input$model.family="poisson"

      r.col <- grep(r.name,names(ma))
      if(length(r.col)==0) stop("Response column was not found")
      if(length(r.col)>1) stop("Multiple columns matched the response column")
         rm.list<-r.col

        # remove background points which aren't used here
         if(length(which(ma[,r.col]==-9999,arr.ind=TRUE))>0) ma<-ma[-c(which(ma[,r.col]==-9999,arr.ind=TRUE)),]

       # remove incomplete cases and warn user if this number is more than 10% of the data

      # find and save xy columns#
      xy.cols <- na.omit(c(match("x",tolower(names(ma))),match("y",tolower(names(ma)))))
      if(length(xy.cols)>0)  rm.list<-c(rm.list,xy.cols)

       # remove weights column except for Random Forest
       site.weights<-match("site.weights",tolower(names(ma)))
        if(!is.na(site.weights)) rm.list<-c(rm.list,site.weights)
        
        # and index as well
       split.indx<-match("split",tolower(names(ma)))
        if(length(na.omit(split.indx))>0) rm.list<-c(rm.list,split.indx)

       #complete the list of columns to include
          include[is.na(include)]<-0
          rm.list<-c(rm.list,(which(include!=1,arr.ind=TRUE)))
          rm.list<-unique(rm.list[!is.na(rm.list)])
          
      ######################### REMOVING INCOMPLETE CASES ###############
        #remove incomplete cases but only for include variables
       all.cases<-nrow(ma)
          out.list$n.pres[1] <- NA
          out.list$n.abs[1] <- NA
          ma<-ma[complete.cases(ma[,-c(rm.list)]),]
          comp.cases<-nrow(ma)
          if(comp.cases/all.cases<.9) warning(paste(round((1-comp.cases/all.cases)*100,digits=2),"% of cases were removed because of missing values",sep=""))
      #########################################################################
        #split out the weights,response, and xy.columns after removing incomplete cases
       if(!is.na(site.weights)){
          out.list$train.weights<-ma[,site.weights]
          } else out.list$train.weights<-rep(1,times=dim(ma)[1])
        if(length(xy.cols)>0) out.list$train.xy<-ma[,xy.cols]
        response<-ma[,r.col]
        
      ma.names<-names(ma)
      # tagging factors and looking at their levels
         factor.cols <- grep("categorical",names(ma))
      factor.cols <- factor.cols[!is.na(factor.cols)]
      if(length(factor.cols)==0){
          out.list$factor.levels <- NA
          } else {
                names(ma) <- ma.names <-  sub("_categorical","",ma.names)
                factor.names <- ma.names[factor.cols]
                factor.levels <- list()
                for (i in 1:length(factor.cols)){
                 f.col <- factor.cols[i]

                        x <- table(ma[,f.col])
                        if(nrow(x)<2){
                              out$dat$bad.factor.cols <- c(out$dat$bad.factor.cols,factor.names[i])
                              }
                        lc.levs <-  as.numeric(row.names(x))[x>0] # make sure there is at least one "available" observation at each level
                        lc.levs <- data.frame(number=lc.levs,class=lc.levs)
                        factor.levels[[i]] <- lc.levs

                    ma[,f.col] <- factor(ma[,f.col],levels=lc.levs$number,labels=lc.levs$class)
                    }

                    names(factor.levels)<-factor.names
                    out.list$factor.levels <- factor.levels

                if(!is.null(out$dat$bad.factor.cols)) rm.list<-c(rm.list,match(out$dat$bad.factor.cols,names(ma)))
          }

            if(length(which(lapply(apply(ma,2,unique),length)==1,arr.ind=TRUE))>0){
                rm.list<-c(rm.list,which(lapply(apply(ma,2,unique),length)==1,arr.ind=TRUE))
                warning(paste("The Following Predictors will be removed because they have only 1 unique value: ",
                names(which(lapply(apply(ma,2,unique),length)==1,arr.ind=TRUE))))
                }
     #remove test training split column if present

          if(length(na.omit(split.indx))>0){
              split.col<-ma[,split.indx]
              out.list$ma.test<-ma[split.col=="test",]
              ma<-ma[split.col=="train",]
              out.list$test.weights<-out.list$train.weights[split.col=="test"]
              out.list$train.weights<-out.list$train.weights[split.col=="train"]
              out.list$test.xy<-out.list$train.xy[split.col=="test",]
              out.list$train.xy<-out.list$train.xy[split.col=="train",]
              out.list$n.pres[4] <- sum(out.list$ma.test[,r.col]!=0)
              out.list$n.abs[4] <- sum(out.list$ma.test[,r.col]==0)
            }

         # Complete cases n.pres and n.abs must be calculated after splitting data (this is train cases reported)
          out.list$n.pres[2] <- sum(ma[,r.col]!=0)
          out.list$n.abs[2] <- sum(ma[,r.col]==0)
          
      # check that response column contains only 1's and 0's, but not all 1's or all 0's if GLMFamily==binomial
      if(out$input$model.source.file=="rf.r") out$input$model.family="bernoulli"
      
      if(tolower(out$input$model.family)=="bernoulli" || tolower(out$input$model.family)=="binomial"){
          if(any(ma[,r.col]!=1 & ma[,r.col]!=0) | sum(ma[,r.col]==1)==nrow(ma) | sum(ma[,r.col]==0)==nrow(ma))
          stop("response column (#",r.col,") in ",ma.name," is not binary 0/1",sep="")
          }

  #check that response column contains at least two unique values for counts

      if(tolower(out$input$model.family)=="poisson"){
          if(length(table(unique(ma[,r.col])))==1)
          stop("response column (#",r.col,") in ",ma.name," does not have at least two unique values",sep="")
          }

          #ma has the first column equal to the response and removes all other remove columns
         ma <- cbind(ma[,r.col],ma[,-c(rm.list)]) #ma still needs the response column
         if(length(na.omit(split.indx))>0) out.list$ma.test <- cbind(out.list$ma.test[,r.col],out.list$ma.test[,-c(rm.list)])
                    paths<-paths[-c(rm.list)]
                    include<-include[-c(rm.list)]
                    
           out.list$resp.name <- names(ma)[1]<-"response"
           if(length(na.omit(split.indx))>0) names(out.list$ma.test)[1]<-"response"
         ma.names<-names(ma)

      # if producing geotiff output, check to make sure geotiffs are available for each column of the model array #
        if(out$input$make.binary.tif==T | out$input$make.p.tif==T){
                #Check that tiffs to be used exist
         if(sum(file.access(paths),mode=0)!=0){
                         temp<-as.vector(file.access(paths))==-1
                         temp.paths<-paths[temp]
                  stop("the following geotiff(s) are missing:",
                      "\nif these are intentionally left blank, uncheck makeBinMap and makeProbabilityMap options\n",
                        paste(paths[temp],collapse="\n"),sep="")
                          }

                 } else out$dat$tif.names <- ma.names[-1]

                 out$dat$tif.ind<-paths

          out.list$ma <- ma

        out.list$dims <- dim(out.list$ma)
        out.list$ratio <- min(sum(out$input$model.fitting.subset)/out.list$dims[1],1)
        out.list$used.covs <- names(out.list$ma)[-1]

      if(!is.null(out$input$model.fitting.subset)){
            pres.sample <- sample(c(1:nrow(out.list$ma))[out.list$ma[,1]>=1],min(out.list$n.pres[2],out$input$model.fitting.subset[1]))
            abs.sample <- sample(c(1:nrow(out.list$ma))[out.list$ma[,1]==0],min(out.list$n.abs[2],out$input$model.fitting.subset[2]))
            out.list$ma.subset <- out.list$ma[c(pres.sample,abs.sample),]
            if(out$input$model.source.file!="rf.r") out.list$weight.subset<-out.list$train.weights[c(pres.sample,abs.sample)]
            out.list$n.pres[3] <- length(pres.sample)
            out.list$n.abs[3] <- length(abs.sample)
            } else {
            out.list$ma.subset <- NULL
            out.list$weight.subset<-NULL
            out.list$n.pres[3] <- NA
            out.list$n.abs[3] <- NA }

if(tolower(out$input$model.family)=="poisson"){
out.list$ma.subset<-out.list$ma
out.list$weight.subset<-out.list$train.weights
}

          out$dat$ma <- out.list

      return(out)
      }