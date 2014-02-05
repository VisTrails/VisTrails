package org.vistrails.java;

import java.io.IOException;
import java.util.Map;

import org.vistrails.java.structs.ParsedClass;

/**
 * This reads Java source files.
 *
 * It is the only way to get the parameter names that we need. It is a very
 * simplified Java parsed since it does not need to read Java code (i.e.
 * statements), only declarations).
 */
public class JavaParser {

    /**
     * Generates the list of classes
     *
     * @param jar_filename Filename of the JAR to read.
     * @param src_prefix Prefix of the source files in the JAR, e.g. "src/".
     */
    public static Map<String, ParsedClass> parse_jar(
            String jar_filename, String src_prefix) throws IOException
    {
        // TODO Auto-generated method stub
        return null;
    }

}
