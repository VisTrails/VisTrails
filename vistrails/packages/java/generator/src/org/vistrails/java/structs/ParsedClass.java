package org.vistrails.java.structs;

import java.util.List;

public class ParsedClass {

    public final String fullname;
    public final List<ParsedMethod> methods;
    public final boolean template;

    public ParsedClass(String name, List<ParsedMethod> methods,
            boolean template)
    {
        this.fullname = name;
        this.methods = methods;
        this.template = template;
    }

}
