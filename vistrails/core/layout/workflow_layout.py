###############################################################################
##
## Copyright (C) 2014-2016, New York University.
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
""" This code creates layouts for workflow digraphs.
Originally written by Lauro D. Lins.

"""

####################################################

from __future__ import division

def uniquify(seq, idfun=None): 
    # order preserving
    if idfun is None:
        def idfun(x): return x
    seen = {}
    result = []
    for item in seq:
        marker = idfun(item)
        # in old Python versions:
        # if seen.has_key(marker)
        # but in new ones:
        if marker in seen: continue
        seen[marker] = 1
        result.append(item)
    return result


class Defaults(object):
    u            = 10.0
    label_margin = 20.0 

class Vec2(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def set(self, x, y):
        self.x = x
        self.y = y
    def __add__(self, other):
        if isinstance(other, (float, int)):
            return Vec2(self.x + other, self.y + other)
        else:
            return Vec2(self.x + other.x, self.y + other.y)
    def __radd__(self, other):
        return self.__add__(other)
    def __sub__(self, other):
        if isinstance(other, (float, int)):
            return Vec2(self.x - other, self.y - other)
        else:
            return Vec2(self.x - other.x, self.y - other.y)
    def __rsub__(self, other):
        return self.__sub__(other)
    def __mul__(self, other):
        if isinstance(other, (float, int)):
            return Vec2(self.x * other, self.y * other)
        else:
            return Vec2(self.x * other.x, self.y * other.y)
    def __rmul__(self, other):
        return self.__mul__(other)
    def dot(self, other):
        return self.x * other.x + self.y * other.y
    def __str__(self):
        return "(%.2f, %.2f)" % (self.x, self.y)
    def __repr__(self):
        return "(%.2f, %.2f)" % (self.x, self.y)

####################################################

UNDEFINED_LAYER = None
INPUT_PORT, OUTPUT_PORT = 1,2

class Pipeline(object):

    def __init__(self):
        self.modules     = []
        self.connections = []

    def createModule(self, shortname, name, num_input_ports, num_output_ports, prev_x=None):
        mod = Module(self, len(self.modules), shortname, name, num_input_ports, num_output_ports, prev_x)
        self.modules.append(mod)
        return mod

    def createConnection(self, mod_source, port_source_idx, mod_target, port_target_idx):     
        source_port = mod_source.getOutputPort(port_source_idx)
        target_port = mod_target.getInputPort(port_target_idx)

        conn = Connection(self, source_port, target_port)
        source_port.addConnection(conn)
        target_port.addConnection(conn)

        self.connections.append(conn)

        return conn

    # def updateCache(self):
    #     self.cached_num_modules      = len(self.modules)
    #     self.cached_num_connections  = len(self.connections)



class Module(object):

    def __init__(self, workflow, key, shortname, name, num_input_ports, num_output_ports, prev_x=None):

        self.workflow     = workflow
        self.key          = key
        self.shortname    = shortname
        self.name         = name

        self.input_ports  = [ Port(self, INPUT_PORT,  i) for i in xrange(num_input_ports ) ]
        self.output_ports = [ Port(self, OUTPUT_PORT, i) for i in xrange(num_output_ports) ]

        self.layout_layer_number = UNDEFINED_LAYER
        self.layout_layer_index  = 0

        self.cached              = False
        self.cached_in_degree    = 0
        self.cached_out_degree   = 0

        self.cached_connections_succ  = [] # successor modules
        self.cached_connections_pred  = [] # predecessor modules

        self.cached_succ         = [] # successor modules
        self.cached_pred         = [] # predecessor modules

        self.cached_num_succ     = 0
        self.cached_num_pred     = 0

        self.flags               = 0

        self.layout_pos          = Vec2(0,0)
        self.layout_dim          = Vec2(1,1)
        
        self.prev_x = prev_x

    def clearFlags(self):
        self.flags = 0

    def updateCache(self):
        self.cached_in_degree = self.getInDegree()
        self.cached_out_degree = self.getOutDegree()

        self.cached_connections_succ  = [] # successor modules
        self.cached_connections_pred  = [] # predecessor modules

        # cached succ
        self.cached_succ = []
        for p in self.output_ports:
            p.collectOppositeModules(self.cached_succ)
            self.cached_connections_succ.extend([c for c in p.connections])

        uniquify(self.cached_succ)
        # print "%s's of cached_succ: " % (self.shortname),
        # print [m.name for m in self.cached_succ]


        # cached pred
        self.cached_pred = []
        for p in self.input_ports:
            p.collectOppositeModules(self.cached_pred)
            self.cached_connections_pred.extend([c for c in p.connections])
        uniquify(self.cached_pred)

        self.cached_num_succ     = len(self.cached_succ)
        self.cached_num_pred     = len(self.cached_pred)

        self.cached = True

    def getInputPort(self, idx):
        return self.input_ports[idx]
                              
    def getOutputPort(self, idx):
        return self.output_ports[idx]

    def getInDegree(self):
        count = 0
        for ip in self.input_ports:
            count += ip.getNumConnections()
        return count

    def getOutDegree(self):
        count = 0
        for ip in self.output_ports:
            count += ip.getNumConnections()
        return count



class Connection(object):
    def __init__(self, workflow, source_port, target_port):
        self.workflow    = workflow
        self.source_port = source_port # an output port
        self.target_port = target_port # an input port

    def getOppositePort(self, port):
        if self.source_port == port:
            return self.target_port
        elif self.target_port == port:
            return self.source_port
        else:
            raise ValueError("oppositePort problem: no opposite port")



class Port(object):

    def __init__(self, module, kind, index):
        self.module      = module
        self.kind        = kind
        self.index       = index
        self.connections = []

        self.layout_pos  = Vec2(0,0)
        self.layout_dim  = Vec2(1,1)

    def getNumConnections(self):
        return len(self.connections)

    def addConnection(self, connection):
        self.connections.append(connection)

        # module is not cached
        self.module.cached = False

    def collectOppositeModules(self, lst):
        for c in self.connections:
            lst.append(c.getOppositePort(self).module)



class ItemDFS(object):
    def __init__(self, module, index, max_index):
        self.module    = module
        self.index     = index
        self.max_index = max_index

        # the creation of ItemDFS implies
        # that it will be stacked on the DFSIterator
        # and the module flag goes from 0 to 1
        self.module.flags = 1



class DFSIterator(object):

    def __init__(self, workflow, update_module_cache=False):
        self.stack = []

        # stack source modules
        for m in workflow.modules:

            m.clearFlags()

            if not m.cached:
                m.updateCache()

            if m.cached_in_degree == 0: # source modules
                m.flags = 1
                self.stack.append(ItemDFS(m,-1,m.cached_num_succ))


    def next(self):
        
        while len(self.stack) > 0:

            top = self.stack[-1]
            top.index += 1
            mod = top.module
            
            #DEBUG
            #print "pop %s index %d max_index %d" % (mod.shortname, top.index, top.max_index)

            if top.index >= top.max_index:
                self.stack.pop()
                return mod
            else:
                next_mod = mod.cached_succ[top.index]
                if next_mod.flags > 0:
                    continue
                next_mod.flags = 1
                self.stack.append(ItemDFS(next_mod, -1, next_mod.cached_num_succ))

        return None

class Layer(object):

    def __init__(self, index):
        self.index   = index
        self.modules = []

        self.y = 0.0

        self.max_module_height = 0.0
        self.sum_modules_width = 0.0

    def addModule(self, module):
        self.modules.append(module)

        self.sum_modules_width += module.layout_dim.x
        self.max_module_height  = max(self.max_module_height,module.layout_dim.y)

        # print "addModule(self, module): max_module_height = ", self.max_module_height



class Layers(object):

    def __init__(self):
        self.layers  = []

    def addModule(self, module, layer_number):

        num_layers = len(self.layers)

        # print "num_layers",    num_layers
        # print "layer_number ", layer_number
        # print "layers",self.layers
        
        if layer_number >= num_layers:
            self.layers.extend([Layer(i) for i in xrange(num_layers,layer_number+1)])
        
        layer = self.layers[layer_number]
        layer.addModule(module)

    
class Page(object):
    def __init__(self, page_x0, page_y0, page_width, page_height):
        self.x0     = page_x0
        self.y0     = page_y0
        self.width  = page_width
        self.height = page_height

    def __str__(self):
        # print self.x0
        # print self.y0
        # print self.width
        # print self.height
        return "%.2f %.2f %.2f %.2f" % (self.x0, self.y0, self.width, self.height)

class WorkflowLayout(object):
    def __init__(self, wf, module_size_f, module_margin, port_size,
                 port_interspace):
        self.wf = wf
        self.module_size_f = module_size_f
        self.module_margin = module_margin
        self.port_size = port_size
        self.port_interspace = port_interspace

    #
    # Compute sizes
    # 
    def compute_module_sizes(self): 
        wf = self.wf # wf is a workflow

        u = Defaults.u # u is the base unit in points to derive the other sizes 

        #
        # A module visual representation consists of three rows
        #
        # first row: input ports
        # mid   row: text label
        # third row: output ports
        #
        row_margin = 0.20 * u
        row_height = u + 2 * row_margin

        module_height       =  3 * row_height # three stripes of

        #DEBUG
        #print "module_height = ", module_height

        module_text_margin  = u
        module_ports_margin = row_margin

        # port_margin         = 0.30 * u
        # port_interspace     = 0.15 * u
        # port_size           = 0.75 * u

        for module in wf.modules:
            module_width, module_height = self.module_size_f(module)

            # [DK] why do we have to do this here?
            if not module.cached:
                module.updateCache()

            max_num_ports = max(len(module.input_ports), len(module.output_ports))

            # ports_width = 2*module_ports_margin + max_num_ports * u + (max_num_ports-1) * module_ports_margin 
            # text_width  = 2*module_text_margin  + len(module.name) * u * 0.6

            # module_width = max(ports_width, text_width)

            module.layout_pos.set(0,0)
            module.layout_dim.set(module_width, module_height)

            for port_list, do_reverse, d in [(module.input_ports, False, -1), 
                                             (module.output_ports, True, 1)]:
                if do_reverse:
                    port_iter = reversed(port_list)
                else:
                    port_iter = port_list

                for i, p in enumerate(port_iter):
                    p.layout_pos.set(d * module_width/2.0 -
                                     d * self.module_margin[0] -
                                     d * (i + 0.5) * self.port_size[0] -
                                     d * self.port_interspace * i,
                                     d * (module_height/2.0 -
                                          self.module_margin[1] - 
                                          self.port_size[1]))
                    p.layout_dim.set(*self.port_size)
                                     
            # for p in module.input_ports:
            #     p.layout_pos.set(-module_width/2.0    +  # initial position
            #                       port_margin         +  # ports margin
            #                       (p.index + 0.5) * port_size +  # widths of previous ports + half port width
            #                       port_interspace * p.index,     # sum of previous interspace
            #                       -module_height / 2.0 + row_height / 2.0 )
            #     p.layout_dim.set(*port_size)


            # op = list(module.output_ports)
            # op.reverse()
            # for i in xrange(len(op)):
            #     p = op[i]
            #     p.layout_pos.set( module_width/2.0 - 
            #                       port_margin - 
            #                       (i + 0.5) * port_size -
            #                       port_interspace * i,
            #                       +module_height/2.0 - row_height / 2.0 )
            #     p.layout_dim.set(port_size, port_size)

    def assign_modules_to_layers(self):
        wf = self.wf

        iterator = DFSIterator(wf)

        # topologically sorted permulation of the modules
        permutation = []
        while True:
            mod = iterator.next()
            if mod is None:
                break
            permutation.append(mod)
        permutation.reverse()

        # define layers
        i = 0
        for module in permutation:
            if module.cached_num_pred == 0:
                module.layout_layer_number = 0
            else:
                module.layout_layer_number = 1 + max([pred.layout_layer_number for pred in module.cached_pred])

            # use permutation index as a the sort key to define
            # the initial permutation of the modules in each layer
            module.layout_layer_index = i
            i += 1


        # log
        # for module in permutation:
        #     print "layer of %s = %d" % (module.shortname, module.layout_layer_number)

        # adjust free modules (a free module in this context is
        # a module whose minimum successor layer and maximum predecessor layer
        # have more than one intermediate layer in between

        #
        # TODO: adjust layer
        for module in permutation:
            if module.cached_num_pred == 0 and module.cached_num_succ > 0:
                module.layout_layer_number = min([succ.layout_layer_number for succ in module.cached_succ]) - 1
            # else:
            #     a = min([succ.layout_layer_number for succ in module.cached_succ]) - 1
            # print "layer of %s = %d" % (module.shortname, module.layout_layer_number)

    def assign_module_to_layers_no_gaps(self):
        if len(self.wf.modules) == 0:
            return
        
        visited = set()
        min_layer = [0]
        def set_module_layer_number(module, layer_number):
            module.layout_layer_number = layer_number
            visited.add(module)
            min_layer[0] = min(min_layer[0], layer_number)
            for port in module.input_ports:
                for conn in port.connections:
                    if conn.source_port.module not in visited:
                        set_module_layer_number(conn.source_port.module, layer_number-1)
            for port in module.output_ports:
                for conn in port.connections:
                    if conn.target_port.module not in visited:
                        set_module_layer_number(conn.target_port.module, layer_number+1)
               
        set_module_layer_number(self.wf.modules[0], 0)
                        
        #adjust all layers numbers so that the min is 0
        if min_layer[0] < 0:
            for module in self.wf.modules:
                module.layout_layer_number -= min_layer[0]

    def assign_module_permutation_to_each_layer(self, preserve_order=False):
        wf = self.wf

        # create layers
        layers = Layers()
        for module in wf.modules:
            layers.addModule(module, module.layout_layer_number)

        # sort modules by the current value of layout_layer_index
        for layer in layers.layers:
            layer.modules.sort(lambda a,b: a.layout_layer_index - b.layout_layer_index)
            for i in xrange(len(layer.modules)):
                layer.modules[i].layout_layer_index = i

        #
        num_layers = len(layers.layers)

        lastModified = [-1 for i in xrange(num_layers)]

        #
        # sweep down and up reducing the number of crossings
        # using the barycentric method (heuristic)
        #
        iteration = 0
        updates = len(wf.modules)
        while updates > 0 and iteration < 100:

            # print "iteration: ", iteration

            updates = 0

            DOWN, UP = 1, -1
            for direction in [DOWN, UP]:

                # print "   direction:", direction

                delta = 1 if direction == DOWN else -1

                i0, i1 = (0,num_layers) if direction == DOWN else (num_layers-1,-1)

                # sweep "direction"
                for i in xrange(i0+delta,i1,direction):
                # for i in xrange(2,4):


                    i_prev = i-delta
                    # print "      layer:"        , i
                    # print "         layer_prev:", i_prev

                    layer = layers.layers[i]

                    # if one module on layer then continue
                    num_modules = len(layer.modules)
                    if num_modules == 1:
                        continue

                    # if nothing chaged on this layer and the "previous" layer (in the sweep direction)
                    # in the last iteration then nothing needs to be done
                    if iteration - lastModified[i_prev] > 1 and \
                           iteration - lastModified[i] > 1:
                        continue

                    # apply barycentric permutation to layer "i" using neighbors on layer "i + delta"
                    barycenters = [-1] * num_modules
                    for j in xrange(num_modules):

                        module      = layer.modules[j]
                        connections = \
                            module.cached_connections_pred  \
                            if direction == DOWN else       \
                            module.cached_connections_succ

                        value = 0.0
                        for c in connections:
                            opposite_port = c.source_port if direction == DOWN else c.target_port
                            value += opposite_port.module.layout_layer_index + opposite_port.index/100.0
                        if len(connections) > 0:
                            value /= 1.0 * len(connections)
                            barycenters[j] = value

                    for j in xrange(1,num_modules):
                        if barycenters[j] < 0:
                            barycenters[j] = barycenters[j-1] + 1e-5

                    # print "         barycenters: ", barycenters


                    new_order = [(barycenters[j], layer.modules[j]) for j in xrange(num_modules)]
                    new_order.sort()

                    # print "            indices before: ", [u.layout_layer_index for u in layer.modules]
                    # print "            indices after:  ", [aux[0] for aux in new_order]
                    # print "            names before =  ",[mod.name for mod in layer.modules]

                    for j in xrange(num_modules):
                        module = new_order[j][1]
                        if module.layout_layer_index != j:
                            # print "            module indexed %d goes to index %d" % (module.layout_layer_index,j)
                            lastModified[i] = iteration
                            updates += 1

                    if lastModified[i] == iteration:
                        for j in xrange(num_modules):
                            module = new_order[j][1]
                            module.layout_layer_index = j


                    # sort using the last layout_layer_index
                    layer.modules.sort(lambda a,b: a.layout_layer_index - b.layout_layer_index)
                    # print "            names after =",[mod.name for mod in layer.modules]


                # print "      updates: ", updates

            # iteration
            iteration += 1

            # break
            break
        
        if preserve_order:
            for layer in layers.layers:                

                # sort using the last layout_layer_index
                layer.modules.sort(key=lambda x: x.layout_layer_index)
            
                #separate modules that have no previous x value
                temp = []
                for i in reversed(range(len(layer.modules))):
                    if layer.modules[i].prev_x is None:
                        temp.append((i,layer.modules.pop(i)))
                
                #sort on previous x
                layer.modules.sort(key=lambda x: x.prev_x)
                
                #put separated modules back in their original slot
                for item in reversed(temp):
                    layer.modules.insert(item[0],item[1])
                    
                #reassign index
                for i in range(len(layer.modules)):
                    layer.modules[i].layout_layer_index = i
            
    #
    # this method is "friend" of the classes above in the C++ sense:
    # it can access and modify
    #
    def compute_layout(self, layer_x_separation, layer_y_separation): 
        wf = self.wf # wf is a workflow

        # create layers
        layers = Layers()
        for module in wf.modules:
            layers.addModule(module, module.layout_layer_number)

        for layer in layers.layers:# sort using the last layout_layer_index
            layer.modules.sort(lambda a,b: a.layout_layer_index - b.layout_layer_index)

        # spread layers
        min_x = max_x = 0.0
        y = min_y = max_y = 0.0

        top_layer = True

        for layer in layers.layers:

            # print "layer: ", layer.index

            if not top_layer:
                y += layer_y_separation
            else:
                top_layer = False


            layer_half_height = layer.max_module_height / 2.0

            # print "layer_half_height", layer_half_height

            y += layer_half_height


            # print "layer ", layer.index, " y = ", y

            layer_num_modules = len(layer.modules)
            layer_width = layer.sum_modules_width + (layer_num_modules-1) * layer_x_separation
            layer_min_x = -layer_width/2.0

            x = layer_min_x

            # set module positions
            for i in xrange(layer_num_modules):

                if (i > 0):
                    x += layer_x_separation

                module = layer.modules[i]

                module_half_width = module.layout_dim.x / 2.0

                x += module_half_width

                module.layout_pos.set(x, y)

                x += module_half_width

            layer_max_x = x

            min_x = min(min_x, layer_min_x)
            max_x = max(max_x, layer_max_x)

            y += layer_half_height

        max_y = y # y only got smaller


        #
        page_x_margin = 3 * Defaults.u
        page_y_margin = 3 * Defaults.u

        page_util_width  = max_x - min_x
        page_util_height = max_y - min_y

        page_width  = page_util_width  + page_x_margin * 2
        page_height = page_util_height + page_y_margin * 2

        page_x0     = -page_width /2.0
        page_y0     = -page_y_margin

        page = Page(page_x0, page_y0, page_width, page_height)

        return page

    def run_all(self, layer_x_separation=50, layer_y_separation=50, preserve_order=False, no_gaps=False):
        self.compute_module_sizes()
        if no_gaps:
            self.assign_module_to_layers_no_gaps()
        else:
            self.assign_modules_to_layers()
        self.assign_module_permutation_to_each_layer(preserve_order)
        self.compute_layout(layer_x_separation, layer_y_separation)