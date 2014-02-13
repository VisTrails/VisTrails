package org.vistrails.java;

import java.io.IOException;
import java.util.Enumeration;
import java.util.Iterator;
import java.util.NoSuchElementException;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;

public final class JarUtils {

    private static class JarClassIterator implements Iterator<String> {

        private Enumeration<? extends ZipEntry> entries;
        private String next_entry;

        JarClassIterator(ZipFile zipfile)
        {
            entries = zipfile.entries();
            next_entry = null;
            advance();
        }

        @Override
        public boolean hasNext()
        {
            return next_entry != null;
        }

        @Override
        public String next()
        {
            if(next_entry == null)
                throw new NoSuchElementException();
            String res = next_entry;
            advance();
            return res;
        }

        @Override
        public void remove()
        {
            throw new UnsupportedOperationException();
        }

        private void advance()
        {
            while(true)
            {
                try {
                    next_entry = entries.nextElement().getName();
                }
                catch(NoSuchElementException e)
                {
                    next_entry = null;
                    return ;
                }
                if(!next_entry.endsWith(".class"))
                    continue;
                next_entry = next_entry.substring(0, next_entry.length() - 6)
                                       .replace('/', '.');
                if(next_entry.contains("$"))
                    continue;

                return ;
            }
        }

    }

    /**
     * Object that enumerates the classes in a JAR file.
     */
    private static class JarClassList implements Iterable<String> {

        private ZipFile zipfile;

        public JarClassList(String filename) throws IOException
        {
            zipfile = new ZipFile(filename);
        }

        @Override
        public Iterator<String> iterator()
        {
            return new JarClassIterator(zipfile);
        }

    }

    private static class JarFileIterator implements Iterator<ZipEntry> {

        private Enumeration<? extends ZipEntry> entries;
        private ZipEntry next_entry;
        private String prefix;

        public JarFileIterator(ZipFile zipfile, String prefix)
        {
            entries = zipfile.entries();
            if(!prefix.endsWith("/"))
                prefix = prefix + '/';
            this.prefix = prefix;
            next_entry = null;
            advance();
        }

        @Override
        public boolean hasNext()
        {
            return next_entry != null;
        }

        @Override
        public ZipEntry next()
        {
            if(next_entry == null)
                throw new NoSuchElementException();
            ZipEntry res = next_entry;
            advance();
            return res;
        }

        @Override
        public void remove()
        {
            throw new UnsupportedOperationException();
        }

        private void advance()
        {
            while(true)
            {
                try {
                    next_entry = entries.nextElement();
                }
                catch(NoSuchElementException e)
                {
                    next_entry = null;
                    return ;
                }
                if(next_entry.isDirectory())
                    continue;
                if(!next_entry.getName().startsWith(prefix))
                    continue;

                return ;
            }
        }

    }

    /**
     * Object that enumerates the files in a JAR.
     */
    private static class JarFileList implements Iterable<ZipEntry> {

        private ZipFile zipfile;
        private String prefix;

        public JarFileList(ZipFile zipfile, String prefix) throws IOException
        {
            this.zipfile = zipfile;
            this.prefix = prefix;
        }

        public JarFileList(String filename, String prefix) throws IOException
        {
            this(new ZipFile(filename), prefix);
        }

        @Override
        public Iterator<ZipEntry> iterator()
        {
            return new JarFileIterator(zipfile, prefix);
        }

    }

    private JarUtils()
    {}

    public static JarClassList list_classes(String filename) throws IOException
    {
        return new JarClassList(filename);
    }

    public static Iterable<ZipEntry> list_files(String filename)
            throws IOException
    {
        return new JarFileList(filename, "");
    }

    public static Iterable<ZipEntry> list_files(String filename, String prefix)
            throws IOException
    {
        return new JarFileList(filename, prefix);
    }

    public static Iterable<ZipEntry> list_files(ZipFile zipfile)
            throws IOException
    {
        return new JarFileList(zipfile, "");
    }

    public static Iterable<ZipEntry> list_files(ZipFile zipfile, String prefix)
            throws IOException
    {
        return new JarFileList(zipfile, prefix);
    }

}
