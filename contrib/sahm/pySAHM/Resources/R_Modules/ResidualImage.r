resid.image<-function(dev.contrib,pred,raw.dat,x,y,model.type,file.name,out){
   z<-sign(pred-raw.dat)*dev.contrib
              a<-loess(z~x*y)
               x.lim<-rep(seq(from=min(out$dat$ma$train.xy[,1]),to=max(out$dat$ma$train.xy[,1]),length=100),each=100)
               y.lim<-rep(seq(from=min(out$dat$ma$train.xy[,2]),to=max(out$dat$ma$train.xy[,2]),length=100),times=100)
              z<-predict(a,newdata=cbind("x"=x.lim,"y"=y.lim))
              x.lim<-seq(from=min(out$dat$ma$train.xy[,1]),to=max(out$dat$ma$train.xy[,1]),length=100)
              y.lim<-seq(from=min(out$dat$ma$train.xy[,2]),to=max(out$dat$ma$train.xy[,2]),length=100)
                 z<-matrix(data=z,ncol=100,nrow=100,byrow=TRUE)
                # browser()
                 ########################################### experiment
                # if(out$input$make.binary.tif==TRUE | out$input$make.p.tif==TRUE){
                # out$dat$tif.ind[1]
                # RasterInfo=raster(out$dat$tif.ind[1])
                #  gi <- GDALinfo(out$dat$tif.ind[1])
                #    dims <- as.vector(gi)[1:2]
                #    ps <- as.vector(gi)[6:7]
                #    ll <- as.vector(gi)[4:5]
                 #   pref<-attr(gi,"projection")


                 # }
                  
                  
                 ##########################################################
              jpeg(file=paste(file.name,"resid.plot.jpg",sep="/"))
                 par(oma=c(3,3,3,3))
                 layout(matrix(data=c(1,2), nrow=1, ncol=2), widths=c(4,1), heights=c(1,1))
                  image(z,x=x.lim,y=y.lim,col=beachcolours(heightrange=c(min(z),max(z)),sealevel=0,ncolours=length(table(z))),
                  main="Spatial pattern of deviance residuals\n(magnitude and sign)",xlab="X coordinate",ylab="Y coordinate")
                  points(x,y,cex=.5)
                  #image(x=c(1,2),y=sort(unique(z)),z=matrix(data=cbind(rep(sort(unique(z)),times=2)),ncol=2),col=beachcolours(heightrange=c(min(z),max(z)),sealevel=0,ncolours=length(table(z))))
                  par(mar = c(3,2.5,2.5,2))
              colrange<-seq(from=min(z),to=max(z),length=100)
               image(1,colrange,
               matrix(data=colrange, ncol=length(colrange),nrow=1),
              col=beachcolours(heightrange=c(min(z),max(z)),sealevel=0,ncolours=length(colrange)),
              xlab="",ylab="",
              xaxt="n")
              graphics.off()
              return(a)
              }
