from vistrails.core.modules.vistrails_module import Module
from bases import MplProperties
import matplotlib.artist
import matplotlib.cbook






def translate_color(c):
    return c.tuple

def translate_MplLine2DProperties_marker(val):
    translate_dict = {'caretright': 5, 'star': '*', 'point': '.', 'mathtext': '$...$', 'triangle_right': '>', 'tickup': 2, 'hexagon1': 'h', 'plus': '+', 'hline': '_', 'vline': '|', 'tickdown': 3, 'nothing': ' ', 'caretleft': 4, 'pentagon': 'p', 'tri_left': '3', 'tickleft': 0, 'tickright': 1, 'tri_down': '1', 'thin_diamond': 'd', 'caretup': 6, 'diamond': 'D', 'caretdown': 7, 'hexagon2': 'H', 'tri_up': '2', 'square': 's', 'x': 'x', 'triangle_down': 'v', 'triangle_up': '^', 'octagon': '8', 'tri_right': '4', 'circle': 'o', 'pixel': ',', 'triangle_left': '<'}
    return translate_dict[val]
def translate_MplLine2DProperties_linestyle(val):
    translate_dict = {'solid': '-', 'dashed': '--', 'dash_dot': '-.', 'dotted': ':', 'draw nothing': ''}
    return translate_dict[val]
def translate_MplAxesProperties_anchor(val):
    translate_dict = {'right': 'E', 'Center': 'C', 'bottom right': 'SE', 'top right': 'NE', 'bottom': 'S', 'top left': 'NW', 'top': 'N', 'bottom left': 'SW', 'left': 'W'}
    return translate_dict[val]

class MplArtistProperties(MplProperties):
    """
    Abstract base class for someone who renders into a
    :class:`FigureCanvas`.
    
    """
    _input_ports = [
              ("picker", "basic:String",
                {'optional': True, 'docstring': "Set the epsilon for picking used by this artist\n\npicker can be one of the following:\n\nNone: picking is disabled for this artist (default)\n\nA boolean: if True then picking will be enabled and the artist will fire a pick event if the mouse event is over the artist\n\nA float: if picker is a number it is interpreted as an epsilon tolerance in points and the artist will fire off an event if it's data is within epsilon of the mouse event.  For some artists like lines and patch collections, the artist may provide additional data to the pick event that is generated, e.g. the indices of the data within epsilon of the pick event\n\nA function: if picker is callable, it is a user supplied function which determines whether the artist is hit by the mouse event:\n\nhit, props = picker(artist, mouseevent)\n\nto determine the hit test.  if the mouse event is over the artist, return hit=True and props is a dictionary of properties you want added to the PickEvent attributes."}),
              ("contains", "basic:String",
                {'optional': True, 'docstring': 'Replace the contains test used by this artist. The new picker should be a callable function which determines whether the artist is hit by the mouse event:\n\nhit, props = picker(artist, mouseevent)\n\nIf the mouse event is over the artist, return hit = True and props is a dictionary of properties you want returned with the contains test.'}),
              ("clip_on", "basic:Boolean",
                {'optional': True, 'docstring': 'Set whether artist uses clipping.'}),
              ("agg_filter", "basic:String",
                {'optional': True, 'docstring': 'set agg_filter fuction.'}),
              ("visible", "basic:Boolean",
                {'optional': True, 'docstring': "Set the artist's visiblity."}),
              ("url", "basic:String",
                {'optional': True, 'docstring': 'Sets the url for the artist'}),
              ("transform", "basic:String",
                {'optional': True, 'docstring': 'Set the :class:`~matplotlib.transforms.Transform` instance used by this artist.'}),
              ("axes", "basic:String",
                {'optional': True, 'docstring': 'Set the :class:`~matplotlib.axes.Axes` instance in which the artist resides, if any.'}),
              ("clip_box", "basic:String",
                {'optional': True, 'docstring': "Set the artist's clip :class:`~matplotlib.transforms.Bbox`."}),
              ("clip_path", "basic:String",
                {'optional': True, 'docstring': "Set the artist's clip path, which may be:\n\na :class:`~matplotlib.patches.Patch` (or subclass) instance\n\n\n\nNone, to remove the clipping path\n\nFor efficiency, if the path happens to be an axis-aligned rectangle, this method will set the clipping box to the corresponding rectangle and set the clipping path to None."}),
              ("lod", "basic:Boolean",
                {'optional': True, 'docstring': 'Set Level of Detail on or off.  If on, the artists may examine things like the pixel width of the axes and draw a subset of their contents accordingly'}),
              ("label", "basic:String",
                {'optional': True, 'docstring': 'Set the label to s for auto legend.'}),
              ("rasterized", "basic:Boolean",
                {'optional': True, 'docstring': "Force rasterized (bitmap) drawing in vector backend output.\n\nDefaults to None, which implies the backend's default behavior"}),
              ("gid", "basic:String",
                {'optional': True, 'docstring': 'Sets the (group) id for the artist'}),
              ("zorder", "basic:String",
                {'optional': True, 'docstring': 'Set the zorder for the artist.  Artists with lower zorder values are drawn first.'}),
              ("snap", "basic:String",
                {'optional': True, 'docstring': 'Sets the snap setting which may be:\n\nTrue: snap vertices to the nearest pixel center\n\nFalse: leave vertices as-is\n\nNone: (auto) If the path contains only rectilinear line segments, round to the nearest pixel center\n\nOnly supported by the Agg and MacOSX backends.'}),
              ("alpha", "basic:Float",
                {'optional': True, 'docstring': 'Set the alpha value used for blending - not supported on all backends.'}),
              ("animated", "basic:Boolean",
                {'optional': True, 'docstring': "Set the artist's animation state."}),
              ("figure", "basic:String",
                {'optional': True, 'docstring': 'Set the :class:`~matplotlib.figure.Figure` instance the artist belongs to.'}),
        ]

    # no output ports except self
    _output_ports = [("self", "(MplArtistProperties)")]

    def __init__(self):
        MplProperties.__init__(self)
        self.props = {}
        self.constructor_props = {}
        self.sub_props = {}

    def compute(self):
        MplProperties.compute(self)
        if self.hasInputFromPort('picker'):
            self.props['picker'] = self.getInputFromPort('picker')
        if self.hasInputFromPort('contains'):
            self.props['contains'] = self.getInputFromPort('contains')
        if self.hasInputFromPort('clip_on'):
            self.props['clip_on'] = self.getInputFromPort('clip_on')
        if self.hasInputFromPort('agg_filter'):
            self.props['agg_filter'] = self.getInputFromPort('agg_filter')
        if self.hasInputFromPort('visible'):
            self.props['visible'] = self.getInputFromPort('visible')
        if self.hasInputFromPort('url'):
            self.props['url'] = self.getInputFromPort('url')
        if self.hasInputFromPort('transform'):
            self.props['transform'] = self.getInputFromPort('transform')
        if self.hasInputFromPort('axes'):
            self.props['axes'] = self.getInputFromPort('axes')
        if self.hasInputFromPort('clip_box'):
            self.props['clip_box'] = self.getInputFromPort('clip_box')
        if self.hasInputFromPort('clip_path'):
            self.props['clip_path'] = self.getInputFromPort('clip_path')
        if self.hasInputFromPort('lod'):
            self.props['lod'] = self.getInputFromPort('lod')
        if self.hasInputFromPort('label'):
            self.props['label'] = self.getInputFromPort('label')
        if self.hasInputFromPort('rasterized'):
            self.props['rasterized'] = self.getInputFromPort('rasterized')
        if self.hasInputFromPort('gid'):
            self.props['gid'] = self.getInputFromPort('gid')
        if self.hasInputFromPort('zorder'):
            self.props['zorder'] = self.getInputFromPort('zorder')
        if self.hasInputFromPort('snap'):
            self.props['snap'] = self.getInputFromPort('snap')
        if self.hasInputFromPort('alpha'):
            self.props['alpha'] = self.getInputFromPort('alpha')
        if self.hasInputFromPort('animated'):
            self.props['animated'] = self.getInputFromPort('animated')
        if self.hasInputFromPort('figure'):
            self.props['figure'] = self.getInputFromPort('figure')

        
    def update_props(self, objs):
        matplotlib.artist.setp(objs, **self.props)

    def update_kwargs(self, kwargs):
        kwargs.update(self.constructor_props)
        kwargs.update(self.props)

class MplCollectionProperties(MplArtistProperties):
    """
    Base class for Collections.  Must be subclassed to be usable.

    All properties in a collection must be sequences or scalars;
    if scalars, they will be converted to sequences.  The
    property of the ith element of the collection is::

      prop[i % len(props)]

    Keyword arguments and default values:

        * *edgecolors*: None
        * *facecolors*: None
        * *linewidths*: None
        * *antialiaseds*: None
        * *offsets*: None
        * *transOffset*: transforms.IdentityTransform()
        * *norm*: None (optional for
          :class:`matplotlib.cm.ScalarMappable`)
        * *cmap*: None (optional for
          :class:`matplotlib.cm.ScalarMappable`)

    *offsets* and *transOffset* are used to translate the patch after
    rendering (default no offsets).

    If any of *edgecolors*, *facecolors*, *linewidths*, *antialiaseds*
    are None, they default to their :data:`matplotlib.rcParams` patch
    setting, in sequence form.

    The use of :class:`~matplotlib.cm.ScalarMappable` is optional.  If
    the :class:`~matplotlib.cm.ScalarMappable` matrix _A is not None
    (ie a call to set_array has been made), at draw time a call to
    scalar mappable will be made to set the face colors.
    
    """
    _input_ports = [
              ("transOffset", "basic:String",
                {'optional': True}),
              ("edgecolor", "basic:List",
                {'optional': True, 'docstring': "Set the edgecolor(s) of the collection. c can be a matplotlib color arg (all patches have same color), or a sequence of rgba tuples; if it is a sequence the patches will cycle through the sequence.\n\nIf c is 'face', the edge color will always be the same as the face color.  If it is 'none', the patch boundary will not be drawn."}),
              ("antialiaseds", "basic:String",
                {'optional': True}),
              ("edgecolors", "basic:String",
                {'optional': True}),
              ("facecolor", "basic:List",
                {'optional': True, 'docstring': "Set the facecolor(s) of the collection.  c can be a matplotlib color arg (all patches have same color), or a sequence of rgba tuples; if it is a sequence the patches will cycle through the sequence.\n\nIf c is 'none', the patch will not be filled."}),
              ("linestyles", "basic:String",
                {'optional': True, 'defaults': "['solid']"}),
              ("offsetsSequence", "basic:List",
                {'optional': True, 'docstring': 'Set the offsets for the collection.  offsets can be a scalar or a sequence.'}),
              ("offsetsScalar", "basic:Float",
               {'docstring': 'Set the offsets for the collection.  offsets can be a scalar or a sequence.', 'optional': True}),
              ("color", "basic:List",
                {'optional': True, 'docstring': 'Set both the edgecolor and the facecolor. .. seealso:\n\n:meth:`set_facecolor`, :meth:`set_edgecolor`    For setting the edge or face color individually.'}),
              ("linewidths", "basic:String",
                {'optional': True}),
              ("cmap", "basic:String",
                {'optional': True}),
              ("antialiasedSequence", "basic:List",
                {'optional': True, 'docstring': 'Set the antialiasing state for rendering.'}),
              ("antialiasedScalar", "basic:Boolean",
               {'docstring': 'Set the antialiasing state for rendering.', 'optional': True}),
              ("urls", "basic:String",
                {'optional': True}),
              ("pickradius", "basic:String",
                {'optional': True}),
              ("alpha", "basic:Float",
                {'optional': True, 'docstring': 'Set the alpha tranparencies of the collection.  alpha must be a float or None.'}),
              ("paths", "basic:String",
                {'optional': True}),
              ("linewidthSequence", "basic:List",
                {'optional': True, 'docstring': 'Set the linewidth(s) for the collection.  lw can be a scalar or a sequence; if it is a sequence the patches will cycle through the sequence'}),
              ("linewidthScalar", "basic:Float",
               {'docstring': 'Set the linewidth(s) for the collection.  lw can be a scalar or a sequence; if it is a sequence the patches will cycle through the sequence', 'optional': True}),
              ("linestyle", "basic:String",
                {'entry_types': "['enum']", 'docstring': 'Set the linestyle(s) for the collection.', 'values': "[['solid', ('dashed', 'dashdot', 'dotted'), '(offset, on-off-dash-seq)']]", 'optional': True}),
              ("facecolors", "basic:String",
                {'optional': True}),
              ("norm", "basic:String",
                {'optional': True}),
        ]

    # no output ports except self
    _output_ports = [("self", "(MplCollectionProperties)")]

    def __init__(self):
        MplArtistProperties.__init__(self)
        self.props = {}
        self.constructor_props = {}
        self.sub_props = {}

    def compute(self):
        MplArtistProperties.compute(self)
        if self.hasInputFromPort('transOffset'):
            self.constructor_props['transOffset'] = self.getInputFromPort('transOffset')
        if self.hasInputFromPort('edgecolor'):
            self.props['edgecolor'] = self.getInputFromPort('edgecolor')
        if self.hasInputFromPort('antialiaseds'):
            self.constructor_props['antialiaseds'] = self.getInputFromPort('antialiaseds')
        if self.hasInputFromPort('edgecolors'):
            self.constructor_props['edgecolors'] = self.getInputFromPort('edgecolors')
        if self.hasInputFromPort('facecolor'):
            self.props['facecolor'] = self.getInputFromPort('facecolor')
        if self.hasInputFromPort('linestyles'):
            self.constructor_props['linestyles'] = self.getInputFromPort('linestyles')
        if self.hasInputFromPort('offsetsSequence'):
            self.props['offsets'] = self.getInputFromPort('offsetsSequence')
        elif self.hasInputFromPort('offsetsScalar'):
            self.props['offsets'] = self.getInputFromPort('offsetsScalar')
        if self.hasInputFromPort('color'):
            self.props['color'] = self.getInputFromPort('color')
        if self.hasInputFromPort('linewidths'):
            self.constructor_props['linewidths'] = self.getInputFromPort('linewidths')
        if self.hasInputFromPort('cmap'):
            self.constructor_props['cmap'] = self.getInputFromPort('cmap')
        if self.hasInputFromPort('antialiasedSequence'):
            self.props['antialiased'] = self.getInputFromPort('antialiasedSequence')
        elif self.hasInputFromPort('antialiasedScalar'):
            self.props['antialiased'] = self.getInputFromPort('antialiasedScalar')
        if self.hasInputFromPort('urls'):
            self.props['urls'] = self.getInputFromPort('urls')
        if self.hasInputFromPort('pickradius'):
            self.props['pickradius'] = self.getInputFromPort('pickradius')
        if self.hasInputFromPort('alpha'):
            self.props['alpha'] = self.getInputFromPort('alpha')
        if self.hasInputFromPort('paths'):
            self.props['paths'] = self.getInputFromPort('paths')
        if self.hasInputFromPort('linewidthSequence'):
            self.props['linewidth'] = self.getInputFromPort('linewidthSequence')
        elif self.hasInputFromPort('linewidthScalar'):
            self.props['linewidth'] = self.getInputFromPort('linewidthScalar')
        if self.hasInputFromPort('linestyle'):
            self.props['linestyle'] = self.getInputFromPort('linestyle')
        if self.hasInputFromPort('facecolors'):
            self.constructor_props['facecolors'] = self.getInputFromPort('facecolors')
        if self.hasInputFromPort('norm'):
            self.constructor_props['norm'] = self.getInputFromPort('norm')

        
    def update_props(self, objs):
        matplotlib.artist.setp(objs, **self.props)

    def update_kwargs(self, kwargs):
        kwargs.update(self.constructor_props)
        kwargs.update(self.props)

class MplPathCollectionProperties(MplCollectionProperties):
    """
    This is the most basic :class:`Collection` subclass.
    
    """
    _input_ports = [
              ("paths", "basic:String",
                {'optional': True}),
              ("sizes", "basic:String",
                {'optional': True}),
        ]

    # no output ports except self
    _output_ports = [("self", "(MplPathCollectionProperties)")]

    def __init__(self):
        MplCollectionProperties.__init__(self)
        self.props = {}
        self.constructor_props = {}
        self.sub_props = {}

    def compute(self):
        MplCollectionProperties.compute(self)
        if self.hasInputFromPort('paths'):
            self.props['paths'] = self.getInputFromPort('paths')
        if self.hasInputFromPort('sizes'):
            self.constructor_props['sizes'] = self.getInputFromPort('sizes')

        
    def update_props(self, objs):
        matplotlib.artist.setp(objs, **self.props)

    def update_kwargs(self, kwargs):
        kwargs.update(self.constructor_props)
        kwargs.update(self.props)

class MplPolyCollectionProperties(MplCollectionProperties):
    """None
    """
    _input_ports = [
              ("paths", "basic:String",
                {'optional': True, 'docstring': 'This allows one to delay initialization of the vertices.'}),
              ("verts", "basic:String",
                {'optional': True, 'docstring': 'This allows one to delay initialization of the vertices.'}),
              ("closed", "basic:Boolean",
                {'optional': True, 'defaults': "['True']"}),
              ("sizes", "basic:String",
                {'optional': True}),
        ]

    # no output ports except self
    _output_ports = [("self", "(MplPolyCollectionProperties)")]

    def __init__(self):
        MplCollectionProperties.__init__(self)
        self.props = {}
        self.constructor_props = {}
        self.sub_props = {}

    def compute(self):
        MplCollectionProperties.compute(self)
        if self.hasInputFromPort('paths'):
            self.props['paths'] = self.getInputFromPort('paths')
        if self.hasInputFromPort('verts'):
            self.props['verts'] = self.getInputFromPort('verts')
        if self.hasInputFromPort('closed'):
            self.constructor_props['closed'] = self.getInputFromPort('closed')
        if self.hasInputFromPort('sizes'):
            self.constructor_props['sizes'] = self.getInputFromPort('sizes')

        
    def update_props(self, objs):
        matplotlib.artist.setp(objs, **self.props)

    def update_kwargs(self, kwargs):
        kwargs.update(self.constructor_props)
        kwargs.update(self.props)

class MplBrokenBarHCollectionProperties(MplPolyCollectionProperties):
    """
    A collection of horizontal bars spanning *yrange* with a sequence of
    *xranges*.
    
    """
    _input_ports = [
              ("xranges", "basic:String",
                {'optional': True}),
              ("yrange", "basic:String",
                {'optional': True}),
        ]

    # no output ports except self
    _output_ports = [("self", "(MplBrokenBarHCollectionProperties)")]

    def __init__(self):
        MplPolyCollectionProperties.__init__(self)
        self.props = {}
        self.constructor_props = {}
        self.sub_props = {}

    def compute(self):
        MplPolyCollectionProperties.compute(self)
        if self.hasInputFromPort('xranges'):
            self.constructor_props['xranges'] = self.getInputFromPort('xranges')
        if self.hasInputFromPort('yrange'):
            self.constructor_props['yrange'] = self.getInputFromPort('yrange')

        
    def update_props(self, objs):
        matplotlib.artist.setp(objs, **self.props)

    def update_kwargs(self, kwargs):
        kwargs.update(self.constructor_props)
        kwargs.update(self.props)

class MplRegularPolyCollectionProperties(MplCollectionProperties):
    """Draw a collection of regular polygons with *numsides*.
    """
    _input_ports = [
              ("numsides", "basic:String",
                {'optional': True}),
              ("rotation", "basic:Integer",
                {'optional': True, 'defaults': "['0']"}),
              ("sizes", "basic:String",
                {'optional': True, 'defaults': "['(1,)']"}),
        ]

    # no output ports except self
    _output_ports = [("self", "(MplRegularPolyCollectionProperties)")]

    def __init__(self):
        MplCollectionProperties.__init__(self)
        self.props = {}
        self.constructor_props = {}
        self.sub_props = {}

    def compute(self):
        MplCollectionProperties.compute(self)
        if self.hasInputFromPort('numsides'):
            self.constructor_props['numsides'] = self.getInputFromPort('numsides')
        if self.hasInputFromPort('rotation'):
            self.constructor_props['rotation'] = self.getInputFromPort('rotation')
        if self.hasInputFromPort('sizes'):
            self.constructor_props['sizes'] = self.getInputFromPort('sizes')

        
    def update_props(self, objs):
        matplotlib.artist.setp(objs, **self.props)

    def update_kwargs(self, kwargs):
        kwargs.update(self.constructor_props)
        kwargs.update(self.props)

class MplStarPolygonCollectionProperties(MplRegularPolyCollectionProperties):
    """
    Draw a collection of regular stars with *numsides* points.
    """
    _input_ports = [
              ("numsides", "basic:String",
                {'optional': True}),
              ("rotation", "basic:Integer",
                {'optional': True, 'defaults': "['0']"}),
              ("sizes", "basic:String",
                {'optional': True, 'defaults': "['(1,)']"}),
        ]

    # no output ports except self
    _output_ports = [("self", "(MplStarPolygonCollectionProperties)")]

    def __init__(self):
        MplRegularPolyCollectionProperties.__init__(self)
        self.props = {}
        self.constructor_props = {}
        self.sub_props = {}

    def compute(self):
        MplRegularPolyCollectionProperties.compute(self)
        if self.hasInputFromPort('numsides'):
            self.constructor_props['numsides'] = self.getInputFromPort('numsides')
        if self.hasInputFromPort('rotation'):
            self.constructor_props['rotation'] = self.getInputFromPort('rotation')
        if self.hasInputFromPort('sizes'):
            self.constructor_props['sizes'] = self.getInputFromPort('sizes')

        
    def update_props(self, objs):
        matplotlib.artist.setp(objs, **self.props)

    def update_kwargs(self, kwargs):
        kwargs.update(self.constructor_props)
        kwargs.update(self.props)

class MplAsteriskPolygonCollectionProperties(MplRegularPolyCollectionProperties):
    """
    Draw a collection of regular asterisks with *numsides* points.
    """
    _input_ports = [
              ("numsides", "basic:String",
                {'optional': True}),
              ("rotation", "basic:Integer",
                {'optional': True, 'defaults': "['0']"}),
              ("sizes", "basic:String",
                {'optional': True, 'defaults': "['(1,)']"}),
        ]

    # no output ports except self
    _output_ports = [("self", "(MplAsteriskPolygonCollectionProperties)")]

    def __init__(self):
        MplRegularPolyCollectionProperties.__init__(self)
        self.props = {}
        self.constructor_props = {}
        self.sub_props = {}

    def compute(self):
        MplRegularPolyCollectionProperties.compute(self)
        if self.hasInputFromPort('numsides'):
            self.constructor_props['numsides'] = self.getInputFromPort('numsides')
        if self.hasInputFromPort('rotation'):
            self.constructor_props['rotation'] = self.getInputFromPort('rotation')
        if self.hasInputFromPort('sizes'):
            self.constructor_props['sizes'] = self.getInputFromPort('sizes')

        
    def update_props(self, objs):
        matplotlib.artist.setp(objs, **self.props)

    def update_kwargs(self, kwargs):
        kwargs.update(self.constructor_props)
        kwargs.update(self.props)

class MplLineCollectionProperties(MplCollectionProperties):
    """
    All parameters must be sequences or scalars; if scalars, they will
    be converted to sequences.  The property of the ith line
    segment is::

       prop[i % len(props)]

    i.e., the properties cycle if the ``len`` of props is less than the
    number of segments.
    
    """
    _input_ports = [
              ("paths", "basic:String",
                {'optional': True}),
              ("antialiaseds", "basic:String",
                {'optional': True}),
              ("linestyles", "basic:String",
                {'optional': True, 'defaults': "['solid']"}),
              ("offsets", "basic:String",
                {'optional': True}),
              ("color", "basic:List",
                {'optional': True, 'docstring': 'Set the color(s) of the line collection.  c can be a matplotlib color arg (all patches have same color), or a sequence or rgba tuples; if it is a sequence the patches will cycle through the sequence.'}),
              ("segments", "basic:String",
                {'optional': True}),
              ("linewidths", "basic:String",
                {'optional': True}),
              ("colors", "basic:String",
                {'optional': True}),
              ("cmap", "basic:String",
                {'optional': True}),
              ("transOffset", "basic:String",
                {'optional': True}),
              ("verts", "basic:String",
                {'optional': True}),
              ("pickradius", "basic:Integer",
                {'optional': True, 'defaults': "['5']"}),
              ("norm", "basic:String",
                {'optional': True}),
        ]

    # no output ports except self
    _output_ports = [("self", "(MplLineCollectionProperties)")]

    def __init__(self):
        MplCollectionProperties.__init__(self)
        self.props = {}
        self.constructor_props = {}
        self.sub_props = {}

    def compute(self):
        MplCollectionProperties.compute(self)
        if self.hasInputFromPort('paths'):
            self.props['paths'] = self.getInputFromPort('paths')
        if self.hasInputFromPort('antialiaseds'):
            self.constructor_props['antialiaseds'] = self.getInputFromPort('antialiaseds')
        if self.hasInputFromPort('linestyles'):
            self.constructor_props['linestyles'] = self.getInputFromPort('linestyles')
        if self.hasInputFromPort('offsets'):
            self.constructor_props['offsets'] = self.getInputFromPort('offsets')
        if self.hasInputFromPort('color'):
            self.props['color'] = self.getInputFromPort('color')
        if self.hasInputFromPort('segments'):
            self.props['segments'] = self.getInputFromPort('segments')
        if self.hasInputFromPort('linewidths'):
            self.constructor_props['linewidths'] = self.getInputFromPort('linewidths')
        if self.hasInputFromPort('colors'):
            self.constructor_props['colors'] = self.getInputFromPort('colors')
        if self.hasInputFromPort('cmap'):
            self.constructor_props['cmap'] = self.getInputFromPort('cmap')
        if self.hasInputFromPort('transOffset'):
            self.constructor_props['transOffset'] = self.getInputFromPort('transOffset')
        if self.hasInputFromPort('verts'):
            self.props['verts'] = self.getInputFromPort('verts')
        if self.hasInputFromPort('pickradius'):
            self.constructor_props['pickradius'] = self.getInputFromPort('pickradius')
        if self.hasInputFromPort('norm'):
            self.constructor_props['norm'] = self.getInputFromPort('norm')

        
    def update_props(self, objs):
        matplotlib.artist.setp(objs, **self.props)

    def update_kwargs(self, kwargs):
        kwargs.update(self.constructor_props)
        kwargs.update(self.props)

class MplCircleCollectionProperties(MplCollectionProperties):
    """
    A collection of circles, drawn using splines.
    
    """
    _input_ports = [
              ("sizes", "basic:String",
                {'optional': True}),
        ]

    # no output ports except self
    _output_ports = [("self", "(MplCircleCollectionProperties)")]

    def __init__(self):
        MplCollectionProperties.__init__(self)
        self.props = {}
        self.constructor_props = {}
        self.sub_props = {}

    def compute(self):
        MplCollectionProperties.compute(self)
        if self.hasInputFromPort('sizes'):
            self.constructor_props['sizes'] = self.getInputFromPort('sizes')

        
    def update_props(self, objs):
        matplotlib.artist.setp(objs, **self.props)

    def update_kwargs(self, kwargs):
        kwargs.update(self.constructor_props)
        kwargs.update(self.props)

class MplEllipseCollectionProperties(MplCollectionProperties):
    """
    A collection of ellipses, drawn using splines.
    
    """
    _input_ports = [
              ("units", "basic:String",
                {'optional': True, 'defaults': "['points']"}),
              ("widths", "basic:String",
                {'optional': True}),
              ("angles", "basic:String",
                {'optional': True}),
              ("heights", "basic:String",
                {'optional': True}),
        ]

    # no output ports except self
    _output_ports = [("self", "(MplEllipseCollectionProperties)")]

    def __init__(self):
        MplCollectionProperties.__init__(self)
        self.props = {}
        self.constructor_props = {}
        self.sub_props = {}

    def compute(self):
        MplCollectionProperties.compute(self)
        if self.hasInputFromPort('units'):
            self.constructor_props['units'] = self.getInputFromPort('units')
        if self.hasInputFromPort('widths'):
            self.constructor_props['widths'] = self.getInputFromPort('widths')
        if self.hasInputFromPort('angles'):
            self.constructor_props['angles'] = self.getInputFromPort('angles')
        if self.hasInputFromPort('heights'):
            self.constructor_props['heights'] = self.getInputFromPort('heights')

        
    def update_props(self, objs):
        matplotlib.artist.setp(objs, **self.props)

    def update_kwargs(self, kwargs):
        kwargs.update(self.constructor_props)
        kwargs.update(self.props)

class MplPatchCollectionProperties(MplCollectionProperties):
    """
    A generic collection of patches.

    This makes it easier to assign a color map to a heterogeneous
    collection of patches.

    This also may improve plotting speed, since PatchCollection will
    draw faster than a large number of patches.
    
    """
    _input_ports = [
              ("paths", "basic:String",
                {'optional': True}),
              ("patches", "basic:String",
                {'optional': True}),
              ("match_original", "basic:Boolean",
                {'optional': True, 'defaults': "['False']"}),
        ]

    # no output ports except self
    _output_ports = [("self", "(MplPatchCollectionProperties)")]

    def __init__(self):
        MplCollectionProperties.__init__(self)
        self.props = {}
        self.constructor_props = {}
        self.sub_props = {}

    def compute(self):
        MplCollectionProperties.compute(self)
        if self.hasInputFromPort('paths'):
            self.props['paths'] = self.getInputFromPort('paths')
        if self.hasInputFromPort('patches'):
            self.constructor_props['patches'] = self.getInputFromPort('patches')
        if self.hasInputFromPort('match_original'):
            self.constructor_props['match_original'] = self.getInputFromPort('match_original')

        
    def update_props(self, objs):
        matplotlib.artist.setp(objs, **self.props)

    def update_kwargs(self, kwargs):
        kwargs.update(self.constructor_props)
        kwargs.update(self.props)

class MplQuadMeshProperties(MplCollectionProperties):
    """
    Class for the efficient drawing of a quadrilateral mesh.

    A quadrilateral mesh consists of a grid of vertices. The
    dimensions of this array are (*meshWidth* + 1, *meshHeight* +
    1). Each vertex in the mesh has a different set of "mesh
    coordinates" representing its position in the topology of the
    mesh. For any values (*m*, *n*) such that 0 <= *m* <= *meshWidth*
    and 0 <= *n* <= *meshHeight*, the vertices at mesh coordinates
    (*m*, *n*), (*m*, *n* + 1), (*m* + 1, *n* + 1), and (*m* + 1, *n*)
    form one of the quadrilaterals in the mesh. There are thus
    (*meshWidth* * *meshHeight*) quadrilaterals in the mesh.  The mesh
    need not be regular and the polygons need not be convex.

    A quadrilateral mesh is represented by a (2 x ((*meshWidth* + 1) *
    (*meshHeight* + 1))) numpy array *coordinates*, where each row is
    the *x* and *y* coordinates of one of the vertices.  To define the
    function that maps from a data point to its corresponding color,
    use the :meth:`set_cmap` method.  Each of these arrays is indexed in
    row-major order by the mesh coordinates of the vertex (or the mesh
    coordinates of the lower left vertex, in the case of the
    colors).

    For example, the first entry in *coordinates* is the
    coordinates of the vertex at mesh coordinates (0, 0), then the one
    at (0, 1), then at (0, 2) .. (0, meshWidth), (1, 0), (1, 1), and
    so on.

    *shading* may be 'flat', 'faceted' or 'gouraud'
    
    """
    _input_ports = [
              ("paths", "basic:String",
                {'optional': True}),
              ("meshHeight", "basic:String",
                {'optional': True}),
              ("showedges", "basic:String",
                {'optional': True}),
              ("coordinates", "basic:String",
                {'optional': True}),
              ("antialiased", "basic:Boolean",
                {'optional': True, 'defaults': "['True']"}),
              ("shading", "basic:String",
                {'optional': True, 'defaults': "['flat']"}),
              ("meshWidth", "basic:String",
                {'optional': True}),
        ]

    # no output ports except self
    _output_ports = [("self", "(MplQuadMeshProperties)")]

    def __init__(self):
        MplCollectionProperties.__init__(self)
        self.props = {}
        self.constructor_props = {}
        self.sub_props = {}

    def compute(self):
        MplCollectionProperties.compute(self)
        if self.hasInputFromPort('paths'):
            self.props['paths'] = self.getInputFromPort('paths')
        if self.hasInputFromPort('meshHeight'):
            self.constructor_props['meshHeight'] = self.getInputFromPort('meshHeight')
        if self.hasInputFromPort('showedges'):
            self.constructor_props['showedges'] = self.getInputFromPort('showedges')
        if self.hasInputFromPort('coordinates'):
            self.constructor_props['coordinates'] = self.getInputFromPort('coordinates')
        if self.hasInputFromPort('antialiased'):
            self.constructor_props['antialiased'] = self.getInputFromPort('antialiased')
        if self.hasInputFromPort('shading'):
            self.constructor_props['shading'] = self.getInputFromPort('shading')
        if self.hasInputFromPort('meshWidth'):
            self.constructor_props['meshWidth'] = self.getInputFromPort('meshWidth')

        
    def update_props(self, objs):
        matplotlib.artist.setp(objs, **self.props)

    def update_kwargs(self, kwargs):
        kwargs.update(self.constructor_props)
        kwargs.update(self.props)

class Mpl_AxesImageBaseProperties(MplArtistProperties):
    """None
    """
    _input_ports = [
              ("origin", "basic:String",
                {'optional': True}),
              ("resample", "basic:Boolean",
                {'optional': True, 'docstring': 'set whether or not image resampling is used'}),
              ("norm", "basic:String",
                {'optional': True}),
              ("cmap", "basic:String",
                {'optional': True}),
              ("filternorm", "basic:String",
                {'optional': True, 'docstring': 'Set whether the resize filter norms the weights -- see help for imshow'}),
              ("ax", "basic:String",
                {'optional': True}),
              ("alpha", "basic:Float",
                {'optional': True, 'docstring': 'Set the alpha value used for blending - not supported on all backends'}),
              ("array", "basic:String",
                {'optional': True, 'docstring': 'retained for backwards compatibility - use set_data instead'}),
              ("data", "basic:String",
                {'optional': True, 'docstring': 'Set the image array'}),
              ("filterrad", "basic:Float",
                {'optional': True, 'docstring': 'Set the resize filter radius only applicable to some interpolation schemes -- see help for imshow'}),
              ("interpolation", "basic:String",
                {'entry_types': "['enum']", 'docstring': "Set the interpolation method the image uses when resizing.\n\nif None, use a value from rc setting. If 'none', the image is shown as is without interpolating. 'none' is only supported in agg, ps and pdf backends and will fall back to 'nearest' mode for other backends.", 'values': "[['nearest', 'bilinear', 'bicubic', 'spline16', 'spline36', 'hanning', 'hamming', 'hermite', 'kaiser', 'quadric', 'catrom', 'gaussian', 'bessel', 'mitchell', 'sinc', 'lanczos', 'none', '']]", 'optional': True}),
        ]

    # no output ports except self
    _output_ports = [("self", "(Mpl_AxesImageBaseProperties)")]

    def __init__(self):
        MplArtistProperties.__init__(self)
        self.props = {}
        self.constructor_props = {}
        self.sub_props = {}

    def compute(self):
        MplArtistProperties.compute(self)
        if self.hasInputFromPort('origin'):
            self.constructor_props['origin'] = self.getInputFromPort('origin')
        if self.hasInputFromPort('resample'):
            self.props['resample'] = self.getInputFromPort('resample')
        if self.hasInputFromPort('norm'):
            self.constructor_props['norm'] = self.getInputFromPort('norm')
        if self.hasInputFromPort('cmap'):
            self.constructor_props['cmap'] = self.getInputFromPort('cmap')
        if self.hasInputFromPort('filternorm'):
            self.props['filternorm'] = self.getInputFromPort('filternorm')
        if self.hasInputFromPort('ax'):
            self.constructor_props['ax'] = self.getInputFromPort('ax')
        if self.hasInputFromPort('alpha'):
            self.props['alpha'] = self.getInputFromPort('alpha')
        if self.hasInputFromPort('array'):
            self.props['array'] = self.getInputFromPort('array')
        if self.hasInputFromPort('data'):
            self.props['data'] = self.getInputFromPort('data')
        if self.hasInputFromPort('filterrad'):
            self.props['filterrad'] = self.getInputFromPort('filterrad')
        if self.hasInputFromPort('interpolation'):
            self.props['interpolation'] = self.getInputFromPort('interpolation')

        
    def update_props(self, objs):
        matplotlib.artist.setp(objs, **self.props)

    def update_kwargs(self, kwargs):
        kwargs.update(self.constructor_props)
        kwargs.update(self.props)

class MplAxesImageProperties(Mpl_AxesImageBaseProperties):
    """None
    """
    _input_ports = [
              ("origin", "basic:String",
                {'optional': True}),
              ("resample", "basic:Boolean",
                {'optional': True, 'defaults': "['False']"}),
              ("norm", "basic:String",
                {'optional': True}),
              ("cmap", "basic:String",
                {'optional': True}),
              ("filterrad", "basic:Float",
                {'optional': True, 'defaults': "['4.0']"}),
              ("extent", "basic:String",
                {'optional': True, 'docstring': 'extent is data axes (left, right, bottom, top) for making image plots\n\nThis updates ax.dataLim, and, if autoscaling, sets viewLim to tightly fit the image, regardless of dataLim.  Autoscaling state is not changed, so following this with ax.autoscale_view will redo the autoscaling in accord with dataLim.'}),
              ("ax", "basic:String",
                {'optional': True}),
              ("filternorm", "basic:Integer",
                {'optional': True, 'defaults': "['1']"}),
              ("interpolation", "basic:String",
                {'optional': True}),
        ]

    # no output ports except self
    _output_ports = [("self", "(MplAxesImageProperties)")]

    def __init__(self):
        Mpl_AxesImageBaseProperties.__init__(self)
        self.props = {}
        self.constructor_props = {}
        self.sub_props = {}

    def compute(self):
        Mpl_AxesImageBaseProperties.compute(self)
        if self.hasInputFromPort('origin'):
            self.constructor_props['origin'] = self.getInputFromPort('origin')
        if self.hasInputFromPort('resample'):
            self.constructor_props['resample'] = self.getInputFromPort('resample')
        if self.hasInputFromPort('norm'):
            self.constructor_props['norm'] = self.getInputFromPort('norm')
        if self.hasInputFromPort('cmap'):
            self.constructor_props['cmap'] = self.getInputFromPort('cmap')
        if self.hasInputFromPort('filterrad'):
            self.constructor_props['filterrad'] = self.getInputFromPort('filterrad')
        if self.hasInputFromPort('extent'):
            self.props['extent'] = self.getInputFromPort('extent')
        if self.hasInputFromPort('ax'):
            self.constructor_props['ax'] = self.getInputFromPort('ax')
        if self.hasInputFromPort('filternorm'):
            self.constructor_props['filternorm'] = self.getInputFromPort('filternorm')
        if self.hasInputFromPort('interpolation'):
            self.constructor_props['interpolation'] = self.getInputFromPort('interpolation')

        
    def update_props(self, objs):
        matplotlib.artist.setp(objs, **self.props)

    def update_kwargs(self, kwargs):
        kwargs.update(self.constructor_props)
        kwargs.update(self.props)

class MplNonUniformImageProperties(MplAxesImageProperties):
    """None
    """
    _input_ports = [
              ("norm", "basic:String",
                {'optional': True}),
              ("cmap", "basic:String",
                {'optional': True}),
              ("filternorm", "basic:String",
                {'optional': True}),
              ("ax", "basic:String",
                {'optional': True}),
              ("array", "basic:String",
                {'optional': True}),
              ("data", "basic:String",
                {'optional': True, 'docstring': 'Set the grid for the pixel centers, and the pixel values.'}),
              ("filterrad", "basic:String",
                {'optional': True}),
              ("interpolation", "basic:String",
                {'optional': True}),
        ]

    # no output ports except self
    _output_ports = [("self", "(MplNonUniformImageProperties)")]

    def __init__(self):
        MplAxesImageProperties.__init__(self)
        self.props = {}
        self.constructor_props = {}
        self.sub_props = {}

    def compute(self):
        MplAxesImageProperties.compute(self)
        if self.hasInputFromPort('norm'):
            self.props['norm'] = self.getInputFromPort('norm')
        if self.hasInputFromPort('cmap'):
            self.props['cmap'] = self.getInputFromPort('cmap')
        if self.hasInputFromPort('filternorm'):
            self.props['filternorm'] = self.getInputFromPort('filternorm')
        if self.hasInputFromPort('ax'):
            self.constructor_props['ax'] = self.getInputFromPort('ax')
        if self.hasInputFromPort('array'):
            self.props['array'] = self.getInputFromPort('array')
        if self.hasInputFromPort('data'):
            self.props['data'] = self.getInputFromPort('data')
        if self.hasInputFromPort('filterrad'):
            self.props['filterrad'] = self.getInputFromPort('filterrad')
        if self.hasInputFromPort('interpolation'):
            self.props['interpolation'] = self.getInputFromPort('interpolation')

        
    def update_props(self, objs):
        matplotlib.artist.setp(objs, **self.props)

    def update_kwargs(self, kwargs):
        kwargs.update(self.constructor_props)
        kwargs.update(self.props)

class MplBboxImageProperties(Mpl_AxesImageBaseProperties):
    """
    The Image class whose size is determined by the given bbox.
    
    """
    _input_ports = [
              ("origin", "basic:String",
                {'optional': True}),
              ("resample", "basic:Boolean",
                {'optional': True, 'defaults': "['False']"}),
              ("cmap", "basic:String",
                {'optional': True}),
              ("filternorm", "basic:Integer",
                {'optional': True, 'defaults': "['1']"}),
              ("norm", "basic:String",
                {'optional': True}),
              ("interpolation", "basic:String",
                {'optional': True}),
              ("filterrad", "basic:Float",
                {'optional': True, 'defaults': "['4.0']"}),
              ("bbox", "basic:String",
                {'optional': True}),
        ]

    # no output ports except self
    _output_ports = [("self", "(MplBboxImageProperties)")]

    def __init__(self):
        Mpl_AxesImageBaseProperties.__init__(self)
        self.props = {}
        self.constructor_props = {}
        self.sub_props = {}

    def compute(self):
        Mpl_AxesImageBaseProperties.compute(self)
        if self.hasInputFromPort('origin'):
            self.constructor_props['origin'] = self.getInputFromPort('origin')
        if self.hasInputFromPort('resample'):
            self.constructor_props['resample'] = self.getInputFromPort('resample')
        if self.hasInputFromPort('cmap'):
            self.constructor_props['cmap'] = self.getInputFromPort('cmap')
        if self.hasInputFromPort('filternorm'):
            self.constructor_props['filternorm'] = self.getInputFromPort('filternorm')
        if self.hasInputFromPort('norm'):
            self.constructor_props['norm'] = self.getInputFromPort('norm')
        if self.hasInputFromPort('interpolation'):
            self.constructor_props['interpolation'] = self.getInputFromPort('interpolation')
        if self.hasInputFromPort('filterrad'):
            self.constructor_props['filterrad'] = self.getInputFromPort('filterrad')
        if self.hasInputFromPort('bbox'):
            self.constructor_props['bbox'] = self.getInputFromPort('bbox')

        
    def update_props(self, objs):
        matplotlib.artist.setp(objs, **self.props)

    def update_kwargs(self, kwargs):
        kwargs.update(self.constructor_props)
        kwargs.update(self.props)

class MplPcolorImageProperties(MplArtistProperties):
    """
    Make a pcolor-style plot with an irregular rectangular grid.

    This uses a variation of the original irregular image code,
    and it is used by pcolorfast for the corresponding grid type.
    
    """
    _input_ports = [
              ("A", "basic:String",
                {'optional': True}),
              ("ax", "basic:String",
                {'optional': True}),
              ("cmap", "basic:String",
                {'optional': True}),
              ("x", "basic:String",
                {'optional': True}),
              ("y", "basic:String",
                {'optional': True}),
              ("alpha", "basic:Float",
                {'optional': True, 'docstring': 'Set the alpha value used for blending - not supported on all backends'}),
              ("array", "basic:String",
                {'optional': True}),
              ("data", "basic:String",
                {'optional': True}),
              ("norm", "basic:String",
                {'optional': True}),
        ]

    # no output ports except self
    _output_ports = [("self", "(MplPcolorImageProperties)")]

    def __init__(self):
        MplArtistProperties.__init__(self)
        self.props = {}
        self.constructor_props = {}
        self.sub_props = {}

    def compute(self):
        MplArtistProperties.compute(self)
        if self.hasInputFromPort('A'):
            self.constructor_props['A'] = self.getInputFromPort('A')
        if self.hasInputFromPort('ax'):
            self.constructor_props['ax'] = self.getInputFromPort('ax')
        if self.hasInputFromPort('cmap'):
            self.constructor_props['cmap'] = self.getInputFromPort('cmap')
        if self.hasInputFromPort('x'):
            self.constructor_props['x'] = self.getInputFromPort('x')
        if self.hasInputFromPort('y'):
            self.constructor_props['y'] = self.getInputFromPort('y')
        if self.hasInputFromPort('alpha'):
            self.props['alpha'] = self.getInputFromPort('alpha')
        if self.hasInputFromPort('array'):
            self.props['array'] = self.getInputFromPort('array')
        if self.hasInputFromPort('data'):
            self.props['data'] = self.getInputFromPort('data')
        if self.hasInputFromPort('norm'):
            self.constructor_props['norm'] = self.getInputFromPort('norm')

        
    def update_props(self, objs):
        matplotlib.artist.setp(objs, **self.props)

    def update_kwargs(self, kwargs):
        kwargs.update(self.constructor_props)
        kwargs.update(self.props)

class MplFigureImageProperties(MplArtistProperties):
    """None
    """
    _input_ports = [
              ("origin", "basic:String",
                {'optional': True}),
              ("offsetx", "basic:Integer",
                {'optional': True, 'defaults': "['0']"}),
              ("offsety", "basic:Integer",
                {'optional': True, 'defaults': "['0']"}),
              ("cmap", "basic:String",
                {'optional': True}),
              ("fig", "basic:String",
                {'optional': True}),
              ("array", "basic:String",
                {'optional': True, 'docstring': 'Deprecated; use set_data for consistency with other image types.'}),
              ("data", "basic:String",
                {'optional': True, 'docstring': 'Set the image array'}),
              ("norm", "basic:String",
                {'optional': True}),
        ]

    # no output ports except self
    _output_ports = [("self", "(MplFigureImageProperties)")]

    def __init__(self):
        MplArtistProperties.__init__(self)
        self.props = {}
        self.constructor_props = {}
        self.sub_props = {}

    def compute(self):
        MplArtistProperties.compute(self)
        if self.hasInputFromPort('origin'):
            self.constructor_props['origin'] = self.getInputFromPort('origin')
        if self.hasInputFromPort('offsetx'):
            self.constructor_props['offsetx'] = self.getInputFromPort('offsetx')
        if self.hasInputFromPort('offsety'):
            self.constructor_props['offsety'] = self.getInputFromPort('offsety')
        if self.hasInputFromPort('cmap'):
            self.constructor_props['cmap'] = self.getInputFromPort('cmap')
        if self.hasInputFromPort('fig'):
            self.constructor_props['fig'] = self.getInputFromPort('fig')
        if self.hasInputFromPort('array'):
            self.props['array'] = self.getInputFromPort('array')
        if self.hasInputFromPort('data'):
            self.props['data'] = self.getInputFromPort('data')
        if self.hasInputFromPort('norm'):
            self.constructor_props['norm'] = self.getInputFromPort('norm')

        
    def update_props(self, objs):
        matplotlib.artist.setp(objs, **self.props)

    def update_kwargs(self, kwargs):
        kwargs.update(self.constructor_props)
        kwargs.update(self.props)

class MplLine2DProperties(MplArtistProperties):
    """
    A line - the line can have both a solid linestyle connecting all
    the vertices, and a marker at each vertex.  Additionally, the
    drawing of the solid line is influenced by the drawstyle, eg one
    can create "stepped" lines in various styles.


    
    """
    _input_ports = [
              ("picker", "basic:Float",
                {'optional': True, 'docstring': 'Sets the event picker details for the line.'}),
              ("dash_capstyle", "basic:String",
                {'entry_types': "['enum']", 'docstring': 'Set the cap style for dashed linestyles', 'values': "[['butt', 'round', 'projecting']]", 'optional': True}),
              ("color", "basic:Color",
                {'optional': True, 'docstring': 'Set the color of the line'}),
              ("markevery", "basic:String",
                {'entry_types': "['enum']", 'docstring': 'Set the markevery property to subsample the plot when using markers.  Eg if markevery=5, every 5-th marker will be plotted.  every can be', 'values': "[['(startind, stride)']]", 'optional': True}),
              ("markeredgecolor", "basic:Color",
                {'optional': True, 'docstring': 'Set the marker edge color'}),
              ("marker", "basic:String",
                {'entry_types': "['enum']", 'docstring': 'Set the line marker\n\nThe marker can also be a tuple (numsides, style, angle), which will create a custom, regular symbol.\n\n\n\nFor backward compatibility, the form (verts, 0) is also accepted, but it is equivalent to just verts for giving a raw set of vertices that define the shape.', 'values': "[['caretdown', 'caretleft', 'caretright', 'caretup', 'circle', 'diamond', 'hexagon1', 'hexagon2', 'hline', 'nothing', 'octagon', 'pentagon', 'pixel', 'plus', 'point', 'square', 'star', 'thin_diamond', 'tickdown', 'tickleft', 'tickright', 'tickup', 'tri_down', 'tri_left', 'tri_right', 'tri_up', 'triangle_down', 'triangle_left', 'triangle_right', 'triangle_up', 'vline', 'x', 'mathtext']]", 'optional': True}),
              ("markerfacecoloralt", "basic:Color",
                {'optional': True, 'docstring': 'Set the alternate marker face color.'}),
              ("linewidth", "basic:Float",
                {'optional': True, 'docstring': 'Set the line width in points'}),
              ("linestyle", "basic:String",
                {'entry_types': "['enum']", 'docstring': "Set the linestyle of the line (also accepts drawstyles)\n\n'steps' is equivalent to 'steps-pre' and is maintained for backward-compatibility.", 'values': "[['solid', 'dashed', 'dash_dot', 'dotted', 'draw nothing', 'draw nothing', 'draw nothing']]", 'optional': True}),
              ("solid_joinstyle", "basic:String",
                {'entry_types': "['enum']", 'docstring': 'Set the join style for solid linestyles', 'values': "[['miter', 'round', 'bevel']]", 'optional': True}),
              ("markerfacecolor", "basic:Color",
                {'optional': True, 'docstring': 'Set the marker face color.'}),
              ("axes", "basic:String",
                {'optional': True, 'docstring': 'Set the :class:`~matplotlib.axes.Axes` instance in which the artist resides, if any.'}),
              ("transform", "basic:String",
                {'optional': True, 'docstring': 'set the Transformation instance used by this artist'}),
              ("fillstyle", "basic:String",
                {'entry_types': "['enum']", 'docstring': "Set the marker fill style; 'full' means fill the whole marker. The other options are for half filled markers", 'values': "[['full', 'left', 'right', 'bottom', 'top']]", 'optional': True}),
              ("markeredgewidth", "basic:Float",
                {'optional': True, 'docstring': 'Set the marker edge width in points'}),
              ("solid_capstyle", "basic:String",
                {'entry_types': "['enum']", 'docstring': 'Set the cap style for solid linestyles', 'values': "[['butt', 'round', 'projecting']]", 'optional': True}),
              ("dashes", "basic:List",
                {'optional': True, 'docstring': 'Set the dash sequence, sequence of dashes with on off ink in points.  If seq is empty or if seq = (None, None), the linestyle will be set to solid.'}),
              ("markersize", "basic:Float",
                {'optional': True, 'docstring': 'Set the marker size in points'}),
              ("antialiased", "basic:Boolean",
                {'optional': True, 'docstring': 'True if line should be drawin with antialiased rendering'}),
              ("xdata", "basic:String",
                {'optional': True, 'docstring': 'Set the data np.array for x'}),
              ("drawstyle", "basic:String",
                {'entry_types': "['enum']", 'docstring': "Set the drawstyle of the plot\n\n'default' connects the points with lines. The steps variants produce step-plots. 'steps' is equivalent to 'steps-pre' and is maintained for backward-compatibility.", 'values': "[['default', 'steps', 'steps-pre', 'steps-mid', 'steps-post']]", 'optional': True}),
              ("data", "basic:String",
                {'optional': True, 'docstring': 'Set the x and y data'}),
              ("dash_joinstyle", "basic:String",
                {'entry_types': "['enum']", 'docstring': 'Set the join style for dashed linestyles', 'values': "[['miter', 'round', 'bevel']]", 'optional': True}),
              ("pickradius", "basic:Float",
                {'optional': True, 'docstring': 'Sets the pick radius used for containment tests'}),
              ("ydata", "basic:String",
                {'optional': True, 'docstring': 'Set the data np.array for y'}),
        ]

    # no output ports except self
    _output_ports = [("self", "(MplLine2DProperties)")]

    def __init__(self):
        MplArtistProperties.__init__(self)
        self.props = {}
        self.constructor_props = {}
        self.sub_props = {}

    def compute(self):
        MplArtistProperties.compute(self)
        if self.hasInputFromPort('picker'):
            self.props['picker'] = self.getInputFromPort('picker')
        if self.hasInputFromPort('dash_capstyle'):
            self.props['dash_capstyle'] = self.getInputFromPort('dash_capstyle')
        if self.hasInputFromPort('color'):
            self.props['color'] = self.getInputFromPort('color')
            self.props['color'] = translate_color(self.props['color'])
        if self.hasInputFromPort('markevery'):
            self.props['markevery'] = self.getInputFromPort('markevery')
        if self.hasInputFromPort('markeredgecolor'):
            self.props['markeredgecolor'] = self.getInputFromPort('markeredgecolor')
            self.props['markeredgecolor'] = translate_color(self.props['markeredgecolor'])
        if self.hasInputFromPort('marker'):
            self.props['marker'] = self.getInputFromPort('marker')
            self.props['marker'] = translate_MplLine2DProperties_marker(self.props['marker'])
        if self.hasInputFromPort('markerfacecoloralt'):
            self.props['markerfacecoloralt'] = self.getInputFromPort('markerfacecoloralt')
            self.props['markerfacecoloralt'] = translate_color(self.props['markerfacecoloralt'])
        if self.hasInputFromPort('linewidth'):
            self.props['linewidth'] = self.getInputFromPort('linewidth')
        if self.hasInputFromPort('linestyle'):
            self.props['linestyle'] = self.getInputFromPort('linestyle')
            self.props['linestyle'] = translate_MplLine2DProperties_linestyle(self.props['linestyle'])
        if self.hasInputFromPort('solid_joinstyle'):
            self.props['solid_joinstyle'] = self.getInputFromPort('solid_joinstyle')
        if self.hasInputFromPort('markerfacecolor'):
            self.props['markerfacecolor'] = self.getInputFromPort('markerfacecolor')
            self.props['markerfacecolor'] = translate_color(self.props['markerfacecolor'])
        if self.hasInputFromPort('axes'):
            self.props['axes'] = self.getInputFromPort('axes')
        if self.hasInputFromPort('transform'):
            self.props['transform'] = self.getInputFromPort('transform')
        if self.hasInputFromPort('fillstyle'):
            self.props['fillstyle'] = self.getInputFromPort('fillstyle')
        if self.hasInputFromPort('markeredgewidth'):
            self.props['markeredgewidth'] = self.getInputFromPort('markeredgewidth')
        if self.hasInputFromPort('solid_capstyle'):
            self.props['solid_capstyle'] = self.getInputFromPort('solid_capstyle')
        if self.hasInputFromPort('dashes'):
            self.props['dashes'] = self.getInputFromPort('dashes')
        if self.hasInputFromPort('markersize'):
            self.props['markersize'] = self.getInputFromPort('markersize')
        if self.hasInputFromPort('antialiased'):
            self.props['antialiased'] = self.getInputFromPort('antialiased')
        if self.hasInputFromPort('xdata'):
            self.props['xdata'] = self.getInputFromPort('xdata')
        if self.hasInputFromPort('drawstyle'):
            self.props['drawstyle'] = self.getInputFromPort('drawstyle')
        if self.hasInputFromPort('data'):
            self.props['data'] = self.getInputFromPort('data')
        if self.hasInputFromPort('dash_joinstyle'):
            self.props['dash_joinstyle'] = self.getInputFromPort('dash_joinstyle')
        if self.hasInputFromPort('pickradius'):
            self.props['pickradius'] = self.getInputFromPort('pickradius')
        if self.hasInputFromPort('ydata'):
            self.props['ydata'] = self.getInputFromPort('ydata')

        
    def update_props(self, objs):
        matplotlib.artist.setp(objs, **self.props)

    def update_kwargs(self, kwargs):
        kwargs.update(self.constructor_props)
        kwargs.update(self.props)

class MplPatchProperties(MplArtistProperties):
    """
    A patch is a 2D thingy with a face color and an edge color.

    If any of *edgecolor*, *facecolor*, *linewidth*, or *antialiased*
    are *None*, they default to their rc params setting.
    
    """
    _input_ports = [
              ("edgecolor", "basic:Color",
                {'optional': True, 'docstring': 'Set the patch edge color'}),
              ("facecolor", "basic:Color",
                {'optional': True, 'docstring': 'Set the patch face color'}),
              ("path_effects", "basic:String",
                {'optional': True, 'docstring': 'set path_effects, which should be a list of instances of matplotlib.patheffect._Base class or its derivatives.'}),
              ("color", "basic:Color",
                {'optional': True, 'docstring': 'Set both the edgecolor and the facecolor. .. seealso:\n\n:meth:`set_facecolor`, :meth:`set_edgecolor`    For setting the edge or face color individually.'}),
              ("antialiased", "basic:Boolean",
                {'optional': True, 'docstring': 'Set whether to use antialiased rendering'}),
              ("hatch", "basic:String",
                {'entry_types': "['enum']", 'docstring': 'Set the hatching pattern\n\nhatch can be one of:\n\n/   - diagonal hatching \\   - back diagonal |   - vertical -   - horizontal +   - crossed x   - crossed diagonal o   - small circle O   - large circle .   - dots *   - stars\n\nLetters can be combined, in which case all the specified hatchings are done.  If same letter repeats, it increases the density of hatching of that pattern.\n\nHatching is supported in the PostScript, PDF, SVG and Agg backends only.', 'values': '[[\'/\', "\'\\\\\'", "\'", "\'", \'-\', \'+\', \'x\', \'o\', \'O\', \'.\', \'*\']]', 'optional': True}),
              ("alpha", "basic:Float",
                {'optional': True, 'docstring': 'Set the alpha tranparency of the patch.'}),
              ("linewidth", "basic:Float",
                {'optional': True, 'docstring': 'Set the patch linewidth in points'}),
              ("linestyle", "basic:String",
                {'entry_types': "['enum']", 'docstring': 'Set the patch linestyle', 'values': "[['solid', 'dashed', 'dashdot', 'dotted']]", 'optional': True}),
              ("fill", "basic:Boolean",
                {'optional': True, 'docstring': 'Set whether to fill the patch'}),
        ]

    # no output ports except self
    _output_ports = [("self", "(MplPatchProperties)")]

    def __init__(self):
        MplArtistProperties.__init__(self)
        self.props = {}
        self.constructor_props = {}
        self.sub_props = {}

    def compute(self):
        MplArtistProperties.compute(self)
        if self.hasInputFromPort('edgecolor'):
            self.props['edgecolor'] = self.getInputFromPort('edgecolor')
            self.props['edgecolor'] = translate_color(self.props['edgecolor'])
        if self.hasInputFromPort('facecolor'):
            self.props['facecolor'] = self.getInputFromPort('facecolor')
            self.props['facecolor'] = translate_color(self.props['facecolor'])
        if self.hasInputFromPort('path_effects'):
            self.props['path_effects'] = self.getInputFromPort('path_effects')
        if self.hasInputFromPort('color'):
            self.props['color'] = self.getInputFromPort('color')
            self.props['color'] = translate_color(self.props['color'])
        if self.hasInputFromPort('antialiased'):
            self.props['antialiased'] = self.getInputFromPort('antialiased')
        if self.hasInputFromPort('hatch'):
            self.props['hatch'] = self.getInputFromPort('hatch')
        if self.hasInputFromPort('alpha'):
            self.props['alpha'] = self.getInputFromPort('alpha')
        if self.hasInputFromPort('linewidth'):
            self.props['linewidth'] = self.getInputFromPort('linewidth')
        if self.hasInputFromPort('linestyle'):
            self.props['linestyle'] = self.getInputFromPort('linestyle')
        if self.hasInputFromPort('fill'):
            self.props['fill'] = self.getInputFromPort('fill')

        
    def update_props(self, objs):
        matplotlib.artist.setp(objs, **self.props)

    def update_kwargs(self, kwargs):
        kwargs.update(self.constructor_props)
        kwargs.update(self.props)

class MplYAArrowProperties(MplPatchProperties):
    """
    Yet another arrow class.

    This is an arrow that is defined in display space and has a tip at
    *x1*, *y1* and a base at *x2*, *y2*.
    
    """
    _input_ports = [
              ("xytip", "basic:String",
                {'optional': True, 'docstring': '(x, y) location of arrow tip'}),
              ("headwidth", "basic:Integer",
                {'optional': True, 'docstring': 'The width of the base of the arrow head in points', 'defaults': "['12']"}),
              ("frac", "basic:Float",
                {'optional': True, 'docstring': 'The fraction of the arrow length occupied by the head', 'defaults': "['0.1']"}),
              ("figure", "basic:String",
                {'optional': True, 'docstring': 'The :class:`~matplotlib.figure.Figure` instance (fig.dpi)'}),
              ("xybase", "basic:String",
                {'optional': True, 'docstring': '(x, y) location the arrow base mid point'}),
              ("width", "basic:Integer",
                {'optional': True, 'docstring': 'The width of the arrow in points', 'defaults': "['4']"}),
        ]

    # no output ports except self
    _output_ports = [("self", "(MplYAArrowProperties)")]

    def __init__(self):
        MplPatchProperties.__init__(self)
        self.props = {}
        self.constructor_props = {}
        self.sub_props = {}

    def compute(self):
        MplPatchProperties.compute(self)
        if self.hasInputFromPort('xytip'):
            self.constructor_props['xytip'] = self.getInputFromPort('xytip')
        if self.hasInputFromPort('headwidth'):
            self.constructor_props['headwidth'] = self.getInputFromPort('headwidth')
        if self.hasInputFromPort('frac'):
            self.constructor_props['frac'] = self.getInputFromPort('frac')
        if self.hasInputFromPort('figure'):
            self.constructor_props['figure'] = self.getInputFromPort('figure')
        if self.hasInputFromPort('xybase'):
            self.constructor_props['xybase'] = self.getInputFromPort('xybase')
        if self.hasInputFromPort('width'):
            self.constructor_props['width'] = self.getInputFromPort('width')

        
    def update_props(self, objs):
        matplotlib.artist.setp(objs, **self.props)

    def update_kwargs(self, kwargs):
        kwargs.update(self.constructor_props)
        kwargs.update(self.props)

class MplFancyBboxPatchProperties(MplPatchProperties):
    """
    Draw a fancy box around a rectangle with lower left at *xy*=(*x*,
    *y*) with specified width and height.

    :class:`FancyBboxPatch` class is similar to :class:`Rectangle`
    class, but it draws a fancy box around the rectangle. The
    transformation of the rectangle box to the fancy box is delegated
    to the :class:`BoxTransmuterBase` and its derived classes.

    
    """
    _input_ports = [
              ("mutation_scale", "basic:Float",
                {'optional': True, 'docstring': 'Set the mutation scale.'}),
              ("bbox_transmuter", "basic:String",
                {'optional': True}),
              ("bounds", "basic:String",
                {'optional': True, 'docstring': 'Set the bounds of the rectangle: l,b,w,h'}),
              ("height", "basic:Float",
                {'optional': True, 'docstring': 'Set the width rectangle'}),
              ("width", "basic:Float",
                {'optional': True, 'docstring': 'Set the width rectangle'}),
              ("xy", "basic:String",
                {'optional': True}),
              ("boxstyle", "basic:String",
                {'optional': True, 'docstring': 'Set the box style.\n\nboxstyle can be a string with boxstyle name with optional comma-separated attributes. Alternatively, the attrs can be provided as keywords:\n\nset_boxstyle("round,pad=0.2") set_boxstyle("round", pad=0.2)\n\nOld attrs simply are forgotten.\n\nWithout argument (or with boxstyle = None), it returns available box styles.'}),
              ("mutation_aspect", "basic:Float",
                {'optional': True, 'docstring': 'Set the aspect ratio of the bbox mutation.'}),
              ("y", "basic:Float",
                {'optional': True, 'docstring': 'Set the bottom coord of the rectangle'}),
              ("x", "basic:Float",
                {'optional': True, 'docstring': 'Set the left coord of the rectangle'}),
        ]

    # no output ports except self
    _output_ports = [("self", "(MplFancyBboxPatchProperties)")]

    def __init__(self):
        MplPatchProperties.__init__(self)
        self.props = {}
        self.constructor_props = {}
        self.sub_props = {}

    def compute(self):
        MplPatchProperties.compute(self)
        if self.hasInputFromPort('mutation_scale'):
            self.props['mutation_scale'] = self.getInputFromPort('mutation_scale')
        if self.hasInputFromPort('bbox_transmuter'):
            self.constructor_props['bbox_transmuter'] = self.getInputFromPort('bbox_transmuter')
        if self.hasInputFromPort('bounds'):
            self.props['bounds'] = self.getInputFromPort('bounds')
        if self.hasInputFromPort('height'):
            self.props['height'] = self.getInputFromPort('height')
        if self.hasInputFromPort('width'):
            self.props['width'] = self.getInputFromPort('width')
        if self.hasInputFromPort('xy'):
            self.constructor_props['xy'] = self.getInputFromPort('xy')
        if self.hasInputFromPort('boxstyle'):
            self.props['boxstyle'] = self.getInputFromPort('boxstyle')
        if self.hasInputFromPort('mutation_aspect'):
            self.props['mutation_aspect'] = self.getInputFromPort('mutation_aspect')
        if self.hasInputFromPort('y'):
            self.props['y'] = self.getInputFromPort('y')
        if self.hasInputFromPort('x'):
            self.props['x'] = self.getInputFromPort('x')

        
    def update_props(self, objs):
        matplotlib.artist.setp(objs, **self.props)

    def update_kwargs(self, kwargs):
        kwargs.update(self.constructor_props)
        kwargs.update(self.props)

class MplEllipseProperties(MplPatchProperties):
    """
    A scale-free ellipse.
    
    """
    _input_ports = [
              ("width", "basic:String",
                {'optional': True}),
              ("xy", "basic:String",
                {'optional': True}),
              ("angle", "basic:Float",
                {'optional': True, 'defaults': "['0.0']"}),
              ("height", "basic:String",
                {'optional': True}),
        ]

    # no output ports except self
    _output_ports = [("self", "(MplEllipseProperties)")]

    def __init__(self):
        MplPatchProperties.__init__(self)
        self.props = {}
        self.constructor_props = {}
        self.sub_props = {}

    def compute(self):
        MplPatchProperties.compute(self)
        if self.hasInputFromPort('width'):
            self.constructor_props['width'] = self.getInputFromPort('width')
        if self.hasInputFromPort('xy'):
            self.constructor_props['xy'] = self.getInputFromPort('xy')
        if self.hasInputFromPort('angle'):
            self.constructor_props['angle'] = self.getInputFromPort('angle')
        if self.hasInputFromPort('height'):
            self.constructor_props['height'] = self.getInputFromPort('height')

        
    def update_props(self, objs):
        matplotlib.artist.setp(objs, **self.props)

    def update_kwargs(self, kwargs):
        kwargs.update(self.constructor_props)
        kwargs.update(self.props)

class MplArcProperties(MplEllipseProperties):
    """
    An elliptical arc.  Because it performs various optimizations, it
    can not be filled.

    The arc must be used in an :class:`~matplotlib.axes.Axes`
    instance---it can not be added directly to a
    :class:`~matplotlib.figure.Figure`---because it is optimized to
    only render the segments that are inside the axes bounding box
    with high resolution.
    
    """
    _input_ports = [
              ("theta2", "basic:Float",
                {'optional': True, 'defaults': "['360.0']"}),
              ("theta1", "basic:Float",
                {'optional': True, 'defaults': "['0.0']"}),
              ("angle", "basic:Float",
                {'optional': True, 'defaults': "['0.0']"}),
              ("height", "basic:String",
                {'optional': True}),
              ("width", "basic:String",
                {'optional': True}),
              ("xy", "basic:String",
                {'optional': True}),
        ]

    # no output ports except self
    _output_ports = [("self", "(MplArcProperties)")]

    def __init__(self):
        MplEllipseProperties.__init__(self)
        self.props = {}
        self.constructor_props = {}
        self.sub_props = {}

    def compute(self):
        MplEllipseProperties.compute(self)
        if self.hasInputFromPort('theta2'):
            self.constructor_props['theta2'] = self.getInputFromPort('theta2')
        if self.hasInputFromPort('theta1'):
            self.constructor_props['theta1'] = self.getInputFromPort('theta1')
        if self.hasInputFromPort('angle'):
            self.constructor_props['angle'] = self.getInputFromPort('angle')
        if self.hasInputFromPort('height'):
            self.constructor_props['height'] = self.getInputFromPort('height')
        if self.hasInputFromPort('width'):
            self.constructor_props['width'] = self.getInputFromPort('width')
        if self.hasInputFromPort('xy'):
            self.constructor_props['xy'] = self.getInputFromPort('xy')

        
    def update_props(self, objs):
        matplotlib.artist.setp(objs, **self.props)

    def update_kwargs(self, kwargs):
        kwargs.update(self.constructor_props)
        kwargs.update(self.props)

class MplCircleProperties(MplEllipseProperties):
    """
    A circle patch.
    
    """
    _input_ports = [
              ("xy", "basic:String",
                {'optional': True}),
              ("radius", "basic:Float",
                {'optional': True, 'docstring': 'Set the radius of the circle'}),
        ]

    # no output ports except self
    _output_ports = [("self", "(MplCircleProperties)")]

    def __init__(self):
        MplEllipseProperties.__init__(self)
        self.props = {}
        self.constructor_props = {}
        self.sub_props = {}

    def compute(self):
        MplEllipseProperties.compute(self)
        if self.hasInputFromPort('xy'):
            self.constructor_props['xy'] = self.getInputFromPort('xy')
        if self.hasInputFromPort('radius'):
            self.props['radius'] = self.getInputFromPort('radius')

        
    def update_props(self, objs):
        matplotlib.artist.setp(objs, **self.props)

    def update_kwargs(self, kwargs):
        kwargs.update(self.constructor_props)
        kwargs.update(self.props)

class MplRegularPolygonProperties(MplPatchProperties):
    """
    A regular polygon patch.
    
    """
    _input_ports = [
              ("xy", "basic:String",
                {'optional': True, 'docstring': 'A length 2 tuple (x, y) of the center.'}),
              ("radius", "basic:Integer",
                {'optional': True, 'docstring': 'The distance from the center to each of the vertices.', 'defaults': "['5']"}),
              ("orientation", "basic:Integer",
                {'optional': True, 'docstring': 'rotates the polygon (in radians).', 'defaults': "['0']"}),
              ("numVertices", "basic:String",
                {'optional': True, 'docstring': 'the number of vertices.'}),
        ]

    # no output ports except self
    _output_ports = [("self", "(MplRegularPolygonProperties)")]

    def __init__(self):
        MplPatchProperties.__init__(self)
        self.props = {}
        self.constructor_props = {}
        self.sub_props = {}

    def compute(self):
        MplPatchProperties.compute(self)
        if self.hasInputFromPort('xy'):
            self.constructor_props['xy'] = self.getInputFromPort('xy')
        if self.hasInputFromPort('radius'):
            self.constructor_props['radius'] = self.getInputFromPort('radius')
        if self.hasInputFromPort('orientation'):
            self.constructor_props['orientation'] = self.getInputFromPort('orientation')
        if self.hasInputFromPort('numVertices'):
            self.constructor_props['numVertices'] = self.getInputFromPort('numVertices')

        
    def update_props(self, objs):
        matplotlib.artist.setp(objs, **self.props)

    def update_kwargs(self, kwargs):
        kwargs.update(self.constructor_props)
        kwargs.update(self.props)

class MplCirclePolygonProperties(MplRegularPolygonProperties):
    """
    A polygon-approximation of a circle patch.
    
    """
    _input_ports = [
              ("radius", "basic:Integer",
                {'optional': True, 'defaults': "['5']"}),
              ("xy", "basic:String",
                {'optional': True}),
              ("resolution", "basic:Integer",
                {'optional': True, 'defaults': "['20']"}),
        ]

    # no output ports except self
    _output_ports = [("self", "(MplCirclePolygonProperties)")]

    def __init__(self):
        MplRegularPolygonProperties.__init__(self)
        self.props = {}
        self.constructor_props = {}
        self.sub_props = {}

    def compute(self):
        MplRegularPolygonProperties.compute(self)
        if self.hasInputFromPort('radius'):
            self.constructor_props['radius'] = self.getInputFromPort('radius')
        if self.hasInputFromPort('xy'):
            self.constructor_props['xy'] = self.getInputFromPort('xy')
        if self.hasInputFromPort('resolution'):
            self.constructor_props['resolution'] = self.getInputFromPort('resolution')

        
    def update_props(self, objs):
        matplotlib.artist.setp(objs, **self.props)

    def update_kwargs(self, kwargs):
        kwargs.update(self.constructor_props)
        kwargs.update(self.props)

class MplPathPatchProperties(MplPatchProperties):
    """
    A general polycurve path patch.
    
    """
    _input_ports = [
              ("path", "basic:String",
                {'optional': True}),
        ]

    # no output ports except self
    _output_ports = [("self", "(MplPathPatchProperties)")]

    def __init__(self):
        MplPatchProperties.__init__(self)
        self.props = {}
        self.constructor_props = {}
        self.sub_props = {}

    def compute(self):
        MplPatchProperties.compute(self)
        if self.hasInputFromPort('path'):
            self.constructor_props['path'] = self.getInputFromPort('path')

        
    def update_props(self, objs):
        matplotlib.artist.setp(objs, **self.props)

    def update_kwargs(self, kwargs):
        kwargs.update(self.constructor_props)
        kwargs.update(self.props)

class MplFancyArrowPatchProperties(MplPatchProperties):
    """
    A fancy arrow patch. It draws an arrow using the :class:ArrowStyle.
    
    """
    _input_ports = [
              ("connectionstyle", "basic:String",
                {'optional': True, 'docstring': 'Set the connection style.\n\nOld attrs simply are forgotten.\n\nWithout argument (or with connectionstyle=None), return available styles as a list of strings.'}),
              ("mutation_scale", "basic:Float",
                {'optional': True, 'docstring': 'Set the mutation scale.'}),
              ("arrowstyle", "basic:String",
                {'optional': True, 'docstring': 'Set the arrow style.\n\nOld attrs simply are forgotten.\n\nWithout argument (or with arrowstyle=None), return available box styles as a list of strings.'}),
              ("arrow_transmuter", "basic:String",
                {'optional': True}),
              ("positions", "basic:String",
                {'optional': True}),
              ("shrinkA", "basic:Float",
                {'optional': True, 'defaults': "['2.0']"}),
              ("posB", "basic:String",
                {'optional': True}),
              ("dpi_cor", "basic:String",
                {'optional': True, 'docstring': 'dpi_cor is currently used for linewidth-related things and shink factor. Mutation scale is not affected by this.'}),
              ("connector", "basic:String",
                {'optional': True}),
              ("path", "basic:String",
                {'optional': True}),
              ("shrinkB", "basic:Float",
                {'optional': True, 'defaults': "['2.0']"}),
              ("mutation_aspect", "basic:Float",
                {'optional': True, 'docstring': 'Set the aspect ratio of the bbox mutation.'}),
              ("patchA", "basic:String",
                {'optional': True, 'docstring': 'set the begin patch.'}),
              ("patchB", "basic:String",
                {'optional': True, 'docstring': 'set the begin patch'}),
              ("posA", "basic:String",
                {'optional': True}),
        ]

    # no output ports except self
    _output_ports = [("self", "(MplFancyArrowPatchProperties)")]

    def __init__(self):
        MplPatchProperties.__init__(self)
        self.props = {}
        self.constructor_props = {}
        self.sub_props = {}

    def compute(self):
        MplPatchProperties.compute(self)
        if self.hasInputFromPort('connectionstyle'):
            self.props['connectionstyle'] = self.getInputFromPort('connectionstyle')
        if self.hasInputFromPort('mutation_scale'):
            self.props['mutation_scale'] = self.getInputFromPort('mutation_scale')
        if self.hasInputFromPort('arrowstyle'):
            self.props['arrowstyle'] = self.getInputFromPort('arrowstyle')
        if self.hasInputFromPort('arrow_transmuter'):
            self.constructor_props['arrow_transmuter'] = self.getInputFromPort('arrow_transmuter')
        if self.hasInputFromPort('positions'):
            self.props['positions'] = self.getInputFromPort('positions')
        if self.hasInputFromPort('shrinkA'):
            self.constructor_props['shrinkA'] = self.getInputFromPort('shrinkA')
        if self.hasInputFromPort('posB'):
            self.constructor_props['posB'] = self.getInputFromPort('posB')
        if self.hasInputFromPort('dpi_cor'):
            self.props['dpi_cor'] = self.getInputFromPort('dpi_cor')
        if self.hasInputFromPort('connector'):
            self.constructor_props['connector'] = self.getInputFromPort('connector')
        if self.hasInputFromPort('path'):
            self.constructor_props['path'] = self.getInputFromPort('path')
        if self.hasInputFromPort('shrinkB'):
            self.constructor_props['shrinkB'] = self.getInputFromPort('shrinkB')
        if self.hasInputFromPort('mutation_aspect'):
            self.props['mutation_aspect'] = self.getInputFromPort('mutation_aspect')
        if self.hasInputFromPort('patchA'):
            self.props['patchA'] = self.getInputFromPort('patchA')
        if self.hasInputFromPort('patchB'):
            self.props['patchB'] = self.getInputFromPort('patchB')
        if self.hasInputFromPort('posA'):
            self.constructor_props['posA'] = self.getInputFromPort('posA')

        
    def update_props(self, objs):
        matplotlib.artist.setp(objs, **self.props)

    def update_kwargs(self, kwargs):
        kwargs.update(self.constructor_props)
        kwargs.update(self.props)

class MplConnectionPatchProperties(MplFancyArrowPatchProperties):
    """
    A :class:`~matplotlib.patches.ConnectionPatch` class is to make
    connecting lines between two points (possibly in different axes).
    
    """
    _input_ports = [
              ("connectionstyle", "basic:String",
                {'optional': True, 'docstring': 'the connection style', 'defaults': "['arc3']"}),
              ("coordsA", "basic:String",
                {'entry_types': "['enum']", 'values': "[['figure points', 'figure pixels', 'figure fraction', 'axes points', 'axes pixels', 'axes fraction', 'data', 'offset points', 'polar']]", 'optional': True}),
              ("arrowstyle", "basic:String",
                {'optional': True, 'docstring': 'the arrow style', 'defaults': "['-']"}),
              ("clip_on", "basic:Boolean",
                {'optional': True, 'defaults': "['False']"}),
              ("arrow_transmuter", "basic:String",
                {'optional': True}),
              ("axesA", "basic:String",
                {'optional': True}),
              ("axesB", "basic:String",
                {'optional': True}),
              ("annotation_clip", "basic:String",
                {'optional': True, 'docstring': 'set annotation_clip attribute.\n\nTrue : the annotation will only be drawn when self.xy is inside the axes.\n\nFalse : the annotation will always be drawn regardless of its position.\n\nNone : the self.xy will be checked only if xycoords is "data"'}),
              ("dpi_cor", "basic:Float",
                {'optional': True, 'defaults': "['1.0']"}),
              ("connector", "basic:String",
                {'optional': True}),
              ("xyA", "basic:String",
                {'optional': True}),
              ("xyB", "basic:String",
                {'optional': True}),
              ("relpos", "basic:String",
                {'optional': True, 'docstring': 'default is (0.5, 0.5)', 'defaults': "['(0.5']"}),
              ("shrinkB", "basic:Float",
                {'optional': True, 'docstring': 'default is 2 points', 'defaults': "['2']"}),
              ("shrinkA", "basic:Float",
                {'optional': True, 'docstring': 'default is 2 points', 'defaults': "['2']"}),
              ("mutation_aspect", "basic:Integer",
                {'optional': True, 'docstring': 'default is 1.', 'defaults': "['1']"}),
              ("mutation_scale", "basic:String",
                {'optional': True, 'docstring': 'default is text size (in points)', 'defaults': "['text']"}),
              ("patchA", "basic:String",
                {'optional': True, 'docstring': 'default is bounding box of the text', 'defaults': "['bounding']"}),
              ("patchB", "basic:String",
                {'optional': True, 'docstring': 'default is None'}),
              ("coordsB", "basic:String",
                {'entry_types': "['enum']", 'values': "[['figure points', 'figure pixels', 'figure fraction', 'axes points', 'axes pixels', 'axes fraction', 'data', 'offset points', 'polar']]", 'optional': True}),
              ("?", "basic:String",
                {'optional': True, 'docstring': 'any key for :class:`matplotlib.patches.PathPatch`'}),
        ]

    # no output ports except self
    _output_ports = [("self", "(MplConnectionPatchProperties)")]

    def __init__(self):
        MplFancyArrowPatchProperties.__init__(self)
        self.props = {}
        self.constructor_props = {}
        self.sub_props = {}

    def compute(self):
        MplFancyArrowPatchProperties.compute(self)
        if self.hasInputFromPort('connectionstyle'):
            self.constructor_props['connectionstyle'] = self.getInputFromPort('connectionstyle')
        if self.hasInputFromPort('coordsA'):
            self.constructor_props['coordsA'] = self.getInputFromPort('coordsA')
        if self.hasInputFromPort('arrowstyle'):
            self.constructor_props['arrowstyle'] = self.getInputFromPort('arrowstyle')
        if self.hasInputFromPort('clip_on'):
            self.constructor_props['clip_on'] = self.getInputFromPort('clip_on')
        if self.hasInputFromPort('arrow_transmuter'):
            self.constructor_props['arrow_transmuter'] = self.getInputFromPort('arrow_transmuter')
        if self.hasInputFromPort('axesA'):
            self.constructor_props['axesA'] = self.getInputFromPort('axesA')
        if self.hasInputFromPort('axesB'):
            self.constructor_props['axesB'] = self.getInputFromPort('axesB')
        if self.hasInputFromPort('annotation_clip'):
            self.props['annotation_clip'] = self.getInputFromPort('annotation_clip')
        if self.hasInputFromPort('dpi_cor'):
            self.constructor_props['dpi_cor'] = self.getInputFromPort('dpi_cor')
        if self.hasInputFromPort('connector'):
            self.constructor_props['connector'] = self.getInputFromPort('connector')
        if self.hasInputFromPort('xyA'):
            self.constructor_props['xyA'] = self.getInputFromPort('xyA')
        if self.hasInputFromPort('xyB'):
            self.constructor_props['xyB'] = self.getInputFromPort('xyB')
        if self.hasInputFromPort('relpos'):
            self.constructor_props['relpos'] = self.getInputFromPort('relpos')
        if self.hasInputFromPort('shrinkB'):
            self.constructor_props['shrinkB'] = self.getInputFromPort('shrinkB')
        if self.hasInputFromPort('shrinkA'):
            self.constructor_props['shrinkA'] = self.getInputFromPort('shrinkA')
        if self.hasInputFromPort('mutation_aspect'):
            self.constructor_props['mutation_aspect'] = self.getInputFromPort('mutation_aspect')
        if self.hasInputFromPort('mutation_scale'):
            self.constructor_props['mutation_scale'] = self.getInputFromPort('mutation_scale')
        if self.hasInputFromPort('patchA'):
            self.constructor_props['patchA'] = self.getInputFromPort('patchA')
        if self.hasInputFromPort('patchB'):
            self.constructor_props['patchB'] = self.getInputFromPort('patchB')
        if self.hasInputFromPort('coordsB'):
            self.constructor_props['coordsB'] = self.getInputFromPort('coordsB')
        if self.hasInputFromPort('?'):
            self.constructor_props['?'] = self.getInputFromPort('?')

        
    def update_props(self, objs):
        matplotlib.artist.setp(objs, **self.props)

    def update_kwargs(self, kwargs):
        kwargs.update(self.constructor_props)
        kwargs.update(self.props)

class MplRectangleProperties(MplPatchProperties):
    """
    Draw a rectangle with lower left at *xy* = (*x*, *y*) with
    specified *width* and *height*.
    
    """
    _input_ports = [
              ("bounds", "basic:String",
                {'optional': True, 'docstring': 'Set the bounds of the rectangle: l,b,w,h'}),
              ("height", "basic:Float",
                {'optional': True, 'docstring': 'Set the width rectangle'}),
              ("width", "basic:Float",
                {'optional': True, 'docstring': 'Set the width rectangle'}),
              ("xy", "basic:List",
                {'optional': True, 'docstring': 'Set the left and bottom coords of the rectangle'}),
              ("y", "basic:Float",
                {'optional': True, 'docstring': 'Set the bottom coord of the rectangle'}),
              ("x", "basic:Float",
                {'optional': True, 'docstring': 'Set the left coord of the rectangle'}),
        ]

    # no output ports except self
    _output_ports = [("self", "(MplRectangleProperties)")]

    def __init__(self):
        MplPatchProperties.__init__(self)
        self.props = {}
        self.constructor_props = {}
        self.sub_props = {}

    def compute(self):
        MplPatchProperties.compute(self)
        if self.hasInputFromPort('bounds'):
            self.props['bounds'] = self.getInputFromPort('bounds')
        if self.hasInputFromPort('height'):
            self.props['height'] = self.getInputFromPort('height')
        if self.hasInputFromPort('width'):
            self.props['width'] = self.getInputFromPort('width')
        if self.hasInputFromPort('xy'):
            self.props['xy'] = self.getInputFromPort('xy')
        if self.hasInputFromPort('y'):
            self.props['y'] = self.getInputFromPort('y')
        if self.hasInputFromPort('x'):
            self.props['x'] = self.getInputFromPort('x')

        
    def update_props(self, objs):
        matplotlib.artist.setp(objs, **self.props)

    def update_kwargs(self, kwargs):
        kwargs.update(self.constructor_props)
        kwargs.update(self.props)

class MplPolygonProperties(MplPatchProperties):
    """
    A general polygon patch.
    
    """
    _input_ports = [
              ("xy", "basic:String",
                {'optional': True}),
              ("closed", "basic:String",
                {'optional': True}),
        ]

    # no output ports except self
    _output_ports = [("self", "(MplPolygonProperties)")]

    def __init__(self):
        MplPatchProperties.__init__(self)
        self.props = {}
        self.constructor_props = {}
        self.sub_props = {}

    def compute(self):
        MplPatchProperties.compute(self)
        if self.hasInputFromPort('xy'):
            self.props['xy'] = self.getInputFromPort('xy')
        if self.hasInputFromPort('closed'):
            self.props['closed'] = self.getInputFromPort('closed')

        
    def update_props(self, objs):
        matplotlib.artist.setp(objs, **self.props)

    def update_kwargs(self, kwargs):
        kwargs.update(self.constructor_props)
        kwargs.update(self.props)

class MplFancyArrowProperties(MplPolygonProperties):
    """
    Like Arrow, but lets you set head width and head height independently.
    
    """
    _input_ports = [
              ("length_includes_head", "basic:Boolean",
                {'optional': True, 'docstring': 'True if head is counted in calculating the length.', 'defaults': "['False']"}),
              ("head_length", "basic:String",
                {'optional': True}),
              ("head_width", "basic:String",
                {'optional': True}),
              ("width", "basic:Float",
                {'optional': True, 'defaults': "['0.001']"}),
              ("shape", "basic:String",
                {'optional': True, 'defaults': "['full']"}),
              ("dx", "basic:String",
                {'optional': True}),
              ("dy", "basic:String",
                {'optional': True}),
              ("y", "basic:String",
                {'optional': True}),
              ("x", "basic:String",
                {'optional': True}),
              ("head_starts_at_zero", "basic:Boolean",
                {'optional': True, 'defaults': "['False']"}),
              ("overhang", "basic:Integer",
                {'optional': True, 'defaults': "['0']"}),
        ]

    # no output ports except self
    _output_ports = [("self", "(MplFancyArrowProperties)")]

    def __init__(self):
        MplPolygonProperties.__init__(self)
        self.props = {}
        self.constructor_props = {}
        self.sub_props = {}

    def compute(self):
        MplPolygonProperties.compute(self)
        if self.hasInputFromPort('length_includes_head'):
            self.constructor_props['length_includes_head'] = self.getInputFromPort('length_includes_head')
        if self.hasInputFromPort('head_length'):
            self.constructor_props['head_length'] = self.getInputFromPort('head_length')
        if self.hasInputFromPort('head_width'):
            self.constructor_props['head_width'] = self.getInputFromPort('head_width')
        if self.hasInputFromPort('width'):
            self.constructor_props['width'] = self.getInputFromPort('width')
        if self.hasInputFromPort('shape'):
            self.constructor_props['shape'] = self.getInputFromPort('shape')
        if self.hasInputFromPort('dx'):
            self.constructor_props['dx'] = self.getInputFromPort('dx')
        if self.hasInputFromPort('dy'):
            self.constructor_props['dy'] = self.getInputFromPort('dy')
        if self.hasInputFromPort('y'):
            self.constructor_props['y'] = self.getInputFromPort('y')
        if self.hasInputFromPort('x'):
            self.constructor_props['x'] = self.getInputFromPort('x')
        if self.hasInputFromPort('head_starts_at_zero'):
            self.constructor_props['head_starts_at_zero'] = self.getInputFromPort('head_starts_at_zero')
        if self.hasInputFromPort('overhang'):
            self.constructor_props['overhang'] = self.getInputFromPort('overhang')

        
    def update_props(self, objs):
        matplotlib.artist.setp(objs, **self.props)

    def update_kwargs(self, kwargs):
        kwargs.update(self.constructor_props)
        kwargs.update(self.props)

class MplWedgeProperties(MplPatchProperties):
    """
    Wedge shaped patch.
    
    """
    _input_ports = [
              ("theta2", "basic:String",
                {'optional': True}),
              ("width", "basic:String",
                {'optional': True}),
              ("r", "basic:String",
                {'optional': True}),
              ("theta1", "basic:String",
                {'optional': True}),
              ("center", "basic:String",
                {'optional': True}),
        ]

    # no output ports except self
    _output_ports = [("self", "(MplWedgeProperties)")]

    def __init__(self):
        MplPatchProperties.__init__(self)
        self.props = {}
        self.constructor_props = {}
        self.sub_props = {}

    def compute(self):
        MplPatchProperties.compute(self)
        if self.hasInputFromPort('theta2'):
            self.constructor_props['theta2'] = self.getInputFromPort('theta2')
        if self.hasInputFromPort('width'):
            self.constructor_props['width'] = self.getInputFromPort('width')
        if self.hasInputFromPort('r'):
            self.constructor_props['r'] = self.getInputFromPort('r')
        if self.hasInputFromPort('theta1'):
            self.constructor_props['theta1'] = self.getInputFromPort('theta1')
        if self.hasInputFromPort('center'):
            self.constructor_props['center'] = self.getInputFromPort('center')

        
    def update_props(self, objs):
        matplotlib.artist.setp(objs, **self.props)

    def update_kwargs(self, kwargs):
        kwargs.update(self.constructor_props)
        kwargs.update(self.props)

class MplArrowProperties(MplPatchProperties):
    """
    An arrow patch.
    
    """
    _input_ports = [
              ("y", "basic:String",
                {'optional': True}),
              ("x", "basic:String",
                {'optional': True}),
              ("dy", "basic:String",
                {'optional': True}),
              ("dx", "basic:String",
                {'optional': True}),
              ("width", "basic:Float",
                {'optional': True, 'defaults': "['1.0']"}),
        ]

    # no output ports except self
    _output_ports = [("self", "(MplArrowProperties)")]

    def __init__(self):
        MplPatchProperties.__init__(self)
        self.props = {}
        self.constructor_props = {}
        self.sub_props = {}

    def compute(self):
        MplPatchProperties.compute(self)
        if self.hasInputFromPort('y'):
            self.constructor_props['y'] = self.getInputFromPort('y')
        if self.hasInputFromPort('x'):
            self.constructor_props['x'] = self.getInputFromPort('x')
        if self.hasInputFromPort('dy'):
            self.constructor_props['dy'] = self.getInputFromPort('dy')
        if self.hasInputFromPort('dx'):
            self.constructor_props['dx'] = self.getInputFromPort('dx')
        if self.hasInputFromPort('width'):
            self.constructor_props['width'] = self.getInputFromPort('width')

        
    def update_props(self, objs):
        matplotlib.artist.setp(objs, **self.props)

    def update_kwargs(self, kwargs):
        kwargs.update(self.constructor_props)
        kwargs.update(self.props)

class MplShadowProperties(MplPatchProperties):
    """None
    """
    _input_ports = [
              ("patch", "basic:String",
                {'optional': True}),
              ("props", "basic:String",
                {'optional': True}),
              ("oy", "basic:String",
                {'optional': True}),
              ("ox", "basic:String",
                {'optional': True}),
        ]

    # no output ports except self
    _output_ports = [("self", "(MplShadowProperties)")]

    def __init__(self):
        MplPatchProperties.__init__(self)
        self.props = {}
        self.constructor_props = {}
        self.sub_props = {}

    def compute(self):
        MplPatchProperties.compute(self)
        if self.hasInputFromPort('patch'):
            self.constructor_props['patch'] = self.getInputFromPort('patch')
        if self.hasInputFromPort('props'):
            self.constructor_props['props'] = self.getInputFromPort('props')
        if self.hasInputFromPort('oy'):
            self.constructor_props['oy'] = self.getInputFromPort('oy')
        if self.hasInputFromPort('ox'):
            self.constructor_props['ox'] = self.getInputFromPort('ox')

        
    def update_props(self, objs):
        matplotlib.artist.setp(objs, **self.props)

    def update_kwargs(self, kwargs):
        kwargs.update(self.constructor_props)
        kwargs.update(self.props)

class MplTextProperties(MplArtistProperties):
    """
    Handle storing and drawing of text in window or data coordinates.
    
    """
    _input_ports = [
              ("rotation_mode", "basic:String",
                {'optional': True, 'docstring': 'set text rotation mode. If "anchor", the un-rotated text will first aligned according to their ha and va, and then will be rotated with the alignement reference point as a origin. If None (default), the text will be rotated first then will be aligned.'}),
              ("style", "basic:String",
                {'entry_types': "['enum']", 'docstring': 'Set the font style.', 'values': "[['normal', 'italic', 'oblique']]", 'optional': True}),
              ("linespacing", "basic:Float",
                {'optional': True, 'docstring': 'Set the line spacing as a multiple of the font size. Default is 1.2.'}),
              ("family", "basic:String",
                {'entry_types': "['enum']", 'docstring': 'Set the font family.  May be either a single string, or a list of strings in decreasing priority.  Each string may be either a real font name or a generic font class name.  If the latter, the specific font names will be looked up in the :file:`matplotlibrc` file.', 'values': "[['FONTNAME', 'serif', 'sans-serif', 'cursive', 'fantasy', 'monospace']]", 'optional': True}),
              ("color", "basic:Color",
                {'optional': True, 'docstring': 'Set the foreground color of the text'}),
              ("text", "basic:String",
                {'optional': True, 'docstring': 'Set the text string s\n\nIt may contain newlines (\\n) or math in LaTeX syntax.'}),
              ("verticalalignment", "basic:String",
                {'entry_types': "['enum']", 'docstring': 'Set the vertical alignment', 'values': "[['center', 'top', 'bottom', 'baseline']]", 'optional': True}),
              ("variant", "basic:String",
                {'entry_types': "['enum']", 'docstring': "Set the font variant, either 'normal' or 'small-caps'.", 'values': "[['normal', 'small-caps']]", 'optional': True}),
              ("path_effects", "basic:String",
                {'optional': True}),
              ("weight", "basic:String",
                {'entry_types': "['enum']", 'docstring': 'Set the font weight.', 'values': "[['a numeric value in range 0-1000', 'ultralight', 'light', 'normal', 'regular', 'book', 'medium', 'roman', 'semibold', 'demibold', 'demi', 'bold', 'heavy', 'extra bold', 'black']]", 'optional': True}),
              ("stretch", "basic:String",
                {'entry_types': "['enum']", 'docstring': 'Set the font stretch (horizontal condensation or expansion).', 'values': "[['a numeric value in range 0-1000', 'ultra-condensed', 'extra-condensed', 'condensed', 'semi-condensed', 'normal', 'semi-expanded', 'expanded', 'extra-expanded', 'ultra-expanded']]", 'optional': True}),
              ("fontproperties", "basic:String",
                {'optional': True, 'docstring': 'Set the font properties that control the text.  fp must be a :class:`matplotlib.font_manager.FontProperties` object.'}),
              ("x", "basic:Float",
                {'optional': True, 'docstring': 'Set the x position of the text'}),
              ("horizontalalignment", "basic:String",
                {'entry_types': "['enum']", 'docstring': 'Set the horizontal alignment to one of', 'values': "[['center', 'right', 'left']]", 'optional': True}),
              ("bbox", "basic:String",
                {'optional': True, 'docstring': 'Draw a bounding box around self.  rectprops are any settable properties for a rectangle, eg facecolor=\'red\', alpha=0.5.\n\nt.set_bbox(dict(facecolor=\'red\', alpha=0.5))\n\nIf rectprops has "boxstyle" key. A FancyBboxPatch is initialized with rectprops and will be drawn. The mutation scale of the FancyBboxPath is set to the fontsize.'}),
              ("backgroundcolor", "basic:Color",
                {'optional': True, 'docstring': 'Set the background color of the text by updating the bbox.'}),
              ("position", "basic:String",
                {'optional': True, 'docstring': 'Set the (x, y) position of the text'}),
              ("y", "basic:Float",
                {'optional': True, 'docstring': 'Set the y position of the text'}),
              ("multialignment", "basic:String",
                {'entry_types': "['enum']", 'docstring': 'Set the alignment for multiple lines layout.  The layout of the bounding box of all the lines is determined bu the horizontalalignment and verticalalignment properties, but the multiline text within that box can be', 'values': "[['left', 'right', 'center']]", 'optional': True}),
              ("rotation", "basic:String",
                {'entry_types': "['enum']", 'docstring': 'Set the rotation of the text', 'values': "[['angle in degrees', 'vertical', 'horizontal']]", 'optional': True}),
              ("size", "basic:String",
                {'entry_types': "['enum']", 'docstring': 'Set the font size.  May be either a size string, relative to the default font size, or an absolute font size in points.', 'values': "[['size in points', 'xx-small', 'x-small', 'small', 'medium', 'large', 'x-large', 'xx-large']]", 'optional': True}),
        ]

    # no output ports except self
    _output_ports = [("self", "(MplTextProperties)")]

    def __init__(self):
        MplArtistProperties.__init__(self)
        self.props = {}
        self.constructor_props = {}
        self.sub_props = {}

    def compute(self):
        MplArtistProperties.compute(self)
        if self.hasInputFromPort('rotation_mode'):
            self.props['rotation_mode'] = self.getInputFromPort('rotation_mode')
        if self.hasInputFromPort('style'):
            self.props['style'] = self.getInputFromPort('style')
        if self.hasInputFromPort('linespacing'):
            self.props['linespacing'] = self.getInputFromPort('linespacing')
        if self.hasInputFromPort('family'):
            self.props['family'] = self.getInputFromPort('family')
        if self.hasInputFromPort('color'):
            self.props['color'] = self.getInputFromPort('color')
            self.props['color'] = translate_color(self.props['color'])
        if self.hasInputFromPort('text'):
            self.props['text'] = self.getInputFromPort('text')
        if self.hasInputFromPort('verticalalignment'):
            self.props['verticalalignment'] = self.getInputFromPort('verticalalignment')
        if self.hasInputFromPort('variant'):
            self.props['variant'] = self.getInputFromPort('variant')
        if self.hasInputFromPort('path_effects'):
            self.props['path_effects'] = self.getInputFromPort('path_effects')
        if self.hasInputFromPort('weight'):
            self.props['weight'] = self.getInputFromPort('weight')
        if self.hasInputFromPort('stretch'):
            self.props['stretch'] = self.getInputFromPort('stretch')
        if self.hasInputFromPort('fontproperties'):
            self.props['fontproperties'] = self.getInputFromPort('fontproperties')
        if self.hasInputFromPort('x'):
            self.props['x'] = self.getInputFromPort('x')
        if self.hasInputFromPort('horizontalalignment'):
            self.props['horizontalalignment'] = self.getInputFromPort('horizontalalignment')
        if self.hasInputFromPort('bbox'):
            self.props['bbox'] = self.getInputFromPort('bbox')
        if self.hasInputFromPort('backgroundcolor'):
            self.props['backgroundcolor'] = self.getInputFromPort('backgroundcolor')
            self.props['backgroundcolor'] = translate_color(self.props['backgroundcolor'])
        if self.hasInputFromPort('position'):
            self.props['position'] = self.getInputFromPort('position')
        if self.hasInputFromPort('y'):
            self.props['y'] = self.getInputFromPort('y')
        if self.hasInputFromPort('multialignment'):
            self.props['multialignment'] = self.getInputFromPort('multialignment')
        if self.hasInputFromPort('rotation'):
            self.props['rotation'] = self.getInputFromPort('rotation')
        if self.hasInputFromPort('size'):
            self.props['size'] = self.getInputFromPort('size')

        
    def update_props(self, objs):
        matplotlib.artist.setp(objs, **self.props)

    def update_kwargs(self, kwargs):
        kwargs.update(self.constructor_props)
        kwargs.update(self.props)

class MplTextWithDashProperties(MplTextProperties):
    """
    This is basically a :class:`~matplotlib.text.Text` with a dash
    (drawn with a :class:`~matplotlib.lines.Line2D`) before/after
    it. It is intended to be a drop-in replacement for
    :class:`~matplotlib.text.Text`, and should behave identically to
    it when *dashlength* = 0.0.

    The dash always comes between the point specified by
    :meth:`~matplotlib.text.Text.set_position` and the text. When a
    dash exists, the text alignment arguments (*horizontalalignment*,
    *verticalalignment*) are ignored.

    *dashlength* is the length of the dash in canvas units.
    (default = 0.0).

    *dashdirection* is one of 0 or 1, where 0 draws the dash after the
    text and 1 before.  (default = 0).

    *dashrotation* specifies the rotation of the dash, and should
    generally stay *None*. In this case
    :meth:`~matplotlib.text.TextWithDash.get_dashrotation` returns
    :meth:`~matplotlib.text.Text.get_rotation`.  (I.e., the dash takes
    its rotation from the text's rotation). Because the text center is
    projected onto the dash, major deviations in the rotation cause
    what may be considered visually unappealing results.
    (default = *None*)

    *dashpad* is a padding length to add (or subtract) space
    between the text and the dash, in canvas units.
    (default = 3)

    *dashpush* "pushes" the dash and text away from the point
    specified by :meth:`~matplotlib.text.Text.set_position` by the
    amount in canvas units.  (default = 0)

    .. note::
        The alignment of the two objects is based on the bounding box
        of the :class:`~matplotlib.text.Text`, as obtained by
        :meth:`~matplotlib.artist.Artist.get_window_extent`.  This, in
        turn, appears to depend on the font metrics as given by the
        rendering backend. Hence the quality of the "centering" of the
        label text with respect to the dash varies depending on the
        backend used.

    .. note::
        I'm not sure that I got the
        :meth:`~matplotlib.text.TextWithDash.get_window_extent` right,
        or whether that's sufficient for providing the object bounding
        box.
    
    """
    _input_ports = [
              ("dashpush", "basic:Float",
                {'optional': True, 'docstring': 'Set the "push" of the TextWithDash, which is the extra spacing between the beginning of the dash and the specified position.'}),
              ("dashdirection", "basic:String",
                {'optional': True, 'docstring': "Set the direction of the dash following the text. 1 is before the text and 0 is after. The default is 0, which is what you'd want for the typical case of ticks below and on the left of the figure."}),
              ("linespacing", "basic:String",
                {'optional': True}),
              ("figure", "basic:String",
                {'optional': True, 'docstring': 'Set the figure instance the artist belong to.'}),
              ("color", "basic:String",
                {'optional': True}),
              ("text", "basic:String",
                {'optional': True, 'defaults': "['']"}),
              ("verticalalignment", "basic:String",
                {'optional': True, 'defaults': "['center']"}),
              ("dashpad", "basic:Float",
                {'optional': True, 'docstring': 'Set the "pad" of the TextWithDash, which is the extra spacing between the dash and the text, in canvas units.'}),
              ("dashrotation", "basic:Float",
                {'optional': True, 'docstring': 'Set the rotation of the dash, in degrees'}),
              ("transform", "basic:String",
                {'optional': True, 'docstring': 'Set the :class:`matplotlib.transforms.Transform` instance used by this artist.'}),
              ("fontproperties", "basic:String",
                {'optional': True}),
              ("multialignment", "basic:String",
                {'optional': True}),
              ("x", "basic:Float",
                {'optional': True, 'docstring': 'Set the x position of the :class:`TextWithDash`.'}),
              ("y", "basic:Float",
                {'optional': True, 'docstring': 'Set the y position of the :class:`TextWithDash`.'}),
              ("position", "basic:String",
                {'optional': True, 'docstring': 'Set the (x, y) position of the :class:`TextWithDash`.'}),
              ("dashlength", "basic:Float",
                {'optional': True, 'docstring': 'Set the length of the dash.'}),
              ("rotation", "basic:String",
                {'optional': True}),
              ("horizontalalignment", "basic:String",
                {'optional': True, 'defaults': "['center']"}),
        ]

    # no output ports except self
    _output_ports = [("self", "(MplTextWithDashProperties)")]

    def __init__(self):
        MplTextProperties.__init__(self)
        self.props = {}
        self.constructor_props = {}
        self.sub_props = {}

    def compute(self):
        MplTextProperties.compute(self)
        if self.hasInputFromPort('dashpush'):
            self.props['dashpush'] = self.getInputFromPort('dashpush')
        if self.hasInputFromPort('dashdirection'):
            self.props['dashdirection'] = self.getInputFromPort('dashdirection')
        if self.hasInputFromPort('linespacing'):
            self.constructor_props['linespacing'] = self.getInputFromPort('linespacing')
        if self.hasInputFromPort('figure'):
            self.props['figure'] = self.getInputFromPort('figure')
        if self.hasInputFromPort('color'):
            self.constructor_props['color'] = self.getInputFromPort('color')
        if self.hasInputFromPort('text'):
            self.constructor_props['text'] = self.getInputFromPort('text')
        if self.hasInputFromPort('verticalalignment'):
            self.constructor_props['verticalalignment'] = self.getInputFromPort('verticalalignment')
        if self.hasInputFromPort('dashpad'):
            self.props['dashpad'] = self.getInputFromPort('dashpad')
        if self.hasInputFromPort('dashrotation'):
            self.props['dashrotation'] = self.getInputFromPort('dashrotation')
        if self.hasInputFromPort('transform'):
            self.props['transform'] = self.getInputFromPort('transform')
        if self.hasInputFromPort('fontproperties'):
            self.constructor_props['fontproperties'] = self.getInputFromPort('fontproperties')
        if self.hasInputFromPort('multialignment'):
            self.constructor_props['multialignment'] = self.getInputFromPort('multialignment')
        if self.hasInputFromPort('x'):
            self.props['x'] = self.getInputFromPort('x')
        if self.hasInputFromPort('y'):
            self.props['y'] = self.getInputFromPort('y')
        if self.hasInputFromPort('position'):
            self.props['position'] = self.getInputFromPort('position')
        if self.hasInputFromPort('dashlength'):
            self.props['dashlength'] = self.getInputFromPort('dashlength')
        if self.hasInputFromPort('rotation'):
            self.constructor_props['rotation'] = self.getInputFromPort('rotation')
        if self.hasInputFromPort('horizontalalignment'):
            self.constructor_props['horizontalalignment'] = self.getInputFromPort('horizontalalignment')

        
    def update_props(self, objs):
        matplotlib.artist.setp(objs, **self.props)

    def update_kwargs(self, kwargs):
        kwargs.update(self.constructor_props)
        kwargs.update(self.props)

class MplTickProperties(MplArtistProperties):
    """
    Abstract base class for the axis ticks, grid lines and labels

    1 refers to the bottom of the plot for xticks and the left for yticks
    2 refers to the top of the plot for xticks and the right for yticks

    Publicly accessible attributes:

      :attr:`tick1line`
          a Line2D instance

      :attr:`tick2line`
          a Line2D instance

      :attr:`gridline`
          a Line2D instance

      :attr:`label1`
          a Text instance

      :attr:`label2`
          a Text instance

      :attr:`gridOn`
          a boolean which determines whether to draw the tickline

      :attr:`tick1On`
          a boolean which determines whether to draw the 1st tickline

      :attr:`tick2On`
          a boolean which determines whether to draw the 2nd tickline

      :attr:`label1On`
          a boolean which determines whether to draw tick label

      :attr:`label2On`
          a boolean which determines whether to draw tick label

    
    """
    _input_ports = [
              ("label1On", "basic:Boolean",
                {'optional': True, 'defaults': "['True']"}),
              ("loc", "basic:String",
                {'optional': True}),
              ("major", "basic:Boolean",
                {'optional': True, 'defaults': "['True']"}),
              ("label2On", "basic:Boolean",
                {'optional': True, 'defaults': "['False']"}),
              ("color", "basic:String",
                {'optional': True}),
              ("label1", "basic:String",
                {'optional': True, 'docstring': 'Set the text of ticklabel'}),
              ("label2", "basic:String",
                {'optional': True, 'docstring': 'Set the text of ticklabel2'}),
              ("axes", "basic:String",
                {'optional': True}),
              ("clip_path", "basic:String",
                {'entry_types': "['enum']", 'docstring': "Set the artist's clip path, which may be:\n\na :class:`~matplotlib.patches.Patch` (or subclass) instance\n\n\n\nNone, to remove the clipping path\n\nFor efficiency, if the path happens to be an axis-aligned rectangle, this method will set the clipping box to the corresponding rectangle and set the clipping path to None.", 'values': "[['(:class:`~matplotlib.path.Path`,         :class:`~matplotlib.transforms.Transform`)', ':class:`~matplotlib.patches.Patch`']]", 'optional': True}),
              ("label", "basic:String",
                {'optional': True, 'docstring': 'Set the text of ticklabel'}),
              ("labelcolor", "basic:String",
                {'optional': True}),
              ("tickdir", "basic:String",
                {'optional': True}),
              ("pad", "basic:Float",
                {'optional': True, 'docstring': 'Set the tick label pad in points'}),
              ("gridOn", "basic:String",
                {'optional': True}),
              ("zorder", "basic:String",
                {'optional': True}),
              ("tick2On", "basic:Boolean",
                {'optional': True, 'defaults': "['True']"}),
              ("labelsize", "basic:String",
                {'optional': True}),
              ("width", "basic:String",
                {'optional': True}),
              ("tick1On", "basic:Boolean",
                {'optional': True, 'defaults': "['True']"}),
              ("size", "basic:String",
                {'optional': True}),
        ]

    # no output ports except self
    _output_ports = [("self", "(MplTickProperties)")]

    def __init__(self):
        MplArtistProperties.__init__(self)
        self.props = {}
        self.constructor_props = {}
        self.sub_props = {}

    def compute(self):
        MplArtistProperties.compute(self)
        if self.hasInputFromPort('label1On'):
            self.constructor_props['label1On'] = self.getInputFromPort('label1On')
        if self.hasInputFromPort('loc'):
            self.constructor_props['loc'] = self.getInputFromPort('loc')
        if self.hasInputFromPort('major'):
            self.constructor_props['major'] = self.getInputFromPort('major')
        if self.hasInputFromPort('label2On'):
            self.constructor_props['label2On'] = self.getInputFromPort('label2On')
        if self.hasInputFromPort('color'):
            self.constructor_props['color'] = self.getInputFromPort('color')
        if self.hasInputFromPort('label1'):
            self.props['label1'] = self.getInputFromPort('label1')
        if self.hasInputFromPort('label2'):
            self.props['label2'] = self.getInputFromPort('label2')
        if self.hasInputFromPort('axes'):
            self.constructor_props['axes'] = self.getInputFromPort('axes')
        if self.hasInputFromPort('clip_path'):
            self.props['clip_path'] = self.getInputFromPort('clip_path')
        if self.hasInputFromPort('label'):
            self.props['label'] = self.getInputFromPort('label')
        if self.hasInputFromPort('labelcolor'):
            self.constructor_props['labelcolor'] = self.getInputFromPort('labelcolor')
        if self.hasInputFromPort('tickdir'):
            self.constructor_props['tickdir'] = self.getInputFromPort('tickdir')
        if self.hasInputFromPort('pad'):
            self.props['pad'] = self.getInputFromPort('pad')
        if self.hasInputFromPort('gridOn'):
            self.constructor_props['gridOn'] = self.getInputFromPort('gridOn')
        if self.hasInputFromPort('zorder'):
            self.constructor_props['zorder'] = self.getInputFromPort('zorder')
        if self.hasInputFromPort('tick2On'):
            self.constructor_props['tick2On'] = self.getInputFromPort('tick2On')
        if self.hasInputFromPort('labelsize'):
            self.constructor_props['labelsize'] = self.getInputFromPort('labelsize')
        if self.hasInputFromPort('width'):
            self.constructor_props['width'] = self.getInputFromPort('width')
        if self.hasInputFromPort('tick1On'):
            self.constructor_props['tick1On'] = self.getInputFromPort('tick1On')
        if self.hasInputFromPort('size'):
            self.constructor_props['size'] = self.getInputFromPort('size')

        
    def update_props(self, objs):
        matplotlib.artist.setp(objs, **self.props)

    def update_kwargs(self, kwargs):
        kwargs.update(self.constructor_props)
        kwargs.update(self.props)

class MplXTickProperties(MplTickProperties):
    """
    Contains all the Artists needed to make an x tick - the tick line,
    the label text and the grid line
    
    """
    _input_ports = [
              ("label1On", "basic:Boolean",
                {'optional': True, 'defaults': "['True']"}),
              ("loc", "basic:String",
                {'optional': True}),
              ("major", "basic:Boolean",
                {'optional': True, 'defaults': "['True']"}),
              ("label2On", "basic:Boolean",
                {'optional': True, 'defaults': "['False']"}),
              ("color", "basic:String",
                {'optional': True}),
              ("axes", "basic:String",
                {'optional': True}),
              ("label", "basic:String",
                {'optional': True}),
              ("labelcolor", "basic:String",
                {'optional': True}),
              ("tickdir", "basic:String",
                {'optional': True}),
              ("pad", "basic:String",
                {'optional': True}),
              ("gridOn", "basic:String",
                {'optional': True}),
              ("zorder", "basic:String",
                {'optional': True}),
              ("tick2On", "basic:Boolean",
                {'optional': True, 'defaults': "['True']"}),
              ("labelsize", "basic:String",
                {'optional': True}),
              ("width", "basic:String",
                {'optional': True}),
              ("tick1On", "basic:Boolean",
                {'optional': True, 'defaults': "['True']"}),
              ("size", "basic:String",
                {'optional': True}),
        ]

    # no output ports except self
    _output_ports = [("self", "(MplXTickProperties)")]

    def __init__(self):
        MplTickProperties.__init__(self)
        self.props = {}
        self.constructor_props = {}
        self.sub_props = {}

    def compute(self):
        MplTickProperties.compute(self)
        if self.hasInputFromPort('label1On'):
            self.constructor_props['label1On'] = self.getInputFromPort('label1On')
        if self.hasInputFromPort('loc'):
            self.constructor_props['loc'] = self.getInputFromPort('loc')
        if self.hasInputFromPort('major'):
            self.constructor_props['major'] = self.getInputFromPort('major')
        if self.hasInputFromPort('label2On'):
            self.constructor_props['label2On'] = self.getInputFromPort('label2On')
        if self.hasInputFromPort('color'):
            self.constructor_props['color'] = self.getInputFromPort('color')
        if self.hasInputFromPort('axes'):
            self.constructor_props['axes'] = self.getInputFromPort('axes')
        if self.hasInputFromPort('label'):
            self.constructor_props['label'] = self.getInputFromPort('label')
        if self.hasInputFromPort('labelcolor'):
            self.constructor_props['labelcolor'] = self.getInputFromPort('labelcolor')
        if self.hasInputFromPort('tickdir'):
            self.constructor_props['tickdir'] = self.getInputFromPort('tickdir')
        if self.hasInputFromPort('pad'):
            self.constructor_props['pad'] = self.getInputFromPort('pad')
        if self.hasInputFromPort('gridOn'):
            self.constructor_props['gridOn'] = self.getInputFromPort('gridOn')
        if self.hasInputFromPort('zorder'):
            self.constructor_props['zorder'] = self.getInputFromPort('zorder')
        if self.hasInputFromPort('tick2On'):
            self.constructor_props['tick2On'] = self.getInputFromPort('tick2On')
        if self.hasInputFromPort('labelsize'):
            self.constructor_props['labelsize'] = self.getInputFromPort('labelsize')
        if self.hasInputFromPort('width'):
            self.constructor_props['width'] = self.getInputFromPort('width')
        if self.hasInputFromPort('tick1On'):
            self.constructor_props['tick1On'] = self.getInputFromPort('tick1On')
        if self.hasInputFromPort('size'):
            self.constructor_props['size'] = self.getInputFromPort('size')

        
    def update_props(self, objs):
        matplotlib.artist.setp(objs, **self.props)

    def update_kwargs(self, kwargs):
        kwargs.update(self.constructor_props)
        kwargs.update(self.props)

class MplYTickProperties(MplTickProperties):
    """
    Contains all the Artists needed to make a Y tick - the tick line,
    the label text and the grid line
    
    """
    _input_ports = [
              ("label1On", "basic:Boolean",
                {'optional': True, 'defaults': "['True']"}),
              ("loc", "basic:String",
                {'optional': True}),
              ("major", "basic:Boolean",
                {'optional': True, 'defaults': "['True']"}),
              ("label2On", "basic:Boolean",
                {'optional': True, 'defaults': "['False']"}),
              ("color", "basic:String",
                {'optional': True}),
              ("axes", "basic:String",
                {'optional': True}),
              ("label", "basic:String",
                {'optional': True}),
              ("labelcolor", "basic:String",
                {'optional': True}),
              ("tickdir", "basic:String",
                {'optional': True}),
              ("pad", "basic:String",
                {'optional': True}),
              ("gridOn", "basic:String",
                {'optional': True}),
              ("zorder", "basic:String",
                {'optional': True}),
              ("tick2On", "basic:Boolean",
                {'optional': True, 'defaults': "['True']"}),
              ("labelsize", "basic:String",
                {'optional': True}),
              ("width", "basic:String",
                {'optional': True}),
              ("tick1On", "basic:Boolean",
                {'optional': True, 'defaults': "['True']"}),
              ("size", "basic:String",
                {'optional': True}),
        ]

    # no output ports except self
    _output_ports = [("self", "(MplYTickProperties)")]

    def __init__(self):
        MplTickProperties.__init__(self)
        self.props = {}
        self.constructor_props = {}
        self.sub_props = {}

    def compute(self):
        MplTickProperties.compute(self)
        if self.hasInputFromPort('label1On'):
            self.constructor_props['label1On'] = self.getInputFromPort('label1On')
        if self.hasInputFromPort('loc'):
            self.constructor_props['loc'] = self.getInputFromPort('loc')
        if self.hasInputFromPort('major'):
            self.constructor_props['major'] = self.getInputFromPort('major')
        if self.hasInputFromPort('label2On'):
            self.constructor_props['label2On'] = self.getInputFromPort('label2On')
        if self.hasInputFromPort('color'):
            self.constructor_props['color'] = self.getInputFromPort('color')
        if self.hasInputFromPort('axes'):
            self.constructor_props['axes'] = self.getInputFromPort('axes')
        if self.hasInputFromPort('label'):
            self.constructor_props['label'] = self.getInputFromPort('label')
        if self.hasInputFromPort('labelcolor'):
            self.constructor_props['labelcolor'] = self.getInputFromPort('labelcolor')
        if self.hasInputFromPort('tickdir'):
            self.constructor_props['tickdir'] = self.getInputFromPort('tickdir')
        if self.hasInputFromPort('pad'):
            self.constructor_props['pad'] = self.getInputFromPort('pad')
        if self.hasInputFromPort('gridOn'):
            self.constructor_props['gridOn'] = self.getInputFromPort('gridOn')
        if self.hasInputFromPort('zorder'):
            self.constructor_props['zorder'] = self.getInputFromPort('zorder')
        if self.hasInputFromPort('tick2On'):
            self.constructor_props['tick2On'] = self.getInputFromPort('tick2On')
        if self.hasInputFromPort('labelsize'):
            self.constructor_props['labelsize'] = self.getInputFromPort('labelsize')
        if self.hasInputFromPort('width'):
            self.constructor_props['width'] = self.getInputFromPort('width')
        if self.hasInputFromPort('tick1On'):
            self.constructor_props['tick1On'] = self.getInputFromPort('tick1On')
        if self.hasInputFromPort('size'):
            self.constructor_props['size'] = self.getInputFromPort('size')

        
    def update_props(self, objs):
        matplotlib.artist.setp(objs, **self.props)

    def update_kwargs(self, kwargs):
        kwargs.update(self.constructor_props)
        kwargs.update(self.props)

class MplAxisProperties(MplArtistProperties):
    """
    Public attributes

    * :attr:`axes.transData` - transform data coords to display coords
    * :attr:`axes.transAxes` - transform axis coords to display coords
    * :attr:`labelpad` - number of points between the axis and its label
    
    """
    _input_ports = [
              ("pickradius", "basic:String",
                {'optional': True, 'docstring': 'Set the depth of the axis used by the picker'}),
              ("minor_formatter", "basic:String",
                {'optional': True, 'docstring': 'Set the formatter of the minor ticker'}),
              ("smart_bounds", "basic:String",
                {'optional': True, 'docstring': 'set the axis to have smart bounds'}),
              ("ticksSequence", "basic:List",
                {'optional': True, 'docstring': 'Set the locations of the tick marks from sequence ticks'}),
              ("ticksScalar", "basic:Float",
               {'docstring': 'Set the locations of the tick marks from sequence ticks', 'optional': True}),
              ("axes", "basic:String",
                {'optional': True}),
              ("view_interval", "basic:String",
                {'optional': True}),
              ("major_locator", "basic:String",
                {'optional': True, 'docstring': 'Set the locator of the major ticker'}),
              ("major_formatter", "basic:String",
                {'optional': True, 'docstring': 'Set the formatter of the major ticker'}),
              ("ticklabelsSequence", "basic:List",
                {'optional': True, 'docstring': 'Set the text values of the tick labels. Return a list of Text instances.  Use kwarg minor=True to select minor ticks. All other kwargs are used to update the text object properties. As for get_ticklabels, label1 (left or bottom) is affected for a given tick only if its label1On attribute is True, and similarly for label2.  The list of returned label text objects consists of all such label1 objects followed by all such label2 objects.\n\nThe input ticklabels is assumed to match the set of tick locations, regardless of the state of label1On and label2On.'}),
              ("ticklabelsScalar", "basic:String",
               {'docstring': 'Set the text values of the tick labels. Return a list of Text instances.  Use kwarg minor=True to select minor ticks. All other kwargs are used to update the text object properties. As for get_ticklabels, label1 (left or bottom) is affected for a given tick only if its label1On attribute is True, and similarly for label2.  The list of returned label text objects consists of all such label1 objects followed by all such label2 objects.\n\nThe input ticklabels is assumed to match the set of tick locations, regardless of the state of label1On and label2On.', 'optional': True}),
              ("clip_path", "basic:String",
                {'optional': True}),
              ("minor_locator", "basic:String",
                {'optional': True, 'docstring': 'Set the locator of the minor ticker'}),
              ("default_intervals", "basic:String",
                {'optional': True, 'docstring': 'set the default limits for the axis data and view interval if they are not mutated'}),
              ("scale", "basic:String",
                {'optional': True}),
              ("data_interval", "basic:String",
                {'optional': True, 'docstring': 'set the axis data limits'}),
              ("label_text", "basic:String",
                {'optional': True, 'docstring': 'Sets the text value of the axis label'}),
              ("label_coords", "basic:String",
                {'optional': True, 'docstring': 'Set the coordinates of the label.  By default, the x coordinate of the y label is determined by the tick label bounding boxes, but this can lead to poor alignment of multiple ylabels if there are multiple axes.  Ditto for the y coodinate of the x label.\n\nYou can also specify the coordinate system of the label with the transform.  If None, the default coordinate system will be the axes coordinate system (0,0) is (left,bottom), (0.5, 0.5) is middle, etc'}),
              ("units", "basic:String",
                {'optional': True, 'docstring': 'set the units for axis'}),
              ("tick_params", "basic:String",
                {'optional': True, 'docstring': 'Set appearance parameters for ticks and ticklabels.\n\nFor documentation of keyword arguments, see :meth:`matplotlib.axes.Axes.tick_params`.'}),
        ]

    # no output ports except self
    _output_ports = [("self", "(MplAxisProperties)")]

    def __init__(self):
        MplArtistProperties.__init__(self)
        self.props = {}
        self.constructor_props = {}
        self.sub_props = {}

    def compute(self):
        MplArtistProperties.compute(self)
        if self.hasInputFromPort('pickradius'):
            self.props['pickradius'] = self.getInputFromPort('pickradius')
        if self.hasInputFromPort('minor_formatter'):
            self.props['minor_formatter'] = self.getInputFromPort('minor_formatter')
        if self.hasInputFromPort('smart_bounds'):
            self.props['smart_bounds'] = self.getInputFromPort('smart_bounds')
        if self.hasInputFromPort('ticksSequence'):
            self.props['ticks'] = self.getInputFromPort('ticksSequence')
        elif self.hasInputFromPort('ticksScalar'):
            self.props['ticks'] = self.getInputFromPort('ticksScalar')
        if self.hasInputFromPort('axes'):
            self.constructor_props['axes'] = self.getInputFromPort('axes')
        if self.hasInputFromPort('view_interval'):
            self.props['view_interval'] = self.getInputFromPort('view_interval')
        if self.hasInputFromPort('major_locator'):
            self.props['major_locator'] = self.getInputFromPort('major_locator')
        if self.hasInputFromPort('major_formatter'):
            self.props['major_formatter'] = self.getInputFromPort('major_formatter')
        if self.hasInputFromPort('ticklabelsSequence'):
            self.props['ticklabels'] = self.getInputFromPort('ticklabelsSequence')
        elif self.hasInputFromPort('ticklabelsScalar'):
            self.props['ticklabels'] = self.getInputFromPort('ticklabelsScalar')
        if self.hasInputFromPort('clip_path'):
            self.props['clip_path'] = self.getInputFromPort('clip_path')
        if self.hasInputFromPort('minor_locator'):
            self.props['minor_locator'] = self.getInputFromPort('minor_locator')
        if self.hasInputFromPort('default_intervals'):
            self.props['default_intervals'] = self.getInputFromPort('default_intervals')
        if self.hasInputFromPort('scale'):
            self.props['scale'] = self.getInputFromPort('scale')
        if self.hasInputFromPort('data_interval'):
            self.props['data_interval'] = self.getInputFromPort('data_interval')
        if self.hasInputFromPort('label_text'):
            self.props['label_text'] = self.getInputFromPort('label_text')
        if self.hasInputFromPort('label_coords'):
            self.props['label_coords'] = self.getInputFromPort('label_coords')
        if self.hasInputFromPort('units'):
            self.props['units'] = self.getInputFromPort('units')
        if self.hasInputFromPort('tick_params'):
            self.props['tick_params'] = self.getInputFromPort('tick_params')

        
    def update_props(self, objs):
        matplotlib.artist.setp(objs, **self.props)

    def update_kwargs(self, kwargs):
        kwargs.update(self.constructor_props)
        kwargs.update(self.props)

class MplXAxisProperties(MplAxisProperties):
    """None
    """
    _input_ports = [
              ("view_interval", "basic:String",
                {'optional': True, 'docstring': 'If ignore is False, the order of vmin, vmax does not matter; the original axis orientation will be preserved. In addition, the view limits can be expanded, but will not be reduced.  This method is for mpl internal use; for normal use, see :meth:`~matplotlib.axes.Axes.set_xlim`.'}),
              ("ticks_position", "basic:String",
                {'entry_types': "['enum']", 'docstring': "Set the ticks position (top, bottom, both, default or none) both sets the ticks to appear on both positions, but does not change the tick labels.  'default' resets the tick positions to the default: ticks on both positions, labels at bottom.  'none' can be used if you don't want any ticks. 'none' and 'both' affect only the ticks, not the labels.", 'values': "[['top', 'bottom', 'both', 'default', 'none']]", 'optional': True}),
              ("axes", "basic:String",
                {'optional': True}),
              ("label_position", "basic:String",
                {'entry_types': "['enum']", 'docstring': 'Set the label position (top or bottom)', 'values': "[['top', 'bottom']]", 'optional': True}),
              ("default_intervals", "basic:String",
                {'optional': True, 'docstring': 'set the default limits for the axis interval if they are not mutated'}),
              ("data_interval", "basic:String",
                {'optional': True, 'docstring': 'set the axis data limits'}),
              ("pickradius", "basic:Integer",
                {'optional': True, 'defaults': "['15']"}),
        ]

    # no output ports except self
    _output_ports = [("self", "(MplXAxisProperties)")]

    def __init__(self):
        MplAxisProperties.__init__(self)
        self.props = {}
        self.constructor_props = {}
        self.sub_props = {}

    def compute(self):
        MplAxisProperties.compute(self)
        if self.hasInputFromPort('view_interval'):
            self.props['view_interval'] = self.getInputFromPort('view_interval')
        if self.hasInputFromPort('ticks_position'):
            self.props['ticks_position'] = self.getInputFromPort('ticks_position')
        if self.hasInputFromPort('axes'):
            self.constructor_props['axes'] = self.getInputFromPort('axes')
        if self.hasInputFromPort('label_position'):
            self.props['label_position'] = self.getInputFromPort('label_position')
        if self.hasInputFromPort('default_intervals'):
            self.props['default_intervals'] = self.getInputFromPort('default_intervals')
        if self.hasInputFromPort('data_interval'):
            self.props['data_interval'] = self.getInputFromPort('data_interval')
        if self.hasInputFromPort('pickradius'):
            self.constructor_props['pickradius'] = self.getInputFromPort('pickradius')

        
    def update_props(self, objs):
        matplotlib.artist.setp(objs, **self.props)

    def update_kwargs(self, kwargs):
        kwargs.update(self.constructor_props)
        kwargs.update(self.props)

class MplYAxisProperties(MplAxisProperties):
    """None
    """
    _input_ports = [
              ("offset_position", "basic:String",
                {'optional': True}),
              ("view_interval", "basic:String",
                {'optional': True, 'docstring': 'If ignore is False, the order of vmin, vmax does not matter; the original axis orientation will be preserved. In addition, the view limits can be expanded, but will not be reduced.  This method is for mpl internal use; for normal use, see :meth:`~matplotlib.axes.Axes.set_ylim`.'}),
              ("ticks_position", "basic:String",
                {'entry_types': "['enum']", 'docstring': "Set the ticks position (left, right, both, default or none) 'both' sets the ticks to appear on both positions, but does not change the tick labels.  'default' resets the tick positions to the default: ticks on both positions, labels at left.  'none' can be used if you don't want any ticks. 'none' and 'both' affect only the ticks, not the labels.", 'values': "[['left', 'right', 'both', 'default', 'none']]", 'optional': True}),
              ("axes", "basic:String",
                {'optional': True}),
              ("label_position", "basic:String",
                {'entry_types': "['enum']", 'docstring': 'Set the label position (left or right)', 'values': "[['left', 'right']]", 'optional': True}),
              ("default_intervals", "basic:String",
                {'optional': True, 'docstring': 'set the default limits for the axis interval if they are not mutated'}),
              ("data_interval", "basic:String",
                {'optional': True, 'docstring': 'set the axis data limits'}),
              ("pickradius", "basic:Integer",
                {'optional': True, 'defaults': "['15']"}),
        ]

    # no output ports except self
    _output_ports = [("self", "(MplYAxisProperties)")]

    def __init__(self):
        MplAxisProperties.__init__(self)
        self.props = {}
        self.constructor_props = {}
        self.sub_props = {}

    def compute(self):
        MplAxisProperties.compute(self)
        if self.hasInputFromPort('offset_position'):
            self.props['offset_position'] = self.getInputFromPort('offset_position')
        if self.hasInputFromPort('view_interval'):
            self.props['view_interval'] = self.getInputFromPort('view_interval')
        if self.hasInputFromPort('ticks_position'):
            self.props['ticks_position'] = self.getInputFromPort('ticks_position')
        if self.hasInputFromPort('axes'):
            self.constructor_props['axes'] = self.getInputFromPort('axes')
        if self.hasInputFromPort('label_position'):
            self.props['label_position'] = self.getInputFromPort('label_position')
        if self.hasInputFromPort('default_intervals'):
            self.props['default_intervals'] = self.getInputFromPort('default_intervals')
        if self.hasInputFromPort('data_interval'):
            self.props['data_interval'] = self.getInputFromPort('data_interval')
        if self.hasInputFromPort('pickradius'):
            self.constructor_props['pickradius'] = self.getInputFromPort('pickradius')

        
    def update_props(self, objs):
        matplotlib.artist.setp(objs, **self.props)

    def update_kwargs(self, kwargs):
        kwargs.update(self.constructor_props)
        kwargs.update(self.props)

class MplLegendProperties(MplArtistProperties):
    """
    Place a legend on the axes at location loc.  Labels are a
    sequence of strings and loc can be a string or an integer
    specifying the legend location

    The location codes are::

      'best'         : 0, (only implemented for axis legends)
      'upper right'  : 1,
      'upper left'   : 2,
      'lower left'   : 3,
      'lower right'  : 4,
      'right'        : 5,
      'center left'  : 6,
      'center right' : 7,
      'lower center' : 8,
      'upper center' : 9,
      'center'       : 10,

    loc can be a tuple of the noramilzed coordinate values with
    respect its parent.

    
    """
    _input_ports = [
              ("fancybox", "basic:String",
                {'optional': True, 'docstring': 'if True, draw a frame with a round fancybox.  If None, use rc'}),
              ("handlelength", "basic:String",
                {'optional': True, 'docstring': 'the length of the legend handles'}),
              ("labels", "basic:String",
                {'optional': True}),
              ("labelspacing", "basic:String",
                {'optional': True, 'docstring': 'the vertical space between the legend entries'}),
              ("columnspacing", "basic:String",
                {'optional': True, 'docstring': 'the spacing between columns'}),
              ("handletextpad", "basic:String",
                {'optional': True, 'docstring': 'the pad between the legend handle and text'}),
              ("ncol", "basic:Integer",
                {'optional': True, 'docstring': 'number of columns', 'defaults': "['1']"}),
              ("borderaxespad", "basic:String",
                {'optional': True, 'docstring': 'the pad between the axes and legend border'}),
              ("loc", "basic:String",
                {'optional': True, 'docstring': 'a location code'}),
              ("bbox_to_anchor", "basic:String",
                {'optional': True, 'docstring': 'set the bbox that the legend will be anchored.\n\nbbox can be a BboxBase instance, a tuple of [left, bottom, width, height] in the given transform (normalized axes coordinate if None), or a tuple of [left, bottom] where the width and height will be assumed to be zero.'}),
              ("title", "basic:String",
                {'optional': True, 'docstring': 'set the legend title'}),
              ("handletextsep", "basic:String",
                {'optional': True}),
              ("numpoints", "basic:String",
                {'optional': True, 'docstring': 'the number of points in the legend for line'}),
              ("prop", "basic:String",
                {'optional': True, 'docstring': 'the font property'}),
              ("handles", "basic:String",
                {'optional': True}),
              ("pad", "basic:String",
                {'optional': True}),
              ("borderpad", "basic:String",
                {'optional': True, 'docstring': 'the fractional whitespace inside the legend border'}),
              ("parent", "basic:String",
                {'optional': True}),
              ("axespad", "basic:String",
                {'optional': True}),
              ("labelsep", "basic:String",
                {'optional': True}),
              ("frame_on", "basic:Boolean",
                {'optional': True, 'docstring': 'Set whether the legend box patch is drawn'}),
              ("scatterpoints", "basic:Integer",
                {'optional': True, 'docstring': 'the number of points in the legend for scatter plot', 'defaults': "['3']"}),
              ("shadow", "basic:String",
                {'optional': True, 'docstring': 'if True, draw a shadow behind legend'}),
              ("handler_map", "basic:String",
                {'optional': True}),
              ("handleheight", "basic:String",
                {'optional': True, 'docstring': 'the length of the legend handles'}),
              ("scatteryoffsets", "basic:List",
                {'optional': True, 'docstring': 'a list of yoffsets for scatter symbols in legend'}),
              ("markerscale", "basic:String",
                {'optional': True, 'docstring': 'the relative size of legend markers vs. original'}),
              ("frameon", "basic:String",
                {'optional': True, 'docstring': 'if True, draw a frame around the legend. If None, use rc'}),
              ("mode", "basic:String",
                {'optional': True}),
              ("handlelen", "basic:String",
                {'optional': True}),
              ("default_handler_map", "basic:String",
                {'optional': True, 'docstring': 'A class method to set the default handler map.'}),
              ("bbox_transform", "basic:String",
                {'optional': True, 'docstring': 'the transform for the bbox. transAxes if None.'}),
        ]

    # no output ports except self
    _output_ports = [("self", "(MplLegendProperties)")]

    def __init__(self):
        MplArtistProperties.__init__(self)
        self.props = {}
        self.constructor_props = {}
        self.sub_props = {}

    def compute(self):
        MplArtistProperties.compute(self)
        if self.hasInputFromPort('fancybox'):
            self.constructor_props['fancybox'] = self.getInputFromPort('fancybox')
        if self.hasInputFromPort('handlelength'):
            self.constructor_props['handlelength'] = self.getInputFromPort('handlelength')
        if self.hasInputFromPort('labels'):
            self.constructor_props['labels'] = self.getInputFromPort('labels')
        if self.hasInputFromPort('labelspacing'):
            self.constructor_props['labelspacing'] = self.getInputFromPort('labelspacing')
        if self.hasInputFromPort('columnspacing'):
            self.constructor_props['columnspacing'] = self.getInputFromPort('columnspacing')
        if self.hasInputFromPort('handletextpad'):
            self.constructor_props['handletextpad'] = self.getInputFromPort('handletextpad')
        if self.hasInputFromPort('ncol'):
            self.constructor_props['ncol'] = self.getInputFromPort('ncol')
        if self.hasInputFromPort('borderaxespad'):
            self.constructor_props['borderaxespad'] = self.getInputFromPort('borderaxespad')
        if self.hasInputFromPort('loc'):
            self.constructor_props['loc'] = self.getInputFromPort('loc')
        if self.hasInputFromPort('bbox_to_anchor'):
            self.props['bbox_to_anchor'] = self.getInputFromPort('bbox_to_anchor')
        if self.hasInputFromPort('title'):
            self.props['title'] = self.getInputFromPort('title')
        if self.hasInputFromPort('handletextsep'):
            self.constructor_props['handletextsep'] = self.getInputFromPort('handletextsep')
        if self.hasInputFromPort('numpoints'):
            self.constructor_props['numpoints'] = self.getInputFromPort('numpoints')
        if self.hasInputFromPort('prop'):
            self.constructor_props['prop'] = self.getInputFromPort('prop')
        if self.hasInputFromPort('handles'):
            self.constructor_props['handles'] = self.getInputFromPort('handles')
        if self.hasInputFromPort('pad'):
            self.constructor_props['pad'] = self.getInputFromPort('pad')
        if self.hasInputFromPort('borderpad'):
            self.constructor_props['borderpad'] = self.getInputFromPort('borderpad')
        if self.hasInputFromPort('parent'):
            self.constructor_props['parent'] = self.getInputFromPort('parent')
        if self.hasInputFromPort('axespad'):
            self.constructor_props['axespad'] = self.getInputFromPort('axespad')
        if self.hasInputFromPort('labelsep'):
            self.constructor_props['labelsep'] = self.getInputFromPort('labelsep')
        if self.hasInputFromPort('frame_on'):
            self.props['frame_on'] = self.getInputFromPort('frame_on')
        if self.hasInputFromPort('scatterpoints'):
            self.constructor_props['scatterpoints'] = self.getInputFromPort('scatterpoints')
        if self.hasInputFromPort('shadow'):
            self.constructor_props['shadow'] = self.getInputFromPort('shadow')
        if self.hasInputFromPort('handler_map'):
            self.constructor_props['handler_map'] = self.getInputFromPort('handler_map')
        if self.hasInputFromPort('handleheight'):
            self.constructor_props['handleheight'] = self.getInputFromPort('handleheight')
        if self.hasInputFromPort('scatteryoffsets'):
            self.constructor_props['scatteryoffsets'] = self.getInputFromPort('scatteryoffsets')
        if self.hasInputFromPort('markerscale'):
            self.constructor_props['markerscale'] = self.getInputFromPort('markerscale')
        if self.hasInputFromPort('frameon'):
            self.constructor_props['frameon'] = self.getInputFromPort('frameon')
        if self.hasInputFromPort('mode'):
            self.constructor_props['mode'] = self.getInputFromPort('mode')
        if self.hasInputFromPort('handlelen'):
            self.constructor_props['handlelen'] = self.getInputFromPort('handlelen')
        if self.hasInputFromPort('default_handler_map'):
            self.props['default_handler_map'] = self.getInputFromPort('default_handler_map')
        if self.hasInputFromPort('bbox_transform'):
            self.constructor_props['bbox_transform'] = self.getInputFromPort('bbox_transform')

        
    def update_props(self, objs):
        matplotlib.artist.setp(objs, **self.props)

    def update_kwargs(self, kwargs):
        kwargs.update(self.constructor_props)
        kwargs.update(self.props)

class MplAxesProperties(MplArtistProperties):
    """
    The :class:`Axes` contains most of the figure elements:
    :class:`~matplotlib.axis.Axis`, :class:`~matplotlib.axis.Tick`,
    :class:`~matplotlib.lines.Line2D`, :class:`~matplotlib.text.Text`,
    :class:`~matplotlib.patches.Polygon`, etc., and sets the
    coordinate system.

    The :class:`Axes` instance supports callbacks through a callbacks
    attribute which is a :class:`~matplotlib.cbook.CallbackRegistry`
    instance.  The events you can connect to are 'xlim_changed' and
    'ylim_changed' and the callback will be called with func(*ax*)
    where *ax* is the :class:`Axes` instance.
    
    """
    _input_ports = [
              ("adjustable", "basic:String",
                {'entry_types': "['enum']", 'values': "[['box', 'datalim', 'box-forced']]", 'optional': True}),
              ("cursor_props", "basic:Float",
                {'optional': True, 'docstring': 'Set the cursor property as:\n\nax.set_cursor_props(linewidth, color)\n\nor:\n\nax.set_cursor_props((linewidth, color))'}),
              ("figure", "basic:String",
                {'optional': True, 'docstring': 'Set the class:~matplotlib.axes.Axes figure\n\naccepts a class:~matplotlib.figure.Figure instance'}),
              ("yscale", "basic:String",
                {'optional': True, 'docstring': "call signature:\n\nset_yscale(value)\n\nSet the scaling of the y-axis: 'linear' | 'log' | 'symlog' Different kwargs are accepted, depending on the scale: 'linear'\n\n'log'\n\n\n\n'symlog'"}),
              ("navigate", "basic:Boolean",
                {'optional': True, 'docstring': 'Set whether the axes responds to navigation toolbar commands'}),
              ("aspect", "basic:String",
                {'entry_types': "['enum']", 'docstring': "aspect\n\n\n\nadjustable\n\n\n\n'box' does not allow axes sharing, as this can cause unintended side effect. For cases when sharing axes is fine, use 'box-forced'.\n\nanchor", 'values': "[['auto', 'normal', 'equal', 'num']]", 'optional': True}),
              ("axis_bgcolor", "basic:Color",
                {'optional': True, 'docstring': 'set the axes background color'}),
              ("ylimSequence", "basic:List",
                {'optional': True, 'docstring': 'call signature:\n\nset_ylim(self, *args, **kwargs):\n\nSet the data limits for the yaxis\n\nExamples:\n\nset_ylim((bottom, top)) set_ylim(bottom, top) set_ylim(bottom=1) # top unchanged set_ylim(top=1) # bottom unchanged\n\nKeyword arguments:\n\n\n\nNote: the bottom (formerly ymin) value may be greater than the top (formerly ymax). For example, suppose y is depth in the ocean. Then one might use:\n\nset_ylim(5000, 0)\n\nso 5000 m depth is at the bottom of the plot and the surface, 0 m, is at the top.\n\nReturns the current ylimits as a length 2 tuple'}),
              ("ylimScalar", "basic:Float",
               {'docstring': 'call signature:\n\nset_ylim(self, *args, **kwargs):\n\nSet the data limits for the yaxis\n\nExamples:\n\nset_ylim((bottom, top)) set_ylim(bottom, top) set_ylim(bottom=1) # top unchanged set_ylim(top=1) # bottom unchanged\n\nKeyword arguments:\n\n\n\nNote: the bottom (formerly ymin) value may be greater than the top (formerly ymax). For example, suppose y is depth in the ocean. Then one might use:\n\nset_ylim(5000, 0)\n\nso 5000 m depth is at the bottom of the plot and the surface, 0 m, is at the top.\n\nReturns the current ylimits as a length 2 tuple', 'optional': True}),
              ("sharey", "basic:String",
                {'optional': True}),
              ("xlimSequence", "basic:List",
                {'optional': True, 'docstring': 'call signature:\n\nset_xlim(self, *args, **kwargs):\n\nSet the data limits for the xaxis\n\nExamples:\n\nset_xlim((left, right)) set_xlim(left, right) set_xlim(left=1) # right unchanged set_xlim(right=1) # left unchanged\n\nKeyword arguments:\n\n\n\nNote: the left (formerly xmin) value may be greater than the right (formerly xmax). For example, suppose x is years before present. Then one might use:\n\nset_ylim(5000, 0)\n\nso 5000 years ago is on the left of the plot and the present is on the right.\n\nReturns the current xlimits as a length 2 tuple'}),
              ("xlimScalar", "basic:Float",
               {'docstring': 'call signature:\n\nset_xlim(self, *args, **kwargs):\n\nSet the data limits for the xaxis\n\nExamples:\n\nset_xlim((left, right)) set_xlim(left, right) set_xlim(left=1) # right unchanged set_xlim(right=1) # left unchanged\n\nKeyword arguments:\n\n\n\nNote: the left (formerly xmin) value may be greater than the right (formerly xmax). For example, suppose x is years before present. Then one might use:\n\nset_ylim(5000, 0)\n\nso 5000 years ago is on the left of the plot and the present is on the right.\n\nReturns the current xlimits as a length 2 tuple', 'optional': True}),
              ("axis_on", "basic:String",
                {'optional': True, 'docstring': 'turn on the axis'}),
              ("title", "basic:String",
                {'optional': True, 'docstring': 'call signature:\n\nset_title(label, fontdict=None, **kwargs):\n\nSet the title for the axes.'}),
              ("axisbg", "basic:String",
                {'optional': True}),
              ("label", "basic:String",
                {'optional': True, 'defaults': "['']"}),
              ("xticksSequence", "basic:List",
                {'optional': True, 'docstring': 'Set the x ticks with list of ticks'}),
              ("xticksScalar", "basic:Float",
               {'docstring': 'Set the x ticks with list of ticks', 'optional': True}),
              ("fig", "basic:String",
                {'optional': True}),
              ("ylabel", "basic:String",
                {'optional': True, 'docstring': 'call signature:\n\nset_ylabel(ylabel, fontdict=None, labelpad=None, **kwargs)\n\nSet the label for the yaxis\n\nlabelpad is the spacing in points between the label and the y-axis'}),
              ("autoscalex_on", "basic:Boolean",
                {'optional': True, 'docstring': 'Set whether autoscaling for the x-axis is applied on plot commands'}),
              ("rasterization_zorder", "basic:String",
                {'optional': True, 'docstring': 'Set zorder value below which artists will be rasterized'}),
              ("axes_locator", "basic:String",
                {'optional': True, 'docstring': 'set axes_locator'}),
              ("axisbelow", "basic:Boolean",
                {'optional': True, 'docstring': 'Set whether the axis ticks and gridlines are above or below most artists'}),
              ("frame_on", "basic:Boolean",
                {'optional': True, 'docstring': 'Set whether the axes rectangle patch is drawn'}),
              ("navigate_mode", "basic:String",
                {'optional': True, 'docstring': 'Set the navigation toolbar button status;\n\nthis is not a user-API function.'}),
              ("xscale", "basic:String",
                {'optional': True, 'docstring': "call signature:\n\nset_xscale(value)\n\nSet the scaling of the x-axis: 'linear' | 'log' | 'symlog' Different kwargs are accepted, depending on the scale: 'linear'\n\n'log'\n\n\n\n'symlog'"}),
              ("axis_off", "basic:String",
                {'optional': True, 'docstring': 'turn off the axis'}),
              ("autoscale_on", "basic:Boolean",
                {'optional': True, 'docstring': 'Set whether autoscaling is applied on plot commands'}),
              ("ybound", "basic:String",
                {'optional': True}),
              ("rect", "basic:String",
                {'optional': True}),
              ("sharex", "basic:String",
                {'optional': True}),
              ("yticklabelsSequence", "basic:List",
                {'optional': True, 'docstring': "call signature:\n\nset_yticklabels(labels, fontdict=None, minor=False, **kwargs)\n\nSet the ytick labels with list of strings labels.  Return a list of :class:`~matplotlib.text.Text` instances.\n\nkwargs set :class:`~matplotlib.text.Text` properties for the labels. Valid properties are\n\nagg_filter: unknown alpha: float (0.0 transparent through 1.0 opaque) animated: [True | False] axes: an :class:`~matplotlib.axes.Axes` instance backgroundcolor: any matplotlib color bbox: rectangle prop dict clip_box: a :class:`matplotlib.transforms.Bbox` instance clip_on: [True | False] clip_path: [ (:class:`~matplotlib.path.Path`,         :class:`~matplotlib.transforms.Transform`) |         :class:`~matplotlib.patches.Patch` | None ] color: any matplotlib color contains: a callable function family or fontfamily or fontname or name: [ FONTNAME | 'serif' | 'sans-serif' | 'cursive' | 'fantasy' | 'monospace' ] figure: a :class:`matplotlib.figure.Figure` instance fontproperties or font_properties: a :class:`matplotlib.font_manager.FontProperties` instance gid: an id string horizontalalignment or ha: [ 'center' | 'right' | 'left' ] label: any string linespacing: float (multiple of font size) lod: [True | False] multialignment: ['left' | 'right' | 'center' ] path_effects: unknown picker: [None|float|boolean|callable] position: (x,y) rasterized: [True | False | None] rotation: [ angle in degrees | 'vertical' | 'horizontal' ] rotation_mode: unknown size or fontsize: [ size in points | 'xx-small' | 'x-small' | 'small' | 'medium' | 'large' | 'x-large' | 'xx-large' ] snap: unknown stretch or fontstretch: [ a numeric value in range 0-1000 | 'ultra-condensed' | 'extra-condensed' | 'condensed' | 'semi-condensed' | 'normal' | 'semi-expanded' | 'expanded' | 'extra-expanded' | 'ultra-expanded' ] style or fontstyle: [ 'normal' | 'italic' | 'oblique'] text: string or anything printable with '%s' conversion. transform: :class:`~matplotlib.transforms.Transform` instance url: a url string variant or fontvariant: [ 'normal' | 'small-caps' ] verticalalignment or va or ma: [ 'center' | 'top' | 'bottom' | 'baseline' ] visible: [True | False] weight or fontweight: [ a numeric value in range 0-1000 | 'ultralight' | 'light' | 'normal' | 'regular' | 'book' | 'medium' | 'roman' | 'semibold' | 'demibold' | 'demi' | 'bold' | 'heavy' | 'extra bold' | 'black' ] x: float y: float zorder: any number"}),
              ("yticklabelsScalar", "basic:String",
               {'docstring': "call signature:\n\nset_yticklabels(labels, fontdict=None, minor=False, **kwargs)\n\nSet the ytick labels with list of strings labels.  Return a list of :class:`~matplotlib.text.Text` instances.\n\nkwargs set :class:`~matplotlib.text.Text` properties for the labels. Valid properties are\n\nagg_filter: unknown alpha: float (0.0 transparent through 1.0 opaque) animated: [True | False] axes: an :class:`~matplotlib.axes.Axes` instance backgroundcolor: any matplotlib color bbox: rectangle prop dict clip_box: a :class:`matplotlib.transforms.Bbox` instance clip_on: [True | False] clip_path: [ (:class:`~matplotlib.path.Path`,         :class:`~matplotlib.transforms.Transform`) |         :class:`~matplotlib.patches.Patch` | None ] color: any matplotlib color contains: a callable function family or fontfamily or fontname or name: [ FONTNAME | 'serif' | 'sans-serif' | 'cursive' | 'fantasy' | 'monospace' ] figure: a :class:`matplotlib.figure.Figure` instance fontproperties or font_properties: a :class:`matplotlib.font_manager.FontProperties` instance gid: an id string horizontalalignment or ha: [ 'center' | 'right' | 'left' ] label: any string linespacing: float (multiple of font size) lod: [True | False] multialignment: ['left' | 'right' | 'center' ] path_effects: unknown picker: [None|float|boolean|callable] position: (x,y) rasterized: [True | False | None] rotation: [ angle in degrees | 'vertical' | 'horizontal' ] rotation_mode: unknown size or fontsize: [ size in points | 'xx-small' | 'x-small' | 'small' | 'medium' | 'large' | 'x-large' | 'xx-large' ] snap: unknown stretch or fontstretch: [ a numeric value in range 0-1000 | 'ultra-condensed' | 'extra-condensed' | 'condensed' | 'semi-condensed' | 'normal' | 'semi-expanded' | 'expanded' | 'extra-expanded' | 'ultra-expanded' ] style or fontstyle: [ 'normal' | 'italic' | 'oblique'] text: string or anything printable with '%s' conversion. transform: :class:`~matplotlib.transforms.Transform` instance url: a url string variant or fontvariant: [ 'normal' | 'small-caps' ] verticalalignment or va or ma: [ 'center' | 'top' | 'bottom' | 'baseline' ] visible: [True | False] weight or fontweight: [ a numeric value in range 0-1000 | 'ultralight' | 'light' | 'normal' | 'regular' | 'book' | 'medium' | 'roman' | 'semibold' | 'demibold' | 'demi' | 'bold' | 'heavy' | 'extra bold' | 'black' ] x: float y: float zorder: any number", 'optional': True}),
              ("autoscaley_on", "basic:Boolean",
                {'optional': True, 'docstring': 'Set whether autoscaling for the y-axis is applied on plot commands'}),
              ("xmargin", "basic:Float",
                {'optional': True, 'docstring': 'Set padding of X data limits prior to autoscaling.\n\nm times the data interval will be added to each end of that interval before it is used in autoscaling.'}),
              ("color_cycle", "basic:Color",
                {'optional': True, 'docstring': 'Set the color cycle for any future plot commands on this Axes.\n\nclist is a list of mpl color specifiers.'}),
              ("frameon", "basic:Boolean",
                {'optional': True, 'defaults': "['True']"}),
              ("xlabel", "basic:String",
                {'optional': True, 'docstring': 'call signature:\n\nset_xlabel(xlabel, fontdict=None, labelpad=None, **kwargs)\n\nSet the label for the xaxis.\n\nlabelpad is the spacing in points between the label and the x-axis'}),
              ("xbound", "basic:String",
                {'optional': True, 'docstring': 'Set the lower and upper numerical bounds of the x-axis. This method will honor axes inversion regardless of parameter order. It will not change the _autoscaleXon attribute.'}),
              ("yticksSequence", "basic:List",
                {'optional': True, 'docstring': 'Set the y ticks with list of ticks Keyword arguments:'}),
              ("yticksScalar", "basic:Float",
               {'docstring': 'Set the y ticks with list of ticks Keyword arguments:', 'optional': True}),
              ("ymargin", "basic:Float",
                {'optional': True, 'docstring': 'Set padding of Y data limits prior to autoscaling.\n\nm times the data interval will be added to each end of that interval before it is used in autoscaling.'}),
              ("position", "basic:String",
                {'optional': True, 'docstring': 'Set the axes position with:\n\npos = [left, bottom, width, height]\n\nin relative 0,1 coords, or pos can be a :class:`~matplotlib.transforms.Bbox`\n\nThere are two position variables: one which is ultimately used, but which may be modified by :meth:`apply_aspect`, and a second which is the starting point for :meth:`apply_aspect`.'}),
              ("anchor", "basic:String",
                {'docstring': 'anchor', 'values': "[['Center', 'bottom left', 'bottom', 'bottom right', 'right', 'top right', 'top', 'top left', 'left']]", 'optional': True}),
              ("xticklabelsSequence", "basic:List",
                {'optional': True, 'docstring': "call signature:\n\nset_xticklabels(labels, fontdict=None, minor=False, **kwargs)\n\nSet the xtick labels with list of strings labels. Return a list of axis text instances.\n\nkwargs set the :class:`~matplotlib.text.Text` properties. Valid properties are\n\nagg_filter: unknown alpha: float (0.0 transparent through 1.0 opaque) animated: [True | False] axes: an :class:`~matplotlib.axes.Axes` instance backgroundcolor: any matplotlib color bbox: rectangle prop dict clip_box: a :class:`matplotlib.transforms.Bbox` instance clip_on: [True | False] clip_path: [ (:class:`~matplotlib.path.Path`,         :class:`~matplotlib.transforms.Transform`) |         :class:`~matplotlib.patches.Patch` | None ] color: any matplotlib color contains: a callable function family or fontfamily or fontname or name: [ FONTNAME | 'serif' | 'sans-serif' | 'cursive' | 'fantasy' | 'monospace' ] figure: a :class:`matplotlib.figure.Figure` instance fontproperties or font_properties: a :class:`matplotlib.font_manager.FontProperties` instance gid: an id string horizontalalignment or ha: [ 'center' | 'right' | 'left' ] label: any string linespacing: float (multiple of font size) lod: [True | False] multialignment: ['left' | 'right' | 'center' ] path_effects: unknown picker: [None|float|boolean|callable] position: (x,y) rasterized: [True | False | None] rotation: [ angle in degrees | 'vertical' | 'horizontal' ] rotation_mode: unknown size or fontsize: [ size in points | 'xx-small' | 'x-small' | 'small' | 'medium' | 'large' | 'x-large' | 'xx-large' ] snap: unknown stretch or fontstretch: [ a numeric value in range 0-1000 | 'ultra-condensed' | 'extra-condensed' | 'condensed' | 'semi-condensed' | 'normal' | 'semi-expanded' | 'expanded' | 'extra-expanded' | 'ultra-expanded' ] style or fontstyle: [ 'normal' | 'italic' | 'oblique'] text: string or anything printable with '%s' conversion. transform: :class:`~matplotlib.transforms.Transform` instance url: a url string variant or fontvariant: [ 'normal' | 'small-caps' ] verticalalignment or va or ma: [ 'center' | 'top' | 'bottom' | 'baseline' ] visible: [True | False] weight or fontweight: [ a numeric value in range 0-1000 | 'ultralight' | 'light' | 'normal' | 'regular' | 'book' | 'medium' | 'roman' | 'semibold' | 'demibold' | 'demi' | 'bold' | 'heavy' | 'extra bold' | 'black' ] x: float y: float zorder: any number"}),
              ("xticklabelsScalar", "basic:String",
               {'docstring': "call signature:\n\nset_xticklabels(labels, fontdict=None, minor=False, **kwargs)\n\nSet the xtick labels with list of strings labels. Return a list of axis text instances.\n\nkwargs set the :class:`~matplotlib.text.Text` properties. Valid properties are\n\nagg_filter: unknown alpha: float (0.0 transparent through 1.0 opaque) animated: [True | False] axes: an :class:`~matplotlib.axes.Axes` instance backgroundcolor: any matplotlib color bbox: rectangle prop dict clip_box: a :class:`matplotlib.transforms.Bbox` instance clip_on: [True | False] clip_path: [ (:class:`~matplotlib.path.Path`,         :class:`~matplotlib.transforms.Transform`) |         :class:`~matplotlib.patches.Patch` | None ] color: any matplotlib color contains: a callable function family or fontfamily or fontname or name: [ FONTNAME | 'serif' | 'sans-serif' | 'cursive' | 'fantasy' | 'monospace' ] figure: a :class:`matplotlib.figure.Figure` instance fontproperties or font_properties: a :class:`matplotlib.font_manager.FontProperties` instance gid: an id string horizontalalignment or ha: [ 'center' | 'right' | 'left' ] label: any string linespacing: float (multiple of font size) lod: [True | False] multialignment: ['left' | 'right' | 'center' ] path_effects: unknown picker: [None|float|boolean|callable] position: (x,y) rasterized: [True | False | None] rotation: [ angle in degrees | 'vertical' | 'horizontal' ] rotation_mode: unknown size or fontsize: [ size in points | 'xx-small' | 'x-small' | 'small' | 'medium' | 'large' | 'x-large' | 'xx-large' ] snap: unknown stretch or fontstretch: [ a numeric value in range 0-1000 | 'ultra-condensed' | 'extra-condensed' | 'condensed' | 'semi-condensed' | 'normal' | 'semi-expanded' | 'expanded' | 'extra-expanded' | 'ultra-expanded' ] style or fontstyle: [ 'normal' | 'italic' | 'oblique'] text: string or anything printable with '%s' conversion. transform: :class:`~matplotlib.transforms.Transform` instance url: a url string variant or fontvariant: [ 'normal' | 'small-caps' ] verticalalignment or va or ma: [ 'center' | 'top' | 'bottom' | 'baseline' ] visible: [True | False] weight or fontweight: [ a numeric value in range 0-1000 | 'ultralight' | 'light' | 'normal' | 'regular' | 'book' | 'medium' | 'roman' | 'semibold' | 'demibold' | 'demi' | 'bold' | 'heavy' | 'extra bold' | 'black' ] x: float y: float zorder: any number", 'optional': True}),
              ("titleProperties", "MplTextProperties",
                {}),
        ]

    # no output ports except self
    _output_ports = [("self", "(MplAxesProperties)")]

    def __init__(self):
        MplArtistProperties.__init__(self)
        self.props = {}
        self.constructor_props = {}
        self.sub_props = {}

    def compute(self):
        MplArtistProperties.compute(self)
        if self.hasInputFromPort('adjustable'):
            self.props['adjustable'] = self.getInputFromPort('adjustable')
        if self.hasInputFromPort('cursor_props'):
            self.props['cursor_props'] = self.getInputFromPort('cursor_props')
        if self.hasInputFromPort('figure'):
            self.props['figure'] = self.getInputFromPort('figure')
        if self.hasInputFromPort('yscale'):
            self.props['yscale'] = self.getInputFromPort('yscale')
        if self.hasInputFromPort('navigate'):
            self.props['navigate'] = self.getInputFromPort('navigate')
        if self.hasInputFromPort('aspect'):
            self.props['aspect'] = self.getInputFromPort('aspect')
        if self.hasInputFromPort('axis_bgcolor'):
            self.props['axis_bgcolor'] = self.getInputFromPort('axis_bgcolor')
            self.props['axis_bgcolor'] = translate_color(self.props['axis_bgcolor'])
        if self.hasInputFromPort('ylimSequence'):
            self.props['ylim'] = self.getInputFromPort('ylimSequence')
        elif self.hasInputFromPort('ylimScalar'):
            self.props['ylim'] = self.getInputFromPort('ylimScalar')
        if self.hasInputFromPort('sharey'):
            self.constructor_props['sharey'] = self.getInputFromPort('sharey')
        if self.hasInputFromPort('xlimSequence'):
            self.props['xlim'] = self.getInputFromPort('xlimSequence')
        elif self.hasInputFromPort('xlimScalar'):
            self.props['xlim'] = self.getInputFromPort('xlimScalar')
        if self.hasInputFromPort('axis_on'):
            self.props['axis_on'] = self.getInputFromPort('axis_on')
        if self.hasInputFromPort('title'):
            self.props['title'] = self.getInputFromPort('title')
        if self.hasInputFromPort('axisbg'):
            self.constructor_props['axisbg'] = self.getInputFromPort('axisbg')
        if self.hasInputFromPort('label'):
            self.constructor_props['label'] = self.getInputFromPort('label')
        if self.hasInputFromPort('xticksSequence'):
            self.props['xticks'] = self.getInputFromPort('xticksSequence')
        elif self.hasInputFromPort('xticksScalar'):
            self.props['xticks'] = self.getInputFromPort('xticksScalar')
        if self.hasInputFromPort('fig'):
            self.constructor_props['fig'] = self.getInputFromPort('fig')
        if self.hasInputFromPort('ylabel'):
            self.props['ylabel'] = self.getInputFromPort('ylabel')
        if self.hasInputFromPort('autoscalex_on'):
            self.props['autoscalex_on'] = self.getInputFromPort('autoscalex_on')
        if self.hasInputFromPort('rasterization_zorder'):
            self.props['rasterization_zorder'] = self.getInputFromPort('rasterization_zorder')
        if self.hasInputFromPort('axes_locator'):
            self.props['axes_locator'] = self.getInputFromPort('axes_locator')
        if self.hasInputFromPort('axisbelow'):
            self.props['axisbelow'] = self.getInputFromPort('axisbelow')
        if self.hasInputFromPort('frame_on'):
            self.props['frame_on'] = self.getInputFromPort('frame_on')
        if self.hasInputFromPort('navigate_mode'):
            self.props['navigate_mode'] = self.getInputFromPort('navigate_mode')
        if self.hasInputFromPort('xscale'):
            self.props['xscale'] = self.getInputFromPort('xscale')
        if self.hasInputFromPort('axis_off'):
            self.props['axis_off'] = self.getInputFromPort('axis_off')
        if self.hasInputFromPort('autoscale_on'):
            self.props['autoscale_on'] = self.getInputFromPort('autoscale_on')
        if self.hasInputFromPort('ybound'):
            self.props['ybound'] = self.getInputFromPort('ybound')
        if self.hasInputFromPort('rect'):
            self.constructor_props['rect'] = self.getInputFromPort('rect')
        if self.hasInputFromPort('sharex'):
            self.constructor_props['sharex'] = self.getInputFromPort('sharex')
        if self.hasInputFromPort('yticklabelsSequence'):
            self.props['yticklabels'] = self.getInputFromPort('yticklabelsSequence')
        elif self.hasInputFromPort('yticklabelsScalar'):
            self.props['yticklabels'] = self.getInputFromPort('yticklabelsScalar')
        if self.hasInputFromPort('autoscaley_on'):
            self.props['autoscaley_on'] = self.getInputFromPort('autoscaley_on')
        if self.hasInputFromPort('xmargin'):
            self.props['xmargin'] = self.getInputFromPort('xmargin')
        if self.hasInputFromPort('color_cycle'):
            self.props['color_cycle'] = self.getInputFromPort('color_cycle')
            self.props['color_cycle'] = translate_color(self.props['color_cycle'])
        if self.hasInputFromPort('frameon'):
            self.constructor_props['frameon'] = self.getInputFromPort('frameon')
        if self.hasInputFromPort('xlabel'):
            self.props['xlabel'] = self.getInputFromPort('xlabel')
        if self.hasInputFromPort('xbound'):
            self.props['xbound'] = self.getInputFromPort('xbound')
        if self.hasInputFromPort('yticksSequence'):
            self.props['yticks'] = self.getInputFromPort('yticksSequence')
        elif self.hasInputFromPort('yticksScalar'):
            self.props['yticks'] = self.getInputFromPort('yticksScalar')
        if self.hasInputFromPort('ymargin'):
            self.props['ymargin'] = self.getInputFromPort('ymargin')
        if self.hasInputFromPort('position'):
            self.props['position'] = self.getInputFromPort('position')
        if self.hasInputFromPort('anchor'):
            self.props['anchor'] = self.getInputFromPort('anchor')
            self.props['anchor'] = translate_MplAxesProperties_anchor(self.props['anchor'])
        if self.hasInputFromPort('xticklabelsSequence'):
            self.props['xticklabels'] = self.getInputFromPort('xticklabelsSequence')
        elif self.hasInputFromPort('xticklabelsScalar'):
            self.props['xticklabels'] = self.getInputFromPort('xticklabelsScalar')
        if self.hasInputFromPort('titleProperties'):
            self.sub_props['title'] = self.getInputFromPort('titleProperties')

        
    def update_props(self, objs):
        matplotlib.artist.setp(objs, **self.props)
        if not matplotlib.cbook.iterable(objs):
            objs = [objs]
        else:
            objs = matplotlib.cbook.flatten(objs)
        for obj in objs:
            if 'title' in self.sub_props:
                self.sub_props['title'].update_props(obj.title)

    def update_kwargs(self, kwargs):
        kwargs.update(self.constructor_props)
        kwargs.update(self.props)

class MplAxesSubplotProperties(MplAxesProperties):
    """None
    """
    _input_ports = [
              ("fig", "basic:String",
                {'optional': True}),
        ]

    # no output ports except self
    _output_ports = [("self", "(MplAxesSubplotProperties)")]

    def __init__(self):
        MplAxesProperties.__init__(self)
        self.props = {}
        self.constructor_props = {}
        self.sub_props = {}

    def compute(self):
        MplAxesProperties.compute(self)
        if self.hasInputFromPort('fig'):
            self.constructor_props['fig'] = self.getInputFromPort('fig')

        
    def update_props(self, objs):
        matplotlib.artist.setp(objs, **self.props)

    def update_kwargs(self, kwargs):
        kwargs.update(self.constructor_props)
        kwargs.update(self.props)

class MplFigureProperties(MplArtistProperties):
    """
    The Figure instance supports callbacks through a *callbacks*
    attribute which is a :class:`matplotlib.cbook.CallbackRegistry`
    instance.  The events you can connect to are 'dpi_changed', and
    the callback will be called with ``func(fig)`` where fig is the
    :class:`Figure` instance.

    *patch*
       The figure patch is drawn by a
       :class:`matplotlib.patches.Rectangle` instance

    *suppressComposite*
       For multiple figure images, the figure will make composite
       images depending on the renderer option_image_nocomposite
       function.  If suppressComposite is True|False, this will
       override the renderer
    
    """
    _input_ports = [
              ("edgecolor", "basic:Color",
                {'optional': True, 'docstring': 'Set the edge color of the Figure rectangle'}),
              ("canvas", "basic:String",
                {'optional': True, 'docstring': 'Set the canvas the contains the figure'}),
              ("facecolor", "basic:Color",
                {'optional': True, 'docstring': 'Set the face color of the Figure rectangle'}),
              ("size_inches", "basic:String",
                {'optional': True, 'docstring': 'set_size_inches(w,h, forward=False)\n\nSet the figure size in inches\n\nUsage:\n\nfig.set_size_inches(w,h)  # OR fig.set_size_inches((w,h) )\n\noptional kwarg forward=True will cause the canvas size to be automatically updated; eg you can resize the figure window from the shell'}),
              ("figwidth", "basic:Float",
                {'optional': True, 'docstring': 'Set the width of the figure in inches'}),
              ("frameon", "basic:Boolean",
                {'optional': True, 'docstring': 'Set whether the figure frame (background) is displayed or invisible'}),
              ("subplotpars", "basic:String",
                {'optional': True}),
              ("figheight", "basic:Float",
                {'optional': True, 'docstring': 'Set the height of the figure in inches'}),
              ("figsize", "basic:String",
                {'optional': True}),
              ("linewidth", "basic:Float",
                {'optional': True, 'defaults': "['0.0']"}),
              ("dpi", "basic:Float",
                {'optional': True, 'docstring': 'Set the dots-per-inch of the figure'}),
        ]

    # no output ports except self
    _output_ports = [("self", "(MplFigureProperties)")]

    def __init__(self):
        MplArtistProperties.__init__(self)
        self.props = {}
        self.constructor_props = {}
        self.sub_props = {}

    def compute(self):
        MplArtistProperties.compute(self)
        if self.hasInputFromPort('edgecolor'):
            self.props['edgecolor'] = self.getInputFromPort('edgecolor')
            self.props['edgecolor'] = translate_color(self.props['edgecolor'])
        if self.hasInputFromPort('canvas'):
            self.props['canvas'] = self.getInputFromPort('canvas')
        if self.hasInputFromPort('facecolor'):
            self.props['facecolor'] = self.getInputFromPort('facecolor')
            self.props['facecolor'] = translate_color(self.props['facecolor'])
        if self.hasInputFromPort('size_inches'):
            self.props['size_inches'] = self.getInputFromPort('size_inches')
        if self.hasInputFromPort('figwidth'):
            self.props['figwidth'] = self.getInputFromPort('figwidth')
        if self.hasInputFromPort('frameon'):
            self.props['frameon'] = self.getInputFromPort('frameon')
        if self.hasInputFromPort('subplotpars'):
            self.constructor_props['subplotpars'] = self.getInputFromPort('subplotpars')
        if self.hasInputFromPort('figheight'):
            self.props['figheight'] = self.getInputFromPort('figheight')
        if self.hasInputFromPort('figsize'):
            self.constructor_props['figsize'] = self.getInputFromPort('figsize')
        if self.hasInputFromPort('linewidth'):
            self.constructor_props['linewidth'] = self.getInputFromPort('linewidth')
        if self.hasInputFromPort('dpi'):
            self.props['dpi'] = self.getInputFromPort('dpi')

        
    def update_props(self, objs):
        matplotlib.artist.setp(objs, **self.props)

    def update_kwargs(self, kwargs):
        kwargs.update(self.constructor_props)
        kwargs.update(self.props)

class MplAnnotationProperties(MplTextProperties):
    """
    A :class:`~matplotlib.text.Text` class to make annotating things
    in the figure, such as :class:`~matplotlib.figure.Figure`,
    :class:`~matplotlib.axes.Axes`,
    :class:`~matplotlib.patches.Rectangle`, etc., easier.
    
    """
    _input_ports = [
              ("xycoords", "basic:String",
                {'entry_types': "['enum']", 'values': "[['figure points', 'figure pixels', 'figure fraction', 'axes points', 'axes pixels', 'axes fraction', 'data', 'offset points', 'polar']]", 'optional': True, 'defaults': "['data']"}),
              ("figure", "basic:String",
                {'optional': True}),
              ("annotation_clip", "basic:String",
                {'optional': True}),
              ("xytext", "basic:String",
                {'optional': True}),
              ("s", "basic:String",
                {'optional': True}),
              ("xy", "basic:String",
                {'optional': True}),
              ("textcoords", "basic:String",
                {'entry_types': "['enum']", 'values': "[['figure points', 'figure pixels', 'figure fraction', 'axes points', 'axes pixels', 'axes fraction', 'data', 'offset points', 'polar']]", 'optional': True}),
              ("arrowprops", "basic:String",
                {'optional': True}),
        ]

    # no output ports except self
    _output_ports = [("self", "(MplAnnotationProperties)")]

    def __init__(self):
        MplTextProperties.__init__(self)
        self.props = {}
        self.constructor_props = {}
        self.sub_props = {}

    def compute(self):
        MplTextProperties.compute(self)
        if self.hasInputFromPort('xycoords'):
            self.constructor_props['xycoords'] = self.getInputFromPort('xycoords')
        if self.hasInputFromPort('figure'):
            self.props['figure'] = self.getInputFromPort('figure')
        if self.hasInputFromPort('annotation_clip'):
            self.constructor_props['annotation_clip'] = self.getInputFromPort('annotation_clip')
        if self.hasInputFromPort('xytext'):
            self.constructor_props['xytext'] = self.getInputFromPort('xytext')
        if self.hasInputFromPort('s'):
            self.constructor_props['s'] = self.getInputFromPort('s')
        if self.hasInputFromPort('xy'):
            self.constructor_props['xy'] = self.getInputFromPort('xy')
        if self.hasInputFromPort('textcoords'):
            self.constructor_props['textcoords'] = self.getInputFromPort('textcoords')
        if self.hasInputFromPort('arrowprops'):
            self.constructor_props['arrowprops'] = self.getInputFromPort('arrowprops')

        
    def update_props(self, objs):
        matplotlib.artist.setp(objs, **self.props)

    def update_kwargs(self, kwargs):
        kwargs.update(self.constructor_props)
        kwargs.update(self.props)


_modules = [
            MplArtistProperties,
            MplCollectionProperties,
            MplPathCollectionProperties,
            MplPolyCollectionProperties,
            MplBrokenBarHCollectionProperties,
            MplRegularPolyCollectionProperties,
            MplStarPolygonCollectionProperties,
            MplAsteriskPolygonCollectionProperties,
            MplLineCollectionProperties,
            MplCircleCollectionProperties,
            MplEllipseCollectionProperties,
            MplPatchCollectionProperties,
            MplQuadMeshProperties,
            Mpl_AxesImageBaseProperties,
            MplAxesImageProperties,
            MplNonUniformImageProperties,
            MplBboxImageProperties,
            MplPcolorImageProperties,
            MplFigureImageProperties,
            MplLine2DProperties,
            MplPatchProperties,
            MplYAArrowProperties,
            MplFancyBboxPatchProperties,
            MplEllipseProperties,
            MplArcProperties,
            MplCircleProperties,
            MplRegularPolygonProperties,
            MplCirclePolygonProperties,
            MplPathPatchProperties,
            MplFancyArrowPatchProperties,
            MplConnectionPatchProperties,
            MplRectangleProperties,
            MplPolygonProperties,
            MplFancyArrowProperties,
            MplWedgeProperties,
            MplArrowProperties,
            MplShadowProperties,
            MplTextProperties,
            MplTextWithDashProperties,
            MplTickProperties,
            MplXTickProperties,
            MplYTickProperties,
            MplAxisProperties,
            MplXAxisProperties,
            MplYAxisProperties,
            MplLegendProperties,
            MplAxesProperties,
            MplAxesSubplotProperties,
            MplFigureProperties,
            MplAnnotationProperties,
]
