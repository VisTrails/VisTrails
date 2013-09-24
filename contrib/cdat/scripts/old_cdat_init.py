############################################################################
##
## Copyright (C) 2006-2007 University of Utah. All rights reserved.
##
## This file is part of VisTrails.
##
## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of
## this file.  Please review the following to ensure GNU General Public
## Licensing requirements will be met:
## http://www.opensource.org/licenses/gpl-license.php
##
## If you are unsure which license is appropriate for your use (for
## instance, you are interested in developing a commercial derivative
## of VisTrails), please contact us at contact@vistrails.org.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################

import core.modules
import core.modules.module_registry
from core.modules.vistrails_module import Module, ModuleError
import vcs, cdms, cdutil
import inspect
import os, sys

class cdms_dataarray(Module) :
  def __init__(self, arr) :
    self.arr = arr

class cdms_dataset(Module) :
  def __init__(self, dataset) :
    self.dataset = dataset
  def slice(self, id, kwargs) :
    dummy = []
    return self.dataset(id, *dummy, **kwargs)

class cdms_get_data(Module) :
  def compute(self) :
    if not self.hasInputFromPort('id') :
      print "Error: must have id input"
      return

    if not self.hasInputFromPort('dataset') :
      print "Error: must have dataset input"
      return
    id = self.get_input('id')
    dataset = self.get_input('dataset')
    kwargs = {}

    if (self.hasInputFromPort('arg_key_1') and
        self.hasInputFromPort('arg_val_1')) :
      
      k = self.get_input('arg_key_1')
      t = self.get_input('arg_val_1')
      kwargs[k] = t


    if (self.hasInputFromPort('arg_key_2') and
        self.hasInputFromPort('arg_val_2')) :
      
      k = self.get_input('arg_key_2')
      t = self.get_input('arg_val_2')
      kwargs[k] = t


    if (self.hasInputFromPort('arg_key_3') and
        self.hasInputFromPort('arg_val_3')) :
      
      k = self.get_input('arg_key_3')
      t = self.get_input('arg_val_3')
      kwargs[k] = t
      
    dummy = []
    arr = dataset.slice(id, kwargs)
    darr = cdms_dataarray(arr)
    self.setResult("cdms_dataarray", darr)

class cdms_open(Module) :
  def compute(self) :
    args = inspect.getargspec(cdms.open)
    def_args = args[3]
    uri = None
    mode = def_args[0]
    template = def_args[1]
    dods = def_args[2]

    if not self.hasInputFromPort('uri') :
      print "Error: must have uri input"
      return
      
    if self.hasInputFromPort('uri') :
      inuri = self.get_input('uri')
      uri = os.path.join(sys.prefix, inuri)
    if self.hasInputFromPort('mode') :
      mode = self.get_input('mode')
    if self.hasInputFromPort('template') :
      template = self.get_input('template')
    if self.hasInputFromPort('dods') :
      dods = self.get_input('dods')

    # output the cdmsfile object.
    cdmsfile = cdms.open(uri,mode,template,dods)
    output = cdms_dataset(cdmsfile)
    self.setResult("cdms_dataset", output)

# just wrap whatever so it can be sent downstream
class generic_port(Module) :
  def __init__(self, data) :
    self.data = data
    
class vcs_canvas(Module) :
  def __init__(self) :
    Module.__init__(self)
    self.canvas = None

  def compute(self):
    if self.canvas == None :
      print "calling vcs.init()"
      self.canvas = vcs.init()
    self.setResult("vcs_canvas", self)


class vcs_canvas_getboxfill(Module) :
  def compute(self) :
    if not self.hasInputFromPort('canvas') :
      print "ERROR: Must have canvas input port"
      return

    bname = None
    if self.hasInputFromPort('boxfill name') :
      bname = self.get_input('boxfill name')
    vcs_c = self.get_input('canvas')

    if bname == None :
      bfm = vcs_c.canvas.getboxfill()
    else :
      bfm = vcs_c.canvas.getboxfill(bname)

    out = generic_port(bfm)
    self.setResult("boxfill graphics method", out)

class vcs_canvas_gettemplate(Module) :
  def compute(self) :
    if not self.hasInputFromPort('canvas') :
      print "ERROR: Must have canvas input port"
      return

    tname = None
    if self.hasInputFromPort('template name') :
      tname = self.get_input('template name')
    vcs_c = self.get_input('canvas')

    if tname == None :
      t = vcs_c.canvas.gettemplate()
    else :
      t = vcs_c.canvas.gettemplate(tname)

    out = generic_port(t)
    self.setResult("template", out)
  
class vcs_canvas_plot(Module) :
  def compute(self) :

    canvas = self.get_input('vcs_canvas').canvas
    data1 = self.get_input('array1').arr
    data2 = None
    if self.hasInputFromPort('array2') :
      data2 = self.get_input('array2').arr
      
    gm = self.get_input('graphics_method').data
    t = self.get_input('template_name').data


    # build up the kewword arguments from the optional inputs.
    kwargs = {}
    kwargs['bg'] = 1
    if self.hasInputFromPort('ratio') :
      kwargs['ratio'] = self.get_input('ratio')

    #variable attribute keys
    if self.hasInputFromPort('comment1') :
      kwargs['comment1'] = self.get_input('comment1')
    if self.hasInputFromPort('comment2') :
      kwargs['comment2'] = self.get_input('comment2')
    if self.hasInputFromPort('comment3') :
      kwargs['comment3'] = self.get_input('comment3')
    if self.hasInputFromPort('comment4') :
      kwargs['comment4'] = self.get_input('comment4')
    if self.hasInputFromPort('file_comment') :
      kwargs['file_comment'] = self.get_input('file_comment')
    if self.hasInputFromPort('hms') :
      kwargs['hms'] = self.get_input('hms')
    if self.hasInputFromPort('long_name') :
      kwargs['long_name'] = self.get_input('long_name')
    if self.hasInputFromPort('name') :
      kwargs['name'] = self.get_input('name')
    if self.hasInputFromPort('time') :
      kwargs['time'] = self.get_input('time')
    if self.hasInputFromPort('units') :
      kwargs['units'] = self.get_input('units')
    if self.hasInputFromPort('ymd') :
      kwargs['ymd'] = self.get_input('ymd')

    # dimension attribute keys
    if self.hasInputFromPort('xarray1') :
      kwargs['xarray1'] = self.get_input('xarray1')
    if self.hasInputFromPort('yarray1') :
      kwargs['yarray1'] = self.get_input('yarray1')
    if self.hasInputFromPort('zarray1') :
      kwargs['zarray1'] = self.get_input('zarray1')
    if self.hasInputFromPort('tarray1') :
      kwargs['tarray1'] = self.get_input('tarray1')
    if self.hasInputFromPort('warray1') :
      kwargs['warray1'] = self.get_input('warray1')
    if self.hasInputFromPort('xarray2') :
      kwargs['xarray2'] = self.get_input('xarray2')
    if self.hasInputFromPort('yarray2') :
      kwargs['yarray2'] = self.get_input('yarray2')
    if self.hasInputFromPort('zarray2') :
      kwargs['zarray2'] = self.get_input('zarray2')
    if self.hasInputFromPort('tarray2') :
      kwargs['tarray2'] = self.get_input('tarray2')
    if self.hasInputFromPort('warray2') :
      kwargs['warray2'] = self.get_input('warray2')
    if self.hasInputFromPort('xbounds') :
      kwargs['xbounds'] = self.get_input('xbounds')
    if self.hasInputFromPort('ybounds') :
      kwargs['ybounds'] = self.get_input('ybounds')
    if self.hasInputFromPort('xname') :
      kwargs['xname'] = self.get_input('xname')
    if self.hasInputFromPort('yname') :
      kwargs['yname'] = self.get_input('yname')
    if self.hasInputFromPort('zname') :
      kwargs['zname'] = self.get_input('zname')
    if self.hasInputFromPort('tname') :
      kwargs['tname'] = self.get_input('tname')
    if self.hasInputFromPort('wname') :
      kwargs['wname'] = self.get_input('wname')
    if self.hasInputFromPort('xunits') :
      kwargs['xunits'] = self.get_input('xunits')
    if self.hasInputFromPort('yunits') :
      kwargs['yunits'] = self.get_input('yunits')
    if self.hasInputFromPort('zunits') :
      kwargs['zunits'] = self.get_input('zunits')
    if self.hasInputFromPort('tunits') :
      kwargs['tunits'] = self.get_input('tunits')
    if self.hasInputFromPort('wunits') :
      kwargs['wunits'] = self.get_input('wunits')
    if self.hasInputFromPort('xweights') :
      kwargs['xweights'] = self.get_input('xweights')
    if self.hasInputFromPort('yweights') :
      kwargs['yweights'] = self.get_input('yweights')

    if data2 == None :
      canvas.plot(data1, gm, t, **kwargs)
    else :
      canvas.plot(data1, data2, gm, t, **kwargs)
    o = self.interpreter.filePool.create_file(suffix='.cdat.gif')
    canvas.gif(o.name)
    self.setResult("image", o)
    

def initialize(*args, **keywords):
  reg = core.modules.module_registry


  reg.addModule(cdms_open)
  reg.addInputPort(cdms_open, 'dods',
                   (core.modules.basic_modules.String, 'tip'))
  reg.addInputPort(cdms_open, 'template',
                   (core.modules.basic_modules.String, 'tip'))
  reg.addInputPort(cdms_open, 'mode',
                   (core.modules.basic_modules.String, 'tip'))
  reg.addInputPort(cdms_open, 'uri',
                   (core.modules.basic_modules.String, 'tip'))

  # output dataset.
  reg.addOutputPort(cdms_open, "cdms_dataset",
                    (cdms_dataset, 'cdms.dataset'))
  #holds the tetgenio class, and acts as a port. 
  reg.addModule(cdms_dataset)

  reg.addModule(cdms_get_data)
  reg.addInputPort(cdms_get_data, 'dataset',
                   (cdms_dataset, 'dataset'))
  reg.addInputPort(cdms_get_data, 'id',
                   (core.modules.basic_modules.String, 'dataset id'))

  reg.addInputPort(cdms_get_data, 'arg_key_1',
                   (core.modules.basic_modules.String, 'argument 1 key'))
  reg.addInputPort(cdms_get_data, 'arg_val_1',
                   ([core.modules.basic_modules.Float,
                     core.modules.basic_modules.Float]))
  
  reg.addInputPort(cdms_get_data, 'arg_key_2',
                   (core.modules.basic_modules.String, 'argument 2 key'))
  reg.addInputPort(cdms_get_data, 'arg_val_2',
                   ([core.modules.basic_modules.Float,
                     core.modules.basic_modules.Float]))

  reg.addInputPort(cdms_get_data, 'arg_key_3',
                   (core.modules.basic_modules.String, 'argument 3 key'))
  reg.addInputPort(cdms_get_data, 'arg_val_3',
                   ([core.modules.basic_modules.Float,
                     core.modules.basic_modules.Float]))
  # output data array.
  reg.addOutputPort(cdms_get_data, "cdms_dataarray",
                    (cdms_dataarray, 'data'))


  # port for passing data arrays
  reg.addModule(cdms_dataarray)
  # port for passing anything
  reg.addModule(generic_port)
  #canvas module
  reg.addModule(vcs_canvas)
  reg.addOutputPort(vcs_canvas, "vcs_canvas",
                    (vcs_canvas, 'the canvas'))

  #canvas module methods...
  reg.addModule(vcs_canvas_getboxfill)
  reg.addInputPort(vcs_canvas_getboxfill, 'canvas',
                   (vcs_canvas, 'the canvas'))
  reg.addInputPort(vcs_canvas_getboxfill, 'boxfill name',
                   (core.modules.basic_modules.String, 'boxfill method name'))

  reg.addOutputPort(vcs_canvas_getboxfill, "boxfill graphics method",
                    (generic_port, 'graphics method'))

  reg.addModule(vcs_canvas_gettemplate)
  reg.addInputPort(vcs_canvas_gettemplate, 'canvas',
                   (vcs_canvas, 'the canvas'))
  reg.addInputPort(vcs_canvas_gettemplate, 'template name',
                   (core.modules.basic_modules.String, 'template name'))

  reg.addOutputPort(vcs_canvas_gettemplate, "template",
                    (generic_port, 'template'))


  reg.addModule(vcs_canvas_plot)
  reg.addInputPort(vcs_canvas_plot, 'vcs_canvas',
                   vcs_canvas)
  reg.addInputPort(vcs_canvas_plot, 'array1',
                   cdms_dataarray)
  reg.addInputPort(vcs_canvas_plot, 'array2',
                   cdms_dataarray)
  reg.addInputPort(vcs_canvas_plot, 'template_name',
                   generic_port)
  reg.addInputPort(vcs_canvas_plot, 'graphics_method',
                   generic_port)
  reg.addInputPort(vcs_canvas_plot, 'graphics_name',
                   generic_port)

  # keyword args 
  reg.addInputPort(vcs_canvas_plot, 'ratio',
                   core.modules.basic_modules.String, True)

  # Variable attribute keys
  reg.addInputPort(vcs_canvas_plot, 'comment1',
                   core.modules.basic_modules.String, True)
  
  reg.addInputPort(vcs_canvas_plot, 'comment2',
                   core.modules.basic_modules.String, True)
  
  reg.addInputPort(vcs_canvas_plot, 'comment3',
                   core.modules.basic_modules.String, True)
  
  reg.addInputPort(vcs_canvas_plot, 'comment4',
                   core.modules.basic_modules.String, True)
  
  reg.addInputPort(vcs_canvas_plot, 'file_comment',
                   core.modules.basic_modules.String, True)
  
  reg.addInputPort(vcs_canvas_plot, 'hms',
                   core.modules.basic_modules.String, True)
  
  reg.addInputPort(vcs_canvas_plot, 'long_name',
                   core.modules.basic_modules.String, True)
  
  reg.addInputPort(vcs_canvas_plot, 'name',
                   core.modules.basic_modules.String, True)
  
  reg.addInputPort(vcs_canvas_plot, 'time',
                   core.modules.basic_modules.String, True)
  
  reg.addInputPort(vcs_canvas_plot, 'units',
                   core.modules.basic_modules.String, True)
  
  reg.addInputPort(vcs_canvas_plot, 'ymd',
                   core.modules.basic_modules.String, True)

  # Dimension attribuge keys
  reg.addInputPort(vcs_canvas_plot, 'xarray1',
                   cdms_dataarray, True)
  reg.addInputPort(vcs_canvas_plot, 'yarray1',
                   cdms_dataarray, True)
  reg.addInputPort(vcs_canvas_plot, 'zarray1',
                   cdms_dataarray, True)
  reg.addInputPort(vcs_canvas_plot, 'tarray1',
                   cdms_dataarray, True)
  reg.addInputPort(vcs_canvas_plot, 'warray1',
                   cdms_dataarray, True)
  reg.addInputPort(vcs_canvas_plot, 'xarray2',
                   cdms_dataarray, True)
  reg.addInputPort(vcs_canvas_plot, 'yarray2',
                   cdms_dataarray, True)
  reg.addInputPort(vcs_canvas_plot, 'zarray2',
                   cdms_dataarray, True)
  reg.addInputPort(vcs_canvas_plot, 'tarray2',
                   cdms_dataarray, True)
  reg.addInputPort(vcs_canvas_plot, 'warray2',
                   cdms_dataarray, True)
  reg.addInputPort(vcs_canvas_plot, 'xbounds',
                   cdms_dataarray, True)
  reg.addInputPort(vcs_canvas_plot, 'ybounds',
                   cdms_dataarray, True)
  reg.addInputPort(vcs_canvas_plot, 'xname',
                   core.modules.basic_modules.String, True)
  reg.addInputPort(vcs_canvas_plot, 'yname',
                   core.modules.basic_modules.String, True)
  reg.addInputPort(vcs_canvas_plot, 'zname',
                   core.modules.basic_modules.String, True)
  reg.addInputPort(vcs_canvas_plot, 'tname',
                   core.modules.basic_modules.String, True)
  reg.addInputPort(vcs_canvas_plot, 'wname',
                   core.modules.basic_modules.String, True)
  reg.addInputPort(vcs_canvas_plot, 'xunits',
                   core.modules.basic_modules.String, True)
  reg.addInputPort(vcs_canvas_plot, 'yunits',
                   core.modules.basic_modules.String, True)
  reg.addInputPort(vcs_canvas_plot, 'zunits',
                   core.modules.basic_modules.String, True)
  reg.addInputPort(vcs_canvas_plot, 'tunits',
                   core.modules.basic_modules.String, True)
  reg.addInputPort(vcs_canvas_plot, 'wunits',
                   core.modules.basic_modules.String, True)
  reg.addInputPort(vcs_canvas_plot, 'xweights',
                   cdms_dataarray, True)
  reg.addInputPort(vcs_canvas_plot, 'yweights',
                   cdms_dataarray, True)
  
  reg.addOutputPort(vcs_canvas_plot, "image",
                    (core.modules.basic_modules.File, 'rendered image'))
