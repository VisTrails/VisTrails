package org.vistrails.java.sourceparser;

import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.vistrails.java.sourceparser.Lexer.Token;
import org.vistrails.java.structs.ParsedClass;
import org.vistrails.java.structs.ParsedClass.Modifiers;
import org.vistrails.java.structs.ParsedConstructor;
import org.vistrails.java.structs.ParsedMethod;
import org.vistrails.java.structs.ParsedParam;

public class Parser {

    /* ******************************
     * Keywords
     */

    private static final Token END_STATEMENT =
            new Token(Token.Type.OPERATOR, ";");
    private static final Token BEGIN_BLOCK =
            new Token(Token.Type.OPERATOR, "{");
    private static final Token END_BLOCK =
            new Token(Token.Type.OPERATOR, "}");
    private static final Token BEGIN_TEMPLATE =
            new Token(Token.Type.OPERATOR, "<");
    private static final Token END_TEMPLATE =
            new Token(Token.Type.OPERATOR, ">");
    private static final Token DOT =
            new Token(Token.Type.OPERATOR, ".");
    private static final Token COMMA =
            new Token(Token.Type.OPERATOR, ",");
    private static final Token ANNOTATION =
            new Token(Token.Type.OPERATOR, "@");
    private static final Token PACKAGE_STATEMENT =
            new Token(Token.Type.IDENTIFIER, "package");
    private static final Token IMPORT_STATEMENT =
            new Token(Token.Type.IDENTIFIER, "import");
    private static final Token CLASS_DEFINITION =
            new Token(Token.Type.IDENTIFIER, "class");
    private static final Token INTERFACE_DEFINITION =
            new Token(Token.Type.IDENTIFIER, "interface");
    private static final Token THROWS_SPECIFIER =
            new Token(Token.Type.IDENTIFIER, "throws");
    private static final Token OPEN_PAREN =
            new Token(Token.Type.OPERATOR, "(");
    private static final Token CLOSE_PAREN =
            new Token(Token.Type.OPERATOR, ")");
    private static final Token ARRAY_LEFT =
            new Token(Token.Type.OPERATOR, "[");
    private static final Token ARRAY_RIGHT =
            new Token(Token.Type.OPERATOR, "]");

    private Lexer lexer;
    private Token stored;
    private String filename;
    private String expected_classname;
    private String expected_pkgname;
    private String pkgname = null;

    public Parser(Lexer lexer, String filename)
    {
        this.lexer = lexer;
        this.filename = filename;
        String fullname = filename
                .substring(0, filename.length() - 5)
                .replace('/', '.');
        int pos = fullname.lastIndexOf('.');
        if(pos == -1)
        {
            expected_classname = fullname;
            expected_pkgname = null;
        }
        else
        {
            expected_classname = fullname.substring(pos + 1);
            expected_pkgname = fullname.substring(0, pos);
        }
    }

    private int lineNumber()
    {
        return lexer.lineNumber();
    }

    /* ******************************
     * Reading tokens from the lexer
     * */

    private void store_token(Token t)
    {
        assert stored == null;
        stored = t;
    }

    private Token next_token() throws EndOfStream
    {
        if(stored != null)
        {
            Token res = stored;
            stored = null;
            return res;
        }
        else
            return lexer.next_token();
    }

    private Token next_token(Token.Type type) throws ParserError
    {
        Token t = next_token();
        if(t.type != type)
            throw unexpected(t);
        return t;
    }

    private void next_token(Token expected) throws ParserError
    {
        Token t = next_token();
        if(!t.equals(expected))
            throw unexpected(t);
    }

    /* ******************************
     * Modifiers for classes/methods/fields
     */

    private static Map<String, Integer> MODIFIERS =
            new HashMap<String, Integer>();
    static {
        MODIFIERS.put("public", Modifiers.PUBLIC);
        MODIFIERS.put("private", Modifiers.PRIVATE);
        MODIFIERS.put("protected", Modifiers.PROTECTED);
        MODIFIERS.put("static", Modifiers.STATIC);
        MODIFIERS.put("abstract", Modifiers.ABSTRACT);
        MODIFIERS.put("final", 0);
        MODIFIERS.put("native", 0);
        MODIFIERS.put("synchronized", 0);
        MODIFIERS.put("transient", 0);
        MODIFIERS.put("volatile", 0);
    }

    private boolean is_modifier(Token t)
    {
        return (t.type == Token.Type.IDENTIFIER &&
                MODIFIERS.containsKey(t.text));
    }

    /* ******************************
     * Skipping uninteresting sections
     */

    private void skip_statement() throws EndOfStream
    {
        // A statement goes until a ';'
        // It might contain blocks, Because of anonymous classes
        Token t = next_token();
        int depth = 0;
        while(depth > 0 || !t.equals(END_STATEMENT))
        {
            if(t.equals(BEGIN_BLOCK))
                depth++;
            else if(t.equals(END_BLOCK))
                depth--;
            t = next_token();
        }
    }

    private void skip_block() throws EndOfStream
    {
        skip_block(1);
    }

    private void skip_block(int depth) throws EndOfStream
    {
        while(true)
        {
            Token t = next_token();
            if(t.equals(BEGIN_BLOCK))
                depth++;
            else if(t.equals(END_BLOCK))
            {
                depth--;
                if(depth == 0)
                    return ;
            }
        }
    }

    private void skip_template_declaration() throws EndOfStream
    {
        skip_template_declaration(1);
    }

    private void skip_template_declaration(int depth) throws EndOfStream
    {
        while(depth > 0)
        {
            Token t = next_token();
            if(t.equals(BEGIN_TEMPLATE))
                depth++;
            else if(t.equals(END_TEMPLATE))
                depth--;
        }
    }

    private void skip_annotation() throws ParserError
    {
        next_token(Token.Type.IDENTIFIER);
        Token t = next_token();
        while(true)
        {
            if(t.equals(DOT))
                next_token(Token.Type.IDENTIFIER);
            else if(t.equals(OPEN_PAREN))
            {
                Token t2 = next_token();
                while(!t2.equals(CLOSE_PAREN))
                    t2 = next_token();
                return ;
            }
            else
            {
                store_token(t);
                return ;
            }
            t = next_token();
        }
    }

    /* ******************************
     * Parsing
     */

    /**
     * Parses an absolute name, e.g. dot-separated identifiers.
     */
    private String parse_qualifiedname() throws ParserError
    {
        StringBuilder name = new StringBuilder();
        Token t = next_token(Token.Type.IDENTIFIER);
        name.append(t.text);
        t = next_token();
        while(!t.equals(END_STATEMENT))
        {
            if(!t.equals(DOT))
                throw new ParserError("Invalid qualified name", lineNumber());
            t = next_token(Token.Type.IDENTIFIER);
            name.append('.');
            name.append(t.text);
            t = next_token();
        }
        return name.toString();
    }

    /**
     * Parses a type name.
     */
    private String parse_type(Token t) throws ParserError
    {
        assert t.type == Token.Type.IDENTIFIER;
        StringBuilder type = new StringBuilder(t.text);
        t = next_token();
        while(true)
        {
            if(t.equals(DOT))
            {
                type.append('.');
                type.append(next_token(Token.Type.IDENTIFIER).text);
            }
            else if(t.equals(BEGIN_TEMPLATE))
                skip_template_declaration();
            else if(t.equals(ARRAY_LEFT))
                next_token(ARRAY_RIGHT);
            else
            {
                store_token(t);
                return type.toString();
            }
            t = next_token();
        }
    }

    /**
     * Entry point of the parser. Parses a Java file.
     */
    public ParsedClass parse() throws ParserError
    {
        Token t = next_token();
        while(true)
        {
            if(t.equals(PACKAGE_STATEMENT))
            {
                if(pkgname != null)
                    throw new ParserError("Two package declarations",
                                          lineNumber());
                pkgname  = parse_qualifiedname();
                if(!pkgname.equals(expected_pkgname))
                    throw new ParserError("Package name mismatch",
                                          lineNumber());
            }
            else if(t.equals(IMPORT_STATEMENT))
                parse_qualifiedname(); // Discard that
            else if(t.equals(ANNOTATION))
                skip_annotation();
            else if(is_modifier(t))
            {
                int modifiers = MODIFIERS.get(t.text);
                Token t2 = next_token(Token.Type.IDENTIFIER);
                while(!t2.equals(CLASS_DEFINITION) &&
                      !t2.equals(INTERFACE_DEFINITION))
                {
                    modifiers |= MODIFIERS.get(t2.text);
                    t2 = next_token(Token.Type.IDENTIFIER);
                }
                String classname = next_token(Token.Type.IDENTIFIER).text;
                if(!classname.equals(expected_classname))
                    skip_block(0);
                else if(t2.equals(INTERFACE_DEFINITION))
                    return null; // It's an interface; skip
                else
                    return parse_class(classname, modifiers);
                modifiers = 0;
            }
            else if(t.equals(CLASS_DEFINITION) ||
                    t.equals(INTERFACE_DEFINITION))
            {
                String classname = next_token(Token.Type.IDENTIFIER).text;
                if(!classname.equals(expected_classname))
                    skip_block(0);
                else if(t.equals(INTERFACE_DEFINITION))
                    return null; // It's an interface; skip
                return parse_class(classname, 0);
            }
            else
                throw unexpected(t);
            t = next_token();
        }
    }

    private static final Set<String> IGNORED_INNER_STRUCTS =
            new HashSet<String>(Arrays.asList(new String[]{
                    "enum",
                    "class",
                    "interface"
            }));

    /**
     * Parses a class.
     *
     * Starts after the class name, i.e. the modifiers, 'class' keyword and
     * name have already been read.
     */
    private ParsedClass parse_class(String classname, int class_modifiers)
            throws ParserError
    {
        // Skips 'extends' and 'implements' declarations
        Token t = next_token();
        if(t.equals(BEGIN_TEMPLATE))
        {
            skip_template_declaration();
            class_modifiers |= Modifiers.TEMPLATE;
        }
        while(!t.equals(BEGIN_BLOCK))
        {
            if(!t.equals(COMMA) && t.type != Token.Type.IDENTIFIER)
                throw unexpected(t);
            t = next_token();
        }

        int modifiers = 0;
        List<ParsedConstructor> constructors =
                new LinkedList<ParsedConstructor>();
        List<ParsedMethod> methods = new LinkedList<ParsedMethod>();
        t = next_token();
        while(true)
        {
            if(t.equals(END_BLOCK))
                break;
            else if(t.equals(ANNOTATION))
                skip_annotation();
            else if(t.equals(END_STATEMENT))
                ;
            else if(t.equals(BEGIN_BLOCK))
            {
                modifiers = 0;
                skip_block();
            }
            else if(t.equals(CLASS_DEFINITION) ||
                    t.equals(INTERFACE_DEFINITION))
                skip_block(0);
            else if(is_modifier(t))
                modifiers |= MODIFIERS.get(t.text);
            else if(t.type == Token.Type.IDENTIFIER)
            {
                if(!IGNORED_INNER_STRUCTS.contains(t.text))
                {
                    /* Several possibilities here:
                     * id id;               single field
                     * id id, ...;          multiple fields
                     * id id = ...;         fields with initexpr
                     * id(...) { ... }      constructor
                     * id id(...) { ...}    method
                     */
                    String type = parse_type(t);
                    Token t2 = next_token();
                    if(t2.type == Token.Type.IDENTIFIER)
                    {
                        Token t3 = next_token();
                        if(t3.equals(OPEN_PAREN)) // Method
                        {
                            List<ParsedParam> parameters = parse_parameters();
                            methods.add(new ParsedMethod(
                                    t2.text,    // name
                                    modifiers,  // modifiers
                                    type,       // return type
                                    parameters));
                            Token end_sig = next_token();
                            if(end_sig.equals(BEGIN_BLOCK))
                                skip_block();
                            else if(end_sig.equals(THROWS_SPECIFIER))
                                skip_block(0);
                            else if(!end_sig.equals(END_STATEMENT))
                                throw unexpected(end_sig);
                        }
                        else if(t3.type == Token.Type.OPERATOR) // Fields
                        {
                            if(!t3.equals(END_STATEMENT))
                                skip_statement();
                        }
                        else
                            throw unexpected(t3);
                    }
                    else if(t2.equals(OPEN_PAREN)) // Constructor
                    {
                        if(!type.equals(classname))
                            throw new ParserError(
                                    "Constructor with wrong name (or method " +
                                    "with no return type)",
                                    lineNumber());
                        List<ParsedParam> parameters = parse_parameters();
                        constructors.add(new ParsedConstructor(
                                modifiers,
                                parameters));
                        t = next_token();
                        if(t.equals(BEGIN_BLOCK))
                            skip_block();
                        else if(t.equals(THROWS_SPECIFIER))
                            skip_block(0);
                        else
                            throw unexpected(t);
                    }
                }
                modifiers = 0;
            }
            else
                throw unexpected(t);
            t = next_token();
        }

        String fullname;
        if(pkgname.isEmpty())
            fullname = classname;
        else
            fullname = pkgname + '.' + classname;

        return new ParsedClass(
                fullname, constructors, methods, class_modifiers,
                filename, lineNumber());
    }

    private List<ParsedParam> parse_parameters() throws ParserError
    {
        List<ParsedParam> parameters = new LinkedList<ParsedParam>();
        int modifiers = 0;
        Token t = next_token();
        if(t.equals(CLOSE_PAREN))
            return parameters;
        while(true)
        {
            if(t.type != Token.Type.IDENTIFIER)
                throw unexpected(t);
            else if(is_modifier(t))
                modifiers |= MODIFIERS.get(t.text);
            else
            {
                String type = parse_type(t);
                t = next_token(Token.Type.IDENTIFIER);
                parameters.add(new ParsedParam(type, t.text, modifiers));
                modifiers = 0;

                t = next_token();
                if(t.equals(CLOSE_PAREN))
                    return parameters;
                else if(!t.equals(COMMA))
                    throw unexpected(t);
            }
            t = next_token();
        }
    }

    private ParserError unexpected(Token t)
    {
        return new UnexpectedToken(t.text, lineNumber());
    }

}
