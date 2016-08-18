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

import os.path

from vistrails.core.modules.vistrails_module import Module
from vistrails.core.modules.config import ModuleSettings
from vistrails.core.modules.module_registry import get_module_registry
from vistrails.core.modules.output_modules import OutputModule, \
    IPythonMode, OutputMode, OutputModeConfig, ConfigField
from vistrails.core.wrapper.specs import SpecList, ClassSpec, \
    FunctionSpec
from vistrails.core.wrapper.pythonclass import gen_class_module
from vistrails.core.wrapper.pythonfunction import gen_function_module


from identifiers import *

this_dir = os.path.dirname(os.path.realpath(__file__))
_modules = []

class Glyph(Module):
    """ Bokeh glyph function

    """
    _settings = ModuleSettings(namespace='plotting', abstract=True)

_modules.append(Glyph)

class_spec_name = os.path.join(this_dir,'classes.xml')
class_list = SpecList.read_from_xml(class_spec_name, ClassSpec)
_modules.extend([gen_class_module(spec,
                                  patches=class_list.patches,
                                  translations=class_list.translations,
) for spec in class_list.module_specs])

func_spec_name = os.path.join(this_dir,'functions.xml')
func_list = SpecList.read_from_xml(func_spec_name, FunctionSpec)
_modules.extend([gen_function_module(spec,
                                     patches=func_list.patches,
                                     translations=func_list.translations)
                 for spec in func_list.module_specs])

from vistrails.packages.spreadsheet.widgets.webview.webview import WebViewCellWidget

################# OUTPUT MODULES #############################################


class bokehBrowserModeConfig(OutputModeConfig):
    """ Bokeh browser output options
    browser - the browser type to use (e.g. 'firefox')

    """
    mode_type = "browser"
    _fields = [ConfigField('browser', None, str)]


class bokehToBrowserMode(OutputMode):
    """ Show Bokeh plot in external browser

    """
    priority = 200
    mode_type = "browser"
    config_cls = bokehBrowserModeConfig

    @staticmethod
    def can_compute():
        return True

    def compute_output(self, output_module, configuration):
        plot = output_module.get_input('plot')
        from bokeh.plotting import show, output_file
        po = output_module.interpreter.filePool.create_file(suffix='.html')
        output_file(po.name, mode='inline')
        kwargs = {}
        if configuration['browser']:
            kwargs['browser'] = configuration['browser']
        show(plot, **kwargs)


class bokehToIPythonMode(IPythonMode):
    """ Show Bokeh plot in ipython notebook
    Only works after calling output_notebook()
    Must use output_notebook(resources=INLINE) until 0.11 is released

    """
    def compute_output(self, output_module, configuration):
        plot = output_module.get_input('plot')
        from bokeh.plotting import show
        show(plot)


class BokehOutput(OutputModule):
    """ Bokeh plot output modes

    """
    _settings = ModuleSettings(configure_widget="vistrails.gui.modules."
                       "output_configuration:OutputModuleConfigurationWidget")
    _input_ports = [('plot', 'plotting|Figure')]
    _output_modes = [bokehToBrowserMode, bokehToIPythonMode]

    if get_module_registry().has_module('org.vistrails.vistrails.spreadsheet',
                           'SpreadsheetCell'):
        from vistrails.packages.spreadsheet.basic_widgets import SpreadsheetMode

        class bokehToSpreadsheetMode(SpreadsheetMode):
            def compute_output(self, output_module, configuration):
                plot = output_module.get_input('plot')
                # TODO: Use CDN when 0.11 is released
                from bokeh.resources import INLINE
                from bokeh.embed import file_html
                html = file_html(plot, INLINE, "my plot")
                po = output_module.interpreter.filePool.create_file(suffix='.html')
                with open(po.name, 'w') as f:
                    f.write(html)
                self.display_and_wait(output_module, configuration,
                                                WebViewCellWidget, (None, po))
        _output_modes.append(bokehToSpreadsheetMode)


class Glyph(Module):
    """ Bokeh glyph function

    """
    _settings = ModuleSettings(abstract=True)

_modules.append(BokehOutput)
