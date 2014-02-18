package org.vistrails.java.sourceparser;

public class Lexer {

    public static class Token {

        enum Type {
            OPERATOR,
            IDENTIFIER,
            STRING_LITERAL,
            NUMBER_LITERAL
        }

        public final Type type;
        public final String text;

        public Token(Type type, String text)
        {
            this.type = type;
            this.text = text;
        }

        public Token(Type type)
        {
            this.type = type;
            this.text = null;
        }

        @Override
        public boolean equals(Object other)
        {
            Token other_ = (Token)other;
            if(other_ == null)
                return false;
            return type == other_.type &&
                   ((text == null && other_.text == null) ||
                    (text != null && text.equals(other_.text)));
        }

    }

    private TextReader reader;
    private int stored = -1;

    public Lexer(TextReader reader)
    {
        this.reader = reader;
    }

    public int lineNumber()
    {
        return reader.lineNumber();
    }

    private char read() throws EndOfStream
    {
        if(stored != -1)
        {
            char c = (char)stored;
            stored = -1;
            return c;
        }
        else
            return reader.read();
    }

    private void unread(char c)
    {
        assert stored == -1;
        stored = c;
    }

    private void skip_multiline_comment() throws EndOfStream
    {
        char c = read();
        boolean last_star = false;
        while(true)
        {
            if(c == '*')
                last_star = true;
            else if(c == '/' && last_star)
                return;
            else
                last_star = false;
            c = read();
        }
    }

    private void skip_line() throws EndOfStream
    {
        char c = read();
        while(true)
        {
            if(c == '\n')
                return ; // UNIX end-of-line (LF)
            else if(c == '\r')
            {
                char n = read();
                if(n == '\n')
                    return ; // Windows end-of-line (CR+LF)
                else
                {
                    unread(n);
                    return ; // Mac end-of-line (CR)
                }
            }
            c = read();
        }
    }

    private boolean char_is_whitespace(char c)
    {
        return c == ' ' || c == '\t' ||
               c == '\n' || c == '\r';
    }

    private boolean char_is_identifier(char c, boolean first)
    {
        return ('a' <= c && c <= 'z') ||
               ('A' <= c && c <= 'Z') ||
               c == '_' || c == '$' ||
               (!first && ('0' <= c && c <= '9'));
    }

    private boolean char_is_numeric(char c, boolean first)
    {
        return ('0' <= c && c <= '9') || c == '.' ||
                (!first && (('a' <= c && c <= 'z') ||
                            ('A' <= c && c <= 'Z')));
    }

    public Token next_token() throws EndOfStream
    {
        char c = read();
        while(true)
        {
            if(char_is_whitespace(c))
                ;
            else if(c == '"' || c == '\'')
            {
                char n = read();
                while(n != c)
                {
                    if(n == '\\')
                        read(); // discard one character
                    n = read();
                }
                return new Token(Token.Type.STRING_LITERAL);
            }
            else if(c == '/')
            {
                char n = read();
                if(n == '*')
                    skip_multiline_comment();
                else if(n == '/')
                    skip_line();
                else
                {
                    unread(n);
                    return new Token(Token.Type.OPERATOR);
                }
            }
            else if(char_is_identifier(c, true))
            {
                StringBuilder word = new StringBuilder();
                word.append(c);
                c = read();
                while(char_is_identifier(c, false))
                {
                    word.append(c);
                    c = read();
                }
                unread(c);
                String word_ = word.toString();
                return new Token(Token.Type.IDENTIFIER, word_);
            }
            else if(c == '.')
            {
                // Ambiguity: this can be in a number literal or by itself
                char n = read();
                if(char_is_numeric(n, true))
                {
                    n = read();
                    while(char_is_numeric(n, false))
                        n = read();
                    unread(n);
                    return new Token(Token.Type.NUMBER_LITERAL);
                }
                else
                {
                    unread(n);
                    return new Token(Token.Type.OPERATOR, ".");
                }
            }
            else if(char_is_numeric(c, true))
            {
                c = read();
                while(char_is_numeric(c, false))
                    c = read();
                unread(c);
                return new Token(Token.Type.NUMBER_LITERAL);
            }
            else
                return new Token(Token.Type.OPERATOR, Character.toString(c));
            c = read();
        }
    }

}
