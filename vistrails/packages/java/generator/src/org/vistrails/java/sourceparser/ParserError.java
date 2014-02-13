package org.vistrails.java.sourceparser;

public class ParserError extends Exception {

    public ParserError(String msg, int lineno)
    {
        super(msg + ((lineno != 0)?
                (" (line " + lineno + ")"):
                ""));
    }

}
