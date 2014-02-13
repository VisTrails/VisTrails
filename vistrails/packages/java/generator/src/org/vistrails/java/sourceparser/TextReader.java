package org.vistrails.java.sourceparser;

import java.io.BufferedReader;
import java.io.Closeable;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.Reader;

public class TextReader implements Closeable {

    private Reader reader;
    private int lineno = 1;
    private boolean last_cr = false;

    public TextReader(InputStream stream)
    {
        this.reader = new BufferedReader(new InputStreamReader(stream));
    }

    public char read() throws EndOfStream
    {
        int res;
        try {
            res = reader.read();
        }
        catch(IOException e)
        {
            throw new EndOfStream(lineno);
        }
        if(res == -1)
            throw new EndOfStream(lineno);
        char c = (char)res;
        if(c == '\r' || (c == '\n' && !last_cr))
            lineno++;
        last_cr = c == '\r';
        return c;
    }

    @Override
    public void close() throws IOException
    {
        reader.close();
    }

    public int lineNumber()
    {
        return lineno;
    }

}
