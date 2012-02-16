make.auc.plot.jpg<-function(ma.reduced,pred,plotname,modelname,test.split=FALSE,thresh=NULL,train=NULL,train.pred=NULL,opt.methods=2,weight,out){

      if(is.null(weight)) weight=rep(1,times=dim(ma.reduced)[1])
    auc.data <- data.frame(ID=1:nrow(ma.reduced),pres.abs=ma.reduced[,1],pred=pred)
    p.bar <- sum(auc.data$pres.abs * weight) / sum(weight)
    n.pres <- sum(auc.data$pres.abs>=1)
    n.abs <- nrow(auc.data)-n.pres

    null.dev<-calc.dev(auc.data$pres.abs, rep(p.bar,times=length(auc.data$pres.abs)), weight, family=out$input$model.family)$deviance*nrow(ma.reduced)
    dev.fit<-calc.dev(auc.data$pres.abs, pred, weight, family=out$input$model.family)$deviance*nrow(ma.reduced)
    dev.exp <- null.dev - dev.fit
    pct.dev.exp <- dev.exp/null.dev*100
   correlation<-cor(auc.data$pres.abs,pred)
    residual.smooth.fct<-NULL
     if(test.split==FALSE) residual.smooth.fct<-resid.image(calc.dev(auc.data$pres.abs, pred, weight, family=out$input$model.family)$dev.cont,pred,
          auc.data$pres.abs,out$dat$ma$train.xy[,1],out$dat$ma$train.xy[,2],out$input$model.family,out$input$output.dir,out)

    if(is.null(thresh) & out$input$model.family!="poisson"){
      thresh <- as.numeric(optimal.thresholds(auc.data,opt.methods=opt.methods))[2]
    }

    if(out$input$model.family%in%c("binomial","bernoulli")){
      auc.fit <- auc(auc.data,st.dev=T)
          if(test.split==TRUE){
            jpeg(file=plotname)
            d<-data.frame(ID=1:nrow(train),pres.abs=train[,1],pred=train.pred)
            thresh<- as.numeric(optimal.thresholds(d,opt.methods=opt.methods))[2]
            TestTrainRocPlot(DATA=d,opt.thresholds=thresh,add.legend=FALSE,lwd=2)
            TestTrainRocPlot(auc.data,model.names=modelname,opt.thresholds=thresh,add.roc=TRUE,line.type=2,color="red",add.legend=FALSE)
            legend(x=.66,y=.2,c("Training Split","Testing Split"),lty=2,col=c("black","red"),lwd=2)
            graphics.off()}
          else {
            jpeg(file=plotname)
            TestTrainRocPlot(auc.data,model.names=modelname,opt.thresholds=thresh)
            graphics.off()
          }
        cmx <- cmx(auc.data,threshold=thresh)
        PCC <- pcc(cmx,st.dev=F)*100
        SENS <- sensitivity(cmx,st.dev=F)
        SPEC <- specificity(cmx,st.dev=F)
        KAPPA <- Kappa(cmx,st.dev=F)
        TSS <- SENS+SPEC-1
    }

    if(out$input$model.family%in%c("poisson")){
      auc.fit <- auc(auc.data,st.dev=T)
          if(test.split==FALSE){
            jpeg(file=plotname)
            par(mfrow=c(2,2))
            #plot(out$mods$final.mod)
             plot(log(pred[pred!=0]),(auc.data$pres.abs[pred!=0]-pred[pred!=0]),xlab="Predicted Values (log scale)",ylab="Residuals",main="Residuals vs Fitted",ylim=c(-3,3))
              abline(h=0,lty=2)
              #this is the residual plot from glm but I don't think it will work for anything else
              qqnorm(residuals(out$mods$final.mod),ylab="Std. deviance residuals")
              qqline(residuals(out$mods$final.mod))
               yl <- as.expression(substitute(sqrt(abs(YL)), list(YL = as.name("Std. Deviance Resid"))))
              plot(log(pred[pred!=0]),sqrt((abs(residuals(out$mods$final.mod,type="deviance")[pred!=0]))),xlab="Predicted Values (log Scale)",ylab=yl)
            graphics.off()}
       prediction.error<-sum((auc.data$pres.abs-pred)^2)
       cmx=PCC=SENS=SPEC=KAPPA=TSS<-NA
    }

      calibration.stats<-calibration(auc.data$pres.abs, pred, family =out$input$model.family)
      response<-ma.reduced$response

    capture.output(cat("\n\n============================================================",
                        "\n\nEvaluation Statistics"),file=paste(out$dat$bname,"_output.txt",sep=""),append=TRUE)
          if(!is.null(out$dat$ma$ma.test))
                        capture.output(cat(" applied to",ifelse(!test.split,"train","test"), "split:\n",sep=" "),
                        file=paste(out$dat$bname,"_output.txt",sep=""),append=TRUE)
                      capture.output(cat( "\n",
                       "\n\t Correlation Coefficient      : ",cor.test(pred,response)$estimate,
                       "\n\t NULL Deviance                : ",null.dev,
                       "\n\t Fit Deviance                 : ",dev.fit,
                       "\n\t Explained Deviance           : ",dev.exp,
                       "\n\t Percent Deviance Explained   : ",pct.dev.exp,
                       file=paste(out$dat$bname,"_output.txt",sep=""),append=TRUE))

                        if(out$input$model.family%in%c("binomial","bernoulli")){
                               capture.output(cat(
                                 "\n\n  Threshold Methods based on", switch(opt.methods,
                                "1"=".5 threshold",
                                "2"="Sens=Spec",
                                "3"="maximize (sensitivity+specificity)/2",
                                "4"="maximize Kappa",
                                "5"="maximize percent correctly classified",
                                "6"="predicted prevalence=observed prevalence",
                                "7"="threshold=observed prevalence",
                                "8"="mean predicted probability",
                                "9"="minimize distance between ROC plot and (0,1)",
                                ),
                                "\n\t Threshold                    : ",
                                thresh,
                                "\n\n\t Confusion Matrix: \n\n"),
                                print.table(cmx),
                           cat("\n\t AUC                          : ",auc.fit[1,1],
                           "\n\t Percent Correctly Classified : ",PCC,
                           "\n\t Sensitivity                  : ",SENS,
                           "\n\t Specificity                  : ",SPEC,
                           "\n\t Kappa                        : ",KAPPA,
                           "\n\t True Skill Statistic         : ",TSS,"\n"),
                           file=paste(out$dat$bname,"_output.txt",sep=""),append=TRUE)
                       }

                         capture.output(cat( "\n\n   Calibration Statistics",
                          "\n\t Intercept (general calibration)                            : ",calibration.stats[1],
                          "\n\t Slope   (direction and variation in fit)                   : ",calibration.stats[2],
                          "\n\t Testa0b1 (overall reliability of predictors)               : ",calibration.stats[3],
                          "\n\t Testa0|b1(incorrect calibration given correct refinement)  : ",calibration.stats[4],
                          "\n\t Testb1|a (refinement given correct calibration)            : ",calibration.stats[5],"\n",
                       file=paste(out$dat$bname,"_output.txt",sep=""),append=TRUE))
                       
                       last.dir<-strsplit(out$input$output.dir,split="\\\\")
                        parent<-sub(paste("\\\\",last.dir[[1]][length(last.dir[[1]])],sep=""),"",out$input$output.dir)

                         compile.out<-paste(parent,
                              paste(switch(out$input$model.family,"binomial"="Binary","bernoulli"="Binary","poisson"="Count"),ifelse(!is.null(out$dat$ma$ma.test),"TestTrain",""),
                              "AppendedOutput.csv",sep="."),sep="/")

                       if(out$input$model.family%in%c("binomial","bernoulli")){
                       x=data.frame(cbind(c("Correlation Coefficient","Percent Deviance Explained","Percent Correctly Classified","Sensitivity","Specificity"),
                            c(as.vector(cor.test(pred,response)$estimate),pct.dev.exp,PCC,SENS,SPEC)))
                       }else  x=data.frame(cbind(c("Correlation Coefficient","Percent Deviance Explained","Prediction Error"),
                            c(as.vector(cor.test(pred,response)$estimate),pct.dev.exp,prediction.error)))

                        Header<-cbind(c("","Original Field Data","Field Data Template","PARC Output Folder","PARC Template","Covariate Selection Name",""),
                            c(last.dir[[1]][length(last.dir[[1]])],
                            out$dat$ma$input$OrigFieldData,out$dat$ma$input$FieldDataTemp,out$dat$ma$input$ParcOutputFolder,
                            out$dat$ma$input$ParcTemplate,ifelse(length(out$dat$ma$input$CovSelectName)==0,"NONE",out$dat$ma$input$CovSelectName),""))

AppendOut(compile.out,Header,x,out,test.split,parent=parent)

    return(list(thresh=thresh,cmx=cmx,null.dev=null.dev,dev.fit=dev.fit,dev.exp=dev.exp,pct.dev.exp=pct.dev.exp,auc=auc.fit[1,1],auc.sd=auc.fit[1,2],
        plotname=plotname,pcc=PCC,sens=SENS,spec=SPEC,kappa=KAPPA,tss=TSS,correlation=correlation,residual.smooth.fct=residual.smooth.fct))
}

