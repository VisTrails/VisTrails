package edu.utah.sci.vistrails.javaspreadsheet;


public interface CellInfos {

    public String getVistrail();

    public int getVersion();

    public int getModule();

    public String getReason();

    // This is a hack used to associate private VisTrails data with this
    // structure
    public int getInternalID();

}
