Pairs.Explore<-function(num.plots=5,min.cor=.7,input.file,output.file,response.col="ResponseBinary",cors.w.highest=FALSE,pres=TRUE,absn=TRUE,bgd=TRUE,Debug=FALSE){


      #num.plots=plots per page of display
      #min.cor=the minimum correlation to be included in determining which set of predictors to display
      #input.file=a csv assumed to have the new vistrails form with the first several rows specifiying where to find tiffs
      #   and which columns to include in analysis
      #output.file=...
      #response.col=name of response column to be removed and used elsewhere
    #modifications
      #5/10/2011 altered to handle count data as well presence absence.
      #any counts higher than or equal to 1 are set to be presence though I might consider
      #adding the option to have a threshold set instead of using just presence/absence


      absn<-as.logical(absn)
      pres<-as.logical(pres)
      bgd<-as.logical(bgd)
      cors.w.highest<-as.logical(cors.w.highest)
      
   #Read input data and remove any columns to be excluded
    dat<-read.csv(input.file,skip=3,header=FALSE)

          hl<-readLines(input.file,1)
          hl=strsplit(hl,',')
          colnames(dat) = hl[[1]]

          tif.info<-readLines(input.file,3)
          tif.info<-strsplit(tif.info,',')
          include<-(as.numeric(tif.info[[2]]))

  #Remove coordinates, response column, site.weights
  #before exploring predictor relationship
    rm.cols <- as.vector(na.omit(c(match("x",tolower(names(dat))),match("y",tolower(names(dat))),
    match("site.weights",tolower(names(dat))),match(tolower(response.col),tolower(names(dat))),match("Split",names(dat)))))

     #remove testing split
    if(!is.na(match("Split",names(dat)))) dat<-dat[-c(which(dat$Split=="test"),arr.ind=TRUE),]

    include[is.na(include)]<-0
    rm.cols<-unique(c(rm.cols,which(include==0,arr.ind=TRUE)))
    response<-dat[,match(tolower(response.col),tolower(names(dat)))]

       dat<-dat[order(response),]
       response<-response[order(response)]

       #for the purpose of the pairs plot, taking all counts greater than 1 and setting them equal to presence
       #this is never exported
      if(response.col=="responseCount") {response[response>=1]<-1
      }
      
    #remove any of pres absn or bgd that aren't desired
     temp<-c(0,1,-9999)
     temp<-temp[c(absn,pres,bgd)]
     dat<-dat[response%in%temp,]
     response<-response[response%in%temp]


     if(sum(response==-9999)>1000){
      s<-sample(which(response==-9999,arr.ind=TRUE),size=(sum(response==-9999)-1000))
      dat<-dat[-c(s),]
      response<-response[-c(s)]
    }

   if (response.col=="responseCount") {
    TrueResponse<-dat[,match(tolower(response.col),tolower(names(dat)))]
    } else TrueResponse<-response

    #now remove all columns except predictors
    dat<-dat[-rm.cols]
     dat[dat==-9999]<-NA
      response<-response[complete.cases(dat)]
      TrueResponse<-TrueResponse[complete.cases(dat)]
     dat<-dat[complete.cases(dat),]


    #dat<-dat[1:2000,]
  #Remove columns with only one unique value
      varr <- function(x) var(x,na.rm=TRUE)
      
    dat<-try(dat[,as.vector(apply(dat,2,varr)==0)!=1],silent=TRUE)
    if(class(dat)=="try-error") stop("mds file contains nonnumeric columns please remove and continue")
  #record correlations for later plots

    cmat<-cor(dat,use="pairwise.complete.obs")
    smat<-cor(dat,method="spearman",use="pairwise.complete.obs")
    if(dim(dat)[1]<2000){
    kmat<-cor(dat,method="kendall",use="pairwise.complete.obs")}
    else {s<-sample(seq(1:dim(dat)[1]),size=2000,replace=FALSE)
     kmat<-cor(dat[s,],method="kendall",use="pairwise.complete.obs")
    }
    
    cmat=pmax(abs(cmat),abs(smat),abs(kmat),na.rm=TRUE)
    
    High.cor<-sort(apply(abs(cmat)>min.cor,2,sum)-1,decreasing=TRUE)

  #take the top num.plots to put in the pairs plot or if the looking at a single
  #predictor and other predictors it's correlated with, take the top num.plots-1
  #of those with which it is correlated
    {if(cors.w.highest==FALSE){
    HighToPlot<-dat[,match(names(High.cor),names(dat))[1:min(num.plots,length(High.cor))]]
      }else{
          #take the column of the correlation matrix corresponding to the
          #predictor with the higest number of total correlations record the names
          #of the predictors that are correlated with this one predictor
          temp<-cmat[rownames(cmat)==names(High.cor[1]),]
          CorWHigh<-temp[abs(cmat[,colnames(cmat)==names(High.cor[1])])>min.cor]

          #record counts of total number of correlations with all predictors for those
          #predictors that are highly correlated with the Highest predictor
          High.cor<-sort(High.cor[names(CorWHigh)],decreasing=TRUE)
          HighToPlot<-dat[,match(names(High.cor),names(dat))[1:min(num.plots,length(High.cor))]]
          }}
              cor.hightoplot<-abs(cor(HighToPlot,use="pairwise.complete.obs"))
              diag(cor.hightoplot)<-0
    cor.range<-c(quantile(as.vector(cor.hightoplot),probs=c(0,.5,.7,.85)),1)

  ## put histograms on the diagonal
    panel.hist <- function(x, ...)
    {
        usr <- par("usr"); on.exit(par(usr))
        par(usr = c(usr[1:2], 0, 1.5) )
        h <- hist(x, plot = FALSE)
        breaks <- h$breaks; nB <- length(breaks)
        y <- h$counts; y <- y/max(y)
        rect(breaks[-nB], 0, breaks[-1], y, col="steelblue", ...)

    }


  ## put (absolute) correlations on the upper panels,
  ## with size proportional to the correlations.
      panel.cor <- function(x, y, digits=2, prefix="", cor.range,cex.cor, ...)
      {
      a<-colors()
          usr <- par("usr"); on.exit(par(usr))
          par(usr = c(0, 1, 0, 1))
          r <- abs(cor(x, y,use="pairwise.complete.obs"))
          spear<-abs(cor(x,y,method="spearman",use="pairwise.complete.obs"))
          ken<- abs(cor(x,y,method="kendall",use="pairwise.complete.obs"))
          all.cor<-max(r,spear,ken)
          #range.seq<-seq(from=cor.range[1],to=cor.range[2],length=20)
          if(all.cor>=cor.range[4]){
            rect(par("usr")[1], par("usr")[3], par("usr")[2], par("usr")[4], col =
            a[59])} else if(all.cor>=cor.range[3]){
            rect(par("usr")[1], par("usr")[3], par("usr")[2], par("usr")[4], col =
            a[76])} else if(all.cor>=cor.range[2]){
            rect(par("usr")[1], par("usr")[3], par("usr")[2], par("usr")[4], col =
            a[382])}
          r<-max(all.cor)
               cex.cor=3
         txt <- format(c(r, 0.123456789), digits=digits)[1]
          txt <- paste(prefix, txt, sep="")
           #if(missing(cex.cor)) cex.cor <- 1.2/strwidth(txt)
         
              txt2=""
            if(max(all.cor)>cor.range[2]){
            if(spear==max(all.cor) && spear!=cor(x,y,use="pairwise.complete.obs")) {txt2 <- " s"
              } else if(ken==max(all.cor) && ken!=cor(x,y,use="pairwise.complete.obs")){
              txt2 <-" k"
              }

         }
          text(0.5, 0.5, txt, cex = .7+cex.cor * (r-min(cor.range))/(max(cor.range)-min(cor.range)))
          text(.9,.1,txt2,cex=1.5)   
         }
         
#   #Find a new unique file name (one in the desired directory that hasn't yet been used)
#   outfile <- paste(output.dir,"Predictor_Correlation.pdf",sep="\\")
#             while(file.access(outfile)==0) outfile<-paste(output.dir,"Predictor_Correlation.pdf",sep="\\")
# 
#  options(warn=-1)
#   pdf(outfile,width=11,height=9,onefile=T)
#     MyPairs(HighToPlot,cor.range=cor.range,my.labels=(as.vector(High.cor)[1:num.plots]),
#     lower.panel=panel.smooth,diag.panel=panel.hist, upper.panel=panel.cor,pch=21,bg = c("red","steelblue")[as.factor(response)],col.smooth = "red")
#   graphics.off()
#  options(warn=0)
#  
#   }

  
  #Find a new unique file name (one in the desired directory that hasn't yet been used)

 options(warn=-1)
 if(Debug==FALSE) jpeg(output.file,width=1000,height=1000,pointsize=13)
    MyPairs(cbind(TrueResponse,HighToPlot),cor.range=cor.range,my.labels=(as.vector(High.cor)[1:num.plots]),
    lower.panel=panel.smooth,diag.panel=panel.hist, upper.panel=panel.cor,pch=21,bg = c("green","red","yellow")[factor(response,levels=c(0,1,-9999))],col.smooth = "red")

 if(Debug==FALSE) graphics.off()
 options(warn=0)
 
  }

MyPairs<-function (x,my.labels,labels, panel = points, ..., lower.panel = panel,
    upper.panel = panel, diag.panel = NULL, text.panel = textPanel,
    label.pos = 0.5 + has.diag/3, cex.labels = NULL, font.labels = 1,
    row1attop = TRUE, gap = 1,Toplabs=NULL)
{
    response<-x[,1]
    response[response==-9999]<-0
    x<-x[,2:dim(x)[2]]

    textPanel <- function(x = 0.5, y = 0.5, txt, cex, font) text(x,
        y, txt, cex = cex, font = font)
    localAxis <- function(side, x, y, xpd, bg, col = NULL, main,
        oma, ...) {
        if (side%%2 == 1)
            Axis(x, side = side, xpd = NA, ...)
        else Axis(y, side = side, xpd = NA, ...)
    }
    localPlot <- function(..., main, oma, font.main, cex.main) plot(...)
    localLowerPanel <- function(..., main, oma, font.main, cex.main) lower.panel(...)
    localUpperPanel <- function(..., main, oma, font.main, cex.main) upper.panel(...)
    localDiagPanel <- function(..., main, oma, font.main, cex.main) diag.panel(...)
    dots <- list(...)
    nmdots <- names(dots)
    if (!is.matrix(x)) {
        x <- as.data.frame(x)
        for (i in seq_along(names(x))) {
            if (is.factor(x[[i]]) || is.logical(x[[i]]))
                x[[i]] <- as.numeric(x[[i]])
            if (!is.numeric(unclass(x[[i]])))
                stop("non-numeric argument to 'pairs'")
        }
    } else if (!is.numeric(x))
        stop("non-numeric argument to 'pairs'")
    panel <- match.fun(panel)
    if ((has.lower <- !is.null(lower.panel)) && !missing(lower.panel))
        lower.panel <- match.fun(lower.panel)
    if ((has.upper <- !is.null(upper.panel)) && !missing(upper.panel))
        upper.panel <- match.fun(upper.panel)
    if ((has.diag <- !is.null(diag.panel)) && !missing(diag.panel))
        diag.panel <- match.fun(diag.panel)
    if (row1attop) {
        tmp <- lower.panel
        lower.panel <- upper.panel
        upper.panel <- tmp
        tmp <- has.lower
        has.lower <- has.upper
        has.upper <- tmp
    }
    nc <- ncol(x)
    if (nc < 2)
        stop("only one column in the argument to 'pairs'")
    has.labs <- TRUE
    if (missing(labels)) {
        labels <- colnames(x)
        if (is.null(labels))
            labels <- paste("var", 1L:nc)
    }
    else if (is.null(labels))
        has.labs <- FALSE
    oma <- if ("oma" %in% nmdots)
        dots$oma
    else NULL
    main <- if ("main" %in% nmdots)
        dots$main
    else NULL
    if (is.null(oma)) {
        oma <- c(4, 4, 4, 4)
        if (!is.null(main))
            oma[3L] <- 6
    }

    nCol<-ifelse(length(unique(response))>1,nc+1,nc)
    j.start<-ifelse(length(unique(response))>1,0,1)
    opar <- par(mfrow = c(nc, nCol), mar = rep.int(gap/2, 4), oma = oma)
    on.exit(par(opar))
    for (i in if (row1attop)
        1L:(nc)
    else nc:1L) for (j in j.start:(nc)) {


        if(i==1){ par(mar = c(gap/2,gap/2,gap,gap/2)) #top row add extra room at top
          if(j==0){
                par(mar = c(gap/2,gap,gap,gap)) #top left corner room at top and on right
          localPlot(x[, i],response, xlab = "", ylab = "", axes = FALSE,
                type="n",...)
                }else if(j==1) {par(mar = c(gap/2,gap,gap,gap/2)) #extra room on left and topfor second plot top row
                    localPlot(x[, j], x[, i], xlab = "", ylab = "", axes = FALSE,
           type="n",...)} else  {
           par(mar = c(gap/2,gap/2,gap,gap/2)) #all other top row plots need extra room at top only
           localPlot(x[, j], x[, i], xlab = "", ylab = "", axes = FALSE,
           type="n",...)
           }}else { par(mar = rep.int(gap/2, 4))
               if(j==0){ par(mar = c(gap/2,gap,gap/2,gap))  #left column needs extra room on right only
               localPlot(x[, i],response, xlab = "", ylab = "", axes = FALSE,
                type="n",...)
                }else if(j==1){ par(mar = c(gap/2,gap,gap/2,gap/2)) #second column needs extra room on left so labels fit
                localPlot(x[, j], x[, i], xlab = "", ylab = "", axes = FALSE,
           type="n",...)
        }else localPlot(x[, j], x[, i], xlab = "", ylab = "", axes = FALSE,
           type="n",...)}
         if(j==0) {
             if(i==1) par(mar=c(gap/2,gap,gap,gap))
                else par(mar = c(gap/2,gap,gap/2,gap))

                  if(i==1) title(main="Response",line=.04,cex.main=1.5)

                  box()
                     my.lab<-paste("cor=",round(max(abs(cor(x[,(i)],response,use="pairwise.complete.obs")),abs(cor(x[,(i)],response,method="spearman",use="pairwise.complete.obs")),
                     abs(cor(x[,(i)],response,method="kendall",use="pairwise.complete.obs"))),digits=2),sep="")

                  #panel smooth doesn't work for two reasons: one, the response is binary and it requires more than two unique values
                  #second I don't think it can use weights which is necessary with an overwhelming amount of background points so that presnce points
                  #can't be viewed
                  #panel.smooth(as.vector(x[, (i)]), as.vector(jitter(response,factor=.1)),weights=
                  #        c(rep(table(response)[2]/table(response)[1],times=table(response)[1]),rep(1,times=table(response)[2])),...)

                   if(length(unique(response))>2) panel.smooth(as.vector(x[, (i)]), as.vector(response),...)
                   else my.panel.smooth(as.vector(x[, (i)]), as.vector(response),weights=
                          c(rep(table(response)[2]/table(response)[1],times=table(response)[1]),rep(1,times=table(response)[2])),...)
                          
                          title(ylab=paste("cor=",round(max(abs(cor(x[,(i)],response,use="pairwise.complete.obs")),
                          abs(cor(x[,(i)],response,method="spearman",use="pairwise.complete.obs")),abs(cor(x[,(i)],response,method="kendall",use="pairwise.complete.obs"))),digits=2),
                          sep=""),line=.02,cex.lab=1.5)
                          #,y=.85,x=max(x[,(i)])-.2*diff(range(x[,(i)])),cex=1.5)

                 } else{
        if (i == j || (i < j && has.lower) || (i > j && has.upper)) {
            box()
            if(i==1) title(main=paste("Total Cor=",my.labels[j],sep=""),line=.04,cex.main=1.5)
            #if (i == 1 && (!(j%%2) || !has.upper || !has.lower))
             #   localAxis(1 + 2 * row1attop, x[, j], x[, i],
             #   ...)
            if (i == nc)
                localAxis(3 - 2 * row1attop, x[, j], x[, i],
                  ...)
            if (j == 1 && (i!=1 || !has.upper || !has.lower))
                localAxis(2, x[, j], x[, i], ...)
            #if (j == nc && (i%%2 || !has.upper || !has.lower))
            #    localAxis(4, x[, j], x[, i], ...)
            mfg <- par("mfg")
            if (i == j) {
                if (has.diag)
                  localDiagPanel(as.vector(x[, i]),...)
                if (has.labs) {
                  par(usr = c(0, 1, 0, 1))
                  if (is.null(cex.labels)) {
                    l.wid <- strwidth(labels, "user")
                    cex.labels <- max(0.8, min(2, 0.9/max(l.wid)))
                  }

                  text.panel(0.5, label.pos, labels[i], cex = cex.labels,
                    font = font.labels)
                }
            }

            else if (i < j)
                  if(length(unique(x[,i])>2)){
                  localLowerPanel(as.vector(x[, j]), as.vector(x[,
                    i]), ...) } else {
                      my.panel.smooth(as.vector(x[, j]),as.vector(x[,i]))
                    }
                  
            else localUpperPanel(as.vector(x[, j]), as.vector(x[,
                i]), ...)
            if (any(par("mfg") != mfg))
                stop("the 'panel' function made a new plot")
        }
        else par(new = FALSE)
    }}
    if (!is.null(main)) {
        font.main <- if ("font.main" %in% nmdots)
            dots$font.main
        else par("font.main")
        cex.main <- if ("cex.main" %in% nmdots)
            dots$cex.main
        else par("cex.main")
        mtext(main, 3, 3, TRUE, 0.5, cex = cex.main, font = font.main)
    }
    invisible(NULL)
}


my.panel.smooth<-function (x, y, col = par("col"), bg = NA, pch = par("pch"),
    cex = 1, col.smooth = "red", span = 2/3, iter = 3, weights=rep(1,times=length(y)), ...)
{
    o<-order(x)
    points(x, y, pch = pch, col = col, bg = bg, cex = cex)
    ok <- is.finite(x) & is.finite(y)
    if (any(ok) && length(unique(x))>3)
    lines(lowess(x[o],y[o],iter=0),col="red")
        #lines(smooth.spline(x,w=weights,jitter(y,amount=(max(y)-min(y))/100),nknots=min(length(unique(x)),4)),col="red")

}


Args <- commandArgs(T)
    print(Args)
    #assign default values
    num.plots <- 10
    min.cor <- .7
    responseCol <- "ResponseBinary"
    cors.w.highest <- FALSE
    pres=TRUE
    absn=TRUE
    bgd=TRUE
    #replace the defaults with passed values
    for (arg in Args) {
    	argSplit <- strsplit(arg, "=")
    	argSplit[[1]][1]
    	argSplit[[1]][2]
    	if(argSplit[[1]][1]=="p") num.plots <- argSplit[[1]][2]
    	if(argSplit[[1]][1]=="m") min.cor <- argSplit[[1]][2]
    	if(argSplit[[1]][1]=="o") output.file <- argSplit[[1]][2]
    	if(argSplit[[1]][1]=="i") infile <- argSplit[[1]][2]
    	if(argSplit[[1]][1]=="rc") responseCol <- argSplit[[1]][2]
    	if(argSplit[[1]][1]=="core") cors.w.highest <- argSplit[[1]][2]
      if(argSplit[[1]][1]=="pres") pres <- argSplit[[1]][2]
      if(argSplit[[1]][1]=="absn") absn <- argSplit[[1]][2]
      if(argSplit[[1]][1]=="bgd") bgd <- argSplit[[1]][2]
    }

    print(num.plots)
    print(min.cor)
    print(output.file)
    print (infile)
    print(responseCol)
    print(cors.w.highest)
    print(pres)
    print(absn)
    print(bgd)
    
	#Run the Pairs Explore function with these parameters
    Pairs.Explore(num.plots=num.plots,
    min.cor=min.cor,
    input.file=infile,
		output.file=output.file,
		response.col=responseCol,
		cors.w.highest=cors.w.highest,
		pres,
		absn,
		bgd)

