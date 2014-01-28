package edu.utah.sci.vistrails.javaspreadsheet;

import java.awt.Point;


public interface SpreadsheetInterface {

    boolean executePipelineToCell(CellInfos infos, String dst_sheet,
            Point dst_loc);

    boolean select_version(CellInfos infos);

}
