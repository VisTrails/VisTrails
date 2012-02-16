library(raster)
slopedeg<-raster("C:\\VisTrails\\mtalbert_20110504T132851\\PARC_1\\slopedeg.tif")
bio_4<-raster("C:\\VisTrails\\mtalbert_20110504T132851\\PARC_1\\bio_4_wgs84.tif")
bio_12<-raster("C:\\VisTrails\\mtalbert_20110504T132851\\PARC_1\\bio_12_wgs84.tif")
bio_7<-raster("C:\\VisTrails\\mtalbert_20110504T132851\\PARC_1\\bio_7_wgs84.tif")

#putting bio_4 on a 0 to 1 range
temp<-as.matrix(log(bio_4))
b4<-(log(bio_4)-min(temp))/max(temp-min(temp))

#putting bio_7 on a 0 to 1 range
temp<-as.matrix(2^bio_7)
b7<-(2^bio_7-min(temp))/max(temp-min(temp))

#putting slopedeg on a 0 to 1 range
temp<-as.matrix(slopedeg)
sld<-(slopedeg-min(temp))/max(temp-min(temp))

#making bio_12 discrete
temp<-as.matrix(bio_12)
qan<-quantile(temp,probs=c(.25,.5,.75))
b12<-.25+.25*(bio_12>=qan[1])+.25*(bio_12>qan[2])+.25*(bio_12>qan[3])
writeRaster(b12, filename="C:\\VisTrails\\mtalbert_20110504T132851\\PARC_1\\Cat12_wgs84.tif")


#for binomal data
myFct<-.5*b4*b7+.25*sld+.25*b12+.18
m<-as.matrix(myFct)
xcoord<-sample(dim(m)[1],size=200)
ycoord<-sample(dim(m)[2],size=200)
cells<-cbind(xcoord,ycoord)
cellNumbs<-cellFromRowCol(myFct,xcoord,ycoord)

writeRaster(myFct, filename="C:\\VisTrails\\mtalbert_20110504T132851\\PARC_1\\BinomialSurface.tif")

value<-extract(myFct,cellNumbs)
responseBinary<-rbinom(length(value),1,value)
xy = xyFromCell(myFct, cellNumbs)

Binom.out<-as.data.frame(cbind(xy,responseBinary))
write.table(Binom.out,file="C:\\VisTrails\\mtalbert_20110504T132851\\FieldDatBinom.csv",row.names=FALSE,col.names=TRUE,sep=",",quote=FALSE)

#now for Poisson data generate a lambda surface we want a lot of zeros

PoisFct<-myFct*4
m<-as.matrix(PoisFct)
xcoord<-sample(dim(m)[1],size=200)
ycoord<-sample(dim(m)[2],size=200)
cells<-cbind(xcoord,ycoord)
cellNumbs<-cellFromRowCol(PoisFct,xcoord,ycoord)

value<-extract(PoisFct,cellNumbs)
responseCount<-rpois(length(value),value)
xy = xyFromCell(myFct, cellNumbs)

par(mfrow=c(2,2))
plot(as.vector(as.matrix(b4)),as.vector(as.matrix(PoisFct)))
plot(as.vector(as.matrix(b7)),as.vector(as.matrix(PoisFct)))
plot(as.vector(as.matrix(sld)),as.vector(as.matrix(PoisFct)))
plot(as.vector(as.matrix(b12)),as.vector(as.matrix(PoisFct)))

writeRaster(PoisFct, filename="C:\\VisTrails\\mtalbert_20110504T132851\\PARC_1\\PoissonSurface.tif")

Pois.out<-as.data.frame(cbind(xy,responseCount))
write.table(Pois.out,file="C:\\VisTrails\\mtalbert_20110504T132851\\FieldDatPois.csv",row.names=FALSE,col.names=TRUE,sep=",",quote=FALSE)

BRT.Out<-raster("C:\\VisTrails\\prob_map.tif")
BRT.Bin<-raster("C:\\VisTrails\\prob_map.tif")
resids<-BRT.Out-PoisFct

par(mfrow=c(2,2))
plot(resids)
plot(PoisFct)
plot(BRT.Out)

par(mfrow=c(2,1))
hist(as.matrix(PoisFct),breaks=40)
hist(as.matrix(BRT.Out),breaks=40)