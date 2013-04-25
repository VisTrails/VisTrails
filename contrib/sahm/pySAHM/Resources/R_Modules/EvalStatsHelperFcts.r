"calibration" <-
      function(obs, preds, family = "binomial")
      {
      #
      # j elith/j leathwick 17th March 2005
      # calculates calibration statistics for either binomial or count data
      # but the family argument must be specified for the latter
      # a conditional test for the latter will catch most failures to specify
      # the family
      #

      if (family == "bernoulli") family <- "binomial"
      pred.range <- max(preds) - min(preds)
      if(pred.range > 1.2 & family == "binomial") {
      print(paste("range of response variable is ", round(pred.range, 2)), sep = "", quote = F)
      print("check family specification", quote = F)
      return()
      }
      if(family == "binomial") {
      pred <- preds + 1e-005
      pred[pred >= 1] <- 0.99999
      mod <- glm(obs ~ log((pred)/(1 - (pred))), family = binomial)
      lp <- log((pred)/(1 - (pred)))
      a0b1 <- glm(obs ~ offset(lp) - 1, family = binomial)
      miller1 <- 1 - pchisq(a0b1$deviance - mod$deviance, 2)
      ab1 <- glm(obs ~ offset(lp), family = binomial)
      miller2 <- 1 - pchisq(a0b1$deviance - ab1$deviance, 1)
      miller3 <- 1 - pchisq(ab1$deviance - mod$deviance, 1)
      }
      if(family == "poisson") {
      mod <- glm(obs ~ log(preds), family = poisson)
      lp <- log(preds)
      a0b1 <- glm(obs ~ offset(lp) - 1, family = poisson)
      miller1 <- 1 - pchisq(a0b1$deviance - mod$deviance, 2)
      ab1 <- glm(obs ~ offset(lp), family = poisson)
      miller2 <- 1 - pchisq(a0b1$deviance - ab1$deviance, 1)
      miller3 <- 1 - pchisq(ab1$deviance - mod$deviance, 1)
      }
      calibration.result <- c(mod$coef, miller1, miller2, miller3)
      names(calibration.result) <- c("intercept", "slope", "testa0b1", "testa0|b1", "testb1|a")
      return(calibration.result)
}

"calc.dev" <-
        function(obs.values, fitted.values, weights = rep(1,length(obs.values)), family="binomial", calc.mean = TRUE)
        {
        # j. leathwick/j. elith
        #
        # version 2.1 - 5th Sept 2005
        #
        # function to calculate deviance given two vectors of raw and fitted values
        # requires a family argument which is set to binomial by default
        #
        #

        if (length(obs.values) != length(fitted.values))
           stop("observations and predictions must be of equal length")

        y_i <- obs.values

        u_i <- fitted.values

        if (family == "binomial" | family == "bernoulli") {

           deviance.contribs <- (y_i * log(u_i)) + ((1-y_i) * log(1 - u_i))
           deviance <- -2 * sum(deviance.contribs * weights)

        }

        if (family == "poisson" | family == "Poisson") {

            deviance.contribs <- ifelse(y_i == 0, 0, (y_i * log(y_i/u_i))) - (y_i - u_i)
            deviance <- 2 * sum(deviance.contribs * weights)

        }

        if (family == "laplace") {
            deviance <- sum(abs(y_i - u_i))
            }

        if (family == "gaussian") {
            deviance <- sum((y_i - u_i) * (y_i - u_i))
            }



        if (calc.mean) deviance <- deviance/length(obs.values)
        dev=list(deviance=deviance,dev.cont=deviance.contribs)
        return(dev)

}

beachcolours<-function (heightrange, sealevel = 0, monochrome = FALSE, ncolours = if (monochrome) 16 else 64)
{
#this function was robbed from the spatstat library internals
    if (monochrome)
        return(grey(seq(0, 1, length = ncolours)))
    stopifnot(is.numeric(heightrange) && length(heightrange) ==
        2)
    stopifnot(all(is.finite(heightrange)))
    depths <- heightrange[1]
    peaks <- heightrange[2]
    dv <- diff(heightrange)/(ncolours - 1)
    epsilon <- dv/2
    lowtide <- max(sealevel - epsilon, depths)
    hightide <- min(sealevel + epsilon, peaks)
    countbetween <- function(a, b, delta) {
        max(0, round((b - a)/delta))
    }
    nsea <- countbetween(depths, lowtide, dv)
    nbeach <- countbetween(lowtide, hightide, dv)
    nland <- countbetween(hightide, peaks, dv)
    colours <- character(0)
    if (nsea > 0)
        colours <- rev(rainbow(nsea, start = 3/6, end = 4/6))
    if (nbeach > 0)
        colours <- c(colours, rev(rainbow(nbeach, start = 3/12,
            end = 5/12)))
    if (nland > 0)
        colours <- c(colours, rev(rainbow(nland, start = 0, end = 1/6)))
    return(colours)
}
