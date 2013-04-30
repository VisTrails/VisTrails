EvaluationStats<-function(out,thresh,train,train.pred,opt.methods=opt.methods){
    response<-out$dat$ma$ma.test[,1]

     if(out$input$model.source.file=="rf.r") {pred<-tweak.p(as.vector(predict(out$mods$final.mod,newdata=out$dat$ma$ma.test[,-1],type="prob")[,2]))
      modelname="Random Forest"
     }

    if(out$input$model.source.file=="mars.r") {pred<-mars.predict(out$mods$final.mod,out$dat$ma$ma.test)$prediction[,1]
         modelname="MARS"
    }

    if(out$input$model.source.file=="glm.r")  {pred=glm.predict(out$mods$final.mod,out$dat$ma$ma.test)
        modelname="GLM"
    }

    if(out$input$model.source.file=="brt.r") {pred=predict.gbm(out$mods$final.mod,out$dat$ma$ma.test,out$mods$final.mod$target.trees,type="response")
       modelname="BRT"
      }
      
    auc.output<-make.auc.plot.jpg(out$dat$ma$ma.test,pred=pred,plotname=paste(out$dat$bname,"_auc_plot.jpg",sep=""),
          modelname=modelname,test.split=TRUE,thresh=thresh,train=train,train.pred,opt.methods=opt.methods,weight=out$dat$ma$test.weights,out=out)

                out$mods$auc.output<-auc.output

}
