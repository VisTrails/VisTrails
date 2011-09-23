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
"""Very thin convenience wrapper around optparse.OptionParser."""

import optparse
import sys

class CommandLineParserSingleton(object):
    """CommandLineParser is a very thin wrapper around
    optparse.OptionParser to make easier the parsing of command line
    parameters."""
    def __call__(self):
        return self
    
    def __init__(self):
        self.parser = optparse.OptionParser()
        self.options_were_read = False
        self.args = []

    def init_options(self,args=sys.argv[1:]):
        """self.init_options(args: [string]) -> None. Initialize option dictionary,
        by parsing command line arguments according to the options set
        by previous add_option calls.

        Few programs should call this. Call self.parse_options() unless
        you know what you're doing."""
        (self.options, self.args) = self.parser.parse_args(args)
        self.options_were_read = True

    def add_option(self, *args, **kwargs):
        """self.add_option(*args, **kwargs) -> None. Adds a new option
        to the command line parser. Behaves identically to the
        optparse.OptionParser.add_option."""
        self.parser.add_option(*args, **kwargs)

    def get_option(self, key):
        """self.get_option(key) -> value. Returns a value corresponding
        to the given key that was parsed from the command line. Throws
        AttributeError if key is not present."""
        self.parse_options()
        return getattr(self.options, key)

    def parse_options(self,args=sys.argv[1:]):
        """self.parse_options() -> None. Parse command line arguments,
        according to the options set by previous add_option calls."""
        if not self.options_were_read:
            self.init_options(args)

    def get_arg(self,number):
        """self.get_arg(number) -> value. Returns the value corresponding
        to the argument at position number from the command line. Returns 
        None if number is greater or equal the number of arguments. """
        if len(self.args) > number:
            return self.args[number]
        else:
            return None 

    def positional_arguments(self):
        """positional_arguments() -> [string]. Returns a list of strings
        representing the positional arguments in the command line."""
        return self.args

# singleton trick
CommandLineParser = CommandLineParserSingleton()
