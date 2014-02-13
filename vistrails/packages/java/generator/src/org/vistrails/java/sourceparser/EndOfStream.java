package org.vistrails.java.sourceparser;

public class EndOfStream extends ParserError {

    public EndOfStream(int lineno)
    {
        super("Unexpected end of stream", lineno);
    }

}
