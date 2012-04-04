Compile.Output<-function(out){
last.dir<-strsplit(out$input$output.dir,split="/")
length(last.dir[[1]])
parent<-sub(paste("/",last.dir[[1]][length(last.dir[[1]])],sep=""),"",out$input$output.dir)

txt0 <- paste("Generalized Liinear Results\n",out$input$run.time,"\n\n","Data:\n\t ",ma.name,"\n\t ","n(pres)=",
        out$dat$ma$n.pres[2],"\n\t n(abs)=",out$dat$ma$n.abs[2],"\n\t number of covariates considered=",(length(names(out$dat$ma$ma))-1),
        "\n\n","Settings:\n","\n\t model family=",out$input$model.family,
        "\n\n","Results:\n\t ","number covariates in final model=",length(out$dat$ma$used.covs),
        "\n\t pct deviance explained on train data =",round(out$mods$auc.output$pct.dev.exp,1),"%\n",
        "\n\t total time for model fitting=",round((unclass(Sys.time())-t0)/60,2),"min\n",sep="")
}