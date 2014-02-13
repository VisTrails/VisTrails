package org.vistrails.java.sourceparser;

public class UnexpectedToken extends ParserError {

    public UnexpectedToken(String token, int lineno)
    {
        super("Unexpected token " + token, lineno);
    }

}
