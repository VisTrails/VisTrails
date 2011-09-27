###############################################################################
##
## Copyright (C) 2006-2011, University of Utah. 
## All rights reserved.
## Contact: contact@vistrails.org
##
## This file is part of VisTrails.
##
## "Redistribution and use in source and binary forms, with or without 
## modification, are permitted provided that the following conditions are met:
##
##  - Redistributions of source code must retain the above copyright notice, 
##    this list of conditions and the following disclaimer.
##  - Redistributions in binary form must reproduce the above copyright 
##    notice, this list of conditions and the following disclaimer in the 
##    documentation and/or other materials provided with the distribution.
##  - Neither the name of the University of Utah nor the names of its 
##    contributors may be used to endorse or promote products derived from 
##    this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
## AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
## THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR 
## PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR 
## CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; 
## OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
## WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR 
## OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF 
## ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
###############################################################################
""" Helper functions for parsing and evaluating expressions """

################################################################################

def evaluate_expressions(expressions):
    """ evaluate_expressions(expressions: str) -> int/float/string        
    Evaluate the contents of the line edit inside each '$' pair
    
    """

    # FIXME: eval should pretty much never be used
    (base, exps) = parse_expression(str(expressions))
    for e in exps:
        try:                        
            base = base[:e[0]] + str(eval(e[1],None,None)) + base[e[0]:]
        except:
            base = base[:e[0]] + '$' + e[1] + '$' + base[e[0]:]
    return base

def parse_expression(expression):
    """ parse_expression(expression: str) -> output (see below)        
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
