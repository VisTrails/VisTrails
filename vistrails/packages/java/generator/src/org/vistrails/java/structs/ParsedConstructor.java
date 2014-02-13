package org.vistrails.java.structs;

import java.util.Collections;
import java.util.List;

public class ParsedConstructor {

    public final int modifiers;
    public final List<ParsedParam> parameters;

    public ParsedConstructor(int modifiers, List<ParsedParam> parameters)
    {
        this.modifiers = modifiers;
        this.parameters = Collections.unmodifiableList(parameters);
    }

}
