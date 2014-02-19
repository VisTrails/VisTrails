package org.vistrails.java;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.io.UnsupportedEncodingException;
import java.util.Map;

import javax.xml.stream.XMLOutputFactory;
import javax.xml.stream.XMLStreamException;
import javax.xml.stream.XMLStreamWriter;

import org.vistrails.java.structs.PackageInfos;
import org.vistrails.java.structs.ParsedClass;
import org.vistrails.java.structs.ReadClass;

/**
 * Entry point of the application.
 *
 * Reads the command-line and calls JavaParser and JavaReflect, then writes an
 * XML file to disk.
 */
public class ClassReader {

    private static class CLI extends OptionsParser {

        CLI()
        {
            super("Usage: ClassReader [options] <jar_file>\n" +
                  "\n" +
                  "Options:\n" +
                  "  -s src_prefix: path to root of source files in the " +
                  "JAR\n" +
                  "  -o output_xml: path to the XML file to be written\n" +
                  "  -S src_jar: path to the JAR files containing the " +
                  "sources, if different");
        }

        String jar_filename = null;
        String src_prefix = null;
        String output_xml = null;
        String src_jar_filename = null;

        @Override
        protected void handleOption(String opt) throws Error
        {
            if(src_prefix == null && opt.equals("-s"))
                src_prefix = readArgument();
            else if(output_xml == null && opt.equals("-o"))
                output_xml = readArgument();
            else if(src_jar_filename == null && opt.equals("-S"))
                src_jar_filename = readArgument();
            else
                throw new Error();
        }

        @Override
        protected void handleParameter(String param, int nb) throws Error
        {
            if(nb == 0)
                jar_filename = param;
            else
                throw new Error();
        }

        @Override
        protected void validate() throws Error
        {
            if(nb_parameters != 1)
                throw new Error();
        }

    }

    public static void main(String[] args)
    {
        CLI cli = new CLI();
        if(!cli.parse(args))
            System.exit(1);

        Map<String, ReadClass> classes = null;

        try {
            // Parse Java source code, to find parameter names
            // This is optional, but if not present, parameters will be numbered
            // (e.g. arg0, arg1, ...)
            Map<String, ParsedClass> parsed_classes = null;
            if(cli.src_jar_filename != null && cli.src_prefix == null)
                cli.src_prefix = "";
            if(cli.src_jar_filename == null)
                cli.src_jar_filename = cli.jar_filename;
            if(cli.src_prefix != null)
                parsed_classes = JavaParser.parse_jar(cli.src_jar_filename,
                                                      cli.src_prefix);
            if(parsed_classes == null)
                System.err.println("Reading JAR without sources; parameter " +
                                   "names won't be available");

            // Use Java reflection to discover classes and methods
            classes = JavaReflect.parse_jar(
                    cli.jar_filename,
                    parsed_classes);
        }
        catch(IOException e)
        {
            System.err.println("Got an exception reading the JAR:");
            e.printStackTrace();
            System.exit(2);
        }

        PackageInfos package_infos = new PackageInfos(classes);

        String output_xml = cli.output_xml;
        if(output_xml == null)
            output_xml = new File(cli.jar_filename).getName() + ".xml";

        try {
            OutputStream stream = new FileOutputStream(output_xml);
            XMLOutputFactory outf = XMLOutputFactory.newInstance();
            XMLStreamWriter out = outf.createXMLStreamWriter(
                    new OutputStreamWriter(stream, "utf-8"));
            out.writeStartDocument("utf-8", "1.0");
            package_infos.write_xml(out);
            out.writeEndDocument();
            out.close();
        }
        catch(FileNotFoundException e)
        {
            System.err.println("Output path is not valid");
            System.exit(1);
        }
        catch(UnsupportedEncodingException e)
        {
            System.err.println("XML lib doesn't support UTF-8");
            System.exit(2);
        }
        catch(XMLStreamException e)
        {
            System.err.println("Error writing XML:");
            e.printStackTrace();
            System.exit(2);
        }
    }

}
