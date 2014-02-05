package org.vistrails.java;

import java.util.ArrayList;

/**
 * Base class for command-line parsing.
 *
 * Subclass this to your application's need.
 */
public abstract class OptionsParser {

    public class Error extends Exception {
        public Error()
        {
            super("Unspecified error");
        }
        public Error(String msg)
        {
            super(msg);
        }
    }

    public class EndOfArguments extends Error {
        public EndOfArguments()
        {
            super("Premature end of parameters");
        }
    }

    public class InvalidArgument extends Error {
        public InvalidArgument()
        {
            super("Invalid argument");
        }
    }

    private String usage;
    private String[] args;
    private int i;
    protected boolean options_ended;
    protected ArrayList<String> parameters;
    protected int nb_parameters = 0;

    public OptionsParser(String usage)
    {
        this.usage = usage;
    }

    public boolean parse(String[] args)
    {
        this.args = args;
        i = 0;
        options_ended = false;
        try {
            while(true)
            {
                String arg;
                try {
                    arg = readArgument();
                }
                catch(EndOfArguments e)
                {
                    break;
                }
                handleArg(arg);
            }
            validate();
            return true;
        }
        catch(Error e)
        {
            System.err.println(
                    "Error while parsing command line: " +
                    e.getMessage() + "\n");
            System.err.println(usage);
            return false;
        }
    }

    protected String readArgument() throws EndOfArguments
    {
        if(i >= args.length)
            throw new EndOfArguments();
        return args[i++];
    }

    protected int readInt() throws EndOfArguments, InvalidArgument
    {
        try {
            return Integer.parseInt(readArgument());
        }
        catch(NumberFormatException e)
        {
            throw new InvalidArgument();
        }
    }

    protected float readFloat() throws EndOfArguments, InvalidArgument
    {
        try {
            return Float.parseFloat(readArgument());
        }
        catch(NumberFormatException e)
        {
            throw new InvalidArgument();
        }
    }

    protected void handleArg(String arg) throws Error
    {
        if(options_ended)
            handleParameter(arg, nb_parameters++);
        else
        {
            if(arg.equals("--"))
                options_ended = true;
            else if(arg.charAt(0) == '-')
                handleOption(arg);
            else
                handleParameter(arg, nb_parameters++);
        }
    }

    protected void validate() throws Error
    {
    }

    protected abstract void handleParameter(String param, int nb) throws Error;
    protected abstract void handleOption(String opt) throws Error;

}
