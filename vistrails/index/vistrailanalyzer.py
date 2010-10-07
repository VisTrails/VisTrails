import re

from lucene import *
import lucene
dir(lucene)

class vistrailAnalyzer(PythonAnalyzer):

    def tokenStream(self, fieldName, reader):

        result = StandardTokenizer(reader)
        result = StandardFilter(result)
        result = vistrailFilter(result)
        result = LowerCaseFilter(result)
        result = PorterStemFilter(result)
        result = StopFilter(result, StopAnalyzer.ENGLISH_STOP_WORDS)

        return result

class stemmingAnalyzer(PythonAnalyzer):

    def tokenStream(self, fieldName, reader):

        result = StandardTokenizer(reader)
        result = StandardFilter(result)
        result = LowerCaseFilter(result)
        result = PorterStemFilter(result)
        result = StopFilter(result, StopAnalyzer.ENGLISH_STOP_WORDS)

        return result

# patterns for splitting words into substrings
patterns = [
    # 32 char md5 sums
    "[a-f0-9]{32}",
    # '2D', '3D'
    "2D", "3D",
    # words beginning with capital letters
    "[A-Z][a-z]+",
    # capital letter sequence ending with a word that begins with a capital letter
    "[A-Z]*(?=[A-Z][a-z])",
    # capital letter sequence
    "[A-Z]{2,}",
    # non-capital letter sequence
    "[a-z]{2,}" ]

splitPattern = re.compile("|".join(patterns))

class vistrailFilter(PythonTokenFilter):

    TOKEN_TYPE_PART = "text"


    def __init__(self, input):
        super(vistrailFilter, self).__init__(input)
        self.input = input
        self.parts = [] # parts found for the current token
        self.current = None

    def next(self):
        if self.parts:
            # continue adding parts
            part = self.parts.pop()
            t = Token(part, self.current.startOffset(),
                      self.current.endOffset(), self.TOKEN_TYPE_PART)
            t.setPositionIncrement(0)
            return t
        else:
            # find parts
            self.current = self.input.next()
            if self.current is None:
                return None
            text = str(self.current.termText())
            pattern = splitPattern.findall(text)
            # remove single characters and duplicates
            pattern = set([p for p in pattern if len(p)>1 and p != text])
#            if len(pattern) > 0:
#                print "vistrailFilter", text, "-->",','.join(pattern)
            self.parts = pattern
            return self.current


