import matplotlib.pyplot
from core.modules.vistrails_module import Module
from bases import MplPlot



def translate_color(c):
    return c.tuple

def translate_MplLegend_loc(val):
    translate_dict = {'right': 5, 'center left': 6, 'upper right': 1, 'lower right': 4, 'best': 0, 'center': 10, 'lower left': 3, 'center right': 7, 'upper left': 2, 'upper center': 9, 'lower center': 8}
    return translate_dict[val]
def translate_MplLinePlot_marker(val):
    translate_dict = {'tri_down marker': '1', 'pentagon marker': 'p', 'hline marker': '_', 'pixel marker': ',', 'triangle_up marker': '^', 'point marker': '.', 'square marker': 's', 'hexagon2 marker': 'H', 'tri_right marker': '4', 'plus marker': '+', 'vline marker': '|', 'triangle_left marker': '<', 'triangle_down marker': 'v', 'triangle_right marker': '>', 'tri_left marker': '3', 'x marker': 'x', 'circle marker': 'o', 'dashed line style': '--', 'hexagon1 marker': 'h', 'dash-dot line style': '-.', 'dotted line style': ':', 'solid line style': '-', 'tri_up marker': '2', 'star marker': '*', 'diamond marker': 'D', 'thin_diamond marker': 'd'}
    return translate_dict[val]

class MplAcorr(MplPlot):
    """call signature:

acorr(x, normed=True, detrend=mlab.detrend_none, usevlines=True,       maxlags=10, **kwargs)

Plot the autocorrelation of x.  If normed = True, normalize the data by the autocorrelation at 0-th lag.  x is detrended by the detrend callable (default no normalization).

Data are plotted as plot(lags, c, **kwargs)

Return value is a tuple (lags, c, line) where:

lags are a length 2*maxlags+1 lag vector

c is the 2*maxlags+1 auto correlation vector

line is a :class:`~matplotlib.lines.Line2D` instance returned by :meth:`plot`

The default linestyle is None and the default marker is 'o', though these can be overridden with keyword args. The cross correlation is performed with :func:`numpy.correlate` with mode = 2.

If usevlines is True, :meth:`~matplotlib.axes.Axes.vlines` rather than :meth:`~matplotlib.axes.Axes.plot` is used to draw vertical lines from the origin to the acorr.  Otherwise, the plot style is determined by the kwargs, which are :class:`~matplotlib.lines.Line2D` properties.

maxlags is a positive integer detailing the number of lags to show.  The default value of None will return all :math:`2        imes \mathrm{len}(x) - 1` lags.

The return value is a tuple (lags, c, linecol, b) where

linecol is the :class:`~matplotlib.collections.LineCollection`

b is the x-axis.

Example:

:func:`~matplotlib.pyplot.xcorr` above, and :func:`~matplotlib.pyplot.acorr` below.

Example:

Additional kwargs: hold = [True|False] overrides default hold state
    """
    _input_ports = [
              ("normed", "basic:Boolean",
                {'optional': True, 'defaults': "['True']"}),
              ("usevlines", "basic:Boolean",
                {'optional': True, 'defaults': "['True']"}),
              ("detrend", "basic:String",
                {'optional': True}),
              ("maxlags", "basic:Integer",
                {'optional': True, 'defaults': "['10']"}),
              ("x", "basic:String",
                {}),
              ("hold", "basic:String",
                {'optional': True}),
        ]

    _output_ports = [
        ("self", "(MplAcorr)"),
        ]
    

    def compute(self):
        # get args into args, kwargs
        # write out translations
        kwargs = {}            
        if self.hasInputFromPort('normed'):
            kwargs['normed'] = self.getInputFromPort('normed')
        if self.hasInputFromPort('usevlines'):
            kwargs['usevlines'] = self.getInputFromPort('usevlines')
        if self.hasInputFromPort('detrend'):
            kwargs['detrend'] = self.getInputFromPort('detrend')
        if self.hasInputFromPort('maxlags'):
            kwargs['maxlags'] = self.getInputFromPort('maxlags')
        kwargs['x'] = self.getInputFromPort('x')
        if self.hasInputFromPort('hold'):
            kwargs['hold'] = self.getInputFromPort('hold')
        # self.get_fig()
        matplotlib.pyplot.acorr(**kwargs)        

class MplArrow(MplPlot):
    """call signature:

arrow(x, y, dx, dy, **kwargs)

Draws arrow on specified axis from (x, y) to (x + dx, y + dy).

Optional kwargs control the arrow properties:

%(FancyArrow)s

Example:

Additional kwargs: hold = [True|False] overrides default hold state
    """
    _input_ports = [
              ("y", "basic:String",
                {}),
              ("x", "basic:String",
                {}),
              ("hold", "basic:String",
                {'optional': True}),
              ("dx", "basic:String",
                {}),
              ("dy", "basic:String",
                {}),
        ]

    _output_ports = [
        ("self", "(MplArrow)"),
        ]
    

    def compute(self):
        # get args into args, kwargs
        # write out translations
        kwargs = {}            
        kwargs['y'] = self.getInputFromPort('y')
        kwargs['x'] = self.getInputFromPort('x')
        if self.hasInputFromPort('hold'):
            kwargs['hold'] = self.getInputFromPort('hold')
        kwargs['dx'] = self.getInputFromPort('dx')
        kwargs['dy'] = self.getInputFromPort('dy')
        # self.get_fig()
        matplotlib.pyplot.arrow(**kwargs)        

class MplAxhline(MplPlot):
    """call signature:

axhline(y=0, xmin=0, xmax=1, **kwargs)

Axis Horizontal Line

Draw a horizontal line at y from xmin to xmax.  With the default values of xmin = 0 and xmax = 1, this line will always span the horizontal extent of the axes, regardless of the xlim settings, even if you change them, eg. with the :meth:`set_xlim` command.  That is, the horizontal extent is in axes coords: 0=left, 0.5=middle, 1.0=right but the y location is in data coordinates.

Return value is the :class:`~matplotlib.lines.Line2D` instance.  kwargs are the same as kwargs to plot, and can be used to control the line properties.  Eg.,

draw a thick red hline at y = 0 that spans the xrange

>>> axhline(linewidth=4, color='r')

draw a default hline at y = 1 that spans the xrange

>>> axhline(y=1)

draw a default hline at y = .5 that spans the the middle half of the xrange

>>> axhline(y=.5, xmin=0.25, xmax=0.75)

Valid kwargs are :class:`~matplotlib.lines.Line2D` properties, with the exception of 'transform':

%(Line2D)s

Additional kwargs: hold = [True|False] overrides default hold state
    """
    _input_ports = [
              ("y", "basic:Integer",
                {'optional': True, 'defaults': "['0']"}),
              ("xmin", "basic:Integer",
                {'optional': True, 'defaults': "['0']"}),
              ("hold", "basic:String",
                {'optional': True}),
              ("xmax", "basic:Integer",
                {'optional': True, 'defaults': "['1']"}),
              ("lineProperties", "MplLine2DProperties",
                {}),
        ]

    _output_ports = [
        ("self", "(MplAxhline)"),
        ]
    

    def compute(self):
        # get args into args, kwargs
        # write out translations
        kwargs = {}            
        if self.hasInputFromPort('y'):
            kwargs['y'] = self.getInputFromPort('y')
        if self.hasInputFromPort('xmin'):
            kwargs['xmin'] = self.getInputFromPort('xmin')
        if self.hasInputFromPort('hold'):
            kwargs['hold'] = self.getInputFromPort('hold')
        if self.hasInputFromPort('xmax'):
            kwargs['xmax'] = self.getInputFromPort('xmax')
        # self.get_fig()
        line = matplotlib.pyplot.axhline(**kwargs)
        if self.hasInputFromPort('lineProperties'):
            properties = self.getInputFromPort('lineProperties')
            properties.update_props(line)

class MplAxhspan(MplPlot):
    """call signature:

axhspan(ymin, ymax, xmin=0, xmax=1, **kwargs)

Axis Horizontal Span.

y coords are in data units and x coords are in axes (relative 0-1) units.

Draw a horizontal span (rectangle) from ymin to ymax. With the default values of xmin = 0 and xmax = 1, this always spans the xrange, regardless of the xlim settings, even if you change them, eg. with the :meth:`set_xlim` command. That is, the horizontal extent is in axes coords: 0=left, 0.5=middle, 1.0=right but the y location is in data coordinates.

Return value is a :class:`matplotlib.patches.Polygon` instance.

Examples:

draw a gray rectangle from y = 0.25-0.75 that spans the horizontal extent of the axes

>>> axhspan(0.25, 0.75, facecolor='0.5', alpha=0.5)

Valid kwargs are :class:`~matplotlib.patches.Polygon` properties:

%(Polygon)s

Example:

Additional kwargs: hold = [True|False] overrides default hold state
    """
    _input_ports = [
              ("xmin", "basic:Integer",
                {'optional': True, 'defaults': "['0']"}),
              ("hold", "basic:String",
                {'optional': True}),
              ("ymin", "basic:String",
                {}),
              ("ymax", "basic:String",
                {}),
              ("xmax", "basic:Integer",
                {'optional': True, 'defaults': "['1']"}),
        ]

    _output_ports = [
        ("self", "(MplAxhspan)"),
        ]
    

    def compute(self):
        # get args into args, kwargs
        # write out translations
        kwargs = {}            
        if self.hasInputFromPort('xmin'):
            kwargs['xmin'] = self.getInputFromPort('xmin')
        if self.hasInputFromPort('hold'):
            kwargs['hold'] = self.getInputFromPort('hold')
        kwargs['ymin'] = self.getInputFromPort('ymin')
        kwargs['ymax'] = self.getInputFromPort('ymax')
        if self.hasInputFromPort('xmax'):
            kwargs['xmax'] = self.getInputFromPort('xmax')
        # self.get_fig()
        matplotlib.pyplot.axhspan(**kwargs)        

class MplAxvline(MplPlot):
    """call signature:

axvline(x=0, ymin=0, ymax=1, **kwargs)

Axis Vertical Line

Draw a vertical line at x from ymin to ymax.  With the default values of ymin = 0 and ymax = 1, this line will always span the vertical extent of the axes, regardless of the ylim settings, even if you change them, eg. with the :meth:`set_ylim` command.  That is, the vertical extent is in axes coords: 0=bottom, 0.5=middle, 1.0=top but the x location is in data coordinates.

Return value is the :class:`~matplotlib.lines.Line2D` instance.  kwargs are the same as kwargs to plot, and can be used to control the line properties.  Eg.,

draw a thick red vline at x = 0 that spans the yrange

>>> axvline(linewidth=4, color='r')

draw a default vline at x = 1 that spans the yrange

>>> axvline(x=1)

draw a default vline at x = .5 that spans the the middle half of the yrange

>>> axvline(x=.5, ymin=0.25, ymax=0.75)

Valid kwargs are :class:`~matplotlib.lines.Line2D` properties, with the exception of 'transform':

%(Line2D)s

Additional kwargs: hold = [True|False] overrides default hold state
    """
    _input_ports = [
              ("x", "basic:Integer",
                {'optional': True, 'defaults': "['0']"}),
              ("hold", "basic:String",
                {'optional': True}),
              ("ymin", "basic:Integer",
                {'optional': True, 'defaults': "['0']"}),
              ("ymax", "basic:Integer",
                {'optional': True, 'defaults': "['1']"}),
              ("lineProperties", "MplLine2DProperties",
                {}),
        ]

    _output_ports = [
        ("self", "(MplAxvline)"),
        ]
    

    def compute(self):
        # get args into args, kwargs
        # write out translations
        kwargs = {}            
        if self.hasInputFromPort('x'):
            kwargs['x'] = self.getInputFromPort('x')
        if self.hasInputFromPort('hold'):
            kwargs['hold'] = self.getInputFromPort('hold')
        if self.hasInputFromPort('ymin'):
            kwargs['ymin'] = self.getInputFromPort('ymin')
        if self.hasInputFromPort('ymax'):
            kwargs['ymax'] = self.getInputFromPort('ymax')
        # self.get_fig()
        line = matplotlib.pyplot.axvline(**kwargs)
        if self.hasInputFromPort('lineProperties'):
            properties = self.getInputFromPort('lineProperties')
            properties.update_props(line)

class MplAxvspan(MplPlot):
    """call signature:

axvspan(xmin, xmax, ymin=0, ymax=1, **kwargs)

Axis Vertical Span.

x coords are in data units and y coords are in axes (relative 0-1) units.

Draw a vertical span (rectangle) from xmin to xmax.  With the default values of ymin = 0 and ymax = 1, this always spans the yrange, regardless of the ylim settings, even if you change them, eg. with the :meth:`set_ylim` command.  That is, the vertical extent is in axes coords: 0=bottom, 0.5=middle, 1.0=top but the y location is in data coordinates.

Return value is the :class:`matplotlib.patches.Polygon` instance.

Examples:

draw a vertical green translucent rectangle from x=1.25 to 1.55 that spans the yrange of the axes

>>> axvspan(1.25, 1.55, facecolor='g', alpha=0.5)

Valid kwargs are :class:`~matplotlib.patches.Polygon` properties:

%(Polygon)s

Additional kwargs: hold = [True|False] overrides default hold state
    """
    _input_ports = [
              ("xmin", "basic:String",
                {}),
              ("hold", "basic:String",
                {'optional': True}),
              ("ymin", "basic:Integer",
                {'optional': True, 'defaults': "['0']"}),
              ("ymax", "basic:Integer",
                {'optional': True, 'defaults': "['1']"}),
              ("xmax", "basic:String",
                {}),
        ]

    _output_ports = [
        ("self", "(MplAxvspan)"),
        ]
    

    def compute(self):
        # get args into args, kwargs
        # write out translations
        kwargs = {}            
        kwargs['xmin'] = self.getInputFromPort('xmin')
        if self.hasInputFromPort('hold'):
            kwargs['hold'] = self.getInputFromPort('hold')
        if self.hasInputFromPort('ymin'):
            kwargs['ymin'] = self.getInputFromPort('ymin')
        if self.hasInputFromPort('ymax'):
            kwargs['ymax'] = self.getInputFromPort('ymax')
        kwargs['xmax'] = self.getInputFromPort('xmax')
        # self.get_fig()
        matplotlib.pyplot.axvspan(**kwargs)        

class MplBar(MplPlot):
    """call signature:

bar(left, height, width=0.8, bottom=0, **kwargs)

Make a bar plot with rectangles bounded by:



left, height, width, and bottom can be either scalars or sequences

Return value is a list of :class:`matplotlib.patches.Rectangle` instances.

Required arguments:



Optional keyword arguments:



For vertical bars, align = 'edge' aligns bars by their left edges in left, while align = 'center' interprets these values as the x coordinates of the bar centers. For horizontal bars, align = 'edge' aligns bars by their bottom edges in bottom, while align = 'center' interprets these values as the y coordinates of the bar centers.

The optional arguments color, edgecolor, linewidth, xerr, and yerr can be either scalars or sequences of length equal to the number of bars.  This enables you to use bar as the basis for stacked bar charts, or candlestick plots. Detail: xerr and yerr are passed directly to :meth:`errorbar`, so they can also have shape 2xN for independent specification of lower and upper errors.

Other optional kwargs:

%(Rectangle)s

Example: A stacked bar chart.

Additional kwargs: hold = [True|False] overrides default hold state
    """
    _input_ports = [
              ("edgecolor", "basic:Color",
                {'optional': True, 'docstring': 'the colors of the bar edges'}),
              ("linewidth", "basic:String",
                {'optional': True, 'docstring': "width of bar edges; None means use default linewidth; 0 means don't draw edges."}),
              ("capsize", "basic:Integer",
                {'optional': True, 'docstring': '(default 3) determines the length in points of the error bar caps', 'defaults': "['3']"}),
              ("orientation", "basic:String",
                {'entry_types': "['enum']", 'docstring': "'vertical' | 'horizontal'", 'values': "[['vertical', 'horizontal']]", 'optional': True}),
              ("bottom", "None",
                {'optional': True, 'docstring': 'the y coordinates of the bottom edges of the bars'}),
              ("color", "basic:Color",
                {'optional': True, 'docstring': 'the colors of the bars'}),
              ("xerr", "basic:String",
                {'optional': True, 'docstring': 'if not None, will be used to generate errorbars on the bar chart'}),
              ("align", "basic:String",
                {'entry_types': "['enum']", 'docstring': "'edge' (default) | 'center'", 'values': "[['edge', 'center']]", 'optional': True, 'defaults': "['edge']"}),
              ("ecolor", "basic:Color",
                {'optional': True, 'docstring': 'specifies the color of any errorbar'}),
              ("height", "basic:String",
                {'docstring': 'the heights of the bars'}),
              ("width", "basic:Float",
                {'optional': True, 'docstring': 'the widths of the bars', 'defaults': "['0.8']"}),
              ("error_kw", "basic:String",
                {'optional': True, 'docstring': 'dictionary of kwargs to be passed to errorbar method. ecolor and capsize may be specified here rather than as independent kwargs.'}),
              ("log", "basic:Boolean",
                {'optional': True, 'docstring': '[False|True] False (default) leaves the orientation axis as-is; True sets it to log scale', 'defaults': "['False']"}),
              ("hold", "basic:String",
                {'optional': True}),
              ("yerr", "basic:String",
                {'optional': True, 'docstring': 'if not None, will be used to generate errorbars on the bar chart'}),
              ("left", "basic:String",
                {'docstring': 'the x coordinates of the left sides of the bars'}),
              ("rectangleProperties", "MplRectangleProperties",
                {}),
        ]

    _output_ports = [
        ("self", "(MplBar)"),
        ]
    

    def compute(self):
        # get args into args, kwargs
        # write out translations
        kwargs = {}            
        if self.hasInputFromPort('edgecolor'):
            kwargs['edgecolor'] = self.getInputFromPort('edgecolor')
            kwargs['edgecolor'] = translate_color(kwargs['edgecolor'])
        if self.hasInputFromPort('linewidth'):
            kwargs['linewidth'] = self.getInputFromPort('linewidth')
        if self.hasInputFromPort('capsize'):
            kwargs['capsize'] = self.getInputFromPort('capsize')
        if self.hasInputFromPort('orientation'):
            kwargs['orientation'] = self.getInputFromPort('orientation')
        if self.hasInputFromPort('bottom'):
            kwargs['bottom'] = self.getInputFromPort('bottom')
        if self.hasInputFromPort('color'):
            kwargs['color'] = self.getInputFromPort('color')
            kwargs['color'] = translate_color(kwargs['color'])
        if self.hasInputFromPort('xerr'):
            kwargs['xerr'] = self.getInputFromPort('xerr')
        if self.hasInputFromPort('align'):
            kwargs['align'] = self.getInputFromPort('align')
        if self.hasInputFromPort('ecolor'):
            kwargs['ecolor'] = self.getInputFromPort('ecolor')
            kwargs['ecolor'] = translate_color(kwargs['ecolor'])
        kwargs['height'] = self.getInputFromPort('height')
        if self.hasInputFromPort('width'):
            kwargs['width'] = self.getInputFromPort('width')
        if self.hasInputFromPort('error_kw'):
            kwargs['error_kw'] = self.getInputFromPort('error_kw')
        if self.hasInputFromPort('log'):
            kwargs['log'] = self.getInputFromPort('log')
        if self.hasInputFromPort('hold'):
            kwargs['hold'] = self.getInputFromPort('hold')
        if self.hasInputFromPort('yerr'):
            kwargs['yerr'] = self.getInputFromPort('yerr')
        kwargs['left'] = self.getInputFromPort('left')
        # self.get_fig()
        rectangles = matplotlib.pyplot.bar(**kwargs)
        if self.hasInputFromPort('rectangleProperties'):
            properties = self.getInputFromPort('rectangleProperties')
            properties.update_props(rectangles)

class MplBarh(MplPlot):
    """call signature:

barh(bottom, width, height=0.8, left=0, **kwargs)

Make a horizontal bar plot with rectangles bounded by:



bottom, width, height, and left can be either scalars or sequences

Return value is a list of :class:`matplotlib.patches.Rectangle` instances.

Required arguments:



Optional keyword arguments:



Setting align = 'edge' aligns bars by their bottom edges in bottom, while align = 'center' interprets these values as the y coordinates of the bar centers.

The optional arguments color, edgecolor, linewidth, xerr, and yerr can be either scalars or sequences of length equal to the number of bars.  This enables you to use barh as the basis for stacked bar charts, or candlestick plots.

other optional kwargs:

%(Rectangle)s

Additional kwargs: hold = [True|False] overrides default hold state
    """
    _input_ports = [
              ("edgecolor", "basic:Color",
                {'optional': True, 'docstring': 'the colors of the bar edges'}),
              ("linewidth", "basic:String",
                {'optional': True, 'docstring': "width of bar edges; None means use default linewidth; 0 means don't draw edges."}),
              ("capsize", "basic:Integer",
                {'optional': True, 'docstring': '(default 3) determines the length in points of the error bar caps', 'defaults': "['3']"}),
              ("log", "basic:Boolean",
                {'optional': True, 'docstring': '[False|True] False (default) leaves the horizontal axis as-is; True sets it to log scale', 'defaults': "['False']"}),
              ("bottom", "basic:String",
                {'docstring': 'the vertical positions of the bottom edges of the bars'}),
              ("color", "basic:Color",
                {'optional': True, 'docstring': 'the colors of the bars'}),
              ("xerr", "basic:String",
                {'optional': True, 'docstring': 'if not None, will be used to generate errorbars on the bar chart'}),
              ("align", "basic:String",
                {'entry_types': "['enum']", 'docstring': "'edge' (default) | 'center'", 'values': "[['edge', 'center']]", 'optional': True, 'defaults': "['edge']"}),
              ("ecolor", "basic:Color",
                {'optional': True, 'docstring': 'specifies the color of any errorbar'}),
              ("height", "basic:Float",
                {'optional': True, 'docstring': 'the heights (thicknesses) of the bars', 'defaults': "['0.8']"}),
              ("width", "basic:String",
                {'docstring': 'the lengths of the bars'}),
              ("hold", "basic:String",
                {'optional': True}),
              ("yerr", "basic:String",
                {'optional': True, 'docstring': 'if not None, will be used to generate errorbars on the bar chart'}),
              ("left", "None",
                {'optional': True, 'docstring': 'the x coordinates of the left edges of the bars'}),
        ]

    _output_ports = [
        ("self", "(MplBarh)"),
        ]
    

    def compute(self):
        # get args into args, kwargs
        # write out translations
        kwargs = {}            
        if self.hasInputFromPort('edgecolor'):
            kwargs['edgecolor'] = self.getInputFromPort('edgecolor')
            kwargs['edgecolor'] = translate_color(kwargs['edgecolor'])
        if self.hasInputFromPort('linewidth'):
            kwargs['linewidth'] = self.getInputFromPort('linewidth')
        if self.hasInputFromPort('capsize'):
            kwargs['capsize'] = self.getInputFromPort('capsize')
        if self.hasInputFromPort('log'):
            kwargs['log'] = self.getInputFromPort('log')
        kwargs['bottom'] = self.getInputFromPort('bottom')
        if self.hasInputFromPort('color'):
            kwargs['color'] = self.getInputFromPort('color')
            kwargs['color'] = translate_color(kwargs['color'])
        if self.hasInputFromPort('xerr'):
            kwargs['xerr'] = self.getInputFromPort('xerr')
        if self.hasInputFromPort('align'):
            kwargs['align'] = self.getInputFromPort('align')
        if self.hasInputFromPort('ecolor'):
            kwargs['ecolor'] = self.getInputFromPort('ecolor')
            kwargs['ecolor'] = translate_color(kwargs['ecolor'])
        if self.hasInputFromPort('height'):
            kwargs['height'] = self.getInputFromPort('height')
        kwargs['width'] = self.getInputFromPort('width')
        if self.hasInputFromPort('hold'):
            kwargs['hold'] = self.getInputFromPort('hold')
        if self.hasInputFromPort('yerr'):
            kwargs['yerr'] = self.getInputFromPort('yerr')
        if self.hasInputFromPort('left'):
            kwargs['left'] = self.getInputFromPort('left')
        # self.get_fig()
        matplotlib.pyplot.barh(**kwargs)        

class MplBroken_barh(MplPlot):
    """call signature:

broken_barh(self, xranges, yrange, **kwargs)

A collection of horizontal bars spanning yrange with a sequence of xranges.

Required arguments:



kwargs are :class:`matplotlib.collections.BrokenBarHCollection` properties:

%(BrokenBarHCollection)s

these can either be a single argument, ie:

facecolors = 'black'

or a sequence of arguments for the various bars, ie:

facecolors = ('black', 'red', 'green')

Example:

Additional kwargs: hold = [True|False] overrides default hold state
    """
    _input_ports = [
              ("xranges", "basic:List",
                {'docstring': 'sequence of (xmin, xwidth)'}),
              ("hold", "basic:String",
                {'optional': True}),
              ("yrange", "basic:List",
                {'docstring': 'sequence of (ymin, ywidth)'}),
        ]

    _output_ports = [
        ("self", "(MplBroken_barh)"),
        ]
    

    def compute(self):
        # get args into args, kwargs
        # write out translations
        kwargs = {}            
        kwargs['xranges'] = self.getInputFromPort('xranges')
        if self.hasInputFromPort('hold'):
            kwargs['hold'] = self.getInputFromPort('hold')
        kwargs['yrange'] = self.getInputFromPort('yrange')
        # self.get_fig()
        matplotlib.pyplot.broken_barh(**kwargs)        

class MplBoxplot(MplPlot):
    """call signature:

boxplot(x, notch=0, sym='+', vert=1, whis=1.5,         positions=None, widths=None, patch_artist=False)

Make a box and whisker plot for each column of x or each vector in sequence x.  The box extends from the lower to upper quartile values of the data, with a line at the median. The whiskers extend from the box to show the range of the data.  Flier points are those past the end of the whiskers.

x is an array or a sequence of vectors.

notch = 0 (default) produces a rectangular box plot.

notch = 1 will produce a notched box plot

sym (default 'b+') is the default symbol for flier points. Enter an empty string ('') if you don't want to show fliers.

vert = 1 (default) makes the boxes vertical.

vert = 0 makes horizontal boxes.  This seems goofy, but that's how MATLAB did it.

whis (default 1.5) defines the length of the whiskers as a function of the inner quartile range.  They extend to the most extreme data point within ( whis*(75%-25%) ) data range.

bootstrap (default None) specifies whether to bootstrap the confidence intervals around the median for notched boxplots. If bootstrap==None, no bootstrapping is performed, and notches are calculated using a Gaussian-based asymptotic approximation (see McGill, R., Tukey, J.W., and Larsen, W.A., 1978, and Kendall and Stuart, 1967). Otherwise, bootstrap specifies the number of times to bootstrap the median to determine it's 95% confidence intervals. Values between 1000 and 10000 are recommended.

positions (default 1,2,...,n) sets the horizontal positions of the boxes. The ticks and limits are automatically set to match the positions.

widths is either a scalar or a vector and sets the width of each box. The default is 0.5, or 0.15*(distance between extreme positions) if that is smaller.

patch_artist = False (default) produces boxes with the Line2D artist

patch_artist = True produces boxes with the Patch artist

Returns a dictionary mapping each component of the boxplot to a list of the :class:`matplotlib.lines.Line2D` instances created.

Example:

Additional kwargs: hold = [True|False] overrides default hold state
    """
    _input_ports = [
              ("hold", "basic:String",
                {'optional': True}),
              ("vert", "basic:Integer",
                {'optional': True, 'defaults': "['1']"}),
              ("positions", "basic:String",
                {'optional': True}),
              ("bootstrap", "basic:String",
                {'optional': True}),
              ("sym", "basic:String",
                {'optional': True, 'defaults': "['b+']"}),
              ("widths", "basic:String",
                {'optional': True}),
              ("patch_artist", "basic:Boolean",
                {'optional': True, 'defaults': "['False']"}),
              ("x", "basic:List",
                {}),
              ("notch", "basic:Integer",
                {'optional': True, 'defaults': "['0']"}),
              ("whis", "basic:Float",
                {'optional': True, 'defaults': "['1.5']"}),
              ("boxProperties", "MplLine2DProperties",
                {}),
              ("flierProperties", "MplLine2DProperties",
                {}),
              ("capProperties", "MplLine2DProperties",
                {}),
              ("medianProperties", "MplLine2DProperties",
                {}),
              ("boxPatchProperties", "MplPathPatchProperties",
                {}),
              ("whiskerProperties", "MplLine2DProperties",
                {}),
        ]

    _output_ports = [
        ("self", "(MplBoxplot)"),
        ]
    

    def compute(self):
        # get args into args, kwargs
        # write out translations
        kwargs = {}            
        if self.hasInputFromPort('hold'):
            kwargs['hold'] = self.getInputFromPort('hold')
        if self.hasInputFromPort('vert'):
            kwargs['vert'] = self.getInputFromPort('vert')
        if self.hasInputFromPort('positions'):
            kwargs['positions'] = self.getInputFromPort('positions')
        if self.hasInputFromPort('bootstrap'):
            kwargs['bootstrap'] = self.getInputFromPort('bootstrap')
        if self.hasInputFromPort('sym'):
            kwargs['sym'] = self.getInputFromPort('sym')
        if self.hasInputFromPort('widths'):
            kwargs['widths'] = self.getInputFromPort('widths')
        if self.hasInputFromPort('patch_artist'):
            kwargs['patch_artist'] = self.getInputFromPort('patch_artist')
        kwargs['x'] = self.getInputFromPort('x')
        if self.hasInputFromPort('notch'):
            kwargs['notch'] = self.getInputFromPort('notch')
        if self.hasInputFromPort('whis'):
            kwargs['whis'] = self.getInputFromPort('whis')
        # self.get_fig()
        output = matplotlib.pyplot.boxplot(**kwargs)        
        if 'patch_artist' in kwargs and kwargs['patch_artist']:
            output['boxPatches'] = output['boxes']
            output['boxes'] = []
        else:
            output['boxPatches'] = []
        boxes = output['boxes']
        fliers = output['fliers']
        caps = output['caps']
        medians = output['medians']
        boxPatches = output['boxPatches']
        whiskers = output['whiskers']
        if self.hasInputFromPort('boxProperties'):
            properties = self.getInputFromPort('boxProperties')
            properties.update_props(boxes)
        if self.hasInputFromPort('flierProperties'):
            properties = self.getInputFromPort('flierProperties')
            properties.update_props(fliers)
        if self.hasInputFromPort('capProperties'):
            properties = self.getInputFromPort('capProperties')
            properties.update_props(caps)
        if self.hasInputFromPort('medianProperties'):
            properties = self.getInputFromPort('medianProperties')
            properties.update_props(medians)
        if self.hasInputFromPort('boxPatchProperties'):
            properties = self.getInputFromPort('boxPatchProperties')
            properties.update_props(boxPatches)
        if self.hasInputFromPort('whiskerProperties'):
            properties = self.getInputFromPort('whiskerProperties')
            properties.update_props(whiskers)

class MplCohere(MplPlot):
    """call signature:

cohere(x, y, NFFT=256, Fs=2, Fc=0, detrend = mlab.detrend_none,        window = mlab.window_hanning, noverlap=0, pad_to=None,        sides='default', scale_by_freq=None, **kwargs)

:meth:`cohere` the coherence between x and y.  Coherence is the normalized cross spectral density:

%(PSD)s



The return value is a tuple (Cxy, f), where f are the frequencies of the coherence vector.

kwargs are applied to the lines.

References:

Bendat & Piersol -- Random Data: Analysis and Measurement Procedures, John Wiley & Sons (1986)

kwargs control the :class:`~matplotlib.lines.Line2D` properties of the coherence plot:

%(Line2D)s

Example:

Additional kwargs: hold = [True|False] overrides default hold state
    """
    _input_ports = [
              ("Fs", "basic:Integer",
                {'optional': True, 'defaults': "['2']"}),
              ("pad_to", "basic:String",
                {'optional': True}),
              ("scale_by_freq", "basic:String",
                {'optional': True}),
              ("detrend", "basic:String",
                {'optional': True, 'defaults': "['<function detrend_none at 0x101f3b0c8>']"}),
              ("window", "basic:String",
                {'optional': True, 'defaults': "['<function window_hanning at 0x101f367d0>']"}),
              ("Fc", "basic:Integer",
                {'optional': True, 'defaults': "['0']"}),
              ("NFFT", "basic:Integer",
                {'optional': True, 'defaults': "['256']"}),
              ("y", "basic:String",
                {}),
              ("x", "basic:String",
                {}),
              ("hold", "basic:String",
                {'optional': True}),
              ("sides", "basic:String",
                {'optional': True, 'defaults': "['default']"}),
              ("noverlap", "basic:Integer",
                {'optional': True, 'defaults': "['0']"}),
        ]

    _output_ports = [
        ("self", "(MplCohere)"),
        ]
    

    def compute(self):
        # get args into args, kwargs
        # write out translations
        kwargs = {}            
        if self.hasInputFromPort('Fs'):
            kwargs['Fs'] = self.getInputFromPort('Fs')
        if self.hasInputFromPort('pad_to'):
            kwargs['pad_to'] = self.getInputFromPort('pad_to')
        if self.hasInputFromPort('scale_by_freq'):
            kwargs['scale_by_freq'] = self.getInputFromPort('scale_by_freq')
        if self.hasInputFromPort('detrend'):
            kwargs['detrend'] = self.getInputFromPort('detrend')
        if self.hasInputFromPort('window'):
            kwargs['window'] = self.getInputFromPort('window')
        if self.hasInputFromPort('Fc'):
            kwargs['Fc'] = self.getInputFromPort('Fc')
        if self.hasInputFromPort('NFFT'):
            kwargs['NFFT'] = self.getInputFromPort('NFFT')
        kwargs['y'] = self.getInputFromPort('y')
        kwargs['x'] = self.getInputFromPort('x')
        if self.hasInputFromPort('hold'):
            kwargs['hold'] = self.getInputFromPort('hold')
        if self.hasInputFromPort('sides'):
            kwargs['sides'] = self.getInputFromPort('sides')
        if self.hasInputFromPort('noverlap'):
            kwargs['noverlap'] = self.getInputFromPort('noverlap')
        # self.get_fig()
        matplotlib.pyplot.cohere(**kwargs)        

class MplClabel(MplPlot):
    """call signature:

clabel(cs, **kwargs)

adds labels to line contours in cs, where cs is a :class:`~matplotlib.contour.ContourSet` object returned by contour.

clabel(cs, v, **kwargs)

only labels contours listed in v.

Optional keyword arguments:



Additional kwargs: hold = [True|False] overrides default hold state
    """
    _input_ports = [
              ("inline_spacing", "basic:String",
                {'optional': True, 'docstring': 'space in pixels to leave on each side of label when placing inline.  Defaults to 5.  This spacing will be exact for labels at locations where the contour is straight, less so for labels on curved contours.'}),
              ("use_clabeltext", "basic:String",
                {'optional': True, 'docstring': 'if True (default is False), ClabelText class (instead of matplotlib.Text) is used to create labels. ClabelText recalculates rotation angles of texts during the drawing time, therefore this can be used if aspect of the axes changes.', 'defaults': "['False)']"}),
              ("fmt", "basic:String",
                {'optional': True, 'docstring': "a format string for the label. Default is '%1.3f' Alternatively, this can be a dictionary matching contour levels with arbitrary strings to use for each contour level (i.e., fmt[level]=string), or it can be any callable, such as a :class:`~matplotlib.ticker.Formatter` instance, that returns a string when called with a numeric contour level.", 'defaults': "['%1.3f']"}),
              ("manual", "basic:String",
                {'optional': True, 'docstring': 'if True, contour labels will be placed manually using mouse clicks.  Click the first button near a contour to add a label, click the second button (or potentially both mouse buttons at once) to finish adding labels.  The third button can be used to remove the last label added, but only if labels are not inline.  Alternatively, the keyboard can be used to select label locations (enter to end label placement, delete or backspace act like the third mouse button, and any other key will select a label location).'}),
              ("cs", "basic:String",
                {}),
              ("colors", "basic:Color",
                {'optional': True, 'docstring': "if None, the color of each label matches the color of the corresponding contour\n\nif one string color, e.g. colors = 'r' or colors = 'red', all labels will be plotted in this color\n\nif a tuple of matplotlib color args (string, float, rgb, etc), different labels will be plotted in different colors in the order specified"}),
              ("fontsize", "basic:String",
                {'optional': True, 'docstring': 'See http://matplotlib.sf.net/fonts.html'}),
              ("rightside_up", "basic:Boolean",
                {'optional': True, 'docstring': 'if True (default), label rotations will always be plus or minus 90 degrees from level.', 'defaults': "['True']"}),
              ("CS", "basic:String",
                {}),
              ("inline", "basic:Boolean",
                {'optional': True, 'docstring': 'controls whether the underlying contour is removed or not. Default is True.', 'defaults': "['True']"}),
        ]

    _output_ports = [
        ("self", "(MplClabel)"),
        ]
    

    def compute(self):
        # get args into args, kwargs
        # write out translations
        kwargs = {}            
        if self.hasInputFromPort('inline_spacing'):
            kwargs['inline_spacing'] = self.getInputFromPort('inline_spacing')
        if self.hasInputFromPort('use_clabeltext'):
            kwargs['use_clabeltext'] = self.getInputFromPort('use_clabeltext')
        if self.hasInputFromPort('fmt'):
            kwargs['fmt'] = self.getInputFromPort('fmt')
        if self.hasInputFromPort('manual'):
            kwargs['manual'] = self.getInputFromPort('manual')
        kwargs['cs'] = self.getInputFromPort('cs')
        if self.hasInputFromPort('colors'):
            kwargs['colors'] = self.getInputFromPort('colors')
            kwargs['colors'] = translate_color(kwargs['colors'])
        if self.hasInputFromPort('fontsize'):
            kwargs['fontsize'] = self.getInputFromPort('fontsize')
        if self.hasInputFromPort('rightside_up'):
            kwargs['rightside_up'] = self.getInputFromPort('rightside_up')
        kwargs['CS'] = self.getInputFromPort('CS')
        if self.hasInputFromPort('inline'):
            kwargs['inline'] = self.getInputFromPort('inline')
        # self.get_fig()
        matplotlib.pyplot.clabel(**kwargs)        

class MplContour(MplPlot):
    """:func:`~matplotlib.pyplot.contour` and :func:`~matplotlib.pyplot.contourf` draw contour lines and filled contours, respectively.  Except as noted, function signatures and return values are the same for both versions.

:func:`~matplotlib.pyplot.contourf` differs from the MATLAB version in that it does not draw the polygon edges. To draw edges, add line contours with calls to :func:`~matplotlib.pyplot.contour`.

call signatures:

contour(Z)

make a contour plot of an array Z. The level values are chosen automatically.

contour(X,Y,Z)

X, Y specify the (x, y) coordinates of the surface

contour(Z,N) contour(X,Y,Z,N)

contour N automatically-chosen levels.

contour(Z,V) contour(X,Y,Z,V)

draw contour lines at the values specified in sequence V

contourf(..., V)

fill the (len(V)-1) regions between the values in V

contour(Z, **kwargs)

Use keyword args to control colors, linewidth, origin, cmap ... see below for more details.

X and Y must both be 2-D with the same shape as Z, or they must both be 1-D such that len(X) is the number of columns in Z and len(Y) is the number of rows in Z.

C = contour(...) returns a :class:`~matplotlib.contour.QuadContourSet` object.

Optional keyword arguments:



contour-only keyword arguments:



contourf-only keyword arguments:



Note: contourf fills intervals that are closed at the top; that is, for boundaries z1 and z2, the filled region is:

z1 < z <= z2

There is one exception: if the lowest boundary coincides with the minimum value of the z array, then that minimum value will be included in the lowest interval.

Examples:

Additional kwargs: hold = [True|False] overrides default hold state
    """
    _input_ports = [
              ("origin", "basic:String",
                {'entry_types': "['enum']", 'docstring': "If None, the first value of Z will correspond to the lower left corner, location (0,0). If 'image', the rc value for image.origin will be used.\n\nThis keyword is not active if X and Y are specified in the call to contour.", 'values': "[['upper', 'lower', 'image']]", 'optional': True}),
              ("xunits", "basic:String",
                {'entry_types': "['enum']", 'docstring': 'Override axis units by specifying an instance of a :class:`matplotlib.units.ConversionInterface`.', 'values': "[['registered units']]", 'optional': True}),
              ("linestyles", "basic:String",
                {'entry_types': "['enum']", 'docstring': "If linestyles is None, the 'solid' is used.\n\nlinestyles can also be an iterable of the above strings specifying a set of linestyles to be used. If this iterable is shorter than the number of contour levels it will be repeated as necessary.\n\nIf contour is using a monochrome colormap and the contour level is less than 0, then the linestyle specified in contour.negative_linestyle in matplotlibrc will be used.", 'values': "[['solid', 'dashed', 'dashdot', 'dotted']]", 'optional': True}),
              ("extend", "basic:String",
                {'entry_types': "['enum']", 'docstring': "Unless this is 'neither', contour levels are automatically added to one or both ends of the range so that all data are included. These added ranges are then mapped to the special colormap values which default to the ends of the colormap range, but can be set via :meth:`matplotlib.colors.Colormap.set_under` and :meth:`matplotlib.colors.Colormap.set_over` methods.", 'values': "[['neither', 'both', 'min', 'max']]", 'optional': True}),
              ("levelsSequence", "basic:List",
                {'optional': True, 'docstring': 'A list of floating point numbers indicating the level curves to draw; eg to draw just the zero contour pass levels=[0]'}),
              ("levelsScalar", "basic:Float",
               {'docstring': 'A list of floating point numbers indicating the level curves to draw; eg to draw just the zero contour pass levels=[0]', 'optional': True}),
              ("linewidths", "basic:String",
                {'entry_types': "['enum']", 'docstring': 'If linewidths is None, the default width in lines.linewidth in matplotlibrc is used.\n\nIf a number, all levels will be plotted with this linewidth.\n\nIf a tuple, different levels will be plotted with different linewidths in the order specified', 'values': "[['number', 'tuple of numbers']]", 'optional': True}),
              ("locator", "basic:String",
                {'optional': True, 'docstring': 'If locator is None, the default :class:`~matplotlib.ticker.MaxNLocator` is used. The locator is used to determine the contour levels if they are not given explicitly via the V argument.'}),
              ("colors", "basic:Color",
                {'optional': True, 'docstring': "If None, the colormap specified by cmap will be used.\n\nIf a string, like 'r' or 'red', all levels will be plotted in this color.\n\nIf a tuple of matplotlib color args (string, float, rgb, etc), different levels will be plotted in different colors in the order specified."}),
              ("cmap", "basic:String",
                {'optional': True, 'docstring': 'A cm :class:`~matplotlib.cm.Colormap` instance or None. If cmap is None and colors is None, a default Colormap is used.'}),
              ("yunits", "basic:String",
                {'optional': True, 'docstring': 'Override axis units by specifying an instance of a :class:`matplotlib.units.ConversionInterface`.'}),
              ("extent", "basic:String",
                {'entry_types': "['enum']", 'docstring': 'If origin is not None, then extent is interpreted as in :func:`matplotlib.pyplot.imshow`: it gives the outer pixel boundaries. In this case, the position of Z[0,0] is the center of the pixel, not a corner. If origin is None, then (x0, y0) is the position of Z[0,0], and (x1, y1) is the position of Z[-1,-1].\n\nThis keyword is not active if X and Y are specified in the call to contour.', 'values': "[['(x0,x1,y0,y1)']]", 'optional': True}),
              ("nchunk", "basic:Integer",
                {'entry_types': "['enum']", 'docstring': 'If 0, no subdivision of the domain. Specify a positive integer to divide the domain into subdomains of roughly nchunk by nchunk points. This may never actually be advantageous, so this option may be removed. Chunking introduces artifacts at the chunk boundaries unless antialiased is False.', 'values': '[[0]]', 'optional': True}),
              ("alpha", "basic:Float",
                {'optional': True, 'docstring': 'The alpha blending value'}),
              ("antialiased", "basic:Boolean",
                {'optional': True, 'docstring': "enable antialiasing, overriding the defaults.  For filled contours, the default is True.  For line contours, it is taken from rcParams['lines.antialiased'].", 'defaults': "['True']"}),
              ("norm", "basic:String",
                {'optional': True, 'docstring': 'A :class:`matplotlib.colors.Normalize` instance for scaling data values to colors. If norm is None and colors is None, the default linear scaling is used.'}),
        ]

    _output_ports = [
        ("self", "(MplContour)"),
        ]
    

    def compute(self):
        # get args into args, kwargs
        # write out translations
        kwargs = {}            
        if self.hasInputFromPort('origin'):
            kwargs['origin'] = self.getInputFromPort('origin')
        if self.hasInputFromPort('xunits'):
            kwargs['xunits'] = self.getInputFromPort('xunits')
        if self.hasInputFromPort('linestyles'):
            kwargs['linestyles'] = self.getInputFromPort('linestyles')
        if self.hasInputFromPort('extend'):
            kwargs['extend'] = self.getInputFromPort('extend')
        if self.hasInputFromPort('levelsSequence'):
            kwargs['levels'] = self.getInputFromPort('levelsSequence')
        elif self.hasInputFromPort('levelsScalar'):
            kwargs['levels'] = self.getInputFromPort('levelsScalar')
        if self.hasInputFromPort('linewidths'):
            kwargs['linewidths'] = self.getInputFromPort('linewidths')
        if self.hasInputFromPort('locator'):
            kwargs['locator'] = self.getInputFromPort('locator')
        if self.hasInputFromPort('colors'):
            kwargs['colors'] = self.getInputFromPort('colors')
            kwargs['colors'] = translate_color(kwargs['colors'])
        if self.hasInputFromPort('cmap'):
            kwargs['cmap'] = self.getInputFromPort('cmap')
        if self.hasInputFromPort('yunits'):
            kwargs['yunits'] = self.getInputFromPort('yunits')
        if self.hasInputFromPort('extent'):
            kwargs['extent'] = self.getInputFromPort('extent')
        if self.hasInputFromPort('nchunk'):
            kwargs['nchunk'] = self.getInputFromPort('nchunk')
        if self.hasInputFromPort('alpha'):
            kwargs['alpha'] = self.getInputFromPort('alpha')
        if self.hasInputFromPort('antialiased'):
            kwargs['antialiased'] = self.getInputFromPort('antialiased')
        if self.hasInputFromPort('norm'):
            kwargs['norm'] = self.getInputFromPort('norm')
        # self.get_fig()
        matplotlib.pyplot.contour(**kwargs)        

class MplContourf(MplPlot):
    """:func:`~matplotlib.pyplot.contour` and :func:`~matplotlib.pyplot.contourf` draw contour lines and filled contours, respectively.  Except as noted, function signatures and return values are the same for both versions.

:func:`~matplotlib.pyplot.contourf` differs from the MATLAB version in that it does not draw the polygon edges. To draw edges, add line contours with calls to :func:`~matplotlib.pyplot.contour`.

call signatures:

contour(Z)

make a contour plot of an array Z. The level values are chosen automatically.

contour(X,Y,Z)

X, Y specify the (x, y) coordinates of the surface

contour(Z,N) contour(X,Y,Z,N)

contour N automatically-chosen levels.

contour(Z,V) contour(X,Y,Z,V)

draw contour lines at the values specified in sequence V

contourf(..., V)

fill the (len(V)-1) regions between the values in V

contour(Z, **kwargs)

Use keyword args to control colors, linewidth, origin, cmap ... see below for more details.

X and Y must both be 2-D with the same shape as Z, or they must both be 1-D such that len(X) is the number of columns in Z and len(Y) is the number of rows in Z.

C = contour(...) returns a :class:`~matplotlib.contour.QuadContourSet` object.

Optional keyword arguments:

extent: [ None | (x0,x1,y0,y1) ]

If origin is not None, then extent is interpreted as in :func:`matplotlib.pyplot.imshow`: it gives the outer pixel boundaries. In this case, the position of Z[0,0] is the center of the pixel, not a corner. If origin is None, then (x0, y0) is the position of Z[0,0], and (x1, y1) is the position of Z[-1,-1].

This keyword is not active if X and Y are specified in the call to contour.

contour-only keyword arguments:



contourf-only keyword arguments:



Note: contourf fills intervals that are closed at the top; that is, for boundaries z1 and z2, the filled region is:

z1 < z <= z2

There is one exception: if the lowest boundary coincides with the minimum value of the z array, then that minimum value will be included in the lowest interval.

Examples:

Additional kwargs: hold = [True|False] overrides default hold state
    """
    _input_ports = [
              ("origin", "basic:String",
                {'entry_types': "['enum']", 'docstring': "If None, the first value of Z will correspond to the lower left corner, location (0,0). If 'image', the rc value for image.origin will be used.\n\nThis keyword is not active if X and Y are specified in the call to contour.", 'values': "[['upper', 'lower', 'image']]", 'optional': True}),
              ("linestyles", "basic:String",
                {'entry_types': "['enum']", 'docstring': "If linestyles is None, the 'solid' is used.\n\nlinestyles can also be an iterable of the above strings specifying a set of linestyles to be used. If this iterable is shorter than the number of contour levels it will be repeated as necessary.\n\nIf contour is using a monochrome colormap and the contour level is less than 0, then the linestyle specified in contour.negative_linestyle in matplotlibrc will be used.", 'values': "[['solid', 'dashed', 'dashdot', 'dotted']]", 'optional': True}),
              ("levelsSequence", "basic:List",
                {'optional': True, 'docstring': 'A list of floating point numbers indicating the level curves to draw; eg to draw just the zero contour pass levels=[0]'}),
              ("levelsScalar", "basic:Float",
               {'docstring': 'A list of floating point numbers indicating the level curves to draw; eg to draw just the zero contour pass levels=[0]', 'optional': True}),
              ("linewidths", "basic:String",
                {'entry_types': "['enum']", 'docstring': 'If linewidths is None, the default width in lines.linewidth in matplotlibrc is used.\n\nIf a number, all levels will be plotted with this linewidth.\n\nIf a tuple, different levels will be plotted with different linewidths in the order specified', 'values': "[['number', 'tuple of numbers']]", 'optional': True}),
              ("colors", "basic:Color",
                {'entry_types': "['enum']", 'docstring': "If None, the colormap specified by cmap will be used.\n\nIf a string, like 'r' or 'red', all levels will be plotted in this color.\n\nIf a tuple of matplotlib color args (string, float, rgb, etc), different levels will be plotted in different colors in the order specified.", 'values': "[['(mpl_colors)']]", 'optional': True}),
              ("cmap", "basic:String",
                {'entry_types': "['enum']", 'docstring': 'A cm :class:`~matplotlib.cm.Colormap` instance or None. If cmap is None and colors is None, a default Colormap is used.', 'values': "[['Colormap']]", 'optional': True}),
              ("nchunk", "basic:Integer",
                {'entry_types': "['enum']", 'docstring': 'If 0, no subdivision of the domain. Specify a positive integer to divide the domain into subdomains of roughly nchunk by nchunk points. This may never actually be advantageous, so this option may be removed. Chunking introduces artifacts at the chunk boundaries unless antialiased is False.', 'values': '[[0]]', 'optional': True}),
              ("alpha", "basic:Float",
                {'optional': True, 'docstring': 'The alpha blending value'}),
              ("norm", "basic:String",
                {'entry_types': "['enum']", 'docstring': 'A :class:`matplotlib.colors.Normalize` instance for scaling data values to colors. If norm is None and colors is None, the default linear scaling is used.', 'values': "[['Normalize']]", 'optional': True}),
        ]

    _output_ports = [
        ("self", "(MplContourf)"),
        ]
    

    def compute(self):
        # get args into args, kwargs
        # write out translations
        kwargs = {}            
        if self.hasInputFromPort('origin'):
            kwargs['origin'] = self.getInputFromPort('origin')
        if self.hasInputFromPort('linestyles'):
            kwargs['linestyles'] = self.getInputFromPort('linestyles')
        if self.hasInputFromPort('levelsSequence'):
            kwargs['levels'] = self.getInputFromPort('levelsSequence')
        elif self.hasInputFromPort('levelsScalar'):
            kwargs['levels'] = self.getInputFromPort('levelsScalar')
        if self.hasInputFromPort('linewidths'):
            kwargs['linewidths'] = self.getInputFromPort('linewidths')
        if self.hasInputFromPort('colors'):
            kwargs['colors'] = self.getInputFromPort('colors')
            kwargs['colors'] = translate_color(kwargs['colors'])
        if self.hasInputFromPort('cmap'):
            kwargs['cmap'] = self.getInputFromPort('cmap')
        if self.hasInputFromPort('nchunk'):
            kwargs['nchunk'] = self.getInputFromPort('nchunk')
        if self.hasInputFromPort('alpha'):
            kwargs['alpha'] = self.getInputFromPort('alpha')
        if self.hasInputFromPort('norm'):
            kwargs['norm'] = self.getInputFromPort('norm')
        # self.get_fig()
        matplotlib.pyplot.contourf(**kwargs)        

class MplCsd(MplPlot):
    """call signature:

csd(x, y, NFFT=256, Fs=2, Fc=0, detrend=mlab.detrend_none,     window=mlab.window_hanning, noverlap=0, pad_to=None,     sides='default', scale_by_freq=None, **kwargs)

The cross spectral density :math:`P_{xy}` by Welch's average periodogram method.  The vectors x and y are divided into NFFT length segments.  Each segment is detrended by function detrend and windowed by function window.  The product of the direct FFTs of x and y are averaged over each segment to compute :math:`P_{xy}`, with a scaling to correct for power loss due to windowing.

Returns the tuple (Pxy, freqs).  P is the cross spectrum (complex valued), and :math:`10\log_{10}|P_{xy}|` is plotted.

%(PSD)s



kwargs control the Line2D properties:

%(Line2D)s

Example:

seealso:  :meth:`psd`     For a description of the optional parameters.

Additional kwargs: hold = [True|False] overrides default hold state
    """
    _input_ports = [
              ("Fs", "basic:Integer",
                {'optional': True, 'defaults': "['2']"}),
              ("pad_to", "basic:String",
                {'optional': True}),
              ("scale_by_freq", "basic:String",
                {'optional': True}),
              ("detrend", "basic:String",
                {'optional': True, 'defaults': "['<function detrend_none at 0x101f3b0c8>']"}),
              ("window", "basic:String",
                {'optional': True, 'defaults': "['<function window_hanning at 0x101f367d0>']"}),
              ("Fc", "basic:Integer",
                {'optional': True, 'defaults': "['0']"}),
              ("NFFT", "basic:Integer",
                {'optional': True, 'defaults': "['256']"}),
              ("y", "basic:String",
                {}),
              ("x", "basic:String",
                {}),
              ("hold", "basic:String",
                {'optional': True}),
              ("sides", "basic:String",
                {'optional': True, 'defaults': "['default']"}),
              ("noverlap", "basic:Integer",
                {'optional': True, 'defaults': "['0']"}),
        ]

    _output_ports = [
        ("self", "(MplCsd)"),
        ]
    

    def compute(self):
        # get args into args, kwargs
        # write out translations
        kwargs = {}            
        if self.hasInputFromPort('Fs'):
            kwargs['Fs'] = self.getInputFromPort('Fs')
        if self.hasInputFromPort('pad_to'):
            kwargs['pad_to'] = self.getInputFromPort('pad_to')
        if self.hasInputFromPort('scale_by_freq'):
            kwargs['scale_by_freq'] = self.getInputFromPort('scale_by_freq')
        if self.hasInputFromPort('detrend'):
            kwargs['detrend'] = self.getInputFromPort('detrend')
        if self.hasInputFromPort('window'):
            kwargs['window'] = self.getInputFromPort('window')
        if self.hasInputFromPort('Fc'):
            kwargs['Fc'] = self.getInputFromPort('Fc')
        if self.hasInputFromPort('NFFT'):
            kwargs['NFFT'] = self.getInputFromPort('NFFT')
        kwargs['y'] = self.getInputFromPort('y')
        kwargs['x'] = self.getInputFromPort('x')
        if self.hasInputFromPort('hold'):
            kwargs['hold'] = self.getInputFromPort('hold')
        if self.hasInputFromPort('sides'):
            kwargs['sides'] = self.getInputFromPort('sides')
        if self.hasInputFromPort('noverlap'):
            kwargs['noverlap'] = self.getInputFromPort('noverlap')
        # self.get_fig()
        matplotlib.pyplot.csd(**kwargs)        

class MplErrorbar(MplPlot):
    """call signature:

errorbar(x, y, yerr=None, xerr=None,          fmt='-', ecolor=None, elinewidth=None, capsize=3,          barsabove=False, lolims=False, uplims=False,          xlolims=False, xuplims=False)

Plot x versus y with error deltas in yerr and xerr. Vertical errorbars are plotted if yerr is not None. Horizontal errorbars are plotted if xerr is not None.

x, y, xerr, and yerr can all be scalars, which plots a single error bar at x, y.

Optional keyword arguments:



All other keyword arguments are passed on to the plot command for the markers. For example, this code makes big red squares with thick green edges:

x,y,yerr = rand(3,10) errorbar(x, y, yerr, marker='s',          mfc='red', mec='green', ms=20, mew=4)

where mfc, mec, ms and mew are aliases for the longer property names, markerfacecolor, markeredgecolor, markersize and markeredgewith.

valid kwargs for the marker properties are

%(Line2D)s

Returns (plotline, caplines, barlinecols):



Example:

Additional kwargs: hold = [True|False] overrides default hold state
    """
    _input_ports = [
              ("lolims", "basic:Boolean",
                {'optional': True, 'docstring': 'These arguments can be used to indicate that a value gives only upper/lower limits. In that case a caret symbol is used to indicate this. lims-arguments may be of the same type as xerr and yerr.', 'defaults': "['False']"}),
              ("capsize", "basic:Float",
                {'optional': True, 'docstring': 'the size of the error bar caps in points', 'defaults': "['3']"}),
              ("uplims", "basic:Boolean",
                {'optional': True, 'docstring': 'These arguments can be used to indicate that a value gives only upper/lower limits. In that case a caret symbol is used to indicate this. lims-arguments may be of the same type as xerr and yerr.', 'defaults': "['False']"}),
              ("xlolims", "basic:Boolean",
                {'optional': True, 'docstring': 'These arguments can be used to indicate that a value gives only upper/lower limits. In that case a caret symbol is used to indicate this. lims-arguments may be of the same type as xerr and yerr.', 'defaults': "['False']"}),
              ("barsabove", "basic:String",
                {'optional': True, 'docstring': 'if True, will plot the errorbars above the plot symbols. Default is below.', 'defaults': "['below']"}),
              ("xerr", "basic:List",
                {'optional': True, 'docstring': 'If a scalar number, len(N) array-like object, or an Nx1 array-like object, errorbars are drawn +/- value.\n\nIf a sequence of shape 2xN, errorbars are drawn at -row1 and +row2'}),
              ("xerrScalar", "basic:Float",
               {'docstring': 'If a scalar number, len(N) array-like object, or an Nx1 array-like object, errorbars are drawn +/- value.\n\nIf a sequence of shape 2xN, errorbars are drawn at -row1 and +row2', 'optional': True}),
              ("fmt", "basic:String",
                {'optional': True, 'docstring': 'The plot format symbol. If fmt is None, only the errorbars are plotted.  This is used for adding errorbars to a bar plot, for example.', 'defaults': "['-']"}),
              ("ecolor", "basic:String",
                {'entry_types': "['enum']", 'docstring': 'a matplotlib color arg which gives the color the errorbar lines; if None, use the marker color.', 'values': "[['mpl color']]", 'optional': True}),
              ("xuplims", "basic:Boolean",
                {'optional': True, 'docstring': 'These arguments can be used to indicate that a value gives only upper/lower limits. In that case a caret symbol is used to indicate this. lims-arguments may be of the same type as xerr and yerr.', 'defaults': "['False']"}),
              ("elinewidth", "basic:Float",
                {'optional': True, 'docstring': 'the linewidth of the errorbar lines. If None, use the linewidth.'}),
              ("y", "basic:List",
                {}),
              ("x", "basic:List",
                {}),
              ("hold", "basic:String",
                {'optional': True}),
              ("yerr", "basic:List",
                {'optional': True, 'docstring': 'If a scalar number, len(N) array-like object, or an Nx1 array-like object, errorbars are drawn +/- value.\n\nIf a sequence of shape 2xN, errorbars are drawn at -row1 and +row2'}),
              ("yerrScalar", "basic:Float",
               {'docstring': 'If a scalar number, len(N) array-like object, or an Nx1 array-like object, errorbars are drawn +/- value.\n\nIf a sequence of shape 2xN, errorbars are drawn at -row1 and +row2', 'optional': True}),
              ("caplineProperties", "MplLine2DProperties",
                {}),
              ("barlineProperties", "MplLineCollectionProperties",
                {}),
              ("plotlineProperties", "MplLine2DProperties",
                {}),
        ]

    _output_ports = [
        ("self", "(MplErrorbar)"),
        ]
    

    def compute(self):
        # get args into args, kwargs
        # write out translations
        kwargs = {}            
        if self.hasInputFromPort('lolims'):
            kwargs['lolims'] = self.getInputFromPort('lolims')
        if self.hasInputFromPort('capsize'):
            kwargs['capsize'] = self.getInputFromPort('capsize')
        if self.hasInputFromPort('uplims'):
            kwargs['uplims'] = self.getInputFromPort('uplims')
        if self.hasInputFromPort('xlolims'):
            kwargs['xlolims'] = self.getInputFromPort('xlolims')
        if self.hasInputFromPort('barsabove'):
            kwargs['barsabove'] = self.getInputFromPort('barsabove')
        if self.hasInputFromPort('xerr'):
            kwargs['xerr'] = self.getInputFromPort('xerr')
        elif self.hasInputFromPort('xerrScalar'):
            kwargs['xerr'] = self.getInputFromPort('xerrScalar')
        if self.hasInputFromPort('fmt'):
            kwargs['fmt'] = self.getInputFromPort('fmt')
        if self.hasInputFromPort('ecolor'):
            kwargs['ecolor'] = self.getInputFromPort('ecolor')
        if self.hasInputFromPort('xuplims'):
            kwargs['xuplims'] = self.getInputFromPort('xuplims')
        if self.hasInputFromPort('elinewidth'):
            kwargs['elinewidth'] = self.getInputFromPort('elinewidth')
        kwargs['y'] = self.getInputFromPort('y')
        kwargs['x'] = self.getInputFromPort('x')
        if self.hasInputFromPort('hold'):
            kwargs['hold'] = self.getInputFromPort('hold')
        if self.hasInputFromPort('yerr'):
            kwargs['yerr'] = self.getInputFromPort('yerr')
        elif self.hasInputFromPort('yerrScalar'):
            kwargs['yerr'] = self.getInputFromPort('yerrScalar')
        # self.get_fig()
        output = matplotlib.pyplot.errorbar(**kwargs)        
        plotline = output[0]
        caplines = output[1]
        barlines = output[2]
        if self.hasInputFromPort('caplineProperties'):
            properties = self.getInputFromPort('caplineProperties')
            properties.update_props(caplines)
        if self.hasInputFromPort('barlineProperties'):
            properties = self.getInputFromPort('barlineProperties')
            properties.update_props(barlines)
        if self.hasInputFromPort('plotlineProperties'):
            properties = self.getInputFromPort('plotlineProperties')
            properties.update_props(plotline)

class MplFill(MplPlot):
    """call signature:

fill(*args, **kwargs)

Plot filled polygons.  args is a variable length argument, allowing for multiple x, y pairs with an optional color format string; see :func:`~matplotlib.pyplot.plot` for details on the argument parsing.  For example, to plot a polygon with vertices at x, y in blue.:

ax.fill(x,y, 'b' )

An arbitrary number of x, y, color groups can be specified:

ax.fill(x1, y1, 'g', x2, y2, 'r')

Return value is a list of :class:`~matplotlib.patches.Patch` instances that were added.

The same color strings that :func:`~matplotlib.pyplot.plot` supports are supported by the fill format string.

If you would like to fill below a curve, eg. shade a region between 0 and y along x, use :meth:`fill_between`

The closed kwarg will close the polygon when True (default).

kwargs control the Polygon properties:

%(Polygon)s

Example:

Additional kwargs: hold = [True|False] overrides default hold state
    """
    _input_ports = [
        ]

    _output_ports = [
        ("self", "(MplFill)"),
        ]
    

    def compute(self):
        # get args into args, kwargs
        # write out translations
        kwargs = {}            
        # self.get_fig()
        matplotlib.pyplot.fill(**kwargs)        

class MplFill_between(MplPlot):
    """call signature:

fill_between(x, y1, y2=0, where=None, **kwargs)

Create a :class:`~matplotlib.collections.PolyCollection` filling the regions between y1 and y2 where where==True

kwargs control the Polygon properties:

%(PolyCollection)s

Additional kwargs: hold = [True|False] overrides default hold state
    """
    _input_ports = [
              ("y2", "basic:Integer",
                {'optional': True, 'defaults': "['0']"}),
              ("interpolate", "basic:Boolean",
                {'optional': True, 'defaults': "['False']"}),
              ("y1", "basic:String",
                {}),
              ("x", "basic:String",
                {}),
              ("hold", "basic:String",
                {'optional': True}),
              ("where", "basic:String",
                {'optional': True}),
        ]

    _output_ports = [
        ("self", "(MplFill_between)"),
        ]
    

    def compute(self):
        # get args into args, kwargs
        # write out translations
        kwargs = {}            
        if self.hasInputFromPort('y2'):
            kwargs['y2'] = self.getInputFromPort('y2')
        if self.hasInputFromPort('interpolate'):
            kwargs['interpolate'] = self.getInputFromPort('interpolate')
        kwargs['y1'] = self.getInputFromPort('y1')
        kwargs['x'] = self.getInputFromPort('x')
        if self.hasInputFromPort('hold'):
            kwargs['hold'] = self.getInputFromPort('hold')
        if self.hasInputFromPort('where'):
            kwargs['where'] = self.getInputFromPort('where')
        # self.get_fig()
        matplotlib.pyplot.fill_between(**kwargs)        

class MplFill_betweenx(MplPlot):
    """call signature:

fill_between(y, x1, x2=0, where=None, **kwargs)

Create a :class:`~matplotlib.collections.PolyCollection` filling the regions between x1 and x2 where where==True

kwargs control the Polygon properties:

%(PolyCollection)s

Additional kwargs: hold = [True|False] overrides default hold state
    """
    _input_ports = [
              ("y", "basic:String",
                {}),
              ("x2", "basic:Integer",
                {'optional': True, 'defaults': "['0']"}),
              ("hold", "basic:String",
                {'optional': True}),
              ("x1", "basic:String",
                {}),
              ("where", "basic:String",
                {'optional': True}),
        ]

    _output_ports = [
        ("self", "(MplFill_betweenx)"),
        ]
    

    def compute(self):
        # get args into args, kwargs
        # write out translations
        kwargs = {}            
        kwargs['y'] = self.getInputFromPort('y')
        if self.hasInputFromPort('x2'):
            kwargs['x2'] = self.getInputFromPort('x2')
        if self.hasInputFromPort('hold'):
            kwargs['hold'] = self.getInputFromPort('hold')
        kwargs['x1'] = self.getInputFromPort('x1')
        if self.hasInputFromPort('where'):
            kwargs['where'] = self.getInputFromPort('where')
        # self.get_fig()
        matplotlib.pyplot.fill_betweenx(**kwargs)        

class MplHexbin(MplPlot):
    """call signature:

hexbin(x, y, C = None, gridsize = 100, bins = None,        xscale = 'linear', yscale = 'linear',        cmap=None, norm=None, vmin=None, vmax=None,        alpha=None, linewidths=None, edgecolors='none'        reduce_C_function = np.mean, mincnt=None, marginals=True        **kwargs)

Make a hexagonal binning plot of x versus y, where x, y are 1-D sequences of the same length, N. If C is None (the default), this is a histogram of the number of occurences of the observations at (x[i],y[i]).

If C is specified, it specifies values at the coordinate (x[i],y[i]). These values are accumulated for each hexagonal bin and then reduced according to reduce_C_function, which defaults to numpy's mean function (np.mean). (If C is specified, it must also be a 1-D sequence of the same length as x and y.)

x, y and/or C may be masked arrays, in which case only unmasked points will be plotted.

Optional keyword arguments:

Other keyword arguments controlling color mapping and normalization arguments:

Other keyword arguments controlling the Collection properties:

Here are the standard descriptions of all the :class:`~matplotlib.collections.Collection` kwargs:

%(Collection)s

The return value is a :class:`~matplotlib.collections.PolyCollection` instance; use :meth:`~matplotlib.collection.PolyCollection.get_array` on this :class:`~matplotlib.collections.PolyCollection` to get the counts in each hexagon. If marginals is True, horizontal bar and vertical bar (both PolyCollections) will be attached to the return collection as attributes hbar and vbar

Example:

Additional kwargs: hold = [True|False] overrides default hold state
    """
    _input_ports = [
              ("vmax", "basic:Float",
                {'optional': True, 'docstring': 'vmin and vmax are used in conjunction with norm to normalize luminance data.  If either are None, the min and max of the color array C is used.  Note if you pass a norm instance, your settings for vmin and vmax will be ignored.'}),
              ("edgecolorsSequence", "basic:List",
                {'entry_types': "['enum']", 'docstring': "If 'none', draws the edges in the same color as the fill color. This is the default, as it avoids unsightly unpainted pixels between the hexagons.\n\nIf None, draws the outlines in the default color.\n\nIf a matplotlib color arg or sequence of rgba tuples, draws the outlines in the specified color.", 'values': "[['mpl color']]", 'optional': True, 'defaults': "['none']"}),
              ("edgecolorsScalar", "basic:String",
               {'values': "[['mpl color']]", 'entry_types': "['enum']", 'docstring': "If 'none', draws the edges in the same color as the fill color. This is the default, as it avoids unsightly unpainted pixels between the hexagons.\n\nIf None, draws the outlines in the default color.\n\nIf a matplotlib color arg or sequence of rgba tuples, draws the outlines in the specified color.", 'optional': True, 'defaults': "['none']"}),
              ("C", "basic:String",
                {'optional': True}),
              ("gridsize", "basic:Integer",
                {'entry_types': "['enum']", 'docstring': 'The number of hexagons in the x-direction, default is 100. The corresponding number of hexagons in the y-direction is chosen such that the hexagons are approximately regular. Alternatively, gridsize can be a tuple with two elements specifying the number of hexagons in the x-direction and the y-direction.', 'values': '[[100]]', 'optional': True, 'defaults': "['100']"}),
              ("vmin", "basic:Float",
                {'optional': True, 'docstring': 'vmin and vmax are used in conjunction with norm to normalize luminance data.  If either are None, the min and max of the color array C is used.  Note if you pass a norm instance, your settings for vmin and vmax will be ignored.'}),
              ("yscale", "basic:String",
                {'optional': True, 'defaults': "['linear']"}),
              ("reduce_C_function", "basic:String",
                {'optional': True, 'defaults': "['<function mean at 0x10166f2a8>']"}),
              ("linewidthsSequence", "basic:List",
                {'optional': True, 'docstring': 'If None, defaults to rc lines.linewidth. Note that this is a tuple, and if you set the linewidths argument you must set it as a sequence of floats, as required by :class:`~matplotlib.collections.RegularPolyCollection`.'}),
              ("linewidthsScalar", "basic:Float",
               {'docstring': 'If None, defaults to rc lines.linewidth. Note that this is a tuple, and if you set the linewidths argument you must set it as a sequence of floats, as required by :class:`~matplotlib.collections.RegularPolyCollection`.', 'optional': True}),
              ("xscale", "basic:String",
                {'entry_types': "['enum']", 'docstring': 'Use a linear or log10 scale on the horizontal axis.', 'values': "[['linear', 'log']]", 'optional': True, 'defaults': "['linear']"}),
              ("cmap", "basic:String",
                {'entry_types': "['enum']", 'docstring': 'a :class:`matplotlib.cm.Colormap` instance. If None, defaults to rc image.cmap.', 'values': "[['Colormap']]", 'optional': True}),
              ("norm", "basic:String",
                {'entry_types': "['enum']", 'docstring': ':class:`matplotlib.colors.Normalize` instance is used to scale luminance data to 0,1.', 'values': "[['Normalize']]", 'optional': True}),
              ("extent", "basic:Float",
                {'optional': True, 'docstring': 'The limits of the bins. The default assigns the limits based on gridsize, x, y, xscale and yscale.'}),
              ("alpha", "basic:Float",
                {'optional': True, 'docstring': 'the alpha value for the patches'}),
              ("y", "basic:String",
                {}),
              ("x", "basic:String",
                {}),
              ("hold", "basic:String",
                {'optional': True}),
              ("mincnt", "basic:Integer",
                {'optional': True, 'docstring': 'If not None, only display cells with more than mincnt number of points in the cell'}),
              ("marginals", "basic:Boolean",
                {'optional': True, 'docstring': 'if marginals is True, plot the marginal density as colormapped rectagles along the bottom of the x-axis and left of the y-axis', 'defaults': "['False']"}),
              ("bins", "basic:String",
                {'entry_types': "['enum']", 'docstring': "If None, no binning is applied; the color of each hexagon directly corresponds to its count value.\n\nIf 'log', use a logarithmic scale for the color map. Internally, :math:`log_{10}(i+1)` is used to determine the hexagon color.\n\nIf an integer, divide the counts in the specified number of bins, and color the hexagons accordingly.\n\nIf a sequence of values, the values of the lower bound of the bins to be used.", 'values': "[['log']]", 'optional': True}),
              ("scale", "basic:String",
                {'entry_types': "['enum']", 'docstring': 'Use a linear or log10 scale on the vertical axis.', 'values': "[['linear', 'log']]", 'optional': True}),
        ]

    _output_ports = [
        ("self", "(MplHexbin)"),
        ]
    

    def compute(self):
        # get args into args, kwargs
        # write out translations
        kwargs = {}            
        if self.hasInputFromPort('vmax'):
            kwargs['vmax'] = self.getInputFromPort('vmax')
        if self.hasInputFromPort('edgecolorsSequence'):
            kwargs['edgecolors'] = self.getInputFromPort('edgecolorsSequence')
        elif self.hasInputFromPort('edgecolorsScalar'):
            kwargs['edgecolors'] = self.getInputFromPort('edgecolorsScalar')
        if self.hasInputFromPort('C'):
            kwargs['C'] = self.getInputFromPort('C')
        if self.hasInputFromPort('gridsize'):
            kwargs['gridsize'] = self.getInputFromPort('gridsize')
        if self.hasInputFromPort('vmin'):
            kwargs['vmin'] = self.getInputFromPort('vmin')
        if self.hasInputFromPort('yscale'):
            kwargs['yscale'] = self.getInputFromPort('yscale')
        if self.hasInputFromPort('reduce_C_function'):
            kwargs['reduce_C_function'] = self.getInputFromPort('reduce_C_function')
        if self.hasInputFromPort('linewidthsSequence'):
            kwargs['linewidths'] = self.getInputFromPort('linewidthsSequence')
        elif self.hasInputFromPort('linewidthsScalar'):
            kwargs['linewidths'] = self.getInputFromPort('linewidthsScalar')
        if self.hasInputFromPort('xscale'):
            kwargs['xscale'] = self.getInputFromPort('xscale')
        if self.hasInputFromPort('cmap'):
            kwargs['cmap'] = self.getInputFromPort('cmap')
        if self.hasInputFromPort('norm'):
            kwargs['norm'] = self.getInputFromPort('norm')
        if self.hasInputFromPort('extent'):
            kwargs['extent'] = self.getInputFromPort('extent')
        if self.hasInputFromPort('alpha'):
            kwargs['alpha'] = self.getInputFromPort('alpha')
        kwargs['y'] = self.getInputFromPort('y')
        kwargs['x'] = self.getInputFromPort('x')
        if self.hasInputFromPort('hold'):
            kwargs['hold'] = self.getInputFromPort('hold')
        if self.hasInputFromPort('mincnt'):
            kwargs['mincnt'] = self.getInputFromPort('mincnt')
        if self.hasInputFromPort('marginals'):
            kwargs['marginals'] = self.getInputFromPort('marginals')
        if self.hasInputFromPort('bins'):
            kwargs['bins'] = self.getInputFromPort('bins')
        if self.hasInputFromPort('scale'):
            kwargs['scale'] = self.getInputFromPort('scale')
        # self.get_fig()
        matplotlib.pyplot.hexbin(**kwargs)        

class MplHist(MplPlot):
    """call signature:

def hist(x, bins=10, range=None, normed=False, weights=None,        cumulative=False, bottom=None, histtype='bar', align='mid',        orientation='vertical', rwidth=None, log=False,        color=None, label=None,        **kwargs):

Compute and draw the histogram of x. The return value is a tuple (n, bins, patches) or ([n0, n1, ...], bins, [patches0, patches1,...]) if the input contains multiple data.

Multiple data can be provided via x as a list of datasets of potentially different length ([x0, x1, ...]), or as a 2-D ndarray in which each column is a dataset.  Note that the ndarray form is transposed relative to the list form.

Masked arrays are not supported at present.

Keyword arguments:



kwargs are used to update the properties of the :class:`~matplotlib.patches.Patch` instances returned by hist:

%(Patch)s

Example:

Additional kwargs: hold = [True|False] overrides default hold state
    """
    _input_ports = [
              ("rwidth", "basic:String",
                {'optional': True, 'docstring': "The relative width of the bars as a fraction of the bin width.  If None, automatically compute the width. Ignored if histtype = 'step' or 'stepfilled'."}),
              ("normed", "basic:Boolean",
                {'optional': True, 'docstring': 'If True, the first element of the return tuple will be the counts normalized to form a probability density, i.e., n/(len(x)*dbin).  In a probability density, the integral of the histogram should be 1; you can verify that with a trapezoidal integration of the probability density function:\n\npdf, bins, patches = ax.hist(...) print np.sum(pdf * np.diff(bins))\n\nUntil numpy release 1.5, the underlying numpy histogram function was incorrect with normed*=*True if bin sizes were unequal.  MPL inherited that error.  It is now corrected within MPL when using earlier numpy versions', 'defaults': "['False']"}),
              ("orientation", "basic:String",
                {'entry_types': "['enum']", 'docstring': "If 'horizontal', :func:`~matplotlib.pyplot.barh` will be used for bar-type histograms and the bottom kwarg will be the left edges.", 'values': "[['horizontal', 'vertical']]", 'optional': True, 'defaults': "['vertical']"}),
              ("bottom", "basic:String",
                {'optional': True}),
              ("color", "basic:List",
                {'optional': True, 'docstring': 'Color spec or sequence of color specs, one per dataset.  Default (None) uses the standard line color sequence.'}),
              ("colorScalar", "basic:Color",
               {'docstring': 'Color spec or sequence of color specs, one per dataset.  Default (None) uses the standard line color sequence.', 'optional': True}),
              ("histtype", "basic:String",
                {'entry_types': "['enum']", 'docstring': "The type of histogram to draw.\n\n'bar' is a traditional bar-type histogram.  If multiple data are given the bars are aranged side by side.\n\n'barstacked' is a bar-type histogram where multiple data are stacked on top of each other.\n\n'step' generates a lineplot that is by default unfilled.\n\n'stepfilled' generates a lineplot that is by default filled.", 'values': "[['bar', 'barstacked', 'step', 'stepfilled']]", 'optional': True, 'defaults': "['bar']"}),
              ("align", "basic:String",
                {'entry_types': "['enum']", 'docstring': "Controls how the histogram is plotted.\n\n'left': bars are centered on the left bin edges.\n\n'mid': bars are centered between the bin edges.\n\n'right': bars are centered on the right bin edges.", 'values': "[['left', 'mid', 'right']]", 'optional': True, 'defaults': "['mid']"}),
              ("cumulative", "basic:Boolean",
                {'optional': True, 'docstring': 'If True, then a histogram is computed where each bin gives the counts in that bin plus all bins for smaller values. The last bin gives the total number of datapoints.  If normed is also True then the histogram is normalized such that the last bin equals 1. If cumulative evaluates to less than 0 (e.g. -1), the direction of accumulation is reversed.  In this case, if normed is also True, then the histogram is normalized such that the first bin equals 1.', 'defaults': "['False']"}),
              ("labelSequence", "basic:List",
                {'optional': True, 'docstring': "String, or sequence of strings to match multiple datasets.  Bar charts yield multiple patches per dataset, but only the first gets the label, so that the legend command will work as expected:\n\nax.hist(10+2*np.random.randn(1000), label='men') ax.hist(12+3*np.random.randn(1000), label='women', alpha=0.5) ax.legend()"}),
              ("labelScalar", "basic:String",
               {'docstring': "String, or sequence of strings to match multiple datasets.  Bar charts yield multiple patches per dataset, but only the first gets the label, so that the legend command will work as expected:\n\nax.hist(10+2*np.random.randn(1000), label='men') ax.hist(12+3*np.random.randn(1000), label='women', alpha=0.5) ax.legend()", 'optional': True}),
              ("range", "basic:List",
                {'optional': True, 'docstring': 'The lower and upper range of the bins. Lower and upper outliers are ignored. If not provided, range is (x.min(), x.max()). Range has no effect if bins is a sequence.\n\nIf bins is a sequence or range is specified, autoscaling is based on the specified bin range instead of the range of x.'}),
              ("weights", "basic:String",
                {'optional': True, 'docstring': 'An array of weights, of the same shape as x.  Each value in x only contributes its associated weight towards the bin count (instead of 1).  If normed is True, the weights are normalized, so that the integral of the density over the range remains 1.'}),
              ("x", "basic:List",
                {}),
              ("hold", "basic:String",
                {'optional': True}),
              ("binsSequence", "basic:List",
                {'optional': True, 'docstring': 'Either an integer number of bins or a sequence giving the bins.  If bins is an integer, bins + 1 bin edges will be returned, consistent with :func:`numpy.histogram` for numpy version >= 1.3, and with the new = True argument in earlier versions. Unequally spaced bins are supported if bins is a sequence.', 'defaults': "['10']"}),
              ("binsScalar", "basic:Integer",
               {'docstring': 'Either an integer number of bins or a sequence giving the bins.  If bins is an integer, bins + 1 bin edges will be returned, consistent with :func:`numpy.histogram` for numpy version >= 1.3, and with the new = True argument in earlier versions. Unequally spaced bins are supported if bins is a sequence.', 'optional': True, 'defaults': "['10']"}),
              ("log", "basic:Boolean",
                {'optional': True, 'docstring': 'If True, the histogram axis will be set to a log scale. If log is True and x is a 1D array, empty bins will be filtered out and only the non-empty (n, bins, patches) will be returned.', 'defaults': "['False']"}),
              ("rectangleProperties", "MplRectangleProperties",
                {}),
        ]

    _output_ports = [
        ("self", "(MplHist)"),
        ]
    

    def compute(self):
        # get args into args, kwargs
        # write out translations
        kwargs = {}            
        if self.hasInputFromPort('rwidth'):
            kwargs['rwidth'] = self.getInputFromPort('rwidth')
        if self.hasInputFromPort('normed'):
            kwargs['normed'] = self.getInputFromPort('normed')
        if self.hasInputFromPort('orientation'):
            kwargs['orientation'] = self.getInputFromPort('orientation')
        if self.hasInputFromPort('bottom'):
            kwargs['bottom'] = self.getInputFromPort('bottom')
        if self.hasInputFromPort('color'):
            kwargs['color'] = self.getInputFromPort('color')
        elif self.hasInputFromPort('colorScalar'):
            kwargs['color'] = self.getInputFromPort('colorScalar')
            kwargs['color'] = translate_color(kwargs['color'])
        if self.hasInputFromPort('histtype'):
            kwargs['histtype'] = self.getInputFromPort('histtype')
        if self.hasInputFromPort('align'):
            kwargs['align'] = self.getInputFromPort('align')
        if self.hasInputFromPort('cumulative'):
            kwargs['cumulative'] = self.getInputFromPort('cumulative')
        if self.hasInputFromPort('labelSequence'):
            kwargs['label'] = self.getInputFromPort('labelSequence')
        elif self.hasInputFromPort('labelScalar'):
            kwargs['label'] = self.getInputFromPort('labelScalar')
        if self.hasInputFromPort('range'):
            kwargs['range'] = self.getInputFromPort('range')
        if self.hasInputFromPort('weights'):
            kwargs['weights'] = self.getInputFromPort('weights')
        kwargs['x'] = self.getInputFromPort('x')
        if self.hasInputFromPort('hold'):
            kwargs['hold'] = self.getInputFromPort('hold')
        if self.hasInputFromPort('binsSequence'):
            kwargs['bins'] = self.getInputFromPort('binsSequence')
        elif self.hasInputFromPort('binsScalar'):
            kwargs['bins'] = self.getInputFromPort('binsScalar')
        if self.hasInputFromPort('log'):
            kwargs['log'] = self.getInputFromPort('log')
        # self.get_fig()
        output = matplotlib.pyplot.hist(**kwargs)        
        rectangles = output[2]
        if self.hasInputFromPort('rectangleProperties'):
            properties = self.getInputFromPort('rectangleProperties')
            properties.update_props(rectangles)

class MplHist2d(MplPlot):
    """call signature:

def hist(x, bins=10, range=None, normed=False, weights=None,        cumulative=False, bottom=None, histtype='bar', align='mid',        orientation='vertical', rwidth=None, log=False,        color=None, label=None,        **kwargs):

Compute and draw the histogram of x. The return value is a tuple (n, bins, patches) or ([n0, n1, ...], bins, [patches0, patches1,...]) if the input contains multiple data.

Multiple data can be provided via x as a list of datasets of potentially different length ([x0, x1, ...]), or as a 2-D ndarray in which each column is a dataset.  Note that the ndarray form is transposed relative to the list form.

Masked arrays are not supported at present.

Keyword arguments:



kwargs are used to update the properties of the :class:`~matplotlib.patches.Patch` instances returned by hist:

%(Patch)s

Example:

Additional kwargs: hold = [True|False] overrides default hold state
    """
    _input_ports = [
              ("rwidth", "basic:String",
                {'optional': True, 'docstring': "The relative width of the bars as a fraction of the bin width.  If None, automatically compute the width. Ignored if histtype = 'step' or 'stepfilled'."}),
              ("normed", "basic:Boolean",
                {'optional': True, 'docstring': 'If True, the first element of the return tuple will be the counts normalized to form a probability density, i.e., n/(len(x)*dbin).  In a probability density, the integral of the histogram should be 1; you can verify that with a trapezoidal integration of the probability density function:\n\npdf, bins, patches = ax.hist(...) print np.sum(pdf * np.diff(bins))\n\nUntil numpy release 1.5, the underlying numpy histogram function was incorrect with normed*=*True if bin sizes were unequal.  MPL inherited that error.  It is now corrected within MPL when using earlier numpy versions', 'defaults': "['False']"}),
              ("orientation", "basic:String",
                {'entry_types': "['enum']", 'docstring': "If 'horizontal', :func:`~matplotlib.pyplot.barh` will be used for bar-type histograms and the bottom kwarg will be the left edges.", 'values': "[['horizontal', 'vertical']]", 'optional': True, 'defaults': "['vertical']"}),
              ("bottom", "basic:String",
                {'optional': True}),
              ("color", "basic:List",
                {'optional': True, 'docstring': 'Color spec or sequence of color specs, one per dataset.  Default (None) uses the standard line color sequence.'}),
              ("histtype", "basic:String",
                {'entry_types': "['enum']", 'docstring': "The type of histogram to draw.\n\n'bar' is a traditional bar-type histogram.  If multiple data are given the bars are aranged side by side.\n\n'barstacked' is a bar-type histogram where multiple data are stacked on top of each other.\n\n'step' generates a lineplot that is by default unfilled.\n\n'stepfilled' generates a lineplot that is by default filled.", 'values': "[['bar', 'barstacked', 'step', 'stepfilled']]", 'optional': True, 'defaults': "['bar']"}),
              ("align", "basic:String",
                {'entry_types': "['enum']", 'docstring': "Controls how the histogram is plotted.\n\n'left': bars are centered on the left bin edges.\n\n'mid': bars are centered between the bin edges.\n\n'right': bars are centered on the right bin edges.", 'values': "[['left', 'mid', 'right']]", 'optional': True, 'defaults': "['mid']"}),
              ("cumulative", "basic:Boolean",
                {'optional': True, 'docstring': 'If True, then a histogram is computed where each bin gives the counts in that bin plus all bins for smaller values. The last bin gives the total number of datapoints.  If normed is also True then the histogram is normalized such that the last bin equals 1. If cumulative evaluates to less than 0 (e.g. -1), the direction of accumulation is reversed.  In this case, if normed is also True, then the histogram is normalized such that the first bin equals 1.', 'defaults': "['False']"}),
              ("labelSequence", "basic:List",
                {'optional': True, 'docstring': "String, or sequence of strings to match multiple datasets.  Bar charts yield multiple patches per dataset, but only the first gets the label, so that the legend command will work as expected:\n\nax.hist(10+2*np.random.randn(1000), label='men') ax.hist(12+3*np.random.randn(1000), label='women', alpha=0.5) ax.legend()"}),
              ("labelScalar", "basic:String",
               {'docstring': "String, or sequence of strings to match multiple datasets.  Bar charts yield multiple patches per dataset, but only the first gets the label, so that the legend command will work as expected:\n\nax.hist(10+2*np.random.randn(1000), label='men') ax.hist(12+3*np.random.randn(1000), label='women', alpha=0.5) ax.legend()", 'optional': True}),
              ("range", "basic:List",
                {'optional': True, 'docstring': 'The lower and upper range of the bins. Lower and upper outliers are ignored. If not provided, range is (x.min(), x.max()). Range has no effect if bins is a sequence.\n\nIf bins is a sequence or range is specified, autoscaling is based on the specified bin range instead of the range of x.'}),
              ("weights", "basic:String",
                {'optional': True, 'docstring': 'An array of weights, of the same shape as x.  Each value in x only contributes its associated weight towards the bin count (instead of 1).  If normed is True, the weights are normalized, so that the integral of the density over the range remains 1.'}),
              ("x", "basic:String",
                {}),
              ("hold", "basic:String",
                {'optional': True}),
              ("binsSequence", "basic:List",
                {'optional': True, 'docstring': 'Either an integer number of bins or a sequence giving the bins.  If bins is an integer, bins + 1 bin edges will be returned, consistent with :func:`numpy.histogram` for numpy version >= 1.3, and with the new = True argument in earlier versions. Unequally spaced bins are supported if bins is a sequence.', 'defaults': "['10']"}),
              ("binsScalar", "basic:Integer",
               {'docstring': 'Either an integer number of bins or a sequence giving the bins.  If bins is an integer, bins + 1 bin edges will be returned, consistent with :func:`numpy.histogram` for numpy version >= 1.3, and with the new = True argument in earlier versions. Unequally spaced bins are supported if bins is a sequence.', 'optional': True, 'defaults': "['10']"}),
              ("log", "basic:Boolean",
                {'optional': True, 'docstring': 'If True, the histogram axis will be set to a log scale. If log is True and x is a 1D array, empty bins will be filtered out and only the non-empty (n, bins, patches) will be returned.', 'defaults': "['False']"}),
        ]

    _output_ports = [
        ("self", "(MplHist2d)"),
        ]
    

    def compute(self):
        # get args into args, kwargs
        # write out translations
        kwargs = {}            
        if self.hasInputFromPort('rwidth'):
            kwargs['rwidth'] = self.getInputFromPort('rwidth')
        if self.hasInputFromPort('normed'):
            kwargs['normed'] = self.getInputFromPort('normed')
        if self.hasInputFromPort('orientation'):
            kwargs['orientation'] = self.getInputFromPort('orientation')
        if self.hasInputFromPort('bottom'):
            kwargs['bottom'] = self.getInputFromPort('bottom')
        if self.hasInputFromPort('color'):
            kwargs['color'] = self.getInputFromPort('color')
        if self.hasInputFromPort('histtype'):
            kwargs['histtype'] = self.getInputFromPort('histtype')
        if self.hasInputFromPort('align'):
            kwargs['align'] = self.getInputFromPort('align')
        if self.hasInputFromPort('cumulative'):
            kwargs['cumulative'] = self.getInputFromPort('cumulative')
        if self.hasInputFromPort('labelSequence'):
            kwargs['label'] = self.getInputFromPort('labelSequence')
        elif self.hasInputFromPort('labelScalar'):
            kwargs['label'] = self.getInputFromPort('labelScalar')
        if self.hasInputFromPort('range'):
            kwargs['range'] = self.getInputFromPort('range')
        if self.hasInputFromPort('weights'):
            kwargs['weights'] = self.getInputFromPort('weights')
        kwargs['x'] = self.getInputFromPort('x')
        if self.hasInputFromPort('hold'):
            kwargs['hold'] = self.getInputFromPort('hold')
        if self.hasInputFromPort('binsSequence'):
            kwargs['bins'] = self.getInputFromPort('binsSequence')
        elif self.hasInputFromPort('binsScalar'):
            kwargs['bins'] = self.getInputFromPort('binsScalar')
        if self.hasInputFromPort('log'):
            kwargs['log'] = self.getInputFromPort('log')
        # self.get_fig()
        matplotlib.pyplot.hist2d(**kwargs)        

class MplHlines(MplPlot):
    """call signature:

hlines(y, xmin, xmax, colors='k', linestyles='solid', **kwargs)

Plot horizontal lines at each y from xmin to xmax.

Returns the :class:`~matplotlib.collections.LineCollection` that was added.

Required arguments:



Optional keyword arguments:



Example:

Additional kwargs: hold = [True|False] overrides default hold state
    """
    _input_ports = [
              ("linestyles", "basic:String",
                {'optional': True, 'docstring': "[ 'solid' | 'dashed' | 'dashdot' | 'dotted' ]", 'defaults': "['solid']"}),
              ("label", "basic:String",
                {'optional': True, 'defaults': "['']"}),
              ("xminScalar", "basic:Float",
                {'docstring': 'can be scalars or len(x) numpy arrays.  If they are scalars, then the respective values are constant, else the widths of the lines are determined by xmin and xmax.'}),
              ("xminSequence", "basic:List",
               {'docstring': 'can be scalars or len(x) numpy arrays.  If they are scalars, then the respective values are constant, else the widths of the lines are determined by xmin and xmax.', 'optional': True}),
              ("colorsSequence", "basic:List",
                {'optional': True, 'docstring': 'a line collections color argument, either a single color or a len(y) list of colors', 'defaults': "['k']"}),
              ("colorsScalar", "basic:String",
               {'docstring': 'a line collections color argument, either a single color or a len(y) list of colors', 'optional': True, 'defaults': "['k']"}),
              ("xmaxScalar", "basic:Float",
                {'docstring': 'can be scalars or len(x) numpy arrays.  If they are scalars, then the respective values are constant, else the widths of the lines are determined by xmin and xmax.'}),
              ("xmaxSequence", "basic:List",
               {'docstring': 'can be scalars or len(x) numpy arrays.  If they are scalars, then the respective values are constant, else the widths of the lines are determined by xmin and xmax.', 'optional': True}),
              ("y", "basic:List",
                {'docstring': 'a 1-D numpy array or iterable.'}),
              ("hold", "basic:String",
                {'optional': True}),
              ("lineProperties", "MplLineCollectionProperties",
                {}),
        ]

    _output_ports = [
        ("self", "(MplHlines)"),
        ]
    

    def compute(self):
        # get args into args, kwargs
        # write out translations
        kwargs = {}            
        if self.hasInputFromPort('linestyles'):
            kwargs['linestyles'] = self.getInputFromPort('linestyles')
        if self.hasInputFromPort('label'):
            kwargs['label'] = self.getInputFromPort('label')
        if self.hasInputFromPort('xminScalar'):
            kwargs['xmin'] = self.getInputFromPort('xminScalar')
        elif self.hasInputFromPort('xminSequence'):
            kwargs['xmin'] = self.getInputFromPort('xminSequence')
        else:
            raise ModuleError(self, 'Must set one of "xminScalar", '                                   '"xminSequence"')
        if self.hasInputFromPort('colorsSequence'):
            kwargs['colors'] = self.getInputFromPort('colorsSequence')
        elif self.hasInputFromPort('colorsScalar'):
            kwargs['colors'] = self.getInputFromPort('colorsScalar')
        if self.hasInputFromPort('xmaxScalar'):
            kwargs['xmax'] = self.getInputFromPort('xmaxScalar')
        elif self.hasInputFromPort('xmaxSequence'):
            kwargs['xmax'] = self.getInputFromPort('xmaxSequence')
        else:
            raise ModuleError(self, 'Must set one of "xmaxScalar", '                                   '"xmaxSequence"')
        kwargs['y'] = self.getInputFromPort('y')
        if self.hasInputFromPort('hold'):
            kwargs['hold'] = self.getInputFromPort('hold')
        # self.get_fig()
        lines = matplotlib.pyplot.hlines(**kwargs)
        if self.hasInputFromPort('lineProperties'):
            properties = self.getInputFromPort('lineProperties')
            properties.update_props(lines)

class MplImshow(MplPlot):
    """call signature:

imshow(X, cmap=None, norm=None, aspect=None, interpolation=None,        alpha=None, vmin=None, vmax=None, origin=None, extent=None,        **kwargs)

Display the image in X to current axes.  X may be a float array, a uint8 array or a PIL image. If X is an array, X can have the following shapes:

MxN -- luminance (grayscale, float array only)

MxNx3 -- RGB (float or uint8 array)

MxNx4 -- RGBA (float or uint8 array)

The value for each component of MxNx3 and MxNx4 float arrays should be in the range 0.0 to 1.0; MxN float arrays may be normalised.

An :class:`matplotlib.image.AxesImage` instance is returned.

Keyword arguments:

interpolation:

Acceptable values are None, 'none', 'nearest', 'bilinear', 'bicubic', 'spline16', 'spline36', 'hanning', 'hamming', 'hermite', 'kaiser', 'quadric', 'catrom', 'gaussian', 'bessel', 'mitchell', 'sinc', 'lanczos'

If interpolation is None, default to rc image.interpolation. See also the filternorm and filterrad parameters

If interpolation is 'none', then no interpolation is performed on the Agg, ps and pdf backends. Other backends will fall back to 'nearest'.

Additional kwargs are :class:`~matplotlib.artist.Artist` properties:

%(Artist)s

Example:

Additional kwargs: hold = [True|False] overrides default hold state
    """
    _input_ports = [
              ("origin", "basic:String",
                {'optional': True}),
              ("imlim", "basic:String",
                {'optional': True}),
              ("extent", "basic:String",
                {'optional': True}),
              ("vmin", "basic:String",
                {'optional': True}),
              ("url", "basic:String",
                {'optional': True}),
              ("resample", "basic:String",
                {'optional': True}),
              ("shape", "basic:String",
                {'optional': True}),
              ("cmap", "basic:String",
                {'entry_types': "['enum']", 'docstring': 'A :class:`matplotlib.cm.Colormap` instance, eg. cm.jet. If None, default to rc image.cmap value.\n\ncmap is ignored when X has RGB(A) information', 'values': "[['Colormap']]", 'optional': True}),
              ("filterrad", "basic:Float",
                {'optional': True, 'defaults': "['4.0']"}),
              ("filternorm", "basic:Integer",
                {'optional': True, 'defaults': "['1']"}),
              ("aspect", "basic:String",
                {'entry_types': "['enum']", 'docstring': "If 'auto', changes the image aspect ratio to match that of the axes\n\nIf 'equal', and extent is None, changes the axes aspect ratio to match that of the image. If extent is not None, the axes aspect ratio is changed to match that of the extent.\n\nIf None, default to rc image.aspect value.", 'values': "[['auto', 'equal']]", 'optional': True}),
              ("alpha", "basic:String",
                {'optional': True}),
              ("vmax", "basic:String",
                {'optional': True}),
              ("X", "basic:String",
                {}),
              ("hold", "basic:String",
                {'optional': True}),
              ("norm", "basic:String",
                {'optional': True}),
              ("interpolation", "basic:String",
                {'optional': True}),
        ]

    _output_ports = [
        ("self", "(MplImshow)"),
        ]
    

    def compute(self):
        # get args into args, kwargs
        # write out translations
        kwargs = {}            
        if self.hasInputFromPort('origin'):
            kwargs['origin'] = self.getInputFromPort('origin')
        if self.hasInputFromPort('imlim'):
            kwargs['imlim'] = self.getInputFromPort('imlim')
        if self.hasInputFromPort('extent'):
            kwargs['extent'] = self.getInputFromPort('extent')
        if self.hasInputFromPort('vmin'):
            kwargs['vmin'] = self.getInputFromPort('vmin')
        if self.hasInputFromPort('url'):
            kwargs['url'] = self.getInputFromPort('url')
        if self.hasInputFromPort('resample'):
            kwargs['resample'] = self.getInputFromPort('resample')
        if self.hasInputFromPort('shape'):
            kwargs['shape'] = self.getInputFromPort('shape')
        if self.hasInputFromPort('cmap'):
            kwargs['cmap'] = self.getInputFromPort('cmap')
        if self.hasInputFromPort('filterrad'):
            kwargs['filterrad'] = self.getInputFromPort('filterrad')
        if self.hasInputFromPort('filternorm'):
            kwargs['filternorm'] = self.getInputFromPort('filternorm')
        if self.hasInputFromPort('aspect'):
            kwargs['aspect'] = self.getInputFromPort('aspect')
        if self.hasInputFromPort('alpha'):
            kwargs['alpha'] = self.getInputFromPort('alpha')
        if self.hasInputFromPort('vmax'):
            kwargs['vmax'] = self.getInputFromPort('vmax')
        kwargs['X'] = self.getInputFromPort('X')
        if self.hasInputFromPort('hold'):
            kwargs['hold'] = self.getInputFromPort('hold')
        if self.hasInputFromPort('norm'):
            kwargs['norm'] = self.getInputFromPort('norm')
        if self.hasInputFromPort('interpolation'):
            kwargs['interpolation'] = self.getInputFromPort('interpolation')
        # self.get_fig()
        matplotlib.pyplot.imshow(**kwargs)        

class MplLoglog(MplPlot):
    """call signature:

loglog(*args, **kwargs)

Make a plot with log scaling on the x and y axis.

:func:`~matplotlib.pyplot.loglog` supports all the keyword arguments of :func:`~matplotlib.pyplot.plot` and :meth:`matplotlib.axes.Axes.set_xscale` / :meth:`matplotlib.axes.Axes.set_yscale`.

Notable keyword arguments:



The remaining valid kwargs are :class:`~matplotlib.lines.Line2D` properties:

%(Line2D)s

Example:

Additional kwargs: hold = [True|False] overrides default hold state
    """
    _input_ports = [
              ("nonposx", "basic:String",
                {'entry_types': "['enum']", 'docstring': 'non-positive values in x or y can be masked as invalid, or clipped to a very small positive number', 'values': "[['mask', 'clip']]", 'optional': True}),
              ("nonposy", "basic:String",
                {'entry_types': "['enum']", 'docstring': 'non-positive values in x or y can be masked as invalid, or clipped to a very small positive number', 'values': "[['mask', 'clip']]", 'optional': True}),
              ("basex", "basic:Float",
                {'optional': True, 'docstring': 'base of the x/y logarithm'}),
              ("basey", "basic:Float",
                {'optional': True, 'docstring': 'base of the x/y logarithm'}),
              ("subsx", "basic:List",
                {'optional': True, 'docstring': 'the location of the minor x/y ticks; None defaults to autosubs, which depend on the number of decades in the plot; see :meth:`matplotlib.axes.Axes.set_xscale` / :meth:`matplotlib.axes.Axes.set_yscale` for details'}),
              ("subsy", "basic:List",
                {'optional': True, 'docstring': 'the location of the minor x/y ticks; None defaults to autosubs, which depend on the number of decades in the plot; see :meth:`matplotlib.axes.Axes.set_xscale` / :meth:`matplotlib.axes.Axes.set_yscale` for details'}),
        ]

    _output_ports = [
        ("self", "(MplLoglog)"),
        ]
    

    def compute(self):
        # get args into args, kwargs
        # write out translations
        kwargs = {}            
        if self.hasInputFromPort('nonposx'):
            kwargs['nonposx'] = self.getInputFromPort('nonposx')
        if self.hasInputFromPort('nonposy'):
            kwargs['nonposy'] = self.getInputFromPort('nonposy')
        if self.hasInputFromPort('basex'):
            kwargs['basex'] = self.getInputFromPort('basex')
        if self.hasInputFromPort('basey'):
            kwargs['basey'] = self.getInputFromPort('basey')
        if self.hasInputFromPort('subsx'):
            kwargs['subsx'] = self.getInputFromPort('subsx')
        if self.hasInputFromPort('subsy'):
            kwargs['subsy'] = self.getInputFromPort('subsy')
        # self.get_fig()
        matplotlib.pyplot.loglog(**kwargs)        

class MplPcolor(MplPlot):
    """call signatures:

pcolor(C, **kwargs) pcolor(X, Y, C, **kwargs)

Create a pseudocolor plot of a 2-D array.

C is the array of color values.

X and Y, if given, specify the (x, y) coordinates of the colored quadrilaterals; the quadrilateral for C[i,j] has corners at:

(X[i,   j],   Y[i,   j]), (X[i,   j+1], Y[i,   j+1]), (X[i+1, j],   Y[i+1, j]), (X[i+1, j+1], Y[i+1, j+1]).

Ideally the dimensions of X and Y should be one greater than those of C; if the dimensions are the same, then the last row and column of C will be ignored.

Note that the the column index corresponds to the x-coordinate, and the row index corresponds to y; for details, see the :ref:`Grid Orientation <axes-pcolor-grid-orientation>` section below.

If either or both of X and Y are 1-D arrays or column vectors, they will be expanded as needed into the appropriate 2-D arrays, making a rectangular grid.

X, Y and C may be masked arrays.  If either C[i, j], or one of the vertices surrounding C[i,j] (X or Y at [i, j], [i+1, j], [i, j+1],[i+1, j+1]) is masked, nothing is plotted.

Keyword arguments:



Return value is a :class:`matplotlib.collection.Collection` instance.

The grid orientation follows the MATLAB convention: an array C with shape (nrows, ncolumns) is plotted with the column number as X and the row number as Y, increasing up; hence it is plotted the way the array would be printed, except that the Y axis is reversed.  That is, C is taken as C*(*y, x).

Similarly for :func:`~matplotlib.pyplot.meshgrid`:

x = np.arange(5) y = np.arange(3) X, Y = meshgrid(x,y)

is equivalent to:



so if you have:

C = rand( len(x), len(y))

then you need:

pcolor(X, Y, C.T)

or:

pcolor(C.T)

MATLAB :func:`pcolor` always discards the last row and column of C, but matplotlib displays the last row and column if X and Y are not specified, or if X and Y have one more row and column than C.

kwargs can be used to control the :class:`~matplotlib.collection.PolyCollection` properties:

%(PolyCollection)s

Note: the default antialiaseds is False if the default edgecolors*="none" is used.  This eliminates artificial lines at patch boundaries, and works regardless of the value of alpha.  If *edgecolors is not "none", then the default antialiaseds is taken from rcParams['patch.antialiased'], which defaults to True. Stroking the edges may be preferred if alpha is 1, but will cause artifacts otherwise.

Additional kwargs: hold = [True|False] overrides default hold state
    """
    _input_ports = [
              ("edgecolorsSequence", "basic:List",
                {'entry_types': "['enum']", 'docstring': "If None, the rc setting is used by default.\n\nIf 'none', edges will not be visible.\n\nAn mpl color or sequence of colors will set the edge color", 'values': "[['none', 'color']]", 'optional': True}),
              ("edgecolorsScalar", "basic:String",
               {'values': "[['none', 'color']]", 'entry_types': "['enum']", 'docstring': "If None, the rc setting is used by default.\n\nIf 'none', edges will not be visible.\n\nAn mpl color or sequence of colors will set the edge color", 'optional': True}),
              ("None", "basic:Float",
                {'optional': True, 'docstring': 'the alpha blending value'}),
              ("vmin", "basic:Float",
                {'optional': True, 'docstring': 'vmin and vmax are used in conjunction with norm to normalize luminance data.  If either are None, the min and max of the color array C is used.  If you pass a norm instance, vmin and vmax will be ignored.'}),
              ("cmap", "basic:String",
                {'entry_types': "['enum']", 'docstring': 'A :class:`matplotlib.cm.Colormap` instance. If None, use rc settings.', 'values': "[['Colormap']]", 'optional': True}),
              ("alpha", "basic:Float",
                {'optional': True, 'docstring': 'the alpha blending value'}),
              ("vmax", "basic:Float",
                {'optional': True, 'docstring': 'vmin and vmax are used in conjunction with norm to normalize luminance data.  If either are None, the min and max of the color array C is used.  If you pass a norm instance, vmin and vmax will be ignored.'}),
              ("shading", "basic:String",
                {'entry_types': "['enum']", 'docstring': "If 'faceted', a black grid is drawn around each rectangle; if 'flat', edges are not drawn. Default is 'flat', contrary to MATLAB.", 'values': "[['flat', 'faceted']]", 'optional': True, 'defaults': "['flat']"}),
        ]

    _output_ports = [
        ("self", "(MplPcolor)"),
        ]
    

    def compute(self):
        # get args into args, kwargs
        # write out translations
        kwargs = {}            
        if self.hasInputFromPort('edgecolorsSequence'):
            kwargs['edgecolors'] = self.getInputFromPort('edgecolorsSequence')
        elif self.hasInputFromPort('edgecolorsScalar'):
            kwargs['edgecolors'] = self.getInputFromPort('edgecolorsScalar')
        if self.hasInputFromPort('None'):
            kwargs['None'] = self.getInputFromPort('None')
        if self.hasInputFromPort('vmin'):
            kwargs['vmin'] = self.getInputFromPort('vmin')
        if self.hasInputFromPort('cmap'):
            kwargs['cmap'] = self.getInputFromPort('cmap')
        if self.hasInputFromPort('alpha'):
            kwargs['alpha'] = self.getInputFromPort('alpha')
        if self.hasInputFromPort('vmax'):
            kwargs['vmax'] = self.getInputFromPort('vmax')
        if self.hasInputFromPort('shading'):
            kwargs['shading'] = self.getInputFromPort('shading')
        # self.get_fig()
        matplotlib.pyplot.pcolor(**kwargs)        

class MplPcolormesh(MplPlot):
    """call signatures:

pcolormesh(C) pcolormesh(X, Y, C) pcolormesh(C, **kwargs)

C may be a masked array, but X and Y may not.  Masked array support is implemented via cmap and norm; in contrast, :func:`~matplotlib.pyplot.pcolor` simply does not draw quadrilaterals with masked colors or vertices.

Keyword arguments:



Return value is a :class:`matplotlib.collection.QuadMesh` object.

kwargs can be used to control the :class:`matplotlib.collections.QuadMesh` properties:

%(QuadMesh)s

Additional kwargs: hold = [True|False] overrides default hold state
    """
    _input_ports = [
              ("edgecolorsSequence", "basic:List",
                {'entry_types': "['enum']", 'docstring': "If None, the rc setting is used by default.\n\nIf 'None', edges will not be visible.\n\nAn mpl color or sequence of colors will set the edge color", 'values': "[['None', 'color']]", 'optional': True}),
              ("edgecolorsScalar", "basic:String",
               {'values': "[['None', 'color']]", 'entry_types': "['enum']", 'docstring': "If None, the rc setting is used by default.\n\nIf 'None', edges will not be visible.\n\nAn mpl color or sequence of colors will set the edge color", 'optional': True}),
              ("None", "basic:Float",
                {'optional': True, 'docstring': 'the alpha blending value'}),
              ("vmin", "basic:Float",
                {'optional': True, 'docstring': 'vmin and vmax are used in conjunction with norm to normalize luminance data.  If either are None, the min and max of the color array C is used.  If you pass a norm instance, vmin and vmax will be ignored.'}),
              ("cmap", "basic:String",
                {'entry_types': "['enum']", 'docstring': 'A :class:`matplotlib.cm.Colormap` instance. If None, use rc settings.', 'values': "[['Colormap']]", 'optional': True}),
              ("alpha", "basic:Float",
                {'optional': True, 'docstring': 'the alpha blending value'}),
              ("vmax", "basic:Float",
                {'optional': True, 'docstring': 'vmin and vmax are used in conjunction with norm to normalize luminance data.  If either are None, the min and max of the color array C is used.  If you pass a norm instance, vmin and vmax will be ignored.'}),
              ("shading", "basic:String",
                {'entry_types': "['enum']", 'docstring': "If 'faceted', a black grid is drawn around each rectangle; if 'flat', edges are not drawn. Default is 'flat', contrary to MATLAB.", 'values': "[['flat', 'faceted', 'gouraud']]", 'optional': True, 'defaults': "['flat']"}),
              ("norm", "basic:String",
                {'entry_types': "['enum']", 'docstring': 'A :class:`matplotlib.colors.Normalize` instance is used to scale luminance data to 0,1. If None, defaults to :func:`normalize`.', 'values': "[['Normalize']]", 'optional': True}),
        ]

    _output_ports = [
        ("self", "(MplPcolormesh)"),
        ]
    

    def compute(self):
        # get args into args, kwargs
        # write out translations
        kwargs = {}            
        if self.hasInputFromPort('edgecolorsSequence'):
            kwargs['edgecolors'] = self.getInputFromPort('edgecolorsSequence')
        elif self.hasInputFromPort('edgecolorsScalar'):
            kwargs['edgecolors'] = self.getInputFromPort('edgecolorsScalar')
        if self.hasInputFromPort('None'):
            kwargs['None'] = self.getInputFromPort('None')
        if self.hasInputFromPort('vmin'):
            kwargs['vmin'] = self.getInputFromPort('vmin')
        if self.hasInputFromPort('cmap'):
            kwargs['cmap'] = self.getInputFromPort('cmap')
        if self.hasInputFromPort('alpha'):
            kwargs['alpha'] = self.getInputFromPort('alpha')
        if self.hasInputFromPort('vmax'):
            kwargs['vmax'] = self.getInputFromPort('vmax')
        if self.hasInputFromPort('shading'):
            kwargs['shading'] = self.getInputFromPort('shading')
        if self.hasInputFromPort('norm'):
            kwargs['norm'] = self.getInputFromPort('norm')
        # self.get_fig()
        matplotlib.pyplot.pcolormesh(**kwargs)        

class MplPie(MplPlot):
    """call signature:

pie(x, explode=None, labels=None,     colors=('b', 'g', 'r', 'c', 'm', 'y', 'k', 'w'),     autopct=None, pctdistance=0.6, labeldistance=1.1, shadow=False)

Make a pie chart of array x.  The fractional area of each wedge is given by x/sum(x).  If sum(x) <= 1, then the values of x give the fractional area directly and the array will not be normalized.

Keyword arguments:



The pie chart will probably look best if the figure and axes are square.  Eg.:

figure(figsize=(8,8)) ax = axes([0.1, 0.1, 0.8, 0.8])

Additional kwargs: hold = [True|False] overrides default hold state
    """
    _input_ports = [
              ("autopct", "basic:String",
                {'entry_types': "['enum']", 'docstring': 'If not None, is a string or function used to label the wedges with their numeric value.  The label will be placed inside the wedge.  If it is a format string, the label will be fmt%pct. If it is a function, it will be called.', 'values': "[['format function']]", 'optional': True}),
              ("pctdistance", "basic:Float",
                {'optional': True, 'docstring': 'The ratio between the center of each pie slice and the start of the text generated by autopct.  Ignored if autopct is None; default is 0.6.', 'defaults': "['0.6']"}),
              ("labelsSequence", "basic:List",
                {'optional': True, 'docstring': 'A sequence of strings providing the labels for each wedge'}),
              ("labelsScalar", "basic:String",
               {'docstring': 'A sequence of strings providing the labels for each wedge', 'optional': True}),
              ("explode", "basic:List",
                {'optional': True, 'docstring': 'If not None, is a len(x) array which specifies the fraction of the radius with which to offset each wedge.'}),
              ("colors", "basic:List",
                {'optional': True, 'docstring': 'A sequence of matplotlib color args through which the pie chart will cycle.'}),
              ("x", "basic:List",
                {}),
              ("shadow", "basic:Boolean",
                {'optional': True, 'docstring': 'Draw a shadow beneath the pie.', 'defaults': "['False']"}),
              ("hold", "basic:String",
                {'optional': True}),
              ("labeldistance", "basic:Float",
                {'optional': True, 'docstring': 'The radial distance at which the pie labels are drawn', 'defaults': "['1.1']"}),
              ("autotextProperties", "MplTextProperties",
                {}),
              ("wedgeProperties", "MplWedgeProperties",
                {}),
              ("textProperties", "MplTextProperties",
                {}),
        ]

    _output_ports = [
        ("self", "(MplPie)"),
        ]
    

    def compute(self):
        # get args into args, kwargs
        # write out translations
        kwargs = {}            
        if self.hasInputFromPort('autopct'):
            kwargs['autopct'] = self.getInputFromPort('autopct')
        if self.hasInputFromPort('pctdistance'):
            kwargs['pctdistance'] = self.getInputFromPort('pctdistance')
        if self.hasInputFromPort('labelsSequence'):
            kwargs['labels'] = self.getInputFromPort('labelsSequence')
        elif self.hasInputFromPort('labelsScalar'):
            kwargs['labels'] = self.getInputFromPort('labelsScalar')
        if self.hasInputFromPort('explode'):
            kwargs['explode'] = self.getInputFromPort('explode')
        if self.hasInputFromPort('colors'):
            kwargs['colors'] = self.getInputFromPort('colors')
        kwargs['x'] = self.getInputFromPort('x')
        if self.hasInputFromPort('shadow'):
            kwargs['shadow'] = self.getInputFromPort('shadow')
        if self.hasInputFromPort('hold'):
            kwargs['hold'] = self.getInputFromPort('hold')
        if self.hasInputFromPort('labeldistance'):
            kwargs['labeldistance'] = self.getInputFromPort('labeldistance')
        # self.get_fig()
        output = matplotlib.pyplot.pie(**kwargs)        
        if len(output) < 3:
            output = output + ([],)
        wedges = output[0]
        texts = output[1]
        autotexts = output[2]
        if self.hasInputFromPort('autotextProperties'):
            properties = self.getInputFromPort('autotextProperties')
            properties.update_props(autotexts)
        if self.hasInputFromPort('wedgeProperties'):
            properties = self.getInputFromPort('wedgeProperties')
            properties.update_props(wedges)
        if self.hasInputFromPort('textProperties'):
            properties = self.getInputFromPort('textProperties')
            properties.update_props(texts)

class MplPlot_date(MplPlot):
    """call signature:

plot_date(x, y, fmt='bo', tz=None, xdate=True, ydate=False, **kwargs)

Similar to the :func:`~matplotlib.pyplot.plot` command, except the x or y (or both) data is considered to be dates, and the axis is labeled accordingly.

x and/or y can be a sequence of dates represented as float days since 0001-01-01 UTC.

Keyword arguments:

Note if you are using custom date tickers and formatters, it may be necessary to set the formatters/locators after the call to :meth:`plot_date` since :meth:`plot_date` will set the default tick locator to :class:`matplotlib.dates.AutoDateLocator` (if the tick locator is not already set to a :class:`matplotlib.dates.DateLocator` instance) and the default tick formatter to :class:`matplotlib.dates.AutoDateFormatter` (if the tick formatter is not already set to a :class:`matplotlib.dates.DateFormatter` instance).

Valid kwargs are :class:`~matplotlib.lines.Line2D` properties:

%(Line2D)s

Additional kwargs: hold = [True|False] overrides default hold state
    """
    _input_ports = [
              ("tz", "basic:String",
                {'entry_types': "['enum']", 'docstring': 'The time zone to use in labeling dates. If None, defaults to rc value.', 'values': "[[':class:`tzinfo` instance']]", 'optional': True}),
              ("fmt", "basic:String",
                {'optional': True, 'docstring': 'The plot format string.', 'defaults': "['bo']"}),
              ("ydate", "basic:Boolean",
                {'optional': True, 'docstring': 'If True, the y-axis will be labeled with dates.', 'defaults': "['False']"}),
              ("xdate", "basic:Boolean",
                {'optional': True, 'docstring': 'If True, the x-axis will be labeled with dates.', 'defaults': "['True']"}),
              ("y", "basic:String",
                {}),
              ("x", "basic:String",
                {}),
              ("hold", "basic:String",
                {'optional': True}),
        ]

    _output_ports = [
        ("self", "(MplPlot_date)"),
        ]
    

    def compute(self):
        # get args into args, kwargs
        # write out translations
        kwargs = {}            
        if self.hasInputFromPort('tz'):
            kwargs['tz'] = self.getInputFromPort('tz')
        if self.hasInputFromPort('fmt'):
            kwargs['fmt'] = self.getInputFromPort('fmt')
        if self.hasInputFromPort('ydate'):
            kwargs['ydate'] = self.getInputFromPort('ydate')
        if self.hasInputFromPort('xdate'):
            kwargs['xdate'] = self.getInputFromPort('xdate')
        kwargs['y'] = self.getInputFromPort('y')
        kwargs['x'] = self.getInputFromPort('x')
        if self.hasInputFromPort('hold'):
            kwargs['hold'] = self.getInputFromPort('hold')
        # self.get_fig()
        matplotlib.pyplot.plot_date(**kwargs)        

class MplPsd(MplPlot):
    """call signature:

psd(x, NFFT=256, Fs=2, Fc=0, detrend=mlab.detrend_none,     window=mlab.window_hanning, noverlap=0, pad_to=None,     sides='default', scale_by_freq=None, **kwargs)

The power spectral density by Welch's average periodogram method.  The vector x is divided into NFFT length segments.  Each segment is detrended by function detrend and windowed by function window.  noverlap gives the length of the overlap between segments.  The :math:`|\mathrm{fft}(i)|^2` of each segment :math:`i` are averaged to compute Pxx, with a scaling to correct for power loss due to windowing.  Fs is the sampling frequency.

%(PSD)s



Returns the tuple (Pxx, freqs).

For plotting, the power is plotted as :math:`10\log_{10}(P_{xx})` for decibels, though Pxx itself is returned.

kwargs control the :class:`~matplotlib.lines.Line2D` properties:

%(Line2D)s

Example:

Additional kwargs: hold = [True|False] overrides default hold state
    """
    _input_ports = [
              ("Fs", "basic:Integer",
                {'optional': True, 'defaults': "['2']"}),
              ("pad_to", "basic:String",
                {'optional': True}),
              ("scale_by_freq", "basic:String",
                {'optional': True}),
              ("detrend", "basic:String",
                {'optional': True, 'defaults': "['<function detrend_none at 0x101f3b0c8>']"}),
              ("window", "basic:String",
                {'optional': True, 'defaults': "['<function window_hanning at 0x101f367d0>']"}),
              ("Fc", "basic:Integer",
                {'optional': True, 'defaults': "['0']"}),
              ("NFFT", "basic:Integer",
                {'optional': True, 'defaults': "['256']"}),
              ("x", "basic:String",
                {}),
              ("hold", "basic:String",
                {'optional': True}),
              ("sides", "basic:String",
                {'optional': True, 'defaults': "['default']"}),
              ("noverlap", "basic:Integer",
                {'optional': True, 'defaults': "['0']"}),
        ]

    _output_ports = [
        ("self", "(MplPsd)"),
        ]
    

    def compute(self):
        # get args into args, kwargs
        # write out translations
        kwargs = {}            
        if self.hasInputFromPort('Fs'):
            kwargs['Fs'] = self.getInputFromPort('Fs')
        if self.hasInputFromPort('pad_to'):
            kwargs['pad_to'] = self.getInputFromPort('pad_to')
        if self.hasInputFromPort('scale_by_freq'):
            kwargs['scale_by_freq'] = self.getInputFromPort('scale_by_freq')
        if self.hasInputFromPort('detrend'):
            kwargs['detrend'] = self.getInputFromPort('detrend')
        if self.hasInputFromPort('window'):
            kwargs['window'] = self.getInputFromPort('window')
        if self.hasInputFromPort('Fc'):
            kwargs['Fc'] = self.getInputFromPort('Fc')
        if self.hasInputFromPort('NFFT'):
            kwargs['NFFT'] = self.getInputFromPort('NFFT')
        kwargs['x'] = self.getInputFromPort('x')
        if self.hasInputFromPort('hold'):
            kwargs['hold'] = self.getInputFromPort('hold')
        if self.hasInputFromPort('sides'):
            kwargs['sides'] = self.getInputFromPort('sides')
        if self.hasInputFromPort('noverlap'):
            kwargs['noverlap'] = self.getInputFromPort('noverlap')
        # self.get_fig()
        matplotlib.pyplot.psd(**kwargs)        

class MplQuiver(MplPlot):
    """Plot a 2-D field of arrows.

call signatures:

quiver(U, V, **kw) quiver(U, V, C, **kw) quiver(X, Y, U, V, **kw) quiver(X, Y, U, V, C, **kw)

Arguments:

X, Y:

The x and y coordinates of the arrow locations (default is tail of arrow; see pivot kwarg)

U, V:

give the x and y components of the arrow vectors

All arguments may be 1-D or 2-D arrays or sequences. If X and Y are absent, they will be generated as a uniform grid.  If U and V are 2-D arrays but X and Y are 1-D, and if len(X) and len(Y) match the column and row dimensions of U, then X and Y will be expanded with :func:`numpy.meshgrid`.

U, V, C may be masked arrays, but masked X, Y are not supported at present.

Keyword arguments:



The defaults give a slightly swept-back arrow; to make the head a triangle, make headaxislength the same as headlength. To make the arrow more pointed, reduce headwidth or increase headlength and headaxislength. To make the head smaller relative to the shaft, scale down all the head parameters. You will probably do best to leave minshaft alone.

linewidths and edgecolors can be used to customize the arrow outlines. Additional :class:`~matplotlib.collections.PolyCollection` keyword arguments:

agg_filter: unknown alpha: float or None animated: [True | False] antialiased or antialiaseds: Boolean or sequence of booleans array: unknown axes: an :class:`~matplotlib.axes.Axes` instance clim: a length 2 sequence of floats clip_box: a :class:`matplotlib.transforms.Bbox` instance clip_on: [True | False] clip_path: [ (:class:`~matplotlib.path.Path`,         :class:`~matplotlib.transforms.Transform`) |         :class:`~matplotlib.patches.Patch` | None ] cmap: a colormap or registered colormap name color: matplotlib color arg or sequence of rgba tuples colorbar: unknown contains: a callable function edgecolor or edgecolors: matplotlib color arg or sequence of rgba tuples facecolor or facecolors: matplotlib color arg or sequence of rgba tuples figure: a :class:`matplotlib.figure.Figure` instance gid: an id string label: any string linestyle or linestyles or dashes: ['solid' | 'dashed', 'dashdot', 'dotted' |         (offset, on-off-dash-seq) ] linewidth or lw or linewidths: float or sequence of floats lod: [True | False] norm: unknown offsets: float or sequence of floats paths: unknown picker: [None|float|boolean|callable] pickradius: unknown rasterized: [True | False | None] snap: unknown transform: :class:`~matplotlib.transforms.Transform` instance url: a url string urls: unknown visible: [True | False] zorder: any number

Additional kwargs: hold = [True|False] overrides default hold state
    """
    _input_ports = [
              ("scaleSequence", "basic:List",
                {'optional': True, 'docstring': 'data units per arrow length unit, e.g. m/s per plot width; a smaller scale parameter makes the arrow longer.  If None, a simple autoscaling algorithm is used, based on the average vector length and the number of vectors.  The arrow length unit is given by the scale_units parameter'}),
              ("scaleScalar", "basic:Float",
               {'docstring': 'data units per arrow length unit, e.g. m/s per plot width; a smaller scale parameter makes the arrow longer.  If None, a simple autoscaling algorithm is used, based on the average vector length and the number of vectors.  The arrow length unit is given by the scale_units parameter', 'optional': True}),
              ("headaxislength", "basic:Float",
                {'optional': True, 'docstring': 'head length at shaft intersection, default is 4.5', 'defaults': "['4.5']"}),
              ("headlength", "basic:Float",
                {'optional': True, 'docstring': 'head length as multiple of shaft width, default is 5', 'defaults': "['5']"}),
              ("minlength", "basic:Float",
                {'optional': True, 'docstring': 'minimum length as a multiple of shaft width; if an arrow length is less than this, plot a dot (hexagon) of this diameter instead. Default is 1.', 'defaults': "['1']"}),
              ("minshaft", "basic:Float",
                {'optional': True, 'docstring': 'length below which arrow scales, in units of head length. Do not set this to less than 1, or small arrows will look terrible! Default is 1', 'defaults': "['1']"}),
              ("width", "basic:List",
                {'optional': True, 'docstring': 'shaft width in arrow units; default depends on choice of units, above, and number of vectors; a typical starting value is about 0.005 times the width of the plot.'}),
              ("headwidth", "basic:Float",
                {'optional': True, 'docstring': 'head width as multiple of shaft width, default is 3', 'defaults': "['3']"}),
              ("units", "basic:String",
                {'entry_types': "['enum']", 'docstring': "arrow units; the arrow dimensions except for length are in multiples of this unit.\n\n'width' or 'height': the width or height of the axes\n\n'dots' or 'inches': pixels or inches, based on the figure dpi\n\n'x', 'y', or 'xy': X, Y, or sqrt(X^2+Y^2) data units\n\nThe arrows scale differently depending on the units.  For 'x' or 'y', the arrows get larger as one zooms in; for other units, the arrow size is independent of the zoom state.  For 'width or 'height', the arrow size increases with the width and height of the axes, respectively, when the the window is resized; for 'dots' or 'inches', resizing does not change the arrows.", 'values': "[['width', 'height', 'dots', 'inches', 'x', 'y', 'xy']]", 'optional': True}),
              ("pivot", "basic:String",
                {'entry_types': "['enum']", 'docstring': 'The part of the arrow that is at the grid point; the arrow rotates about this point, hence the name pivot.', 'values': "[['tail', 'middle', 'tip']]", 'optional': True}),
              ("colorSequence", "basic:List",
                {'entry_types': "['enum']", 'docstring': 'This is a synonym for the :class:`~matplotlib.collections.PolyCollection` facecolor kwarg. If C has been set, color has no effect.', 'values': "[['color']]", 'optional': True}),
              ("colorScalar", "basic:String",
               {'values': "[['color']]", 'entry_types': "['enum']", 'docstring': 'This is a synonym for the :class:`~matplotlib.collections.PolyCollection` facecolor kwarg. If C has been set, color has no effect.', 'optional': True}),
        ]

    _output_ports = [
        ("self", "(MplQuiver)"),
        ]
    

    def compute(self):
        # get args into args, kwargs
        # write out translations
        kwargs = {}            
        if self.hasInputFromPort('scaleSequence'):
            kwargs['scale'] = self.getInputFromPort('scaleSequence')
        elif self.hasInputFromPort('scaleScalar'):
            kwargs['scale'] = self.getInputFromPort('scaleScalar')
        if self.hasInputFromPort('headaxislength'):
            kwargs['headaxislength'] = self.getInputFromPort('headaxislength')
        if self.hasInputFromPort('headlength'):
            kwargs['headlength'] = self.getInputFromPort('headlength')
        if self.hasInputFromPort('minlength'):
            kwargs['minlength'] = self.getInputFromPort('minlength')
        if self.hasInputFromPort('minshaft'):
            kwargs['minshaft'] = self.getInputFromPort('minshaft')
        if self.hasInputFromPort('width'):
            kwargs['width'] = self.getInputFromPort('width')
        if self.hasInputFromPort('headwidth'):
            kwargs['headwidth'] = self.getInputFromPort('headwidth')
        if self.hasInputFromPort('units'):
            kwargs['units'] = self.getInputFromPort('units')
        if self.hasInputFromPort('pivot'):
            kwargs['pivot'] = self.getInputFromPort('pivot')
        if self.hasInputFromPort('colorSequence'):
            kwargs['color'] = self.getInputFromPort('colorSequence')
        elif self.hasInputFromPort('colorScalar'):
            kwargs['color'] = self.getInputFromPort('colorScalar')
        # self.get_fig()
        matplotlib.pyplot.quiver(**kwargs)        

class MplQuiverkey(MplPlot):
    """Add a key to a quiver plot.

call signature:

quiverkey(Q, X, Y, U, label, **kw)

Arguments:



Keyword arguments:



Any additional keyword arguments are used to override vector properties taken from Q.

The positioning of the key depends on X, Y, coordinates, and labelpos.  If labelpos is 'N' or 'S', X, Y give the position of the middle of the key arrow.  If labelpos is 'E', X, Y positions the head, and if labelpos is 'W', X, Y positions the tail; in either of these two cases, X, Y is somewhere in the middle of the arrow+label key object.

Additional kwargs: hold = [True|False] overrides default hold state
    """
    _input_ports = [
              ("color", "basic:Color",
                {'optional': True, 'docstring': 'overrides face and edge colors from Q.'}),
              ("coordinatesSequence", "basic:List",
                {'entry_types': "['enum']", 'docstring': "Coordinate system and units for X, Y: 'axes' and 'figure' are normalized coordinate systems with 0,0 in the lower left and 1,1 in the upper right; 'data' are the axes data coordinates (used for the locations of the vectors in the quiver plot itself); 'inches' is position in the figure in inches, with 0,0 at the lower left corner.", 'values': "[['axes', 'figure', 'data', 'inches']]", 'optional': True}),
              ("coordinatesScalar", "basic:String",
               {'values': "[['axes', 'figure', 'data', 'inches']]", 'entry_types': "['enum']", 'docstring': "Coordinate system and units for X, Y: 'axes' and 'figure' are normalized coordinate systems with 0,0 in the lower left and 1,1 in the upper right; 'data' are the axes data coordinates (used for the locations of the vectors in the quiver plot itself); 'inches' is position in the figure in inches, with 0,0 at the lower left corner.", 'optional': True}),
              ("label", "basic:String",
                {'optional': True, 'docstring': 'a string with the length and units of the key'}),
              ("Q", "basic:String",
                {'optional': True, 'docstring': 'The Quiver instance returned by a call to quiver.'}),
              ("labelcolor", "basic:Color",
                {'optional': True, 'docstring': 'defaults to default :class:`~matplotlib.text.Text` color.'}),
              ("fontproperties", "basic:String",
                {'optional': True, 'docstring': 'A dictionary with keyword arguments accepted by the :class:`~matplotlib.font_manager.FontProperties` initializer: family, style, variant, size, weight'}),
              ("U", "basic:String",
                {'optional': True, 'docstring': 'The length of the key'}),
              ("labelpos", "basic:String",
                {'entry_types': "['enum']", 'docstring': 'Position the label above, below, to the right, to the left of the arrow, respectively.', 'values': "[['N', 'S', 'E', 'W']]", 'optional': True}),
              ("Y", "basic:String",
                {'optional': True, 'docstring': 'The location of the key; additional explanation follows.'}),
              ("X", "basic:String",
                {'optional': True, 'docstring': 'The location of the key; additional explanation follows.'}),
              ("labelsep", "basic:Float",
                {'optional': True, 'docstring': 'Distance in inches between the arrow and the label.  Default is 0.1', 'defaults': "['0.1']"}),
        ]

    _output_ports = [
        ("self", "(MplQuiverkey)"),
        ]
    

    def compute(self):
        # get args into args, kwargs
        # write out translations
        kwargs = {}            
        if self.hasInputFromPort('color'):
            kwargs['color'] = self.getInputFromPort('color')
            kwargs['color'] = translate_color(kwargs['color'])
        if self.hasInputFromPort('coordinatesSequence'):
            kwargs['coordinates'] = self.getInputFromPort('coordinatesSequence')
        elif self.hasInputFromPort('coordinatesScalar'):
            kwargs['coordinates'] = self.getInputFromPort('coordinatesScalar')
        if self.hasInputFromPort('label'):
            kwargs['label'] = self.getInputFromPort('label')
        if self.hasInputFromPort('Q'):
            kwargs['Q'] = self.getInputFromPort('Q')
        if self.hasInputFromPort('labelcolor'):
            kwargs['labelcolor'] = self.getInputFromPort('labelcolor')
            kwargs['labelcolor'] = translate_color(kwargs['labelcolor'])
        if self.hasInputFromPort('fontproperties'):
            kwargs['fontproperties'] = self.getInputFromPort('fontproperties')
        if self.hasInputFromPort('U'):
            kwargs['U'] = self.getInputFromPort('U')
        if self.hasInputFromPort('labelpos'):
            kwargs['labelpos'] = self.getInputFromPort('labelpos')
        if self.hasInputFromPort('Y'):
            kwargs['Y'] = self.getInputFromPort('Y')
        if self.hasInputFromPort('X'):
            kwargs['X'] = self.getInputFromPort('X')
        if self.hasInputFromPort('labelsep'):
            kwargs['labelsep'] = self.getInputFromPort('labelsep')
        # self.get_fig()
        matplotlib.pyplot.quiverkey(**kwargs)        

class MplScatter(MplPlot):
    """call signatures:

scatter(x, y, s=20, c='b', marker='o', cmap=None, norm=None,         vmin=None, vmax=None, alpha=None, linewidths=None,         verts=None, **kwargs)

Make a scatter plot of x versus y, where x, y are converted to 1-D sequences which must be of the same length, N.

Keyword arguments:



Any or all of x, y, s, and c may be masked arrays, in which case all masks will be combined and only unmasked points will be plotted.

Other keyword arguments: the color mapping and normalization arguments will be used only if c is an array of floats.



Optional kwargs control the :class:`~matplotlib.collections.Collection` properties; in particular:



Here are the standard descriptions of all the :class:`~matplotlib.collections.Collection` kwargs:

%(Collection)s

A :class:`~matplotlib.collections.Collection` instance is returned.

Additional kwargs: hold = [True|False] overrides default hold state
    """
    _input_ports = [
              ("vmax", "basic:String",
                {'optional': True, 'docstring': 'vmin and vmax are used in conjunction with norm to normalize luminance data.  If either are None, the min and max of the color array C is used.  Note if you pass a norm instance, your settings for vmin and vmax will be ignored.'}),
              ("edgecolors", "basic:String",
                {'optional': True, 'docstring': "The string 'none' to plot faces with no outlines"}),
              ("cSequence", "basic:List",
                {'optional': True, 'docstring': 'a color. c can be a single color format string, or a sequence of color specifications of length N, or a sequence of N numbers to be mapped to colors using the cmap and norm specified via kwargs (see below). Note that c should not be a single numeric RGB or RGBA sequence because that is indistinguishable from an array of values to be colormapped.  c can be a 2-D array in which the rows are RGB or RGBA, however.', 'defaults': "['b']"}),
              ("cScalar", "basic:String",
               {'docstring': 'a color. c can be a single color format string, or a sequence of color specifications of length N, or a sequence of N numbers to be mapped to colors using the cmap and norm specified via kwargs (see below). Note that c should not be a single numeric RGB or RGBA sequence because that is indistinguishable from an array of values to be colormapped.  c can be a 2-D array in which the rows are RGB or RGBA, however.', 'optional': True, 'defaults': "['b']"}),
              ("vmin", "basic:String",
                {'optional': True, 'docstring': 'vmin and vmax are used in conjunction with norm to normalize luminance data.  If either are None, the min and max of the color array C is used.  Note if you pass a norm instance, your settings for vmin and vmax will be ignored.'}),
              ("faceted", "basic:Boolean",
                {'optional': True, 'defaults': "['True']"}),
              ("linewidthsSequence", "basic:List",
                {'optional': True, 'docstring': 'If None, defaults to (lines.linewidth,).  Note that this is a tuple, and if you set the linewidths argument you must set it as a sequence of floats, as required by :class:`~matplotlib.collections.RegularPolyCollection`.'}),
              ("linewidthsScalar", "basic:Float",
               {'docstring': 'If None, defaults to (lines.linewidth,).  Note that this is a tuple, and if you set the linewidths argument you must set it as a sequence of floats, as required by :class:`~matplotlib.collections.RegularPolyCollection`.', 'optional': True}),
              ("marker", "basic:String",
                {'optional': True, 'docstring': 'can be one of:\n\n%(MarkerTable)s', 'defaults': "['o']"}),
              ("s", "basic:Float",
                {'optional': True, 'docstring': 'size in points^2.  It is a scalar or an array of the same length as x and y.', 'defaults': "['20']"}),
              ("cmap", "basic:String",
                {'optional': True, 'docstring': 'A :class:`matplotlib.colors.Colormap` instance or registered name. If None, defaults to rc image.cmap. cmap is only used if c is an array of floats.'}),
              ("verts", "basic:String",
                {'optional': True}),
              ("alpha", "basic:Float",
                {'optional': True, 'docstring': 'The alpha value for the patches'}),
              ("y", "basic:List",
                {}),
              ("x", "basic:List",
                {}),
              ("hold", "basic:String",
                {'optional': True}),
              ("facecolors", "basic:String",
                {'optional': True, 'docstring': "The string 'none' to plot unfilled outlines"}),
              ("norm", "basic:String",
                {'optional': True, 'docstring': 'A :class:`matplotlib.colors.Normalize` instance is used to scale luminance data to 0, 1. If None, use the default :func:`normalize`. norm is only used if c is an array of floats.'}),
        ]

    _output_ports = [
        ("self", "(MplScatter)"),
        ]
    

    def compute(self):
        # get args into args, kwargs
        # write out translations
        kwargs = {}            
        if self.hasInputFromPort('vmax'):
            kwargs['vmax'] = self.getInputFromPort('vmax')
        if self.hasInputFromPort('edgecolors'):
            kwargs['edgecolors'] = self.getInputFromPort('edgecolors')
        if self.hasInputFromPort('cSequence'):
            kwargs['c'] = self.getInputFromPort('cSequence')
        elif self.hasInputFromPort('cScalar'):
            kwargs['c'] = self.getInputFromPort('cScalar')
        if self.hasInputFromPort('vmin'):
            kwargs['vmin'] = self.getInputFromPort('vmin')
        if self.hasInputFromPort('faceted'):
            kwargs['faceted'] = self.getInputFromPort('faceted')
        if self.hasInputFromPort('linewidthsSequence'):
            kwargs['linewidths'] = self.getInputFromPort('linewidthsSequence')
        elif self.hasInputFromPort('linewidthsScalar'):
            kwargs['linewidths'] = self.getInputFromPort('linewidthsScalar')
        if self.hasInputFromPort('marker'):
            kwargs['marker'] = self.getInputFromPort('marker')
        if self.hasInputFromPort('s'):
            kwargs['s'] = self.getInputFromPort('s')
        if self.hasInputFromPort('cmap'):
            kwargs['cmap'] = self.getInputFromPort('cmap')
        if self.hasInputFromPort('verts'):
            kwargs['verts'] = self.getInputFromPort('verts')
        if self.hasInputFromPort('alpha'):
            kwargs['alpha'] = self.getInputFromPort('alpha')
        kwargs['y'] = self.getInputFromPort('y')
        kwargs['x'] = self.getInputFromPort('x')
        if self.hasInputFromPort('hold'):
            kwargs['hold'] = self.getInputFromPort('hold')
        if self.hasInputFromPort('facecolors'):
            kwargs['facecolors'] = self.getInputFromPort('facecolors')
        if self.hasInputFromPort('norm'):
            kwargs['norm'] = self.getInputFromPort('norm')
        # self.get_fig()
        matplotlib.pyplot.scatter(**kwargs)        

class MplSemilogx(MplPlot):
    """call signature:

semilogx(*args, **kwargs)

Make a plot with log scaling on the x axis.

:func:`semilogx` supports all the keyword arguments of :func:`~matplotlib.pyplot.plot` and :meth:`matplotlib.axes.Axes.set_xscale`.

Notable keyword arguments:



The remaining valid kwargs are :class:`~matplotlib.lines.Line2D` properties:

%(Line2D)s

Additional kwargs: hold = [True|False] overrides default hold state
    """
    _input_ports = [
              ("basex", "basic:Float",
                {'optional': True, 'docstring': 'base of the x logarithm'}),
              ("nonposx", "basic:String",
                {'entry_types': "['enum']", 'docstring': 'non-positive values in x can be masked as invalid, or clipped to a very small positive number', 'values': "[['mask', 'clip']]", 'optional': True}),
              ("subsx", "basic:List",
                {'optional': True, 'docstring': 'The location of the minor xticks; None defaults to autosubs, which depend on the number of decades in the plot; see :meth:`~matplotlib.axes.Axes.set_xscale` for details.'}),
        ]

    _output_ports = [
        ("self", "(MplSemilogx)"),
        ]
    

    def compute(self):
        # get args into args, kwargs
        # write out translations
        kwargs = {}            
        if self.hasInputFromPort('basex'):
            kwargs['basex'] = self.getInputFromPort('basex')
        if self.hasInputFromPort('nonposx'):
            kwargs['nonposx'] = self.getInputFromPort('nonposx')
        if self.hasInputFromPort('subsx'):
            kwargs['subsx'] = self.getInputFromPort('subsx')
        # self.get_fig()
        matplotlib.pyplot.semilogx(**kwargs)        

class MplSemilogy(MplPlot):
    """call signature:

semilogy(*args, **kwargs)

Make a plot with log scaling on the y axis.

:func:`semilogy` supports all the keyword arguments of :func:`~matplotlib.pylab.plot` and :meth:`matplotlib.axes.Axes.set_yscale`.

Notable keyword arguments:



The remaining valid kwargs are :class:`~matplotlib.lines.Line2D` properties:

%(Line2D)s

Additional kwargs: hold = [True|False] overrides default hold state
    """
    _input_ports = [
              ("basey", "basic:Float",
                {'optional': True, 'docstring': 'Base of the y logarithm'}),
              ("nonposy", "basic:String",
                {'entry_types': "['enum']", 'docstring': 'non-positive values in y can be masked as invalid, or clipped to a very small positive number', 'values': "[['mask', 'clip']]", 'optional': True}),
              ("subsy", "basic:List",
                {'optional': True, 'docstring': 'The location of the minor yticks; None defaults to autosubs, which depend on the number of decades in the plot; see :meth:`~matplotlib.axes.Axes.set_yscale` for details.'}),
        ]

    _output_ports = [
        ("self", "(MplSemilogy)"),
        ]
    

    def compute(self):
        # get args into args, kwargs
        # write out translations
        kwargs = {}            
        if self.hasInputFromPort('basey'):
            kwargs['basey'] = self.getInputFromPort('basey')
        if self.hasInputFromPort('nonposy'):
            kwargs['nonposy'] = self.getInputFromPort('nonposy')
        if self.hasInputFromPort('subsy'):
            kwargs['subsy'] = self.getInputFromPort('subsy')
        # self.get_fig()
        matplotlib.pyplot.semilogy(**kwargs)        

class MplSpecgram(MplPlot):
    """call signature:

specgram(x, NFFT=256, Fs=2, Fc=0, detrend=mlab.detrend_none,          window=mlab.window_hanning, noverlap=128,          cmap=None, xextent=None, pad_to=None, sides='default',          scale_by_freq=None, **kwargs)

Compute a spectrogram of data in x.  Data are split into NFFT length segments and the PSD of each section is computed.  The windowing function window is applied to each segment, and the amount of overlap of each segment is specified with noverlap.

%(PSD)s

kwargs:

Additional kwargs are passed on to imshow which makes the specgram image

Return value is (Pxx, freqs, bins, im):

bins are the time points the spectrogram is calculated over

freqs is an array of frequencies

Pxx is a len(times) x len(freqs) array of power

im is a :class:`matplotlib.image.AxesImage` instance

Note: If x is real (i.e. non-complex), only the positive spectrum is shown.  If x is complex, both positive and negative parts of the spectrum are shown.  This can be overridden using the sides keyword argument.

Example:

Additional kwargs: hold = [True|False] overrides default hold state
    """
    _input_ports = [
              ("Fs", "basic:Integer",
                {'optional': True, 'defaults': "['2']"}),
              ("pad_to", "basic:String",
                {'optional': True}),
              ("scale_by_freq", "basic:String",
                {'optional': True}),
              ("xextent", "basic:String",
                {'optional': True}),
              ("detrend", "basic:String",
                {'optional': True, 'defaults': "['<function detrend_none at 0x101f3b0c8>']"}),
              ("window", "basic:String",
                {'optional': True, 'defaults': "['<function window_hanning at 0x101f367d0>']"}),
              ("Fc", "basic:Integer",
                {'optional': True, 'defaults': "['0']"}),
              ("NFFT", "basic:Integer",
                {'optional': True, 'defaults': "['256']"}),
              ("cmap", "basic:String",
                {'optional': True}),
              ("x", "basic:String",
                {}),
              ("hold", "basic:String",
                {'optional': True}),
              ("sides", "basic:String",
                {'optional': True, 'defaults': "['default']"}),
              ("noverlap", "basic:Integer",
                {'optional': True, 'defaults': "['128']"}),
        ]

    _output_ports = [
        ("self", "(MplSpecgram)"),
        ]
    

    def compute(self):
        # get args into args, kwargs
        # write out translations
        kwargs = {}            
        if self.hasInputFromPort('Fs'):
            kwargs['Fs'] = self.getInputFromPort('Fs')
        if self.hasInputFromPort('pad_to'):
            kwargs['pad_to'] = self.getInputFromPort('pad_to')
        if self.hasInputFromPort('scale_by_freq'):
            kwargs['scale_by_freq'] = self.getInputFromPort('scale_by_freq')
        if self.hasInputFromPort('xextent'):
            kwargs['xextent'] = self.getInputFromPort('xextent')
        if self.hasInputFromPort('detrend'):
            kwargs['detrend'] = self.getInputFromPort('detrend')
        if self.hasInputFromPort('window'):
            kwargs['window'] = self.getInputFromPort('window')
        if self.hasInputFromPort('Fc'):
            kwargs['Fc'] = self.getInputFromPort('Fc')
        if self.hasInputFromPort('NFFT'):
            kwargs['NFFT'] = self.getInputFromPort('NFFT')
        if self.hasInputFromPort('cmap'):
            kwargs['cmap'] = self.getInputFromPort('cmap')
        kwargs['x'] = self.getInputFromPort('x')
        if self.hasInputFromPort('hold'):
            kwargs['hold'] = self.getInputFromPort('hold')
        if self.hasInputFromPort('sides'):
            kwargs['sides'] = self.getInputFromPort('sides')
        if self.hasInputFromPort('noverlap'):
            kwargs['noverlap'] = self.getInputFromPort('noverlap')
        # self.get_fig()
        matplotlib.pyplot.specgram(**kwargs)        

class MplStackplot(MplPlot):
    """call signature:

specgram(x, NFFT=256, Fs=2, Fc=0, detrend=mlab.detrend_none,          window=mlab.window_hanning, noverlap=128,          cmap=None, xextent=None, pad_to=None, sides='default',          scale_by_freq=None, **kwargs)

Compute a spectrogram of data in x.  Data are split into NFFT length segments and the PSD of each section is computed.  The windowing function window is applied to each segment, and the amount of overlap of each segment is specified with noverlap.

%(PSD)s

kwargs:

Additional kwargs are passed on to imshow which makes the specgram image

Return value is (Pxx, freqs, bins, im):

bins are the time points the spectrogram is calculated over

freqs is an array of frequencies

Pxx is a len(times) x len(freqs) array of power

im is a :class:`matplotlib.image.AxesImage` instance

Note: If x is real (i.e. non-complex), only the positive spectrum is shown.  If x is complex, both positive and negative parts of the spectrum are shown.  This can be overridden using the sides keyword argument.

Example:

Additional kwargs: hold = [True|False] overrides default hold state
    """
    _input_ports = [
              ("Fs", "basic:Integer",
                {'optional': True, 'defaults': "['2']"}),
              ("pad_to", "basic:String",
                {'optional': True}),
              ("scale_by_freq", "basic:String",
                {'optional': True}),
              ("xextent", "basic:String",
                {'optional': True}),
              ("detrend", "basic:String",
                {'optional': True, 'defaults': "['<function detrend_none at 0x101f3b0c8>']"}),
              ("window", "basic:String",
                {'optional': True, 'defaults': "['<function window_hanning at 0x101f367d0>']"}),
              ("Fc", "basic:Integer",
                {'optional': True, 'defaults': "['0']"}),
              ("NFFT", "basic:Integer",
                {'optional': True, 'defaults': "['256']"}),
              ("cmap", "basic:String",
                {'optional': True}),
              ("x", "basic:String",
                {}),
              ("hold", "basic:String",
                {'optional': True}),
              ("sides", "basic:String",
                {'optional': True, 'defaults': "['default']"}),
              ("noverlap", "basic:Integer",
                {'optional': True, 'defaults': "['128']"}),
        ]

    _output_ports = [
        ("self", "(MplStackplot)"),
        ]
    

    def compute(self):
        # get args into args, kwargs
        # write out translations
        kwargs = {}            
        if self.hasInputFromPort('Fs'):
            kwargs['Fs'] = self.getInputFromPort('Fs')
        if self.hasInputFromPort('pad_to'):
            kwargs['pad_to'] = self.getInputFromPort('pad_to')
        if self.hasInputFromPort('scale_by_freq'):
            kwargs['scale_by_freq'] = self.getInputFromPort('scale_by_freq')
        if self.hasInputFromPort('xextent'):
            kwargs['xextent'] = self.getInputFromPort('xextent')
        if self.hasInputFromPort('detrend'):
            kwargs['detrend'] = self.getInputFromPort('detrend')
        if self.hasInputFromPort('window'):
            kwargs['window'] = self.getInputFromPort('window')
        if self.hasInputFromPort('Fc'):
            kwargs['Fc'] = self.getInputFromPort('Fc')
        if self.hasInputFromPort('NFFT'):
            kwargs['NFFT'] = self.getInputFromPort('NFFT')
        if self.hasInputFromPort('cmap'):
            kwargs['cmap'] = self.getInputFromPort('cmap')
        kwargs['x'] = self.getInputFromPort('x')
        if self.hasInputFromPort('hold'):
            kwargs['hold'] = self.getInputFromPort('hold')
        if self.hasInputFromPort('sides'):
            kwargs['sides'] = self.getInputFromPort('sides')
        if self.hasInputFromPort('noverlap'):
            kwargs['noverlap'] = self.getInputFromPort('noverlap')
        # self.get_fig()
        matplotlib.pyplot.stackplot(**kwargs)        

class MplStem(MplPlot):
    """call signature:

stem(x, y, linefmt='b-', markerfmt='bo', basefmt='r-')

A stem plot plots vertical lines (using linefmt) at each x location from the baseline to y, and places a marker there using markerfmt.  A horizontal line at 0 is is plotted using basefmt.

Return value is a tuple (markerline, stemlines, baseline).

Example:

Additional kwargs: hold = [True|False] overrides default hold state
    """
    _input_ports = [
              ("linefmt", "basic:String",
                {'optional': True, 'defaults': "['b-']"}),
              ("markerfmt", "basic:String",
                {'optional': True, 'defaults': "['bo']"}),
              ("y", "basic:String",
                {}),
              ("x", "basic:String",
                {}),
              ("hold", "basic:String",
                {'optional': True}),
              ("basefmt", "basic:String",
                {'optional': True, 'defaults': "['r-']"}),
        ]

    _output_ports = [
        ("self", "(MplStem)"),
        ]
    

    def compute(self):
        # get args into args, kwargs
        # write out translations
        kwargs = {}            
        if self.hasInputFromPort('linefmt'):
            kwargs['linefmt'] = self.getInputFromPort('linefmt')
        if self.hasInputFromPort('markerfmt'):
            kwargs['markerfmt'] = self.getInputFromPort('markerfmt')
        kwargs['y'] = self.getInputFromPort('y')
        kwargs['x'] = self.getInputFromPort('x')
        if self.hasInputFromPort('hold'):
            kwargs['hold'] = self.getInputFromPort('hold')
        if self.hasInputFromPort('basefmt'):
            kwargs['basefmt'] = self.getInputFromPort('basefmt')
        # self.get_fig()
        matplotlib.pyplot.stem(**kwargs)        

class MplStep(MplPlot):
    """call signature:

step(x, y, *args, **kwargs)

Make a step plot. Additional keyword args to :func:`step` are the same as those for :func:`~matplotlib.pyplot.plot`.

x and y must be 1-D sequences, and it is assumed, but not checked, that x is uniformly increasing.

Keyword arguments:

Additional kwargs: hold = [True|False] overrides default hold state
    """
    _input_ports = [
              ("y", "basic:String",
                {}),
              ("x", "basic:String",
                {}),
              ("where", "basic:String",
                {'entry_types': "['enum']", 'docstring': "If 'pre', the interval from x[i] to x[i+1] has level y[i+1]\n\nIf 'post', that interval has level y[i]\n\nIf 'mid', the jumps in y occur half-way between the x-values.", 'values': "[['pre', 'post', 'mid']]", 'optional': True}),
        ]

    _output_ports = [
        ("self", "(MplStep)"),
        ]
    

    def compute(self):
        # get args into args, kwargs
        # write out translations
        kwargs = {}            
        kwargs['y'] = self.getInputFromPort('y')
        kwargs['x'] = self.getInputFromPort('x')
        if self.hasInputFromPort('where'):
            kwargs['where'] = self.getInputFromPort('where')
        # self.get_fig()
        matplotlib.pyplot.step(**kwargs)        

class MplStreamplot(MplPlot):
    """call signature:

step(x, y, *args, **kwargs)

Make a step plot. Additional keyword args to :func:`step` are the same as those for :func:`~matplotlib.pyplot.plot`.

x and y must be 1-D sequences, and it is assumed, but not checked, that x is uniformly increasing.

Keyword arguments:

Additional kwargs: hold = [True|False] overrides default hold state
    """
    _input_ports = [
              ("y", "basic:String",
                {}),
              ("x", "basic:String",
                {}),
              ("where", "basic:String",
                {'entry_types': "['enum']", 'docstring': "If 'pre', the interval from x[i] to x[i+1] has level y[i+1]\n\nIf 'post', that interval has level y[i]\n\nIf 'mid', the jumps in y occur half-way between the x-values.", 'values': "[['pre', 'post', 'mid']]", 'optional': True}),
        ]

    _output_ports = [
        ("self", "(MplStreamplot)"),
        ]
    

    def compute(self):
        # get args into args, kwargs
        # write out translations
        kwargs = {}            
        kwargs['y'] = self.getInputFromPort('y')
        kwargs['x'] = self.getInputFromPort('x')
        if self.hasInputFromPort('where'):
            kwargs['where'] = self.getInputFromPort('where')
        # self.get_fig()
        matplotlib.pyplot.streamplot(**kwargs)        

class MplTricontour(MplPlot):
    """:func:`~matplotlib.pyplot.tricontour` and :func:`~matplotlib.pyplot.tricontourf` draw contour lines and filled contours, respectively, on an unstructured triangular grid.  Except as noted, function signatures and return values are the same for both versions.

The triangulation can be specified in one of two ways; either:

tricontour(triangulation, ...)

where triangulation is a :class:`~matplotlib.tri.Triangulation` object, or

tricontour(x, y, ...) tricontour(x, y, triangles, ...) tricontour(x, y, triangles=triangles, ...) tricontour(x, y, mask=mask, ...) tricontour(x, y, triangles, mask=mask, ...)

in which case a Triangulation object will be created.  See :class:`~matplotlib.tri.Triangulation` for a explanation of these possibilities.

The remaining arguments may be:

tricontour(..., Z)

where Z is the array of values to contour, one per point in the triangulation.  The level values are chosen automatically.

tricontour(..., Z, N)

contour N automatically-chosen levels.

tricontour(..., Z, V)

draw contour lines at the values specified in sequence V

tricontourf(..., Z, V)

fill the (len(V)-1) regions between the values in V

tricontour(Z, **kwargs)

Use keyword args to control colors, linewidth, origin, cmap ... see below for more details.

C = tricontour(...) returns a :class:`~matplotlib.contour.TriContourSet` object.

Optional keyword arguments:

extent: [ None | (x0,x1,y0,y1) ]

If origin is not None, then extent is interpreted as in :func:`matplotlib.pyplot.imshow`: it gives the outer pixel boundaries. In this case, the position of Z[0,0] is the center of the pixel, not a corner. If origin is None, then (x0, y0) is the position of Z[0,0], and (x1, y1) is the position of Z[-1,-1].

This keyword is not active if X and Y are specified in the call to contour.

tricontour-only keyword arguments:



tricontourf-only keyword arguments:



Note: tricontourf fills intervals that are closed at the top; that is, for boundaries z1 and z2, the filled region is:

z1 < z <= z2

There is one exception: if the lowest boundary coincides with the minimum value of the z array, then that minimum value will be included in the lowest interval.

Examples:

Additional kwargs: hold = [True|False] overrides default hold state
    """
    _input_ports = [
              ("origin", "basic:String",
                {'entry_types': "['enum']", 'docstring': "If None, the first value of Z will correspond to the lower left corner, location (0,0). If 'image', the rc value for image.origin will be used.\n\nThis keyword is not active if X and Y are specified in the call to contour.", 'values': "[['upper', 'lower', 'image']]", 'optional': True}),
              ("linestyles", "basic:String",
                {'entry_types': "['enum']", 'docstring': "If linestyles is None, the 'solid' is used.\n\nlinestyles can also be an iterable of the above strings specifying a set of linestyles to be used. If this iterable is shorter than the number of contour levels it will be repeated as necessary.\n\nIf contour is using a monochrome colormap and the contour level is less than 0, then the linestyle specified in contour.negative_linestyle in matplotlibrc will be used.", 'values': "[['solid', 'dashed', 'dashdot', 'dotted']]", 'optional': True}),
              ("levelsSequence", "basic:List",
                {'optional': True, 'docstring': 'A list of floating point numbers indicating the level curves to draw; eg to draw just the zero contour pass levels=[0]'}),
              ("levelsScalar", "basic:Float",
               {'docstring': 'A list of floating point numbers indicating the level curves to draw; eg to draw just the zero contour pass levels=[0]', 'optional': True}),
              ("linewidths", "basic:String",
                {'entry_types': "['enum']", 'docstring': 'If linewidths is None, the default width in lines.linewidth in matplotlibrc is used.\n\nIf a number, all levels will be plotted with this linewidth.\n\nIf a tuple, different levels will be plotted with different linewidths in the order specified', 'values': "[['number', 'tuple of numbers']]", 'optional': True}),
              ("colors", "basic:Color",
                {'entry_types': "['enum']", 'docstring': "If None, the colormap specified by cmap will be used.\n\nIf a string, like 'r' or 'red', all levels will be plotted in this color.\n\nIf a tuple of matplotlib color args (string, float, rgb, etc), different levels will be plotted in different colors in the order specified.", 'values': "[['(mpl_colors)']]", 'optional': True}),
              ("cmap", "basic:String",
                {'entry_types': "['enum']", 'docstring': 'A cm :class:`~matplotlib.cm.Colormap` instance or None. If cmap is None and colors is None, a default Colormap is used.', 'values': "[['Colormap']]", 'optional': True}),
              ("antialiased", "basic:Boolean",
                {'optional': True, 'docstring': 'enable antialiasing'}),
              ("nchunk", "basic:Integer",
                {'entry_types': "['enum']", 'docstring': 'If 0, no subdivision of the domain. Specify a positive integer to divide the domain into subdomains of roughly nchunk by nchunk points. This may never actually be advantageous, so this option may be removed. Chunking introduces artifacts at the chunk boundaries unless antialiased is False.', 'values': '[[0]]', 'optional': True}),
              ("alpha", "basic:Float",
                {'optional': True, 'docstring': 'The alpha blending value'}),
              ("norm", "basic:String",
                {'entry_types': "['enum']", 'docstring': 'A :class:`matplotlib.colors.Normalize` instance for scaling data values to colors. If norm is None and colors is None, the default linear scaling is used.', 'values': "[['Normalize']]", 'optional': True}),
        ]

    _output_ports = [
        ("self", "(MplTricontour)"),
        ]
    

    def compute(self):
        # get args into args, kwargs
        # write out translations
        kwargs = {}            
        if self.hasInputFromPort('origin'):
            kwargs['origin'] = self.getInputFromPort('origin')
        if self.hasInputFromPort('linestyles'):
            kwargs['linestyles'] = self.getInputFromPort('linestyles')
        if self.hasInputFromPort('levelsSequence'):
            kwargs['levels'] = self.getInputFromPort('levelsSequence')
        elif self.hasInputFromPort('levelsScalar'):
            kwargs['levels'] = self.getInputFromPort('levelsScalar')
        if self.hasInputFromPort('linewidths'):
            kwargs['linewidths'] = self.getInputFromPort('linewidths')
        if self.hasInputFromPort('colors'):
            kwargs['colors'] = self.getInputFromPort('colors')
            kwargs['colors'] = translate_color(kwargs['colors'])
        if self.hasInputFromPort('cmap'):
            kwargs['cmap'] = self.getInputFromPort('cmap')
        if self.hasInputFromPort('antialiased'):
            kwargs['antialiased'] = self.getInputFromPort('antialiased')
        if self.hasInputFromPort('nchunk'):
            kwargs['nchunk'] = self.getInputFromPort('nchunk')
        if self.hasInputFromPort('alpha'):
            kwargs['alpha'] = self.getInputFromPort('alpha')
        if self.hasInputFromPort('norm'):
            kwargs['norm'] = self.getInputFromPort('norm')
        # self.get_fig()
        matplotlib.pyplot.tricontour(**kwargs)        

class MplTricontourf(MplPlot):
    """:func:`~matplotlib.pyplot.tricontour` and :func:`~matplotlib.pyplot.tricontourf` draw contour lines and filled contours, respectively, on an unstructured triangular grid.  Except as noted, function signatures and return values are the same for both versions.

The triangulation can be specified in one of two ways; either:

tricontour(triangulation, ...)

where triangulation is a :class:`~matplotlib.tri.Triangulation` object, or

tricontour(x, y, ...) tricontour(x, y, triangles, ...) tricontour(x, y, triangles=triangles, ...) tricontour(x, y, mask=mask, ...) tricontour(x, y, triangles, mask=mask, ...)

in which case a Triangulation object will be created.  See :class:`~matplotlib.tri.Triangulation` for a explanation of these possibilities.

The remaining arguments may be:

tricontour(..., Z)

where Z is the array of values to contour, one per point in the triangulation.  The level values are chosen automatically.

tricontour(..., Z, N)

contour N automatically-chosen levels.

tricontour(..., Z, V)

draw contour lines at the values specified in sequence V

tricontourf(..., Z, V)

fill the (len(V)-1) regions between the values in V

tricontour(Z, **kwargs)

Use keyword args to control colors, linewidth, origin, cmap ... see below for more details.

C = tricontour(...) returns a :class:`~matplotlib.contour.TriContourSet` object.

Optional keyword arguments:

extent: [ None | (x0,x1,y0,y1) ]

If origin is not None, then extent is interpreted as in :func:`matplotlib.pyplot.imshow`: it gives the outer pixel boundaries. In this case, the position of Z[0,0] is the center of the pixel, not a corner. If origin is None, then (x0, y0) is the position of Z[0,0], and (x1, y1) is the position of Z[-1,-1].

This keyword is not active if X and Y are specified in the call to contour.

tricontour-only keyword arguments:



tricontourf-only keyword arguments:



Note: tricontourf fills intervals that are closed at the top; that is, for boundaries z1 and z2, the filled region is:

z1 < z <= z2

There is one exception: if the lowest boundary coincides with the minimum value of the z array, then that minimum value will be included in the lowest interval.

Examples:

Additional kwargs: hold = [True|False] overrides default hold state
    """
    _input_ports = [
              ("origin", "basic:String",
                {'entry_types': "['enum']", 'docstring': "If None, the first value of Z will correspond to the lower left corner, location (0,0). If 'image', the rc value for image.origin will be used.\n\nThis keyword is not active if X and Y are specified in the call to contour.", 'values': "[['upper', 'lower', 'image']]", 'optional': True}),
              ("linestyles", "basic:String",
                {'entry_types': "['enum']", 'docstring': "If linestyles is None, the 'solid' is used.\n\nlinestyles can also be an iterable of the above strings specifying a set of linestyles to be used. If this iterable is shorter than the number of contour levels it will be repeated as necessary.\n\nIf contour is using a monochrome colormap and the contour level is less than 0, then the linestyle specified in contour.negative_linestyle in matplotlibrc will be used.", 'values': "[['solid', 'dashed', 'dashdot', 'dotted']]", 'optional': True}),
              ("levelsSequence", "basic:List",
                {'optional': True, 'docstring': 'A list of floating point numbers indicating the level curves to draw; eg to draw just the zero contour pass levels=[0]'}),
              ("levelsScalar", "basic:Float",
               {'docstring': 'A list of floating point numbers indicating the level curves to draw; eg to draw just the zero contour pass levels=[0]', 'optional': True}),
              ("linewidths", "basic:String",
                {'entry_types': "['enum']", 'docstring': 'If linewidths is None, the default width in lines.linewidth in matplotlibrc is used.\n\nIf a number, all levels will be plotted with this linewidth.\n\nIf a tuple, different levels will be plotted with different linewidths in the order specified', 'values': "[['number', 'tuple of numbers']]", 'optional': True}),
              ("colors", "basic:Color",
                {'entry_types': "['enum']", 'docstring': "If None, the colormap specified by cmap will be used.\n\nIf a string, like 'r' or 'red', all levels will be plotted in this color.\n\nIf a tuple of matplotlib color args (string, float, rgb, etc), different levels will be plotted in different colors in the order specified.", 'values': "[['(mpl_colors)']]", 'optional': True}),
              ("cmap", "basic:String",
                {'entry_types': "['enum']", 'docstring': 'A cm :class:`~matplotlib.cm.Colormap` instance or None. If cmap is None and colors is None, a default Colormap is used.', 'values': "[['Colormap']]", 'optional': True}),
              ("antialiased", "basic:Boolean",
                {'optional': True, 'docstring': 'enable antialiasing'}),
              ("nchunk", "basic:Integer",
                {'entry_types': "['enum']", 'docstring': 'If 0, no subdivision of the domain. Specify a positive integer to divide the domain into subdomains of roughly nchunk by nchunk points. This may never actually be advantageous, so this option may be removed. Chunking introduces artifacts at the chunk boundaries unless antialiased is False.', 'values': '[[0]]', 'optional': True}),
              ("alpha", "basic:Float",
                {'optional': True, 'docstring': 'The alpha blending value'}),
              ("norm", "basic:String",
                {'entry_types': "['enum']", 'docstring': 'A :class:`matplotlib.colors.Normalize` instance for scaling data values to colors. If norm is None and colors is None, the default linear scaling is used.', 'values': "[['Normalize']]", 'optional': True}),
        ]

    _output_ports = [
        ("self", "(MplTricontourf)"),
        ]
    

    def compute(self):
        # get args into args, kwargs
        # write out translations
        kwargs = {}            
        if self.hasInputFromPort('origin'):
            kwargs['origin'] = self.getInputFromPort('origin')
        if self.hasInputFromPort('linestyles'):
            kwargs['linestyles'] = self.getInputFromPort('linestyles')
        if self.hasInputFromPort('levelsSequence'):
            kwargs['levels'] = self.getInputFromPort('levelsSequence')
        elif self.hasInputFromPort('levelsScalar'):
            kwargs['levels'] = self.getInputFromPort('levelsScalar')
        if self.hasInputFromPort('linewidths'):
            kwargs['linewidths'] = self.getInputFromPort('linewidths')
        if self.hasInputFromPort('colors'):
            kwargs['colors'] = self.getInputFromPort('colors')
            kwargs['colors'] = translate_color(kwargs['colors'])
        if self.hasInputFromPort('cmap'):
            kwargs['cmap'] = self.getInputFromPort('cmap')
        if self.hasInputFromPort('antialiased'):
            kwargs['antialiased'] = self.getInputFromPort('antialiased')
        if self.hasInputFromPort('nchunk'):
            kwargs['nchunk'] = self.getInputFromPort('nchunk')
        if self.hasInputFromPort('alpha'):
            kwargs['alpha'] = self.getInputFromPort('alpha')
        if self.hasInputFromPort('norm'):
            kwargs['norm'] = self.getInputFromPort('norm')
        # self.get_fig()
        matplotlib.pyplot.tricontourf(**kwargs)        

class MplTripcolor(MplPlot):
    """Create a pseudocolor plot of an unstructured triangular grid to the :class:`~matplotlib.axes.Axes`.

The triangulation can be specified in one of two ways; either:

tripcolor(triangulation, ...)

where triangulation is a :class:`~matplotlib.tri.Triangulation` object, or

tripcolor(x, y, ...) tripcolor(x, y, triangles, ...) tripcolor(x, y, triangles=triangles, ...) tripcolor(x, y, mask=mask, ...) tripcolor(x, y, triangles, mask=mask, ...)

in which case a Triangulation object will be created.  See :class:`~matplotlib.tri.Triangulation` for a explanation of these possibilities.

The next argument must be C, the array of color values, one per point in the triangulation.  The colors used for each triangle are from the mean C of the triangle's three points.

The remaining kwargs are the same as for :meth:`~matplotlib.axes.Axes.pcolor`.

Example:



Additional kwargs: hold = [True|False] overrides default hold state
    """
    _input_ports = [
        ]

    _output_ports = [
        ("self", "(MplTripcolor)"),
        ]
    

    def compute(self):
        # get args into args, kwargs
        # write out translations
        kwargs = {}            
        # self.get_fig()
        matplotlib.pyplot.tripcolor(**kwargs)        

class MplTriplot(MplPlot):
    """Draw a unstructured triangular grid as lines and/or markers to the :class:`~matplotlib.axes.Axes`.

The triangulation to plot can be specified in one of two ways; either:

triplot(triangulation, ...)

where triangulation is a :class:`~matplotlib.tri.Triangulation` object, or

triplot(x, y, ...) triplot(x, y, triangles, ...) triplot(x, y, triangles=triangles, ...) triplot(x, y, mask=mask, ...) triplot(x, y, triangles, mask=mask, ...)

in which case a Triangulation object will be created.  See :class:`~matplotlib.tri.Triangulation` for a explanation of these possibilities.

The remaining args and kwargs are the same as for :meth:`~matplotlib.axes.Axes.plot`.

Example:



Additional kwargs: hold = [True|False] overrides default hold state
    """
    _input_ports = [
        ]

    _output_ports = [
        ("self", "(MplTriplot)"),
        ]
    

    def compute(self):
        # get args into args, kwargs
        # write out translations
        kwargs = {}            
        # self.get_fig()
        matplotlib.pyplot.triplot(**kwargs)        

class MplVlines(MplPlot):
    """call signature:

vlines(x, ymin, ymax, color='k', linestyles='solid')

Plot vertical lines at each x from ymin to ymax.  ymin or ymax can be scalars or len(x) numpy arrays.  If they are scalars, then the respective values are constant, else the heights of the lines are determined by ymin and ymax.

linestyles

one of [ 'solid' | 'dashed' | 'dashdot' | 'dotted' ]

Returns the :class:`matplotlib.collections.LineCollection` that was added.

kwargs are :class:`~matplotlib.collections.LineCollection` properties:

%(LineCollection)s

Additional kwargs: hold = [True|False] overrides default hold state
    """
    _input_ports = [
              ("hold", "basic:String",
                {'optional': True}),
              ("ymax", "basic:String",
                {}),
              ("linestyles", "basic:String",
                {'optional': True, 'defaults': "['solid']"}),
              ("color", "basic:String",
                {'optional': True, 'defaults': "['k']"}),
              ("label", "basic:String",
                {'optional': True, 'defaults': "['']"}),
              ("colors", "basic:String",
                {'optional': True, 'defaults': "['k']"}),
              ("x", "basic:String",
                {}),
              ("ymin", "basic:String",
                {}),
        ]

    _output_ports = [
        ("self", "(MplVlines)"),
        ]
    

    def compute(self):
        # get args into args, kwargs
        # write out translations
        kwargs = {}            
        if self.hasInputFromPort('hold'):
            kwargs['hold'] = self.getInputFromPort('hold')
        kwargs['ymax'] = self.getInputFromPort('ymax')
        if self.hasInputFromPort('linestyles'):
            kwargs['linestyles'] = self.getInputFromPort('linestyles')
        if self.hasInputFromPort('color'):
            kwargs['color'] = self.getInputFromPort('color')
        if self.hasInputFromPort('label'):
            kwargs['label'] = self.getInputFromPort('label')
        if self.hasInputFromPort('colors'):
            kwargs['colors'] = self.getInputFromPort('colors')
        kwargs['x'] = self.getInputFromPort('x')
        kwargs['ymin'] = self.getInputFromPort('ymin')
        # self.get_fig()
        matplotlib.pyplot.vlines(**kwargs)        

class MplXcorr(MplPlot):
    """call signature:

def xcorr(self, x, y, normed=True, detrend=mlab.detrend_none,   usevlines=True, maxlags=10, **kwargs):

Plot the cross correlation between x and y.  If normed = True, normalize the data by the cross correlation at 0-th lag.  x and y are detrended by the detrend callable (default no normalization).  x and y must be equal length.

Data are plotted as plot(lags, c, **kwargs)

Return value is a tuple (lags, c, line) where:

lags are a length 2*maxlags+1 lag vector

c is the 2*maxlags+1 auto correlation vector

The default linestyle is None and the default marker is 'o', though these can be overridden with keyword args.  The cross correlation is performed with :func:`numpy.correlate` with mode = 2.

If usevlines is True:

:func:`~matplotlib.pyplot.vlines` rather than :func:`~matplotlib.pyplot.plot` is used to draw vertical lines from the origin to the xcorr.  Otherwise the plotstyle is determined by the kwargs, which are :class:`~matplotlib.lines.Line2D` properties.

The return value is a tuple (lags, c, linecol, b) where linecol is the :class:`matplotlib.collections.LineCollection` instance and b is the x-axis.

maxlags is a positive integer detailing the number of lags to show. The default value of None will return all (2*len(x)-1) lags.

Example:

:func:`~matplotlib.pyplot.xcorr` above, and :func:`~matplotlib.pyplot.acorr` below.

Example:

Additional kwargs: hold = [True|False] overrides default hold state
    """
    _input_ports = [
              ("normed", "basic:Boolean",
                {'optional': True, 'defaults': "['True']"}),
              ("usevlines", "basic:Boolean",
                {'optional': True, 'defaults': "['True']"}),
              ("detrend", "basic:String",
                {'optional': True, 'defaults': "['<function detrend_none at 0x101f3b0c8>']"}),
              ("maxlags", "basic:Integer",
                {'optional': True, 'defaults': "['10']"}),
              ("y", "basic:String",
                {}),
              ("x", "basic:String",
                {}),
              ("hold", "basic:String",
                {'optional': True}),
        ]

    _output_ports = [
        ("self", "(MplXcorr)"),
        ]
    

    def compute(self):
        # get args into args, kwargs
        # write out translations
        kwargs = {}            
        if self.hasInputFromPort('normed'):
            kwargs['normed'] = self.getInputFromPort('normed')
        if self.hasInputFromPort('usevlines'):
            kwargs['usevlines'] = self.getInputFromPort('usevlines')
        if self.hasInputFromPort('detrend'):
            kwargs['detrend'] = self.getInputFromPort('detrend')
        if self.hasInputFromPort('maxlags'):
            kwargs['maxlags'] = self.getInputFromPort('maxlags')
        kwargs['y'] = self.getInputFromPort('y')
        kwargs['x'] = self.getInputFromPort('x')
        if self.hasInputFromPort('hold'):
            kwargs['hold'] = self.getInputFromPort('hold')
        # self.get_fig()
        matplotlib.pyplot.xcorr(**kwargs)        

class MplBarbs(MplPlot):
    """%(barbs_doc)s Example:

Additional kwargs: hold = [True|False] overrides default hold state
    """
    _input_ports = [
        ]

    _output_ports = [
        ("self", "(MplBarbs)"),
        ]
    

    def compute(self):
        # get args into args, kwargs
        # write out translations
        kwargs = {}            
        # self.get_fig()
        matplotlib.pyplot.barbs(**kwargs)        

class MplSpy(MplPlot):
    """call signature:

spy(Z, precision=0, marker=None, markersize=None,     aspect='equal', **kwargs)

spy(Z) plots the sparsity pattern of the 2-D array Z.

If precision is 0, any non-zero value will be plotted; else, values of :math:`|Z| > precision` will be plotted.

For :class:`scipy.sparse.spmatrix` instances, there is a special case: if precision is 'present', any value present in the array will be plotted, even if it is identically zero.

The array will be plotted as it would be printed, with the first index (row) increasing down and the second index (column) increasing to the right.

By default aspect is 'equal', so that each array element occupies a square space; set the aspect kwarg to 'auto' to allow the plot to fill the plot box, or to any scalar number to specify the aspect ratio of an array element directly.

Two plotting styles are available: image or marker. Both are available for full arrays, but only the marker style works for :class:`scipy.sparse.spmatrix` instances.

If marker and markersize are None, an image will be returned and any remaining kwargs are passed to :func:`~matplotlib.pyplot.imshow`; else, a :class:`~matplotlib.lines.Line2D` object will be returned with the value of marker determining the marker type, and any remaining kwargs passed to the :meth:`~matplotlib.axes.Axes.plot` method.

If marker and markersize are None, useful kwargs include:

cmap

alpha

For controlling colors, e.g. cyan background and red marks, use:

cmap = mcolors.ListedColormap(['c','r'])

If marker or markersize is not None, useful kwargs include:

marker

markersize

color

Useful values for marker include:

's'  square (default)

'o'  circle

'.'  point

','  pixel

Additional kwargs: hold = [True|False] overrides default hold state
    """
    _input_ports = [
              ("hold", "basic:String",
                {'optional': True}),
              ("markersize", "basic:String",
                {'optional': True}),
              ("precision", "basic:Integer",
                {'optional': True, 'defaults': "['0']"}),
              ("aspect", "basic:String",
                {'optional': True, 'defaults': "['equal']"}),
              ("marker", "basic:String",
                {'optional': True}),
              ("Z", "basic:String",
                {}),
        ]

    _output_ports = [
        ("self", "(MplSpy)"),
        ]
    

    def compute(self):
        # get args into args, kwargs
        # write out translations
        kwargs = {}            
        if self.hasInputFromPort('hold'):
            kwargs['hold'] = self.getInputFromPort('hold')
        if self.hasInputFromPort('markersize'):
            kwargs['markersize'] = self.getInputFromPort('markersize')
        if self.hasInputFromPort('precision'):
            kwargs['precision'] = self.getInputFromPort('precision')
        if self.hasInputFromPort('aspect'):
            kwargs['aspect'] = self.getInputFromPort('aspect')
        if self.hasInputFromPort('marker'):
            kwargs['marker'] = self.getInputFromPort('marker')
        kwargs['Z'] = self.getInputFromPort('Z')
        # self.get_fig()
        matplotlib.pyplot.spy(**kwargs)        

class MplPolar(MplPlot):
    """call signature:

polar(theta, r, **kwargs)

Make a polar plot.  Multiple theta, r arguments are supported, with format strings, as in :func:`~matplotlib.pyplot.plot`.

An optional kwarg resolution sets the number of vertices to interpolate between each pair of points.  The default is 1, which disables interpolation.
    """
    _input_ports = [
              ("theta", "basic:String",
                {}),
              ("r", "basic:String",
                {}),
        ]

    _output_ports = [
        ("self", "(MplPolar)"),
        ]
    

    def compute(self):
        # get args into args, kwargs
        # write out translations
        kwargs = {}            
        kwargs['theta'] = self.getInputFromPort('theta')
        kwargs['r'] = self.getInputFromPort('r')
        # self.get_fig()
        matplotlib.pyplot.polar(**kwargs)        

class MplLegend(MplPlot):
    """call signature:

legend(*args, **kwargs)

Place a legend on the current axes at location loc.  Labels are a sequence of strings and loc can be a string or an integer specifying the legend location.

To make a legend with existing lines:

legend()

:meth:`legend` by itself will try and build a legend using the label property of the lines/patches/collections.  You can set the label of a line by doing:

plot(x, y, label='my data')

or:

line.set_label('my data').

If label is set to '_nolegend_', the item will not be shown in legend.

To automatically generate the legend from labels:

legend( ('label1', 'label2', 'label3') )

To make a legend for a list of lines and labels:

legend( (line1, line2, line3), ('label1', 'label2', 'label3') )

To make a legend at a given location, using a location argument:

legend( ('label1', 'label2', 'label3'), loc='upper left')

or:

legend( (line1, line2, line3),  ('label1', 'label2', 'label3'), loc=2)

The location codes are



Users can specify any arbitrary location for the legend using the bbox_to_anchor keyword argument. bbox_to_anchor can be an instance of BboxBase(or its derivatives) or a tuple of 2 or 4 floats. For example,

loc = 'upper right', bbox_to_anchor = (0.5, 0.5)

will place the legend so that the upper right corner of the legend at the center of the axes.

The legend location can be specified in other coordinate, by using the bbox_transform keyword.

The loc itslef can be a 2-tuple giving x,y of the lower-left corner of the legend in axes coords (bbox_to_anchor is ignored).

Keyword arguments:



Padding and spacing between various elements use following keywords parameters. These values are measure in font-size units. E.g., a fontsize of 10 points and a handlelength=5 implies a handlelength of 50 points.  Values from rcParams will be used if None.

Not all kinds of artist are supported by the legend command. See LINK (FIXME) for details.

Example:

Also see :ref:`plotting-guide-legend`.
    """
    _input_ports = [
              ("loc", "basic:String",
                {'entry_types': "['enum']", 'values': "[['best', 'upper right', 'upper left', 'lower left', 'lower right', 'right', 'center left', 'center right', 'lower center', 'upper center', 'center']]", 'optional': True}),
              ("fancybox", "basic:Boolean",
                {'optional': True, 'docstring': 'if True, draw a frame with a round fancybox.  If None, use rc'}),
              ("bbox_to_anchor", "basic:String",
                {'optional': True, 'docstring': 'the bbox that the legend will be anchored.'}),
              ("title", "basic:String",
                {'optional': True, 'docstring': 'the legend title'}),
              ("handlelength", "basic:String",
                {'optional': True, 'docstring': 'the length of the legend handles'}),
              ("markerscale", "basic:Float",
                {'optional': True, 'docstring': 'The relative size of legend markers vs. original. If None, use rc settings.'}),
              ("numpoints", "basic:Integer",
                {'optional': True, 'docstring': 'The number of points in the legend for line'}),
              ("labelspacing", "basic:String",
                {'optional': True, 'docstring': 'the vertical space between the legend entries'}),
              ("scatterpoints", "basic:Integer",
                {'optional': True, 'docstring': 'The number of points in the legend for scatter plot'}),
              ("frameon", "basic:Boolean",
                {'optional': True, 'docstring': "if True, draw a frame around the legend. The default is set by the rcParam 'legend.frameon'"}),
              ("columnspacing", "basic:String",
                {'optional': True, 'docstring': 'the spacing between columns'}),
              ("handletextpad", "basic:String",
                {'optional': True, 'docstring': 'the pad between the legend handle and text'}),
              ("scatteroffsetsSequence", "basic:List",
                {'optional': True, 'docstring': 'a list of yoffsets for scatter symbols in legend'}),
              ("scatteroffsetsScalar", "basic:Float",
               {'docstring': 'a list of yoffsets for scatter symbols in legend', 'optional': True}),
              ("mode", "basic:String",
                {'optional': True, 'docstring': 'if mode is "expand", the legend will be horizontally expanded to fill the axes area (or bbox_to_anchor)'}),
              ("ncol", "basic:Integer",
                {'optional': True, 'docstring': 'number of columns. default is 1', 'defaults': "['1']"}),
              ("shadow", "basic:Boolean",
                {'optional': True, 'docstring': 'If True, draw a shadow behind legend. If None, use rc settings.'}),
              ("prop", "basic:String",
                {'optional': True, 'docstring': 'A :class:`matplotlib.font_manager.FontProperties` instance. If prop is a dictionary, a new instance will be created with prop. If None, use rc settings.'}),
              ("borderpad", "basic:String",
                {'optional': True, 'docstring': 'the fractional whitespace inside the legend border'}),
              ("bbox_transform", "basic:String",
                {'optional': True, 'docstring': 'the transform for the bbox. transAxes if None.'}),
              ("borderaxespad", "basic:String",
                {'optional': True, 'docstring': 'the pad between the axes and legend border'}),
        ]

    _output_ports = [
        ("self", "(MplLegend)"),
        ]
    

    def compute(self):
        # get args into args, kwargs
        # write out translations
        kwargs = {}            
        if self.hasInputFromPort('loc'):
            kwargs['loc'] = self.getInputFromPort('loc')
            kwargs['loc'] = translate_MplLegend_loc(kwargs['loc'])
        if self.hasInputFromPort('fancybox'):
            kwargs['fancybox'] = self.getInputFromPort('fancybox')
        if self.hasInputFromPort('bbox_to_anchor'):
            kwargs['bbox_to_anchor'] = self.getInputFromPort('bbox_to_anchor')
        if self.hasInputFromPort('title'):
            kwargs['title'] = self.getInputFromPort('title')
        if self.hasInputFromPort('handlelength'):
            kwargs['handlelength'] = self.getInputFromPort('handlelength')
        if self.hasInputFromPort('markerscale'):
            kwargs['markerscale'] = self.getInputFromPort('markerscale')
        if self.hasInputFromPort('numpoints'):
            kwargs['numpoints'] = self.getInputFromPort('numpoints')
        if self.hasInputFromPort('labelspacing'):
            kwargs['labelspacing'] = self.getInputFromPort('labelspacing')
        if self.hasInputFromPort('scatterpoints'):
            kwargs['scatterpoints'] = self.getInputFromPort('scatterpoints')
        if self.hasInputFromPort('frameon'):
            kwargs['frameon'] = self.getInputFromPort('frameon')
        if self.hasInputFromPort('columnspacing'):
            kwargs['columnspacing'] = self.getInputFromPort('columnspacing')
        if self.hasInputFromPort('handletextpad'):
            kwargs['handletextpad'] = self.getInputFromPort('handletextpad')
        if self.hasInputFromPort('scatteroffsetsSequence'):
            kwargs['scatteroffsets'] = self.getInputFromPort('scatteroffsetsSequence')
        elif self.hasInputFromPort('scatteroffsetsScalar'):
            kwargs['scatteroffsets'] = self.getInputFromPort('scatteroffsetsScalar')
        if self.hasInputFromPort('mode'):
            kwargs['mode'] = self.getInputFromPort('mode')
        if self.hasInputFromPort('ncol'):
            kwargs['ncol'] = self.getInputFromPort('ncol')
        if self.hasInputFromPort('shadow'):
            kwargs['shadow'] = self.getInputFromPort('shadow')
        if self.hasInputFromPort('prop'):
            kwargs['prop'] = self.getInputFromPort('prop')
        if self.hasInputFromPort('borderpad'):
            kwargs['borderpad'] = self.getInputFromPort('borderpad')
        if self.hasInputFromPort('bbox_transform'):
            kwargs['bbox_transform'] = self.getInputFromPort('bbox_transform')
        if self.hasInputFromPort('borderaxespad'):
            kwargs['borderaxespad'] = self.getInputFromPort('borderaxespad')
        # self.get_fig()
        matplotlib.pyplot.legend(**kwargs)        

class MplAnnotate(MplPlot):
    """call signature:

annotate(s, xy, xytext=None, xycoords='data',          textcoords='data', arrowprops=None, **kwargs)

Keyword arguments:

Annotate the x, y point xy with text s at x, y location xytext.  (If xytext = None, defaults to xy, and if textcoords = None, defaults to xycoords).

arrowprops, if not None, is a dictionary of line properties (see :class:`matplotlib.lines.Line2D`) for the arrow that connects annotation to the point.

If the dictionary has a key arrowstyle, a FancyArrowPatch instance is created with the given dictionary and is drawn. Otherwise, a YAArow patch instance is created and drawn. Valid keys for YAArow are

Valid keys for FancyArrowPatch are

xycoords and textcoords are strings that indicate the coordinates of xy and xytext.

If a 'points' or 'pixels' option is specified, values will be added to the bottom-left and if negative, values will be subtracted from the top-right.  Eg:

# 10 points to the right of the left border of the axes and # 5 points below the top border xy=(10,-5), xycoords='axes points'

You may use an instance of :class:`~matplotlib.transforms.Transform` or :class:`~matplotlib.artist.Artist`. See :ref:`plotting-guide-annotation` for more details.

The annotation_clip attribute contols the visibility of the annotation when it goes outside the axes area. If True, the annotation will only be drawn when the xy is inside the axes. If False, the annotation will always be drawn regardless of its position.  The default is None, which behave as True only if xycoords is"data".

Additional kwargs are Text properties:

%(Text)s
    """
    _input_ports = [
              ("xycoords", "basic:String",
                {'entry_types': "['enum']", 'values': "[['figure points', 'figure pixels', 'figure fraction', 'axes points', 'axes pixels', 'axes fraction', 'data', 'offset points', 'polar']]", 'optional': True}),
              ("xytext", "basic:Float, basic:Float",
                {'optional': True}),
              ("s", "basic:String",
                {}),
              ("xy", "basic:Float, basic:Float",
                {}),
              ("textcoords", "basic:String",
                {'entry_types': "['enum']", 'values': "[['figure points', 'figure pixels', 'figure fraction', 'axes points', 'axes pixels', 'axes fraction', 'data', 'offset points', 'polar']]", 'optional': True}),
              ("fancyArrowProperties", "MplFancyArrowPatchProperties",
                {'optional': True}),
              ("arrowProperties", "MplYAArrowProperties",
                {'optional': True}),
              ("annotationProperties", "MplAnnotationProperties",
                {}),
        ]

    _output_ports = [
        ("self", "(MplAnnotate)"),
        ]
    

    def compute(self):
        # get args into args, kwargs
        # write out translations
        kwargs = {}            
        if self.hasInputFromPort('xycoords'):
            kwargs['xycoords'] = self.getInputFromPort('xycoords')
        if self.hasInputFromPort('xytext'):
            kwargs['xytext'] = self.getInputFromPort('xytext')
        kwargs['s'] = self.getInputFromPort('s')
        kwargs['xy'] = self.getInputFromPort('xy')
        if self.hasInputFromPort('textcoords'):
            kwargs['textcoords'] = self.getInputFromPort('textcoords')
        # self.get_fig()
        if self.hasInputFromPort("fancyArrowProperties"):
            kwargs['arrowprops'] = \
                self.getInputFromPort("fancyArrowProperties").props
        elif self.hasInputFromPort("arrowProperties"):
            kwargs['arrowprops'] = \
                self.getInputFromPort("arrowProperties").props
        annotation = matplotlib.pyplot.annotate(**kwargs)
        if self.hasInputFromPort('annotationProperties'):
            properties = self.getInputFromPort('annotationProperties')
            properties.update_props(annotation)

class MplLinePlot(MplPlot):
    """Plot lines and/or markers to the :class:`~matplotlib.axes.Axes`.  args is a variable length argument, allowing for multiple x, y pairs with an optional format string.  For example, each of the following is legal:

plot(x, y)         # plot x and y using default line style and color plot(x, y, 'bo')   # plot x and y using blue circle markers plot(y)            # plot y using x as index array 0..N-1 plot(y, 'r+')      # ditto, but with red plusses

If x and/or y is 2-dimensional, then the corresponding columns will be plotted.

An arbitrary number of x, y, fmt groups can be specified, as in:

a.plot(x1, y1, 'g^', x2, y2, 'g-')

Return value is a list of lines that were added.

The following format string characters are accepted to control the line style or marker:

The following color abbreviations are supported:

In addition, you can specify colors in many weird and wonderful ways, including full names ('green'), hex strings ('#008000'), RGB or RGBA tuples ((0,1,0,1)) or grayscale intensities as a string ('0.8').  Of these, the string specifications can be used in place of a fmt group, but the tuple forms can be used only as kwargs.

Line styles and colors are combined in a single format string, as in 'bo' for blue circles.

The kwargs can be used to set line properties (any property that has a set_* method).  You can use this to set a line label (for auto legends), linewidth, anitialising, marker face color, etc.  Here is an example:

plot([1,2,3], [1,2,3], 'go-', label='line 1', linewidth=2) plot([1,2,3], [1,4,9], 'rs',  label='line 2') axis([0, 4, 0, 10]) legend()

If you make multiple lines with one plot command, the kwargs apply to all those lines, e.g.:

plot(x1, y1, x2, y2, antialised=False)

Neither line will be antialiased.

You do not need to use format strings, which are just abbreviations.  All of the line properties can be controlled by keyword arguments.  For example, you can set the color, marker, linestyle, and markercolor with:

plot(x, y, color='green', linestyle='dashed', marker='o',      markerfacecolor='blue', markersize=12).  See      :class:`~matplotlib.lines.Line2D` for details.

The kwargs are :class:`~matplotlib.lines.Line2D` properties:

%(Line2D)s

kwargs scalex and scaley, if defined, are passed on to :meth:`~matplotlib.axes.Axes.autoscale_view` to determine whether the x and y axes are autoscaled; the default is True.

Additional kwargs: hold = [True|False] overrides default hold state
    """
    _input_ports = [
              ("marker", "basic:String",
                {'entry_types': "['enum']", 'values': "[['solid line style', 'dashed line style', 'dash-dot line style', 'dotted line style', 'point marker', 'pixel marker', 'circle marker', 'triangle_down marker', 'triangle_up marker', 'triangle_left marker', 'triangle_right marker', 'tri_down marker', 'tri_up marker', 'tri_left marker', 'tri_right marker', 'square marker', 'pentagon marker', 'star marker', 'hexagon1 marker', 'hexagon2 marker', 'plus marker', 'x marker', 'diamond marker', 'thin_diamond marker', 'vline marker', 'hline marker']]", 'optional': True}),
              ("y", "basic:List",
                {}),
              ("x", "basic:List",
                {}),
              ("lineProperties", "MplLine2DProperties",
                {}),
        ]

    _output_ports = [
        ("self", "(MplLinePlot)"),
        ]
    

    def compute(self):
        # get args into args, kwargs
        # write out translations
        kwargs = {}            
        if self.hasInputFromPort('marker'):
            kwargs['marker'] = self.getInputFromPort('marker')
            kwargs['marker'] = translate_MplLinePlot_marker(kwargs['marker'])
        kwargs['y'] = self.getInputFromPort('y')
        kwargs['x'] = self.getInputFromPort('x')
        # self.get_fig()
        x = kwargs["x"]
        y = kwargs["y"]
        del kwargs["x"]
        del kwargs["y"]
        lines = matplotlib.pyplot.plot(x, y, **kwargs)
        if self.hasInputFromPort('lineProperties'):
            properties = self.getInputFromPort('lineProperties')
            properties.update_props(lines)

          
_modules = [
            MplAcorr,
            MplArrow,
            MplAxhline,
            MplAxhspan,
            MplAxvline,
            MplAxvspan,
            MplBar,
            MplBarh,
            MplBroken_barh,
            MplBoxplot,
            MplCohere,
            MplClabel,
            MplContour,
            MplContourf,
            MplCsd,
            MplErrorbar,
            MplFill,
            MplFill_between,
            MplFill_betweenx,
            MplHexbin,
            MplHist,
            MplHist2d,
            MplHlines,
            MplImshow,
            MplLoglog,
            MplPcolor,
            MplPcolormesh,
            MplPie,
            MplPlot_date,
            MplPsd,
            MplQuiver,
            MplQuiverkey,
            MplScatter,
            MplSemilogx,
            MplSemilogy,
            MplSpecgram,
            MplStackplot,
            MplStem,
            MplStep,
            MplStreamplot,
            MplTricontour,
            MplTricontourf,
            MplTripcolor,
            MplTriplot,
            MplVlines,
            MplXcorr,
            MplBarbs,
            MplSpy,
            MplPolar,
            MplLegend,
            MplAnnotate,
            MplLinePlot,
]
