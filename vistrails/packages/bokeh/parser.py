#!/usr/bin/env python
###############################################################################
##
## Copyright (C) 2014-2015, New York University.
## Copyright (C) 2011-2014, NYU-Poly.
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
##  - Neither the name of the New York University nor the names of its
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

from __future__ import division

from bokeh.properties import *
import os.path
import pydoc

from vistrails.core.wrapper.diff import apply_diff
from vistrails.core.wrapper.specs import SpecList, ClassSpec, \
    FunctionSpec
from vistrails.core.wrapper.python_parser import PythonParser, parse_googledoc

# minor modifications to default_key_to_type
key_to_type = [['file', 'basic:File'],
               ['array_like', 'basic:List'],
               ['ndarray', 'basic:List'],
               ['array', 'basic:List'],
               ['sequence', 'basic:List'],
               ['object', 'basic:List'],
               ['vector', 'basic:List'],
               ['Figure', 'plotting:Figure'],
               ['color', 'basic:Color'], # bokeh color ("#hexvalue")
               ['list', 'basic:List'],
               ['tuple', 'basic:List'],
               ['float', 'basic:Float'],
               ['scalar', 'basic:Float'],
               ['double', 'basic:Float'],
               ['integer', 'basic:Integer'],
               ['boolean', 'basic:Boolean'],
               ['bool', 'basic:Boolean'],
               ['dict', 'basic:Dictionary'],
               ['string', 'basic:String'],
               ['int', 'basic:Integer'],
               ['any', 'basic:Variant'], #
               ['str', 'basic:String']]

# append type to the name of alternate ports
alt_suffixes = {'basic:Integer': '_int',
                'basic:Float': '_float',
                'basic:String': '_str',
                'basic:Boolean': '_bool',
                'basic:List': '_list',
                'basic:Dictionary': '_dict'}


def parse_bokeh_property(prop):
    """ parse property into string that wrapper can understand
    """
    if prop.name == 'filename':
        return 'file'
    if hasattr(prop, 'descriptor'):
        prop = prop.descriptor
    if isinstance(prop, Color) or isinstance(prop, ColorSpec):
        # wrapper uses a 3 float color tuple with the color editor
        return 'color or str'
    if isinstance(prop, Enum):
        # wrapper needs {'x', 'y'}
        return str(prop).replace('Enum(', '{').replace(')', '}')
    if isinstance(prop, String):
        return 'str'
    if isinstance(prop, Interval):
        return str(prop.interval_type)
    if isinstance(prop, DataSpec):
        # DataSpec's can be lists
        # wrapper understands 'or'
        return ('string or dict or %(typ)s or list' %
                {'typ': str(prop.type_params[2])})
    if isinstance(prop, Either):
        # wrapper understands 'or'
        return ' or '.join([str(t) for t in reversed(prop.type_params)])
    prop_to_type = [
        [Regex, 'str'],
        [Complex, 'list'],
        [JSON, 'str'],
        [Size, 'float'],
        [Percent, 'float'],
        [DistanceSpec, 'float'],
        [Angle, 'float']]
    for key, val in prop_to_type:
        if isinstance(prop, key):
            return val
    return str(prop)


def bokeh_property_parser(obj):
    """ extract bokeh property information from an object
    """
    from bokeh.properties import Property
    args = []
    for argname in dir(obj):
        arg = getattr(obj, argname)
        if isinstance(arg, Property):
            doc = (arg.__doc__ or '').strip()
            if doc:
                desc = doc + '\n' + 'Property: ' + str(arg)
            else:
                desc = 'Property: ' + str(arg)
            prop = parse_bokeh_property(arg) + ', optional'
            default = arg.class_default(obj)
            if default is not None:
                desc = desc + '\ndefault is ' + repr(default)
            args.append((argname, prop, desc))
    # check for docstring references
    docstring = pydoc.getdoc(obj)
    if hasattr(obj, '__module__') and 'bokeh.charts.builders.' in obj.__module__:
        from bokeh.charts.chart_options import ChartOptions
        args.extend(bokeh_property_parser(ChartOptions)[1])
    if 'styling_line_properties' in docstring:
        from bokeh.mixins import LineProps
        args.extend(bokeh_property_parser(LineProps)[1])
    if 'styling_fill_properties' in docstring:
        from bokeh.mixins import FillProps
        args.extend(bokeh_property_parser(FillProps)[1])
    if 'styling_text_properties' in docstring:
        from bokeh.mixins import TextProps
        args.extend(bokeh_property_parser(TextProps)[1])
    return '', args, [], [], []


def parse_fig_method(f):
    """ Figure methods use properties from corresponding marker/glyph
    """
    from bokeh.models import markers
    from bokeh.models import glyphs
    # CamelCase translation works for almost all method names
    try:
        marker = getattr(markers, f.__name__)
    except:
        marker = getattr(glyphs, f.__name__)
    return bokeh_property_parser(marker)


translations = {'basic:Color': ('basic_Color_input', 'basic_Color_output'),
                'basic:Path': ('basic_Path_input', 'basic_Path_output')}

patch_name = os.path.realpath(os.path.join(os.path.dirname(__file__),
                                           'patch.py'))

def parser():
    """ Wraps Figure class, figure function, figure methods, and charts

    """
    parser = PythonParser(instance_type='plotting|Figure',
                          parsers=[bokeh_property_parser, parse_googledoc],
                          key_to_type=key_to_type,
                          alt_suffixes=alt_suffixes)
    this_dir = os.path.dirname(os.path.realpath(__file__))

    ##########################################################################
    # wrap classes

    class_spec_name = os.path.join(this_dir,'classes.xml')
    raw_class_spec_name = class_spec_name[:-4] + '-raw.xml'
    class_spec_diff = class_spec_name[:-4] +  '-diff.xml'

    # generate specs
    classes = []
    class_names = []
    functions = []
    func_names = []

    # wrap Figure class
    def add(base, clist, namespace):
        if isinstance(clist, basestring):
            clist = clist.split(',')
        for c in clist:
            klass = base + '.' + c
            if klass in class_names:
                print "Skipping duplicate:", klass
                continue
            class_names.append(klass)
            classes.append(parser.parse_class(klass,
                                              namespace=namespace,
                                              attribute_parsing=False))
            inspector = parser.parse_class(klass,
                                           name=c+'Inspector',
                                           namespace=namespace,
                                           argument_parsing=False)
            if (len(inspector.input_port_specs) > 1 or
                len(inspector.output_port_specs) > 1):
                classes.append(inspector)
            for f in parser.parse_class_methods(klass,
                                         namespace=namespace+'|'+c+'Methods'):
                fname = (f.namespace, f.module_name)
                if fname in func_names:
                    print "Skipping duplicate:", fname
                    continue
                func_names.append(fname)
                functions.append(f)
    #add('bokeh.plotting', 'Figure', namespace='plotting')

    # Wrap figure methods
    fig_method_parser = PythonParser(parsers=[parse_fig_method, parse_googledoc],
                                     key_to_type=key_to_type,
                                     alt_suffixes=alt_suffixes)
    from bokeh.plotting import Figure
    for name in dir(Figure):
        arg = getattr(Figure, name)
        if hasattr(arg, '__module__') and arg.__module__ == 'bokeh.plotting_helpers':
            functions.append(fig_method_parser.parse_function(
                                  arg,
                                  name=name,
                                  code_ref=name,
                                  namespace='plotting',
                                  method='plotting|Figure',
                                  is_empty=True,
                                  is_operation=True,
                                  output_type='plotting|Glyph'))

    fun_spec_name = os.path.join(this_dir, 'functions.xml')
    raw_fun_spec_name = fun_spec_name[:-4] + '-raw.xml'
    fun_spec_diff = fun_spec_name[:-4] + '-diff.xml'

    # wrap figure function
    # figure function gets properties from Figure class
    from bokeh.plotting import Figure
    parse_figure = lambda x: bokeh_property_parser(Figure)
    figure_parser = PythonParser(instance_type='plotting|Figure',
                                 parsers=[parse_figure, parse_googledoc],
                                 key_to_type=key_to_type,
                                 alt_suffixes=alt_suffixes)
    figure = figure_parser.parse_function('bokeh.plotting.figure',
                                          name='Figure',
                                          namespace='plotting',
                                          output_type='plotting|Figure',
                                          operations={'glyph': 'plotting|Glyph'})
    functions.append(figure)

    # wrap charts
    from bokeh import charts
    for name in dir(charts):
        chart = getattr(charts, name)
        if hasattr(chart, '__module__') and 'bokeh.charts.builders.' in chart.__module__:
            figure = parser.parse_function('bokeh.charts.' + name,
                                           namespace='charts',
                                           output_type='plotting|Figure')
            functions.append(figure)


    class_list = SpecList(classes, translations=translations)
    class_list.write_to_xml(raw_class_spec_name)
    apply_diff(ClassSpec, raw_class_spec_name, class_spec_diff, class_spec_name)
    fun_list = SpecList(functions, translations=translations)
    fun_list.write_to_xml(raw_fun_spec_name)
    apply_diff(FunctionSpec, raw_fun_spec_name, fun_spec_diff, fun_spec_name)
    return class_list, fun_list

if __name__ == '__main__':
    parser()
