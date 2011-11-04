check.libs <- function(libs,out){

      lib.mssg <- unlist(suppressMessages(suppressWarnings(lapply(libs,require,quietly = T, warn.conflicts=F,character.only=T))))
      if(any(!lib.mssg)){
            install.packages(unlist(libs[!lib.mssg]), repos = "http://cran.r-project.org")
            lib.mssg <- unlist(suppressMessages(suppressWarnings(lapply(unlist(libs[!lib.mssg]),require,quietly = T, warn.conflicts=F,character.only=T))))
            }
        if(any(!lib.mssg)) {
           out$ec <- out$ec+1
            out$dat$missing.libs <-  paste(unlist(libs)[!lib.mssg],collapse="; ")
        stop("the following package(s) could not be loaded:",out$dat$missing.libs)
        }
      return(out)
      }


