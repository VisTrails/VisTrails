from PyQt4 import QtGui
from PyQt4.QtCore import QString
import core.common
import re
import time
import xml.sax.saxutils

# This shouldn't be called VersionTreeSearch anymore, but Search, since it now
# includes modules. We'll fix it later.

################################################################################

class SearchParseError(Exception):
    pass

class SearchStmt(object):
    def __init__(self, content):
        self.text = content
        self.content = re.compile('.*'+content+'.*', re.MULTILINE | re.IGNORECASE)

    def matchModule(self, v, m):
        return True

    def run(self, v, n):
        pass

    def __call__(self):
        """Make SearchStmt behave just like a QueryObject."""
        return self

class TimeSearchStmt(SearchStmt):
    oneSecond = 1.0
    oneMinute = oneSecond * 60.0
    oneHour = oneMinute * 60.0
    oneDay = oneHour * 24.0
    oneWeek = oneDay * 7.0
    oneMonth = oneDay * 31.0 # wrong, I know
    oneYear = oneDay * 365.0 # wrong, I know
    amounts = {'seconds': oneSecond,
               'minutes': oneMinute,
               'hours': oneHour,
               'days': oneDay,
               'weeks': oneWeek,
               'months': oneMonth,
               'years': oneYear}
    months = {'january': 1,
              'february': 2,
              'march': 3,
              'april': 4,
              'may': 5,
              'june': 6,
              'july': 7,
              'august': 8,
              'september': 9,
              'october': 10,
              'november': 11,
              'december': 12}
    
    dateEntry = r'([^\,\/\: ]+)'
    timeEntry = r'(\d?\d?)'
    dateSep = r' *[\,\/\- ] *'
    timeSep = r' *: *'
    sep = r' *'
    start = r'^ *'
    finish = r' *$'
    twoEntryDate = (dateEntry+
                    dateSep+
                    dateEntry)
    threeEntryDate = (dateEntry+
                      dateSep+
                      dateEntry+
                      dateSep+
                      dateEntry)
    twoEntryTime = (timeEntry+
                    timeSep+
                    timeEntry)
    threeEntryTime = (timeEntry+
                      timeSep+
                      timeEntry+
                      timeSep+
                      timeEntry)

    dateRE = [re.compile((start+
                          twoEntryDate+
                          finish)), # Mar 12   Mar, 12    
              re.compile((start+
                          threeEntryDate+
                          finish)), # Mar, 12, 2006    2006 Mar 12     etc
              re.compile((start+
                          twoEntryTime+
                          finish)),
              re.compile((start+
                          threeEntryTime+
                          finish)),
              re.compile((start+
                          twoEntryDate+
                          sep+
                          twoEntryTime+
                          finish)),
              re.compile((start+
                          twoEntryDate+
                          sep+
                          threeEntryTime+
                          finish)),
              re.compile((start+
                          threeEntryDate+
                          sep+
                          twoEntryTime+
                          finish)),
              re.compile((start+
                          threeEntryDate+
                          sep+
                          threeEntryTime+
                          finish)),
              re.compile((start+
                          twoEntryTime+
                          sep+
                          twoEntryDate+
                          finish)),
              re.compile((start+
                          twoEntryTime+
                          sep+
                          threeEntryDate+
                          finish)),
              re.compile((start+
                          threeEntryTime+
                          sep+
                          twoEntryDate+
                          finish)),
              re.compile((start+
                          threeEntryTime+
                          sep+
                          threeEntryDate+
                          finish))]
    
    def __init__(self, date):
        self.date = self.parseDate(date)

    def parseDate(self, dateStr):
        def parseAgo(s):
            [amount, unit] = s.split(' ')
            try:
                amount = float(amount)
            except ValueError:
                raise SearchParseError("Expected a number, got %s" % amount)
            if amount <= 0:
                raise SearchParseError("Expected a positive number, got %s" % amount)
            unitRe = re.compile('^'+unit)
            keys = [k
                    for k in TimeSearchStmt.amounts.keys()
                    if unitRe.match(k)]
            if len(keys) == 0:
                raise SearchParseError("Time unit unknown: %s" % unit)
            elif len(keys) > 1:
                raise SearchParseError("Time unit ambiguous: %s matches %s" % (unit, keys))
            return round(time.time()) - TimeSearchStmt.amounts[keys[0]] * amount

        def guessDate(unknownEntries, year=None):
            def guessStrMonth(s):
                monthRe = re.compile('^'+s)
                keys = [k
                        for k in TimeSearchStmt.months.keys()
                        if monthRe.match(k)]
                if len(keys) == 0:
                    raise SearchParseError("Unknown month: %s" % s)
                elif len(keys) > 1:
                    raise SearchParseError("Ambiguous month: %s matches %s" % (s, keys))
                return TimeSearchStmt.months[keys[0]]
            if not year:
                m = None
                # First heuristic: if month comes first, then year comes last
                try:
                    e0 = int(unknownEntries[0])
                except ValueError:
                    m = guessStrMonth(unknownEntries[0])
                    try:
                        d = int(unknownEntries[1])
                    except ValueError:
                        raise SearchParseError("Expected day, got %s" % unknownEntries[1])
                    try:
                        y = int(unknownEntries[2])
                    except ValueError:
                        raise SearchParseError("Expected year, got %s" % unknownEntries[2])
                    return (y, m, d)
                # Second heuristic: if month comes last, then year comes first
                try:
                    e2 = int(unknownEntries[2])
                except ValueError:
                    m = guessStrMonth(unknownEntries[2])
                    try:
                        d = int(unknownEntries[1])
                    except ValueError:
                        raise SearchParseError("Expected day, got %s" % unknownEntries[1])
                    try:
                        y = int(unknownEntries[0])
                    except ValueError:
                        raise SearchParseError("Expected year, got %s" % unknownEntries[0])
                    return (y, m, d)
                # If month is the middle one, decide day and year by size
                # (year is largest, hopefully year was entered using 4 digits)
                try:
                    e1 = int(unknownEntries[1])
                except ValueError:
                    m = guessStrMonth(unknownEntries[1])
                    try:
                        d = int(unknownEntries[2])
                    except ValueError:
                        raise SearchParseError("Expected day or year, got %s" % unknownEntries[2])
                    try:
                        y = int(unknownEntries[0])
                    except ValueError:
                        raise SearchParseError("Expected year or year, got %s" % unknownEntries[0])
                    return (max(y,d), m, min(y, d))
                lst = [(e0,0),(e1,1),(e2,2)]
                lst.sort()
                return guessDate([str(lst[0][0]),
                                  str(lst[1][0])],
                                 year=e2)
            # We know year, decide month using similar heuristics - try string month first,
            # then decide which is possible
            try:
                e0 = int(unknownEntries[0])
            except ValueError:
                m = guessStrMonth(unknownEntries[0])
                try:
                    d = int(unknownEntries[1])
                except ValueError:
                    raise SearchParseError("Expected day, got %s" % unknownEntries[1])
                return (year, m, d)
            try:
                e1 = int(unknownEntries[1])
            except ValueError:
                m = guessStrMonth(unknownEntries[1])
                try:
                    d = int(unknownEntries[0])
                except ValueError:
                    raise SearchParseError("Expected day, got %s" % unknownEntries[0])
                return (year, m, d)
            if e0 > 12:
                return (year, e1, e0)
            else:
                return (year, e0, e1)

        dateStr = dateStr.lower().lstrip().rstrip()
        if dateStr.endswith(" ago"):
            return parseAgo(dateStr[:-4])
        if dateStr == "yesterday":
            lst = list(time.localtime(round(time.time()) - TimeSearchStmt.oneDay))
            # Reset hour, minute, second
            lst[3] = 0
            lst[4] = 0
            lst[5] = 0
            return time.mktime(lst)
        if dateStr == "today":
            lst = list(time.localtime())
            # Reset hour, minute, second
            lst[3] = 0
            lst[4] = 0
            lst[5] = 0
            return time.mktime(lst)
        if dateStr.startswith("this "):
            rest = dateStr[5:]
            lst = list(time.localtime(round(time.time())))
            if rest == "minute":
                lst[5] = 0
            elif rest == "hour":
                lst[5] = 0
                lst[4] = 0
            elif rest == "day":
                lst[5] = 0
                lst[4] = 0
                lst[3] = 0
            elif rest == "week": # weeks start on monday
                lst[5]  = 0
                lst[4]  = 0
                lst[3]  = 0
                # This hack saves me the hassle of computing negative days, months, etc
                lst = list(time.localtime(time.mktime(lst) - TimeSearchStmt.oneDay * lst[6]))
            elif rest == "month":
                lst[5]  = 0
                lst[4]  = 0
                lst[3]  = 0
                lst[2]  = 1
            elif rest == "year":
                lst[5]  = 0
                lst[4]  = 0
                lst[3]  = 0
                lst[2]  = 1
                lst[1]  = 1
            return time.mktime(lst)
                
        result = [x.match(dateStr) for x in TimeSearchStmt.dateRE]
        this = list(time.localtime())
        def setTwoDate(g):
            d = guessDate(g, year=this[0])
            this[0] = d[0]
            this[1] = d[1]
            this[2] = d[2]
        def setThreeDate(g):
            d = guessDate(g)
            this[0] = d[0]
            this[1] = d[1]
            this[2] = d[2]
        def setTwoTime(g):
            this[3] = int(g[0])
            this[4] = int(g[1])
            this[5] = 0
        def setThreeTime(g):
            this[3] = int(g[0])
            this[4] = int(g[1])
            this[5] = int(g[2])
        if result[0]:
            setTwoDate(result[0].groups())
            setTwoTime([0,0])
        elif result[1]:
            setThreeDate(result[1].groups())
            setTwoTime([0,0])
        elif result[2]:
            setTwoTime(result[2].groups())
        elif result[3]:
            setThreeTime(result[3].groups())
        elif result[4]:
            g = result[4].groups()
            setTwoDate([g[0], g[1]])
            setTwoTime([g[2], g[3]])
        elif result[5]:
            g = result[5].groups()
            setTwoDate([g[0], g[1]])
            setThreeTime([g[2], g[3], g[4]])
        elif result[6]:
            g = result[6].groups()
            setThreeDate([g[0], g[1], g[2]])
            setTwoTime([g[3], g[4]])
        elif result[7]:
            g = result[7].groups()
            setThreeDate([g[0], g[1], g[2]])
            setThreeTime([g[3], g[4], g[5]])
        elif result[8]:
            g = result[8].groups()
            setTwoTime([g[0], g[1]])
            setTwoDate([g[2], g[3]])
        elif result[9]:
            g = result[9].groups()
            setTwoTime([g[0], g[1]])
            setThreeDate([g[2], g[3], g[4]])
        elif result[10]:
            g = result[10].groups()
            setThreeTime([g[0], g[1], g[2]])
            setTwoDate([g[3], g[4]])
        elif result[11]:
            g = result[11].groups()
            setThreeTime([g[0], g[1], g[2]])
            setThreeDate([g[3], g[4],g[5]])
        else:
            raise SearchParseError("Expected a date, got '%s'" % dateStr)
        return time.mktime(this)
        
class BeforeSearchStmt(TimeSearchStmt):
    def match(self, action):
        if not action.date:
            return False
        t = time.mktime(time.strptime(action.date, "%d %b %Y %H:%M:%S"))
        return t <= self.date

class AfterSearchStmt(TimeSearchStmt):
    def match(self, action):
        if not action.date:
            return False
        t = time.mktime(time.strptime(action.date, "%d %b %Y %H:%M:%S"))
        print t, self.date, action.date
        return t >= self.date

class UserSearchStmt(SearchStmt):
    def match(self, action):
        if not action.user:
            return False
        return self.content.match(action.user)

class NotesSearchStmt(SearchStmt):
    def match(self, action):
        notes = xml.sax.saxutils.unescape(action.notes)
        fragment = QtGui.QTextDocumentFragment.fromHtml(QString(notes))
        plainNotes = str(fragment.toPlainText())
        return self.content.search(plainNotes)

class NameSearchStmt(SearchStmt):
    def match(self, action):
        vistrail = action.vistrail
        if not vistrail.inverseTagMap.has_key(action.timestep):
            return False
        m = self.content.match(vistrail.inverseTagMap[action.timestep])
        t = self.text
        return bool(m)

class AndSearchStmt(SearchStmt):
    def __init__(self, lst):
        self.matchList = lst
    def match(self, action):
        for s in self.matchList:
            if not s.match(action):
                return False
        return True

class OrSearchStmt(SearchStmt):
    def __init__(self, lst):
        self.matchList = lst
    def match(self, action):
        for s in self.matchList:
            if s.match(action):
                return True
        return False

class NotSearchStmt(SearchStmt):
    def __init__(self, stmt):
        self.stmt = stmt
    def match(self, action):
        return not self.stmt.match(action)

class TrueSearch(SearchStmt):
    def __init__(self):
        pass
    def match(self, action):
        return True

################################################################################

class SearchCompiler(object):
    SEPARATOR = -1
    def __init__(self, searchStr):
        self.searchStmt = self.compile(searchStr)
    def compile(self, searchStr):
        lst = []
        t1 = searchStr.split(' ')
        while t1:
            tok = t1[0]
            cmd = tok.split(':')
            if not SearchCompiler.dispatch.has_key(cmd[0]):
                fun = SearchCompiler.parseAny
            else:
                fun = SearchCompiler.dispatch[cmd[0]]
            if len(cmd) > 1:
                [search, rest] = fun(self, cmd[1:] + t1[1:])
            else:
                [search, rest] = fun(self, t1)
            lst.append(search)
            t1 = rest
        return AndSearchStmt(lst)
    def parseUser(self, tokStream):
        if len(tokStream) == 0:
            raise SearchParseError('Expected token, got end of search')
        return (UserSearchStmt(tokStream[0]), tokStream[1:])
    def parseAny(self, tokStream):
        if len(tokStream) == 0:
            raise SearchParseError('Expected token, got end of search')
        tok = tokStream[0]
        return (OrSearchStmt([UserSearchStmt(tok),
                              NotesSearchStmt(tok),
                              NameSearchStmt(tok)]), tokStream[1:])
    def parseNotes(self, tokStream):
        if len(tokStream) == 0:
            raise SearchParseError('Expected token, got end of search')
        lst = []
        while len(tokStream):
            tok = tokStream[0]
            if ':' in tok:
                return (AndSearchStmt(lst), tokStream)
            lst.append(NotesSearchStmt(tok))
            tokStream = tokStream[1:]
        return (AndSearchStmt(lst), [])
    def parseName(self, tokStream):
        if len(tokStream) == 0:
            raise SearchParseError('Expected token, got end of search')
        lst = []
        while len(tokStream):
            tok = tokStream[0]
            if ':' in tok:
                return (AndSearchStmt(lst), tokStream)
            lst.append(NameSearchStmt(tok))
            tokStream = tokStream[1:]
        return (AndSearchStmt(lst), [])
    def parseBefore(self, tokStream):
        if len(tokStream) == 0:
            raise SearchParseError('Expected token, got end of search')
        lst = []
        while len(tokStream):
            tok = tokStream[0]
            # ugly, special case times
            if (':' in tok and
                not TimeSearchStmt.dateRE[2].match(tok) and
                not TimeSearchStmt.dateRE[3].match(tok)):
                return (BeforeSearchStmt(" ".join(lst)), tokStream)
            lst.append(tok)
            tokStream = tokStream[1:]
        return (BeforeSearchStmt(" ".join(lst)), [])
    def parseAfter(self, tokStream):
        if len(tokStream) == 0:
            raise SearchParseError('Expected token, got end of search')
        lst = []
        while len(tokStream):
            tok = tokStream[0]
            # ugly, special case times
            if (':' in tok and
                not TimeSearchStmt.dateRE[2].match(tok) and
                not TimeSearchStmt.dateRE[3].match(tok)):
                return (AfterSearchStmt(" ".join(lst)), tokStream)
            lst.append(tok)
            tokStream = tokStream[1:]
        return (AfterSearchStmt(" ".join(lst)), [])

    dispatch = {'user': parseUser,
                'notes': parseNotes,
                'before': parseBefore,
                'after': parseAfter,
                'name': parseName,
                'any': parseAny}
                
            

################################################################################

import unittest

class TestSearch(unittest.TestCase):
    def test1(self):
        self.assertEquals((TimeSearchStmt('1 day ago').date -
                           TimeSearchStmt('2 days ago').date), TimeSearchStmt.oneDay)
    def test2(self):
        self.assertEquals((TimeSearchStmt('12 mar 2006').date -
                           TimeSearchStmt('11 mar 2006').date), TimeSearchStmt.oneDay)
    def test3(self):
        self.assertEquals((TimeSearchStmt('12 mar').date -
                           TimeSearchStmt('12 mar 2006').date), 0.0)
    def test4(self):
        self.assertEquals((TimeSearchStmt('mar 12').date -
                           TimeSearchStmt('12 mar 2006').date), 0.0)
    def test5(self):
        self.assertEquals((TimeSearchStmt('03 15').date -
                           TimeSearchStmt('15 mar 2006').date), 0.0)
    def test6(self):
        self.assertEquals((TimeSearchStmt('03/15/2006').date -
                           TimeSearchStmt('15 mar 2006').date), 0.0)
    def test7(self):
        self.assertEquals((TimeSearchStmt('1 day ago').date -
                           TimeSearchStmt('24 hours ago').date), 0.0)
    def test8(self):
        self.assertEquals((TimeSearchStmt('1 hour ago').date -
                           TimeSearchStmt('60 minutes ago').date), 0.0)
    def test9(self):
        self.assertEquals((TimeSearchStmt('1 minute ago').date -
                           TimeSearchStmt('60 seconds ago').date), 0.0)
    def test10(self):
        self.assertEquals((TimeSearchStmt('1 week ago').date -
                           TimeSearchStmt('7 days ago').date), 0.0)
    def test11(self):
        self.assertEquals((TimeSearchStmt('1 month ago').date -
                           TimeSearchStmt('31 days ago').date), 0.0)
    def test12(self):
        self.assertEquals(TimeSearchStmt('12 mar 2006 21:00:00').date,
                          TimeSearchStmt('21:00:00 12 mar 2006').date)
    def test13(self):
        self.assertEquals(TimeSearchStmt('12 mar 2006 21:00').date,
                          TimeSearchStmt('21:00:00 12 mar').date)
    def test14(self):
        self.assertEquals(TimeSearchStmt('13 apr 2006 21:00').date,
                          TimeSearchStmt('04/13/2006 21:00:00').date)
    def test15(self):
        import core.vistrail
        import core.xml_parser
        import core.system
        parser = core.xml_parser.XMLParser()
        parser.openVistrail(core.system.visTrailsRootDirectory() +
                            '/tests/resources/dummy.xml')
        v = parser.getVistrail()
        parser.closeVistrail()
        self.assertTrue(NotesSearchStmt('mapper').match(v.actionMap[36]))
        self.assertFalse(NotesSearchStmt('-qt-block-indent').match(v.actionMap[36]))
    def test16(self):
        self.assertRaises(SearchParseError, lambda *args: SearchCompiler('before:'))
    def test17(self):
        self.assertRaises(SearchParseError, lambda *args: SearchCompiler('before:lalala'))
    def test17(self):
        self.assertRaises(SearchParseError, lambda *args: SearchCompiler('after:yesterday before:lalala'))
    def test18(self):
        self.assertEquals(TimeSearchStmt('   13 apr 2006  ').date,
                          TimeSearchStmt(' 13 apr 2006   ').date)
    def test19(self):
        self.assertEquals(SearchCompiler('before:13 apr 2006 12:34:56').searchStmt.matchList[0].date,
                          BeforeSearchStmt('13 apr 2006 12:34:56').date)
    def test20(self):
        self.assertEquals(SearchCompiler('after:yesterday').searchStmt.matchList[0].date,
                          SearchCompiler('before:yesterday').searchStmt.matchList[0].date)
    def test21(self):
        self.assertEquals(SearchCompiler('after:today').searchStmt.matchList[0].date,
                          SearchCompiler('before:today').searchStmt.matchList[0].date)
    def test22(self):
        self.assertEquals(SearchCompiler('before:today').searchStmt.matchList[0].date,
                          SearchCompiler('before:this day').searchStmt.matchList[0].date)
    def test23(self):
        t = time.localtime()
        import core.common
        inv = core.common.invert(TimeSearchStmt.months)
        m = inv[t[1]]
        self.assertEquals(SearchCompiler('after:%s %s %s' % (t[0], m, t[2])).searchStmt.matchList[0].date,
                          SearchCompiler('after:today').searchStmt.matchList[0].date)
        

if __name__ == '__main__':
    unittest.main()
