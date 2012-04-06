import time

__all__ = ['setup']

def _convert_month(month):
    if month == 'Jan':
        return 1
    elif month == 'Feb':
        return 2
    elif month == 'Mar':
        return 3
    elif month == 'Apr':
        return 4
    elif month == 'May':
        return 5
    elif month == 'Jun':
        return 6
    elif month == 'Jul':
        return 7
    elif month == 'Aug':
        return 8
    elif month == 'Sep':
        return 9
    elif month == 'Oct':
        return 10
    elif month == 'Nov':
        return 11
    elif month == 'Dec':
        return 12


# Jython's implementation of strptime doesn't work -- we have to redefine it

# Jython has a bug when assigning a function to a module, it wraps it as an
# unbound method as if the module was a class (e.g. time.strptime = strptime)
# This is why we are using a callable class instead of a function here

class strptime:
    def __call__(self, data, fmt):
        # Returns: [y m d H M S 0 0 0]
        if fmt == '%d %b %Y %H:%M:%S':
            fields = data.split(" ")
            fields[-1:] = fields[-1].split(":")
            return (int(fields[2]), _convert_month(fields[1]), int(fields[0]), int(fields[3]), int(fields[4]), int(fields[5]), 0, 0, 0)
        elif fmt == '%Y-%m-%d %H:%M:%S':
            fields = data.split(" ")
            fields[:1] = fields[0].split("-")
            fields[-1:] = fields[-1].split(":")
            return (int(fields[0]), int(fields[1]), int(fields[2]), int(fields[3]), int(fields[4]), int(fields[5]), 0, 0, 0)
        else:
            raise Exception("Error: this Jython workaround was given a format "
                "string it wasn't expecting: %s" % fmt)


def setup():
    try:
        time.strptime("31 Dec 1989 03:25:12", "%d %b %Y %H:%M:%S")
    except:
        # This function is broken -- install replacement
        time.strptime = strptime()
