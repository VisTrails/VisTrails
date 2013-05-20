import datetime
import re
import time

from vistrails.core.modules.vistrails_module import Module, ModuleError
from vistrails.core.bundles import py_import


class UTC(datetime.tzinfo):
    def utcoffset(self, dt):
        return datetime.timedelta(0)

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return datetime.timedelta(0)

utc = UTC()


class FixedOffset(datetime.tzinfo):
    def __init__(self, offset, name):
        self.offset = offset
        self.name = name

    def utcoffset(self, dt):
        return self.offset

    def tzname(self, dt):
        return self.name

    def dst(self, dt):
        return datetime.timedelta(0)


class LocalTimezone(datetime.tzinfo):
    STDOFFSET = datetime.timedelta(seconds=time.timezone)
    if time.daylight:
        DSTOFFSET = datetime.timedelta(seconds=-time.altzone)
    else:
        DSTOFFSET = STDOFFSET

    DSTDIFF = DSTOFFSET - STDOFFSET

    def utcoffset(self, dt):
        if self._isdst(dt):
            return self.DSTOFFSET
        else:
            return self.STDOFFSET

    def dst(self, dt):
        if self._isdst(dt):
            return self.DSTDIFF
        else:
            return datetime.timedelta(0)

    def tzname(self, dt):
        return time.tzname[self._isdst(dt)]

    def _isdst(self, dt):
        tt = (dt.year, dt.month, dt.day,
              dt.hour, dt.minute, dt.second,
              dt.weekday(), 0, 0)
        timestamp = time.mktime(tt)
        tt = time.localtime(timestamp)
        return tt.tm_isdst > 0


_decimal_fmt = re.compile(
        r'^'
        '([-+]?)'           # + means we are advancing compared to UTC
        '([0-9]?[0-9])'     # hours
        '([0-9][0-9])?$')   # minutes

def make_timezone(s):
        if s == 'local':
            return LocalTimezone()

        match = _decimal_fmt.match(s)
        if match is not None:
            sign, hours, minutes = match.groups('')
            sign = -1 if sign == '-' else 1
            hours = int(hours)
            minutes = int(minutes) if minutes else 0
            offset = datetime.timedelta(
                    minutes=sign * (hours*60 + minutes))
            name = '%s%02d%02d' % (
                    '-' if sign == -1 else '+',
                    hours,
                    minutes)
            return FixedOffset(offset, name)

        try:
            pytz = py_import('pytz', {
                    'linux-debian': 'python-tz',
                    'linux-ubuntu': 'python-tz',
                    'linux-fedora': 'pytz'})
        except ImportError:
            raise ValueError("can't understand timezone %r (maybe you should "
                             "install pytz?)" % s)
        else:
            try:
                return pytz.timezone(s)
            except KeyError:
                raise ValueError("can't understand timezone %r (defaulted to "
                                 "pytz, which gave no answer)" % s)


class TimestampsToDates(Module):
    """
    Converts a List or numpy array of timestamps into datetime objects.

    A UNIX timestamp represents the number of seconds since Jan 1 1970 0:00,
    UTC. It represents a specific point in time that is not dependent on a
    timezone.
    The returned datetime objects are in the UTC timezone.
    """
    _input_ports = [
            ('timestamps', '(org.vistrails.vistrails.basic:List)')]
    _output_ports = [
            ('dates', '(org.vistrails.vistrails.basic:List)')]

    def compute(self):
        timestamps = self.getInputFromPort('timestamps')

        result = [datetime.datetime.fromtimestamp(t, utc) for t in timestamps]
        self.setResult('dates', result)


class StringsToDates(Module):
    """
    Converts a List of dates (as strings) into datetime objects.

    If no format is given, the dateutil.parser module will be used to guess
    what each string refers to; else, it is passed to strptime() to read each
    date. For example: '%Y-%m-%d %H:%M:%S'.
    The 'timezone' parameter indicates which timezone these dates are expressed
    in. It can be either:
      * 'local', in which case each date is interpreted as being in whatever
        timezone the system is set to use;
      * an offset in hours/minutes from UTC, for instance '-0400' for DST
        (eastern America time, when daylight saving is in effect). Note that in
        this case, the same offset is used for every date, without regard for
        daylight saving (if a date falls in winter, '-0500' will not be used
        instead).
      * if pytz is available, anything else will be passed to pytz.timezone(),
        so you would be able to use strings such as 'US/Eastern' or
        'Europe/Amsterdam'.
    """
    _input_ports = [
            ('strings', '(org.vistrails.vistrails.basic:List)'),
            ('format', '(org.vistrails.vistrails.basic:String)',
             {'optional': True, 'defaults': "['']"}),
            ('timezone', '(org.vistrails.vistrails.basic:String)',
             {'optional': True, 'defaults': "['']"})]
    _output_ports = [
            ('dates', '(org.vistrails.vistrails.basic:List)')]

    @staticmethod
    def convert_to_dates(strings, fmt, tz):
        if not fmt:
            try:
                py_import('dateutil', {
                    'linux-debian': 'python-dateutil',
                    'linux-ubuntu': 'python-dateutil',
                    'linux-fedora': 'python-dateutil'})
            except ImportError:
                raise ValueError("can't read dates without a format without "
                                 "the dateutil package")
            from dateutil import parser
            result = [parser.parse(s, ignoretz=tz is not None)
                      for s in strings]
        else:
            result = [datetime.datetime.strptime(s, fmt) for s in strings]

        if tz:
            result = [dt.replace(tzinfo=tz) for dt in result]

        return result

    def compute(self):
        tz = self.getInputFromPort('timezone')
        if tz:
            try:
                tz = make_timezone(tz)
            except ValueError, e:
                raise ModuleError(self, e.message)
        else:
            tz = None

        strings = self.getInputFromPort('strings')
        fmt = self.getInputFromPort('format')

        try:
            result = self.convert_to_dates(strings, fmt, tz)
        except ValueError, e:
            raise ModuleError(self, e.message)
        self.setResult('dates', result)


class StringsToMatplotlib(Module):
    """
    Converts a List of dates (as strings) to an array accepted by matplotlib.
    """
    _input_ports = [
            ('strings', '(org.vistrails.vistrails.basic:List)'),
            ('format', '(org.vistrails.vistrails.basic:String)',
             {'optional': True, 'defaults': "['']"}),
            ('timezone', '(org.vistrails.vistrails.basic:String)',
             {'optional': True, 'defaults': "['']"})]
    _output_ports = [
            ('dates', '(org.vistrails.vistrails.basic:List)')]

    def compute(self):
        try:
            py_import('matplotlib', {
                    'linux-debian': 'python-matplotlib',
                    'linux-ubuntu': 'python-matplotlib',
                    'linux-fedora': 'python-matplotlib'})
        except ImportError:
            raise ModuleError(self, "matplotlib is not available")
        else:
            from matplotlib.dates import date2num

        tz = self.getInputFromPort('timezone')
        if tz:
            try:
                tz = make_timezone(tz)
            except ValueError, e:
                raise ModuleError(self, e.message)
        else:
            tz = None

        strings = self.getInputFromPort('strings')
        fmt = self.getInputFromPort('format')

        try:
            result = StringsToDates.convert_to_dates(strings, fmt, tz)
        except ValueError, e:
            raise ModuleError(self, e.message)
        result = date2num(result)
        self.setResult('dates', result)


_modules = {'dates': [TimestampsToDates, StringsToDates, StringsToMatplotlib]}


###############################################################################

import unittest
from vistrails.tests.utils import execute, intercept_result
from ..identifiers import identifier


class TestTimestampToDates(unittest.TestCase):
    def test_timestamps(self):
        """Test conversion to datetime objects.
        """
        timestamps = [1369041900, 1369042260, 1357153500]
        with intercept_result(TimestampsToDates, 'dates') as results:
            self.assertFalse(execute([
                    ('convert|dates|TimestampsToDates', identifier, [
                        ('timestamps', [('List', repr(timestamps))]),
                    ]),
                ]))
        self.assertEqual(len(results), 1)
        results = results[0]
        self.assertTrue(all(d.tzinfo is utc for d in results))
        fmt = '%Y-%m-%d %H:%M:%S %Z %z'
        self.assertEqual(
                [d.strftime(fmt) for d in results],
                ['2013-05-20 09:25:00 UTC +0000',
                 '2013-05-20 09:31:00 UTC +0000',
                 '2013-01-02 19:05:00 UTC +0000'])
        try:
            import pytz
        except ImportError:
            pass
        else:
            self.assertEqual(
                    [d.astimezone(pytz.timezone('US/Eastern')).strftime(fmt)
                     for d in results],
                    ['2013-05-20 05:25:00 EDT -0400',
                     '2013-05-20 05:31:00 EDT -0400',
                     '2013-01-02 14:05:00 EST -0500'])


class TestStringsToDates(unittest.TestCase):
    def test_naive(self):
        """Test reading non-timezone-aware dates.
        """
        dates = ['2013-05-20 9:25', '2013-05-20 09:31', '2013-01-02 19:05']
        in_fmt = '%Y-%m-%d %H:%M'
        with intercept_result(StringsToDates, 'dates') as results:
            self.assertFalse(execute([
                    ('convert|dates|StringsToDates', identifier, [
                        ('strings', [('List', repr(dates))]),
                        ('format', [('String', in_fmt)]),
                    ]),
                ]))
        self.assertEqual(len(results), 1)
        results = results[0]
        self.assertTrue(all(d.tzinfo is None for d in results))
        fmt = '%Y-%m-%d %H:%M:%S %Z %z'
        self.assertEqual(
                [d.strftime(fmt) for d in results],
                ['2013-05-20 09:25:00  ',
                 '2013-05-20 09:31:00  ',
                 '2013-01-02 19:05:00  '])

    def test_dateutil(self):
        """Test reading non-timezone-aware dates without providing the format.

        dateutil is required for this one.
        """
        try:
            import dateutil
        except ImportError:
            self.skipTest("dateutil is not available")

        dates = ['2013-05-20 9:25',
                 'Thu Sep 25 10:36:28 2003',
                 '2003 10:36:28 CET 25 Sep Thu'] # Timezone will be ignored
        with intercept_result(StringsToDates, 'dates') as results:
            self.assertFalse(execute([
                    ('convert|dates|StringsToDates', identifier, [
                        ('strings', [('List', repr(dates))]),
                    ]),
                ]))
        self.assertEqual(len(results), 1)
        results = results[0]
        fmt = '%Y-%m-%d %H:%M:%S %Z %z'
        self.assertEqual(
                [d.strftime(fmt) for d in results],
                ['2013-05-20 09:25:00  ',
                 '2003-09-25 10:36:28  ',
                 '2003-09-25 10:36:28  '])

    def test_timezone(self):
        """Test reading timezone-aware dates by supplying an offset.
        """
        dates = ['2013-05-20 9:25', '2013-05-20 09:31', '2013-01-02 19:05']
        in_fmt = '%Y-%m-%d %H:%M'
        with intercept_result(StringsToDates, 'dates') as results:
            self.assertFalse(execute([
                    ('convert|dates|StringsToDates', identifier, [
                        ('strings', [('List', repr(dates))]),
                        ('format', [('String', in_fmt)]),
                        ('timezone', [('String', '-0500')])
                    ]),
                ]))
        self.assertEqual(len(results), 1)
        results = results[0]
        self.assertTrue(all(d.tzinfo is not None for d in results))
        fmt = '%Y-%m-%d %H:%M:%S %z'
        self.assertEqual(
                [d.strftime(fmt) for d in results],
                ['2013-05-20 09:25:00 -0500',
                 '2013-05-20 09:31:00 -0500',
                 '2013-01-02 19:05:00 -0500'])

    def test_timezone_pytz(self):
        """Test reading timezone-aware dates through pytz.
        """
        try:
            import pytz
        except ImportError:
            self.skipTest("pytz is not available")

        dates = ['2013-01-20 9:25', '2013-01-20 09:31', '2013-06-02 19:05']
        in_fmt = '%Y-%m-%d %H:%M'
        with intercept_result(StringsToDates, 'dates') as results:
            self.assertFalse(execute([
                    ('convert|dates|StringsToDates', identifier, [
                        ('strings', [('List', repr(dates))]),
                        ('format', [('String', in_fmt)]),
                        ('timezone', [('String', 'America/New_York')])
                    ]),
                ]))
        self.assertEqual(len(results), 1)
        results = results[0]
        self.assertTrue(all(d.tzinfo is not None for d in results))
        fmt = '%Y-%m-%d %H:%M:%S %Z %z'
        self.assertEqual(
                [d.strftime(fmt) for d in results],
                ['2013-01-20 09:25:00 EST -0500',
                 '2013-01-20 09:31:00 EST -0500',
                 '2013-06-02 19:05:00 EDT -0400']) # FIXME: fails for some reason!


class TestStringsToMatplotlib(unittest.TestCase):
    def test_timezone(self):
        """Test reading timezone-aware dates by supplying an offset.
        """
        try:
            import matplotlib
        except ImportError:
            self.skipTest("matplotlib is not available")

        from matplotlib.dates import date2num

        dates = ['2013-05-20 9:25', '2013-05-20 09:31', '2013-01-02 18:05']
        in_fmt = '%Y-%m-%d %H:%M'
        with intercept_result(StringsToMatplotlib, 'dates') as results:
            self.assertFalse(execute([
                    ('convert|dates|StringsToMatplotlib', identifier, [
                        ('strings', [('List', repr(dates))]),
                        ('format', [('String', in_fmt)]),
                        ('timezone', [('String', '-0500')])
                    ]),
                ]))
        self.assertEqual(len(results), 1)
        results = results[0]
        self.assertEqual(list(results), list(date2num([
                datetime.datetime(2013, 5, 20, 14, 25, 0),
                datetime.datetime(2013, 5, 20, 14, 31, 0),
                datetime.datetime(2013, 1, 2, 23, 5, 0)])))
