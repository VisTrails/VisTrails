dat<-read.csv("C:\\VisTrails\\DICK_MDS_binary.csv")

rf.full <- randomForest(x=dat[,-1],y=factor(dat[,1]),importance=TRUE,
        ntree=1000, replace=FALSE)

pred<-predict(rf.full, newdata=dat[,-1],type="prob")[,2]

null.dev<-calc.deviance(dat[,1], rep(p.bar,times=length(dat[,1])),family="binomial")*nrow(dat)
    dev.fit<-calc.deviance(dat[,1], pred, family="binomial")*nrow(dat)
    dev.exp <- null.dev - dev.fit
    pct.dev.exp <- dev.exp/null.dev*100
    
r<-randomForest(x=dat[,-1],y=factor(out$dat$ma$ma[,1]),xtest=xtest,ytest=ytest,importance=TRUE, ntree=n.trees,
        mtry=mtry,replace=samp.replace,sampsize=ifelse(is.null(sampsize),(ifelse(samp.replace,nrow(x),ceiling(.632*nrow(x)))),sampsize),
        nodesize=ifelse(is.null(nodesize),(if (!is.null(y) && !is.factor(y)) 5 else 1),nodesize),maxnodes=maxnodes,
        localImp=localImp, nPerm=nPerm, keep.forest=ifelse(is.null(keep.forest),!is.null(y) && is.null(xtest),keep.forest),
        corr.bias=corr.bias, keep.inbag=keep.inbag)