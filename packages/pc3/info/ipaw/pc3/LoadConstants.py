


class LoadConstants(object): 
    EXPECTED_TABLES = ["P2Detection", "P2FrameMeta", "P2ImageMeta"]
    EXPECTED_DETECTION_COLS = ["objID", "detectID", "ippObjID", "ippDetectID", "filterID", "imageID", "obsTime", "xPos", "yPos", "xPosErr", "yPosErr", "instFlux", "instFluxErr", "psfWidMajor", "psfWidMinor", "psfTheta", "psfLikelihood", "psfCf", "infoFlag", "htmID", "zoneID", "assocDate", "modNum", "ra", "dec", "raErr", "decErr", "cx", "cy", "cz", "peakFlux", "calMag", "calMagErr", "calFlux", "calFluxErr", "calColor", "calColorErr", "sky", "skyErr", "sgSep", "dataRelease"]
    EXPECTED_FRAME_META_COLS = ["frameID", "surveyID", "filterID", "cameraID", "telescopeID", "analysisVer", "p1Recip", "p2Recip", "p3Recip", "nP2Images", "astroScat", "photoScat", "nAstRef", "nPhoRef", "expStart", "expTime", "airmass", "raBore", "decBore"]
    EXPECTED_IMAGE_META_COLS = ["imageID", "frameID", "ccdID", "photoCalID", "filterID", "bias", "biasScat", "sky", "skyScat", "nDetect", "magSat", "completMag", "astroScat", "photoScat", "nAstRef", "nPhoRef", "nx", "ny", "psfFwhm", "psfModelID", "psfSigMajor", "psfSigMinor", "psfTheta", "psfExtra1", "psfExtra2", "apResid", "dapResid", "detectorID", "qaFlags", "detrend1", "detrend2", "detrend3", "detrend4", "detrend5", "detrend6", "detrend7", "detrend8", "photoZero", "photoColor", "projection1", "projection2", "crval1", "crval2", "crpix1", "crpix2", "pc001001", "pc001002", "pc002001", "pc002002", "polyOrder", "pca1x3y0", "pca1x2y1", "pca1x1y2", "pca1x0y3", "pca1x2y0", "pca1x1y1", "pca1x0y2", "pca2x3y0", "pca2x2y1", "pca2x1y2", "pca2x0y3", "pca2x2y0", "pca2x1y1", "pca2x0y2"]

    class ColumnRange(object):
        def __init__(self, ColumnName_, MinValue_, MaxValue_):
            self.ColumnName = ColumnName_
            self.MinValue = MinValue_
            self.MaxValue = MaxValue_

    EXPECTED_DETECTION_COL_RANGES = [ColumnRange("ra", "0", "360"),
                                     ColumnRange("\"dec\"", "-90", "90"),
                                     ColumnRange("raErr", "-2000", "9"),
                                     ColumnRange("decErr", "0", "9"),]
