###############################################################################
##
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
##  - Neither the name of the University of Utah nor the names of its 
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
import copy
from itertools import imap, chain
import math
import operator
import scipy
import tempfile

from vistrails.core.data_structures.bijectivedict import Bidict
from vistrails.core.utils import append_to_dict_of_lists

from .pipeline_utils import pipeline_bbox, pipeline_centroid


##############################################################################
# This is the analogy implementation

##############################################################################
# EigenBase

def mzeros(*args, **kwargs):
    az = scipy.zeros(*args, dtype=float, **kwargs)
    return scipy.matrix(az)

def mones(*args, **kwargs):
    az = scipy.ones(*args, dtype=float, **kwargs)
    return scipy.matrix(az)

#mzeros = lambda *args, **kwargs: scipy.matrix(scipy.zeros(*args, **kwargs))
# mones = lambda *args, **kwargs: scipy.matrix(scipy.ones(*args, **kwargs))
 
class EigenBase(object):

    ##########################################################################
    # Constructor and initialization

    def __init__(self,
                 pipeline1,
                 pipeline2):
        self._p1 = pipeline1
        self._p2 = pipeline2
        self._debug = False
        self.init_vertex_similarity()
        self.init_edge_similarity()

    def init_vertex_similarity(self):
        num_verts_p1 = len(self._p1.graph.vertices)
        num_verts_p2 = len(self._p2.graph.vertices)
        m_i = mzeros((num_verts_p1, num_verts_p2))
        m_o = mzeros((num_verts_p1, num_verts_p2))
        def get_vertex_map(g):
            return Bidict([(v, k) for (k, v)
                           in enumerate(g.iter_vertices())])
        # vertex_maps: vertex_id to matrix index
        self._g1_vertex_map = get_vertex_map(self._p1.graph)
        self._g2_vertex_map = get_vertex_map(self._p2.graph)
        for i in xrange(num_verts_p1):
            for j in xrange(num_verts_p2):
                v1_id = self._g1_vertex_map.inverse[i]
                v2_id = self._g2_vertex_map.inverse[j]
                (in_s8y, out_s8y) = self.compare_modules(v1_id, v2_id)
                m_i[i,j] = in_s8y
                m_o[i,j] = out_s8y
        # print m_i
        # print m_o
        self._input_vertex_s8y = m_i
        self._output_vertex_s8y = m_o
        self._vertex_s8y = (m_i + m_o) / 2.0

    def init_edge_similarity(self):
        def get_edge_map(g):
            itor = enumerate(imap(lambda x: x[2],
                                  g.iter_all_edges()))
            return Bidict([(v, k) for (k, v)
                           in itor])
        # edge_maps: edge_id to matrix index
        self._g1_edge_map = get_edge_map(self._p1.graph)
        self._g2_edge_map = get_edge_map(self._p2.graph)

        m_e = mzeros((len(self._g1_edge_map),
                      len(self._g2_edge_map)))

        for i in xrange(len(self._g1_edge_map)):
            for j in xrange(len(self._g2_edge_map)):
                c1_id = self._g1_edge_map.inverse[i]
                c2_id = self._g2_edge_map.inverse[j]
                s8y = self.compare_connections(c1_id, c2_id)
                m_e[i, j] = s8y
        self._edge_s8y = m_e

    ##########################################################################
    # Atomic comparisons for modules and connections

    def create_type_portmap(self, ports):
        result = {}
        for port_name, port_descs in ports.iteritems():
            for port_desc in port_descs:
                sp = tuple(port_desc)
                append_to_dict_of_lists(result, sp, port_name)
        return result

    def compare_modules(self, p1_id, p2_id):
        """Returns two values \in [0, 1] that is how similar the
        modules are intrinsically, ie. without looking at
        neighborhoods. The first value gives similarity wrt input
        ports, the second to output ports."""
        (m1_inputs, m1_outputs) = self.get_ports(self._p1.modules[p1_id])
        (m2_inputs, m2_outputs) = self.get_ports(self._p2.modules[p2_id])


        m2_input_hist = self.create_type_portmap(m2_inputs)
        m2_output_hist = self.create_type_portmap(m2_outputs)

        output_similarity = 0.0
        total = 0
        # Outputs can be covariant, inputs can be contravariant
        # FIXME: subtypes, etc etc
        for (port_name, port_descs) in m1_outputs.iteritems():
            # we use max() .. because we want to count
            # nullary ports as well
            total_descs = max(len(port_descs), 1)
            total += total_descs
            # assert len(port_descs) == 1
            if (m2_outputs.has_key(port_name) and
                m2_outputs[port_name] == port_descs):
                output_similarity += float(total_descs)
            else:
                for port_desc in port_descs:
                    port_desc = tuple(port_desc)
                    if m2_output_hist.has_key(port_desc):
                        output_similarity += 1
        if len(m1_outputs):
            output_similarity /= total
        else:
            output_similarity = 0.2

        if (self._p1.modules[p1_id].name !=
            self._p2.modules[p2_id].name):
            output_similarity *= 0.99

        input_similarity = 0.0
        total = 0
        # FIXME: consider supertypes, etc etc
        
        for (port_name, port_descs) in m1_inputs.iteritems():
            # we use max() .. because we want to count
            # nullary ports as well
            total_descs = max(len(port_descs), 1)
            total += total_descs
            if (m2_inputs.has_key(port_name) and
                m2_inputs[port_name] == port_descs):
                input_similarity += 1.0
            else:
                for port_desc in port_descs:
                    port_desc = tuple(port_desc)
                    if m2_input_hist.has_key(port_desc):
                        input_similarity += 1

        if len(m1_inputs):
            input_similarity /= total
        else:
            input_similarity = 0.2

        if (self._p1.modules[p1_id].name !=
            self._p2.modules[p2_id].name):
            input_similarity *= 0.99

        return (input_similarity, output_similarity)

    def compare_connections(self, p1_id, p2_id):
        """Returns a value \in [0, 1] that says how similar
        the two connections are."""
        c1 = self._p1.connections[p1_id]
        c2 = self._p2.connections[p2_id]

        # FIXME: Make this softer in the future
        if self._debug:
            print "COMPARING %s:%s -> %s:%s with %s:%s -> %s:%s" % \
                (self._p1.modules[c1.sourceId].name, c1.source.name,
                 self._p1.modules[c1.destinationId].name, c1.destination.name,
                 self._p2.modules[c2.sourceId].name, c2.source.name,
                 self._p2.modules[c2.destinationId].name, c2.destination.name),
        if c1.source.name != c2.source.name:
            if self._debug:
                print 0.0
            return 0.0
        if c1.destination.name != c2.destination.name:
            if self._debug:
                print 0.0
            return 0.0

        m_c1_sid = self._g1_vertex_map[c1.sourceId]
        m_c1_did = self._g1_vertex_map[c1.destinationId]
        m_c2_sid = self._g2_vertex_map[c2.sourceId]
        m_c2_did = self._g2_vertex_map[c2.destinationId]

        if self._debug:
            print (self._output_vertex_s8y[m_c1_sid, m_c2_sid] +
                    self._input_vertex_s8y[m_c1_did, m_c2_did]) / 2.0
        return (self._output_vertex_s8y[m_c1_sid, m_c2_sid] +
                self._input_vertex_s8y[m_c1_did, m_c2_did]) / 2.0


    ##########################################################################
    # Utility

    @staticmethod
    def pm(m, digits=5):
        def get_digits(x):
            if x == 0: return 0
            return int(math.log(abs(x) * 10.0, 10.0))
        vd = scipy.vectorize(get_digits)
        dm = vd(m)
        widths = dm.max(0)
        (l, c) = m.shape
        for i in xrange(l):
            EigenBase.pv(m[i,:],
                         digits=digits,
                         left_digits=widths)

    @staticmethod
    def pv(v, digits=5, left_digits=None):
        # FIXME - some scipy indexing seems to be currently
        # inconsistent across different deployed versions. Fix this.
        if isinstance(v, scipy.matrix):
            v = scipy.array(v)[0]
        (c,) = v.shape
        print "[ ",
        for j in xrange(c):
            if left_digits != None:
                d = left_digits[0,j]
            else:
                d = 0
            fmt = ("%" +
                   str(d + digits + 1) + 
                   "." + str(digits) + "f ")
            print (fmt % v[j]),
        print "]"

    def print_s8ys(self):
        print "Input s8y"
        self.pm(self._input_vertex_s8y)
        print "\nOutput s8y"
        self.pm(self._output_vertex_s8y)
        print "\nConnection s8y"
        self.pm(self._edge_s8y)
        print "\nCombined s8y"
        self.pm(self._vertex_s8y)

    # FIXME: move this somewhere decent.
    def get_ports(self, module, include_optional=False):
        """get_ports(module) -> (input_ports, output_ports)

        Returns all ports for a given module name, all the way
        up the class hierarchy."""

        def remove_descriptions(d):
            def update_elements(spec):
                return [v.name for v
                        in spec.descriptors()]
            for k in d.keys():
                v = update_elements(d[k])
                if len(v):
                    d[k] = v
                else:
                    del d[k]

        inputs = dict([(port.name, port) for
                       port in module.destinationPorts()
                       if (not port.optional or include_optional)])
        outputs = dict([(port.name, port) for
                        port in module.sourcePorts()
                        if (not port.optional or include_optional)])

        remove_descriptions(inputs)
        remove_descriptions(outputs)
        return (inputs, outputs)

##############################################################################
# EigenPipelineSimilarity2

class EigenPipelineSimilarity2(EigenBase):

    def __init__(self, *args, **kwargs):
        alpha = kwargs.pop('alpha')
        EigenBase.__init__(self, *args, **kwargs)
        self.init_operator(alpha=alpha)

    def init_operator(self, alpha):
        def edges(pip, v_id):
            def from_fn(x): return (x[1], x[2])
            def to_fn(x): return (x[0], x[2])
            return chain(imap(from_fn,   pip.graph.iter_edges_from(v_id)),
                         imap(to_fn,     pip.graph.iter_edges_to(v_id)))
        num_verts_p1 = len(self._p1.graph.vertices)
        num_verts_p2 = len(self._p2.graph.vertices)
        n = num_verts_p1 * num_verts_p2
        def ix(a,b): return num_verts_p2 * a + b
        # h is the raw substochastic matrix
        from scipy import sparse
        h = sparse.lil_matrix((n, n))
        # a is the dangling node vector
        a = mzeros(n)
        for i in xrange(num_verts_p1):
            v1_id = self._g1_vertex_map.inverse[i]
            for j in xrange(num_verts_p2):
                ix_ij = ix(i,j)
                v2_id = self._g2_vertex_map.inverse[j]
                running_sum = 0.0
                for (_, p1_edge) in edges(self._p1, v1_id):
                    for (_, p2_edge) in edges(self._p2, v2_id):
                        e1_id = self._g1_edge_map[p1_edge]
                        e2_id = self._g2_edge_map[p2_edge]
                        running_sum += self._edge_s8y[e1_id, e2_id]
                if running_sum == 0.0:
                    a[0, ix_ij] = 1.0
                    continue
                for (p1_v, p1_edge_id) in edges(self._p1, v1_id):
                    for (p2_v, p2_edge_id) in edges(self._p2, v2_id):
                        e1_id = self._g1_edge_map[p1_edge_id]
                        e2_id = self._g2_edge_map[p2_edge_id]
                        p1_v_id = self._g1_vertex_map[p1_v]
                        p2_v_id = self._g2_vertex_map[p2_v]
                        value = self._edge_s8y[e1_id, e2_id] / running_sum
                        h[ix_ij, ix(p1_v_id, p2_v_id)] = value

        self._alpha = alpha
        self._n = n
        self._h = h
        self._a = a
        self._e = mones(n) / n

    def step(self, pi_k):
        r = pi_k * self._h * self._alpha
        t = pi_k * self._alpha * self._a.transpose()
        r += self._v * (t[0,0] + 1.0 - self._alpha)
        return r

    def solve_v(self, s8y):
        fl = s8y.flatten()
        self._v = fl / fl.sum()
        v = copy.copy(self._e)
        step = 0
        def write_current_matrix():
            f = open('%s/%s_%03d.v' % (tempfile.gettempdir(),
                                       self._debug_matrix_file, step), 'w')
            x = v.reshape(len(self._p1.modules),
                          len(self._p2.modules))
            for i in xrange(len(self._p1.modules)):
                for j in xrange(len(self._p2.modules)):
                    f.write('%f ' % x[i,j])
                f.write('\n')
            f.close()
        while 1:
            if self._debug:
                write_current_matrix()
            new = self.step(v)
            r = (v-new)
            r = scipy.multiply(r,r)
            s = r.sum()
            if s < 0.0000001 and step >= 10:
                return v
            step += 1
            v = new

    def solve(self):
        def write_debug_pipeline_positions(pipeline, mmap, f):
            f.write('%d %d\n' % (len(pipeline.modules),
                                 len(pipeline.connections)))
            for k, v in mmap.iteritems():
                f.write('%d %d\n' % (k, v))
            c = pipeline_centroid(pipeline)
            mn, mx = pipeline_bbox(pipeline)
            f.write('%f %f %f %f\n' % (mn.x, mn.y, mx.x, mx.y))
            for i, m in pipeline.modules.iteritems():
                nc = m.center - c
                f.write('%d %s %f %f\n' % (i, m.name, nc.x, nc.y))
            for i, c in pipeline.connections.iteritems():
                f.write('%d %d %d\n' % (i, c.sourceId, c.destinationId))

        if self._debug:
            out = open('%s/pipelines.txt' % tempfile.gettempdir(), 'w')
            write_debug_pipeline_positions(self._p1, self._g1_vertex_map, out)
            write_debug_pipeline_positions(self._p2, self._g2_vertex_map, out)
            self.print_s8ys()
            out.close()

        self._debug_matrix_file = 'input_matrix'
        r_in  = self.solve_v(self._input_vertex_s8y)
        self._debug_matrix_file = 'output_matrix'
        r_out = self.solve_v(self._output_vertex_s8y)
        r_in = r_in.reshape(len(self._p1.modules),
                            len(self._p2.modules))
        r_out = r_out.reshape(len(self._p1.modules),
                              len(self._p2.modules))

        s = r_in.sum(1)
        s[s==0.0] = 1
        r_in /= s

        s = r_out.sum(1)
        s[s==0.0] = 1
        r_out /= s
        
        r_combined = scipy.multiply(r_in, r_out)

        # Breaks ties on combined similarity
        r_in = r_in * 0.9 + r_combined * 0.1
        r_out = r_out * 0.9 + r_combined * 0.1

        if self._debug:
            print "== G1 =="
            for (k,v) in sorted(self._g1_vertex_map.iteritems(), key=operator.itemgetter(1)):
                print v, k, self._p1.modules[k].name
            print "== G2 =="
            for (k,v) in sorted(self._g2_vertex_map.iteritems(), key=operator.itemgetter(1)):
                print v, k, self._p2.modules[k].name
            
            print "input similarity"
            self.pm(r_in, digits=3)
            print "output similarity"
            self.pm(r_out, digits=3)
            print "combined similarity"
            self.pm(r_combined, digits=3)

        inputmap = dict([(self._g1_vertex_map.inverse[ix],
                          self._g2_vertex_map.inverse[v[0,0]])
                         for (ix, v) in
                         enumerate(r_in.argmax(1))])
        outputmap = dict([(self._g1_vertex_map.inverse[ix],
                           self._g2_vertex_map.inverse[v[0,0]])
                          for (ix, v) in
                          enumerate(r_out.argmax(1))])
        combinedmap = dict([(self._g1_vertex_map.inverse[ix],
                             self._g2_vertex_map.inverse[v[0,0]])
                            for (ix, v) in
                            enumerate(r_combined.argmax(1))])
#         print inputmap
#         print outputmap
        return inputmap, outputmap, combinedmap


    
