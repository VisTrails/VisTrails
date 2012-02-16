unit.test<-function(i,use.list,model.list,model,outpur.dir,rc){
  list.fct<-function(x,i) sum(!is.na(match(x=i,table=x)))
      valid.params<-which(unlist(lapply(use.list,list.fct,i=i))!=0,arr.ind=TRUE)
       Model.Out<-list()
       Model.Out[[i]]<-data.frame(list("FctFailed"=rep(FALSE,times=length(valid.params)),
                              "PredictFailed"=rep(FALSE,times=length(valid.params)),
                              "NullDev"=rep(0,times=length(valid.params)),
                              "FitDev"=rep(0,times=length(valid.params)),
                              "Correlation"=rep(0,times=length(valid.params)),
                              "ErrorMessage"=rep("No Error",times=length(valid.params))),row.names=valid.params)

                            class(Model.Out[[i]]$ErrorMessage)<-"character"
      if(length(valid.params)!=0){
      for(j in 1:length(valid.params)){

            k<-valid.params[j]
                   if(Debug==TRUE) parameter.list$brt.list[[k]]$debug.mode=TRUE

                    a<-paste(paste(names(model.list[[k]]),model.list[[k]],sep="="),collapse=",")
                    call.fct<-paste("fit.",model,".fct(ma.name=\"",input.file[i],
                                  "\", tif.dir=NULL,output.dir=\"",output.dir,"\", response.col=\"",rc,"\",",a,")",sep="")
                    #Right here I should remove almost everything since all output is written to the global environment
                    call.predict<-"PredictModel(workspace=paste(output.dir,\"modelWorkspace\",sep=\"/\"),out.dir=output.dir)"
                      if(Debug==FALSE) {call.fct<-paste("try(",call.fct,",silent=TRUE)",sep="")
                                      call.predict<-paste("try(",call.predict,")",sep="")
                     #so that we don't predict on an old copy in the next loop
                     file.remove(paste(output.dir,"modelWorkspace",sep="/"))
                                        }

                  fct.output<-eval(parse(text=call.fct))
                    sink()
                  pred.output<-eval(parse(text=call.predict))
                    sink()
                if(class(fct.output)=="try-error") {
                Model.Out[[i]][j,1]=TRUE
                Model.Out[[i]][j,6]=fct.output[1]
                  }  else {
                  Model.Out[[i]][j,1]=FALSE
                  Model.Out[[i]][j,3]<-fct.output$mods$auc.output$null.dev
                  Model.Out[[i]][j,4]<-fct.output$mods$auc.output$dev.fit
                  Model.Out[[i]][j,5]<-fct.output$mods$auc.output$correlation
                    }
                if(class(pred.output)=="try-error") Model.Out[[i]][j,2]=TRUE

          }
          print(Model.Out)
          } ## END BRT
return(Model.Out)
 }