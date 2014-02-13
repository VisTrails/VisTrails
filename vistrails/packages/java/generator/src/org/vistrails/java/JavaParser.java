package org.vistrails.java;

import java.io.IOException;
import java.io.InputStream;
import java.util.HashMap;
import java.util.Map;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;

import org.vistrails.java.sourceparser.Lexer;
import org.vistrails.java.sourceparser.Parser;
import org.vistrails.java.sourceparser.TextReader;
import org.vistrails.java.structs.ParsedClass;

/**
 * This reads Java source files.
 *
 * It is the only way to get the parameter names that we need. It is a very
 * simplified Java parsed since it does not need to read Java code (i.e.
 * statements), only declarations).
 */
public class JavaParser {

    private JavaParser()
    {
    }

    /**
     * Generates the list of classes
     *
     * @param jar_filename Filename of the JAR to read.
     * @param src_prefix Prefix of the source files in the JAR, e.g. "src/".
     */
    public static Map<String, ParsedClass> parse_jar(
            String jar_filename, String src_prefix) throws IOException
    {
        Map<String, ParsedClass> parsed_classes =
                new HashMap<String, ParsedClass>();

        if(src_prefix.length() > 0 && src_prefix.charAt(src_prefix.length() - 1) != '/')
            src_prefix = src_prefix + '/';

        ZipFile jar = new ZipFile(jar_filename);
        for(ZipEntry entry : JarUtils.list_files(jar, src_prefix))
        {
            String filename = entry.getName();
            if(!filename.endsWith(".java") || filename.contains("$"))
                continue;

            InputStream fp = jar.getInputStream(entry);
            TextReader reader = new TextReader(fp);
            Lexer lexer = new Lexer(reader);
            Parser parser = new Parser(lexer, filename.substring(src_prefix.length()));
            ParsedClass clasz = null;
            try {
                clasz = parser.parse();
            }
            catch(Exception e)
            {
                System.err.println(String.format(
                        "Couldn't parse %s from the sources: %s",
                        filename,
                        e.toString()));
            }
            finally
            {
                reader.close();
            }
            if(clasz != null)
            {
                ParsedClass prev = parsed_classes.get(clasz.fullname);
                if(prev != null)
                {
                    System.err.println(String.format(
                            "Found duplicate class %s:\n" +
                            "  %s line %d\n" +
                            "  %s line %d",
                            clasz.fullname,
                            clasz.filename, clasz.lineno,
                            prev.filename, prev.lineno));
                }
                else
                    parsed_classes.put(clasz.fullname, clasz);
            }
        }
        jar.close();
        if(parsed_classes.isEmpty())
            return null;
        return parsed_classes;
    }

}
