package org.vistrails.java.structs;

public class ParsedParam {

    public final String type;
    public final String name;
    public final int modifiers;

    public ParsedParam(String type, String name, int modifiers)
    {
        this.type = type;
        this.name = name;
        this.modifiers = modifiers;
    }

}
