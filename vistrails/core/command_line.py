############################################################################
##
## Copyright (C) 2006-2007 University of Utah. All rights reserved.
##
## This file is part of VisTrails.
##
## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of
## this file.  Please review the following to ensure GNU General Public
## Licensing requirements will be met:
## http://www.opensource.org/licenses/gpl-license.php
##
## If you are unsure which license is appropriate for your use (for
## instance, you are interested in developing a commercial derivative
## of VisTrails), please contact us at vistrails@sci.utah.edu.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################
"""Very thin convenience wrapper around optparse.OptionParser."""

import optparse

class CommandLineParserSingleton(object):
    """CommandLineParser is a very thin wrapper around
    optparse.OptionParser to make easier the parsing of command line
    parameters."""
    def __call__(self):
        return self
    
    def __init__(self):
        self.parser = optparse.OptionParser()
        self.optionsWereRead = False
        self.args = []

    def initOptions(self):
        """self.initOptions() -> None. Initialize option dictionary,
        by parsing command line arguments according to the options set
        by previous addOption calls.

        Few programs should call this. Call self.parseOptions() unless
        you know what you're doing."""
        (self.options, self.args) = self.parser.parse_args()
        self.optionsWereRead = True

    def addOption(self, *args, **kwargs):
        """self.addOption(*args, **kwargs) -> None. Adds a new option
        to the command line parser. Behaves identically to the
        optparse.OptionParser.add_option."""
        self.parser.add_option(*args, **kwargs)

    def getOption(self, key):
        """self.getOption(key) -> value. Returns a value corresponding
        to the given key that was parsed from the command line. Throws
        AttributeError if key is not present."""
        self.parseOptions()
        return getattr(self.options, key)

    def parseOptions(self):
        """self.parseOptions() -> None. Parse command line arguments,
        according to the options set by previous addOption calls."""
        if not self.optionsWereRead:
            self.initOptions()

    def getArg(self,number):
        """self.getArg(number) -> value. Returns the value corresponding
        to the argument at position number from the command line. Returns 
        None if number is greater or equal the number of arguments. """
        if len(self.args) > number:
            return self.args[number]
        else:
            return None 

    def positionalArguments(self):
        """positionalArguments() -> [string]. Returns a list of strings
        representing the positional arguments in the command line."""
        return self.args

# singleton trick
CommandLineParser = CommandLineParserSingleton()
