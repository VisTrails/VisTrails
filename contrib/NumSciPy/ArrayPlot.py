import core.modules
import core.modules.module_registry
from core.modules.vistrails_module import Module, ModuleError
from core.modules.basic_modules import PythonSource
from Array import *
from Matrix import *

import pylab
import matplotlib
import urllib
import random

class ArrayPlot(object):
    namespace = 'numpy|array|plotting'
    def get_label(self, ar, i):
        lab = ar.get_name(i)
        if lab == None:
            return 'Array ' + str(i)
        else:
            return lab
            
    def is_cacheable(self):
        return False

    def get_color(self, colors, i, randomcolor):
        if randomcolor:
            return (random.random(), random.random(), random.random())

        if self.color_dict == None:
            self.color_dict = {}
            for (k,r,g,b) in colors:
                self.color_dict[k] = (r,g,b)

        if self.color_dict.has_key(i):
            return self.color_dict[i]
        else:
            return None
                
    def get_marker(self, markers, i):
        if markers == None:
            return None

        if self.marker_dict == None:
            self.marker_dict = {}
            for (k,m) in markers:
                self.marker_dict[k] = m

        if self.marker_dict.has_key(i):
            return self.marker_dict[i]
        else:
            return None

    def get_alpha(self, alphas, i):
        return None

class ArrayImage(ArrayPlot, Module):
    '''
    Display the 2D input Data Array as a color-mapped image.
    Independent control of the aspect ratio, colormap, presence of the
    colorbar and presented axis values are provided through the
    appropriate input ports: Aspect Ratio, Colormap, Colorbar,
    Extents.  To change the colormap being used, it must be one of the
    pre-made maps provided by matplotlib.cm.  Only 1 2D array can be
    viewed at a time.
    '''
    def compute(self):
        data = self.get_input("Data Array")
        da_ar = data.get_array().squeeze()
        if da_ar.ndim != 2:
            raise ModuleError("Input Data Array must have dimension = 2")

        aspect_ratio = self.force_get_input("Aspect Ratio")
        colormap = self.force_get_input("Colormap")
        colorbar = self.force_get_input("Colorbar")
        extents = self.force_get_input("Extents")

        # Quickly check the assigned colormap to make sure it's valid
        if colormap == None:
            colormap = "jet"
        if not hasattr(pylab, colormap):
            colormap = "jet"
            
        bg_color = self.force_get_input("Background")
        array_x_t = self.force_get_input("Use X Title")
        array_y_t = self.force_get_input("Use Y Title")

        p_title = self.force_get_input("Title")
        x_label = self.force_get_input("X Title")
        y_label = self.force_get_input("Y Title")
        
        s = urllib.unquote(str(self.force_get_input("source", '')))

        s = 'from pylab import *\n' +\
            'from numpy import *\n' +\
            'import numpy\n'
        
        if bg_color == None:
            bg_color = 'w'

        if type(bg_color) == type(''):
            s += 'figure(facecolor=\'' + bg_color + '\')\n'
        else:
            s += 'figure(facecolor=' + str(bg_color) + ')\n'

        s += 'imshow(da_ar, interpolation=\'bicubic\''
        if aspect_ratio != None:
            s += ', aspect=' + str(aspect_ratio)

        if extents != None:
            s += ', extent=['+str(extents[0])+','+str(extents[1])+','+str(extents[2])+','+str(extents[3])+']'
        s += ')\n'

        s += colormap + '()\n'

        if colorbar:
            s += 'colorbar()\n'

        if array_x_t:
            s += 'xlabel(\'' + data.get_domain_name() + '\')\n'
        elif x_label:
            s += 'xlabel(\'' + x_label + '\')\n'

        if array_y_t:
            s += 'ylabel(\'' + data.get_range_name() + '\')\n'
        elif y_label:
            s += 'ylabel(\'' + y_label + '\')\n'

        if p_title:
            s += 'title(\'' + p_title + '\')\n'

        exec s
        self.set_output('source', s)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.namespace)

    @classmethod
    def register_ports(cls, reg, basic):
        reg.add_input_port(cls, "source", (basic.String, 'source'), True)
        reg.add_input_port(cls, "Data Array", (NDArray, 'Array to Plot'))
        reg.add_input_port(cls, "Aspect Ratio", (basic.Float, 'Aspect Ratio'))
        reg.add_input_port(cls, "Colormap", (basic.String, 'Colormap'))
        reg.add_input_port(cls, "Colorbar", (basic.Boolean, 'Show Colorbar'), True)
        reg.add_input_port(cls, "Extents", [basic.Float, basic.Float, basic.Float, basic.Float], True)
        reg.add_input_port(cls, "Background", [basic.Float, basic.Float, basic.Float], True)
        reg.add_input_port(cls, "Use X Title", (basic.Boolean, 'Apply X-axis Label'))
        reg.add_input_port(cls, "Use Y Title", (basic.Boolean, 'Apply Y-axis Label'))
        reg.add_input_port(cls, "Title", (basic.String, 'Figure Title'))
        reg.add_input_port(cls, "X Title", (basic.String, 'X-axis label'), True)
        reg.add_input_port(cls, "Y Title", (basic.String, 'Y-axis label'), True)
        reg.add_output_port(cls, "source", (basic.String, 'source'))
        
class Histogram(ArrayPlot, Module):
    '''
    Plot a histogram of the data values.  Multiple datasets can be
    presented by providing multiple connections to the Data Array
    port.  These data are then differentiated by assigned colors and
    labels.  By default, 10 bins are used to histogram the data.
    Additionally, recapturing the PDF of the data is possible by
    enabling the Normalize option.
    '''
    def compute(self):
        data = self.get_input_list("Data Array")
        self.label_dict = None
        self.color_dict = None
        use_legend = self.force_get_input("Legend")
        randomcolors = self.force_get_input("Random Colors")
        colors = self.force_get_input_list("Colors")
        bg_color = self.force_get_input("Background")
        array_x_t = self.force_get_input("Use X Title")
        array_y_t = self.force_get_input("Use Y Title")
        p_title = self.force_get_input("Title")
        x_label = self.force_get_input("X Title")
        nbins = self.force_get_input("Bins")
        if nbins == None:
            nbins = 10
        normed = self.force_get_input("Normalize")
        if normed == None:
            normed = False

        s = urllib.unquote(str(self.force_get_input("source", '')))
        self.source = ''

        s = 'from pylab import *\n' +\
            'from numpy import *\n' +\
            'import numpy\n'
        
        if bg_color == None:
            bg_color = 'w'

        if type(bg_color) == type(''):
            s += 'figure(facecolor=\'' + bg_color + '\')\n'
        else:
            s += 'figure(facecolor=' + str(bg_color) + ')\n'

        data_list = []
        for i in data:
            data_list.append(i.get_array().squeeze())

        da_ar = None
        try:
            da_ar = numpy.array(data_list)
        except:
            raise ModuleException("Not all Data Array inputs are the same size!")

        for i in range(da_ar.shape[0]):
            lab = self.get_label(data[i], i)
            col = self.get_color(colors, i, randomcolors)

            s += 'hist(da_ar['+str(i)+',:], bins=' + str(nbins)
            
            if lab != None:
                s += ', label=\'' + lab + '\''
            if col != None:
                s += ', facecolor=' + str(col)

            s += ', normed='+str(normed)
            s += ')\n'

        if use_legend:
            s += 'legend()\n'

        if array_x_t:
            s += 'xlabel(\'' + data[0].get_domain_name() + '\')\n'
        elif x_label:
            s += 'xlabel(\'' + x_label + '\')\n'

        if array_y_t:
            s += 'ylabel(\'Histogram Value\')\n'

        if p_title:
            s += 'title(\'' + p_title + '\')\n'

        exec s
        self.set_output("source", s)        

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.namespace)

    @classmethod
    def register_ports(cls, reg, basic):
        reg.add_input_port(cls, "source", (basic.String, 'source'), True)
        reg.add_input_port(cls, "Data Array", (NDArray, 'Data Array to Plot'))
        reg.add_input_port(cls, "Legend", (basic.Boolean, 'Use Legend'), True)
        reg.add_input_port(cls, "Random Colors", (basic.Boolean, 'Assign Random Colors'), True)
        reg.add_input_port(cls, "Colors", [basic.Integer, basic.Float, basic.Float, basic.Float], True)
        reg.add_input_port(cls, "Background", [basic.Float, basic.Float, basic.Float], True)
        reg.add_input_port(cls, "Use X Title", (basic.Boolean, 'Apply X-axis Label'))
        reg.add_input_port(cls, "Use Y Title", (basic.Boolean, 'Apply Y-axis Label'))
        reg.add_input_port(cls, "Title", (basic.String, 'Figure Title'))
        reg.add_input_port(cls, "X Title", (basic.String, 'X-axis label'), True)
        reg.add_input_port(cls, "Bins", (basic.Integer, 'Number of Bins'))
        reg.add_input_port(cls, "Normalize", (basic.Boolean, 'Normalize to PDF'), True)
        reg.add_output_port(cls, "source", (basic.String, 'source'))
        
class BarChart(ArrayPlot, Module):
    '''
    Create a bar chart of the input data.  Different datasets can be
    used simultaneously by connecting to the Data input port multiple
    times.  Each successive data connection will be rendered on top of
    the previous dataset.  This creates a stacked bar chart.  Error
    bars are drawn with the errors for each of the datasets connected
    to the Error Bars input port.
    '''
    def get_ticks(self, num):
        a = []
        for i in range(num):
            a.append('')

        for i in self.tick_dict.keys():
            a[i] = self.tick_dict[i]

        return a
        
    def compute(self):
        data = self.get_input_list("Data")
        errs = self.force_get_input_list("Error Bars")
        if len(errs) == 0:
            errs = None

        self.label_dict = None
        self.color_dict = None
        use_legend = self.force_get_input("Legend")
        randomcolors = self.force_get_input("Random Colors")
        colors = self.force_get_input_list("Colors")
        bg_color = self.force_get_input("Background")
        array_x_t = self.force_get_input("Use X Title")
        array_y_t = self.force_get_input("Use Y Title")
        ticks = self.force_get_input_list("Bar Labels")
        self.tick_dict = {}
        for (k,v) in ticks:
            self.tick_dict[k] = v
        p_title = self.force_get_input("Title")
        x_label = self.force_get_input("X Title")
        y_label = self.force_get_input("Y Title")

        width = self.force_get_input("Bar Width")
        if width == None:
            width = 0.5

        if errs != None:
            if len(data) != len(errs):
                raise ModuleError("Number of data does not match number of error bar data")

        s = urllib.unquote(str(self.force_get_input("source", '')))
        self.source = ''

        s = 'from pylab import *\n' +\
            'from numpy import *\n' +\
            'import numpy\n'
        
        if bg_color == None:
            bg_color = 'w'

        if type(bg_color) == type(''):
            s += 'figure(facecolor=\'' + bg_color + '\')\n'
        else:
            s += 'figure(facecolor=' + str(bg_color) + ')\n'

        numpts = None
        ind = None
        prev = None
        ind = numpy.arange(data[0].get_array().flatten().shape[0])
        t = self.get_ticks(data[0].get_array().flatten().shape[0])
        ag_ar = numpy.zeros((len(data), data[0].get_array().flatten().shape[0]))
        for i in range(len(data)):
            da_ar = data[i].get_array().flatten()
            ag_ar[i,:] = da_ar

        er_ar = numpy.zeros((len(data), data[0].get_array().flatten().shape[0]))
        if errs != None:
            for i in range(len(data)):
                er_ar[i,:] = errs[i].get_array().flatten()
            
        for i in range(ag_ar.shape[0]):
            s += 'bar(ind, ag_ar[' + str(i) + ',:], width'
            lab = self.get_label(data[i], i)
            col = self.get_color(colors, i, randomcolors)
            if lab != None:
                s += ', label=\'' + lab + '\''
            if col != None:
                s += ', color=' + str(col)

            if errs != None:
                s += ', yerr=er_ar[' + str(i) + ',:]'

            if prev != None:
                s += ', bottom=ag_ar[' + str(i-1) + ',:]'

            s += ')\n'
            prev = ag_ar[i]
                
        if use_legend:
            s += 'legend()\n'

        if array_x_t:
            s += 'xlabel(\'' + data[0].get_domain_name() + '\')\n'
        elif x_label:
            s += 'xlabel(\'' + x_label + '\')\n'

        if array_y_t:
            s += 'ylabel(\'' + data[0].get_range_name() + '\')\n'
        elif y_label:
            s += 'ylabel(\'' + y_label + '\')\n'

        if p_title:
            s += 'title(\'' + p_title + '\')\n'

        s += 'xticks(ind + width/2., t)\n'
        exec s
        self.set_output("source", s)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.namespace)

    @classmethod
    def register_ports(cls, reg, basic):
        reg.add_input_port(cls, "source", (basic.String, 'source'), True)
        reg.add_input_port(cls, "Data", (NDArray, 'Data Array to Plot'))
        reg.add_input_port(cls, "Error Bars", (NDArray, 'Error Array to Plot'))
        reg.add_input_port(cls, "Legend", (basic.Boolean, 'Use Legend'), True)
        reg.add_input_port(cls, "Random Colors", (basic.Boolean, 'Assign Random Colors'), True)
        reg.add_input_port(cls, "Colors", [basic.Integer, basic.Float, basic.Float, basic.Float], True)
        reg.add_input_port(cls, "Background", [basic.Float, basic.Float, basic.Float], True)
        reg.add_input_port(cls, "Bar Labels", [basic.Integer, basic.String], True)
        reg.add_input_port(cls, "Use X Title", (basic.Boolean, 'Apply X-axis Label'))
        reg.add_input_port(cls, "Use Y Title", (basic.Boolean, 'Apply Y-axis Label'))
        reg.add_input_port(cls, "X Title", (basic.String, 'X-axis label'), True)
        reg.add_input_port(cls, "Y Title", (basic.String, 'Y-axis label'), True)
        reg.add_input_port(cls, "Title", (basic.String, 'Figure Title'))
        reg.add_input_port(cls, "Bar Width", (basic.Float, 'Bar Width'), True)
        reg.add_output_port(cls, "source", (basic.String, 'source'))
        
class ScatterPlot(ArrayPlot, Module):
    '''
    Create a scatter plot from X and Y positions defined by the X
    Array and Y Array ports, respectively.  Datasets can be added by
    connecting multiple arrays to the appropriate input ports.
    Symbols representing each dataset can be defined by using the
    Markers input assigning a valid pylab symbol to a dataset.
    '''
    def compute(self):
        xdata = self.get_input_list("X Array")
        ydata = self.get_input_list("Y Array")
        self.label_dict = None
        use_legend = self.force_get_input("Legend")
        randomcolors = self.force_get_input("Random Colors")
        colors = self.force_get_input_list("Colors")
        self.color_dict = None
        bg_color = self.force_get_input("Background")
        markers = self.force_get_input_list("Markers")
        self.marker_dict = None
        ps = self.force_get_input("Point Size")
        array_x_t = self.force_get_input("Use X Title")
        array_y_t = self.force_get_input("Use Y Title")

        p_title = self.force_get_input("Title")
        x_label = self.force_get_input("X Title")
        y_label = self.force_get_input("Y Title")

        s = urllib.unquote(str(self.force_get_input("source", '')))
        self.source = ''

        if len(xdata) != len(ydata):
            raise ModuleError("Cannot create scatter plot for different number of X and Y datasets.")

        s = 'from pylab import *\n' +\
            'from numpy import *\n' +\
            'import numpy\n'
        
        if bg_color == None:
            bg_color = 'w'

        if type(bg_color) == type(''):
            s += 'figure(facecolor=\'' + bg_color + '\')\n'
        else:
            s += 'figure(facecolor=' + str(bg_color) + ')\n'

        xdata_ar = numpy.zeros((len(xdata), xdata[0].get_array().flatten().shape[0]))
        ydata_ar = numpy.zeros((len(xdata), xdata[0].get_array().flatten().shape[0]))

        for i in range(len(xdata)):
            xd = xdata[i]
            yd = ydata[i]
            xdata_ar[i,:] = xd.get_array().flatten()
            ydata_ar[i,:] = yd.get_array().flatten()
            
        for i in range(len(xdata)):
            xar = xdata[i]
            yar = ydata[i]

            lab = self.get_label(xar, i)
            col = self.get_color(colors, i, randomcolors)
            mar = self.get_marker(markers, i)

            s += 'scatter(xdata_ar[' + str(i) +',:], ydata_ar[' + str(i) + ',:]'
            
            if lab != None:
                s += ', label=\'' + lab +'\''
            if col != None:
                s += ', color=' + str(col)
            if mar != None:
                s += ', marker=\'' + mar + '\''
            if ps != None:
                s += ', size=' + str(ps)
            s += ')\n'

        if use_legend:
            s += 'legend()\n'

        if array_x_t:
            s += 'xlabel(\'' + xar.get_domain_name() + '\')\n'
        elif x_label:
            s += 'xlabel(\'' + x_label + '\')\n'

        if array_y_t:
            s += 'ylabel(\'' + yar.get_domain_name() + '\')\n'
        elif y_label:
            s += 'ylabel(\'' + y_label + '\')\n'

        if p_title:
            s += 'title(\'' + p_title + '\')\n'

        print s
        exec s
        self.set_output("source", s)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.namespace)

    @classmethod
    def register_ports(cls, reg, basic):
        reg.add_input_port(cls, "source", (basic.String, 'source'), True)
        reg.add_input_port(cls, "X Array", (NDArray, 'X Array to Plot'))
        reg.add_input_port(cls, "Y Array", (NDArray, 'Y Array to Plot'))
        reg.add_input_port(cls, "Legend", (basic.Boolean, 'Use Legend'), True)
        reg.add_input_port(cls, "Random Colors", (basic.Boolean, 'Assign Random Colors'), True)
        reg.add_input_port(cls, "Colors", [basic.Integer, basic.Float, basic.Float, basic.Float], True)
        reg.add_input_port(cls, "Background", [basic.Float, basic.Float, basic.Float], True)
        reg.add_input_port(cls, "Markers", [basic.Integer, basic.String], True)
        reg.add_input_port(cls, "Use X Title", (basic.Boolean, 'Apply X-axis Label'))
        reg.add_input_port(cls, "Use Y Title", (basic.Boolean, 'Apply Y-axis Label'))
        reg.add_input_port(cls, "X Title", (basic.String, 'X-axis label'), True)
        reg.add_input_port(cls, "Y Title", (basic.String, 'Y-axis label'), True)
        reg.add_input_port(cls, "Title", (basic.String, 'Figure Title'))
        reg.add_input_port(cls, "Point Size", (basic.Float, 'Point Size'), True)
        reg.add_output_port(cls, "source", (basic.String, 'source'))

class LinePlot(ArrayPlot, Module):
    '''
    Create a standard line plot from a 1 or 2-dimensional Input Array.
    If the Input Array is 2-dimensional, each row will be plotted as a
    new line.
    '''    
    def compute(self):
        data = self.get_input("Input Array")
        indexes = self.force_get_input("Indexes")
        self.label_dict = None
        use_legend = self.force_get_input("Legend")
        randomcolors = self.force_get_input("Random Colors")
        colors = self.force_get_input_list("Colors")
        self.color_dict = None
        markers = self.force_get_input_list("Markers")
        self.marker_dict = None
        x_label = self.force_get_input("X Title")
        y_label = self.force_get_input("Y Title")
        p_title = self.force_get_input("Title")
        bg_color = self.force_get_input("Background")

        array_x_t = self.force_get_input("Use X Title")
        array_y_t = self.force_get_input("Use Y Title")

        s = urllib.unquote(str(self.force_get_input("source", '')))
        self.source = ''
        da_ar = data.get_array()

        if da_ar.ndim > 2:
            raise ModuleError("Cannot plot data with dimensions > 2")
        
        s = 'from pylab import *\n' +\
            'from numpy import *\n' +\
            'import numpy\n'
        
        if bg_color == None:
            bg_color = 'w'

        if type(bg_color) == type(''):
            s += 'figure(facecolor=\'' + bg_color + '\')\n'
        else:
            s += 'figure(facecolor=' + str(bg_color) + ')\n'
            
        if da_ar.ndim == 1:
            da_ar.shape = (1, da_ar.shape[0])

        xar = self.force_get_input("X Values")
        sf = self.force_get_input("Scaling Factor")
        if sf == None:
            sf = 1.

        if xar == None:
            start_i = None
            end_i = None
            if indexes == None:
                start_i = 0
                end_i = da_ar.shape[1]
            else:
                start_i = indexes[0]
                end_i = indexes[1]

            xar = numpy.arange(start_i, end_i)
            xar = xar * sf
        else:
            xar = xar.get_array()
        
        print da_ar.shape
        print xar.shape
        for i in range(da_ar.shape[0]):
            lab = self.get_label(data, i)
            col = self.get_color(colors, i, randomcolors)
            mar = self.get_marker(markers, i)
            if indexes == None:
                s += 'plot(xar, da_ar[' + str(i) + ',:]'
            else:
                s += 'plot(xar, da_ar[' + str(i) + ',' + str(indexes[0]) + ':' + str(indexes[1]) + ']'
                
            if lab != None:
                s += ', label=\'' + lab +'\''
            if col != None:
                s += ', color=' + str(col)
            if mar != None:
                s += ', marker=\'' + mar + '\''
            s += ')\n'

        if use_legend:
            s += 'legend()\n'

        if array_x_t:
            s += 'xlabel(\'' + data.get_domain_name() + '\')\n'
        elif x_label:
            s += 'xlabel(\'' + x_label + '\')\n'

        if array_y_t:
            s += 'ylabel(\'' + data.get_range_name() + '\')\n'
        elif y_label:
            s += 'ylabel(\'' + y_label + '\')\n'

        if p_title:
            s += 'title(\'' + p_title + '\')\n'

        exec s
        self.set_output("source", s)

    @classmethod
    def register(cls, reg, basic):
        reg.add_module(cls, namespace=cls.namespace)

    @classmethod
    def register_ports(cls, reg, basic):
        reg.add_input_port(cls, "source", (basic.String, 'source'), True)
        reg.add_input_port(cls, "Input Array", (NDArray, 'Array to Plot'))
        reg.add_input_port(cls, "X Values", (NDArray, 'Domain Values'))
        reg.add_input_port(cls, "Legend", (basic.Boolean, 'Use Legend'), True)
        reg.add_input_port(cls, "Random Colors", (basic.Boolean, 'Assign Random Colors'), True)
        reg.add_input_port(cls, "Colors", [basic.Integer, basic.Float, basic.Float, basic.Float], True)
        reg.add_input_port(cls, "Markers", [basic.Integer, basic.String], True)
        reg.add_input_port(cls, "Use X Title", (basic.Boolean, 'Apply X-axis Label'))
        reg.add_input_port(cls, "Use Y Title", (basic.Boolean, 'Apply Y-axis Label'))
        reg.add_input_port(cls, "X Title", (basic.String, 'X-axis label'), True)
        reg.add_input_port(cls, "Y Title", (basic.String, 'Y-axis label'), True)
        reg.add_input_port(cls, "Title", (basic.String, 'Figure Title'))
        reg.add_input_port(cls, "Background", [basic.Float, basic.Float, basic.Float], True)
        reg.add_input_port(cls, "Indexes", [basic.Integer, basic.Integer], True)
        reg.add_input_port(cls, "Scaling Factor", (basic.Float, 'Scaling Factor'), True)
        reg.add_output_port(cls, "source", (basic.String, 'source'))
