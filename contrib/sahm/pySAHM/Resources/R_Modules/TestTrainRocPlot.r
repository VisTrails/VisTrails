TestTrainRocPlot<-function (DATA, threshold = 101, find.auc = TRUE, which.model = (1:(ncol(DATA) -
    2)), na.rm = FALSE, xlab = "1-Specificity (false positives)",
    ylab = "Sensitivity (true positives)", main = "ROC Plot",
    model.names = NULL, color = NULL, line.type = NULL, lwd = 1,
    mark = 0, mark.numbers = TRUE, mark.color = NULL, opt.thresholds = NULL,
    opt.methods = NULL, req.sens, req.spec, obs.prev = NULL,
    smoothing = 1, add.legend = TRUE, legend.text = model.names,
    legend.cex = 0.8, add.opt.legend = TRUE, opt.legend.text = NULL,
    opt.legend.cex = 0.7, counter.diagonal = FALSE, pch = NULL,
    FPC, FNC, cost.line = FALSE,add.roc=FALSE)
{
    if (is.data.frame(DATA) == FALSE) {
        if (is.matrix(DATA) == TRUE) {
            DATA <- as.data.frame(DATA)
        }
        else {
            stop("'DATA' must be either data frame or matrix")
        }
    }
    OBS <- DATA[, 2]
    if (length(OBS[OBS == 0]) == 0) {
        stop("no observed absences in dataset, therefore specificity does not",
            "exist, and modeling, much less Area Under the Curve, is not very",
            "meaningful")
    }
    if (length(OBS[OBS == 1]) == 0) {
        stop("no observed presences in dataset, therefore sensitivity does not",
            "exist, and modeling, much less Area Under the Curve, is not very",
            "meaningful")
    }
    if (is.logical(find.auc) == FALSE) {
        stop("'find.auc' must be of logical type")
    }
    if (is.logical(na.rm) == FALSE) {
        stop("'na.rm' must be of logical type")
    }
    if (is.logical(mark.numbers) == FALSE) {
        stop("'mark.numbers' must be of logical type!")
    }
    if (is.logical(add.legend) == FALSE) {
        stop("'add.legend' must be of logical type!")
    }
    if (is.logical(add.opt.legend) == FALSE) {
        stop("'add.opt.legend' must be of logical type")
    }
    if (is.logical(counter.diagonal) == FALSE) {
        stop("'counter.diagonal' must be of logical type")
    }
    if (length(smoothing) != 1) {
        stop("'smoothing' must be a single number greater than or equal to 1")
    }
    else {
        if (is.numeric(smoothing) == FALSE) {
            stop("'smoothing' must be a single number greater than or equal to 1")
        }
        else {
            if (smoothing < 1) {
                stop("'smoothing' must be a single number greater than or equal to 1")
            }
        }
    }
    if (sum(is.na(DATA)) > 0) {
        if (na.rm == TRUE) {
            NA.rows <- apply(is.na(DATA), 1, sum)
            warning(length(NA.rows[NA.rows > 0]), " rows ignored due to NA values")
            DATA <- DATA[NA.rows == 0, ]
        }
        else {
            return(NA)
        }
    }
    DATA[DATA[, 2] > 0, 2] <- 1
    N.models <- ncol(DATA) - 2
    if (is.null(obs.prev) == TRUE) {
        obs.prev <- sum(DATA[, 2])/nrow(DATA)
    }
    if (obs.prev < 0 || obs.prev > 1) {
        stop("'obs.prev' must be a number between zero and one")
    }
    if (obs.prev == 0) {
        warning("because your observed prevalence was zero, results may be strange")
    }
    if (obs.prev == 1) {
        warning("because your observed prevalence was one, results may be strange")
    }
    if (min(which.model) < 1 || sum(round(which.model) != which.model) !=
        0) {
        stop("values in 'which.model' must be positive integers")
    }
    if (max(which.model) > N.models) {
        stop("values in 'which.model' must not be greater than number of models in 'DATA'!")
    }
    if (is.null(model.names) == TRUE) {
        model.names <- if (is.null(names(DATA)) == FALSE) {
            names(DATA)[-c(1, 2)]
        }
        else {
            paste("Model", 1:N.models)
        }
    }
    if (N.models != length(model.names) && (length(which.model) !=
        1 || length(model.names) != 1)) {
        stop("If 'model.names' is specified it must either be a single name, or a vector",
            "of the same length as the number of model predictions in 'DATA'")
    }
    if (is.null(legend.text) == TRUE) {
        legend.text <- model.names
    }
    if (length(legend.text) != N.models) {
        stop("'opt.legend.text' must be of same length as 'opt.methods'")
    }
    DATA <- DATA[, c(1, 2, which.model + 2)]
    if (length(model.names) != 1) {
        model.names <- model.names[which.model]
    }
    if (length(legend.text) != 1) {
        legend.text <- legend.text[which.model]
    }
    N.dat <- ncol(DATA) - 2
    if (is.null(obs.prev) == TRUE) {
        obs.prev <- sum(DATA[, 2])/nrow(DATA)
    }
    if (obs.prev < 0 || obs.prev > 1) {
        stop("'obs.prev' must be a number between zero and one")
    }
    mark <- matrix(mark, length(mark), N.dat)
    if (!is.null(opt.methods) && is.null(opt.thresholds)) {
        opt.thresholds <- TRUE
    }
    if (is.null(opt.methods) && is.null(opt.thresholds)) {
        opt.thresholds <- FALSE
    }
    if (is.null(opt.methods)) {
        opt.methods <- c(1, 2, 4)
    }
    if (is.logical(opt.thresholds) == TRUE) {
        if (opt.thresholds == TRUE) {
            POSSIBLE.meth <- c("Default", "Sens=Spec", "MaxSens+Spec",
                "MaxKappa", "MaxPCC", "PredPrev=Obs", "ObsPrev",
                "MeanProb", "MinROCdist", "ReqSens", "ReqSpec",
                "Cost")
            N.meth <- length(opt.methods)
            if (is.numeric(opt.methods) == TRUE) {
                if (sum(opt.methods %in% (1:length(POSSIBLE.meth))) !=
                  N.meth) {
                  stop("invalid optimization method")
                }
                else {
                  opt.methods <- POSSIBLE.meth[opt.methods]
                }
            }
            if (sum(opt.methods %in% POSSIBLE.meth) != N.meth) {
                stop("invalid optimization method")
            }
            if (is.null(opt.legend.text) == TRUE) {
                opt.legend.text <- opt.methods
            }
            if (length(opt.legend.text) != N.meth) {
                stop("'opt.legend.text' must be of same length as 'opt.methods'")
            }
            if ("ReqSens" %in% opt.methods) {
                if (missing(req.sens)) {
                  warning("req.sens defaults to 0.85")
                  req.sens <- 0.85
                }
            }
            if ("ReqSpec" %in% opt.methods) {
                if (missing(req.spec)) {
                  warning("req.spec defaults to 0.85")
                  req.spec <- 0.85
                }
            }
            if ("Cost" %in% opt.methods) {
                if (missing(FPC) || missing(FNC)) {
                  warning("costs assumed to be equal")
                  FPC <- 1
                  FNC <- 1
                }
                if (FPC <= 0 || FNC <= 0) {
                  stop("costs must be positive")
                }
                if (is.logical(cost.line) == FALSE) {
                  stop("'cost.line' must be of logical type")
                }
                if (!"Cost" %in% opt.methods) {
                  cost.line <- FALSE
                }
            }
            mark <- optimal.thresholds(DATA = DATA, threshold = threshold,
                model.names = model.names, na.rm = na.rm, opt.methods = opt.methods,
                req.sens = req.sens, req.spec = req.spec, obs.prev = obs.prev,
                smoothing = smoothing, FPC = FPC, FNC = FNC)[,
                -1, drop = FALSE]
            if (is.null(pch) == TRUE) {
                pch <- c(1, 5, 2, 16, 15, 17, 8, 6, 9, 12, 4,
                  7)[match(opt.methods, POSSIBLE.meth)]
            }
            else {
                pch <- rep(pch, length(opt.methods))[1:length(opt.methods)]
            }
        }
    }
    if (is.logical(opt.thresholds) == FALSE) {
        if (!is.numeric(opt.thresholds)) {
            stop("'opt.thresholds' must be 'TRUE', 'FALSE', or numeric")
        }
        if (min(opt.thresholds) < 0) {
            stop("'opt.thresholds' can not be negative")
        }
        if (max(opt.thresholds) > 1) {
            if (N.thr == 1 && round(opt.thresholds) == opt.thresholds) {
                opt.thresholds <- seq(length = opt.thresholds,
                  from = 0, to = 1)
                N.thr <- length(opt.thresholds)
            }
            else {
                stop("non-interger, non-logical 'opt.thresholds' greater than 1")
            }
        }
        N.opt.thresh <- length(opt.thresholds)
        if (is.null(opt.legend.text)) {
            opt.legend.text <- rep("threshold", N.opt.thresh)
        }
        if (length(opt.legend.text) != N.opt.thresh) {
            stop("length of 'opt.legend.text' does not match number of specified thresholds")
        }
        if (is.null(pch)) {
            pch <- 1:N.opt.thresh
        }
        if (length(pch) != N.opt.thresh) {
            stop("length of 'pch' does not match number of specified thresholds")
        }
        mark <- matrix(opt.thresholds, length(opt.thresholds),
            N.dat)
        opt.thresholds = TRUE
    }
    if (is.null(pch) == TRUE) {
        pch <- 16
    }
    if (is.null(color) == TRUE) {
        colors <- rep(1, N.dat)
        if (is.null(line.type) == TRUE) {
            line.type <- (1:N.dat) + 1
        }
    }
    else {
        if (is.logical(color) == TRUE) {
            if (color == FALSE) {
                colors <- rep(1, N.dat)
                if (is.null(line.type) == TRUE) {
                  line.type <- (1:N.dat) + 1
                }
            }
            else {
                colors <- (1:N.dat) + 1
                lwd <- 2 * lwd
                if (is.null(line.type) == TRUE) {
                  line.type <- rep(1, N.dat)
                }
            }
        }
        else {
            colors <- rep(color, N.dat)[1:N.dat]
            lwd <- 2 * lwd
            if (is.null(line.type) == TRUE) {
                line.type <- rep(1, N.dat)
            }
        }
    }
    if (is.null(mark.color) == TRUE) {
        mark.colors <- colors
    }
    else {
        if (is.logical(mark.color) == TRUE) {
            if (mark.color == FALSE) {
                mark.colors <- rep(1, N.dat)
            }
            else {
                mark.colors <- (1:N.dat) + 1
            }
        }
        else {
            mark.colors <- rep(mark.color, N.dat)[1:N.dat]
        }
    }
    if (is.null(line.type) == FALSE) {
        if (is.logical(line.type) == TRUE) {
            if (line.type == FALSE) {
                line.type <- rep(1, N.dat)
            }
            else {
                line.type <- (1:N.dat) + 1
            }
        }
        else {
            line.type <- rep(line.type, N.dat)[1:N.dat]
        }
    }
    op <- par(pty = "s")
    if(add.roc==FALSE){
    plot(c(0, 1), c(0, 1), type = "n", xlab = xlab, ylab = ylab,
        main = main)}
    lines(c(0, 1), c(0, 1), col = "lightgray")
    if (counter.diagonal == TRUE) {
        abline(a = 1, b = -1, col = "lightgray")
    }
    for (dat in 1:N.dat) {
        Model.dat <- roc.plot.calculate(DATA = DATA, threshold = threshold,
            which.model = dat)
        lines(x = (1 - Model.dat$specificity), y = Model.dat$sensitivity,
            lty = line.type[dat], lwd = lwd, col = colors[dat])
        if (max(mark) != 0) {
            Mark.dat <- roc.plot.calculate(DATA = DATA, threshold = mark[,
                dat], which.model = dat)
            Mark.pretty <- round(Mark.dat$threshold, 2)
            Mark.pretty.char <- as.character(Mark.pretty)
            Mark.pretty.char[Mark.pretty == 0] <- "0.00"
            Mark.pretty.char[Mark.pretty == 1] <- "1.00"
            Mark.pretty.char[nchar(Mark.pretty.char) == 3] <- paste(Mark.pretty.char[nchar(Mark.pretty.char) ==
                3], "0", sep = "")
            if(add.roc==FALSE){
            points(x = (1 - Mark.dat$specificity), y = Mark.dat$sensitivity,
                cex = 2, pch = pch, col = mark.colors[dat])
            if (mark.numbers == TRUE) {
                text(x = (1 - Mark.dat$specificity), y = Mark.dat$sensitivity -
                  0.03, labels = Mark.pretty.char, pos = 4, col = mark.colors[dat])
            }}
        }
        if (cost.line == TRUE) {
            tag <- match("Cost", opt.methods)
            sl <- (FPC/FNC) * (1 - obs.prev)/obs.prev
            if (obs.prev == 0) {
                obs.prev <- 1e-06
            }
            abline(a = Mark.dat$sensitivity[tag] - ((1 - Mark.dat$specificity[tag]) *
                sl), b = sl, col = mark.colors[dat], lty = 3)
        }
    }
    inset <- c(0.02, 0.02)
    if (opt.thresholds == TRUE && add.opt.legend == TRUE) {
        if (N.dat == 1) {
            opt.legend.names <- paste(Mark.pretty.char, opt.legend.text)
        }
        else {
            opt.legend.names <- opt.legend.text
        }
        leg.loc <- legend(x = "bottomright", inset = inset, pt.cex = 1,
            legend = opt.legend.names, pch = pch, bg = "white",
            cex = opt.legend.cex)
        inset <- c(0.02, leg.loc$rect$top + 0.05)
    }
    if (add.legend == TRUE) {
        legend.names <- legend.text
        if (find.auc == TRUE) {
            AUC <- rep(0, N.dat)
            for (dat in 1:N.dat) {
                AUC[dat] <- auc(DATA = DATA, which.model = dat)$AUC
            }
            AUC.pretty <- round(AUC, 2)
            AUC.pretty.char <- as.character(AUC.pretty)
            AUC.pretty.char[AUC.pretty == 0] <- "0.00"
            AUC.pretty.char[AUC.pretty == 1] <- "1.00"
            AUC.pretty.char[nchar(AUC.pretty.char) == 3] <- paste(AUC.pretty.char[nchar(AUC.pretty.char) ==
                3], "0", sep = "")
            legend.names <- paste(AUC.pretty.char, legend.text)
        }
        legend(x = "bottomright", inset = inset, legend = legend.names,
            lty = line.type, col = colors, title = "AUC:", cex = legend.cex,
            lwd = lwd, bg = "white")
    }
    par(op)
}
