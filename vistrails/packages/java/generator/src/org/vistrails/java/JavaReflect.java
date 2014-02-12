package org.vistrails.java;

import java.io.File;
import java.io.IOException;
import java.lang.reflect.Constructor;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.URLClassLoader;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;

import org.vistrails.java.structs.ParsedClass;
import org.vistrails.java.structs.ParsedMethod;
import org.vistrails.java.structs.ReadClass;
import org.vistrails.java.structs.ReadConstructor;
import org.vistrails.java.structs.ReadMethod;
import org.vistrails.java.structs.ReadParam;

/**
 * This reads the .class files of a JAR through java.lang.reflect.
 *
 * This builds the actual list of classes/methods that we'll write to disk. It
 * uses the parameter names from the sources if provided, else generates
 * generic names (arg0, arg1, ...).
 */
public class JavaReflect {

    private Map<String, ParsedClass> sources;
    private Map<String, ReadClass> classes;

    public static final String OK = "ok";
    public static final String OK_NO_PARAM_NAME =
            "parameter names not available";

    public static String format_type(Class<?> t)
    {
        if(!t.isArray())
            return t.getName();
        else
            return format_type(t.getComponentType()) + "[]";
    }

    private JavaReflect(Map<String, ParsedClass> parsed_classes)
    {
        sources = parsed_classes;
        classes = new HashMap<String, ReadClass>();
    }

    private String process(Class<?> c)
    {
        String status = OK;

        // We are not interested in interfaces
        // FIXME : Aren't we? What about getters?
        if(c.isInterface())
            return "skipped (interface)";

        // Get the class info that was retrieved from the sources
        ParsedClass sourceClass = null;
        if(sources != null)
        {
            sourceClass = sources.get(c.getName());
            if(sourceClass != null && sourceClass.template)
                return "skipped (template)";
        }

        // TODO : Nested classes are currently ignored

        // Find the superclass
        String superclass = c.getSuperclass().getName();
        if(superclass.startsWith("java."))
            superclass = null;

        // Read the methods
        List<ReadMethod> readMethods = new LinkedList<ReadMethod>();

        for(Method m : c.getDeclaredMethods())
        {
            int mods = m.getModifiers();
            if(Modifier.isAbstract(mods) ||
                    !Modifier.isPublic(mods))
                continue;
            List<ReadParam> readParams = new LinkedList<ReadParam>();
            Class<?>[] params = m.getParameterTypes();

            // Find the parameter names from the parsed source
            String[] paramNames = null;
            if(sourceClass != null)
            {
                int nb_params = m.getParameterTypes().length;
                for(ParsedMethod sourceMethod : sourceClass.methods)
                {
                    if(sourceMethod.name.equals(m.getName()) &&
                            sourceMethod.parameters.length == nb_params)
                    {
                        paramNames = sourceMethod.parameters;
                        break;
                    }
                }
            }
            if(paramNames == null)
            {
                status = OK_NO_PARAM_NAME;
                paramNames = new String[params.length];
                for(int i = 0; i < params.length; ++i)
                    paramNames[i] = String.format("arg%d", i);
            }

            for(int i = 0; i < params.length; ++i)
                readParams.add(new ReadParam(params[i], paramNames[i]));

            readMethods.add(new ReadMethod(
                    m.getName(),
                    Modifier.isStatic(mods),
                    format_type(m.getReturnType()),
                    readParams));
        }

        // Read the constructors
        List<ReadConstructor> readConstructors = new LinkedList<ReadConstructor>();

        for(Constructor<?> m : c.getConstructors())
        {
            int mods = m.getModifiers();
            if(!Modifier.isPublic(mods))
                continue;
            List<ReadParam> readParams = new LinkedList<ReadParam>();
            Class<?>[] params = m.getParameterTypes();

            // Find the parameter names from the parsed source
            String[] paramNames = null;
            if(sourceClass != null)
            {
                int nb_params = m.getParameterTypes().length;
                for(ParsedMethod sourceMethod : sourceClass.methods)
                {
                    if(sourceMethod.name.equals(m.getName()) &&
                            sourceMethod.parameters.length == nb_params)
                    {
                        paramNames = sourceMethod.parameters;
                        break;
                    }
                }
            }
            if(paramNames == null)
            {
                status = OK_NO_PARAM_NAME;
                paramNames = new String[params.length];
                for(int i = 0; i < params.length; ++i)
                    paramNames[i] = String.format("arg%d", i);
            }

            for(int i = 0; i < params.length; ++i)
                readParams.add(new ReadParam(params[i], paramNames[i]));

            readConstructors.add(new ReadConstructor(readParams));
        }

        ReadClass readClass = new ReadClass(
                c.getName(),
                superclass,
                Modifier.isAbstract(c.getModifiers()),
                readMethods,
                readConstructors);

        classes.put(readClass.fullname, readClass);

        return status;
    }

    /**
     * Generates the list of classes from a JAR file.
     *
     * @param jar_filename Filename of the JAR to read.
     * @param parsed_classes Information obtained from reading the sources, or
     * null.
     */
    public static Map<String, ReadClass> parse_jar(
            String jar_filename,
            Map<String, ParsedClass> parsed_classes) throws IOException
    {
        URL url = null;
        try {
            url = new File(jar_filename).toURI().toURL();
        }
        catch(MalformedURLException e1)
        {
            assert false;
        }
        URLClassLoader classLoader = new URLClassLoader(
                new URL[] {url},
                JavaReflect.class.getClassLoader());
        JavaReflect analyzer;
        try {
            analyzer = new JavaReflect(parsed_classes);

            Map<String, Integer> statuses = new HashMap<String, Integer>();
            for(String classname : JarUtils.list_classes(jar_filename))
            {
                String status;
                try {
                    Class<?> c = Class.forName(classname, true, classLoader);
                    status = analyzer.process(c);
                }
                catch(ClassNotFoundException e)
                {
                    e.printStackTrace();
                    status = "error";
                }

                Integer count = statuses.get(status);
                if(count == null)
                    statuses.put(status, 1);
                else
                    statuses.put(status, count + 1);
            }

            System.out.println("Done reading classes in JAR. Results:");
            for(Entry<String, Integer> entry : statuses.entrySet())
            {
                System.out.println(String.format(
                        "  %s: %d",
                        entry.getKey(), entry.getValue()));
            }
        }
        finally
        {
            classLoader.close();
        }

        return analyzer.classes;
    }

}
