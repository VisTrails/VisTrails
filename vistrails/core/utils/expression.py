""" Helper functions for parsing and evaluating expressions """

################################################################################

def evaluateExpressions(expressions):
    """ evaluateExpressions(expressions: str) -> int/float/string        
    Evaluate the contents of the line edit inside each '$' pair
    
    """
    (base, exps) = parseExpression(str(expressions))
    for e in exps:
        try:                        
            base = base[:e[0]] + str(eval(e[1],None,None)) + base[e[0]:]
        except:
            base = base[:e[0]] + '$' + e[1] + '$' + base[e[0]:]
    return base

def parseExpression(expression):
    """ parseExpression(expression: str) -> output (see below)        
    Parse the mixed expression string into expressions and string
    constants

    Keyword arguments:        
    output - (simplified string, [(pos:exp),(pos:exp),...]
        simplified string: the string without any '$exp$'. All
        $$ will be replace by a single $.
    (pos:exp) - the expression to be computed and where it should be
        inserted back to the simplified string, starting from
        the end of the string.

    """
    import re
    output = expression
    result = []
    p = re.compile(r'\$[^$]+\$')
    e = p.finditer(output)
    if e:
        offset = 0
        for s in e:
            exp = s.group()
            result.append((s.span()[0]-offset, exp[1:len(exp)-1]))
            offset += s.span()[1]-s.span()[0]
        result.reverse()
        output = p.sub('', output)
        output.replace('$$','$')
    return (output, result)
