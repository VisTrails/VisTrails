TestFunction<-function(input.file,parameter.list,Debug,rc,output.dir){

    ifelse(Debug,
        options(error=expression(if(interactive()) recover() else dump.calls())),
        options(error=NULL))
 Brt.Out<-list()
 Mars.Out<-list()
 Glm.Out<-list()
 RF.Out<-list()
  for (i in 1:length(input.file)){
      Brt.Out[[i]]<-unit.test(i,parameter.list$brt.use.list,parameter.list$brt.list,"brt",outpur.dir,rc)
      Mars.Out[[i]]<-unit.test(i,parameter.list$mars.use.list,parameter.list$mars.list,"mars",outpur.dir,rc)
      Glm.Out[[i]]<-unit.test(i,parameter.list$mars.use.list,parameter.list$mars.list,"glm",outpur.dir,rc)
      RF.Out[[i]]<-unit.test(i,parameter.list$mars.use.list,parameter.list$mars.list,"rf",outpur.dir,rc)
    } #end file for loop

    options(error=NULL)
    Out.list=list(Brt.Out=Brt.Out,Mars.Out=Mars.Out,Glm.Out=Glm.Out,RF.Out)
    return(Out.list)
}



