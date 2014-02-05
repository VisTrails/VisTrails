package org.vistrails.java.structs;


public class ParsedMethod {

    public final String name;
    public final String[] parameters;

    public ParsedMethod(String name, String[] parameters)
    {
        this.name = name;
        this.parameters = parameters;
    }

}
