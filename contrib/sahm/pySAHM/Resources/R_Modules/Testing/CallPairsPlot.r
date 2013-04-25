#Running R from the command line
#input.file="I:\\VisTrails\\WorkingFiles\\workspace\\GYA_demo\\test.csv"
    #output.dir<-"H:\\Desktop\\SAHM\\Rcode\\ExposingModelParameters\\PDFCheck\\"
    #response.col= "ResponseBinary"
    #min.cor<-.7
    #num.plots<-10
source("I:\\VisTrails\\Central_VisTrailsInstall_debug\\vistrails\\packages\\sahm\\pySAHM\\Resources\\R_Modules\\PairsExplore.r")



num.plots <- 10
    min.cor <- .7
    responseCol <- "responseCount"
    cors.w.highest <- FALSE
    pres=FALSE
    absn=TRUE
    bgd=TRUE
    #infile="I:\\VisTrails\\WorkingFiles\\workspace\\talbertc_20110510T100421\\TestTrainingSplit_1.csv"
    infile="I:\\NPS_NPMP_data\\ModelingSession_June\\EAME_MDS.csv"
    output.file="H:\\Desktop\\SAHM\\Output\\PairsPlot\\pairPres.jpg"
    Pairs.Explore(num.plots=num.plots,
    min.cor=min.cor,
    input.file=infile,
		output.file=output.file,
		response.col=responseCol,
		pres=TRUE,
		absn=TRUE,
		bgd=TRUE,
    Debug=TRUE)

#binary
input.file="C:\\VisTrails\\EAMEBinTT.csv"
input.file="C:\\VisTrails\\DICKBinTT.csv"
input.file="C:\\VisTrails\\HESPBinTT.csv"
input.file="C:\\VisTrails\\GRSPBinTT.csv"
responseCol="responseBinary"
input.file="I:\\SpeciesData\\kudzu\\July2011\\MergedDataset_1.csv"
#list.files("I:\\VisTrails\\WorkingFiles\\workspace\\morisettej_20110725T102358")
Pairs.Explore(num.plots=num.plots,
    min.cor=min.cor,
    input.file=input.file,
		output.file=output.file,
		response.col=responseCol,
		pres=TRUE,
		absn=TRUE,
		bgd=TRUE,
    Debug=TRUE)


#count
input.file="I:\\NPS_NPMP_data\\ModelingSession_June\\EAME_MDS.csv"
input.file="I:\\NPS_NPMP_data\\ModelingSession_June\\DICK_MDS.csv"
input.file="I:\\NPS_NPMP_data\\ModelingSession_June\\HESP_MDS.csv"
input.file="I:\\NPS_NPMP_data\\ModelingSession_June\\GRSP_MDS.csv"
input.file="N:\\Active\\FORT_RAM\\VisTrails\\workspace\\talbertc_20110621T083827\\MergedDataset_1.csv"

input.file="N:\\Active\\FORT_RAM\\VisTrails\\workspace\\talbertc_20110621T114212\\MergedDataset_1.csv"
responseCol="responseBinary"
Pairs.Explore(num.plots=num.plots,
    min.cor=min.cor,
    input.file=input.file,
		output.file=output.file,
		response.col=responseCol,
		pres=TRUE,
		absn=TRUE,
		bgd=TRUE,
    Debug=TRUE)

print(getwd())
source_pathname  = get("PairsExplore",envir = parent.frame())
source_dirname = dirname(source_pathname )
setwd(source_dirname)
print(getwd())


frame_files <- lapply(sys.frames(), function(x) x$ofile)
frame_files <- Filter(Negate(is.null), frame_files)
PATH <- dirname(frame_files[[length(frame_files)]])


as.double.foo <- function(x)
{
    str(sys.calls())
    print(sys.frames())
    print(sys.parents())
    print(sys.frame(-1)); print(parent.frame())
    x
}
t2 <- function(x) as.double(x)
a <- structure(pi, class = "foo")
t2(a)

library(R.utils)
print(getAbsolutePath("Pairs.Explore"))


Pairs.Explore(num.plots=10,min.cor=.7,input.file="I:\\VisTrails\\WorkingFiles\\workspace\\GYA_demo\\test.csv",
output.dir="H:\\Desktop\\SAHM\\Rcode\\ExposingModelParameters\\PDFCheck\\",
response.col="ResponseBinary",cors.w.highest=TRUE)

# The BRT Function
C:\R-2.12.1\bin\i386\Rterm.exe --vanilla -f I:\VisTrails\Central_VisTrailsInstall_debug\vistrails\packages\sahm\pySAHM\Resources\R_Modules\FIT_BRT_pluggable.r --args c=I:\VisTrails\WorkingFiles\workspace\GYA_demo\test.csv o=C:\temp rc=ResponseBinary


C:\R-2.12.1\bin\i386\Rterm.exe --vanilla -f H:\Desktop\SAHM\Rcode\PredictorSelection\PairsExplore2.r --args p=10 m=.7 o=H:\Desktop\SAHM\Rcode\ExposingModelParameters\PDFCheck\ i="I:\VisTrails\WorkingFiles\workspace\GYA_demo\test.csv" rc="ResponseBinary" core=TRUE



if(argSplit[[1]][1]=="p") num.plots <- argSplit[[1]][2]
    	if(argSplit[[1]][1]=="m") min.cor <- argSplit[[1]][2]
    	if(argSplit[[1]][1]=="o") output.dir <- argSplit[[1]][2]
    	if(argSplit[[1]][1]=="i") input.file <- argSplit[[1]][2]
    	if(argSplit[[1]][1]=="rc") responseCol <- argSplit[[1]][2]
    	if(argSplit[[1]][1]=="core") cors.w.higest <- argSplit[[1]][2]