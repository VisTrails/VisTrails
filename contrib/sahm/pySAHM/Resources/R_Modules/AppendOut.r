AppendOut<-function(compile.out,Header,x,out,test.split,parent){
    Header.Length<-nrow(Header)
    Parm.Len<-nrow(x)
  if(file.access(compile.out,mode=0)==-1){ #if very first time through little to do
          #A more complex than necessary way of writing a csv with several header lines
          write.table(Header,file =compile.out,row.names=FALSE,col.names=FALSE,quote=FALSE,sep=",")
          if(!is.null(out$dat$ma$ma.test))
              write.table(cbind("","Train Split"),file=compile.out,row.names=FALSE,col.names=FALSE,quote=FALSE,append=TRUE,sep=",")
          write.table(x,file=compile.out,row.names=FALSE,col.names=FALSE,quote=FALSE,append=TRUE,sep=",")
  } else { #this else (not the first time through) goes to the very end of the function
          input<-read.table(compile.out,fill=TRUE,sep=",")
          Orig.Header<-input[1:Header.Length,]

          if(!is.null(out$dat$ma$ma.test)){ #if there is a test train split this if lasts until after plotting
                  Train.x<-input[(Header.Length+2):(Header.Length+Parm.Len+1),]
                  Orig.Train<-input[(Header.Length+1),]

                  if(nrow(input)>15){ #if there is a test split in input (not in very first loop)
                     Test.x<-input[(Header.Length+Parm.Len+4):nrow(input),]
                     Orig.Test<-input[(Header.Length+Parm.Len+2):(Header.Length+Parm.Len+3),]
                      if(test.split){ # if we're hitting this on a test and not a train
                            Test.x[,ncol(Test.x)]<-x[,2]
                             class(Orig.Test[,ncol(Orig.Test)])="character"
                            Orig.Test[1,ncol(Orig.Test)]<-""
                            Orig.Test[2,ncol(Orig.Test)]<-"Test Split"
                      } else{
                            Orig.Header<-cbind(Orig.Header,Header[,2])
                            Train.x<-cbind(Train.x,x[,2])
                            Orig.Train<-cbind(Orig.Train,"Train Split")
                            }
                  } else{
                     Orig.Test=rbind(c("",""),cbind("","Test Split"))
                     Test.x=x
                  }

                  temp<-try(write.table(Orig.Header,file =compile.out,row.names=FALSE,col.names=FALSE,quote=FALSE,sep=","),silent=TRUE)

                  while(class(temp)=="try-error"){
                      modalDialog("","Please Close the AppendedOutput.exe\ so that R can write to it then press ok to continue ","")
                      temp<-try(write.table(Orig.Header,file =compile.out,row.names=FALSE,col.names=FALSE,quote=FALSE,sep=","),silent=TRUE)
                  }
                  try(write.table(Orig.Train,file =compile.out,row.names=FALSE,col.names=FALSE,quote=FALSE,append=TRUE,sep=","))
                  try(write.table(Train.x,file =compile.out,row.names=FALSE,col.names=FALSE,quote=FALSE,append=TRUE,sep=","))
                  try(write.table(Orig.Test,file =compile.out,row.names=FALSE,col.names=FALSE,quote=FALSE,append=TRUE,sep=","))
                  try(write.table(Test.x,file =compile.out,row.names=FALSE,col.names=FALSE,quote=FALSE,append=TRUE,sep=","))
                  if(ncol(Train.x)==ncol(Test.x) & ncol(Test.x)>2){

                  jpeg(file=paste(parent,"AcrossModelPerformTestTrain.jpg",sep="//"),width=1000,height=1000,pointsize=13)
                          par(mfrow=c(nrow(Train.x),1),mar=c(.2, 5, .6, 2),cex=1.1,oma=c(5, 0, 3, 0))
                            temp<-Train.x[,2:ncol(Train.x)]
                          temp<-matrix(data=as.numeric(as.matrix(temp,nrow=Par.Len)),nrow=Parm.Len,ncol=(ncol(Train.x)-1))
                          temp1<-temp
                          temp[2,]<-temp[2,]/100
                          temp[3,]<-temp[3,]/100
                          temp2<-Test.x[,2:ncol(Test.x)]
                          temp2<-matrix(data=as.numeric(as.matrix(temp2,nrow=Par.Len)),nrow=Parm.Len,ncol=(ncol(Test.x)-1))
                          temp2[2,]<-temp2[2,]/100
                          temp2[3,]<-temp2[3,]/100
                           ss<-seq(from=1,to=(ncol(Train.x)-1),by=1)
                           x.labs<-sub(" ","\n",Train.x[,1])
                           x.labs<-sub("Percent","Proportion",x.labs)
                          colors.test=c("chocolate3","gold1","darkolivegreen2","steelblue1","brown3")
                        colors.train=c("chocolate4","gold3","darkolivegreen4","steelblue4","brown4")
                   #Plot 1.
                        plot(c(0,(ncol(Test.x)+2)),c(0,1.1),type="n",xaxt="n",
                            xlab=paste("Corresponding Column in ",ifelse(!is.null(out$dat$ma$ma.test),"AppendedOutputTestTrain.csv","AppendedOutput.csv"),sep=""),
                            ylab=x.labs[1])
                            grid(nx=10)
                            legend(ncol(Test.x),y=.75,legend=c("Test","Train"),fill=c(colors.test[1],colors.train[1]))
                          rect(xleft=ss-.4,ybottom=0,xright=ss,ytop=temp[1,],col=colors.train[1],lwd=2)
                          rect(xleft=ss,ybottom=0,xright=(ss+.4),ytop=pmax(0,temp2[1,]),col=colors.test[1],lwd=2)
                          text((which(temp1[1,]==max(temp1[1,],na.rm=TRUE),arr.ind=TRUE)-.25),
                              max(temp1[1,],na.rm=TRUE)+.05,labels=as.character(round(max(temp1[1,]),digits=2)),cex=.8)
                          text((which(temp2[1,]==max(temp2[1,],na.rm=TRUE),arr.ind=TRUE)+.25),
                              max(temp2[1,],na.rm=TRUE)+.05,labels=as.character(round(max(temp2[1,]),digits=2)),cex=.8)
                        par(mar=c(.2, 5, .6, 2))
                 #Middle Plots.
                        for(i in 2:(nrow(Train.x)-1)){
                            plot(c(0,(ncol(Test.x)+2)),c(0,1.1),type="n",xaxt="n",
                            ylab=x.labs[i])
                            grid(nx=10)
                          rect(xleft=ss-.4,ybottom=0,xright=ss,ytop=temp[i,],col=colors.train[i],lwd=2)
                          rect(xleft=ss,ybottom=0,xright=(ss+.4),ytop=pmax(0,temp2[i,]),col=colors.test[i],lwd=2)
                          legend(ncol(Test.x),y=.75,legend=c("Test","Train"),fill=c(colors.test[i],colors.train[i]))
                          text((which(temp[i,]==max(temp[i,],na.rm=TRUE),arr.ind=TRUE)-.25),
                              max(temp[i,],na.rm=TRUE)+.05,labels=as.character(round(max(temp[i,]),digits=2)),cex=.8)
                          text((which(temp2[i,]==max(temp2[i,],na.rm=TRUE),arr.ind=TRUE)+.25),
                              max(temp2[i,],na.rm=TRUE)+.05,labels=as.character(round(max(temp2[i,]),digits=2)),cex=.8)
                          par(mar=c(.3, 5, .4, 2))
                          }
                          par(mar=c(2, 5, .4, 2))
                #Last Plot.
                       i=nrow(Train.x)
                      plot(c(0,(ncol(Test.x)+2)),c(0,1.1),type="n",xaxt="n",
                            xlab="n",
                            ylab=x.labs[i])
                            grid(nx=10)
                          rect(xleft=ss-.4,ybottom=0,xright=ss,ytop=temp[i,],col=colors.train[i],lwd=2)
                          rect(xleft=ss,ybottom=0,xright=(ss+.4),ytop=pmax(0,temp2[i,]),col=colors.test[i],lwd=2)
                          legend(ncol(Test.x),y=.75,legend=c("Test","Train"),fill=c(colors.test[i],colors.train[i]))
                          text((which(temp1[i,]==max(temp1[i,],na.rm=TRUE),arr.ind=TRUE)-.25),
                              max(temp1[i,],na.rm=TRUE)+.05,labels=as.character(round(max(temp1[i,]),digits=2)),cex=.8)
                          text((which(temp2[i,]==max(temp2[i,],na.rm=TRUE),arr.ind=TRUE)+.25),
                              max(temp2[i,],na.rm=TRUE)+.05,labels=as.character(round(max(temp2[i,]),digits=2)),cex=.8)
             #Outer margin labels
                            for(i in 2:ncol(Orig.Header)) mtext(Orig.Header[1,i],line=-12,at=(i-1),las=2)
                          mtext("Evaluation Metrics Performance Across Model Runs",outer=TRUE,side=3,cex=1.3)
                          mtext(paste("Folder Name where model is found in ",
                            ifelse(!is.null(out$dat$ma$ma.test),"AppendedOutputTestTrain.csv","AppendedOutput.csv"),sep=""),side=1,outer=TRUE,line=3)
                       dev.off()
                    }
              }  else{

          Orig.x<-input[(Header.Length+1):nrow(input),]
          temp<-try(write.table(cbind(Orig.Header,Header[,2]),file =compile.out,row.names=FALSE,col.names=FALSE,quote=FALSE,sep=","),silent=TRUE)
           while(class(temp)=="try-error"){
                      modalDialog("","Please Close the AppendedOutput.exe\ so that R can write to it then press ok to continue ","")
                      temp<-try(write.table(cbind(Orig.Header,Header[,2]),file =compile.out,row.names=FALSE,col.names=FALSE,quote=FALSE,sep=","),silent=TRUE)
                  }
           if(ncol(Orig.x)>2){

        jpeg(file=paste(parent,"AcrossModelPerform.jpg",sep="//"),width=1000,height=1000,pointsize=13)
                          par(mfrow=c(5,1),mar=c(.2, 5, .6, 2),cex=1.1,oma=c(5, 0, 3, 0))
                            temp<-Orig.x[,2:ncol(Orig.x)]
                          temp<-matrix(data=as.numeric(as.matrix(temp,nrow=Par.Len)),nrow=Parm.Len,ncol=(ncol(Orig.x)-1))
                          temp1<-temp
                          temp[2,]<-temp[2,]/100
                          temp[3,]<-temp[3,]/100
                           ss<-seq(from=1,to=(ncol(Orig.x)-1),by=1)
                           x.labs<-sub(" ","\n",Orig.x[,1])
                           x.labs<-sub("Percent","Proportion",x.labs)
                        colors.train=c("chocolate4","gold3","darkolivegreen4","steelblue4","brown4")
                   #Plot 1.
                        plot(c(0,(ncol(Orig.x))),c(0,1.1),type="n",xaxt="n",ylab=x.labs[1])
                            grid(nx=10)
                          rect(xleft=ss-.3,ybottom=0,xright=ss+.3,ytop=temp[1,],col=colors.train[1],lwd=2)
                          text((which(temp1[1,]==max(temp1[1,],na.rm=TRUE),arr.ind=TRUE)),
                              max(temp1[1,],na.rm=TRUE)+.06,labels=as.character(round(max(temp1[1,]),digits=2)),cex=.8)
                        par(mar=c(.2, 5, .6, 2))
                 #Plot 2-4.
                        for(i in 2:(nrow(x)-1)){
                            plot(c(0,(ncol(Orig.x))),c(0,1.1),type="n",xaxt="n",
                            ylab=x.labs[i])
                            grid(nx=10)
                          rect(xleft=ss-.3,ybottom=0,xright=ss+.3,ytop=temp[i,],col=colors.train[i],lwd=2)
                          text((which(temp[i,]==max(temp[i,],na.rm=TRUE),arr.ind=TRUE)),
                              max(temp[i,],na.rm=TRUE)+.06,labels=as.character(round(max(temp[i,]),digits=2)),cex=.8)
                          par(mar=c(.3, 5, .4, 2))
                          }
                          par(mar=c(2, 5, .4, 2))
                #Plot 5.
                       i=nrow(x)
                       plot(c(0,(ncol(Orig.x))),c(0,1.1),type="n",xaxt="n",
                            ylab=x.labs[i])
                            grid(nx=10)
                          rect(xleft=ss-.3,ybottom=0,xright=ss+.3,ytop=temp[i,],col=colors.train[i],lwd=2)
                          text((which(temp[i,]==max(temp[i,],na.rm=TRUE),arr.ind=TRUE)),
                              max(temp[i,],na.rm=TRUE)+.06,labels=as.character(round(max(temp[i,]),digits=2)),cex=.8)
             #Outer margin labels
                            for(i in 2:ncol(Orig.Header)) mtext(Orig.Header[1,i],line=-12,at=(i-1),las=2)
                          mtext("Evaluation Metrics Performance Across Model Runs",outer=TRUE,side=3,cex=1.3)
                          mtext(paste("Folder Name where model is found in ",
                            ifelse(!is.null(out$dat$ma$ma.test),"AppendedOutputTestTrain.csv","AppendedOutput.csv"),sep=""),side=1,outer=TRUE,line=3)
                       dev.off()
                     }

          try(write.table(cbind(Orig.x,x[,2]),file =compile.out,row.names=FALSE,col.names=FALSE,quote=FALSE,append=TRUE,sep=","))
          }}
               }
               