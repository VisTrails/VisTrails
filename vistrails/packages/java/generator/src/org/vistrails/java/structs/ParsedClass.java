package org.vistrails.java.structs;

import java.util.Collections;
import java.util.List;

public class ParsedClass {

    public class Modifiers {
        public static final int
                PUBLIC      = 0x01,
                PRIVATE     = 0x02,
                PROTECTED   = 0x04,
                STATIC      = 0x08,
                ABSTRACT    = 0x10,
                TEMPLATE    = 0x20;
    }

    public final String fullname;
    public final List<ParsedConstructor> constructors;
    public final List<ParsedMethod> methods;
    public final boolean template;
    public final String filename;
    public final int lineno;

    public ParsedClass(String name,
            List<ParsedConstructor> constructors, List<ParsedMethod> methods,
            int modifiers, String filename, int lineno)
    {
        this.fullname = name;
        this.constructors = Collections.unmodifiableList(constructors);
        this.methods = Collections.unmodifiableList(methods);
        this.template = (modifiers & Modifiers.TEMPLATE) != 0;
        this.filename = filename;
        this.lineno = lineno;
    }

    public ParsedClass(String name,
            List<ParsedConstructor> constructors, List<ParsedMethod> methods,
            int modifiers)
    {
        this(name, constructors, methods, modifiers, null, 0);
    }

}
