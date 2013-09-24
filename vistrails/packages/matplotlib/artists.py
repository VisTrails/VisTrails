from vistrails.core.modules.vistrails_module import Module
from bases import MplProperties
import matplotlib.artist
import matplotlib.cbook






def translate_color(c):
    return c.tuple

def translate_MplLine2DProperties_marker(val):
    translate_dict = {'caretright': 5, 'star': '*', 'point': '.', 'mathtext': '$...$', 'triangle_right': '>', 'tickup': 2, 'hexagon1': 'h', 'plus': '+', 'hline': '_', 'vline': '|', 'tickdown': 3, 'nothing': ' ', 'caretup': 6, 'caretleft': 4, 'pentagon': 'p', 'tri_left': '3', 'tickleft': 0, 'tickright': 1, 'tri_down': '1', 'thin_diamond': 'd', 'diamond': 'D', 'caretdown': 7, 'hexagon2': 'H', 'tri_up': '2', 'square': 's', 'x': 'x', 'triangle_down': 'v', 'triangle_up': '^', 'octagon': '8', 'tri_right': '4', 'circle': 'o', 'pixel': ',', 'triangle_left': '<'}
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
        if self.has_input('picker'):
            self.props['picker'] = self.get_input('picker')
        if self.has_input('contains'):
            self.props['contains'] = self.get_input('contains')
        if self.has_input('clip_on'):
            self.props['clip_on'] = self.get_input('clip_on')
        if self.has_input('agg_filter'):
            self.props['agg_filter'] = self.get_input('agg_filter')
        if self.has_input('visible'):
            self.props['visible'] = self.get_input('visible')
        if self.has_input('url'):
            self.props['url'] = self.get_input('url')
        if self.has_input('transform'):
            self.props['transform'] = self.get_input('transform')
        if self.has_input('axes'):
            self.props['axes'] = self.get_input('axes')
        if self.has_input('clip_box'):
            self.props['clip_box'] = self.get_input('clip_box')
        if self.has_input('clip_path'):
            self.props['clip_path'] = self.get_input('clip_path')
        if self.has_input('lod'):
            self.props['lod'] = self.get_input('lod')
        if self.has_input('label'):
            self.props['label'] = self.get_input('label')
        if self.has_input('rasterized'):
            self.props['rasterized'] = self.get_input('rasterized')
        if self.has_input('gid'):
            self.props['gid'] = self.get_input('gid')
        if self.has_input('zorder'):
            self.props['zorder'] = self.get_input('zorder')
        if self.has_input('snap'):
            self.props['snap'] = self.get_input('snap')
        if self.has_input('alpha'):
            self.props['alpha'] = self.get_input('alpha')
        if self.has_input('animated'):
            self.props['animated'] = self.get_input('animated')
        if self.has_input('figure'):
            self.props['figure'] = self.get_input('figure')

        
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
                {'optional': True, 'docstring': 'Set whether or not image resampling is used'}),
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
                {'optional': True, 'docstring': 'Retained for backwards compatibility - use set_data instead'}),
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
        if self.has_input('origin'):
            self.constructor_props['origin'] = self.get_input('origin')
        if self.has_input('resample'):
            self.props['resample'] = self.get_input('resample')
        if self.has_input('norm'):
            self.constructor_props['norm'] = self.get_input('norm')
        if self.has_input('cmap'):
            self.constructor_props['cmap'] = self.get_input('cmap')
        if self.has_input('filternorm'):
            self.props['filternorm'] = self.get_input('filternorm')
        if self.has_input('ax'):
            self.constructor_props['ax'] = self.get_input('ax')
        if self.has_input('alpha'):
            self.props['alpha'] = self.get_input('alpha')
        if self.has_input('array'):
            self.props['array'] = self.get_input('array')
        if self.has_input('data'):
            self.props['data'] = self.get_input('data')
        if self.has_input('filterrad'):
            self.props['filterrad'] = self.get_input('filterrad')
        if self.has_input('interpolation'):
            self.props['interpolation'] = self.get_input('interpolation')

        
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
        if self.has_input('origin'):
            self.constructor_props['origin'] = self.get_input('origin')
        if self.has_input('resample'):
            self.constructor_props['resample'] = self.get_input('resample')
        if self.has_input('norm'):
            self.constructor_props['norm'] = self.get_input('norm')
        if self.has_input('cmap'):
            self.constructor_props['cmap'] = self.get_input('cmap')
        if self.has_input('filterrad'):
            self.constructor_props['filterrad'] = self.get_input('filterrad')
        if self.has_input('extent'):
            self.props['extent'] = self.get_input('extent')
        if self.has_input('ax'):
            self.constructor_props['ax'] = self.get_input('ax')
        if self.has_input('filternorm'):
            self.constructor_props['filternorm'] = self.get_input('filternorm')
        if self.has_input('interpolation'):
            self.constructor_props['interpolation'] = self.get_input('interpolation')

        
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
        if self.has_input('norm'):
            self.props['norm'] = self.get_input('norm')
        if self.has_input('cmap'):
            self.props['cmap'] = self.get_input('cmap')
        if self.has_input('filternorm'):
            self.props['filternorm'] = self.get_input('filternorm')
        if self.has_input('ax'):
            self.constructor_props['ax'] = self.get_input('ax')
        if self.has_input('array'):
            self.props['array'] = self.get_input('array')
        if self.has_input('data'):
            self.props['data'] = self.get_input('data')
        if self.has_input('filterrad'):
            self.props['filterrad'] = self.get_input('filterrad')
        if self.has_input('interpolation'):
            self.props['interpolation'] = self.get_input('interpolation')

        
    def update_props(self, objs):
        matplotlib.artist.setp(objs, **self.props)

    def update_kwargs(self, kwargs):
        kwargs.update(self.constructor_props)
        kwargs.update(self.props)

class MplBboxImageProperties(Mpl_AxesImageBaseProperties):
    """The Image class whose size is determined by the given bbox.
    """
    _input_ports = [
              ("origin", "basic:String",
                {'optional': True}),
              ("interp_at_native", "basic:Boolean",
                {'optional': True, 'defaults': "['True']"}),
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
        if self.has_input('origin'):
            self.constructor_props['origin'] = self.get_input('origin')
        if self.has_input('interp_at_native'):
            self.constructor_props['interp_at_native'] = self.get_input('interp_at_native')
        if self.has_input('resample'):
            self.constructor_props['resample'] = self.get_input('resample')
        if self.has_input('cmap'):
            self.constructor_props['cmap'] = self.get_input('cmap')
        if self.has_input('filternorm'):
            self.constructor_props['filternorm'] = self.get_input('filternorm')
        if self.has_input('norm'):
            self.constructor_props['norm'] = self.get_input('norm')
        if self.has_input('interpolation'):
            self.constructor_props['interpolation'] = self.get_input('interpolation')
        if self.has_input('filterrad'):
            self.constructor_props['filterrad'] = self.get_input('filterrad')
        if self.has_input('bbox'):
            self.constructor_props['bbox'] = self.get_input('bbox')

        
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
        if self.has_input('A'):
            self.constructor_props['A'] = self.get_input('A')
        if self.has_input('ax'):
            self.constructor_props['ax'] = self.get_input('ax')
        if self.has_input('cmap'):
            self.constructor_props['cmap'] = self.get_input('cmap')
        if self.has_input('x'):
            self.constructor_props['x'] = self.get_input('x')
        if self.has_input('y'):
            self.constructor_props['y'] = self.get_input('y')
        if self.has_input('alpha'):
            self.props['alpha'] = self.get_input('alpha')
        if self.has_input('array'):
            self.props['array'] = self.get_input('array')
        if self.has_input('data'):
            self.props['data'] = self.get_input('data')
        if self.has_input('norm'):
            self.constructor_props['norm'] = self.get_input('norm')

        
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
                {'optional': True, 'docstring': 'Set the image array.'}),
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
        if self.has_input('origin'):
            self.constructor_props['origin'] = self.get_input('origin')
        if self.has_input('offsetx'):
            self.constructor_props['offsetx'] = self.get_input('offsetx')
        if self.has_input('offsety'):
            self.constructor_props['offsety'] = self.get_input('offsety')
        if self.has_input('cmap'):
            self.constructor_props['cmap'] = self.get_input('cmap')
        if self.has_input('fig'):
            self.constructor_props['fig'] = self.get_input('fig')
        if self.has_input('array'):
            self.props['array'] = self.get_input('array')
        if self.has_input('data'):
            self.props['data'] = self.get_input('data')
        if self.has_input('norm'):
            self.constructor_props['norm'] = self.get_input('norm')

        
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
        * *offset_position*: 'screen' (default) or 'data'
        * *norm*: None (optional for
          :class:`matplotlib.cm.ScalarMappable`)
        * *cmap*: None (optional for
          :class:`matplotlib.cm.ScalarMappable`)
        * *hatch*: None

    *offsets* and *transOffset* are used to translate the patch after
    rendering (default no offsets).  If offset_position is 'screen'
    (default) the offset is applied after the master transform has
    been applied, that is, the offsets are in screen coordinates.  If
    offset_position is 'data', the offset is applied before the master
    transform, i.e., the offsets are in data coordinates.

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
              ("offset_position", "basic:String",
                {'optional': True, 'docstring': "Set how offsets are applied.  If offset_position is 'screen' (default) the offset is applied after the master transform has been applied, that is, the offsets are in screen coordinates. If offset_position is 'data', the offset is applied before the master transform, i.e., the offsets are in data coordinates."}),
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
              ("pickradius", "basic:String",
                {'optional': True}),
              ("antialiaseds", "basic:String",
                {'optional': True}),
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
              ("hatch", "basic:String",
                {'entry_types': "['enum']", 'docstring': 'Set the hatching pattern\n\nhatch can be one of:\n\n/   - diagonal hatching \\   - back diagonal |   - vertical -   - horizontal +   - crossed x   - crossed diagonal o   - small circle O   - large circle .   - dots *   - stars\n\nLetters can be combined, in which case all the specified hatchings are done.  If same letter repeats, it increases the density of hatching of that pattern.\n\nHatching is supported in the PostScript, PDF, SVG and Agg backends only.\n\nUnlike other properties such as linewidth and colors, hatching can only be specified for the collection as a whole, not separately for each member.', 'values': '[[\'/\', "\'\\\\\'", "\'", "\'", \'-\', \'+\', \'x\', \'o\', \'O\', \'.\', \'*\']]', 'optional': True}),
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
        if self.has_input('transOffset'):
            self.constructor_props['transOffset'] = self.get_input('transOffset')
        if self.has_input('edgecolor'):
            self.props['edgecolor'] = self.get_input('edgecolor')
        if self.has_input('offset_position'):
            self.props['offset_position'] = self.get_input('offset_position')
        if self.has_input('edgecolors'):
            self.constructor_props['edgecolors'] = self.get_input('edgecolors')
        if self.has_input('facecolor'):
            self.props['facecolor'] = self.get_input('facecolor')
        if self.has_input('linestyles'):
            self.constructor_props['linestyles'] = self.get_input('linestyles')
        if self.has_input('offsetsSequence'):
            self.props['offsets'] = self.get_input('offsetsSequence')
        elif self.has_input('offsetsScalar'):
            self.props['offsets'] = self.get_input('offsetsScalar')
        if self.has_input('color'):
            self.props['color'] = self.get_input('color')
        if self.has_input('pickradius'):
            self.props['pickradius'] = self.get_input('pickradius')
        if self.has_input('antialiaseds'):
            self.constructor_props['antialiaseds'] = self.get_input('antialiaseds')
        if self.has_input('linewidths'):
            self.constructor_props['linewidths'] = self.get_input('linewidths')
        if self.has_input('cmap'):
            self.constructor_props['cmap'] = self.get_input('cmap')
        if self.has_input('antialiasedSequence'):
            self.props['antialiased'] = self.get_input('antialiasedSequence')
        elif self.has_input('antialiasedScalar'):
            self.props['antialiased'] = self.get_input('antialiasedScalar')
        if self.has_input('urls'):
            self.props['urls'] = self.get_input('urls')
        if self.has_input('hatch'):
            self.props['hatch'] = self.get_input('hatch')
        if self.has_input('alpha'):
            self.props['alpha'] = self.get_input('alpha')
        if self.has_input('paths'):
            self.props['paths'] = self.get_input('paths')
        if self.has_input('linewidthSequence'):
            self.props['linewidth'] = self.get_input('linewidthSequence')
        elif self.has_input('linewidthScalar'):
            self.props['linewidth'] = self.get_input('linewidthScalar')
        if self.has_input('linestyle'):
            self.props['linestyle'] = self.get_input('linestyle')
        if self.has_input('facecolors'):
            self.constructor_props['facecolors'] = self.get_input('facecolors')
        if self.has_input('norm'):
            self.constructor_props['norm'] = self.get_input('norm')

        
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
        if self.has_input('paths'):
            self.props['paths'] = self.get_input('paths')
        if self.has_input('sizes'):
            self.constructor_props['sizes'] = self.get_input('sizes')

        
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
        if self.has_input('paths'):
            self.props['paths'] = self.get_input('paths')
        if self.has_input('verts'):
            self.props['verts'] = self.get_input('verts')
        if self.has_input('closed'):
            self.constructor_props['closed'] = self.get_input('closed')
        if self.has_input('sizes'):
            self.constructor_props['sizes'] = self.get_input('sizes')

        
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
        if self.has_input('xranges'):
            self.constructor_props['xranges'] = self.get_input('xranges')
        if self.has_input('yrange'):
            self.constructor_props['yrange'] = self.get_input('yrange')

        
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
        if self.has_input('numsides'):
            self.constructor_props['numsides'] = self.get_input('numsides')
        if self.has_input('rotation'):
            self.constructor_props['rotation'] = self.get_input('rotation')
        if self.has_input('sizes'):
            self.constructor_props['sizes'] = self.get_input('sizes')

        
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
        if self.has_input('numsides'):
            self.constructor_props['numsides'] = self.get_input('numsides')
        if self.has_input('rotation'):
            self.constructor_props['rotation'] = self.get_input('rotation')
        if self.has_input('sizes'):
            self.constructor_props['sizes'] = self.get_input('sizes')

        
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
        if self.has_input('numsides'):
            self.constructor_props['numsides'] = self.get_input('numsides')
        if self.has_input('rotation'):
            self.constructor_props['rotation'] = self.get_input('rotation')
        if self.has_input('sizes'):
            self.constructor_props['sizes'] = self.get_input('sizes')

        
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
        if self.has_input('paths'):
            self.props['paths'] = self.get_input('paths')
        if self.has_input('antialiaseds'):
            self.constructor_props['antialiaseds'] = self.get_input('antialiaseds')
        if self.has_input('linestyles'):
            self.constructor_props['linestyles'] = self.get_input('linestyles')
        if self.has_input('offsets'):
            self.constructor_props['offsets'] = self.get_input('offsets')
        if self.has_input('color'):
            self.props['color'] = self.get_input('color')
        if self.has_input('segments'):
            self.props['segments'] = self.get_input('segments')
        if self.has_input('linewidths'):
            self.constructor_props['linewidths'] = self.get_input('linewidths')
        if self.has_input('colors'):
            self.constructor_props['colors'] = self.get_input('colors')
        if self.has_input('cmap'):
            self.constructor_props['cmap'] = self.get_input('cmap')
        if self.has_input('transOffset'):
            self.constructor_props['transOffset'] = self.get_input('transOffset')
        if self.has_input('verts'):
            self.props['verts'] = self.get_input('verts')
        if self.has_input('pickradius'):
            self.constructor_props['pickradius'] = self.get_input('pickradius')
        if self.has_input('norm'):
            self.constructor_props['norm'] = self.get_input('norm')

        
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
        if self.has_input('sizes'):
            self.constructor_props['sizes'] = self.get_input('sizes')

        
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
        if self.has_input('units'):
            self.constructor_props['units'] = self.get_input('units')
        if self.has_input('widths'):
            self.constructor_props['widths'] = self.get_input('widths')
        if self.has_input('angles'):
            self.constructor_props['angles'] = self.get_input('angles')
        if self.has_input('heights'):
            self.constructor_props['heights'] = self.get_input('heights')

        
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
        if self.has_input('paths'):
            self.props['paths'] = self.get_input('paths')
        if self.has_input('patches'):
            self.constructor_props['patches'] = self.get_input('patches')
        if self.has_input('match_original'):
            self.constructor_props['match_original'] = self.get_input('match_original')

        
    def update_props(self, objs):
        matplotlib.artist.setp(objs, **self.props)

    def update_kwargs(self, kwargs):
        kwargs.update(self.constructor_props)
        kwargs.update(self.props)

class MplTriMeshProperties(MplCollectionProperties):
    """
    Class for the efficient drawing of a triangular mesh using
    Gouraud shading.

    A triangular mesh is a :class:`~matplotlib.tri.Triangulation`
    object.
    
    """
    _input_ports = [
              ("triangulation", "basic:String",
                {'optional': True}),
              ("paths", "basic:String",
                {'optional': True}),
        ]

    # no output ports except self
    _output_ports = [("self", "(MplTriMeshProperties)")]

    def __init__(self):
        MplCollectionProperties.__init__(self)
        self.props = {}
        self.constructor_props = {}
        self.sub_props = {}

    def compute(self):
        MplCollectionProperties.compute(self)
        if self.has_input('triangulation'):
            self.constructor_props['triangulation'] = self.get_input('triangulation')
        if self.has_input('paths'):
            self.props['paths'] = self.get_input('paths')

        
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

    *shading* may be 'flat', or 'gouraud'
    
    """
    _input_ports = [
              ("paths", "basic:String",
                {'optional': True}),
              ("meshWidth", "basic:String",
                {'optional': True}),
              ("coordinates", "basic:String",
                {'optional': True}),
              ("antialiased", "basic:Boolean",
                {'optional': True, 'defaults': "['True']"}),
              ("shading", "basic:String",
                {'optional': True, 'defaults': "['flat']"}),
              ("meshHeight", "basic:String",
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
        if self.has_input('paths'):
            self.props['paths'] = self.get_input('paths')
        if self.has_input('meshWidth'):
            self.constructor_props['meshWidth'] = self.get_input('meshWidth')
        if self.has_input('coordinates'):
            self.constructor_props['coordinates'] = self.get_input('coordinates')
        if self.has_input('antialiased'):
            self.constructor_props['antialiased'] = self.get_input('antialiased')
        if self.has_input('shading'):
            self.constructor_props['shading'] = self.get_input('shading')
        if self.has_input('meshHeight'):
            self.constructor_props['meshHeight'] = self.get_input('meshHeight')

        
    def update_props(self, objs):
        matplotlib.artist.setp(objs, **self.props)

    def update_kwargs(self, kwargs):
        kwargs.update(self.constructor_props)
        kwargs.update(self.props)

class MplPatchProperties(MplArtistProperties):
    """
    A patch is a 2D artist with a face color and an edge color.

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
        if self.has_input('edgecolor'):
            self.props['edgecolor'] = self.get_input('edgecolor')
            self.props['edgecolor'] = translate_color(self.props['edgecolor'])
        if self.has_input('facecolor'):
            self.props['facecolor'] = self.get_input('facecolor')
            self.props['facecolor'] = translate_color(self.props['facecolor'])
        if self.has_input('path_effects'):
            self.props['path_effects'] = self.get_input('path_effects')
        if self.has_input('color'):
            self.props['color'] = self.get_input('color')
            self.props['color'] = translate_color(self.props['color'])
        if self.has_input('antialiased'):
            self.props['antialiased'] = self.get_input('antialiased')
        if self.has_input('hatch'):
            self.props['hatch'] = self.get_input('hatch')
        if self.has_input('alpha'):
            self.props['alpha'] = self.get_input('alpha')
        if self.has_input('linewidth'):
            self.props['linewidth'] = self.get_input('linewidth')
        if self.has_input('linestyle'):
            self.props['linestyle'] = self.get_input('linestyle')
        if self.has_input('fill'):
            self.props['fill'] = self.get_input('fill')

        
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
        if self.has_input('patch'):
            self.constructor_props['patch'] = self.get_input('patch')
        if self.has_input('props'):
            self.constructor_props['props'] = self.get_input('props')
        if self.has_input('oy'):
            self.constructor_props['oy'] = self.get_input('oy')
        if self.has_input('ox'):
            self.constructor_props['ox'] = self.get_input('ox')

        
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
        if self.has_input('bounds'):
            self.props['bounds'] = self.get_input('bounds')
        if self.has_input('height'):
            self.props['height'] = self.get_input('height')
        if self.has_input('width'):
            self.props['width'] = self.get_input('width')
        if self.has_input('xy'):
            self.props['xy'] = self.get_input('xy')
        if self.has_input('y'):
            self.props['y'] = self.get_input('y')
        if self.has_input('x'):
            self.props['x'] = self.get_input('x')

        
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
        if self.has_input('xy'):
            self.constructor_props['xy'] = self.get_input('xy')
        if self.has_input('radius'):
            self.constructor_props['radius'] = self.get_input('radius')
        if self.has_input('orientation'):
            self.constructor_props['orientation'] = self.get_input('orientation')
        if self.has_input('numVertices'):
            self.constructor_props['numVertices'] = self.get_input('numVertices')

        
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
        if self.has_input('radius'):
            self.constructor_props['radius'] = self.get_input('radius')
        if self.has_input('xy'):
            self.constructor_props['xy'] = self.get_input('xy')
        if self.has_input('resolution'):
            self.constructor_props['resolution'] = self.get_input('resolution')

        
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
        if self.has_input('path'):
            self.constructor_props['path'] = self.get_input('path')

        
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
        if self.has_input('xy'):
            self.props['xy'] = self.get_input('xy')
        if self.has_input('closed'):
            self.props['closed'] = self.get_input('closed')

        
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
                {'optional': True, 'defaults': "['False']"}),
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
        if self.has_input('length_includes_head'):
            self.constructor_props['length_includes_head'] = self.get_input('length_includes_head')
        if self.has_input('head_length'):
            self.constructor_props['head_length'] = self.get_input('head_length')
        if self.has_input('head_width'):
            self.constructor_props['head_width'] = self.get_input('head_width')
        if self.has_input('width'):
            self.constructor_props['width'] = self.get_input('width')
        if self.has_input('shape'):
            self.constructor_props['shape'] = self.get_input('shape')
        if self.has_input('dx'):
            self.constructor_props['dx'] = self.get_input('dx')
        if self.has_input('dy'):
            self.constructor_props['dy'] = self.get_input('dy')
        if self.has_input('y'):
            self.constructor_props['y'] = self.get_input('y')
        if self.has_input('x'):
            self.constructor_props['x'] = self.get_input('x')
        if self.has_input('head_starts_at_zero'):
            self.constructor_props['head_starts_at_zero'] = self.get_input('head_starts_at_zero')
        if self.has_input('overhang'):
            self.constructor_props['overhang'] = self.get_input('overhang')

        
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
        if self.has_input('theta2'):
            self.constructor_props['theta2'] = self.get_input('theta2')
        if self.has_input('width'):
            self.constructor_props['width'] = self.get_input('width')
        if self.has_input('r'):
            self.constructor_props['r'] = self.get_input('r')
        if self.has_input('theta1'):
            self.constructor_props['theta1'] = self.get_input('theta1')
        if self.has_input('center'):
            self.constructor_props['center'] = self.get_input('center')

        
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
        if self.has_input('y'):
            self.constructor_props['y'] = self.get_input('y')
        if self.has_input('x'):
            self.constructor_props['x'] = self.get_input('x')
        if self.has_input('dy'):
            self.constructor_props['dy'] = self.get_input('dy')
        if self.has_input('dx'):
            self.constructor_props['dx'] = self.get_input('dx')
        if self.has_input('width'):
            self.constructor_props['width'] = self.get_input('width')

        
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
        if self.has_input('xytip'):
            self.constructor_props['xytip'] = self.get_input('xytip')
        if self.has_input('headwidth'):
            self.constructor_props['headwidth'] = self.get_input('headwidth')
        if self.has_input('frac'):
            self.constructor_props['frac'] = self.get_input('frac')
        if self.has_input('figure'):
            self.constructor_props['figure'] = self.get_input('figure')
        if self.has_input('xybase'):
            self.constructor_props['xybase'] = self.get_input('xybase')
        if self.has_input('width'):
            self.constructor_props['width'] = self.get_input('width')

        
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
        if self.has_input('width'):
            self.constructor_props['width'] = self.get_input('width')
        if self.has_input('xy'):
            self.constructor_props['xy'] = self.get_input('xy')
        if self.has_input('angle'):
            self.constructor_props['angle'] = self.get_input('angle')
        if self.has_input('height'):
            self.constructor_props['height'] = self.get_input('height')

        
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
        if self.has_input('xy'):
            self.constructor_props['xy'] = self.get_input('xy')
        if self.has_input('radius'):
            self.props['radius'] = self.get_input('radius')

        
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
        if self.has_input('theta2'):
            self.constructor_props['theta2'] = self.get_input('theta2')
        if self.has_input('theta1'):
            self.constructor_props['theta1'] = self.get_input('theta1')
        if self.has_input('angle'):
            self.constructor_props['angle'] = self.get_input('angle')
        if self.has_input('height'):
            self.constructor_props['height'] = self.get_input('height')
        if self.has_input('width'):
            self.constructor_props['width'] = self.get_input('width')
        if self.has_input('xy'):
            self.constructor_props['xy'] = self.get_input('xy')

        
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
        if self.has_input('mutation_scale'):
            self.props['mutation_scale'] = self.get_input('mutation_scale')
        if self.has_input('bbox_transmuter'):
            self.constructor_props['bbox_transmuter'] = self.get_input('bbox_transmuter')
        if self.has_input('bounds'):
            self.props['bounds'] = self.get_input('bounds')
        if self.has_input('height'):
            self.props['height'] = self.get_input('height')
        if self.has_input('width'):
            self.props['width'] = self.get_input('width')
        if self.has_input('xy'):
            self.constructor_props['xy'] = self.get_input('xy')
        if self.has_input('boxstyle'):
            self.props['boxstyle'] = self.get_input('boxstyle')
        if self.has_input('mutation_aspect'):
            self.props['mutation_aspect'] = self.get_input('mutation_aspect')
        if self.has_input('y'):
            self.props['y'] = self.get_input('y')
        if self.has_input('x'):
            self.props['x'] = self.get_input('x')

        
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
        if self.has_input('connectionstyle'):
            self.props['connectionstyle'] = self.get_input('connectionstyle')
        if self.has_input('mutation_scale'):
            self.props['mutation_scale'] = self.get_input('mutation_scale')
        if self.has_input('arrowstyle'):
            self.props['arrowstyle'] = self.get_input('arrowstyle')
        if self.has_input('arrow_transmuter'):
            self.constructor_props['arrow_transmuter'] = self.get_input('arrow_transmuter')
        if self.has_input('positions'):
            self.props['positions'] = self.get_input('positions')
        if self.has_input('shrinkA'):
            self.constructor_props['shrinkA'] = self.get_input('shrinkA')
        if self.has_input('posB'):
            self.constructor_props['posB'] = self.get_input('posB')
        if self.has_input('dpi_cor'):
            self.props['dpi_cor'] = self.get_input('dpi_cor')
        if self.has_input('connector'):
            self.constructor_props['connector'] = self.get_input('connector')
        if self.has_input('path'):
            self.constructor_props['path'] = self.get_input('path')
        if self.has_input('shrinkB'):
            self.constructor_props['shrinkB'] = self.get_input('shrinkB')
        if self.has_input('mutation_aspect'):
            self.props['mutation_aspect'] = self.get_input('mutation_aspect')
        if self.has_input('patchA'):
            self.props['patchA'] = self.get_input('patchA')
        if self.has_input('patchB'):
            self.props['patchB'] = self.get_input('patchB')
        if self.has_input('posA'):
            self.constructor_props['posA'] = self.get_input('posA')

        
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
                {'optional': True, 'docstring': 'set annotation_clip attribute.\n\nNone: the self.xy will be checked only if xycoords is "data"'}),
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
        if self.has_input('connectionstyle'):
            self.constructor_props['connectionstyle'] = self.get_input('connectionstyle')
        if self.has_input('coordsA'):
            self.constructor_props['coordsA'] = self.get_input('coordsA')
        if self.has_input('arrowstyle'):
            self.constructor_props['arrowstyle'] = self.get_input('arrowstyle')
        if self.has_input('clip_on'):
            self.constructor_props['clip_on'] = self.get_input('clip_on')
        if self.has_input('arrow_transmuter'):
            self.constructor_props['arrow_transmuter'] = self.get_input('arrow_transmuter')
        if self.has_input('axesA'):
            self.constructor_props['axesA'] = self.get_input('axesA')
        if self.has_input('axesB'):
            self.constructor_props['axesB'] = self.get_input('axesB')
        if self.has_input('annotation_clip'):
            self.props['annotation_clip'] = self.get_input('annotation_clip')
        if self.has_input('dpi_cor'):
            self.constructor_props['dpi_cor'] = self.get_input('dpi_cor')
        if self.has_input('connector'):
            self.constructor_props['connector'] = self.get_input('connector')
        if self.has_input('xyA'):
            self.constructor_props['xyA'] = self.get_input('xyA')
        if self.has_input('xyB'):
            self.constructor_props['xyB'] = self.get_input('xyB')
        if self.has_input('relpos'):
            self.constructor_props['relpos'] = self.get_input('relpos')
        if self.has_input('shrinkB'):
            self.constructor_props['shrinkB'] = self.get_input('shrinkB')
        if self.has_input('shrinkA'):
            self.constructor_props['shrinkA'] = self.get_input('shrinkA')
        if self.has_input('mutation_aspect'):
            self.constructor_props['mutation_aspect'] = self.get_input('mutation_aspect')
        if self.has_input('mutation_scale'):
            self.constructor_props['mutation_scale'] = self.get_input('mutation_scale')
        if self.has_input('patchA'):
            self.constructor_props['patchA'] = self.get_input('patchA')
        if self.has_input('patchB'):
            self.constructor_props['patchB'] = self.get_input('patchB')
        if self.has_input('coordsB'):
            self.constructor_props['coordsB'] = self.get_input('coordsB')
        if self.has_input('?'):
            self.constructor_props['?'] = self.get_input('?')

        
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
                {'entry_types': "['enum']", 'docstring': "Set the marker fill style; 'full' means fill the whole marker. 'none' means no filling; other options are for half-filled markers.", 'values': "[['full', 'left', 'right', 'bottom', 'top', 'none']]", 'optional': True}),
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
        if self.has_input('picker'):
            self.props['picker'] = self.get_input('picker')
        if self.has_input('dash_capstyle'):
            self.props['dash_capstyle'] = self.get_input('dash_capstyle')
        if self.has_input('color'):
            self.props['color'] = self.get_input('color')
            self.props['color'] = translate_color(self.props['color'])
        if self.has_input('markevery'):
            self.props['markevery'] = self.get_input('markevery')
        if self.has_input('markeredgecolor'):
            self.props['markeredgecolor'] = self.get_input('markeredgecolor')
            self.props['markeredgecolor'] = translate_color(self.props['markeredgecolor'])
        if self.has_input('marker'):
            self.props['marker'] = self.get_input('marker')
            self.props['marker'] = translate_MplLine2DProperties_marker(self.props['marker'])
        if self.has_input('markerfacecoloralt'):
            self.props['markerfacecoloralt'] = self.get_input('markerfacecoloralt')
            self.props['markerfacecoloralt'] = translate_color(self.props['markerfacecoloralt'])
        if self.has_input('linewidth'):
            self.props['linewidth'] = self.get_input('linewidth')
        if self.has_input('linestyle'):
            self.props['linestyle'] = self.get_input('linestyle')
            self.props['linestyle'] = translate_MplLine2DProperties_linestyle(self.props['linestyle'])
        if self.has_input('solid_joinstyle'):
            self.props['solid_joinstyle'] = self.get_input('solid_joinstyle')
        if self.has_input('markerfacecolor'):
            self.props['markerfacecolor'] = self.get_input('markerfacecolor')
            self.props['markerfacecolor'] = translate_color(self.props['markerfacecolor'])
        if self.has_input('axes'):
            self.props['axes'] = self.get_input('axes')
        if self.has_input('transform'):
            self.props['transform'] = self.get_input('transform')
        if self.has_input('fillstyle'):
            self.props['fillstyle'] = self.get_input('fillstyle')
        if self.has_input('markeredgewidth'):
            self.props['markeredgewidth'] = self.get_input('markeredgewidth')
        if self.has_input('solid_capstyle'):
            self.props['solid_capstyle'] = self.get_input('solid_capstyle')
        if self.has_input('dashes'):
            self.props['dashes'] = self.get_input('dashes')
        if self.has_input('markersize'):
            self.props['markersize'] = self.get_input('markersize')
        if self.has_input('antialiased'):
            self.props['antialiased'] = self.get_input('antialiased')
        if self.has_input('xdata'):
            self.props['xdata'] = self.get_input('xdata')
        if self.has_input('drawstyle'):
            self.props['drawstyle'] = self.get_input('drawstyle')
        if self.has_input('data'):
            self.props['data'] = self.get_input('data')
        if self.has_input('dash_joinstyle'):
            self.props['dash_joinstyle'] = self.get_input('dash_joinstyle')
        if self.has_input('pickradius'):
            self.props['pickradius'] = self.get_input('pickradius')
        if self.has_input('ydata'):
            self.props['ydata'] = self.get_input('ydata')

        
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
              ("x", "basic:Float",
                {'optional': True, 'docstring': 'Set the x position of the text'}),
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
        if self.has_input('rotation_mode'):
            self.props['rotation_mode'] = self.get_input('rotation_mode')
        if self.has_input('style'):
            self.props['style'] = self.get_input('style')
        if self.has_input('linespacing'):
            self.props['linespacing'] = self.get_input('linespacing')
        if self.has_input('family'):
            self.props['family'] = self.get_input('family')
        if self.has_input('x'):
            self.props['x'] = self.get_input('x')
        if self.has_input('color'):
            self.props['color'] = self.get_input('color')
            self.props['color'] = translate_color(self.props['color'])
        if self.has_input('text'):
            self.props['text'] = self.get_input('text')
        if self.has_input('verticalalignment'):
            self.props['verticalalignment'] = self.get_input('verticalalignment')
        if self.has_input('variant'):
            self.props['variant'] = self.get_input('variant')
        if self.has_input('path_effects'):
            self.props['path_effects'] = self.get_input('path_effects')
        if self.has_input('weight'):
            self.props['weight'] = self.get_input('weight')
        if self.has_input('stretch'):
            self.props['stretch'] = self.get_input('stretch')
        if self.has_input('fontproperties'):
            self.props['fontproperties'] = self.get_input('fontproperties')
        if self.has_input('horizontalalignment'):
            self.props['horizontalalignment'] = self.get_input('horizontalalignment')
        if self.has_input('bbox'):
            self.props['bbox'] = self.get_input('bbox')
        if self.has_input('backgroundcolor'):
            self.props['backgroundcolor'] = self.get_input('backgroundcolor')
            self.props['backgroundcolor'] = translate_color(self.props['backgroundcolor'])
        if self.has_input('position'):
            self.props['position'] = self.get_input('position')
        if self.has_input('y'):
            self.props['y'] = self.get_input('y')
        if self.has_input('multialignment'):
            self.props['multialignment'] = self.get_input('multialignment')
        if self.has_input('rotation'):
            self.props['rotation'] = self.get_input('rotation')
        if self.has_input('size'):
            self.props['size'] = self.get_input('size')

        
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
        if self.has_input('dashpush'):
            self.props['dashpush'] = self.get_input('dashpush')
        if self.has_input('dashdirection'):
            self.props['dashdirection'] = self.get_input('dashdirection')
        if self.has_input('linespacing'):
            self.constructor_props['linespacing'] = self.get_input('linespacing')
        if self.has_input('figure'):
            self.props['figure'] = self.get_input('figure')
        if self.has_input('color'):
            self.constructor_props['color'] = self.get_input('color')
        if self.has_input('text'):
            self.constructor_props['text'] = self.get_input('text')
        if self.has_input('verticalalignment'):
            self.constructor_props['verticalalignment'] = self.get_input('verticalalignment')
        if self.has_input('dashpad'):
            self.props['dashpad'] = self.get_input('dashpad')
        if self.has_input('dashrotation'):
            self.props['dashrotation'] = self.get_input('dashrotation')
        if self.has_input('transform'):
            self.props['transform'] = self.get_input('transform')
        if self.has_input('fontproperties'):
            self.constructor_props['fontproperties'] = self.get_input('fontproperties')
        if self.has_input('multialignment'):
            self.constructor_props['multialignment'] = self.get_input('multialignment')
        if self.has_input('x'):
            self.props['x'] = self.get_input('x')
        if self.has_input('y'):
            self.props['y'] = self.get_input('y')
        if self.has_input('position'):
            self.props['position'] = self.get_input('position')
        if self.has_input('dashlength'):
            self.props['dashlength'] = self.get_input('dashlength')
        if self.has_input('rotation'):
            self.constructor_props['rotation'] = self.get_input('rotation')
        if self.has_input('horizontalalignment'):
            self.constructor_props['horizontalalignment'] = self.get_input('horizontalalignment')

        
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
        if self.has_input('label1On'):
            self.constructor_props['label1On'] = self.get_input('label1On')
        if self.has_input('loc'):
            self.constructor_props['loc'] = self.get_input('loc')
        if self.has_input('major'):
            self.constructor_props['major'] = self.get_input('major')
        if self.has_input('label2On'):
            self.constructor_props['label2On'] = self.get_input('label2On')
        if self.has_input('color'):
            self.constructor_props['color'] = self.get_input('color')
        if self.has_input('label1'):
            self.props['label1'] = self.get_input('label1')
        if self.has_input('label2'):
            self.props['label2'] = self.get_input('label2')
        if self.has_input('axes'):
            self.constructor_props['axes'] = self.get_input('axes')
        if self.has_input('clip_path'):
            self.props['clip_path'] = self.get_input('clip_path')
        if self.has_input('label'):
            self.props['label'] = self.get_input('label')
        if self.has_input('labelcolor'):
            self.constructor_props['labelcolor'] = self.get_input('labelcolor')
        if self.has_input('tickdir'):
            self.constructor_props['tickdir'] = self.get_input('tickdir')
        if self.has_input('pad'):
            self.props['pad'] = self.get_input('pad')
        if self.has_input('gridOn'):
            self.constructor_props['gridOn'] = self.get_input('gridOn')
        if self.has_input('zorder'):
            self.constructor_props['zorder'] = self.get_input('zorder')
        if self.has_input('tick2On'):
            self.constructor_props['tick2On'] = self.get_input('tick2On')
        if self.has_input('labelsize'):
            self.constructor_props['labelsize'] = self.get_input('labelsize')
        if self.has_input('width'):
            self.constructor_props['width'] = self.get_input('width')
        if self.has_input('tick1On'):
            self.constructor_props['tick1On'] = self.get_input('tick1On')
        if self.has_input('size'):
            self.constructor_props['size'] = self.get_input('size')

        
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
        if self.has_input('label1On'):
            self.constructor_props['label1On'] = self.get_input('label1On')
        if self.has_input('loc'):
            self.constructor_props['loc'] = self.get_input('loc')
        if self.has_input('major'):
            self.constructor_props['major'] = self.get_input('major')
        if self.has_input('label2On'):
            self.constructor_props['label2On'] = self.get_input('label2On')
        if self.has_input('color'):
            self.constructor_props['color'] = self.get_input('color')
        if self.has_input('axes'):
            self.constructor_props['axes'] = self.get_input('axes')
        if self.has_input('label'):
            self.constructor_props['label'] = self.get_input('label')
        if self.has_input('labelcolor'):
            self.constructor_props['labelcolor'] = self.get_input('labelcolor')
        if self.has_input('tickdir'):
            self.constructor_props['tickdir'] = self.get_input('tickdir')
        if self.has_input('pad'):
            self.constructor_props['pad'] = self.get_input('pad')
        if self.has_input('gridOn'):
            self.constructor_props['gridOn'] = self.get_input('gridOn')
        if self.has_input('zorder'):
            self.constructor_props['zorder'] = self.get_input('zorder')
        if self.has_input('tick2On'):
            self.constructor_props['tick2On'] = self.get_input('tick2On')
        if self.has_input('labelsize'):
            self.constructor_props['labelsize'] = self.get_input('labelsize')
        if self.has_input('width'):
            self.constructor_props['width'] = self.get_input('width')
        if self.has_input('tick1On'):
            self.constructor_props['tick1On'] = self.get_input('tick1On')
        if self.has_input('size'):
            self.constructor_props['size'] = self.get_input('size')

        
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
        if self.has_input('label1On'):
            self.constructor_props['label1On'] = self.get_input('label1On')
        if self.has_input('loc'):
            self.constructor_props['loc'] = self.get_input('loc')
        if self.has_input('major'):
            self.constructor_props['major'] = self.get_input('major')
        if self.has_input('label2On'):
            self.constructor_props['label2On'] = self.get_input('label2On')
        if self.has_input('color'):
            self.constructor_props['color'] = self.get_input('color')
        if self.has_input('axes'):
            self.constructor_props['axes'] = self.get_input('axes')
        if self.has_input('label'):
            self.constructor_props['label'] = self.get_input('label')
        if self.has_input('labelcolor'):
            self.constructor_props['labelcolor'] = self.get_input('labelcolor')
        if self.has_input('tickdir'):
            self.constructor_props['tickdir'] = self.get_input('tickdir')
        if self.has_input('pad'):
            self.constructor_props['pad'] = self.get_input('pad')
        if self.has_input('gridOn'):
            self.constructor_props['gridOn'] = self.get_input('gridOn')
        if self.has_input('zorder'):
            self.constructor_props['zorder'] = self.get_input('zorder')
        if self.has_input('tick2On'):
            self.constructor_props['tick2On'] = self.get_input('tick2On')
        if self.has_input('labelsize'):
            self.constructor_props['labelsize'] = self.get_input('labelsize')
        if self.has_input('width'):
            self.constructor_props['width'] = self.get_input('width')
        if self.has_input('tick1On'):
            self.constructor_props['tick1On'] = self.get_input('tick1On')
        if self.has_input('size'):
            self.constructor_props['size'] = self.get_input('size')

        
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
                {'optional': True}),
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
        if self.has_input('pickradius'):
            self.props['pickradius'] = self.get_input('pickradius')
        if self.has_input('minor_formatter'):
            self.props['minor_formatter'] = self.get_input('minor_formatter')
        if self.has_input('smart_bounds'):
            self.props['smart_bounds'] = self.get_input('smart_bounds')
        if self.has_input('ticksSequence'):
            self.props['ticks'] = self.get_input('ticksSequence')
        elif self.has_input('ticksScalar'):
            self.props['ticks'] = self.get_input('ticksScalar')
        if self.has_input('axes'):
            self.constructor_props['axes'] = self.get_input('axes')
        if self.has_input('view_interval'):
            self.props['view_interval'] = self.get_input('view_interval')
        if self.has_input('major_locator'):
            self.props['major_locator'] = self.get_input('major_locator')
        if self.has_input('major_formatter'):
            self.props['major_formatter'] = self.get_input('major_formatter')
        if self.has_input('ticklabelsSequence'):
            self.props['ticklabels'] = self.get_input('ticklabelsSequence')
        elif self.has_input('ticklabelsScalar'):
            self.props['ticklabels'] = self.get_input('ticklabelsScalar')
        if self.has_input('clip_path'):
            self.props['clip_path'] = self.get_input('clip_path')
        if self.has_input('minor_locator'):
            self.props['minor_locator'] = self.get_input('minor_locator')
        if self.has_input('default_intervals'):
            self.props['default_intervals'] = self.get_input('default_intervals')
        if self.has_input('scale'):
            self.props['scale'] = self.get_input('scale')
        if self.has_input('data_interval'):
            self.props['data_interval'] = self.get_input('data_interval')
        if self.has_input('label_text'):
            self.props['label_text'] = self.get_input('label_text')
        if self.has_input('label_coords'):
            self.props['label_coords'] = self.get_input('label_coords')
        if self.has_input('units'):
            self.props['units'] = self.get_input('units')
        if self.has_input('tick_params'):
            self.props['tick_params'] = self.get_input('tick_params')

        
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
        if self.has_input('view_interval'):
            self.props['view_interval'] = self.get_input('view_interval')
        if self.has_input('ticks_position'):
            self.props['ticks_position'] = self.get_input('ticks_position')
        if self.has_input('axes'):
            self.constructor_props['axes'] = self.get_input('axes')
        if self.has_input('label_position'):
            self.props['label_position'] = self.get_input('label_position')
        if self.has_input('default_intervals'):
            self.props['default_intervals'] = self.get_input('default_intervals')
        if self.has_input('data_interval'):
            self.props['data_interval'] = self.get_input('data_interval')
        if self.has_input('pickradius'):
            self.constructor_props['pickradius'] = self.get_input('pickradius')

        
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
        if self.has_input('offset_position'):
            self.props['offset_position'] = self.get_input('offset_position')
        if self.has_input('view_interval'):
            self.props['view_interval'] = self.get_input('view_interval')
        if self.has_input('ticks_position'):
            self.props['ticks_position'] = self.get_input('ticks_position')
        if self.has_input('axes'):
            self.constructor_props['axes'] = self.get_input('axes')
        if self.has_input('label_position'):
            self.props['label_position'] = self.get_input('label_position')
        if self.has_input('default_intervals'):
            self.props['default_intervals'] = self.get_input('default_intervals')
        if self.has_input('data_interval'):
            self.props['data_interval'] = self.get_input('data_interval')
        if self.has_input('pickradius'):
            self.constructor_props['pickradius'] = self.get_input('pickradius')

        
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
                {'optional': True}),
              ("handlelength", "basic:String",
                {'optional': True}),
              ("labels", "basic:String",
                {'optional': True}),
              ("labelspacing", "basic:String",
                {'optional': True}),
              ("columnspacing", "basic:String",
                {'optional': True}),
              ("handletextpad", "basic:String",
                {'optional': True}),
              ("ncol", "basic:Integer",
                {'optional': True, 'defaults': "['1']"}),
              ("borderaxespad", "basic:String",
                {'optional': True}),
              ("loc", "basic:String",
                {'optional': True}),
              ("bbox_to_anchor", "basic:String",
                {'optional': True, 'docstring': 'set the bbox that the legend will be anchored.\n\nbbox can be a BboxBase instance, a tuple of [left, bottom, width, height] in the given transform (normalized axes coordinate if None), or a tuple of [left, bottom] where the width and height will be assumed to be zero.'}),
              ("title", "basic:String",
                {'optional': True, 'docstring': 'set the legend title. Fontproperties can be optionally set with prop parameter.'}),
              ("handletextsep", "basic:String",
                {'optional': True}),
              ("numpoints", "basic:String",
                {'optional': True}),
              ("prop", "basic:String",
                {'optional': True}),
              ("handles", "basic:String",
                {'optional': True}),
              ("pad", "basic:String",
                {'optional': True}),
              ("borderpad", "basic:String",
                {'optional': True}),
              ("parent", "basic:String",
                {'optional': True}),
              ("axespad", "basic:String",
                {'optional': True}),
              ("labelsep", "basic:String",
                {'optional': True}),
              ("frame_on", "basic:Boolean",
                {'optional': True, 'docstring': 'Set whether the legend box patch is drawn'}),
              ("scatterpoints", "basic:Integer",
                {'optional': True, 'defaults': "['3']"}),
              ("fontsize", "basic:String",
                {'optional': True}),
              ("shadow", "basic:String",
                {'optional': True}),
              ("handler_map", "basic:String",
                {'optional': True}),
              ("handleheight", "basic:String",
                {'optional': True}),
              ("scatteryoffsets", "basic:String",
                {'optional': True}),
              ("markerscale", "basic:String",
                {'optional': True}),
              ("frameon", "basic:String",
                {'optional': True}),
              ("mode", "basic:String",
                {'optional': True}),
              ("handlelen", "basic:String",
                {'optional': True}),
              ("default_handler_map", "basic:String",
                {'optional': True, 'docstring': 'A class method to set the default handler map.'}),
              ("bbox_transform", "basic:String",
                {'optional': True}),
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
        if self.has_input('fancybox'):
            self.constructor_props['fancybox'] = self.get_input('fancybox')
        if self.has_input('handlelength'):
            self.constructor_props['handlelength'] = self.get_input('handlelength')
        if self.has_input('labels'):
            self.constructor_props['labels'] = self.get_input('labels')
        if self.has_input('labelspacing'):
            self.constructor_props['labelspacing'] = self.get_input('labelspacing')
        if self.has_input('columnspacing'):
            self.constructor_props['columnspacing'] = self.get_input('columnspacing')
        if self.has_input('handletextpad'):
            self.constructor_props['handletextpad'] = self.get_input('handletextpad')
        if self.has_input('ncol'):
            self.constructor_props['ncol'] = self.get_input('ncol')
        if self.has_input('borderaxespad'):
            self.constructor_props['borderaxespad'] = self.get_input('borderaxespad')
        if self.has_input('loc'):
            self.constructor_props['loc'] = self.get_input('loc')
        if self.has_input('bbox_to_anchor'):
            self.props['bbox_to_anchor'] = self.get_input('bbox_to_anchor')
        if self.has_input('title'):
            self.props['title'] = self.get_input('title')
        if self.has_input('handletextsep'):
            self.constructor_props['handletextsep'] = self.get_input('handletextsep')
        if self.has_input('numpoints'):
            self.constructor_props['numpoints'] = self.get_input('numpoints')
        if self.has_input('prop'):
            self.constructor_props['prop'] = self.get_input('prop')
        if self.has_input('handles'):
            self.constructor_props['handles'] = self.get_input('handles')
        if self.has_input('pad'):
            self.constructor_props['pad'] = self.get_input('pad')
        if self.has_input('borderpad'):
            self.constructor_props['borderpad'] = self.get_input('borderpad')
        if self.has_input('parent'):
            self.constructor_props['parent'] = self.get_input('parent')
        if self.has_input('axespad'):
            self.constructor_props['axespad'] = self.get_input('axespad')
        if self.has_input('labelsep'):
            self.constructor_props['labelsep'] = self.get_input('labelsep')
        if self.has_input('frame_on'):
            self.props['frame_on'] = self.get_input('frame_on')
        if self.has_input('scatterpoints'):
            self.constructor_props['scatterpoints'] = self.get_input('scatterpoints')
        if self.has_input('fontsize'):
            self.constructor_props['fontsize'] = self.get_input('fontsize')
        if self.has_input('shadow'):
            self.constructor_props['shadow'] = self.get_input('shadow')
        if self.has_input('handler_map'):
            self.constructor_props['handler_map'] = self.get_input('handler_map')
        if self.has_input('handleheight'):
            self.constructor_props['handleheight'] = self.get_input('handleheight')
        if self.has_input('scatteryoffsets'):
            self.constructor_props['scatteryoffsets'] = self.get_input('scatteryoffsets')
        if self.has_input('markerscale'):
            self.constructor_props['markerscale'] = self.get_input('markerscale')
        if self.has_input('frameon'):
            self.constructor_props['frameon'] = self.get_input('frameon')
        if self.has_input('mode'):
            self.constructor_props['mode'] = self.get_input('mode')
        if self.has_input('handlelen'):
            self.constructor_props['handlelen'] = self.get_input('handlelen')
        if self.has_input('default_handler_map'):
            self.props['default_handler_map'] = self.get_input('default_handler_map')
        if self.has_input('bbox_transform'):
            self.constructor_props['bbox_transform'] = self.get_input('bbox_transform')

        
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
                {'optional': True, 'docstring': "Call signature:\n\nset_yscale(value)\n\nSet the scaling of the y-axis: 'linear' | 'log' | 'symlog' Different kwargs are accepted, depending on the scale: 'linear'\n\n'log'\n\n\n\n'symlog'"}),
              ("navigate", "basic:Boolean",
                {'optional': True, 'docstring': 'Set whether the axes responds to navigation toolbar commands'}),
              ("aspect", "basic:String",
                {'entry_types': "['enum']", 'docstring': "aspect\n\n\n\nadjustable\n\n\n\n'box' does not allow axes sharing, as this can cause unintended side effect. For cases when sharing axes is fine, use 'box-forced'.\n\nanchor", 'values': "[['auto', 'normal', 'equal', 'num']]", 'optional': True}),
              ("axis_bgcolor", "basic:Color",
                {'optional': True, 'docstring': 'set the axes background color'}),
              ("ylimSequence", "basic:List",
                {'optional': True, 'docstring': 'Call signature:\n\nset_ylim(self, *args, **kwargs):\n\nSet the data limits for the yaxis\n\nExamples:\n\nset_ylim((bottom, top)) set_ylim(bottom, top) set_ylim(bottom=1) # top unchanged set_ylim(top=1) # bottom unchanged\n\nKeyword arguments:\n\n\n\nNote, the bottom (formerly ymin) value may be greater than the top (formerly ymax). For example, suppose y is depth in the ocean. Then one might use:\n\nset_ylim(5000, 0)\n\nso 5000 m depth is at the bottom of the plot and the surface, 0 m, is at the top.\n\nReturns the current ylimits as a length 2 tuple'}),
              ("ylimScalar", "basic:Float",
               {'docstring': 'Call signature:\n\nset_ylim(self, *args, **kwargs):\n\nSet the data limits for the yaxis\n\nExamples:\n\nset_ylim((bottom, top)) set_ylim(bottom, top) set_ylim(bottom=1) # top unchanged set_ylim(top=1) # bottom unchanged\n\nKeyword arguments:\n\n\n\nNote, the bottom (formerly ymin) value may be greater than the top (formerly ymax). For example, suppose y is depth in the ocean. Then one might use:\n\nset_ylim(5000, 0)\n\nso 5000 m depth is at the bottom of the plot and the surface, 0 m, is at the top.\n\nReturns the current ylimits as a length 2 tuple', 'optional': True}),
              ("sharey", "basic:String",
                {'optional': True}),
              ("xlimSequence", "basic:List",
                {'optional': True, 'docstring': 'Call signature:\n\nset_xlim(self, *args, **kwargs):\n\nSet the data limits for the xaxis\n\nExamples:\n\nset_xlim((left, right)) set_xlim(left, right) set_xlim(left=1) # right unchanged set_xlim(right=1) # left unchanged\n\nKeyword arguments:\n\n\n\nNote, the left (formerly xmin) value may be greater than the right (formerly xmax). For example, suppose x is years before present. Then one might use:\n\nset_ylim(5000, 0)\n\nso 5000 years ago is on the left of the plot and the present is on the right.\n\nReturns the current xlimits as a length 2 tuple'}),
              ("xlimScalar", "basic:Float",
               {'docstring': 'Call signature:\n\nset_xlim(self, *args, **kwargs):\n\nSet the data limits for the xaxis\n\nExamples:\n\nset_xlim((left, right)) set_xlim(left, right) set_xlim(left=1) # right unchanged set_xlim(right=1) # left unchanged\n\nKeyword arguments:\n\n\n\nNote, the left (formerly xmin) value may be greater than the right (formerly xmax). For example, suppose x is years before present. Then one might use:\n\nset_ylim(5000, 0)\n\nso 5000 years ago is on the left of the plot and the present is on the right.\n\nReturns the current xlimits as a length 2 tuple', 'optional': True}),
              ("axis_on", "basic:String",
                {'optional': True, 'docstring': 'turn on the axis'}),
              ("title", "basic:String",
                {'optional': True, 'docstring': 'Call signature:\n\nset_title(label, fontdict=None, **kwargs):\n\nSet the title for the axes.'}),
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
                {'optional': True, 'docstring': 'Call signature:\n\nset_ylabel(ylabel, fontdict=None, labelpad=None, **kwargs)\n\nSet the label for the yaxis\n\nlabelpad is the spacing in points between the label and the y-axis'}),
              ("autoscalex_on", "basic:Boolean",
                {'optional': True, 'docstring': 'Set whether autoscaling for the x-axis is applied on plot commands'}),
              ("rasterization_zorder", "basic:String",
                {'optional': True, 'docstring': 'Set zorder value below which artists will be rasterized.  Set to None to disable rasterizing of artists below a particular zorder.'}),
              ("axes_locator", "basic:String",
                {'optional': True, 'docstring': 'set axes_locator'}),
              ("axisbelow", "basic:Boolean",
                {'optional': True, 'docstring': 'Set whether the axis ticks and gridlines are above or below most artists'}),
              ("frame_on", "basic:Boolean",
                {'optional': True, 'docstring': 'Set whether the axes rectangle patch is drawn'}),
              ("navigate_mode", "basic:String",
                {'optional': True, 'docstring': 'Set the navigation toolbar button status;\n\nthis is not a user-API function.'}),
              ("xscale", "basic:String",
                {'optional': True, 'docstring': "Call signature:\n\nset_xscale(value)\n\nSet the scaling of the x-axis: 'linear' | 'log' | 'symlog' Different kwargs are accepted, depending on the scale: 'linear'\n\n'log'\n\n\n\n'symlog'"}),
              ("axis_off", "basic:String",
                {'optional': True, 'docstring': 'turn off the axis'}),
              ("autoscale_on", "basic:Boolean",
                {'optional': True, 'docstring': 'Set whether autoscaling is applied on plot commands'}),
              ("ybound", "basic:String",
                {'optional': True, 'docstring': 'Set the lower and upper numerical bounds of the y-axis. This method will honor axes inversion regardless of parameter order. It will not change the _autoscaleYon attribute.'}),
              ("rect", "basic:String",
                {'optional': True}),
              ("sharex", "basic:String",
                {'optional': True}),
              ("yticklabelsSequence", "basic:List",
                {'optional': True, 'docstring': "Call signature:\n\nset_yticklabels(labels, fontdict=None, minor=False, **kwargs)\n\nSet the y tick labels with list of strings labels.  Return a list of :class:`~matplotlib.text.Text` instances.\n\nkwargs set :class:`~matplotlib.text.Text` properties for the labels. Valid properties are\n\nagg_filter: unknown alpha: float (0.0 transparent through 1.0 opaque) animated: [True | False] axes: an :class:`~matplotlib.axes.Axes` instance backgroundcolor: any matplotlib color bbox: rectangle prop dict clip_box: a :class:`matplotlib.transforms.Bbox` instance clip_on: [True | False] clip_path: [ (:class:`~matplotlib.path.Path`,         :class:`~matplotlib.transforms.Transform`) |         :class:`~matplotlib.patches.Patch` | None ] color: any matplotlib color contains: a callable function family or fontfamily or fontname or name: [ FONTNAME | 'serif' | 'sans-serif' | 'cursive' | 'fantasy' | 'monospace' ] figure: a :class:`matplotlib.figure.Figure` instance fontproperties or font_properties: a :class:`matplotlib.font_manager.FontProperties` instance gid: an id string horizontalalignment or ha: [ 'center' | 'right' | 'left' ] label: string or anything printable with '%s' conversion. linespacing: float (multiple of font size) lod: [True | False] multialignment: ['left' | 'right' | 'center' ] path_effects: unknown picker: [None|float|boolean|callable] position: (x,y) rasterized: [True | False | None] rotation: [ angle in degrees | 'vertical' | 'horizontal' ] rotation_mode: unknown size or fontsize: [ size in points | 'xx-small' | 'x-small' | 'small' | 'medium' | 'large' | 'x-large' | 'xx-large' ] snap: unknown stretch or fontstretch: [ a numeric value in range 0-1000 | 'ultra-condensed' | 'extra-condensed' | 'condensed' | 'semi-condensed' | 'normal' | 'semi-expanded' | 'expanded' | 'extra-expanded' | 'ultra-expanded' ] style or fontstyle: [ 'normal' | 'italic' | 'oblique'] text: string or anything printable with '%s' conversion. transform: :class:`~matplotlib.transforms.Transform` instance url: a url string variant or fontvariant: [ 'normal' | 'small-caps' ] verticalalignment or va or ma: [ 'center' | 'top' | 'bottom' | 'baseline' ] visible: [True | False] weight or fontweight: [ a numeric value in range 0-1000 | 'ultralight' | 'light' | 'normal' | 'regular' | 'book' | 'medium' | 'roman' | 'semibold' | 'demibold' | 'demi' | 'bold' | 'heavy' | 'extra bold' | 'black' ] x: float y: float zorder: any number"}),
              ("yticklabelsScalar", "basic:String",
               {'docstring': "Call signature:\n\nset_yticklabels(labels, fontdict=None, minor=False, **kwargs)\n\nSet the y tick labels with list of strings labels.  Return a list of :class:`~matplotlib.text.Text` instances.\n\nkwargs set :class:`~matplotlib.text.Text` properties for the labels. Valid properties are\n\nagg_filter: unknown alpha: float (0.0 transparent through 1.0 opaque) animated: [True | False] axes: an :class:`~matplotlib.axes.Axes` instance backgroundcolor: any matplotlib color bbox: rectangle prop dict clip_box: a :class:`matplotlib.transforms.Bbox` instance clip_on: [True | False] clip_path: [ (:class:`~matplotlib.path.Path`,         :class:`~matplotlib.transforms.Transform`) |         :class:`~matplotlib.patches.Patch` | None ] color: any matplotlib color contains: a callable function family or fontfamily or fontname or name: [ FONTNAME | 'serif' | 'sans-serif' | 'cursive' | 'fantasy' | 'monospace' ] figure: a :class:`matplotlib.figure.Figure` instance fontproperties or font_properties: a :class:`matplotlib.font_manager.FontProperties` instance gid: an id string horizontalalignment or ha: [ 'center' | 'right' | 'left' ] label: string or anything printable with '%s' conversion. linespacing: float (multiple of font size) lod: [True | False] multialignment: ['left' | 'right' | 'center' ] path_effects: unknown picker: [None|float|boolean|callable] position: (x,y) rasterized: [True | False | None] rotation: [ angle in degrees | 'vertical' | 'horizontal' ] rotation_mode: unknown size or fontsize: [ size in points | 'xx-small' | 'x-small' | 'small' | 'medium' | 'large' | 'x-large' | 'xx-large' ] snap: unknown stretch or fontstretch: [ a numeric value in range 0-1000 | 'ultra-condensed' | 'extra-condensed' | 'condensed' | 'semi-condensed' | 'normal' | 'semi-expanded' | 'expanded' | 'extra-expanded' | 'ultra-expanded' ] style or fontstyle: [ 'normal' | 'italic' | 'oblique'] text: string or anything printable with '%s' conversion. transform: :class:`~matplotlib.transforms.Transform` instance url: a url string variant or fontvariant: [ 'normal' | 'small-caps' ] verticalalignment or va or ma: [ 'center' | 'top' | 'bottom' | 'baseline' ] visible: [True | False] weight or fontweight: [ a numeric value in range 0-1000 | 'ultralight' | 'light' | 'normal' | 'regular' | 'book' | 'medium' | 'roman' | 'semibold' | 'demibold' | 'demi' | 'bold' | 'heavy' | 'extra bold' | 'black' ] x: float y: float zorder: any number", 'optional': True}),
              ("autoscaley_on", "basic:Boolean",
                {'optional': True, 'docstring': 'Set whether autoscaling for the y-axis is applied on plot commands'}),
              ("xmargin", "basic:Float",
                {'optional': True, 'docstring': 'Set padding of X data limits prior to autoscaling.\n\nm times the data interval will be added to each end of that interval before it is used in autoscaling.'}),
              ("color_cycle", "basic:Color",
                {'optional': True, 'docstring': 'Set the color cycle for any future plot commands on this Axes.\n\nclist is a list of mpl color specifiers.'}),
              ("frameon", "basic:Boolean",
                {'optional': True, 'defaults': "['True']"}),
              ("xlabel", "basic:String",
                {'optional': True, 'docstring': 'Call signature:\n\nset_xlabel(xlabel, fontdict=None, labelpad=None, **kwargs)\n\nSet the label for the xaxis.\n\nlabelpad is the spacing in points between the label and the x-axis'}),
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
                {'optional': True, 'docstring': "Call signature:\n\nset_xticklabels(labels, fontdict=None, minor=False, **kwargs)\n\nSet the xtick labels with list of strings labels. Return a list of axis text instances.\n\nkwargs set the :class:`~matplotlib.text.Text` properties. Valid properties are\n\nagg_filter: unknown alpha: float (0.0 transparent through 1.0 opaque) animated: [True | False] axes: an :class:`~matplotlib.axes.Axes` instance backgroundcolor: any matplotlib color bbox: rectangle prop dict clip_box: a :class:`matplotlib.transforms.Bbox` instance clip_on: [True | False] clip_path: [ (:class:`~matplotlib.path.Path`,         :class:`~matplotlib.transforms.Transform`) |         :class:`~matplotlib.patches.Patch` | None ] color: any matplotlib color contains: a callable function family or fontfamily or fontname or name: [ FONTNAME | 'serif' | 'sans-serif' | 'cursive' | 'fantasy' | 'monospace' ] figure: a :class:`matplotlib.figure.Figure` instance fontproperties or font_properties: a :class:`matplotlib.font_manager.FontProperties` instance gid: an id string horizontalalignment or ha: [ 'center' | 'right' | 'left' ] label: string or anything printable with '%s' conversion. linespacing: float (multiple of font size) lod: [True | False] multialignment: ['left' | 'right' | 'center' ] path_effects: unknown picker: [None|float|boolean|callable] position: (x,y) rasterized: [True | False | None] rotation: [ angle in degrees | 'vertical' | 'horizontal' ] rotation_mode: unknown size or fontsize: [ size in points | 'xx-small' | 'x-small' | 'small' | 'medium' | 'large' | 'x-large' | 'xx-large' ] snap: unknown stretch or fontstretch: [ a numeric value in range 0-1000 | 'ultra-condensed' | 'extra-condensed' | 'condensed' | 'semi-condensed' | 'normal' | 'semi-expanded' | 'expanded' | 'extra-expanded' | 'ultra-expanded' ] style or fontstyle: [ 'normal' | 'italic' | 'oblique'] text: string or anything printable with '%s' conversion. transform: :class:`~matplotlib.transforms.Transform` instance url: a url string variant or fontvariant: [ 'normal' | 'small-caps' ] verticalalignment or va or ma: [ 'center' | 'top' | 'bottom' | 'baseline' ] visible: [True | False] weight or fontweight: [ a numeric value in range 0-1000 | 'ultralight' | 'light' | 'normal' | 'regular' | 'book' | 'medium' | 'roman' | 'semibold' | 'demibold' | 'demi' | 'bold' | 'heavy' | 'extra bold' | 'black' ] x: float y: float zorder: any number"}),
              ("xticklabelsScalar", "basic:String",
               {'docstring': "Call signature:\n\nset_xticklabels(labels, fontdict=None, minor=False, **kwargs)\n\nSet the xtick labels with list of strings labels. Return a list of axis text instances.\n\nkwargs set the :class:`~matplotlib.text.Text` properties. Valid properties are\n\nagg_filter: unknown alpha: float (0.0 transparent through 1.0 opaque) animated: [True | False] axes: an :class:`~matplotlib.axes.Axes` instance backgroundcolor: any matplotlib color bbox: rectangle prop dict clip_box: a :class:`matplotlib.transforms.Bbox` instance clip_on: [True | False] clip_path: [ (:class:`~matplotlib.path.Path`,         :class:`~matplotlib.transforms.Transform`) |         :class:`~matplotlib.patches.Patch` | None ] color: any matplotlib color contains: a callable function family or fontfamily or fontname or name: [ FONTNAME | 'serif' | 'sans-serif' | 'cursive' | 'fantasy' | 'monospace' ] figure: a :class:`matplotlib.figure.Figure` instance fontproperties or font_properties: a :class:`matplotlib.font_manager.FontProperties` instance gid: an id string horizontalalignment or ha: [ 'center' | 'right' | 'left' ] label: string or anything printable with '%s' conversion. linespacing: float (multiple of font size) lod: [True | False] multialignment: ['left' | 'right' | 'center' ] path_effects: unknown picker: [None|float|boolean|callable] position: (x,y) rasterized: [True | False | None] rotation: [ angle in degrees | 'vertical' | 'horizontal' ] rotation_mode: unknown size or fontsize: [ size in points | 'xx-small' | 'x-small' | 'small' | 'medium' | 'large' | 'x-large' | 'xx-large' ] snap: unknown stretch or fontstretch: [ a numeric value in range 0-1000 | 'ultra-condensed' | 'extra-condensed' | 'condensed' | 'semi-condensed' | 'normal' | 'semi-expanded' | 'expanded' | 'extra-expanded' | 'ultra-expanded' ] style or fontstyle: [ 'normal' | 'italic' | 'oblique'] text: string or anything printable with '%s' conversion. transform: :class:`~matplotlib.transforms.Transform` instance url: a url string variant or fontvariant: [ 'normal' | 'small-caps' ] verticalalignment or va or ma: [ 'center' | 'top' | 'bottom' | 'baseline' ] visible: [True | False] weight or fontweight: [ a numeric value in range 0-1000 | 'ultralight' | 'light' | 'normal' | 'regular' | 'book' | 'medium' | 'roman' | 'semibold' | 'demibold' | 'demi' | 'bold' | 'heavy' | 'extra bold' | 'black' ] x: float y: float zorder: any number", 'optional': True}),
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
        if self.has_input('adjustable'):
            self.props['adjustable'] = self.get_input('adjustable')
        if self.has_input('cursor_props'):
            self.props['cursor_props'] = self.get_input('cursor_props')
        if self.has_input('figure'):
            self.props['figure'] = self.get_input('figure')
        if self.has_input('yscale'):
            self.props['yscale'] = self.get_input('yscale')
        if self.has_input('navigate'):
            self.props['navigate'] = self.get_input('navigate')
        if self.has_input('aspect'):
            self.props['aspect'] = self.get_input('aspect')
        if self.has_input('axis_bgcolor'):
            self.props['axis_bgcolor'] = self.get_input('axis_bgcolor')
            self.props['axis_bgcolor'] = translate_color(self.props['axis_bgcolor'])
        if self.has_input('ylimSequence'):
            self.props['ylim'] = self.get_input('ylimSequence')
        elif self.has_input('ylimScalar'):
            self.props['ylim'] = self.get_input('ylimScalar')
        if self.has_input('sharey'):
            self.constructor_props['sharey'] = self.get_input('sharey')
        if self.has_input('xlimSequence'):
            self.props['xlim'] = self.get_input('xlimSequence')
        elif self.has_input('xlimScalar'):
            self.props['xlim'] = self.get_input('xlimScalar')
        if self.has_input('axis_on'):
            self.props['axis_on'] = self.get_input('axis_on')
        if self.has_input('title'):
            self.props['title'] = self.get_input('title')
        if self.has_input('axisbg'):
            self.constructor_props['axisbg'] = self.get_input('axisbg')
        if self.has_input('label'):
            self.constructor_props['label'] = self.get_input('label')
        if self.has_input('xticksSequence'):
            self.props['xticks'] = self.get_input('xticksSequence')
        elif self.has_input('xticksScalar'):
            self.props['xticks'] = self.get_input('xticksScalar')
        if self.has_input('fig'):
            self.constructor_props['fig'] = self.get_input('fig')
        if self.has_input('ylabel'):
            self.props['ylabel'] = self.get_input('ylabel')
        if self.has_input('autoscalex_on'):
            self.props['autoscalex_on'] = self.get_input('autoscalex_on')
        if self.has_input('rasterization_zorder'):
            self.props['rasterization_zorder'] = self.get_input('rasterization_zorder')
        if self.has_input('axes_locator'):
            self.props['axes_locator'] = self.get_input('axes_locator')
        if self.has_input('axisbelow'):
            self.props['axisbelow'] = self.get_input('axisbelow')
        if self.has_input('frame_on'):
            self.props['frame_on'] = self.get_input('frame_on')
        if self.has_input('navigate_mode'):
            self.props['navigate_mode'] = self.get_input('navigate_mode')
        if self.has_input('xscale'):
            self.props['xscale'] = self.get_input('xscale')
        if self.has_input('axis_off'):
            self.props['axis_off'] = self.get_input('axis_off')
        if self.has_input('autoscale_on'):
            self.props['autoscale_on'] = self.get_input('autoscale_on')
        if self.has_input('ybound'):
            self.props['ybound'] = self.get_input('ybound')
        if self.has_input('rect'):
            self.constructor_props['rect'] = self.get_input('rect')
        if self.has_input('sharex'):
            self.constructor_props['sharex'] = self.get_input('sharex')
        if self.has_input('yticklabelsSequence'):
            self.props['yticklabels'] = self.get_input('yticklabelsSequence')
        elif self.has_input('yticklabelsScalar'):
            self.props['yticklabels'] = self.get_input('yticklabelsScalar')
        if self.has_input('autoscaley_on'):
            self.props['autoscaley_on'] = self.get_input('autoscaley_on')
        if self.has_input('xmargin'):
            self.props['xmargin'] = self.get_input('xmargin')
        if self.has_input('color_cycle'):
            self.props['color_cycle'] = self.get_input('color_cycle')
            self.props['color_cycle'] = translate_color(self.props['color_cycle'])
        if self.has_input('frameon'):
            self.constructor_props['frameon'] = self.get_input('frameon')
        if self.has_input('xlabel'):
            self.props['xlabel'] = self.get_input('xlabel')
        if self.has_input('xbound'):
            self.props['xbound'] = self.get_input('xbound')
        if self.has_input('yticksSequence'):
            self.props['yticks'] = self.get_input('yticksSequence')
        elif self.has_input('yticksScalar'):
            self.props['yticks'] = self.get_input('yticksScalar')
        if self.has_input('ymargin'):
            self.props['ymargin'] = self.get_input('ymargin')
        if self.has_input('position'):
            self.props['position'] = self.get_input('position')
        if self.has_input('anchor'):
            self.props['anchor'] = self.get_input('anchor')
            self.props['anchor'] = translate_MplAxesProperties_anchor(self.props['anchor'])
        if self.has_input('xticklabelsSequence'):
            self.props['xticklabels'] = self.get_input('xticklabelsSequence')
        elif self.has_input('xticklabelsScalar'):
            self.props['xticklabels'] = self.get_input('xticklabelsScalar')
        if self.has_input('titleProperties'):
            self.sub_props['title'] = self.get_input('titleProperties')

        
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
        if self.has_input('fig'):
            self.constructor_props['fig'] = self.get_input('fig')

        
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
       override the renderer.
    
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
              ("tight_layout", "basic:Boolean",
                {'optional': True, 'docstring': "Set whether :meth:`tight_layout` is used upon drawing. If None, the rcParams['figure.autolayout'] value will be set."}),
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
        if self.has_input('edgecolor'):
            self.props['edgecolor'] = self.get_input('edgecolor')
            self.props['edgecolor'] = translate_color(self.props['edgecolor'])
        if self.has_input('canvas'):
            self.props['canvas'] = self.get_input('canvas')
        if self.has_input('facecolor'):
            self.props['facecolor'] = self.get_input('facecolor')
            self.props['facecolor'] = translate_color(self.props['facecolor'])
        if self.has_input('size_inches'):
            self.props['size_inches'] = self.get_input('size_inches')
        if self.has_input('figwidth'):
            self.props['figwidth'] = self.get_input('figwidth')
        if self.has_input('frameon'):
            self.props['frameon'] = self.get_input('frameon')
        if self.has_input('subplotpars'):
            self.constructor_props['subplotpars'] = self.get_input('subplotpars')
        if self.has_input('figheight'):
            self.props['figheight'] = self.get_input('figheight')
        if self.has_input('figsize'):
            self.constructor_props['figsize'] = self.get_input('figsize')
        if self.has_input('linewidth'):
            self.constructor_props['linewidth'] = self.get_input('linewidth')
        if self.has_input('tight_layout'):
            self.props['tight_layout'] = self.get_input('tight_layout')
        if self.has_input('dpi'):
            self.props['dpi'] = self.get_input('dpi')

        
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
        if self.has_input('xycoords'):
            self.constructor_props['xycoords'] = self.get_input('xycoords')
        if self.has_input('figure'):
            self.props['figure'] = self.get_input('figure')
        if self.has_input('annotation_clip'):
            self.constructor_props['annotation_clip'] = self.get_input('annotation_clip')
        if self.has_input('xytext'):
            self.constructor_props['xytext'] = self.get_input('xytext')
        if self.has_input('s'):
            self.constructor_props['s'] = self.get_input('s')
        if self.has_input('xy'):
            self.constructor_props['xy'] = self.get_input('xy')
        if self.has_input('textcoords'):
            self.constructor_props['textcoords'] = self.get_input('textcoords')
        if self.has_input('arrowprops'):
            self.constructor_props['arrowprops'] = self.get_input('arrowprops')

        
    def update_props(self, objs):
        matplotlib.artist.setp(objs, **self.props)

    def update_kwargs(self, kwargs):
        kwargs.update(self.constructor_props)
        kwargs.update(self.props)


_modules = [
            MplArtistProperties,
            Mpl_AxesImageBaseProperties,
            MplAxesImageProperties,
            MplNonUniformImageProperties,
            MplBboxImageProperties,
            MplPcolorImageProperties,
            MplFigureImageProperties,
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
            MplTriMeshProperties,
            MplQuadMeshProperties,
            MplPatchProperties,
            MplShadowProperties,
            MplRectangleProperties,
            MplRegularPolygonProperties,
            MplCirclePolygonProperties,
            MplPathPatchProperties,
            MplPolygonProperties,
            MplFancyArrowProperties,
            MplWedgeProperties,
            MplArrowProperties,
            MplYAArrowProperties,
            MplEllipseProperties,
            MplCircleProperties,
            MplArcProperties,
            MplFancyBboxPatchProperties,
            MplFancyArrowPatchProperties,
            MplConnectionPatchProperties,
            MplLine2DProperties,
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
